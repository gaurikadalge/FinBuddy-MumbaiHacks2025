# backend/services/compliance_service.py

from datetime import datetime
from typing import Optional
from backend.core.config import settings
from backend.core.database import get_transactions_collection
from backend.models.transaction import TransactionType
from backend.utils.logger import logger


class ComplianceService:
    def __init__(self):
        self.gst_threshold = settings.GST_THRESHOLD

    # --------------------------------------------------------
    # SAFELY GET DATABASE COLLECTION
    # --------------------------------------------------------
    @property
    def collection(self):
        return get_transactions_collection()

    # --------------------------------------------------------
    # HELPER: SAFE DATE PARSING
    # --------------------------------------------------------
    def _ensure_datetime(self, dt):
        if isinstance(dt, datetime):
            return dt
        try:
            return datetime.fromisoformat(dt)
        except Exception:
            return datetime.utcnow()

    # --------------------------------------------------------
    # YTD INCOME (from MongoDB)
    # --------------------------------------------------------
    async def get_ytd_income(self, year: int) -> float:
        """Calculate Year-To-Date credited income directly from MongoDB."""
        cursor = self.collection.find({
            "txn_type": TransactionType.CREDITED.value,
            "date": {
                "$gte": datetime(year, 1, 1),
                "$lte": datetime(year, 12, 31)
            }
        })

        docs = await cursor.to_list(None)
        total = sum(tx.get("amount", 0) for tx in docs)
        return total

    # --------------------------------------------------------
    # GST COMPLIANCE CHECK
    # --------------------------------------------------------
    async def check_gst_compliance(self, year: int) -> Optional[str]:
        """Check if the user's credited income crosses GST threshold."""
        ytd_income = await self.get_ytd_income(year)
        threshold = self.gst_threshold

        logger.info(f"Checking GST compliance YTD={ytd_income:,} | Threshold={threshold:,}")

        if ytd_income >= threshold:
            return (
                f"🚨 Critical: GST registration required! "
                f"Yearly income ₹{ytd_income:,.2f} exceeded the threshold of ₹{threshold:,.2f}."
            )

        # 90% threshold warning
        if ytd_income >= (threshold * 0.9):
            remaining = threshold - ytd_income
            return (
                f"⚠️ Warning: Approaching GST registration limit. "
                f"Only ₹{remaining:,.2f} below the threshold of ₹{threshold:,.2f}."
            )

        return None

    # --------------------------------------------------------
    # MAIN TRANSACTION ANALYZER
    # --------------------------------------------------------
    async def analyze_transaction(self, tx: dict) -> dict:
        """Generate insights + GST compliance alerts for a transaction."""
        try:
            amount = tx.get("amount", 0)
            txn_type = tx.get("txn_type", TransactionType.UNKNOWN.value)
            category = tx.get("category", "")

            insights = []
            alerts = []

            # ------------------------------------------------
            # HUMAN INSIGHTS
            # ------------------------------------------------
            if txn_type == TransactionType.CREDITED.value:
                if amount > 10000:
                    insights.append("Large credit received — review tax implications.")
                else:
                    insights.append("Income credited — recorded for financial tracking.")

            elif txn_type == TransactionType.DEBITED.value:
                if amount > 5000:
                    insights.append("High-value expense — consider if this was essential.")
                else:
                    insights.append("Expense recorded — contributes to monthly budgeting.")

            # ------------------------------------------------
            # GST CHECK
            # ------------------------------------------------
            tx_date = self._ensure_datetime(tx.get("date"))
            year = tx_date.year

            gst_msg = await self.check_gst_compliance(year)
            if gst_msg:
                alerts.append(gst_msg)

            return {
                "insight": " ".join(insights) if insights else "Transaction processed.",
                "compliance_alert": " ".join(alerts) if alerts else None,
            }

        except Exception as e:
            logger.error(f"Compliance analysis error: {e}")
            return {
                "insight": "Transaction processed.",
                "compliance_alert": None
            }
