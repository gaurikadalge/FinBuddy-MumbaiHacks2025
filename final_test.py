import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.services.chat_manager import ChatManager
from backend.core.database import connect_to_mongo, close_mongo_connection

async def test():
    await connect_to_mongo()
    cm = ChatManager()
    
    # Test 1: Balance
    print("\n[TEST 1] Balance Query")
    print("-" * 50)
    res = await cm.process_message("user1", "whats my balance")
    print(f"Type: {res.get('type')}")
    print(f"Intent: {res.get('intent')}")
    if res.get('type') == 'balance':
        print("SUCCESS: Balance query worked!")
        print(f"Response preview: {res.get('text', '')[:100]}")
    else:
        print(f"FAILED: {res.get('text')}")
    
    # Test 2: Add Transaction
    print("\n[TEST 2] Add Transaction")
    print("-" * 50)
    res2 = await cm.process_message("user1", "Spent 250 on TestCoffee")
    print(f"Type: {res2.get('type')}")
    if res2.get('type') in ['transaction_action', 'transaction']:
        print("SUCCESS: Transaction added!")
    else:
        print(f"Response: {res2.get('text', '')[:100]}")
    
    # Test 3: History
    print("\n[TEST 3] Transaction History")
    print("-" * 50)
    res3 = await cm.process_message("user1", "show my transactions")
    print(f"Type: {res3.get('type')}")
    if res3.get('type') == 'history':
        print("SUCCESS: History retrieved!")
    else:
        print(f"Response: {res3.get('text', '')[:100]}")
    
    await close_mongo_connection()
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)

asyncio.run(test())
