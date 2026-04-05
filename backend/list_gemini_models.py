import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing available Gemini models for your API key...\n")
try:
    for m in client.models.list():
        print(f"Model Name: {m.name}")
        print(f"Display Name: {m.display_name}")
        print(f"Description: {m.description}")
        print("-" * 30)
except Exception as e:
    print(f"Error listing models: {e}")
