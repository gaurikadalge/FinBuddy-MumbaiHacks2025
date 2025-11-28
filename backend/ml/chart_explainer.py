from backend.utils.logger import logger
from typing import Dict, List, Any

class ChartExplainer:
    """
    Generates natural language explanations for financial charts.
    """
    def __init__(self):
        logger.info("Initializing ChartExplainer...")

    def explain_spending_trend(self, data_points: List[float], labels: List[str]) -> str:
        """
        Explain a simple trend line.
        """
        if len(data_points) < 2:
            return "Not enough data to identify a trend."

        current = data_points[-1]
        previous = data_points[-2]
        
        if previous == 0:
            return f"Spending started at ₹{current} this month."

        change = ((current - previous) / previous) * 100
        
        if change > 10:
            return f"Spending increased by {change:.1f}% compared to last month. Watch out!"
        elif change < -10:
            return f"Great job! Spending decreased by {abs(change):.1f}% compared to last month."
        else:
            return "Spending is relatively stable compared to last month."

    def explain_category_pie(self, category_data: Dict[str, float]) -> List[str]:
        """
        Explain category breakdown.
        """
        if not category_data:
            return ["No spending data available."]

        total = sum(category_data.values())
        sorted_cats = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        
        insights = []
        
        # Top category insight
        top_cat, top_amount = sorted_cats[0]
        top_pct = (top_amount / total) * 100
        insights.append(f"Your highest spending is in **{top_cat}** ({top_pct:.0f}%).")

        # Spike detection (simple)
        if top_pct > 50:
            insights.append(f"⚠️ Warning: {top_cat} accounts for more than half of your expenses.")

        return insights
