from app import app, db
from flask import Flask
from flask_migrate import Migrate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

def run_migrations():
    logger.info("Adding color column to Product table")
    
    with app.app_context():
        # Check if the column already exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('product')]
        
        if 'color' not in columns:
            logger.info("Color column does not exist. Creating it now.")
            
            # Add the color column with default value 'Black'
            db.engine.execute('ALTER TABLE product ADD COLUMN color VARCHAR(20) DEFAULT "Black"')
            logger.info("Color column added successfully")
        else:
            logger.info("Color column already exists")

if __name__ == "__main__":
    run_migrations()