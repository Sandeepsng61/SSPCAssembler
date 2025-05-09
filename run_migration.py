import logging
import sys
from app import app, db
from sqlalchemy import text

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run database migrations to add new columns to both order and user tables."""
    try:
        with app.app_context():
            # Check if order table columns already exist to avoid errors
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_order_columns = [c['name'] for c in inspector.get_columns('order')]
            existing_user_columns = [c['name'] for c in inspector.get_columns('user')]
            
            # Define the columns we want to add to the order table
            order_columns = {
                'shipping_locality': 'VARCHAR(100)',
                'shipping_landmark': 'VARCHAR(100)',
                'alt_phone': 'VARCHAR(20)',
                'address_type': 'VARCHAR(20) NOT NULL DEFAULT \'home\''
            }
            
            # Define the columns we want to add to the user table
            user_columns = {
                'reset_token': 'VARCHAR(100)',
                'reset_token_expiry': 'TIMESTAMP',
                'locality': 'VARCHAR(100)'
            }
            
            # Add columns to order table
            with db.engine.connect() as connection:
                # Add order columns
                for column_name, column_type in order_columns.items():
                    if column_name not in existing_order_columns:
                        logger.info(f"Adding column '{column_name}' to order table...")
                        sql = text(f"ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
                        connection.execute(sql)
                        connection.commit()
                        logger.info(f"Added column '{column_name}' to order table successfully")
                    else:
                        logger.info(f"Column '{column_name}' already exists in order table. Skipping.")
                
                # Add user columns
                for column_name, column_type in user_columns.items():
                    if column_name not in existing_user_columns:
                        logger.info(f"Adding column '{column_name}' to user table...")
                        sql = text(f"ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
                        connection.execute(sql)
                        connection.commit()
                        logger.info(f"Added column '{column_name}' to user table successfully")
                    else:
                        logger.info(f"Column '{column_name}' already exists in user table. Skipping.")
            
            logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()