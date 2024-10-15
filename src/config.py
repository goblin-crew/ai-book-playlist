import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenAI configuration from environment variables
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def print_configuration():
    print("Configuration:")
    print(f"OPENAI_MODEL: {OPENAI_MODEL}")
    print(f"OPENAI_API_BASE: {OPENAI_API_BASE}")
    print(f"LOG_LEVEL: {LOG_LEVEL}")
