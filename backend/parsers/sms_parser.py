# backend/parsers/sms_parser.py

import re
from datetime import datetime
from backend.utils.constants import CATEGORY_RULES


# ----------------------------------------------------------
# Amount extraction patterns (strong)
# ----------------------------------------------------------
AMOUNT_PATTERNS = [
    r'inr\s*([\d,]+\.?\d*)',
    r'rs\.?\s*([\d,]+\.?\d*)',
    r'₹\s*([\d,]+\.?\d*)',
    r'amount\s*([\d,]+\.?\d*)',
    r'amt[:\s]*([\d,]+\.?\d*)',
    r'([\d,]+\.\d{2})',  # 4500.00
]


# ----------------------------------------------------------
# Counterparty patterns
# ----------------------------------------------------------
COUNTERPARTY_PATTERNS = [
    r'from\s+([A-Za-z0-9 .&_\-]+)',
    r'to\s+([A-Za-z0-9 .&_\-]+)',
    r'via\s+([A-Za-z0-9@ .&_\-]+)',
    r'at\s+([A-Za-z0-9 .&_\-]+)',
    r'merchant[:\s]+([A-Za-z0-9 .&_\-]+)',
    r'sent\s+to\s+([A-Za-z0-9 .&_\-]+)',
    r'received\s+from\s+([A-Za-z0-9 .&_\-]+)',
]


# ----------------------------------------------------------
# Clean counterparty names
# ----------------------------------------------------------
def clean_counterparty(cp: str) -> str:
    cp = cp.strip()

    # Remove common SMS noise words
    noise = ["upi", "ref", "txn", "id", "no", "bank"]
    parts = cp.split()

    filtered = [p for p in parts if p.lower() not in noise]

    cp_clean = " ".join(filtered)

    # If still empty → fallback to original
    if not cp_clean:
        cp_clean = cp

    return cp_clean.title()


# ----------------------------------------------------------
# Category classification using keyword rules
# ----------------------------------------------------------
def categorize_transaction(text_low: str, txn_type: str) -> str:
    if isinstance(CATEGORY_RULES, dict):
        for keyword, category in CATEGORY_RULES.items():
            if keyword in text_low:
                return category

    # Default fallback
    if txn_type == "Credited":
        return "Income: Other"
    if txn_type == "Debited":
        return "Expense: Other"
    return "Unknown"


# ----------------------------------------------------------
# Main SMS Parsing Function
# ----------------------------------------------------------
def parse_sms(text: str):
    text_low = text.lower().strip()

    # ------------------------------------------------------
    # Transaction Type Detection
    # ------------------------------------------------------
    if any(k in text_low for k in ["credited", " credit ", " cr ", "received"]):
        txn_type = "Credited"
    elif any(k in text_low for k in ["debited", " debit ", " dr ", "spent", "paid"]):
        txn_type = "Debited"
    else:
        txn_type = "Unknown"

    # ------------------------------------------------------
    # Extract Amount
    # ------------------------------------------------------
    amount = 0.0
    for pattern in AMOUNT_PATTERNS:
        m = re.search(pattern, text_low)
        if m:
            try:
                amount = float(m.group(1).replace(",", ""))
                break
            except:
                continue

    # safe fallback: only 3–7 digit numbers
    if amount == 0.0:
        m = re.search(r'\b(\d{3,7})\b', text_low)
        if m:
            amount = float(m.group(1))

    # ------------------------------------------------------
    # Extract Counterparty
    # ------------------------------------------------------
    counterparty = "Unknown"
    for pattern in COUNTERPARTY_PATTERNS:
        m = re.search(pattern, text_low)
        if m:
            cp = clean_counterparty(m.group(1))
            if len(cp) > 1:
                counterparty = cp
                break

    # ------------------------------------------------------
    # Category Classification
    # ------------------------------------------------------
    category = categorize_transaction(text_low, txn_type)

    # ------------------------------------------------------
    # Extract Date if present
    # ------------------------------------------------------
    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text_low)
    if date_match:
        raw = date_match.group(1)
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"):
            try:
                txn_date = datetime.strptime(raw, fmt)
                break
            except:
                continue
        else:
            txn_date = datetime.now()
    else:
        txn_date = datetime.now()

    # ------------------------------------------------------
    # Final Response
    # ------------------------------------------------------
    return {
        "txn_type": txn_type,
        "amount": amount,
        "counterparty": counterparty,
        "message": text,
        "category": category,
        "date": txn_date.isoformat()
    }
