from models import User, Product, CartItem, Order, OrderItem
from flask_login import current_user
from flask import session
from app import db
import random
import string


def get_cart_count():
    """Get the number of items in the cart"""
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).count()
    else:
        cart = session.get('cart', {})
        return sum(quantity for quantity in cart.values())


def get_cart_total():
    """Get the total price of items in the cart"""
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        return sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = session.get('cart', {})
        total = 0
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                total += product.price * quantity
        return total


def merge_guest_cart():
    """Merge guest cart into user cart after login"""
    if not current_user.is_authenticated:
        return
    
    cart = session.get('cart', {})
    if not cart:
        return
    
    for product_id, quantity in cart.items():
        # Check if product already in user's cart
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=int(product_id)).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
        else:
            # Add new item to cart
            cart_item = CartItem(user_id=current_user.id, product_id=int(product_id), quantity=quantity)
            db.session.add(cart_item)
    
    # Commit changes to database
    db.session.commit()
    
    # Clear guest cart
    session.pop('cart', None)


def generate_order_id():
    """Generate a unique order ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def get_related_products(product, limit=4):
    """Get related products based on the category"""
    return Product.query.filter_by(category=product.category).filter(Product.id != product.id).limit(limit).all()


def format_price(price):
    """Format price as currency"""
    return f"₹{price:.2f}"


def generate_invoice_pdf(order):
    """Generate a PDF invoice for an order
    
    Args:
        order: Order object
        
    Returns:
        str: Filename of the generated PDF
    """
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime
    
    # Create a directory for invoices if it doesn't exist
    invoice_dir = os.path.join('static', 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)
    
    # Create a directory for assets if it doesn't exist
    assets_dir = os.path.join('static', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # Get paths to signature and stamp PNG files
    signature_path = os.path.join(assets_dir, 'signature.png')
    stamp_path = os.path.join(assets_dir, 'stamp.png')
    
    # If the PNG files don't exist, try to create them with the signature.py script
    if not os.path.exists(signature_path) or not os.path.exists(stamp_path):
        try:
            # Check if the signature generator script exists
            signature_script = os.path.join(assets_dir, 'signature.py')
            if os.path.exists(signature_script):
                import subprocess
                subprocess.run(['python', signature_script], cwd=assets_dir)
            else:
                # Create simple signature and stamp with PIL
                from PIL import Image, ImageDraw, ImageFont
                
                # Create signature
                width, height = 500, 150
                image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                draw = ImageDraw.Draw(image)
                
                # Draw a signature line
                draw.line([(50, 80), (450, 80)], fill=(0, 0, 150), width=2)
                draw.text((250, 100), "Authorized Signature", fill=(0, 0, 0))
                image.save(signature_path)
                
                # Create stamp
                stamp_width, stamp_height = 300, 300
                stamp = Image.new('RGBA', (stamp_width, stamp_height), (255, 255, 255, 0))
                stamp_draw = ImageDraw.Draw(stamp)
                stamp_draw.ellipse((10, 10, stamp_width-10, stamp_height-10), outline=(135, 20, 20), width=3)
                stamp_draw.ellipse((30, 30, stamp_width-30, stamp_height-30), outline=(135, 20, 20), width=2)
                stamp_draw.text((stamp_width//2, stamp_height//2), "PC ASSEMBLER", fill=(135, 20, 20))
                stamp.save(stamp_path)
        except Exception as e:
            print(f"Error creating signature/stamp: {e}")
    
    # Generate a unique filename
    filename = f"invoice_{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(invoice_dir, filename)
    
    # Register Arial Unicode font for proper Rupee symbol display
    # Try to use existing system font if available, otherwise use defaults
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        default_font = 'DejaVuSans'
    except:
        default_font = 'Helvetica'
    
    # Use a safe representation of the Rupee symbol that works in PDF
    rupee_symbol = 'Rs.'  # Using text instead of Unicode to ensure compatibility
    
    # Create the PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Add custom styles
    styles.add(ParagraphStyle(name='Center', alignment=1, fontName=default_font))
    styles.add(ParagraphStyle(name='Right', alignment=2, fontName=default_font))
    
    # Override default styles with our font
    title_style = styles['Title']
    title_style.fontName = default_font
    
    normal_style = styles['Normal']
    normal_style.fontName = default_font
    
    heading2_style = styles['Heading2']
    heading2_style.fontName = default_font
    
    # Create the content
    content = []
    
    # Add the header
    content.append(Paragraph("PC Assembler", styles['Title']))
    content.append(Paragraph("Invoice", styles['Title']))
    content.append(Spacer(1, 20))
    
    # Add order details
    content.append(Paragraph(f"Invoice #: {order.id}", styles['Normal']))
    content.append(Paragraph(f"Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    content.append(Paragraph(f"Transaction ID: {order.transaction_id or 'N/A'}", styles['Normal']))
    content.append(Paragraph(f"Payment Method: {order.payment_method.replace('_', ' ').title()}", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Add customer details
    content.append(Paragraph("Shipping Information:", styles['Heading2']))
    content.append(Paragraph(f"Customer: {order.user.full_name()}", styles['Normal']))
    content.append(Paragraph(f"Email: {order.user.email}", styles['Normal']))
    content.append(Paragraph(f"Phone: {order.contact_phone}", styles['Normal']))
    content.append(Paragraph(f"Address: {order.shipping_address}", styles['Normal']))
    content.append(Paragraph(f"{order.shipping_city}, {order.shipping_state} {order.shipping_zipcode}", styles['Normal']))
    content.append(Paragraph(f"{order.shipping_country}", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Add order items
    content.append(Paragraph("Order Items:", styles['Heading2']))
    
    # Create table data
    table_data = [["Item", "Quantity", "Price", "Total"]]
    
    # Add items to table
    for item in order.items:
        product = item.product
        table_data.append([
            product.name,
            str(item.quantity),
            f"{rupee_symbol}{item.price:,.2f}",
            f"{rupee_symbol}{(item.price * item.quantity):,.2f}"
        ])
    
    # Add total row
    table_data.append(["", "", "Total:", f"{rupee_symbol}{order.total_amount:,.2f}"])
    
    # Create table
    table = Table(table_data, colWidths=[250, 70, 100, 100])
    
    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -2), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), default_font + '-Bold' if default_font == 'Helvetica' else default_font),
        ('FONTNAME', (0, -1), (-1, -1), default_font + '-Bold' if default_font == 'Helvetica' else default_font),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BOX', (0, -1), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))
    
    content.append(table)
    content.append(Spacer(1, 40))
    
    # Add signature and stamp
    signature_stamp_data = [
        [Paragraph('For PC Assembler', styles['Normal']), ""],
        [Image(signature_path, width=2*inch, height=0.8*inch), Image(stamp_path, width=1.2*inch, height=1.2*inch)],
        [Paragraph('Authorized Signatory', styles['Normal']), ""],
    ]
    
    signature_stamp_table = Table(signature_stamp_data, colWidths=[300, 220])
    signature_stamp_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    content.append(signature_stamp_table)
    content.append(Spacer(1, 20))
    
    # Add footer
    content.append(Paragraph("Thank you for shopping with PC Assembler!", styles['Center']))
    content.append(Spacer(1, 10))
    content.append(Paragraph("This is a computer-generated invoice and does not require a physical signature.", 
                            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))
    
    # Build the PDF
    doc.build(content)
    
    return filename
