# backend/parsers/receipt_parser.py

import re
from datetime import datetime
from backend.utils.logger import logger


# ----------------------------------------------------------
# CATEGORY KEYWORDS FOR RECEIPT CATEGORY DETECTION
# ----------------------------------------------------------
RECEIPT_CATEGORY_KEYWORDS = {
    "Fuel": ["petrol", "diesel", "fuel", "pump", "hp", "io"],
    "Grocery": ["mart", "supermarket", "grocery", "fresh", "bazaar", "bazar", "store", "kirana"],
    "Restaurant": ["restaurant", "cafe", "food", "dining", "hotel", "swiggy", "zomato"],
    "Pharmacy": ["medical", "pharmacy", "chemist", "medicare", "drug"],
    "Shopping": ["mall", "electronics", "fashion", "lifestyle", "reliance", "myntra", "flipkart"],
    "Utilities": ["bill", "electricity", "water", "gas", "recharge", "dth"],
}


# ----------------------------------------------------------
# Clean merchant name
# ----------------------------------------------------------
def clean_merchant_name(name: str):
    # Remove common noise
    noise = ["gst", "bill", "tax", "invoice", "#", "no", "date"]
    words = name.split()
    filtered = [w for w in words if w.lower() not in noise]

    cleaned = " ".join(filtered).strip()
    return cleaned.title() if cleaned else name.title()


# ----------------------------------------------------------
# MAIN RECEIPT PARSER
# ----------------------------------------------------------
def parse_receipt_text(text: str):
    logger.info("🔍 Parsing OCR text from receipt...")

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    text_low = text.lower()

    amount = 0.0
    merchant = "Unknown"
    date_found = None
    items = []

    # ------------------------------------------------------
    # Amount Extraction (priority-first)
    # ------------------------------------------------------
    amount_patterns = [
        r'grand\s*total[:\-]?\s*₹?\s*([\d,]+\.?\d*)',
        r'total\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)',
        r'amount\s*payable[:\-]?\s*₹?\s*([\d,]+\.?\d*)',
        r'net\s*amount[:\-]?\s*₹?\s*([\d,]+\.?\d*)',
        r'bill\s*amt[:\-]?\s*₹?\s*([\d,]+\.?\d*)',
        r'₹\s*([\d,]+\.?\d*)',
        r'rs\.?\s*([\d,]+\.?\d*)'
    ]

    for line in lines:
        l_low = line.lower()
        for pattern in amount_patterns:
            m = re.search(pattern, l_low)
            if m:
                try:
                    amount = float(m.group(1).replace(",", ""))
                    break
                except:
                    continue
        if amount > 0:
            break

    # Fallback: find highest number in receipt
    if amount == 0:
        numbers = re.findall(r'\b\d{2,7}\.?\d*\b', text_low)
        if numbers:
            nums = [float(n.replace(",", "")) for n in numbers]
            amount = max(nums)

    # ------------------------------------------------------
    # Merchant Detection (top 5 lines)
    # ------------------------------------------------------
    merchant_patterns = [
        r'(.*store.*)',
        r'(.*mart.*)',
        r'(.*bazaar.*)',
        r'(reliance.*)',
        r'(dmart.*)',
        r'(big bazaar.*)',
        r'(.*petrol.*pump.*)',
        r'(.*restaurant.*)',
        r'(.*medical.*store.*)',
    ]

    for line in lines[:5]:
        l_low = line.lower()
        for pat in merchant_patterns:
            if re.search(pat, l_low):
                merchant = clean_merchant_name(line)
                break
        if merchant != "Unknown":
            break

    # ------------------------------------------------------
    # Date Extraction
    # ------------------------------------------------------
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})',
    ]

    for pat in date_patterns:
        d = re.search(pat, text_low)
        if d:
            raw = d.group(1)
            for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y"]:
                try:
                    date_found = datetime.strptime(raw, fmt)
                    break
                except:
                    continue
        if date_found:
            break

    if not date_found:
        date_found = datetime.now()

    # ------------------------------------------------------
    # Item Extraction
    # ------------------------------------------------------
    item_pattern = r'([A-Za-z0-9 \-]+)\s+(\d+)\s*x\s*([\d\.]+)'
    for line in lines:
        m = re.search(item_pattern, line)
        if m:
            items.append({
                "name": m.group(1).strip().title(),
                "quantity": int(m.group(2)),
                "price": float(m.group(3))
            })

    # ------------------------------------------------------
    # Category Detection
    # ------------------------------------------------------
    category = "Expense"
    for cat, keywords in RECEIPT_CATEGORY_KEYWORDS.items():
        if any(k in text_low for k in keywords):
            category = cat.title()
            break

    # ------------------------------------------------------
    # Final Return Structure
    # ------------------------------------------------------
    return {
        "amount": amount,
        "merchant": merchant,
        "date": date_found.isoformat(),
        "items": items,
        "category": category,
        "message": text,
        "type": "Expense"
    }
