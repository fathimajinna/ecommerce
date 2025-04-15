import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

print("List of models that support generateContent:\n")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)

print("\nList of models that support embedContent:\n")
for model in genai.list_models():
    if "embedContent" in model.supported_generation_methods:
        print(model.name)