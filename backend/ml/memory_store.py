from sentence_transformers import SentenceTransformer, util
from datetime import datetime
import torch
from backend.utils.logger import logger

class VectorMemory:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # We can potentially share the model instance if passed, but for now load separately
        self.embedder = SentenceTransformer(model_name)
        self.memory = [] # List of dicts: {'text': str, 'embedding': tensor, 'metadata': dict}
        self.limit = 50 # Keep last 50 interactions for now
        
    def add_interaction(self, user_text, bot_response, intent, entities):
        """Store the interaction in memory"""
        text = f"User: {user_text} | Bot: {bot_response}"
        embedding = self.embedder.encode(text, convert_to_tensor=True)
        
        entry = {
            "text": text,
            "embedding": embedding,
            "timestamp": datetime.now(),
            "metadata": {
                "user_text": user_text,
                "bot_response": bot_response,
                "intent": intent,
                "entities": entities
            }
        }
        
        self.memory.append(entry)
        
        # Prune if too large
        if len(self.memory) > self.limit:
            self.memory.pop(0)
            
    def get_context(self, current_query, top_k=3):
        """Retrieve relevant past interactions"""
        if not self.memory:
            return []
            
        query_embedding = self.embedder.encode(current_query, convert_to_tensor=True)
        
        # Stack memory embeddings
        memory_embeddings = torch.stack([m['embedding'] for m in self.memory])
        
        # Compute cosine similarity
        cos_scores = util.cos_sim(query_embedding, memory_embeddings)[0]
        
        # Get top_k results
        # If we have fewer than top_k memories, take all
        k = min(top_k, len(self.memory))
        top_results = torch.topk(cos_scores, k=k)
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            if score > 0.4: # Relevance threshold
                results.append(self.memory[idx])
                
        return results
