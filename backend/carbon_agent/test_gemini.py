import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

print("Sending request to Gemini...")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello! Reply in one sentence."
)

print("Gemini response:")
print(response.text)