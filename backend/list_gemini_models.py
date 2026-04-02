import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Listing available Gemini models for your API key...\n")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Description: {m.description}")
            print("-" * 30)
except Exception as e:
    print(f"Error listing models: {e}")
