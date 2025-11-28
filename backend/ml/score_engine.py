from backend.utils.logger import logger
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class FinancialHealthScorer:
    """Basic Financial Health Scorer - Preserved for backward compatibility"""
    def __init__(self):
        logger.info("Initializing FinancialHealthScorer...")

    def calculate_score(self, income: float, expenses: float, anomalies: int = 0):
        """
        Calculate Financial Health Score (0-100).
        Metrics:
        1. Savings Rate (40%)
        2. Expense Ratio (30%)
        3. Anomaly Penalty (10%)
        4. Base Score (20%)
        """
        if income <= 0:
            return 0, "Income data missing."

        savings = income - expenses
        savings_rate = (savings / income) * 100
        expense_ratio = (expenses / income) * 100
        
        # 1. Savings Score (Max 40)
        # Target: 20% savings = 40 points
        savings_score = min(40, (savings_rate / 20) * 40)
        if savings_score < 0: savings_score = 0
        
        # 2. Expense Control Score (Max 30)
        # Target: < 50% needs, < 30% wants. Simplified: < 80% total
        if expense_ratio < 50:
            control_score = 30
        elif expense_ratio < 80:
            control_score = 20
        elif expense_ratio < 100:
            control_score = 10
        else:
            control_score = 0
            
        # 3. Anomaly Penalty (Max 10 deduction)
        penalty = min(10, anomalies * 2)
        
        # 4. Base Score (20) - for just tracking
        base_score = 20
        
        total_score = base_score + savings_score + control_score - penalty
        total_score = max(0, min(100, total_score))
        
        return int(total_score), self._get_assessment(total_score)

    def _get_assessment(self, score):
        if score >= 80:
            return "🌟 Excellent! You are a financial master. Keep investing."
        elif score >= 60:
            return "✅ Good job. You are saving well, but could optimize more."
        elif score >= 40:
            return "⚠️ Fair. You are living paycheck to paycheck. Try to cut wants."
        else:
            return "🚨 Critical. Your expenses are too high. Immediate budget review needed."


# ============================================================================
# ADVANCED FINANCIAL HEALTH SCORER
# ============================================================================

