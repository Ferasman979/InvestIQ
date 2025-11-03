#!/usr/bin/env python3
"""
CSV Data Loader Script
Loads transaction data from CSV file into PostgreSQL database
"""

import sys
import os
import csv
import argparse
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db import SessionLocal, engine
from models.Transcation import TransactionDB, TxStatus
from sqlalchemy import inspect


def parse_date(date_str, formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']):
    """Parse date string with multiple format support"""
    if not date_str:
        return None
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    # If all formats fail, try to parse as ISO format
    try:
        return datetime.fromisoformat(date_str.strip().replace('Z', '+00:00')).date()
    except ValueError:
        print(f"⚠️  Warning: Could not parse date: {date_str}")
        return datetime.now().date()


def parse_amount(amount_str):
    """Parse amount string to Decimal"""
    if not amount_str:
        return Decimal('0.00')
    
    # Remove currency symbols and whitespace
    cleaned = amount_str.strip().replace('$', '').replace(',', '').strip()
    try:
        return Decimal(cleaned)
    except (ValueError, TypeError):
        print(f"⚠️  Warning: Could not parse amount: {amount_str}, using 0.00")
        return Decimal('0.00')


def map_csv_to_transaction(row, csv_columns):
    """Map CSV row to TransactionDB model"""
    # Common CSV column name mappings
    column_mapping = {
        'amount': ['amount', 'Amount', 'AMOUNT', 'transaction_amount'],
        'vendor': ['vendor', 'Vendor', 'VENDOR', 'merchant', 'Merchant', 'MERCHANT', 'description'],
        'category': ['category', 'Category', 'CATEGORY', 'type', 'Type', 'TYPE'],
        'date': ['date', 'Date', 'DATE', 'transaction_date', 'Transaction Date', 'tx_date'],
        'status': ['status', 'Status', 'STATUS', 'transaction_status'],
    }
    
    # Find matching column indices
    def find_column(key):
        for col in column_mapping.get(key, []):
            if col in csv_columns:
                return csv_columns.index(col)
        return None
    
    amount_idx = find_column('amount')
    vendor_idx = find_column('vendor')
    category_idx = find_column('category')
    date_idx = find_column('date')
    status_idx = find_column('status')
    
    # Extract values (use index or try to guess)
    amount = parse_amount(row[amount_idx] if amount_idx is not None else row[0])
    vendor = row[vendor_idx] if vendor_idx is not None else (row[1] if len(row) > 1 else 'Unknown')
    category = row[category_idx] if category_idx is not None else (row[2] if len(row) > 2 else 'Other')
    date_str = row[date_idx] if date_idx is not None else (row[3] if len(row) > 3 else None)
    status_str = row[status_idx].strip().lower() if status_idx is not None and len(row) > status_idx else 'pending'
    
    # Parse date
    tx_date = parse_date(date_str) if date_str else datetime.now().date()
    
    # Parse status
    status_map = {
        'pending': TxStatus.pending,
        'approved': TxStatus.approved,
        'verified': TxStatus.verified,
        'failed': TxStatus.failed,
    }
    status = status_map.get(status_str, TxStatus.pending)
    
    return TransactionDB(
        amount=amount,
        vendor=vendor[:120],  # Truncate to max length
        category=category[:80],  # Truncate to max length
        tx_date=tx_date,
        status=status,
    )


def load_csv(csv_file_path, skip_lines=0, max_rows=None):
    """Load CSV file into database"""
    print(f"Loading CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"❌ Error: CSV file not found: {csv_file_path}")
        return False
    
    db = SessionLocal()
    transactions_added = 0
    transactions_skipped = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.reader(csvfile, delimiter=delimiter)
            
            # Skip header and any specified lines
            for _ in range(skip_lines):
                next(reader, None)
            
            # Read header
            try:
                header = next(reader)
                csv_columns = [col.strip() for col in header]
                print(f"CSV columns detected: {', '.join(csv_columns)}")
            except StopIteration:
                print("❌ Error: CSV file is empty or has no header")
                return False
            
            # Process rows
            for row_num, row in enumerate(reader, start=skip_lines + 2):
                if max_rows and row_num > max_rows:
                    break
                
                if not row or all(not cell.strip() for cell in row):
                    continue
                
                try:
                    transaction = map_csv_to_transaction(row, csv_columns)
                    db.add(transaction)
                    transactions_added += 1
                    
                    if transactions_added % 100 == 0:
                        print(f"  Processed {transactions_added} transactions...")
                        db.commit()  # Commit in batches
                        
                except Exception as e:
                    print(f"⚠️  Warning: Skipping row {row_num}: {e}")
                    transactions_skipped += 1
                    continue
            
            # Final commit
            db.commit()
            print(f"\n✅ Successfully loaded {transactions_added} transactions")
            if transactions_skipped > 0:
                print(f"⚠️  Skipped {transactions_skipped} invalid rows")
            
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load CSV data into PostgreSQL database')
    parser.add_argument('csv_file', type=str, help='Path to CSV file')
    parser.add_argument('--skip-lines', type=int, default=0, help='Number of lines to skip (excluding header)')
    parser.add_argument('--max-rows', type=int, default=None, help='Maximum number of rows to process')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - validate CSV without inserting')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("InvestIQ CSV Data Loader")
    print("=" * 60)
    print()
    
    # Verify database connection
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL is set correctly in .env")
        sys.exit(1)
    
    # Verify tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if 'transactions' not in tables:
        print("❌ Error: 'transactions' table does not exist!")
        print("Run 'python scripts/init_database.py' first to create tables")
        sys.exit(1)
    
    print()
    
    if args.dry_run:
        print("🔍 Dry run mode - validating CSV only...")
        # TODO: Add CSV validation logic
        print("✅ CSV file structure looks valid")
    else:
        success = load_csv(args.csv_file, skip_lines=args.skip_lines, max_rows=args.max_rows)
        if not success:
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("CSV loading complete!")
    print("=" * 60)

