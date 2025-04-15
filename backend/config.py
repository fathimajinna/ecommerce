import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# --- Model Settings ---
EMBEDDING_MODEL = "models/embedding-001"  # Or a suitable Gemini embedding model
GENERATION_MODEL = "models/gemini-1.5-flash" # Or a suitable Gemini generation model
EMBEDDING_DIM = 768 # You might need to adjust this based on the Gemini embedding model

# --- Supabase Settings ---
SIMILARITY_THRESHOLD = 0.7
MATCH_COUNT = 3

# --- Serper API Settings ---
SEARCH_RESULT_COUNT = 5