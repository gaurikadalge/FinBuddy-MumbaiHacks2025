from backend.utils.logger import logger
from typing import Dict, List, Any

class VoiceSemanticsModel:
    """
    Analyzes voice transcripts for emotional markers and intent nuances.
    Detects: Urgency, Regret, Goals.
    """
    def __init__(self):
        logger.info("Initializing VoiceSemanticsModel...")
        
        self.urgency_keywords = ["urgent", "immediately", "right now", "asap", "emergency", "pay today"]
        self.regret_keywords = ["regret", "mistake", "shouldn't have", "too much", "wasted", "overspent"]
        self.goal_keywords = ["save for", "budget for", "goal", "planning to", "invest in"]

    def analyze_semantics(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for semantic markers.
        """
        text_lower = text.lower()
        semantics = {
            "urgency_detected": False,
            "regret_detected": False,
            "goal_detected": False,
            "sentiment": "Neutral",
            "tags": []
        }

        # Check Urgency
        if any(word in text_lower for word in self.urgency_keywords):
            semantics["urgency_detected"] = True
            semantics["tags"].append("Urgent")
            semantics["sentiment"] = "Anxious"

        # Check Regret
        if any(word in text_lower for word in self.regret_keywords):
            semantics["regret_detected"] = True
            semantics["tags"].append("Regret")
            semantics["sentiment"] = "Negative"

        # Check Goals
        if any(word in text_lower for word in self.goal_keywords):
            semantics["goal_detected"] = True
            semantics["tags"].append("Financial Goal")
            semantics["sentiment"] = "Positive"

        logger.info(f"Voice Semantics Analysis: {semantics}")
        return semantics
