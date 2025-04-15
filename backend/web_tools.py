from typing import List, Dict
import logging
import config
import os
import google.generativeai as genai
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Configure Gemini API (ensure this is done)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Google CSE API credentials from environment variables
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def generate_embedding(text: str) -> List[float]:
    """Generates an embedding for the given text using Gemini."""
    try:
        model = config.EMBEDDING_MODEL
        response = genai.embed_content(
            model=model,
            content=text
        )
        return response['embedding']
    except Exception as e:
        logger.error(f"Error generating embedding for text: '{text}'. Error: {e}")
        return []

def perform_web_search(query: str, num_results: int = 3) -> List[Dict[str, str]]:
    """Performs a web search using Google Custom Search Engine."""
    results = []
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
        logger.warning("Google CSE API key or ID not found in environment variables.")
        return results

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_CSE_API_KEY)
        response = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()
        if 'items' in response:
            for item in response['items']:
                results.append({
                    'title': item['title'],
                    'link': item['link'],
                    'snippet': item['snippet']
                })
    except Exception as e:
        logger.error(f"Error during Google CSE request: {e}")
    return results

if __name__ == '__main__':
    # Example usage
    query = "What is the capital of France?"
    search_results = perform_web_search(query)
    if search_results:
        print("Search Results:")
        for result in search_results:
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
            print(f"Snippet: {result['snippet']}")
            print("-" * 20)

    sample_text = "This is a sample text for embedding."
    embedding = generate_embedding(sample_text)
    if embedding:
        print(f"Embedding for '{sample_text}':")
        print(embedding[:10], "...")