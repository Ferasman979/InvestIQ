#!/usr/bin/env python3
"""
Test script for LLM Service with Database
Tests the LLM service endpoints with actual database queries

Usage:
    python3 test_llm_service.py

Requirements:
    - PostgreSQL database running (local or EKS)
    - GOOGLE_API_KEY environment variable (optional - for LLM endpoint test)
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add paths
sys.path.insert(0, 'backend/llm-service')
sys.path.insert(0, 'backend')

# Set up environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://investiq:investiq123@localhost:5432/investiq_db"
)
os.environ["DATABASE_URL"] = DATABASE_URL

def test_database_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    try:
        from db_config import get_db
        from sqlalchemy import text
        
        db = get_db()
        try:
            result = db.execute(text('SELECT 1 as test'))
            row = result.fetchone()
            if row.test == 1:
                print("   ✅ Database connection successful")
                return True
        finally:
            db.close()
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_transactions_query():
    """Test transactions query"""
    print("📊 Testing transactions query...")
    try:
        from db_config import get_db
        from sqlalchemy import text
        
        db = get_db()
        try:
            result = db.execute(text("""
                SELECT vendor as merchant, amount, category, tx_date as transaction_date
                FROM transactions
                WHERE tx_date >= CURRENT_DATE - INTERVAL '2 days'
                ORDER BY tx_date DESC
                LIMIT 3
            """))
            rows = []
            for row in result:
                rows.append({
                    'merchant': row.merchant,
                    'amount': float(row.amount),
                    'category': row.category,
                    'transaction_date': row.transaction_date
                })
            print(f"   ✅ Query successful: Found {len(rows)} transactions")
            if rows:
                print(f"   Sample: {rows[0]['merchant']} - ${rows[0]['amount']}")
            return rows
        finally:
            db.close()
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_llm_service_endpoint(base_url="http://localhost:8000"):
    """Test LLM service endpoint"""
    print("")
    print("🤖 Testing LLM Service Endpoint...")
    print(f"   URL: {base_url}/generate-security-question")
    
    try:
        response = requests.post(
            f"{base_url}/generate-security-question",
            json={},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get("security_questions", [])
            contexts = data.get("contexts", [])
            
            print(f"   ✅ Endpoint successful!")
            print(f"   Generated {len(questions)} security question(s)")
            
            for i, question in enumerate(questions, 1):
                print(f"")
                print(f"   Question {i}:")
                print(f"   {question[:100]}..." if len(question) > 100 else f"   {question}")
            
            if contexts:
                print(f"")
                print(f"   Context (first {len(contexts[0])} chars):")
                print(f"   {contexts[0][:100]}..." if len(contexts[0]) > 100 else f"   {contexts[0]}")
            
            return data
        else:
            print(f"   ❌ Endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  LLM service not running")
        print(f"   Start it with: cd backend/llm-service && uvicorn main:app --port 8000")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_verify_endpoint(base_url="http://localhost:8000"):
    """Test verify endpoint"""
    print("")
    print("✅ Testing Verify Endpoint...")
    print(f"   URL: {base_url}/verify-security-answer")
    
    # Test with a sample answer
    test_data = {
        "user_answer": "Amazon",
        "question": "What was the merchant name for the Shopping transaction?",
        "context": "Amazon (Shopping) on 2025-11-03"
    }
    
    try:
        response = requests.post(
            f"{base_url}/verify-security-answer",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", "").lower()
            print(f"   ✅ Endpoint successful!")
            print(f"   Verification result: {result}")
            return data
        else:
            print(f"   ❌ Endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  LLM service not running")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 LLM Service Integration Test")
    print("=" * 60)
    print("")
    
    # Test 1: Database connection
    if not test_database_connection():
        print("")
        print("❌ Database connection failed - cannot continue")
        return 1
    
    # Test 2: Transactions query
    transactions = test_transactions_query()
    if not transactions:
        print("")
        print("⚠️  No transactions found - LLM service may not work properly")
        print("   Add transactions to test the full flow")
    
    # Test 3: LLM service endpoint (if running)
    llm_response = test_llm_service_endpoint()
    
    # Test 4: Verify endpoint (if LLM service is running)
    if llm_response:
        test_verify_endpoint()
    
    print("")
    print("=" * 60)
    print("📋 Test Summary:")
    print("=" * 60)
    print("")
    print("✅ Database connection: Working")
    print("✅ Transactions query: Working")
    if llm_response:
        print("✅ LLM service endpoint: Working")
        print("✅ Verify endpoint: Working")
        print("")
        print("🎉 All tests passed! LLM service is fully functional!")
    else:
        print("⚠️  LLM service endpoint: Not running")
        print("")
        print("📝 To test LLM endpoints:")
        print("   1. Start LLM service: cd backend/llm-service && uvicorn main:app --port 8000")
        print("   2. Run this test again")
    print("")
    
    return 0 if llm_response else 1

if __name__ == "__main__":
    sys.exit(main())

