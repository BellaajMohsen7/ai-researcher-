import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# We test HuggingFace Serverless Inference API with a meta-llama model
# that supports tool calling natively
model_id = "huggingface/meta-llama/Meta-Llama-3-70B-Instruct"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

print(f"Testing {model_id} with Tool Calling...")

try:
    response = completion(
        model=model_id,
        messages=[{"role": "user", "content": "What's the weather like in Boston today?"}],
        tools=tools,
        tool_choice="auto",
        api_key=os.getenv("HF_API_TOKEN")
    )
    print("SUCCESS!")
    print(response.choices[0].message)
except Exception as e:
    print("FAILED!")
    print(e)
