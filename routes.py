from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from models import User, Product, CartItem, WishlistItem, Order, OrderItem
from forms import LoginForm, RegistrationForm, ProfileForm, CheckoutForm, PaymentForm
from compatibility import check_compatibility, calculate_power_consumption
import json
from werkzeug.security import generate_password_hash
from datetime import datetime


@app.route('/')
def index():
    featured_products = Product.query.filter_by(featured=True).limit(8).all()
    cpu_products = Product.query.filter_by(category='cpu').limit(4).all()
    gpu_products = Product.query.filter_by(category='gpu').limit(4).all()
    return render_template('index.html', 
                           featured_products=featured_products,
                           cpu_products=cpu_products, 
                           gpu_products=gpu_products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('dashboard.html', orders=orders)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.country.data = current_user.country
        form.zipcode.data = current_user.zipcode
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.country = form.country.data
        current_user.zipcode = form.zipcode.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html', form=form)


@app.route('/components')
def components():
    categories = [
        {'id': 'cpu', 'name': 'CPU', 'icon': 'microchip'},
        {'id': 'gpu', 'name': 'GPU', 'icon': 'tv'},
        {'id': 'motherboard', 'name': 'Motherboard', 'icon': 'desktop'},
        {'id': 'ram', 'name': 'RAM', 'icon': 'memory'},
        {'id': 'storage', 'name': 'Storage', 'icon': 'hdd'},
        {'id': 'psu', 'name': 'Power Supply', 'icon': 'plug'},
        {'id': 'case', 'name': 'Cabinet', 'icon': 'server'},
        {'id': 'cooling', 'name': 'Cooling', 'icon': 'wind'},
        {'id': 'peripherals', 'name': 'Peripherals', 'icon': 'keyboard'},
        {'id': 'monitor', 'name': 'Monitor', 'icon': 'desktop'},
        {'id': 'gaming_console', 'name': 'Gaming Consoles', 'icon': 'play'}
    ]
    return render_template('components.html', categories=categories)


@app.route('/components/<category>')
def component_category(category):
    valid_categories = ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooling', 'peripherals', 'monitor', 'gaming_console']
    if category not in valid_categories:
        flash('Invalid component category', 'danger')
        return redirect(url_for('components'))
    
    page = request.args.get('page', 1, type=int)
    
    # Special handling for peripherals to show subcategories
    if category == 'peripherals':
        # Get all products with category starting with 'peripherals_'
        subcategories = db.session.query(Product.category, db.func.count(Product.id).label('count')) \
            .filter(Product.category.like('peripherals_%')) \
            .group_by(Product.category) \
            .all()
        
        # Create a dictionary of subcategory names
        subcategory_names = {
            'peripherals_wifi': 'WiFi Adapters',
            'peripherals_bluetooth': 'Bluetooth Adapters',
            'peripherals_mouse': 'Mouse',
            'peripherals_keyboard': 'Keyboards',
            'peripherals_combo': 'Keyboard & Mouse Combos',
            'peripherals_mousepad': 'Mouse Pads',
            'peripherals_speakers': 'Speakers',
            'peripherals_fans': 'Case Fans',
            'peripherals_pcie': 'PCI Expansion Cards'
        }
        
        # Format the subcategories for display
        formatted_subcategories = []
        for subcat, count in subcategories:
            if subcat in subcategory_names:
                formatted_subcategories.append({
                    'id': subcat,
                    'name': subcategory_names[subcat],
                    'count': count
                })
        
        return render_template('peripherals.html', subcategories=formatted_subcategories, category=category)
    else:
        # Normal category handling
        products = Product.query.filter_by(category=category).paginate(page=page, per_page=12)
        return render_template('component_category.html', products=products, category=category)


@app.route('/components/peripherals/<subcategory>')
def components_peripherals(subcategory):
    # Validate subcategory
    valid_subcategories = [
        'peripherals_wifi', 'peripherals_bluetooth', 'peripherals_mouse', 
        'peripherals_keyboard', 'peripherals_combo', 'peripherals_mousepad', 
        'peripherals_speakers', 'peripherals_fans', 'peripherals_pcie'
    ]
    
    if subcategory not in valid_subcategories:
        flash('Invalid peripheral subcategory', 'danger')
        return redirect(url_for('component_category', category='peripherals'))
    
    # Dictionary of subcategory display names
    subcategory_names = {
        'peripherals_wifi': 'WiFi Adapters',
        'peripherals_bluetooth': 'Bluetooth Adapters',
        'peripherals_mouse': 'Mouse',
        'peripherals_keyboard': 'Keyboards',
        'peripherals_combo': 'Keyboard & Mouse Combos',
        'peripherals_mousepad': 'Mouse Pads',
        'peripherals_speakers': 'Speakers',
        'peripherals_fans': 'Case Fans',
        'peripherals_pcie': 'PCI Expansion Cards'
    }
    
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category=subcategory).paginate(page=page, per_page=12)
    
    return render_template('component_category.html', 
                           products=products, 
                           category=subcategory,
                           category_display_name=subcategory_names.get(subcategory, 'Peripherals'))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if this is an AJAX request from the modal view
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('modal') == '1':
        return render_template('product_modal_view.html', product=product)
    
    # Normal page view
    related_products = Product.query.filter_by(category=product.category).filter(Product.id != product.id).limit(4).all()
    return render_template('product_detail.html', product=product, related_products=related_products)


