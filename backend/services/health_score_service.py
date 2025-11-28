# backend/services/health_score_service.py

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.ml.score_engine import AdvancedFinancialHealthScorer
from backend.services.transaction_service import TransactionService
from backend.utils.logger import logger


class HealthScoreService:
    """
    Service layer for advanced financial health score calculation.
    Coordinates data fetching and score computation.
    """
    
    def __init__(self):
        self.scorer = AdvancedFinancialHealthScorer()
        self.transaction_service = TransactionService()
        logger.info("HealthScoreService initialized")
    
    def get_default_budgets(self) -> Dict[str, float]:
        """
        Get default budget thresholds by category.
        In production, this would come from user settings in database.
        """
        return {
            "food": 15000,
            "travel": 8000,
            "shopping": 10000,
            "entertainment": 5000,
            "bills": 12000,
            "general": 5000
        }
    
    async def get_financial_health_score(self, days: int = 60) -> dict:
        """
        Calculate comprehensive financial health score.
        
        Args:
            days: Number of past days to analyze (default 60)
        
        Returns:
            Complete health score result with breakdown and recommendations
        """
        logger.info(f"Calculating financial health score for last {days} days...")
        
        try:
            # Fetch transactions
            all_transactions = await self.transaction_service.get_all_transactions()
            
            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            filtered_transactions = []
            for txn in all_transactions:
                # Convert Transaction model to dict
                txn_dict = txn.dict() if hasattr(txn, 'dict') else txn
                
                txn_date = txn_dict.get('date')
                if isinstance(txn_date, datetime) and txn_date >= cutoff_date:
                    filtered_transactions.append(txn_dict)
            
            logger.info(f"Analyzing {len(filtered_transactions)} transactions")
            
            # Get budgets
            budgets = self.get_default_budgets()
            
            # Calculate score
            result = self.scorer.calculate_advanced_score(
                transactions=filtered_transactions,
                budgets=budgets
            )
            
            # Add metadata
            result['analysis_period_days'] = days
            result['total_transactions'] = len(filtered_transactions)
            
            return result
            
        except Exception as e:
            logger.error(f"Health score calculation failed: {str(e)}")
            raise
    
    def get_score_history(self, months: int = 3) -> List[dict]:
        """
        Calculate score for each of the past N months to show trend.
        This is a placeholder - in production, would cache monthly scores.
        """
        # Placeholder implementation
        # In production, you'd calculate score for each month and cache results
        return []
