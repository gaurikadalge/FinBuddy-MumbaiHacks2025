# backend/utils/constants.py

# -----------------------------------------
# TRANSACTION CATEGORY RULES (Expanded & Cleaned)
# -----------------------------------------

CATEGORY_RULES = {
    # ======================
    # INCOME
    # ======================
    "salary": "Income: Salary",
    "credited": "Income: Other",
    "credit": "Income: Other",
    "neft": "Income: Transfer",
    "imps": "Income: Transfer",
    "upi received": "Income: Transfer",
    "payout": "Income: Freelance",
    "received": "Income: Other",
    "refund": "Income: Refund",
    "cashback": "Income: Cashback",

    # ======================
    # FOOD & DINING
    # ======================
    "zomato": "Expense: Food & Dining",
    "swiggy": "Expense: Food & Dining",
    "dominos": "Expense: Food & Dining",
    "kfc": "Expense: Food & Dining",
    "restaurant": "Expense: Food & Dining",
    "hotel": "Expense: Food & Dining",        # added
    "food": "Expense: Food & Dining",
    "dining": "Expense: Food & Dining",

    # ======================
    # TRAVEL / FUEL
    # ======================
    "uber": "Expense: Travel",
    "ola": "Expense: Travel",
    "rapido": "Expense: Travel",
    "irctc": "Expense: Travel",
    "metro": "Expense: Travel",
    "train": "Expense: Travel",
    "flight": "Expense: Travel",

    # Fuel-specific
    "petrol": "Expense: Fuel",
    "diesel": "Expense: Fuel",
    "fuel": "Expense: Fuel",

    # ======================
    # SHOPPING
    # ======================
    "amazon": "Expense: Shopping",
    "flipkart": "Expense: Shopping",
    "myntra": "Expense: Shopping",
    "ajio": "Expense: Shopping",

    # Groceries
    "bigbasket": "Expense: Groceries",
    "dmart": "Expense: Groceries",
    "kirana": "Expense: Groceries",
    "grocery": "Expense: Groceries",           # added

    # ======================
    # UTILITIES
    # ======================
    "airtel": "Expense: Utility",
    "jio": "Expense: Utility",
    "vodafone": "Expense: Utility",
    "vi": "Expense: Utility",                  # added

    "electricity": "Expense: Utility",
    "water": "Expense: Utility",               # added
    "gas": "Expense: Utility",                 # added
    "gas bill": "Expense: Utility",
    "water bill": "Expense: Utility",
    "mobile recharge": "Expense: Utility",
    "recharge": "Expense: Utility",            # added

    # ======================
    # HOUSING
    # ======================
    "rent": "Expense: Housing",
    "maintenance": "Expense: Housing",
    "society": "Expense: Housing",

    # ======================
    # LOANS & FINANCE
    # ======================
    "emi": "Expense: Loan EMI",
    "installment": "Expense: Loan EMI",
    "loan": "Expense: Loan EMI",
    "credit card": "Expense: Credit Card Payment",

    # ======================
    # HEALTHCARE
    # ======================
    "hospital": "Expense: Healthcare",
    "doctor": "Expense: Healthcare",
    "medical": "Expense: Healthcare",
    "pharmacy": "Expense: Healthcare",
    "apollo": "Expense: Healthcare",

    # ======================
    # ENTERTAINMENT
    # ======================
    "netflix": "Expense: Entertainment",
    "prime video": "Expense: Entertainment",
    "amazon prime": "Expense: Entertainment",  # added
    "hotstar": "Expense: Entertainment",       # added
    "disney": "Expense: Entertainment",
    "spotify": "Expense: Entertainment",
    "movie": "Expense: Entertainment",

    # ======================
    # INVESTMENT
    # ======================
    "mutual fund": "Expense: Investment",
    "stock": "Expense: Investment",
    "zerodha": "Expense: Investment",
    "groww": "Expense: Investment",

    # ======================
    # DEFAULT FALLBACK
    # ======================
    "default": "Expense: Other"
}

