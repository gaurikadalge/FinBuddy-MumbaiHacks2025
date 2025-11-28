"""
Quick Fix Migration - Handles List Values
Specifically fixes counterparty=['TestCoff'] -> counterparty='TestCoff'
"""

import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.core.database import connect_to_mongo, close_mongo_connection, get_transactions_collection

async def fix_lists():
    print("Fixing list values in database...")
    
    try:
        await connect_to_mongo()
        print("Connected to MongoDB\n")
        
        collection = get_transactions_collection()
        all_docs = await collection.find({}).to_list(None)
        
        print(f"Found {len(all_docs)} transactions\n")
        
        fixed = 0
        
        for doc in all_docs:
            updates = {}
            
            # Helper to convert lists to strings
            def list_to_string(value):
                if isinstance(value, list):
                    if len(value) > 0:
                        return str(value[0])  # Take first element
                    return ""
                return value
            
            # Fix all string fields that might be lists
            for field in ['counterparty', 'message', 'category', 'txn_type', 'ai_insight', 'compliance_alert']:
                if field in doc:
                    value = doc[field]
                    if isinstance(value, list):
                        new_value = list_to_string(value)
                        updates[field] = new_value
                        print(f"  Fixed {field}: {value} -> '{new_value}'")
            
            if updates:
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": updates}
                )
                fixed += 1
        
        print(f"\nFixed {fixed} transactions with list values")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(fix_lists())
