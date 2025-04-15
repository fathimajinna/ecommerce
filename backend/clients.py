
import google.generativeai as genai
import config
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Gemini Clients ---
def get_embedding_model():
    """Gets the Gemini Embedding Model name."""
    genai.configure(api_key=GEMINI_API_KEY)
    return config.EMBEDDING_MODEL

def get_generative_model():
    """Gets the Gemini Text Generation Model instance."""
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(config.GENERATION_MODEL)

