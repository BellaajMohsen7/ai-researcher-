import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()
completion = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
      {
        "role": "user",
        "content": "Tell me a fun fact about Artificial Intelligence."
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
