import sys
import os
import asyncio

sys.path.append(os.getcwd())

from backend.ml.intent_classifier import IntentClassifier

async def test():
    ic = IntentClassifier()
    
    messages = [
        "whats my balance",
        "what's my balance?",
        "show my balance",
        "check balance"
    ]
    
    for msg in messages:
        intent, conf = ic.predict(msg)
        print(f"Message: '{msg}'")
        print(f"  Intent: {intent} (confidence: {conf:.2f})")
        print()

asyncio.run(test())
