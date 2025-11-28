# backend/services/nlp_engine.py

import re
import random
from typing import Dict, List, Tuple


class NLPEngine:
    """
    Intent + entity extraction system.
    Simplified, stable, and aligned with the orchestrator.
    """

    def __init__(self):

        # ----------------------------------------------
        # INTENT DEFINITIONS
        # ----------------------------------------------
        self.intent_patterns = {
            "balance_inquiry": {
                "patterns": [
                    r"(balance|kitna.*paisa|remaining.*amount)",
                    r"(current.*balance|how.*much.*money)"
                ],
                "keywords": ["balance", "paisa", "remaining", "money"]
            },

            "transaction_add": {
                "patterns": [
                    r"(add|spend|expense|kharcha).*(\d+)",
                    r"(\d+).*(rs|rupaye|rupees).*(add|spend)",
                    r"(petrol|food|kirana|fuel).*(\d+)"
                ],
                "keywords": ["add", "expense", "spend", "kharcha"]
            },

            "financial_advice": {
                "patterns": [
                    r"(tax.*saving|deduction)",
                    r"(investment|mutual.*fund|stock)",
                    r"(saving|bachat|financial.*tip)",
                    r"(budget|monthly.*planning)"
                ],
                "keywords": ["tax", "investment", "saving", "budget"]
            },

            "transaction_history": {
                "patterns": [
                    r"(history|record|statement|transactions)",
                    r"(past.*spending|previous.*transaction)",
                    r"(show.*expenses|where.*money.*went)"
                ],
                "keywords": ["history", "transactions", "past"]
            },

            "general_help": {
                "patterns": [
                    r"(help|madad|sahayata)",
                    r"(how.*to.*use|instructions|guide)"
                ],
                "keywords": ["help", "guide"]
            },

            "greeting": {
                "patterns": [
                    r"(hello|hi|namaste|hey)",
                    r"(good.*morning|good.*evening)"
                ],
                "keywords": ["hello", "hi", "namaste"]
            },
        }

        # ----------------------------------------------
        # SIMPLE KNOWLEDGE BASE
        # ----------------------------------------------
        self.knowledge_base = {
            "tax": (
                "Tax Saving Options:\n"
                "- ELSS Mutual Funds (80C)\n"
                "- PPF (Public Provident Fund)\n"
                "- NPS (extra ₹50k deduction)\n"
                "- Term Insurance\n"
                "- Health Insurance (80D)\n"
            ),

            "investment": (
                "Smart Investment Tips:\n"
                "- Start SIP monthly\n"
                "- Build 6-month emergency fund\n"
                "- Follow 50-30-20 rule\n"
                "- Mix equity, debt, gold\n"
            ),

            "saving": (
                "Money Saving Tips:\n"
                "- Reduce food delivery\n"
                "- Track expenses weekly\n"
                "- Automate RD/PPF savings\n"
                "- Follow 50/30/20 rule\n"
            ),
        }

    # ------------------------------------------------------------------------------------------
    # INTENT DETECTION
    # ------------------------------------------------------------------------------------------
    def detect_intent(self, text: str) -> Tuple[str, float, Dict]:
        text = text.lower().strip()
        scores = {}

        for intent, data in self.intent_patterns.items():
            pattern_score = sum(1 for p in data["patterns"] if re.search(p, text))
            keyword_score = sum(1 for k in data["keywords"] if k in text)

            # weight = 70% regex, 30% keywords
            score = (pattern_score * 0.7) + (keyword_score * 0.3)
            scores[intent] = score

        best_intent = max(scores, key=scores.get)
        raw_score = scores[best_intent]

        # NORMALIZED CONFIDENCE
        max_possible = len(self.intent_patterns[best_intent]["patterns"]) * 0.7 + \
                       len(self.intent_patterns[best_intent]["keywords"]) * 0.3

        confidence = raw_score / max_possible if max_possible else 1
        confidence = max(0.0, min(1.0, confidence))  # clamp 0-1

        entities = self.extract_entities(text)

        return best_intent, confidence, entities

    # ------------------------------------------------------------------------------------------
    # ENTITY EXTRACTION
    # ------------------------------------------------------------------------------------------
    def extract_entities(self, text: str) -> Dict:
        entities = {}

        # Amount
        amount_patterns = [
            r"₹\s?(\d+(?:,\d+)*(?:\.\d+)?)",
            r"rs\.?\s?(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(rupaye|rupees|rs)"
        ]
        for p in amount_patterns:
            m = re.search(p, text)
            if m:
                try:
                    entities["amount"] = float(m.group(1).replace(",", ""))
                    break
                except:
                    pass

        # Category
        category_map = {
            "petrol": "Travel", "fuel": "Travel", "diesel": "Travel",
            "food": "Food & Dining", "restaurant": "Food & Dining",
            "shopping": "Shopping", "kirana": "Groceries",
            "amazon": "Shopping", "flipkart": "Shopping",
            "salary": "Income", "credited": "Income",
            "bill": "Utilities", "recharge": "Utilities"
        }
        for word, cat in category_map.items():
            if word in text:
                entities["category"] = cat
                break

        # Transaction type
        if any(w in text for w in ["credited", "salary", "received"]):
            entities["txn_type"] = "Credited"
        elif any(w in text for w in ["spent", "paid", "expense", "kharcha"]):
            entities["txn_type"] = "Debited"

        return entities

    # ------------------------------------------------------------------------------------------
    # KNOWLEDGE LOOKUP
    # ------------------------------------------------------------------------------------------
    def find_knowledge_answer(self, text: str):
        text = text.lower()
        for k in self.knowledge_base:
            if k in text:
                return self.knowledge_base[k]
        return None

    # ------------------------------------------------------------------------------------------
    # FALLBACK
    # ------------------------------------------------------------------------------------------
    def generate_fallback_response(self, text: str):
        hints = [
            "Ask me about your expenses, savings, or tax tips.",
            "You can say: 'Add expense 120 for food'.",
            "Try asking: 'What is my balance?'",
            "Say 'Give me tax saving advice' for tips.",
        ]
        return random.choice(hints)

    # ------------------------------------------------------------------------------------------
    # QUICK ACTION SUGGESTIONS
    # ------------------------------------------------------------------------------------------
    def get_quick_responses(self, intent: str) -> List[str]:
        suggestions = {
            "balance_inquiry": ["Add expense", "View history", "Tax tips"],
            "transaction_add": ["View balance", "Add another", "Categories"],
            "financial_advice": ["My balance", "Investment tips", "Tax saving"],
            "transaction_history": ["Current balance", "Show categories"],
            "general_help": ["My balance", "Add expense"],
            "greeting": ["My balance", "Add transaction"],
        }
        return suggestions.get(intent, ["My balance", "Add transaction", "Help"])
