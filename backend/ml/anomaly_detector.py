from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
from datetime import datetime
from backend.utils.logger import logger

class AnomalyDetector:
    def __init__(self):
        logger.info("Initializing AnomalyDetector (IsolationForest)...")
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False
        self.recent_transactions = [] # For duplicate detection
        
        # Dummy historical data for training (Amount, Hour)
        # Normal behavior: Small amounts (50-2000), mostly day time
        self.training_data = [
            [50, 9], [100, 10], [200, 12], [500, 13], [150, 14], [80, 15],
            [1200, 18], [2000, 19], [300, 20], [100, 21], [50, 8],
            [1500, 10], [2500, 12] # Some larger but normal
        ]
        
        self._train()

    def _train(self):
        X = np.array(self.training_data)
        self.model.fit(X)
        self.is_trained = True
        logger.info("AnomalyDetector trained on baseline data.")

    def check(self, amount: float, category: str, merchant: str) -> dict:
        """
        Check for anomalies.
        Returns: {'is_anomaly': bool, 'reason': str}
        """
        if not self.is_trained:
            return {"is_anomaly": False, "reason": ""}
            
        current_hour = datetime.now().hour
        
        # 1. Check for Duplicates (Simple Rule)
        # Same amount & merchant within last 5 mins (simulated by checking last few entries)
        for txn in self.recent_transactions[-5:]:
            if txn['amount'] == amount and txn['merchant'] == merchant:
                 # In real app, check timestamp diff
                 return {"is_anomaly": True, "reason": "Duplicate transaction detected."}
        
        # Add to recent
        self.recent_transactions.append({"amount": amount, "merchant": merchant, "time": datetime.now()})
        if len(self.recent_transactions) > 20:
            self.recent_transactions.pop(0)

        # 2. ML Anomaly Detection (Isolation Forest)
        # Feature vector: [Amount, Hour]
        features = np.array([[amount, current_hour]])
        prediction = self.model.predict(features)[0] # 1 for normal, -1 for anomaly
        
        if prediction == -1:
            return {"is_anomaly": True, "reason": f"Unusual spending pattern (Amount: {amount}) for this time."}
            
        # 3. Heuristic High Value Check (Fallback)
        if amount > 10000 and category == "Food":
             return {"is_anomaly": True, "reason": "Unusually high amount for Food."}
             
        return {"is_anomaly": False, "reason": ""}
