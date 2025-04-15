from typing import List
import logging
from clients import get_generative_model
from memory_tools import search_similar_faqs, save_faq_to_memory
from web_tools import perform_web_search, generate_embedding as generate_web_embedding
import numpy as np
import random
import requests
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = get_generative_model()

SHOPIFY_STORE_URL = "https://ecommerce-chatbot.myshopify.com"
STOREFRONT_API_TOKEN = "9328b77914fceca85f7b6849cf197dd3"

predefined_questions_and_responses = {
    "what is the return policy for this product?": "Our return policy allows you to return most items within 30 days of purchase for a full refund. Please ensure the item is in its original condition with all tags attached.",
    "how long does delivery take for orders to my location?": "Delivery times vary depending on your location. Typically, standard shipping takes 3-5 business days. You can see more detailed estimates during checkout after you provide your shipping address.",
    "can you provide details about the warranty for this item?": "The warranty for this item covers manufacturing defects for 1 year from the date of purchase. It does not cover accidental damage or misuse. Please refer to the product manual for complete warranty details.",
    "based on our last conversation, what are the payment options available on this site?": "As we discussed, we accept major credit cards (Visa, Mastercard, American Express), PayPal, and also offer options like Apple Pay and Google Pay.",
    "where can i find information about product specifications we discussed earlier?": "You can find the detailed specifications for the product we discussed on its product page. I can provide you with a link if you remember the product name, or you can search for it on our website.",
}

