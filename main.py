from app import app, db

# Initialize database tables
with app.app_context():
    from models import User, Product, CartItem, WishlistItem, Order, OrderItem
    db.create_all()

    # Import data module and initialize the database with products
    # Only force=True when you want to reset all products
    from data import init_db
    init_db(force=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
