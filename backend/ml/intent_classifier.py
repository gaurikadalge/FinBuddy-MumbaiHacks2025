import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from backend.utils.logger import logger

class IntentClassifier:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_path = "backend/ml/models/intent_model.pkl"
        self.encoder_path = "backend/ml/models/label_encoder.pkl"
        
        logger.info(f"Loading embedding model: {model_name}...")
        self.embedder = SentenceTransformer(model_name)
        
        self.clf = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        self.le = LabelEncoder()
        self.is_trained = False
        
        # Small initial dataset to bootstrap
        self.training_data = {
            "check_balance": [
                "What is my balance?", "How much money do I have?", "Show my account balance", 
                "Check balance", "My current balance", "Do I have enough money?", "Bank balance"
            ],
            "add_transaction": [
                "I spent 500 on food", "Add expense of 200", "Bought groceries for 1000",
                "Paid 5000 for rent", "Deducted 200 from wallet", "Spent 50 rs on tea",
                "Transaction of 500", "Record a payment"
            ],
            "tax_advice": [
                "How can I save tax?", "Tax saving options", "80C deductions", 
                "Investments for tax saving", "Reduce my tax liability", "Tax planning help"
            ],
            "transaction_history": [
                "Show my recent transactions", "Where did I spend money?", "Last 5 expenses",
                "History of transactions", "My spending report", "Statement for this month"
            ],
            "greeting": [
                "Hello", "Hi", "Hey there", "Good morning", "Namaste", "Hola"
            ],
            "help": [
                "Help me", "What can you do?", "Show menu", "Guide me", "Features", "How to use"
            ]
        }
        
        self._train_or_load()

    def _train_or_load(self):
        # For now, we'll retrain on startup to keep it simple and robust. 
        # In prod, we would load from disk.
        logger.info("Training intent classifier...")
        X_raw = []
        y_raw = []
        
        for intent, phrases in self.training_data.items():
            for phrase in phrases:
                X_raw.append(phrase)
                y_raw.append(intent)
                
        X_embeddings = self.embedder.encode(X_raw)
        y_encoded = self.le.fit_transform(y_raw)
        
        self.clf.fit(X_embeddings, y_encoded)
        self.is_trained = True
        logger.info("Intent classifier trained successfully.")

    def predict(self, text):
        if not self.is_trained:
            return "unknown", 0.0
            
        embedding = self.embedder.encode([text])
        prob = self.clf.predict_proba(embedding)[0]
        pred_idx = np.argmax(prob)
        confidence = prob[pred_idx]
        
        intent = self.le.inverse_transform([pred_idx])[0]
        
        # Threshold
        if confidence < 0.4:
            return "unknown", confidence
            
        return intent, confidence
