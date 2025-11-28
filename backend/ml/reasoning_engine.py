from backend.utils.logger import logger
from typing import Dict, List, Any

class MultimodalReasoningEngine:
    """
    Combines inputs from various sources (Text, Voice, OCR) to form a holistic view.
    Acts as a 'Judge' for transaction context.
    """
    def __init__(self):
        logger.info("Initializing MultimodalReasoningEngine...")

    def analyze_context(self, transaction_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Analyze the context of a transaction based on its source and content.
        """
        reasoning = {
            "risk_level": "Low",
            "context_tags": [],
            "flags": []
        }

        amount = transaction_data.get("amount", 0)
        category = transaction_data.get("category", "Uncategorized")
        merchant = transaction_data.get("counterparty", "Unknown")

        # 1. Source-based reasoning
        if source == "voice":
            reasoning["context_tags"].append("Verified by Voice")
        elif source == "ocr":
            reasoning["context_tags"].append("Verified by Receipt")
        
        # 2. Amount-based reasoning (Simple heuristics for now)
        if amount > 5000 and category.lower() in ["food", "entertainment"]:
            reasoning["risk_level"] = "Medium"
            reasoning["flags"].append("High discretionary spending")
        
        if amount > 20000:
            reasoning["risk_level"] = "High"
            reasoning["flags"].append("Large transaction detected")

        # 3. Category-specific checks
        if category.lower() == "medical":
            reasoning["context_tags"].append("Essential Expense")
            reasoning["risk_level"] = "Low" # Medical is usually necessary

        return reasoning

    def detect_anomalies(self, current_txn: Dict[str, Any], history: List[Dict[str, Any]]) -> List[str]:
        """
        Detect anomalies by comparing with recent history.
        """
        anomalies = []
        category = current_txn.get("category", "General")
        amount = current_txn.get("amount", 0)

        # Filter history for same category
        same_cat_txns = [t for t in history if t.get("category") == category]
        
        if not same_cat_txns:
            return anomalies

        # Calculate average
        avg_amount = sum(t.get("amount", 0) for t in same_cat_txns) / len(same_cat_txns)
        
        # Check for spike (> 2x average)
        if amount > avg_amount * 2 and amount > 500: # Threshold to ignore small variances
            anomalies.append(f"Spending in {category} is 2x higher than usual average (₹{avg_amount:.0f})")

        return anomalies
