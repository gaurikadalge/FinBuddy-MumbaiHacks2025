# backend/parsers/voice_parser.py

import re
from datetime import datetime


# ----------------------------------------------
# Master keyword dictionary (Hinglish-friendly)
# ----------------------------------------------
VOICE_CATEGORY_KEYWORDS = {
    "Travel": ["petrol", "diesel", "fuel", "cab", "auto", "ola", "uber"],
    "Food & Dining": ["food", "khana", "restaurant", "zomato", "swiggy", "burger", "pizza"],
    "Groceries": ["kirana", "grocery", "sabzi", "vegetable", "dairy", "milk", "store"],
    "Shopping": ["shopping", "amazon", "flipkart", "myntra", "mall", "dress", "clothes"],
    "Utilities": ["bill", "electricity", "water", "gas", "recharge", "dth", "mobile"],
    "Entertainment": ["movie", "netflix", "prime", "hotstar"],
    "Housing": ["rent", "maintenance"],
    "Medical": ["medicine", "medical", "chemist", "hospital"],
    "Income: Salary": ["salary", "income", "credited", "paisa aya", "received"],
}


# ----------------------------------------------
# Extract amount (strong patterns)
# ----------------------------------------------
def extract_amount(text_low: str):
    amount_patterns = [
        r'₹\s*([\d,]+\.?\d*)',
        r'rs\.?\s*([\d,]+\.?\d*)',
        r'inr\s*([\d,]+\.?\d*)',
        r'([\d,]+)\s*(rupaye|rs|rupees)',
        r'([\d,]+)\s*(spent|kharch|pay)',
    ]

    # Find matches from strong patterns
    for pattern in amount_patterns:
        m = re.search(pattern, text_low)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except:
                continue

    # Last fallback — only if number ≥ 100 (to avoid matching time like 8 PM)
    fallback_match = re.search(r'\b(\d{3,7})\b', text_low)
    if fallback_match:
        return float(fallback_match.group(1))

    return 0.0


# ----------------------------------------------
# Category detection
# ----------------------------------------------
def detect_category(text_low: str):
    for cat, keywords in VOICE_CATEGORY_KEYWORDS.items():
        for k in keywords:
            if k in text_low:
                return cat
    return "Miscellaneous"


# ----------------------------------------------
# Counterparty detection
# ----------------------------------------------
def detect_counterparty(text_low: str):
    merchant_patterns = [
        r'from\s+([a-z0-9 .&_-]+)',
        r'to\s+([a-z0-9 .&_-]+)',
        r'at\s+([a-z0-9 .&_-]+)',
        r'via\s+([a-z0-9 .&@_-]+)',
    ]

    # Pattern-based extraction
    for pat in merchant_patterns:
        m = re.search(pat, text_low)
        if m:
            return m.group(1).strip().title()

    # Keyword merchant fallback
    keyword_merchants = {
        "amazon": "Amazon",
        "flipkart": "Flipkart",
        "zomato": "Zomato",
        "swiggy": "Swiggy",
        "uber": "Uber",
        "ola": "Ola",
        "kirana": "Kirana Store",
        "petrol": "Petrol Pump",
        "restaurant": "Restaurant"
    }

    for k, v in keyword_merchants.items():
        if k in text_low:
            return v

    return "Voice Entry"


# ----------------------------------------------
# Detect transaction type
# ----------------------------------------------
def detect_txn_type(text_low: str):
    credit_keywords = ["salary", "income", "credited", "paisa aya", "received"]
    if any(k in text_low for k in credit_keywords):
        return "Credited"
    return "Debited"


# ----------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------
def parse_voice_command(text: str):
    text_low = text.lower()

    amount = extract_amount(text_low)
    if amount == 0:
        amount = 100.0  # small fallback default

    category = detect_category(text_low)
    counterparty = detect_counterparty(text_low)
    txn_type = detect_txn_type(text_low)

    return {
        "txn_type": txn_type,
        "amount": amount,
        "counterparty": counterparty,
        "message": f"Voice command: {text}",
        "category": category,
        "date": datetime.now().isoformat()
    }
