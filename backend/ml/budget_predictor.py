# backend/ml/budget_predictor.py

from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.utils.logger import logger


class PredictionResult:
    """Stores prediction results for a category"""
    def __init__(self, category: str, predicted_amount: float, confidence: float, 
                 trend: str, warning: Optional[str] = None):
        self.category = category
        self.predicted_amount = predicted_amount
        self.confidence = confidence
        self.trend = trend
        self.warning = warning
    
    def to_dict(self):
        return {
            "category": self.category,
            "predicted_amount": round(self.predicted_amount, 2),
            "confidence": round(self.confidence, 2),
            "trend": self.trend,
            "warning": self.warning
        }


class BudgetPredictor:
    """
    ML-based budget predictor using Facebook Prophet.
    Predicts next month's expenses by category with overspend warnings.
    """
    
    def __init__(self):
        logger.info("Initializing BudgetPredictor with Prophet...")
        self.models = {}  # Cache trained models by category
        self.min_data_points = 7  # Minimum 7 days of data
        
    def prepare_data(self, transactions: List[dict], category: str) -> pd.DataFrame:
        """
        Prepare transaction data for Prophet.
        Prophet requires columns: 'ds' (date) and 'y' (value)
        """
        # Filter by category
        category_txns = [t for t in transactions if t.get('category', '').lower() == category.lower()]
        
        if len(category_txns) == 0:
            logger.warning(f"No transactions found for category: {category}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(category_txns)
        
        # Ensure date column exists
        if 'date' not in df.columns:
            logger.error("Transaction data missing 'date' column")
            return pd.DataFrame()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter only debited transactions (expenses)
        df = df[df['txn_type'] == 'Debited']
        
        # Aggregate by date
        daily_expenses = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        daily_expenses.columns = ['ds', 'y']
        
        # Convert ds back to datetime
        daily_expenses['ds'] = pd.to_datetime(daily_expenses['ds'])
        
        # Fill missing dates with 0 (important for Prophet)
        if len(daily_expenses) > 0:
            date_range = pd.date_range(
                start=daily_expenses['ds'].min(),
                end=daily_expenses['ds'].max(),
                freq='D'
            )
            daily_expenses = daily_expenses.set_index('ds').reindex(date_range, fill_value=0).reset_index()
            daily_expenses.columns = ['ds', 'y']
        
        return daily_expenses
    
    def train_and_predict(self, data: pd.DataFrame, periods: int = 30) -> Optional[pd.DataFrame]:
        """
        Train Prophet model and predict future values.
        
        Args:
            data: DataFrame with 'ds' and 'y' columns
            periods: Number of days to predict (default 30)
        
        Returns:
            DataFrame with predictions or None if insufficient data
        """
        if len(data) < self.min_data_points:
            logger.warning(f"Insufficient data points: {len(data)} < {self.min_data_points}")
            return None
        
        try:
            # Initialize Prophet with custom settings
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05,  # Less sensitive to trend changes
                interval_width=0.8  # 80% confidence interval
            )
            
            # Suppress Prophet's verbose output
            import logging
            prophet_logger = logging.getLogger('prophet')
            prophet_logger.setLevel(logging.WARNING)
            
            # Fit model
            model.fit(data)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=periods)
            
            # Predict
            forecast = model.predict(future)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Prophet training failed: {str(e)}")
            return None
    
    def predict_next_month(self, transactions: List[dict], category: str, 
                          budget: Optional[float] = None) -> Optional[PredictionResult]:
        """
        Predict next month's total expenses for a category.
        
        Args:
            transactions: List of transaction dictionaries
            category: Category to predict
            budget: Optional budget threshold for overspend detection
        
        Returns:
            PredictionResult or None if prediction fails
        """
        logger.info(f"Predicting expenses for category: {category}")
        
        # Prepare data
        data = self.prepare_data(transactions, category)
        
        if data.empty:
            logger.warning(f"No data available for {category}")
            return None
        
        # Train and predict
        forecast = self.train_and_predict(data, periods=30)
        
        if forecast is None:
            return None
        
        # Get predictions for next 30 days
        future_predictions = forecast.tail(30)
        predicted_total = future_predictions['yhat'].sum()
        
        # Calculate confidence (based on uncertainty)
        avg_uncertainty = (future_predictions['yhat_upper'] - future_predictions['yhat_lower']).mean()
        confidence = max(0.5, min(1.0, 1 - (avg_uncertainty / predicted_total)))
        
        # Determine trend
        historical_avg = data['y'].mean() * 30  # 30-day average
        if predicted_total > historical_avg * 1.1:
            trend = "increasing"
        elif predicted_total < historical_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Check for overspend warning
        warning = None
        if budget and predicted_total > budget:
            overshoot = predicted_total - budget
            warning = f"At current pace you will exceed your {category} budget by ₹{overshoot:,.0f}"
        
        result = PredictionResult(
            category=category,
            predicted_amount=predicted_total,
            confidence=confidence,
            trend=trend,
            warning=warning
        )
        
        logger.info(f"Prediction for {category}: ₹{predicted_total:.2f} ({trend})")
        
        return result
    
    def predict_all_categories(self, transactions: List[dict], 
                              budgets: Optional[Dict[str, float]] = None) -> Dict[str, dict]:
        """
        Predict expenses for all categories with data.
        
        Args:
            transactions: List of all transactions
            budgets: Optional dict of {category: budget_amount}
        
        Returns:
            Dict of {category: prediction_dict}
        """
        # Extract unique categories
        categories = set(t.get('category', '').lower() for t in transactions if t.get('category'))
        categories = [c for c in categories if c and c != 'income']
        
        predictions = {}
        
        for category in categories:
            budget = budgets.get(category) if budgets else None
            result = self.predict_next_month(transactions, category, budget)
            
            if result:
                predictions[category] = result.to_dict()
        
        logger.info(f"Generated predictions for {len(predictions)} categories")
        
        return predictions
