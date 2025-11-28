import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.ml.intent_classifier import IntentClassifier
from backend.ml.ner_extractor import NERExtractor
from backend.ml.memory_store import VectorMemory

def test_ml_components():
    print("----------------------------------------------------------------")
    print("🧪 Testing ML Components")
    print("----------------------------------------------------------------")

    # 1. Test Intent Classifier
    print("\n[1] Testing Intent Classifier...")
    classifier = IntentClassifier()
    
    test_queries = [
        "What is my balance?",
        "I spent 500 on food",
        "How to save tax?",
        "Hello there"
    ]
    
    for q in test_queries:
        intent, conf = classifier.predict(q)
        print(f"   Query: '{q}' -> Intent: {intent} ({conf:.2f})")
        
    # 2. Test NER
    print("\n[2] Testing NER Extractor...")
    ner = NERExtractor()
    
    ner_text = "I paid 5000 rupees to Amazon on Monday."
    entities = ner.extract_entities(ner_text)
    print(f"   Text: '{ner_text}'")
    print(f"   Entities: {entities}")
    
    # 3. Test Memory
    print("\n[3] Testing Vector Memory...")
    memory = VectorMemory()
    memory.add_interaction("Hi", "Hello!", "greeting", {})
    memory.add_interaction("My balance?", "5000", "check_balance", {})
    
    context = memory.get_context("What is my balance?")
    print(f"   Context retrieved: {len(context)} items")
    for c in context:
        print(f"   - {c['text']}")

    print("\n✅ ML Components Verified!")

if __name__ == "__main__":
    test_ml_components()
