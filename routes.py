from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from models import User, Product, CartItem, WishlistItem, Order, OrderItem
from forms import LoginForm, RegistrationForm, ProfileForm, CheckoutForm, PaymentForm, ForgotPasswordForm, ResetPasswordForm
from compatibility import check_compatibility, calculate_power_consumption
import json
import secrets
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


@app.route('/')
def index():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
    featured_products = Product.query.filter_by(is_featured=True).limit(8).all()
    cpu_products = Product.query.filter_by(category='cpu').limit(4).all()
    gpu_products = Product.query.filter_by(category='gpu').limit(4).all()
    return render_template('index.html',
                           featured_products=featured_products,
                           cpu_products=cpu_products,
                           gpu_products=gpu_products,
                           get_default_product_image=get_default_product_image)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Better debugging for login issues
        app.logger.info(f"Login attempt for email: {email}")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('No account found with this email address', 'danger')
            app.logger.info(f"Login failed: No user found with email {email}")
            return render_template('login.html', form=form)
        
        # Check password
        is_valid = user.check_password(password)
        app.logger.info(f"Password check result: {is_valid}")
        
        if is_valid:
            login_user(user, remember=form.remember_me.data)
            app.logger.info(f"Login successful for user: {user.username}")
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Incorrect password', 'danger')
            app.logger.info(f"Login failed: Incorrect password for {email}")
    
    return render_template('login.html', form=form)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Reset link
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Here you would normally send an email with the reset link
            # For development purposes, we'll just display the link
            flash(f'Password reset link has been generated. Please check your email.', 'info')
            flash(f'Development Note: Reset URL: {reset_url}', 'warning')
            
            return redirect(url_for('login'))
        else:
            # Don't reveal if email exists in database for security reasons
            flash('If this email exists in our system, a password reset link has been sent.', 'info')
            
    return render_template('forgot_password.html', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Verify token
    user = User.query.filter_by(reset_token=token).first()
    
    # Check if token exists and is valid
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset link. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        
        # Clear reset token
        user.reset_token = None
        user.reset_token_expiry = None
        
        db.session.commit()
        flash('Your password has been successfully reset. You can now log in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username already exists. Please choose another username.', 'danger')
            else:
                flash('Email already registered. Please use another email or try to log in.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user if no conflicts
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating user: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
            
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(
        Order.created_at.desc()).all()
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
        form.locality.data = current_user.locality

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
        current_user.locality = form.locality.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile.html', form=form)


@app.route('/components')
def components():
    categories = [{
        'id': 'cpu',
        'name': 'CPU',
        'icon': 'microchip'
    }, {
        'id': 'gpu',
        'name': 'GPU',
        'icon': 'tv'
    }, {
        'id': 'motherboard',
        'name': 'Motherboard',
        'icon': 'desktop'
    }, {
        'id': 'ram',
        'name': 'RAM',
        'icon': 'memory'
    }, {
        'id': 'storage',
        'name': 'Storage',
        'icon': 'hdd'
    }, {
        'id': 'psu',
        'name': 'Power Supply',
        'icon': 'plug'
    }, {
        'id': 'case',
        'name': 'Cabinet',
        'icon': 'server'
    }, {
        'id': 'cooling',
        'name': 'Cooling',
        'icon': 'wind'
    }, {
        'id': 'peripherals',
        'name': 'Peripherals',
        'icon': 'keyboard'
    }, {
        'id': 'monitor',
        'name': 'Monitor',
        'icon': 'desktop'
    }, {
        'id': 'gaming_console',
        'name': 'Gaming Consoles',
        'icon': 'play'
    }]
    return render_template('components.html', categories=categories)


@app.route('/components/<category>')
def component_category(category):
    valid_categories = [
        'cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case',
        'cooling', 'peripherals', 'monitor', 'gaming_console', 
        'prebuilt_intel', 'prebuilt_amd'
    ]
    if category not in valid_categories:
        flash('Invalid component category', 'danger')
        return redirect(url_for('components'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', '')
    
    # Import the get_default_product_image function
    from utils import get_default_product_image

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

        return render_template('peripherals.html',
                               subcategories=formatted_subcategories,
                               category=category)
    else:
        # Normal category handling with search and sort capability
        query = Product.query.filter_by(category=category)
        
        # Apply search filter if provided
        if search:
            query = query.filter(
                Product.name.ilike(f'%{search}%') | 
                Product.description.ilike(f'%{search}%')
            )
        
        # Apply sorting if provided
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'newest':
            query = query.order_by(Product.created_at.desc())
        elif sort == 'name_asc':
            query = query.order_by(Product.name.asc())
        else:
            # Default sort by featured and then id
            query = query.order_by(Product.is_featured.desc(), Product.id.desc())
        
        products = query.paginate(page=page, per_page=12)
        
        category_display_name = category.replace('_', ' ').title()
        if category == 'prebuilt_intel':
            category_display_name = 'Intel Prebuilt PCs'
        elif category == 'prebuilt_amd':
            category_display_name = 'AMD Prebuilt PCs'
            
        return render_template('component_category.html',
                               products=products,
                               category=category,
                               category_display_name=category_display_name,
                               get_default_product_image=get_default_product_image)


@app.route('/components/peripherals/<subcategory>')
def components_peripherals(subcategory):
    # Validate subcategory
    valid_subcategories = [
        'peripherals_wifi', 'peripherals_bluetooth', 'peripherals_mouse',
        'peripherals_keyboard', 'peripherals_combo', 'peripherals_mousepad',
        'peripherals_speakers', 'peripherals_fans', 'peripherals_pcie'
    ]
    
    # Import the get_default_product_image function
    from utils import get_default_product_image

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
    search = request.args.get('search', '')
    sort = request.args.get('sort', '')
    
    # Base query
    query = Product.query.filter_by(category=subcategory)
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%') | 
            Product.description.ilike(f'%{search}%')
        )
    
    # Apply sorting if provided
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'newest':
        query = query.order_by(Product.created_at.desc())
    elif sort == 'name_asc':
        query = query.order_by(Product.name.asc())
    else:
        # Default sort by featured and then id
        query = query.order_by(Product.is_featured.desc(), Product.id.desc())
    
    products = query.paginate(page=page, per_page=12)

    return render_template('component_category.html',
                           products=products,
                           category=subcategory,
                           category_display_name=subcategory_names.get(
                               subcategory, 'Peripherals'),
                           get_default_product_image=get_default_product_image)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Import the get_default_product_image function
    from utils import get_default_product_image

    # Check if this is an AJAX request from the modal view
    if request.headers.get(
            'X-Requested-With') == 'XMLHttpRequest' or request.args.get(
                'modal') == '1':
        return render_template('product_modal_view.html', product=product)

    # Normal page view
    related_products = Product.query.filter_by(
        category=product.category).filter(
            Product.id != product.id).limit(4).all()
    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products,
                           get_default_product_image=get_default_product_image)


@app.route('/pc-builder')
def pc_builder():
    categories = [
        'cpu', 'motherboard', 'ram', 'storage', 'gpu', 'psu', 'case', 'cooling'
    ]
    components = {}

    # Get components for each category
    for category in categories:
        if category == 'storage':
            # Split storage into three subcategories: NVMe, SSD, and HDD
            components['nvme'] = Product.query.filter(
                Product.category == 'storage',
                Product.specs_json.like('%"interface": "%NVMe%"%')).all()

            components['ssd'] = Product.query.filter(
                Product.category == 'storage',
                Product.specs_json.like('%"interface": "%SATA%"%')).all()

            components['hdd'] = Product.query.filter(
                Product.category == 'storage',
                Product.specs_json.like('%"form_factor": "%3.5%"%')).all()

            # Also include storage components in the main category for backward compatibility
            components['storage'] = Product.query.filter_by(
                category='storage').all()
        else:
            components[category] = Product.query.filter_by(
                category=category).all()

    return render_template('pc_builder.html',
                           categories=categories,
                           components=components)


@app.route('/api/check-compatibility', methods=['POST'])
def api_check_compatibility():
    try:
        data = request.json
        if not data:
            return jsonify({
                'compatible': True,
                'issues': ["No components selected"],
                'estimated_wattage': 0
            })
            
        components = {}

        # Get product objects for each component
        for category, product_id in data.items():
            try:
                product_id = int(product_id)  # Ensure we have an integer ID
                product = Product.query.get(product_id)
                if product:
                    components[category] = product
            except (ValueError, TypeError):
                # Skip invalid product IDs
                continue

        if not components:
            return jsonify({
                'compatible': True,
                'issues': ["No valid components found"],
                'estimated_wattage': 0
            })

        # Perform compatibility check
        compatibility_result = check_compatibility(components)
        power_consumption = calculate_power_consumption(components)

        return jsonify({
            'compatible': compatibility_result['compatible'],
            'issues': compatibility_result['issues'],
            'estimated_wattage': power_consumption
        })
        
    except Exception as e:
        # Log error and return graceful fallback
        print(f"Error in compatibility check: {str(e)}")
        return jsonify({
            'compatible': True,
            'issues': ["Could not check compatibility. Try refreshing the page."],
            'estimated_wattage': 100
        })


@app.route('/cart')
def cart():
    # Import utility functions
    from utils import get_default_product_image, get_related_products
    
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
                cart_items.append({'product': product, 'quantity': quantity})
                total += product.price * quantity

    # Get recommended products based on cart items (if there are any)
    recommended_products = []
    if cart_items:
        for item in cart_items[:2]:  # Use first two items for recommendations
            product = item.product if hasattr(item, 'product') else item['product']
            related = get_related_products(product, limit=2)
            for rel_product in related:
                if rel_product not in recommended_products:
                    recommended_products.append(rel_product)
        
        # Limit to 4 products
        recommended_products = recommended_products[:4]

    return render_template('cart.html', 
                          cart=cart_items, 
                          total=total,
                          recommended_products=recommended_products,
                          get_default_product_image=get_default_product_image)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    buy_now = request.form.get('buy_now') == 'true'
    color = request.form.get('color')  # Get selected color if available

    product = Product.query.get_or_404(product_id)
    
    # Update product color if color selection was made and product category supports it
    if color and product.category in ['case', 'monitor', 'gpu', 'peripherals_keyboard', 'peripherals_mouse', 'peripherals_combo']:
        product.color = color
        db.session.commit()

    if quantity > product.stock:
        flash(f'Sorry, only {product.stock} items available in stock.',
              'danger')
        return redirect(request.referrer or url_for('index'))

    if current_user.is_authenticated:
        # Check if product already in cart
        cart_item = CartItem.query.filter_by(user_id=current_user.id,
                                             product_id=product_id).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=current_user.id,
                                 product_id=product_id,
                                 quantity=quantity)
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
        return redirect(
            url_for('checkout') if current_user.
            is_authenticated else url_for('cart'))

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
        flash(f'Sorry, only {product.stock} items available in stock.',
              'danger')
        return redirect(url_for('cart'))

    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product_id).first_or_404()
        cart_item.quantity = quantity
        db.session.commit()

        # For AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_items = CartItem.query.filter_by(
                user_id=current_user.id).all()
            cart_total = sum(item.product.price * item.quantity
                             for item in cart_items)
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
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product_id).first_or_404()
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
    wishlist_item = WishlistItem.query.filter_by(
        user_id=current_user.id, product_id=product_id).first()

    if not wishlist_item:
        wishlist_item = WishlistItem(user_id=current_user.id,
                                     product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Product added to wishlist!', 'success')
    else:
        flash('Product already in wishlist', 'info')

    return redirect(request.referrer or url_for('index'))


@app.route('/wishlist')
@login_required
def wishlist():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
    wishlist_items = WishlistItem.query.filter_by(
        user_id=current_user.id).all()
    
    # Get featured products for recommendations
    featured_products = Product.query.filter_by(is_featured=True).limit(4).all()
    
    return render_template('wishlist.html', 
                          wishlist=wishlist_items,
                          featured_products=featured_products,
                          get_default_product_image=get_default_product_image)


@app.route('/remove-from-wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    product_id = request.form.get('product_id')
    wishlist_item = WishlistItem.query.filter_by(
        user_id=current_user.id, product_id=product_id).first_or_404()
    db.session.delete(wishlist_item)
    db.session.commit()
    flash('Item removed from wishlist', 'success')
    return redirect(url_for('wishlist'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
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
        form.full_name.data = f"{current_user.first_name} {current_user.last_name}".strip(
        )
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
            'alt_phone': form.alt_phone.data if hasattr(form, 'alt_phone') else None,
            'address': form.address.data,
            'locality': form.locality.data if hasattr(form, 'locality') else None,
            'landmark': form.landmark.data if hasattr(form, 'landmark') else None,
            'address_type': form.address_type.data if hasattr(form, 'address_type') else 'home',
            'city': form.city.data,
            'state': form.state.data,
            'country': form.country.data,
            'zipcode': form.zipcode.data,
            'payment_method': form.payment_method.data
        }
        return redirect(url_for('payment'))

    total = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('checkout.html',
                           form=form,
                           cart=cart_items,
                           total=total,
                           get_default_product_image=get_default_product_image)


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
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
        total_amount = sum(item.product.price * item.quantity
                           for item in cart_items)

        order = Order(user_id=current_user.id,
                      total_amount=total_amount,
                      payment_method=checkout_info['payment_method'],
                      # Customer information
                      full_name=checkout_info['full_name'],
                      email=checkout_info['email'],
                      phone=checkout_info['phone'],
                      # Address information
                      address=checkout_info['address'],
                      city=checkout_info['city'],
                      state=checkout_info['state'],
                      country=checkout_info['country'],
                      zipcode=checkout_info['zipcode'],
                      # Extended information
                      shipping_locality=checkout_info.get('locality'),
                      shipping_landmark=checkout_info.get('landmark'),
                      alt_phone=checkout_info.get('alt_phone'),
                      address_type=checkout_info.get('address_type', 'home'))

        # For payment methods other than COD, set transaction ID
        if checkout_info['payment_method'] != 'cod':
            pass
            # Transaction ID is commented out in the model for now
            # order.transaction_id = f"TR{datetime.now().strftime('%Y%m%d%H%M%S')}"

        db.session.add(order)

        # Add order items
        for cart_item in cart_items:
            order_item = OrderItem(order=order,
                                   product_id=cart_item.product_id,
                                   quantity=cart_item.quantity,
                                   price=cart_item.product.price)
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

    return render_template('payment.html',
                           form=form,
                           checkout_info=checkout_info,
                           cart=cart_items,
                           total=total,
                           get_default_product_image=get_default_product_image)


@app.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
    order = Order.query.filter_by(id=order_id,
                                  user_id=current_user.id).first_or_404()
    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('order_confirmation.html',
                           order=order,
                           order_items=order_items,
                           get_default_product_image=get_default_product_image)


@app.route('/generate-invoice/<int:order_id>')
@login_required
def generate_invoice(order_id):
    from utils import generate_invoice_pdf

    order = Order.query.filter_by(id=order_id,
                                  user_id=current_user.id).first_or_404()

    # Generate the invoice PDF
    filename = generate_invoice_pdf(order)

    # Return the file for download
    return redirect(url_for('static', filename=f'invoices/{filename}'))


@app.route('/learn')
@app.route('/learn/<topic>')
def learn(topic=None):
    """Learn page with educational content about PC building"""
    topics = {
        'choosing_components': {
            'title': 'Choosing the Right Components',
            'description': 'Learn how to select the perfect components for your PC build based on your needs and budget.'
        },
        'building_process': {
            'title': 'The PC Building Process',
            'description': 'Step-by-step guide to assembling your PC from components to a working system.'
        },
        'troubleshooting': {
            'title': 'Troubleshooting Common Issues',
            'description': 'Solutions to common problems encountered during and after the PC building process.'
        },
        'tips_and_tricks': {
            'title': 'Tips & Tricks',
            'description': 'Expert advice and insider tips to enhance your PC building experience.'
        }
    }
    
    return render_template('learn.html', topic=topic, topics=topics)


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
    flash(
        'Your support request has been submitted. Our team will contact you shortly.',
        'success')
    return redirect(url_for('support', success='true'))


@app.route('/intel-pcs')
def intel_pcs():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category='prebuilt_intel').paginate(
        page=page, per_page=12)

    return render_template('intel_pcs.html', 
                          products=products,
                          get_default_product_image=get_default_product_image)


@app.route('/amd-pcs')
def amd_pcs():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category='prebuilt_amd').paginate(
        page=page, per_page=12)

    return render_template('amd_pcs.html', 
                          products=products,
                          get_default_product_image=get_default_product_image)


@app.route('/search')
def search():
    # Import the get_default_product_image function
    from utils import get_default_product_image
    
    query = request.args.get('q', '')
    category = request.args.get('category', '')

    if not query:
        return redirect(url_for('index'))

    products_query = Product.query.filter(
        Product.name.ilike(f'%{query}%')
        | Product.description.ilike(f'%{query}%'))

    if category and category != 'all':
        products_query = products_query.filter_by(category=category)

    products = products_query.all()

    return render_template('search.html',
                           products=products,
                           query=query,
                           category=category,
                           get_default_product_image=get_default_product_image)

# Location API Routes
@app.route('/api/states')
def get_states():
    """Get all states for India"""
    from location_data import STATES
    app.logger.debug(f"API: Fetching all states: {STATES}")
    return jsonify(STATES)

@app.route('/api/cities/<state_id>')
def get_cities_for_state(state_id):
    """Get cities for a state"""
    from location_data import get_cities
    cities = get_cities(state_id)
    app.logger.debug(f"API: Fetching cities for state {state_id}: {cities}")
    return jsonify(cities)

@app.route('/api/pincodes/<state_id>/<city_id>')
def get_pincodes_for_city(state_id, city_id):
    """Get pincodes for a city"""
    from location_data import get_pincodes
    pincodes = get_pincodes(state_id, city_id)
    return jsonify(pincodes if pincodes else {})

@app.route('/api/postoffices/<state_id>/<city_id>/<pincode>')
def get_postoffices_for_pincode(state_id, city_id, pincode):
    """Get post offices for a pincode"""
    from location_data import get_postoffices
    postoffices = get_postoffices(state_id, city_id, pincode)
    return jsonify(postoffices)


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
                cart_item = CartItem.query.filter_by(
                    user_id=current_user.id, product_id=product_id).first()

                if cart_item:
                    cart_item.quantity += 1
                else:
                    cart_item = CartItem(user_id=current_user.id,
                                         product_id=product_id,
                                         quantity=1)
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