@app.route('/pc-builder')
def pc_builder():
    categories = ['cpu', 'motherboard', 'ram', 'storage', 'gpu', 'psu', 'case', 'cooling']
    components = {}
    
    # Get components for each category
    for category in categories:
        if category == 'storage':
            # Split storage into three subcategories: NVMe, SSD, and HDD
            components['nvme'] = Product.query.filter(
                Product.category == 'storage',
                Product._specs.like('%"interface": "%NVMe%"%')
            ).all()
            
            components['ssd'] = Product.query.filter(
                Product.category == 'storage',
                Product._specs.like('%"interface": "%SATA%"%')
            ).all()
            
            components['hdd'] = Product.query.filter(
                Product.category == 'storage',
                Product._specs.like('%"form_factor": "%3.5%"%')
            ).all()
            
            # Also include storage components in the main category for backward compatibility
            components['storage'] = Product.query.filter_by(category='storage').all()
        else:
            components[category] = Product.query.filter_by(category=category).all()
    
    return render_template('pc_builder.html', categories=categories, components=components)


@app.route('/api/check-compatibility', methods=['POST'])
def api_check_compatibility():
    data = request.json
    components = {}
    
    # Get product objects for each component
    for category, product_id in data.items():
        product = Product.query.get(product_id)
        if product:
            components[category] = product
    
    compatibility_result = check_compatibility(components)
    power_consumption = calculate_power_consumption(components)
    
    return jsonify({
        'compatible': compatibility_result['compatible'],
        'issues': compatibility_result['issues'],
        'estimated_wattage': power_consumption
    })


@app.route('/cart')
def cart():
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart_items = []
        total = 0
        cart_data = session.get('cart', {})
        for product_id, quantity in cart_data.items():
            product = Product.query.get(int(product_id))
            if product:
                cart_items.append({
                    'product': product,
                    'quantity': quantity
                })
                total += product.price * quantity
    
    return render_template('cart.html', cart=cart_items, total=total)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    buy_now = request.form.get('buy_now') == 'true'
    
    product = Product.query.get_or_404(product_id)
    
    if quantity > product.stock:
        flash(f'Sorry, only {product.stock} items available in stock.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    if current_user.is_authenticated:
        # Check if product already in cart
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
    else:
        # For non-authenticated users, use session
        cart = session.get('cart', {})
        cart_product_id = str(product_id)
        
        if cart_product_id in cart:
            cart[cart_product_id] += quantity
        else:
            cart[cart_product_id] = quantity
            
        session['cart'] = cart
    
    flash(f'{product.name} added to cart!', 'success')
    
    # If buy_now is True, redirect to checkout/cart
    if buy_now:
        return redirect(url_for('checkout') if current_user.is_authenticated else url_for('cart'))
    
    return redirect(request.referrer or url_for('index'))


@app.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    if quantity < 1:
        flash('Quantity must be at least 1', 'danger')
        return redirect(url_for('cart'))
    
    product = Product.query.get_or_404(product_id)
    
    if quantity > product.stock:
        flash(f'Sorry, only {product.stock} items available in stock.', 'danger')
        return redirect(url_for('cart'))
    
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
        cart_item.quantity = quantity
        db.session.commit()
        
        # For AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            cart_total = sum(item.product.price * item.quantity for item in cart_items)
            return jsonify({
                'success': True,
                'item_total': product.price * quantity,
                'cart_total': cart_total
            })
    else:
        cart = session.get('cart', {})
        cart_product_id = str(product_id)
        
        if cart_product_id in cart:
            cart[cart_product_id] = quantity
            session['cart'] = cart
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                cart_total = 0
                for pid, qty in cart.items():
                    p = Product.query.get(int(pid))
                    if p:
                        cart_total += p.price * qty
                return jsonify({
                    'success': True,
                    'item_total': product.price * quantity,
                    'cart_total': cart_total
                })
    
    return redirect(url_for('cart'))


@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')
    
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
    else:
        cart = session.get('cart', {})
        cart_product_id = str(product_id)
        
        if cart_product_id in cart:
            del cart[cart_product_id]
            session['cart'] = cart
    
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))


@app.route('/empty-cart', methods=['POST'])
def empty_cart():
    if current_user.is_authenticated:
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
    else:
        session['cart'] = {}
    
    flash('Your cart has been emptied', 'success')
    return redirect(url_for('cart'))


@app.route('/add-to-wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    product_id = request.form.get('product_id')
    
    # Check if product already in wishlist
    wishlist_item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if not wishlist_item:
        wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Product added to wishlist!', 'success')
    else:
        flash('Product already in wishlist', 'info')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist=wishlist_items)


