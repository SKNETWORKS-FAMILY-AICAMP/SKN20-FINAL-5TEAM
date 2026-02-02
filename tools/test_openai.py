import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    print("Testing OpenAI Connectivity...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, respond with 'READY'"}],
        max_tokens=5
    )
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"OpenAI Test Failed: {e}")
