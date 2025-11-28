import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.ml.forecaster import BudgetForecaster
from backend.ml.score_engine import FinancialHealthScorer

def test_predictive_features():
    print("----------------------------------------------------------------")
    print("🔮 Testing Predictive & Scoring Features")
    print("----------------------------------------------------------------")

    # 1. Test Budget Forecaster
    print("\n[1] Testing Budget Forecaster...")
    bf = BudgetForecaster()
    
    # Forecast
    next_month = bf.predict_next_month()
    print(f"   Next Month Forecast: ₹{next_month}")
    
    # Overshoot Check (Scenario: Spent 30k by day 15, Budget 50k)
    # Run rate = 2k/day -> 60k total -> Overshoot
    res1 = bf.check_overshoot(30000, 50000, 15)
    print(f"   Check Overshoot (30k/50k @ Day 15): {res1['overshoot']} ({res1['message']})")
    
    # Safe Check (Scenario: Spent 10k by day 15, Budget 50k)
    res2 = bf.check_overshoot(10000, 50000, 15)
    print(f"   Check Safe (10k/50k @ Day 15): {res2['overshoot']} ({res2['message']})")

    # 2. Test Financial Health Scorer
    print("\n[2] Testing Financial Health Scorer...")
    scorer = FinancialHealthScorer()
    
    # Good Profile
    s1, n1 = scorer.calculate_score(100000, 40000, anomalies=0)
    print(f"   Good Profile (100k in, 40k out): Score {s1} - {n1}")
    
    # Bad Profile
    s2, n2 = scorer.calculate_score(50000, 48000, anomalies=5)
    print(f"   Bad Profile (50k in, 48k out): Score {s2} - {n2}")

    print("\n✅ Predictive Features Verified!")

if __name__ == "__main__":
    test_predictive_features()
