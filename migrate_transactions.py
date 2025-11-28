"""
Migration Script: Add Missing Required Fields to Transactions
This script updates all existing transactions in the database to include
required fields that might be missing from legacy data.
"""

import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.core.database import connect_to_mongo, close_mongo_connection, get_transactions_collection

async def migrate_transactions():
    print("=" * 60)
    print("Transaction Migration Script")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n1. Connecting to MongoDB...")
        await connect_to_mongo()
        print("   ✅ Connected")
        
        # Get transactions collection
        collection = get_transactions_collection()
        
        # Count total transactions
        total = await collection.count_documents({})
        print(f"\n2. Found {total} transactions in database")
        
        if total == 0:
            print("   No transactions to migrate.")
            return
        
        # Define default values for missing fields
        defaults = {
            "counterparty": "Unknown",
            "message": "No description",
            "category": "general",
            "txn_type": "Unknown"
        }
        
        # Update transactions with missing fields
        print("\n3. Updating transactions with missing fields...")
        updated_count = 0
        
        for field, default_value in defaults.items():
            # Find documents missing this field or where it's null/empty
            query = {
                "$or": [
                    {field: {"$exists": False}},
                    {field: None},
                    {field: ""}
                ]
            }
            
            # Update with default value
            result = await collection.update_many(
                query,
                {"$set": {field: default_value}}
            )
            
            if result.modified_count > 0:
                print(f"   • Set '{field}' = '{default_value}' for {result.modified_count} transactions")
                updated_count += result.modified_count
        
        print(f"\n4. Migration complete!")
        print(f"   • Total transactions: {total}")
        print(f"   • Updated fields: {updated_count}")
        print("\n✅ All transactions now have required fields")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n⚠️  This script will update your transaction database.")
    print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
    
    import time
    try:
        time.sleep(3)
        asyncio.run(migrate_transactions())
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
