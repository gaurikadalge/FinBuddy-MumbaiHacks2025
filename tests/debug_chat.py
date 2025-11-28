import sys
import os
import asyncio
import json

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.chat_manager import ChatManager
from backend.core.database import connect_to_mongo, close_mongo_connection

async def debug_chat():
    output = []
    output.append("=" * 60)
    output.append("🐞 Debugging Chat DB Integration")
    output.append("=" * 60)

    try:
        # Connect to DB
        await connect_to_mongo()
        
        cm = ChatManager()
        output.append("\n✅ ChatManager Initialized")
        
        # 1. Test Balance
        output.append("\n[1] Testing Balance Check...")
        res_bal = await cm.process_message("user1", "whats my balance")
        output.append("\nFull Response:")
        output.append(json.dumps(res_bal, indent=2))
        
        # 2. Test Add Transaction
        output.append("\n\n[2] Testing Add Transaction...")
        res_add = await cm.process_message("user1", "Spent 150 on DebugFood")
        output.append(f"Response Type: {res_add.get('type')}")
        output.append(f"Response Text: {res_add.get('text', '')[:200]}")
        
        # 3. Test History
        output.append("\n\n[3] Testing History...")
        res_hist = await cm.process_message("user1", "show recent transactions")
        output.append(f"Response Type: {res_hist.get('type')}")
        output.append(f"Response Text: {res_hist.get('text', '')[:200]}")
        
    except Exception as e:
        output.append(f"\n\n❌ Exception caught:")
        output.append(str(e))
        import traceback
        output.append(traceback.format_exc())
    finally:
        await close_mongo_connection()
    
    # Write to file
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    
    print("Debug output written to debug_output.txt")

if __name__ == "__main__":
    asyncio.run(debug_chat())
