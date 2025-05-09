"""
This script forces the database to be reinitialized with the updated products.
Run this script once to update the database with the new Intel CPUs.
"""

from data import init_db

if __name__ == '__main__':
    # Force database reinitialization by passing force=True
    init_db(force=True)
    print("Database has been reinitialized with new Intel CPU products.")