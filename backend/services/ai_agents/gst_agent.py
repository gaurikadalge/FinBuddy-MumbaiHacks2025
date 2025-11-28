# backend/services/ai_agents/gst_agent.py

from backend.core.config import settings
from backend.utils.logger import logger


class GSTAgent:
    """
    Soft advisory GST agent.
    - No emojis (PDF safe)
    - Consistent logic with ComplianceService
    - Simple explanations for user-facing messages
    """

    def __init__(self):
        self.threshold = float(getattr(settings, "GST_THRESHOLD", 2000000))  # default 20L

    async def check_gst_implications(self, transaction: dict, ytd_income: float) -> str:
        """
        Provide GST advisory messages based on YTD income.
        Does NOT enforce rules (ComplianceService handles strict logic).
        """
        try:
            amount = transaction.get("amount", 0)
            txn_type = str(transaction.get("txn_type", "")).lower()

            # Apply only to credited income transactions
            if "credit" not in txn_type and "income" not in txn_type:
                return None

            if self.threshold <= 0:
                return None

            percent = (ytd_income / self.threshold) * 100

            # -----------------------------
            # 1. Above threshold
            # -----------------------------
            if ytd_income >= self.threshold:
                return (
                    "GST registration is required. "
                    f"Your year-to-date income has crossed the ₹{self.threshold:,.0f} threshold."
                )

            # -----------------------------
            # 2. 90% warning zone
            # -----------------------------
            if percent >= 90:
                remaining = self.threshold - ytd_income
                return (
                    "You are very close to the GST threshold. "
                    f"Only ₹{remaining:,.0f} remaining before crossing it."
                )

            # -----------------------------
            # 3. 70% advisory zone
            # -----------------------------
            if percent >= 70:
                return (
                    "Your income is approaching GST limits. "
                    "Monitor income regularly to ensure compliance."
                )

            # -----------------------------
            # 4. General advisory
            # -----------------------------
            if amount > 20000:
                return (
                    "A large credit has been detected. "
                    "Ensure income records are maintained properly."
                )

            return None

        except Exception as e:
            logger.error(f"GST check error: {e}")
            return None
