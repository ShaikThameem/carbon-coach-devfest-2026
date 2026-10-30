import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print("Gemini API key loaded successfully!")
else:
    print("API key not found. Check your .env file.")
    