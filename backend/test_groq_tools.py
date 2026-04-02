import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

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

try:
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
          {
            "role": "user",
            "content": "What's the weather like in Boston today?"
          }
        ],
        tools=tools,
        tool_choice="auto",
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None
    )
    print("SUCCESS:")
    print(completion.choices[0].message)
except Exception as e:
    print("FAILED:")
    print(e)
