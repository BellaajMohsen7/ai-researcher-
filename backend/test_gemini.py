import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# We test multiple Gemini models to see which free tier is active.
models_to_test = [
    "gemini/gemini-1.5-flash",
    "gemini/gemini-2.0-flash", 
    "gemini/gemini-2.0-flash-exp",
    "gemini/gemini-1.5-pro",
]

print("Starting Google Gemini Native API Tests...\n")

for model_id in models_to_test:
    print(f"Testing {model_id}...")
    try:
        response = completion(
            model=model_id,
            messages=[{"role": "user", "content": "Reply with 'Hello World!'"}],
            api_key=os.getenv("GEMINI_API_KEY")
        )
        print("SUCCESS!")
        print("Response:", response.choices[0].message.content.strip())
        print("-" * 50)
    except Exception as e:
        print("FAILED!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("-" * 50)
