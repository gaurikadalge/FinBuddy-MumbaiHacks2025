# backend/services/ai_agents/insights_agent.py

from backend.utils.logger import logger


class InsightsAgent:
    """
    Professional, PDF-safe insight generator.
    - No emojis (works with ReportLab)
    - Clean, consistent advisory tone
    - Category-aware recommendations
    - Works with standardized categories
    """

    async def generate_insight(self, tx: dict) -> str:
        try:
            amount = tx.get("amount", 0)
            category = tx.get("category", "Unknown")
            txn_type = str(tx.get("txn_type", "Unknown")).lower()
            message = tx.get("message", "")
            msg = message.lower()

            # Income
            if "credit" in txn_type:
                return self._income_insights(amount)

            # Expense
            if "debit" in txn_type:
                return self._expense_insights(amount, category, msg)

            # Unknown
            return (
                "Transaction recorded. Review category and details to ensure accuracy."
            )

        except Exception as e:
            logger.error(f"Insight generation error: {e}")
            return (
                "Transaction analyzed. No major observations. "
                "Maintain consistent financial tracking."
            )

    # =========================================================
    # INCOME INSIGHTS
    # =========================================================
    def _income_insights(self, amount: float) -> str:
        if amount >= 100000:
            return (
                "High-value income received. Consider allocating a portion into "
                "investments, emergency funds, and tax-saving instruments."
            )

        elif amount >= 50000:
            return (
                "A solid income credit. This is a good opportunity to increase savings "
                "or SIP contributions and plan short-term goals."
            )

        elif amount >= 10000:
            return (
                "A stable income credit received. Continue strengthening consistent "
                "earning and saving habits."
            )

        return (
            "Small income credit received. Regular tracking helps build long-term "
            "financial discipline."
        )

    # =========================================================
    # EXPENSE INSIGHTS
    # =========================================================
    def _expense_insights(self, amount: float, category: str, msg: str) -> str:
        cat = category.lower()

        # Category-specific insights
        if cat == "food & dining":
            return self._food_insight(amount)

        if cat == "shopping":
            return self._shopping_insight(amount)

        if cat == "travel":
            return self._travel_insight(amount)

        if cat == "utilities":
            return "Utility bill paid. This is a recurring essential expense."

        if cat == "housing":
            return "Housing or rent payment completed. This is typically a major monthly expense."

        if cat == "loan / emi":
            return "Loan or EMI payment processed. Ensure your debt-to-income ratio remains healthy."

        if cat == "healthcare":
            return "Healthcare spending recorded. Maintaining adequate health insurance is advisable."

        if cat == "entertainment":
            return (
                "Entertainment expense noted. Consider monitoring monthly leisure spending."
            )

        if cat == "investment":
            return (
                "Investment transaction recorded. A good step toward long-term financial growth."
            )

        if cat == "insurance":
            return (
                "Insurance premium recorded. Maintaining insurance coverage strengthens financial safety."
            )

        if cat == "refund":
            return (
                "Refund or cashback recorded. Adjust category if needed for clear reporting."
            )

        # Amount-based fallback
        if amount >= 20000:
            return (
                "Significant spending detected. Review whether this aligns with your "
                "financial plan."
            )

        if amount >= 10000:
            return (
                "Large expense recorded. Ensure this was a planned or necessary purchase."
            )

        if amount >= 3000:
            return (
                "Medium-value expense recorded. Monitoring such expenses helps maintain "
                "monthly budgets."
            )

        if amount >= 500:
            return "Regular expense recorded. Tracking these helps improve budgeting accuracy."

        return "Small expense recorded. Continue good tracking habits."

    # =========================================================
    # CATEGORY DETAIL INSIGHTS
    # =========================================================
    def _food_insight(self, amount: float) -> str:
        if amount > 1500:
            return (
                "Notable food or dining expense. Consider balancing convenience with meal planning."
            )
        return (
            "Food-related spending noted. Maintaining a mix of home-cooked meals and "
            "outside food helps manage budgets."
        )

    def _shopping_insight(self, amount: float) -> str:
        if amount > 5000:
            return (
                "Major shopping expense recorded. Review to avoid impulsive or unplanned purchases."
            )
        return (
            "Shopping expense noted. Tracking discretionary spending supports better budgeting."
        )

    def _travel_insight(self, amount: float) -> str:
        if amount > 2000:
            return (
                "High travel-related expense. Consider carpooling or public transport "
                "if suitable."
            )
        return (
            "Travel expense recorded. Keeping a log is useful for personal or business tracking."
        )
