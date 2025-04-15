import logging
import os
import numpy as np
from supabase import create_client, Client
from sklearn.metrics.pairwise import cosine_similarity
from web_tools import generate_embedding as generate_web_embedding
import config
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FAQ_TABLE_NAME = "ecommerce_faq_memory"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger = logging.getLogger(__name__)

def search_similar_faqs(query: str, match_threshold: float = 0.75, match_count: int = 5):
    """Searches for similar FAQs in the memory using the Supabase function."""
    query_embedding = generate_web_embedding(query)
    if not query_embedding:
        logger.warning(f"Could not generate embedding for query: '{query}'.")
        return []

    try:
        response = supabase.rpc('match_faqs', {
            'query_embedding': query_embedding,
            'match_threshold': match_threshold,
            'match_count': match_count
        }).execute()

        if response.data is None:
            logger.error(f"Error searching for similar FAQs: {response}") # Log the entire response for debugging
            return []
        return response.data

    except Exception as e:
        logger.error(f"Error searching for similar FAQs: {e}")
        return []

def save_faq_to_memory(question: str, answer: str):
    """Saves a new FAQ to the memory."""
    question_embedding = generate_web_embedding(question)
    if not question_embedding:
        logger.warning(f"Could not generate embedding for question: '{question}'.")
        return

    try:
        data, count = supabase.from_(FAQ_TABLE_NAME).insert({
            "question": question,
            "answer": answer,
            "embedding": question_embedding
        }).execute()
        logger.info(f"FAQ saved to memory: Q='{question[:50]}...', A='{answer[:50]}...'")
    except Exception as e:
        logger.error(f"Error saving FAQ to memory: {e}")

if __name__ == '__main__':
   
    query = "What is your return policy?"
    similar_faqs = search_similar_faqs(query)
    print("Similar FAQs:", similar_faqs)

    