class AdvancedFinancialHealthScorer:
    """
    Advanced Financial Health Scorer with 6 comprehensive metrics.
    Patent-ready feature for startup evaluation.
    """
    
    def __init__(self):
        logger.info("Initializing AdvancedFinancialHealthScorer...")
        
        # Metric weights (total = 100)
        self.weights = {
            "spending_discipline": 25,
            "recurring_costs": 20,
            "category_balance": 20,
            "income_stability": 15,
            "savings_rate": 15,
            "debt_indicators": 5
        }
    
    def calculate_advanced_score(self, transactions: List[dict], 
                                budgets: Optional[Dict[str, float]] = None) -> dict:
        """
        Calculate comprehensive financial health score.
        
        Args:
            transactions: List of transaction dictionaries
            budgets: Optional category budgets for discipline scoring
        
        Returns:
            Dictionary with overall score, breakdown, trend, and recommendations
        """
        if not transactions:
            logger.warning("No transactions provided for scoring")
            return self._empty_score_result()
        
        # Calculate each metric
        discipline_score = self._analyze_spending_discipline(transactions, budgets)
        recurring_score = self._analyze_recurring_costs(transactions)
        balance_score = self._analyze_category_balance(transactions)
        stability_score = self._analyze_income_stability(transactions)
        savings_score = self._analyze_savings_rate(transactions)
        debt_score = self._analyze_debt_indicators(transactions)
        
        # Calculate weighted total
        breakdown = {
            "spending_discipline": discipline_score,
            "recurring_costs": recurring_score,
            "category_balance": balance_score,
            "income_stability": stability_score,
            "savings_rate": savings_score,
            "debt_indicators": debt_score
        }
        
        overall_score = sum(breakdown.values())
        overall_score = max(0, min(100, int(overall_score)))
        
        # Get grade and assessment
        grade = self._get_grade(overall_score)
        assessment = self._get_assessment(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(breakdown, transactions)
        
        # Determine trend (would compare with historical scores in production)
        trend = self._get_trend([overall_score])  # Placeholder
        
        result = {
            "overall_score": overall_score,
            "grade": grade,
            "trend": trend,
            "breakdown": breakdown,
            "recommendations": recommendations,
            "assessment": assessment,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Advanced Health Score calculated: {overall_score}/100 ({grade})")
        
        return result
    
    def _analyze_spending_discipline(self, transactions: List[dict], 
                                    budgets: Optional[Dict[str, float]]) -> float:
        """
        Score 0-25: How well user stays within category budgets.
        """
        if not budgets:
            # Default scoring based on month-to-month consistency
            return 15  # Neutral
        
        # Calculate actual spending by category
        category_spending = defaultdict(float)
        for txn in transactions:
            if txn.get('txn_type') == 'Debited':
                cat = txn.get('category', 'general').lower()
                category_spending[cat] += txn.get('amount', 0)
        
        # Compare to budgets
        total_categories = len(budgets)
        categories_on_budget = 0
        
        for cat, budget in budgets.items():
            actual = category_spending.get(cat.lower(), 0)
            if actual <= budget:
                categories_on_budget += 1
        
        # Score
        if total_categories > 0:
            discipline_ratio = categories_on_budget / total_categories
            score = discipline_ratio * self.weights["spending_discipline"]
        else:
            score = self.weights["spending_discipline"] * 0.6
        
        return round(score, 2)
    
    def _analyze_recurring_costs(self, transactions: List[dict]) -> float:
        """
        Score 0-20: Ratio of fixed vs variable expenses (lower fixed = better).
        """
        # Identify recurring patterns (Bills category and similar amounts)
        bills_spending = 0
        total_spending = 0
        
        for txn in transactions:
            if txn.get('txn_type') == 'Debited':
                amount = txn.get('amount', 0)
                category = txn.get('category', '').lower()
                
                total_spending += amount
                
                if category in ['bills', 'subscription', 'rent']:
                    bills_spending += amount
        
        if total_spending == 0:
            return self.weights["recurring_costs"] * 0.6
        
        # Lower recurring ratio = better score
        recurring_ratio = bills_spending / total_spending
        
        if recurring_ratio < 0.3:
            score = self.weights["recurring_costs"]
        elif recurring_ratio < 0.5:
            score = self.weights["recurring_costs"] * 0.7
        elif recurring_ratio < 0.7:
            score = self.weights["recurring_costs"] * 0.4
        else:
            score = self.weights["recurring_costs"] * 0.2
        
        return round(score, 2)
    
    def _analyze_category_balance(self, transactions: List[dict]) -> float:
        """
        Score 0-20: Diversity across spending categories (avoid 80% in one category).
        """
        category_totals = defaultdict(float)
        total_spending = 0
        
        for txn in transactions:
            if txn.get('txn_type') == 'Debited':
                cat = txn.get('category', 'general').lower()
                amount = txn.get('amount', 0)
                category_totals[cat] += amount
                total_spending += amount
        
        if total_spending == 0:
            return self.weights["category_balance"] * 0.6
        
        # Find max category percentage
        max_category_pct = max(category_totals.values()) / total_spending if category_totals else 0
        
        # Better balance = higher score
        if max_category_pct < 0.4:  # Well balanced
            score = self.weights["category_balance"]
        elif max_category_pct < 0.6:
            score = self.weights["category_balance"] * 0.7
        elif max_category_pct < 0.8:
            score = self.weights["category_balance"] * 0.4
        else:
            score = self.weights["category_balance"] * 0.2
        
        return round(score, 2)
    
    def _analyze_income_stability(self, transactions: List[dict]) -> float:
        """
        Score 0-15: Regularity of income transactions.
        """
        income_txns = [t for t in transactions if t.get('txn_type') == 'Credited']
        
        if len(income_txns) == 0:
            return 0
        
        if len(income_txns) == 1:
            return self.weights["income_stability"] * 0.5
        
        # Check if income is regular (monthly)
        if len(income_txns) >= 2:
            # Regular income gets full score
            score = self.weights["income_stability"]
        else:
            score = self.weights["income_stability"] * 0.6
        
        return round(score, 2)
    
    def _analyze_savings_rate(self, transactions: List[dict]) -> float:
        """
        Score 0-15: Actual savings vs income.
        """
        total_income = sum(t.get('amount', 0) for t in transactions if t.get('txn_type') == 'Credited')
        total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('txn_type') == 'Debited')
        
        if total_income == 0:
            return 0
        
        savings = total_income - total_expenses
        savings_rate = (savings / total_income) * 100
        
        # Target: 20% savings = full score
        if savings_rate >= 20:
            score = self.weights["savings_rate"]
        elif savings_rate >= 10:
            score = self.weights["savings_rate"] * 0.7
        elif savings_rate >= 5:
            score = self.weights["savings_rate"] * 0.4
        elif savings_rate >= 0:
            score = self.weights["savings_rate"] * 0.2
        else:
            score = 0  # Negative savings
        
        return round(score, 2)
    
    def _analyze_debt_indicators(self, transactions: List[dict]) -> float:
        """
        Score 0-5: Penalize overdraft or overspending patterns.
        """
        # Simple check: if total expenses > total income
        total_income = sum(t.get('amount', 0) for t in transactions if t.get('txn_type') == 'Credited')
        total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('txn_type') == 'Debited')
        
        if total_income == 0:
            return self.weights["debt_indicators"] * 0.5
        
        if total_expenses <= total_income:
            score = self.weights["debt_indicators"]
        elif total_expenses <= total_income * 1.1:
            score = self.weights["debt_indicators"] * 0.5
        else:
            score = 0
        
        return round(score, 2)
    
    def _generate_recommendations(self, breakdown: Dict[str, float], 
                                 transactions: List[dict]) -> List[str]:
        """
        Generate personalized recommendations based on weakest metrics.
        """
        recommendations = []
        
        # Find weakest metrics (normalized by weight)
        normalized_scores = {}
        for metric, score in breakdown.items():
            weight = self.weights[metric]
            normalized_scores[metric] = (score / weight) if weight > 0 else 1.0
        
        # Sort by normalized score (lowest first)
        sorted_metrics = sorted(normalized_scores.items(), key=lambda x: x[1])
        
        # Top 3 improvement areas
        for metric, norm_score in sorted_metrics[:3]:
            if norm_score < 0.7:  # Only recommend if score is below 70%
                rec = self._get_recommendation_for_metric(metric, transactions)
                if rec:
                    recommendations.append(rec)
        
        if not recommendations:
            recommendations.append("🎉 Excellent! You're doing great across all metrics.")
        
        return recommendations[:3]  # Max 3 recommendations
    
    def _get_recommendation_for_metric(self, metric: str, transactions: List[dict]) -> Optional[str]:
        """Get specific recommendation for a metric."""
        
        if metric == "spending_discipline":
            return "📊 Try setting stricter category budgets and track them weekly"
        
        elif metric == "recurring_costs":
            return "💳 Review subscriptions and bills - cancel unused services"
        
        elif metric == "category_balance":
            # Find dominant category
            category_totals = defaultdict(float)
            for txn in transactions:
                if txn.get('txn_type') == 'Debited':
                    cat = txn.get('category', 'general')
                    category_totals[cat] += txn.get('amount', 0)
            
            if category_totals:
                top_cat = max(category_totals.items(), key=lambda x: x[1])[0]
                total = sum(category_totals.values())
                pct = (category_totals[top_cat] / total * 100) if total > 0 else 0
                return f"⚖️ Your {top_cat} spending is {pct:.0f}% of expenses - try to reduce to 30-40%"
        
        elif metric == "income_stability":
            return "💼 Consider diversifying income sources for better stability"
        
        elif metric == "savings_rate":
            total_income = sum(t.get('amount', 0) for t in transactions if t.get('txn_type') == 'Credited')
            total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('txn_type') == 'Debited')
            if total_income > 0:
                rate = ((total_income - total_expenses) / total_income) * 100
                target_savings = total_income * 0.2
                return f"💰 Increase savings from {rate:.1f}% to 20% (save ₹{target_savings:,.0f}/month)"
        
        elif metric == "debt_indicators":
            return "⚠️ Your expenses exceed income - immediate budget cuts needed"
        
        return None
    
    def _get_trend(self, historical_scores: List[float]) -> str:
        """Determine trend based on historical scores."""
        if len(historical_scores) < 2:
            return "Stable"
        
        # Compare latest vs previous
        if historical_scores[-1] > historical_scores[-2] + 5:
            return "Improving"
        elif historical_scores[-1] < historical_scores[-2] - 5:
            return "Declining"
        else:
            return "Stable"
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _get_assessment(self, score: int) -> str:
        """Get textual assessment."""
        if score >= 80:
            return "🌟 Excellent! You are a financial master. Keep investing."
        elif score >= 60:
            return "✅ Good job. You are saving well, but could optimize more."
        elif score >= 40:
            return "⚠️ Fair. You are living paycheck to paycheck. Try to cut wants."
        else:
            return "🚨 Critical. Your expenses are too high. Immediate budget review needed."
    
    def _empty_score_result(self) -> dict:
        """Return empty result when no data available."""
        return {
            "overall_score": 0,
            "grade": "N/A",
            "trend": "Unknown",
            "breakdown": {k: 0 for k in self.weights.keys()},
            "recommendations": ["Add transactions to calculate your financial health score"],
            "assessment": "Insufficient data",
            "timestamp": datetime.utcnow().isoformat()
        }

