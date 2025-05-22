import requests
import os
from dotenv import load_dotenv

from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.environ.get("AI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "what is 2 + 2?",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)
