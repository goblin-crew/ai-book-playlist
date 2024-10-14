import os
from dotenv import load_dotenv

def check_environment():
    print("Checking environment setup...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found. Please create a .env file with your API keys.")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: The following required environment variables are missing: {', '.join(missing_vars)}")
        print("Please add them to your .env file.")
        return False
    
    # Check for required packages
    try:
        import langchain
        import langchain_community
        import openai
        import spotipy
    except ImportError as e:
        print(f"Error: Required package not found: {e.name}")
        print("Please make sure you have activated the correct Conda environment and all packages are installed.")
        return False
    
    print("Environment setup looks good!")
    return True

if __name__ == "__main__":
    check_environment()
