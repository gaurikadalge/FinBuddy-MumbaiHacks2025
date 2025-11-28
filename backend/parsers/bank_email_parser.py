# backend/parsers/bank_email_parser.py

import re
from datetime import datetime
from backend.utils.logger import logger


# ---------------------------------------------------------
# Regex Patterns
# ---------------------------------------------------------
AMOUNT_PATTERNS = [
    r'inr\s*([\d,]+\.?\d*)',
    r'rs\.?\s*([\d,]+\.?\d*)',
    r'₹\s*([\d,]+\.?\d*)',
    r'amount\s*([\d,]+\.?\d*)',
    r'amt[:\s]*([\d,]+\.?\d*)',
]

CREDIT_KEYWORDS = ["credited", "received", "deposit", "income"]
DEBIT_KEYWORDS = ["debited", "spent", "paid", "withdrawn", "charged"]

MERCHANT_PATTERNS = [
    r'from\s+([A-Za-z0-9 .&@_-]+)',
    r'to\s+([A-Za-z0-9 .&@_-]+)',
    r'merchant[:\s]+([A-Za-z0-9 .&@_-]+)',
    r'by\s+([A-Za-z0-9 .&@_-]+)',
    r'via\s+([A-Za-z0-9 .&@_-]+)',
]

CATEGORY_KEYWORDS = {
    "Salary": ["salary", "payout", "credited", "income"],
    "Shopping": ["amazon", "flipkart", "myntra", "order"],
    "Food & Dining": ["zomato", "swiggy", "restaurant"],
    "Travel": ["uber", "ola", "ride"],
    "Utilities": ["bill", "recharge", "electricity", "water", "dth"],
    "Medical": ["pharmacy", "medical", "chemist"],
    "Refund": ["refund", "reversed", "reversal"],
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def detect_category(text_low: str):
    for cat, keys in CATEGORY_KEYWORDS.items():
        if any(k in text_low for k in keys):
            return cat
    return "Other"


def clean_counterparty(cp: str) -> str:
    # Remove common noisy tokens
    noise = ["upi", "ref", "txn", "id", "no"]
    parts = cp.split()

    filtered = [p for p in parts if p.lower() not in noise]
    cp_clean = " ".join(filtered).strip()

    return cp_clean.title() if cp_clean else cp.title()


# ---------------------------------------------------------
# Main Parser
# ---------------------------------------------------------
def parse_email_text(text: str):
    try:
        text_low = text.lower()

        # ------------------------------------------
        # Transaction Type
        # ------------------------------------------
        if any(k in text_low for k in CREDIT_KEYWORDS):
            txn_type = "Credited"
        elif any(k in text_low for k in DEBIT_KEYWORDS):
            txn_type = "Debited"
        else:
            txn_type = "Unknown"

        # ------------------------------------------
        # Amount Extraction
        # ------------------------------------------
        amount = 0.0
        for pat in AMOUNT_PATTERNS:
            m = re.search(pat, text_low)
            if m:
                try:
                    amount = float(m.group(1).replace(",", ""))
                    break
                except:
                    continue

        # ------------------------------------------
        # Counterparty Detection
        # ------------------------------------------
        counterparty = "Unknown"
        for pat in MERCHANT_PATTERNS:
            m = re.search(pat, text_low)
            if m:
                counterparty = clean_counterparty(m.group(1))
                break

        # ------------------------------------------
        # Category Detection
        # ------------------------------------------
        category = detect_category(text_low)

        # ------------------------------------------
        # Date Extraction
        # ------------------------------------------
        date_patterns = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d-%m-%y",
            "%d/%m/%y",
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y",
        ]

        date_found = None
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})', text_low)

        if date_match:
            raw_date = date_match.group(1)
            for fmt in date_patterns:
                try:
                    date_found = datetime.strptime(raw_date, fmt)
                    break
                except:
                    continue

        if not date_found:
            date_found = datetime.now()

        # ------------------------------------------
        # Final structured output
        # ------------------------------------------
        return {
            "txn_type": txn_type,
            "amount": amount,
            "counterparty": counterparty,
            "category": category,
            "message": text,
            "date": date_found.isoformat()
        }

    except Exception as e:
        logger.error(f"Email parse failure: {e}")
        return {
            "txn_type": "Unknown",
            "amount": 0.0,
            "counterparty": "Unknown",
            "category": "Error",
            "message": text,
        }
