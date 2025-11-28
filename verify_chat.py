import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

# Mock the TransactionService BEFORE importing ChatManager
# We need to patch the module where it's imported
from backend.services import chat_manager

# Create a mock service
mock_txn_service = MagicMock()
# Use AsyncMock for async methods
mock_txn_service.get_transactions_summary = AsyncMock(return_value={
    'total_credit': 50000,
    'total_debit': 20000,
    'net_balance': 30000,
    'ytd_credit': 600000
})
mock_txn_service.create_transaction = AsyncMock(return_value=True)

# Patch the class in the module
chat_manager.TransactionService = MagicMock(return_value=mock_txn_service)

from backend.services.chat_manager import ChatManager

async def test_chat():
    print("Initializing ChatManager (with mocked DB)...")
    chat = ChatManager()
    
    # Test 1: High Food Spend (Counseling Trigger)
    print("\n--- Test 1: High Food Spend ---")
    msg = "Spent 2500 on Food"
    response = await chat.process_message("user123", msg)
    print(f"User: {msg}")
    print(f"Bot: {response['text']}")
    
    if "That's a bit high" in response['text']:
        print("✅ Counseling logic triggered successfully!")
    else:
        print("❌ Counseling logic NOT triggered.")

    # Test 2: Normal Spend
    print("\n--- Test 2: Normal Spend ---")
    msg = "Spent 100 on Travel"
    response = await chat.process_message("user123", msg)
    print(f"User: {msg}")
    print(f"Bot: {response['text']}")

if __name__ == "__main__":
    asyncio.run(test_chat())
