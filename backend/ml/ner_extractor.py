from transformers import pipeline
import re
from backend.utils.logger import logger

class NERExtractor:
    def __init__(self):
        logger.info("Loading NER and Sentiment pipelines (this may take a moment)...")
        # Use a smaller, faster model for NER
        self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        
        # Sentiment analysis
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
    def extract_entities(self, text):
        entities = {}
        
        # 1. Standard NER (Person, Org, Loc, Date)
        ner_results = self.ner_pipeline(text)
        for res in ner_results:
            group = res['entity_group']
            word = res['word']
            if group not in entities:
                entities[group] = []
            entities[group].append(word)
            
        # 2. Custom Regex for Amounts (INR)
        amount = self._extract_amount(text)
        if amount:
            entities['AMOUNT'] = amount
            
        # 3. Sentiment
        sentiment = self.sentiment_pipeline(text)[0]
        entities['SENTIMENT'] = sentiment['label']
        entities['SENTIMENT_SCORE'] = sentiment['score']
        
        return entities

    def _extract_amount(self, text: str):
        """Detect amounts like '500', '₹500', '500 rs'"""
        # Improved regex to handle commas and decimals
        # Changed \d{1,3} to \d+ to allow unformatted numbers like 1000 or 10000
        m = re.search(r"(?:₹|Rs\.?|INR)?\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)", text, re.IGNORECASE)
        if m:
            try:
                val_str = m.group(1).replace(",", "")
                return float(val_str)
            except:
                return None
        return None
