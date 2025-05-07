from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import User, Product, Order, OrderItem
from forms import ProductForm
import json

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))


@admin_bp.route('/')
@login_required
def index():
    # Dashboard statistics
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Revenue statistics
    revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    # Stock statistics
    low_stock_products = Product.query.filter(Product.stock < 10).all()
    
    return render_template('admin/index.html', 
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           recent_orders=recent_orders,
                           revenue=revenue,
                           low_stock_products=low_stock_products)


@admin_bp.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    products_query = Product.query
    
    if category:
        products_query = products_query.filter_by(category=category)
    
    products = products_query.order_by(Product.id).paginate(page=page, per_page=15)
    
    categories = [
        {'id': 'cpu', 'name': 'CPU'},
        {'id': 'gpu', 'name': 'GPU'},
        {'id': 'motherboard', 'name': 'Motherboard'},
        {'id': 'ram', 'name': 'RAM'},
        {'id': 'storage', 'name': 'Storage'},
        {'id': 'psu', 'name': 'PSU'},
        {'id': 'case', 'name': 'Case'},
        {'id': 'cooling', 'name': 'Cooling'},
        {'id': 'peripherals', 'name': 'Peripherals'},
        {'id': 'monitor', 'name': 'Monitor'},
        {'id': 'prebuilt_intel', 'name': 'Prebuilt PC - Intel'},
        {'id': 'prebuilt_amd', 'name': 'Prebuilt PC - AMD'}
    ]
    
    return render_template('admin/products.html', products=products, categories=categories, current_category=category)


@admin_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    
    if form.validate_on_submit():
        specs = {}
        if form.specs.data:
            try:
                specs = json.loads(form.specs.data)
            except json.JSONDecodeError:
                flash('Invalid JSON format for specifications', 'danger')
                return render_template('admin/add_product.html', form=form)
        
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category=form.category.data,
            image_url=form.image_url.data,
            featured=form.featured.data
        )
        product.specs = specs
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html', form=form)


@admin_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    
    if request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.stock.data = product.stock
        form.category.data = product.category
        form.image_url.data = product.image_url
        form.featured.data = product.featured
        form.specs.data = json.dumps(product.specs, indent=2)
    
    if form.validate_on_submit():
        specs = {}
        if form.specs.data:
            try:
                specs = json.loads(form.specs.data)
            except json.JSONDecodeError:
                flash('Invalid JSON format for specifications', 'danger')
                return render_template('admin/edit_product.html', form=form, product=product)
        
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category = form.category.data
        product.image_url = form.image_url.data
        product.featured = form.featured.data
        product.specs = specs
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', form=form, product=product)


@admin_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    orders_query = Order.query
    
    if status:
        orders_query = orders_query.filter_by(status=status)
    
    orders = orders_query.order_by(Order.created_at.desc()).paginate(page=page, per_page=15)
    
    statuses = ['pending', 'processing', 'shipped', 'completed']
    
    return render_template('admin/orders.html', orders=orders, statuses=statuses, current_status=status)


@admin_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    return render_template('admin/order_detail.html', order=order, order_items=order_items)


@admin_bp.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    
    if status in ['pending', 'processing', 'shipped', 'completed']:
        order.status = status
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('admin.order_detail', order_id=order.id))


@admin_bp.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=15)
    
    return render_template('admin/users.html', users=users)


@admin_bp.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow admin to remove their own admin status
    if user.id == current_user.id:
        flash('You cannot change your own admin status', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'Admin status for {user.username} updated successfully!', 'success')
    return redirect(url_for('admin.users'))
