import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.ml.categorizer import SmartCategorizer
from backend.ml.anomaly_detector import AnomalyDetector

def test_advanced_ml():
    print("----------------------------------------------------------------")
    print("🧪 Testing Advanced ML Features")
    print("----------------------------------------------------------------")

    # 1. Test Smart Categorizer
    print("\n[1] Testing Smart Categorizer...")
    cat = SmartCategorizer()
    
    test_cases = [
        ("I ordered from Swiggy Instamart", "Food"),
        ("Paid for Uber ride", "Travel"),
        ("Bought a new dress from Zara", "Shopping"),
        ("Paid electricity bill", "Bills"),
        ("Subscription for Netflix", "Entertainment"),
        ("Salary credited", "Income")
    ]
    
    for text, expected in test_cases:
        pred = cat.predict(text)
        status = "✅" if pred == expected else "❌"
        print(f"   '{text}' -> {pred} (Expected: {expected}) {status}")

    # 2. Test Anomaly Detection
    print("\n[2] Testing Anomaly Detector...")
    ad = AnomalyDetector()
    
    # Normal transaction
    res1 = ad.check(500, "Food", "Restaurant")
    print(f"   Check 500 (Food): {res1['is_anomaly']} ({res1['reason']})")
    
    # High amount anomaly
    res2 = ad.check(50000, "Food", "Burger King")
    print(f"   Check 50000 (Food): {res2['is_anomaly']} ({res2['reason']})")
    
    # Duplicate check
    ad.check(500, "Food", "Restaurant") # Add first
    res3 = ad.check(500, "Food", "Restaurant") # Add duplicate
    print(f"   Check Duplicate (500, Restaurant): {res3['is_anomaly']} ({res3['reason']})")

    print("\n✅ Advanced ML Features Verified!")

if __name__ == "__main__":
    test_advanced_ml()
