import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import calendar
from backend.utils.logger import logger

class BudgetForecaster:
    def __init__(self):
        logger.info("Initializing BudgetForecaster...")
        self.model = LinearRegression()
        self.is_trained = False
        
        # Dummy historical daily spending (Day of Month, Amount)
        # Simulating a trend of increasing spending
        self.history = [
            [1, 500], [2, 600], [3, 400], [4, 800], [5, 500],
            [6, 700], [7, 900], [8, 500], [9, 600], [10, 1000],
            [11, 500], [12, 600], [13, 700], [14, 800], [15, 900]
        ]
        self._train()

    def _train(self):
        X = np.array([x[0] for x in self.history]).reshape(-1, 1) # Day
        y = np.array([x[1] for x in self.history]) # Amount
        
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("BudgetForecaster trained on historical data.")

    def predict_next_month(self, category="General"):
        """Forecast total spend for next month"""
        if not self.is_trained:
            return 0.0
            
        # Predict for all days in next month (approx 30 days)
        # We'll just project the trend forward
        last_day = self.history[-1][0]
        next_month_days = np.arange(last_day + 1, last_day + 31).reshape(-1, 1)
        
        predictions = self.model.predict(next_month_days)
        total_forecast = np.sum(predictions)
        
        # Add some randomness/noise for realism if needed, or category specific multipliers
        if category == "Food":
            total_forecast *= 0.4 # Assume food is 40% of spend
        elif category == "Travel":
            total_forecast *= 0.2
            
        return max(0.0, round(total_forecast, 2))

    def check_overshoot(self, current_spend: float, budget: float, day_of_month: int) -> dict:
        """
        Check if user will overshoot budget based on current pace.
        Returns: {'overshoot': bool, 'predicted_total': float, 'message': str}
        """
        if day_of_month <= 0: day_of_month = 1
        
        # Simple run-rate projection
        days_in_month = 30
        daily_avg = current_spend / day_of_month
        predicted_total = daily_avg * days_in_month
        
        # ML-adjusted projection (using trend)
        # If model predicts increasing trend, increase the run-rate projection
        if self.is_trained:
            trend_factor = self.model.coef_[0] # Slope
            if trend_factor > 0:
                # Add expected increase for remaining days
                remaining_days = days_in_month - day_of_month
                predicted_total += (trend_factor * remaining_days * remaining_days) / 2
        
        predicted_total = round(predicted_total, 2)
        
        if predicted_total > budget:
            excess = round(predicted_total - budget, 2)
            return {
                "overshoot": True,
                "predicted_total": predicted_total,
                "message": f"At this pace, you will exceed your budget by ₹{excess}."
            }
            
        return {
            "overshoot": False,
            "predicted_total": predicted_total,
            "message": "You are on track to stay within budget."
        }
