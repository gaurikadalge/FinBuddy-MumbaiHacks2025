import sys
import os
sys.path.append(os.getcwd())

from backend.ml.voice_semantics import VoiceSemanticsModel
from backend.ml.chart_explainer import ChartExplainer
from backend.ml.reasoning_engine import MultimodalReasoningEngine

def test_voice_semantics():
    print("\n--- Testing Voice Semantics ---")
    model = VoiceSemanticsModel()
    
    phrases = [
        "I need to pay this bill immediately",
        "I regret buying that expensive watch",
        "I want to save for a new car",
        "Just checking my balance"
    ]
    
    for text in phrases:
        result = model.analyze_semantics(text)
        print(f"Text: '{text}' -> Tags: {result['tags']}, Sentiment: {result['sentiment']}")

def test_chart_explainer():
    print("\n--- Testing Chart Explainer ---")
    explainer = ChartExplainer()
    
    # Trend
    data = [1000, 1200, 1500, 2000]
    labels = ["Jan", "Feb", "Mar", "Apr"]
    trend = explainer.explain_spending_trend(data, labels)
    print(f"Trend Insight: {trend}")
    
    # Category
    cats = {"Food": 5000, "Rent": 15000, "Travel": 2000}
    cat_insights = explainer.explain_category_pie(cats)
    print(f"Category Insights: {cat_insights}")

def test_reasoning_engine():
    print("\n--- Testing Reasoning Engine ---")
    engine = MultimodalReasoningEngine()
    
    # Context
    txn = {"amount": 6000, "category": "Food", "counterparty": "Fancy Restaurant"}
    context = engine.analyze_context(txn, source="voice")
    print(f"Context Analysis: {context}")
    
    # Anomaly
    history = [
        {"amount": 500, "category": "Food"},
        {"amount": 600, "category": "Food"},
        {"amount": 550, "category": "Food"}
    ]
    current = {"amount": 2000, "category": "Food"}
    anomalies = engine.detect_anomalies(current, history)
    print(f"Anomalies: {anomalies}")

if __name__ == "__main__":
    test_voice_semantics()
    test_chart_explainer()
    test_reasoning_engine()