@app.route('/remove-from-wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    product_id = request.form.get('product_id')
    wishlist_item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
    db.session.delete(wishlist_item)
    db.session.commit()
    flash('Item removed from wishlist', 'success')
    return redirect(url_for('wishlist'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not current_user.is_authenticated:
        flash('Please login to proceed with checkout', 'warning')
        return redirect(url_for('login', next=url_for('checkout')))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty', 'info')
        return redirect(url_for('cart'))
    
    form = CheckoutForm()
    
    # Pre-fill form with user data if available
    if request.method == 'GET':
        form.full_name.data = f"{current_user.first_name} {current_user.last_name}".strip()
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.country.data = current_user.country
        form.zipcode.data = current_user.zipcode
    
    if form.validate_on_submit():
        # Store checkout info in session
        session['checkout_info'] = {
            'full_name': form.full_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'address': form.address.data,
            'city': form.city.data,
            'state': form.state.data,
            'country': form.country.data,
            'zipcode': form.zipcode.data,
            'payment_method': form.payment_method.data
        }
        return redirect(url_for('payment'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('checkout.html', form=form, cart=cart_items, total=total)


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    checkout_info = session.get('checkout_info')
    
    if not checkout_info:
        flash('Please complete checkout information first', 'warning')
        return redirect(url_for('checkout'))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty', 'info')
        return redirect(url_for('cart'))
    
    form = PaymentForm()
    
    if form.validate_on_submit():
        # Create order
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            payment_method=checkout_info['payment_method'],
            shipping_address=checkout_info['address'],
            shipping_city=checkout_info['city'],
            shipping_state=checkout_info['state'],
            shipping_country=checkout_info['country'],
            shipping_zipcode=checkout_info['zipcode'],
            contact_phone=checkout_info['phone']
        )
        
        # For payment methods other than COD, set transaction ID
        if checkout_info['payment_method'] != 'cod':
            order.transaction_id = f"TR{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        db.session.add(order)
        
        # Add order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update product stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            db.session.add(product)
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        # Clear checkout info from session
        session.pop('checkout_info', None)
        
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('payment.html', form=form, checkout_info=checkout_info, cart=cart_items, total=total)


@app.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    return render_template('order_confirmation.html', order=order, order_items=order_items)


@app.route('/generate-invoice/<int:order_id>')
@login_required
def generate_invoice(order_id):
    from utils import generate_invoice_pdf
    
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Generate the invoice PDF
    filename = generate_invoice_pdf(order)
    
    # Return the file for download
    return redirect(url_for('static', filename=f'invoices/{filename}'))


@app.route('/support')
def support():
    """Support/Contact page"""
    return render_template('support.html')


@app.route('/support/submit', methods=['POST'])
def support_submit():
    """Process support form submission"""
    # In a real implementation, this would send an email or create a support ticket
    # For now, we'll just redirect back to the support page with a success message
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    order_id = request.form.get('order_id')
    subject = request.form.get('subject')
    message = request.form.get('message')
    copy_me = 'copy_me' in request.form
    
    # Log the support request
    app.logger.info(f"Support request from {name} ({email}): {subject}")
    
    # Redirect with success parameter
    flash('Your support request has been submitted. Our team will contact you shortly.', 'success')
    return redirect(url_for('support', success='true'))


@app.route('/intel-pcs')
def intel_pcs():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category='prebuilt_intel').paginate(page=page, per_page=12)
    
    return render_template('intel_pcs.html', products=products)


@app.route('/amd-pcs')
def amd_pcs():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category='prebuilt_amd').paginate(page=page, per_page=12)
    
    return render_template('amd_pcs.html', products=products)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    if not query:
        return redirect(url_for('index'))
    
    products_query = Product.query.filter(Product.name.ilike(f'%{query}%') | 
                                         Product.description.ilike(f'%{query}%'))
    
    if category and category != 'all':
        products_query = products_query.filter_by(category=category)
    
    products = products_query.all()
    
    return render_template('search_results.html', products=products, query=query, category=category)


@app.route('/add-all-to-cart', methods=['POST'])
def add_all_to_cart():
    component_ids = {}
    for key, value in request.form.items():
        if key.startswith('components[') and key.endswith(']'):
            category = key[11:-1]  # Extract category from components[category]
            component_ids[category] = value
    
    for category, product_id in component_ids.items():
        product = Product.query.get(product_id)
        if product:
            if current_user.is_authenticated:
                # Check if product already in cart
                cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
                
                if cart_item:
                    cart_item.quantity += 1
                else:
                    cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
                    db.session.add(cart_item)
            else:
                # For non-authenticated users, use session
                cart = session.get('cart', {})
                cart_product_id = str(product_id)
                
                if cart_product_id in cart:
                    cart[cart_product_id] += 1
                else:
                    cart[cart_product_id] = 1
                    
                session['cart'] = cart
    
    if current_user.is_authenticated:
        db.session.commit()
    
    flash('All components added to cart!', 'success')
    return redirect(url_for('cart'))
