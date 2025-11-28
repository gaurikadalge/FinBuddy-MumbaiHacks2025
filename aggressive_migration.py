"""
Aggressive Transaction Migration - Fixes All Data Issues
This script will:
1. Inspect all transactions
2. Fix data types
3. Add missing required fields
4. Ensure Pydantic compatibility
"""

import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.core.database import connect_to_mongo, close_mongo_connection, get_transactions_collection
from datetime import datetime

async def aggressive_migration():
    print("=" * 70)
    print("AGGRESSIVE TRANSACTION MIGRATION")
    print("=" * 70)
    
    try:
        await connect_to_mongo()
        print("\nConnected to MongoDB\n")
        
        collection = get_transactions_collection()
        
        # Get all transactions
        all_docs = await collection.find({}).to_list(None)
        total = len(all_docs)
        
        print(f"Found {total} transactions in database\n")
        
        if total == 0:
            print("No transactions to migrate.")
            return
        
        fixed_count = 0
        errors = []
        
        for i, doc in enumerate(all_docs, 1):
            print(f"[{i}/{total}] Processing transaction {doc.get('_id')}...")
            
            try:
                updates = {}
                
                # Helper function to ensure string type
                def ensure_string(value, default=""):
                    if value is None:
                        return default
                    if isinstance(value, str):
                        return value
                    if isinstance(value, (dict, list)):
                        return str(value) if value else default
                    return str(value)
                
                # Fix counterparty
                counterparty = doc.get("counterparty")
                if not isinstance(counterparty, str) or not counterparty:
                    updates["counterparty"] = ensure_string(counterparty, "Unknown")
                    print(f"   • Fixed counterparty: {type(counterparty).__name__} -> str")
                
                # Fix message
                message = doc.get("message")
                if not isinstance(message, str) or not message:
                    updates["message"] = ensure_string(message, "No description")
                    print(f"   • Fixed message: {type(message).__name__} -> str")
                
                # Fix category
                category = doc.get("category")
                if not isinstance(category, str) or not category:
                    updates["category"] = ensure_string(category, "general")
                    print(f"   • Fixed category: {type(category).__name__} -> str")
                
                # Fix txn_type
                txn_type = doc.get("txn_type")
                if not isinstance(txn_type, str) or not txn_type:
                    updates["txn_type"] = ensure_string(txn_type, "Unknown")
                    print(f"   • Fixed txn_type: {type(txn_type).__name__} -> str")
                
                # Fix amount - ensure it's a number
                amount = doc.get("amount")
                if amount is None:
                    updates["amount"] = 0.0
                    print(f"   • Fixed amount: None -> 0.0")
                elif not isinstance(amount, (int, float)):
                    try:
                        updates["amount"] = float(amount)
                        print(f"   • Fixed amount: {type(amount).__name__} -> float")
                    except:
                        updates["amount"] = 0.0
                        print(f"   • Fixed amount: invalid -> 0.0")
                
                # Fix date
                date = doc.get("date")
                if date is None:
                    updates["date"] = datetime.utcnow()
                    print(f"   • Fixed date: None -> now")
                elif isinstance(date, str):
                    try:
                        updates["date"] = datetime.fromisoformat(date.replace("Z", "+00:00"))
                    except:
                        updates["date"] = datetime.utcnow()
                        print(f"   • Fixed date: invalid string -> now")
                
                # Fix ai_insight
                ai_insight = doc.get("ai_insight")
                if not isinstance(ai_insight, str):
                    updates["ai_insight"] = ensure_string(ai_insight, "")
                    print(f"   • Fixed ai_insight: {type(ai_insight).__name__} -> str")
                
                # Fix compliance_alert
                compliance_alert = doc.get("compliance_alert")
                if not isinstance(compliance_alert, str):
                    updates["compliance_alert"] = ensure_string(compliance_alert, "")
                    print(f"   • Fixed compliance_alert: {type(compliance_alert).__name__} -> str")
                
                # Apply updates if any
                if updates:
                    await collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": updates}
                    )
                    fixed_count += 1
                    print(f"   ✅ Updated {len(updates)} fields")
                else:
                    print(f"   ✓ Already valid")
                
                print()
                
            except Exception as e:
                error_msg = f"Transaction {doc.get('_id')}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ Error: {e}\n")
        
        print("=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70)
        print(f"Total transactions: {total}")
        print(f"Fixed: {fixed_count}")
        print(f"Errors: {len(errors)}")
        
        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\n✅ All transactions successfully migrated!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()
        print("\n" + "=" * 70)

if __name__ == "__main__":
    print("\n⚠️  This will modify your database")
    print("Starting in 2 seconds...")
    
    import time
    try:
        time.sleep(2)
        asyncio.run(aggressive_migration())
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled")
