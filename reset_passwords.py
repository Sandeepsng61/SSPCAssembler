from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_passwords():
    """Reset passwords for demo and admin accounts."""
    with app.app_context():
        # Update admin account
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            # Set new admin password
            admin.password_hash = generate_password_hash('admin123')
            print(f"Reset admin password: {admin.email}")
        else:
            print("Admin user not found")
            
        # Update demo account
        demo = User.query.filter_by(email='demo@mail.com').first()
        if demo:
            # Change 'newdemopass' to your desired demo password
            demo.password_hash = generate_password_hash('demo123')
            print(f"Reset demo password: {demo.email}")
        else:
            print("Demo user not found")
        
        # Commit changes
        db.session.commit()
        print("Password reset completed")

if __name__ == "__main__":
    reset_passwords()