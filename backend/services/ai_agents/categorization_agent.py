# backend/services/ai_agents/categorization_agent.py

import re
from backend.utils.logger import logger


class CategorizationAgent:
    """
    Unified transaction categorization:
    - Hinglish friendly
    - Word-boundary matching (no false positives)
    - Consistent categories used across all parsers
    - Smart fallbacks
    """

    def __init__(self):

        # Unified category map (strict, word-based)
        self.category_map = {
            # Income
            r"\bsalary\b": "Income",
            r"\bcredited\b": "Income",
            r"\breceive(d)?\b": "Income",
            r"\bdeposit\b": "Income",

            # Refunds
            r"\brefund\b": "Refund",
            r"\bcashback\b": "Refund",
            r"\breward\b": "Refund",

            # Food & Dining
            r"\bfood\b": "Food & Dining",
            r"\brestaurant\b": "Food & Dining",
            r"\bdining\b": "Food & Dining",
            r"\bzomato\b": "Food & Dining",
            r"\bswiggy\b": "Food & Dining",
            r"\bkhana\b": "Food & Dining",

            # Shopping
            r"\bshopping\b": "Shopping",
            r"\bamazon\b": "Shopping",
            r"\bflipkart\b": "Shopping",
            r"\bmyntra\b": "Shopping",
            r"\bkirana\b": "Groceries",
            r"\bgrocery\b": "Groceries",
            r"\bmilk\b": "Groceries",
            
            # Travel
            r"\bpetrol\b": "Travel",
            r"\bfuel\b": "Travel",
            r"\bdiesel\b": "Travel",
            r"\buber\b": "Travel",
            r"\bola\b": "Travel",
            r"\bbus\b": "Travel",
            r"\btrain\b": "Travel",
            r"\bflight\b": "Travel",

            # Utilities
            r"\bbill\b": "Utilities",
            r"\belectricity\b": "Utilities",
            r"\bwater\b": "Utilities",
            r"\binternet\b": "Utilities",
            r"\bmobile\b": "Utilities",
            r"\brecharge\b": "Utilities",

            # Housing
            r"\brent\b": "Housing",
            r"\bmaintenance\b": "Housing",

            # Loan / EMI
            r"\bemi\b": "Loan / EMI",
            r"\bloan\b": "Loan / EMI",
            r"\binstallment\b": "Loan / EMI",

            # Healthcare
            r"\bmedical\b": "Healthcare",
            r"\bhospital\b": "Healthcare",
            r"\bdoctor\b": "Healthcare",
            r"\bmedicine\b": "Healthcare",

            # Entertainment
            r"\bmovie\b": "Entertainment",
            r"\bnetflix\b": "Entertainment",
            r"\bprime\b": "Entertainment",
            r"\bhotstar\b": "Entertainment",

            # Investment
            r"\binvest(ment)?\b": "Investment",
            r"\bmutual fund\b": "Investment",
            r"\bstock\b": "Investment",
            r"\bsip\b": "Investment",

            # Insurance
            r"\binsurance\b": "Insurance",
            r"\bpremium\b": "Insurance",
        }

    # -----------------------------------------------------------
    # MAIN CATEGORIZATION METHOD
    # -----------------------------------------------------------
    async def categorize_transaction(self, text: str, amount: float) -> str:
        try:
            t = text.lower()

            # -----------------------------------------------
            # 1. Regex-based keyword detection (safe matching)
            # -----------------------------------------------
            for pattern, category in self.category_map.items():
                if re.search(pattern, t):
                    logger.info(f"[Categorization] Matched '{pattern}' → {category}")
                    return category

            # -----------------------------------------------
            # 2. Amount-based fallback (simplified)
            # -----------------------------------------------
            if amount >= 25000:
                return "High-Value Expense"
            if amount >= 10000:
                return "Large Expense"
            if amount >= 3000:
                return "General Expense"

            # -----------------------------------------------
            # 3. Universal fallback
            # -----------------------------------------------
            return "Uncategorized"

        except Exception as e:
            logger.error(f"Categorization error: {e}")
            return "Uncategorized"
