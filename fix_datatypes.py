"""
Migration: Fix Data Types in Transactions
Converts all fields to proper types (strings for text fields)
"""

import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.core.database import connect_to_mongo, close_mongo_connection, get_transactions_collection

async def fix_datatypes():
    print("=" * 60)
    print("Fix Transaction Data Types")
    print("=" * 60)
    
    try:
        await connect_to_mongo()
        print("\n✅ Connected to MongoDB")
        
        collection = get_transactions_collection()
        
        # Get all transactions
        all_docs = await collection.find({}).to_list(None)
        print(f"\nFound {len(all_docs)} transactions")
        
        if len(all_docs) == 0:
            print("No transactions to fix.")
            return
        
        fixed_count = 0
        
        for doc in all_docs:
            updates = {}
            
            # Ensure counterparty is a string
            if "counterparty" in doc:
                if not isinstance(doc["counterparty"], str):
                    updates["counterparty"] = str(doc["counterparty"]) if doc["counterparty"] is not None else "Unknown"
            else:
                updates["counterparty"] = "Unknown"
            
            # Ensure message is a string
            if "message" in doc:
                if not isinstance(doc["message"], str):
                    updates["message"] = str(doc["message"]) if doc["message"] is not None else "No description"
            else:
                updates["message"] = "No description"
            
            # Ensure category is a string
            if "category" in doc:
                if not isinstance(doc["category"], str):
                    updates["category"] = str(doc["category"]) if doc["category"] is not None else "general"
            else:
                updates["category"] = "general"
            
            # Ensure txn_type is a string
            if "txn_type" in doc:
                if not isinstance(doc["txn_type"], str):
                    updates["txn_type"] = str(doc["txn_type"]) if doc["txn_type"] is not None else "Unknown"
            else:
                updates["txn_type"] = "Unknown"
            
            # Ensure ai_insight is a string or empty
            if "ai_insight" in doc:
                if not isinstance(doc["ai_insight"], str):
                    updates["ai_insight"] = str(doc["ai_insight"]) if doc["ai_insight"] is not None else ""
            else:
                updates["ai_insight"] = ""
            
            # Ensure compliance_alert is a string or empty
            if "compliance_alert" in doc:
                if not isinstance(doc["compliance_alert"], str):
                    updates["compliance_alert"] = str(doc["compliance_alert"]) if doc["compliance_alert"] is not None else ""
            else:
                updates["compliance_alert"] = ""
            
            # Apply updates if any
            if updates:
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": updates}
                )
                fixed_count += 1
                print(f"  Fixed transaction {doc['_id']}: {list(updates.keys())}")
        
        print(f"\n✅ Migration complete!")
        print(f"   • Fixed {fixed_count} transactions")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(fix_datatypes())
