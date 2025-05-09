from models import User, Product, CartItem, Order, OrderItem
from flask_login import current_user
from flask import session, url_for
from app import db
import random
import string
import os


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
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id, product_id=int(product_id)).first()

        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
        else:
            # Add new item to cart
            cart_item = CartItem(user_id=current_user.id,
                                 product_id=int(product_id),
                                 quantity=quantity)
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
    return Product.query.filter_by(category=product.category).filter(
        Product.id != product.id).limit(limit).all()


def format_price(price):
    """Format price as currency"""
    return f"Rs. {price:.2f}"


def get_default_product_image(product):
    """
    Get default product image URL based on category
    
    Args:
        product: Product object
        
    Returns:
        str: URL to default image for the product category
    """
    from flask import url_for
    
    # Temporarily disabling external image URLs and using only SVG images
    # TEMPORARY: Previously checked if product had a valid image URL
    # if product.image_url and product.image_url.startswith(('http://', 'https://')):
    #    return product.image_url
    
    # Get product category
    category = product.category
    
    # Make sure category is valid
    valid_categories = [
        'cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 
        'cooling', 'peripherals', 'monitor', 'prebuilt_intel', 'prebuilt_amd'
    ]
    
    # If category has peripheral subcategory (like peripherals_keyboard)
    if category.startswith('peripherals_'):
        subcategory = category
        try:
            return url_for('static', filename=f'images/categories/{subcategory}.svg')
        except:
            # Fallback to main peripherals image
            return url_for('static', filename='images/categories/peripherals.svg')
    
    # For prebuilt PCs, use a CPU or GPU image as fallback
    elif category == 'prebuilt_intel' or category == 'prebuilt_amd':
        try:
            # Try to find a prebuilt PC image
            return url_for('static', filename=f'images/categories/{category}.svg')
        except:
            # Fallback to CPU image for prebuilt
            return url_for('static', filename='images/categories/cpu.svg')
    
    # For regular categories
    elif category in valid_categories:
        return url_for('static', filename=f'images/categories/{category}.svg')
    
    # Default fallback image for unknown categories
    else:
        return url_for('static', filename='images/default-product.svg')