def cosine_similarity(a, b):
    """Calculates the cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_product_details(product_name: str):
    """Fetches product details from Shopify Storefront API by product name (using a simple search)."""
    base_url = SHOPIFY_STORE_URL
    api_endpoint = "/api/2023-10/graphql.json"
    api_url = base_url + api_endpoint

    headers = {
        "X-Shopify-Storefront-Access-Token": STOREFRONT_API_TOKEN,
        "Content-Type": "application/json",
    }


    search_query = """
        query SearchProducts($query: String!) {
          products(first: 1, query: $query) {
            edges {
              node {
                handle
              }
            }
          }
        }
    """

    search_payload = {
        "query": search_query,
        "variables": {"query": product_name}
    }

    try:
        search_response = requests.post(api_url, headers=headers, json=search_payload)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data and search_data.get("data") and search_data["data"].get("products") and search_data["data"]["products"].get("edges"):
            product_handle = search_data["data"]["products"]["edges"][0]["node"]["handle"]


            product_details_query = """
                query GetProductByHandle($handle: String!) {
                  productByHandle(handle: $handle) {
                    title
                    description
                    variants(first: 1) {
                      edges {
                        node {
                          priceV2 {
                            amount
                            currencyCode
                          }
                          availableForSale
                        }
                      }
                    }
                    featuredImage {
                      url
                    }
                  }
                }
            """

            details_payload = {
                "query": product_details_query,
                "variables": {"handle": product_handle}
            }

            details_response = requests.post(api_url, headers=headers, json=details_payload)
            details_response.raise_for_status()
            details_data = details_response.json()

            if details_data and details_data.get("data") and details_data["data"].get("productByHandle"):
                product = details_data["data"]["productByHandle"]
                variant = product.get("variants", {}).get("edges", [])[0]["node"] if product.get("variants", {}).get("edges") else {}
                return {
                    "name": product.get("title"),
                    "description": product.get("description"),
                    "price": f"{variant.get('priceV2', {}).get('amount')} {variant.get('priceV2', {}).get('currencyCode')}" if variant else "Price not available",
                    "availability": "In Stock" if variant.get("availableForSale") else "Out of Stock" if variant else "Availability not available",
                    "image_url": product.get("featuredImage", {}).get("url"),

                }
            else:
                logger.warning(f"Could not retrieve details for product with handle: {product_handle}")
                return None
        else:
            logger.warning(f"Product '{product_name}' not found on Shopify.")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching product details from Shopify: {e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Error parsing Shopify product data: {e}")
        return None
class GeneralAgent:
    def __init__(self):
        self.llm = llm
        self.tools = {
            "web_search": perform_web_search,
            "get_product_details": get_product_details,
        }

    def run(self, user_query: str) -> str:
        logger.info(f"Agent received query: {user_query}")


        user_query_lower = user_query.lower().strip()
        if user_query_lower in ["hello", "hi"]:
            greetings = [
                "Hey there! Ready to explore our amazing products?",
                "Hi! What can I help you find today?",
                "Hello! Welcome to our store. How can I assist you?",
                "Greetings! Looking for something special?",
                "Hiya! Let's find what you need."
            ]
            return random.choice(greetings)

        if user_query_lower in predefined_questions_and_responses:
            return predefined_questions_and_responses[user_query_lower]

       
        similar_faqs = search_similar_faqs(user_query)
        if similar_faqs:
            best_match = similar_faqs[0]
            logger.info(f"Found similar FAQ (Similarity: {best_match['similarity']:.2f}): {best_match['question']}")
            return f"(From memory) {best_match['answer']}"

        logger.info("No relevant FAQ found in memory. Proceeding to check for product query.")

       
        if "product" in user_query_lower or "about" in user_query_lower or "details for" in user_query_lower:
            logger.info("Query seems to be about a specific product. Trying product details tool.")
            product_name = ""
            if "about" in user_query_lower:
                product_name = user_query.split("about")[-1].strip()
            elif "product" in user_query_lower:
                product_name = user_query.split("product")[-1].strip()
            elif "details for" in user_query_lower:
                product_name = user_query.split("details for")[-1].strip()

            product_name = product_name.replace("\"", "").replace("'", "").strip() # Clean up the product name

            product_info = self.tools["get_product_details"](product_name)
            if product_info:
                logger.info(f"Tool 'get_product_details' executed for '{product_name}'.")
                details = "\n".join([f"{key.capitalize()}: {value}" for key, value in product_info.items()])
                return f"(From product catalog)\n{details}"
            else:
                logger.info(f"Product '{product_name}' not found in catalog.")
                return "Sorry, I couldn't find details for that product in our catalog."

        logger.info("Not a product-specific query. Proceeding to web search.")

        
        search_results = []
        try:
            search_results = self.tools["web_search"](user_query)
            logger.info(f"Tool 'perform_web_search' executed.")
        except Exception as e:
            logger.error(f"Error executing web search tool: {e}", exc_info=True)
            return "Sorry, there was an error trying to search the web for information."

        if not search_results:
            return "Sorry, I couldn't find relevant information online for your query."

       
        query_embedding = generate_web_embedding(user_query)

        scored_results = []
        for res in search_results:
            title_similarity = cosine_similarity(query_embedding, res.get('title_embedding', []))
            snippet_similarity = cosine_similarity(query_embedding, res.get('snippet_embedding', []))
            res['similarity_score'] = snippet_similarity
            scored_results.append(res)

        scored_results.sort(key=lambda x: x.get('similarity_score', 0.0), reverse=True)

        top_n = 3
        relevant_results = scored_results[:top_n]

        context = "\n---\n".join([
            f"Title: {res.get('title', 'N/A')}\nSnippet: {res.get('snippet', 'N/A')}"
            for res in relevant_results
        ])

        final_answer_prompt = f"""
        You are a helpful AI assistant. Answer the user's query based *only* on the provided web search results context.
        Be concise and informative. If the context doesn't fully answer the query, state what you found and indicate that the information might be incomplete based on the search results.
        Do not make up information not present in the context.

        User Query: {user_query}

        Web Search Results Context:
        ---
        {context}
        ---

        Based *only* on the context above, answer the user query.
        """

        try:
            response = self.llm.generate_content(final_answer_prompt)
            if hasattr(response, 'text'):
                final_answer = response.text
            elif isinstance(response, str):
                final_answer = response
            else:
                try:
                    final_answer = response.parts[0].text if response.parts else "Could not extract text from response."
                except (AttributeError, IndexError):
                    final_answer = "Received an unexpected response format from the language model."

            logger.info("LLM generated final answer from web context.")

            if final_answer and "Sorry" not in final_answer and "error" not in final_answer.lower():
                logger.info(f"Attempting to save Q: '{user_query}' A: '{final_answer[:200]}...' to memory.")
                save_faq_to_memory(user_query, final_answer)

            return final_answer

        except Exception as e:
            logger.error(f"Error generating final answer with LLM: {e}", exc_info=True)
            return "Sorry, I encountered an error while processing the information."


agent = GeneralAgent()

def get_agent_response(query: str) -> str:
    """Entry point to interact with the agent."""
    return agent.run(query)