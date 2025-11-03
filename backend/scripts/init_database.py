#!/usr/bin/env python3
"""
Database Initialization Script
Creates all database tables from SQLAlchemy models
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db import Base, engine, DATABASE_URL
from models.Transcation import TransactionDB
from models.ledger import TransactionLedger
from sqlalchemy import inspect


def create_tables():
    """Create all database tables from SQLAlchemy models"""
    print(f"Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    # Import all models to register them with Base
    # SQLAlchemy needs all models imported before create_all()
    print("Creating database tables...")
    
    try:
        # Drop all tables (CAUTION: This deletes all data!)
        # Uncomment if you need to reset the database
        # print("⚠️  Dropping all existing tables...")
        # Base.metadata.drop_all(engine)
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)


def verify_connection():
    """Verify database connection"""
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL is set correctly in .env")
        print("  3. Database credentials are correct")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("InvestIQ Database Initialization")
    print("=" * 60)
    print()
    
    if not verify_connection():
        sys.exit(1)
    
    print()
    create_tables()
    print()
    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)

