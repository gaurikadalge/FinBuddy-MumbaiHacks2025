# backend/parsers/pdf_statement_parser.py

import re
from datetime import datetime
from backend.utils.logger import logger


# ---------------------------------------------------------
# Regex patterns for PDF statement OCR text
# ---------------------------------------------------------
DATE_PATTERNS = [
    r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
    r'(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})'
]

AMOUNT_PATTERNS = [
    r'([\d,]+\.\d{2})',      # 1,234.56
    r'([\d,]+)'              # 1234
]

DEBIT_KEYWORDS = ["debit", "dr", "withdrawal", "spent", "paid"]
CREDIT_KEYWORDS = ["credit", "cr", "deposit", "received"]


# ---------------------------------------------------------
# Parse PDF Statement
# ---------------------------------------------------------
def parse_pdf_statement(text: str):
    logger.info("📄 Parsing PDF bank statement...")

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    transactions = []

    for line in lines:
        line_low = line.lower()

        # ------------------------------------------------------
        # 1) Extract Date
        # ------------------------------------------------------
        date_found = None
        for pattern in DATE_PATTERNS:
            dm = re.search(pattern, line_low)
            if dm:
                raw = dm.group(1)
                for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y",
                            "%Y-%m-%d", "%d %B %Y", "%d %b %Y"):
                    try:
                        date_found = datetime.strptime(raw, fmt)
                        break
                    except:
                        continue
            if date_found:
                break

        if not date_found:
            continue  # skip lines without a clear date

        # ------------------------------------------------------
        # 2) Extract Amount
        # ------------------------------------------------------
        amount = 0.0
        for pattern in AMOUNT_PATTERNS:
            m = re.search(pattern, line_low)
            if m:
                try:
                    amount = float(m.group(1).replace(",", ""))
                    break
                except:
                    continue

        if amount <= 0:
            continue

        # ------------------------------------------------------
        # 3) Detect Transaction Type
        # ------------------------------------------------------
        if any(k in line_low for k in CREDIT_KEYWORDS):
            txn_type = "Credited"
        elif any(k in line_low for k in DEBIT_KEYWORDS):
            txn_type = "Debited"
        else:
            txn_type = "Unknown"

        # ------------------------------------------------------
        # 4) Merchant / UPI / Counterparty detection
        # ------------------------------------------------------
        merchant_keywords = [
            "upi", "amazon", "flipkart", "swiggy", "zomato",
            "petrol", "store", "shop", "paytm", "ola", "uber"
        ]

        merchant = "Unknown"
        for k in merchant_keywords:
            if k in line_low:
                merchant = k.title()
                break

        # ------------------------------------------------------
        # 5) Append transaction
        # ------------------------------------------------------
        transactions.append({
            "txn_type": txn_type,
            "amount": amount,
            "counterparty": merchant,
            "date": date_found.isoformat(),
            "message": line,
            "category": "Statement Entry"
        })

    return {
        "total_extracted": len(transactions),
        "transactions": transactions
    }
