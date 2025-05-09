from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    zipcode = db.Column(db.String(20))
    locality = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    cart_items = db.relationship('CartItem',
                                 backref='user',
                                 lazy=True,
                                 cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem',
                                     backref='user',
                                     lazy=True,
                                     cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50),
                         nullable=False)  # cpu, gpu, motherboard, etc.
    color = db.Column(db.String(20), default='Black')  # For products with color options (Black, White)
    image_url = db.Column(db.String(200))
    specs_json = db.Column(db.Text, name='specs')  # JSON string of specs
    is_featured = db.Column(db.Boolean, default=False, name='is_featured')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    wishlist_items = db.relationship('WishlistItem',
                                     backref='product',
                                     lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    @property
    def specs(self):
        if self.specs_json:
            return json.loads(self.specs_json)
        return {}

    @specs.setter
    def specs(self, specs_dict):
        self.specs_json = json.dumps(specs_dict)
        
    @property
    def featured(self):
        return self.is_featured
        
    @featured.setter
    def featured(self, value):
        self.is_featured = value


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)
    quantity = db.Column(db.Integer, default=1)
    # Commented out for now as this column might not exist in the DB
    # added_at = db.Column(db.DateTime, default=datetime.utcnow)


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)
    # Commented out for now as this column might not exist in the DB
    # added_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20),
        default='pending')  # pending, processing, shipped, completed
    payment_method = db.Column(db.String(50))
    # Commented out as this column doesn't exist in the database yet
    # transaction_id = db.Column(db.String(100))
    
    # Customer information
    full_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Address information - using actual column names from database
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    zipcode = db.Column(db.String(20))
    
    # Extended address information
    shipping_locality = db.Column(db.String(100), nullable=True)
    shipping_landmark = db.Column(db.String(100), nullable=True)
    alt_phone = db.Column(db.String(20), nullable=True)
    address_type = db.Column(db.String(20), default='home')  # home or work
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem',
                            backref='order',
                            lazy=True,
                            cascade='all, delete-orphan')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float,
                      nullable=False)  # Price at the time of purchase
