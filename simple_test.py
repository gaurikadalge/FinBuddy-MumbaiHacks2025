import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.services.chat_manager import ChatManager
from backend.core.database import connect_to_mongo, close_mongo_connection

async def test():
    await connect_to_mongo()
    cm = ChatManager()
    res = await cm.process_message("user1", "whats my balance")
    await close_mongo_connection()
    
    with open("simple_test_output.txt", "w") as f:
        f.write(f"Type: {res.get('type')}\n")
        f.write(f"Text: {res.get('text')}\n")
        f.write(f"Intent: {res.get('intent')}\n")
    
    print("Done")

asyncio.run(test())
