from sentence_transformers import SentenceTransformer, util
import torch
from backend.utils.logger import logger

class SmartCategorizer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        logger.info("Initializing SmartCategorizer...")
        self.embedder = SentenceTransformer(model_name)
        
        # Seed data: (Example Text, Category)
        # We embed these to form our "knowledge base"
        self.seed_data = [
            ("Starbucks coffee", "Food"),
            ("McDonalds burger", "Food"),
            ("Pizza Hut", "Food"),
            ("Swiggy order", "Food"),
            ("Zomato delivery", "Food"),
            ("Lunch at office", "Food"),
            ("Groceries from BigBasket", "Food"),
            ("Vegetables market", "Food"),
            
            ("Uber ride", "Travel"),
            ("Ola cab", "Travel"),
            ("Petrol pump", "Travel"),
            ("Shell station fuel", "Travel"),
            ("Flight ticket indigo", "Travel"),
            ("Train booking irctc", "Travel"),
            ("Bus fare", "Travel"),
            
            ("Amazon purchase", "Shopping"),
            ("Flipkart order", "Shopping"),
            ("Myntra clothes", "Shopping"),
            ("Zara dress", "Shopping"),
            ("Nike shoes", "Shopping"),
            ("IKEA furniture", "Shopping"),
            
            ("Netflix subscription", "Entertainment"),
            ("Spotify premium", "Entertainment"),
            ("PVR movie tickets", "Entertainment"),
            ("BookMyShow", "Entertainment"),
            ("Disney Hotstar", "Entertainment"),
            
            ("Electricity bill", "Bills"),
            ("Water bill", "Bills"),
            ("Wifi recharge", "Bills"),
            ("Jio mobile plan", "Bills"),
            ("House rent", "Bills"),
            
            ("Salary credited", "Income"),
            ("Freelance payment", "Income"),
            ("Interest received", "Income")
        ]
        
        # Pre-compute embeddings for seed data
        self.texts = [item[0] for item in self.seed_data]
        self.categories = [item[1] for item in self.seed_data]
        self.embeddings = self.embedder.encode(self.texts, convert_to_tensor=True)
        
        logger.info(f"SmartCategorizer initialized with {len(self.seed_data)} seed examples.")

    def predict(self, text: str) -> str:
        """Predict category based on semantic similarity"""
        if not text:
            return "General"
            
        # Encode user text
        query_embedding = self.embedder.encode(text, convert_to_tensor=True)
        
        # Compute cosine similarity with all seed examples
        cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        
        # Find best match
        best_match_idx = torch.argmax(cos_scores).item()
        best_score = cos_scores[best_match_idx].item()
        
        predicted_category = self.categories[best_match_idx]
        
        logger.info(f"Categorization: '{text}' -> {predicted_category} (Score: {best_score:.2f}, Matched: '{self.texts[best_match_idx]}')")
        
        # Threshold for "Unknown" or "General"
        if best_score < 0.3:
            return "General"
            
        return predicted_category
