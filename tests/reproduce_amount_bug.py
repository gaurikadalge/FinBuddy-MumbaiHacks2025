import re

def extract_amount(text: str):
    # Current Regex in NERExtractor
    m = re.search(r"(?:₹|Rs\.?|INR)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

def extract_amount_fixed(text: str):
    # Proposed Fix: Allow more digits at the start
    m = re.search(r"(?:₹|Rs\.?|INR)?\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

test_cases = [
    "I spent 1000 rupees",
    "Paid 10000 for rent",
    "500 rs",
    "1,000 rupees",
    "1,50,000 (Indian format often uses 2 digits after first 3, but let's see standard)",
    "Cost is 12345.50"
]

print("--- Current Regex ---")
for t in test_cases:
    print(f"'{t}' -> {extract_amount(t)}")

print("\n--- Fixed Regex ---")
for t in test_cases:
    print(f"'{t}' -> {extract_amount_fixed(t)}")
