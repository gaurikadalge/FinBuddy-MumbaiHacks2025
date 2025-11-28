import sys
import os
import asyncio
import json

sys.path.append(os.getcwd())

from backend.core.database import connect_to_mongo, close_mongo_connection, get_transactions_collection

async def inspect_db():
    await connect_to_mongo()
    collection = get_transactions_collection()
    
    # Get first 5 transactions
    docs = await collection.find({}).limit(5).to_list(5)
    
    print(f"Found {len(docs)} transactions\n")
    
    for i, doc in enumerate(docs):
        print(f"Transaction {i+1}:")
        for key, value in doc.items():
            print(f"  {key}: {value} (type: {type(value).__name__})")
        print()
    
    await close_mongo_connection()

asyncio.run(inspect_db())