def generate_invoice_pdf(order):
    """Generate a PDF invoice for an order with GST details

    Args:
        order: Order object

    Returns:
        str: Filename of the generated PDF
    """
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
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

    # If the PNG files don't exist, create them with PIL
    if not os.path.exists(signature_path) or not os.path.exists(stamp_path):
        try:
            # Check if the signature generator script exists
            signature_script = os.path.join(assets_dir, 'signature.py')
            if os.path.exists(signature_script):
                import subprocess
                subprocess.run(['python', signature_script], cwd=assets_dir)
            else:
                # Create simple signature and stamp with PIL
                from PIL import Image as PILImage
                from PIL import ImageDraw, ImageFont

                # Create signature
                width, height = 500, 150
                image = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
                draw = ImageDraw.Draw(image)

                # Draw a signature line
                draw.line([(50, 80), (450, 80)], fill=(0, 0, 150), width=2)
                draw.text((250, 100), "Authorized Signature", fill=(0, 0, 0))
                image.save(signature_path)

                # Create stamp - make it look like an official round stamp
                stamp_width, stamp_height = 300, 300
                stamp = PILImage.new('RGBA', (stamp_width, stamp_height),
                                 (255, 255, 255, 0))
                stamp_draw = ImageDraw.Draw(stamp)
                
                # Outer circle
                stamp_draw.ellipse(
                    (10, 10, stamp_width - 10, stamp_height - 10),
                    outline=(135, 20, 20),
                    width=3)
                
                # Inner circle
                stamp_draw.ellipse(
                    (40, 40, stamp_width - 40, stamp_height - 40),
                    outline=(135, 20, 20),
                    width=2)
                
                # Text on top of circle
                stamp_draw.text((150, 50), "SS PC ASSEMBLER", 
                               fill=(135, 20, 20))
                
                # Text in middle
                stamp_draw.text((100, 140), "AUTHORIZED", 
                               fill=(135, 20, 20))
                
                # Text at bottom
                stamp_draw.text((120, 180), "LUCKNOW", 
                               fill=(135, 20, 20))
                
                stamp.save(stamp_path)
        except Exception as e:
            print(f"Error creating signature/stamp: {e}")

    # Generate a unique filename
    invoice_number = f"INV-{order.id}-{datetime.now().strftime('%Y%m%d')}"
    filename = f"invoice_{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(invoice_dir, filename)

    # Register fonts for proper display
    try:
        pdfmetrics.registerFont(
            TTFont('DejaVuSans',
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(
            TTFont('DejaVuSans-Bold',
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        default_font = 'DejaVuSans'
        bold_font = 'DejaVuSans-Bold'
    except:
        default_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    # Use a safe representation of the Rupee symbol that works in PDF
    rupee_symbol = 'Rs.'

    # Create the PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    # Add custom styles
    styles.add(ParagraphStyle(name='Center', alignment=1, fontName=default_font))
    styles.add(ParagraphStyle(name='Right', alignment=2, fontName=default_font))
    styles.add(ParagraphStyle(name='Bold', fontName=bold_font))
    styles.add(ParagraphStyle(name='CustomHeading', fontName=bold_font, fontSize=12))
    styles.add(ParagraphStyle(name='Small', fontName=default_font, fontSize=8))
    
    # Override default styles with our font
    title_style = styles['Title']
    title_style.fontName = bold_font
    title_style.fontSize = 16
    title_style.alignment = 1
    
    heading2_style = styles['Heading2']
    heading2_style.fontName = bold_font

    # Create the content
    content = []

    # Add the header - TAX INVOICE
    content.append(Paragraph("TAX INVOICE", styles['Title']))
    content.append(Spacer(1, 10))
    
    # Company info
    company_info = [
        [Paragraph("<b>Sold By:</b>", styles['Normal']), 
         Paragraph("<b>Invoice Details:</b>", styles['Normal'])],
        [Paragraph("SS PC Assembler<br/>Shop No. 5, Near ITI Chauraha<br/>Vikas Nagar, Lucknow<br/>Uttar Pradesh – 226022<br/>GSTIN: HIIJNI54465464FDD", styles['Normal']),
         Paragraph(f"Invoice Number: {invoice_number}<br/>Invoice Date: {datetime.now().strftime('%d-%m-%Y')}<br/>Order ID: {order.id}", styles['Normal'])]
    ]
    
    company_table = Table(company_info, colWidths=[300, 220])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    
    content.append(company_table)
    content.append(Spacer(1, 15))
    
    # Add horizontal line
    content.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))
    
    # Customer details
    content.append(Paragraph("<b>Bill To / Ship To</b>", styles['Normal']))
    content.append(Spacer(1, 5))
    
    # Format customer name and address with wrapping for long text
    customer_name = order.full_name or order.user.full_name()
    customer_address = f"{order.address}"
    if hasattr(order, 'shipping_locality') and order.shipping_locality:
        customer_address += f", {order.shipping_locality}"
    
    # Check if address is too long and add line breaks for PDF
    if len(customer_address) > 60:
        words = customer_address.split()
        customer_address = ""
        line = ""
        for word in words:
            if len(line + " " + word) > 60:
                customer_address += line + "<br/>"
                line = word
            else:
                line = line + " " + word if line else word
        customer_address += line

    customer_city = f"{order.city}, {order.state} - {order.zipcode}"
    customer_phone = order.phone or order.user.phone
    
    content.append(Paragraph(f"Name: {customer_name}", styles['Normal']))
    content.append(Paragraph(f"Address: {customer_address}", styles['Normal']))
    content.append(Paragraph(f"{customer_city}", styles['Normal']))
    content.append(Paragraph(f"Phone: {customer_phone}", styles['Normal']))
    
    content.append(Spacer(1, 15))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))

    # Add order items
    content.append(Paragraph("<b>Order Items</b>", styles['Normal']))
    content.append(Spacer(1, 5))

    # Create table data with headers using Paragraph objects for proper formatting
    table_data = [[
        Paragraph("<b>Item</b>", styles['Normal']),
        Paragraph("<b>Qty</b>", styles['Normal']),
        Paragraph("<b>Price</b>", styles['Normal']),
        Paragraph("<b>CGST (9%)</b>", styles['Normal']),
        Paragraph("<b>SGST (9%)</b>", styles['Normal']),
        Paragraph("<b>Total</b>", styles['Normal'])
    ]]

    # Add items to table
    item_total = 0
    for item in order.items:
        product = item.product
        price = item.price
        item_subtotal = price * item.quantity
        item_total += item_subtotal
        
        # Calculate GST - 18% split as 9% CGST and 9% SGST
        gst_per_item = price * 0.18
        cgst = gst_per_item / 2
        sgst = gst_per_item / 2
        
        # Calculate the base price without GST
        base_price = price / 1.18
        
        # Use Paragraph for product name to allow for automatic wrapping
        product_name = product.name
        product_name_paragraph = Paragraph(product_name, styles['Normal'])
            
        table_data.append([
            product_name_paragraph,
            str(item.quantity),
            f"{rupee_symbol} {base_price:.2f}",
            f"{rupee_symbol} {cgst:.2f}",
            f"{rupee_symbol} {sgst:.2f}",
            f"{rupee_symbol} {price:.2f}"
        ])

    # Calculate tax totals
    subtotal_without_gst = item_total / 1.18
    total_tax = item_total - subtotal_without_gst
    cgst_total = total_tax / 2
    sgst_total = total_tax / 2

    # Create table
    table = Table(table_data, colWidths=[200, 40, 80, 70, 70, 70])

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('WORDWRAP', (0, 0), (0, -1), True),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    content.append(table)
    content.append(Spacer(1, 10))

    # Add summary table with tax breakdown
    summary_data = [
        ["", "Subtotal (Excl. GST):", f"{rupee_symbol} {subtotal_without_gst:.2f}"],
        ["", "CGST (9%):", f"{rupee_symbol} {cgst_total:.2f}"],
        ["", "SGST (9%):", f"{rupee_symbol} {sgst_total:.2f}"],
        ["", "Total GST (18%):", f"{rupee_symbol} {total_tax:.2f}"],
        ["", "Grand Total:", f"{rupee_symbol} {item_total:.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[320, 100, 80])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (1, -1), (2, -1), bold_font),
        ('LINEABOVE', (1, -1), (2, -1), 1, colors.black),
        ('LINEBELOW', (1, -1), (2, -1), 1, colors.black),
    ]))

    content.append(summary_table)
    content.append(Spacer(1, 20))
    
    # Add warranty information
    content.append(Paragraph("<b>Warranty:</b> Manufacturer warranty applicable as per product specifications.", styles['Normal']))
    content.append(Spacer(1, 15))

    # Add signature and stamp
    from reportlab.platypus import Image as ReportLabImage
    
    signature_stamp_data = [
        [Paragraph('Authorized Signatory:', styles['Normal']), ""],
        [
            ReportLabImage(signature_path, width=1.5 * inch, height=0.7 * inch),
            ReportLabImage(stamp_path, width=1.1 * inch, height=1.1 * inch)
        ],
        [Paragraph('SS PC Assembler', styles['Normal']), ""],
    ]

    signature_stamp_table = Table(signature_stamp_data, colWidths=[300, 220])
    signature_stamp_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    content.append(signature_stamp_table)
    content.append(Spacer(1, 15))
    
    # Add horizontal line
    content.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))
    
    # Add terms and notes
    content.append(Paragraph("<b>Terms & Notes</b>", styles['Normal']))
    content.append(Spacer(1, 5))
    content.append(Paragraph("• Returns only accepted within 7 days for defective parts.", styles['Normal']))
    content.append(Paragraph("• Prices inclusive of applicable taxes.", styles['Normal']))
    content.append(Paragraph("• Keep this invoice safe for warranty claims.", styles['Normal']))
    content.append(Spacer(1, 15))

    # Add footer
    content.append(Paragraph("Thank you for shopping with SS PC Assembler!", styles['Center']))
    content.append(Spacer(1, 10))
    content.append(
        Paragraph(
            "This is a computer-generated invoice and does not require a physical signature.",
            styles['Small']))

    # Build the PDF
    doc.build(content)

    return filename
