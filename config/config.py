import os
from dotenv import load_dotenv

# Load environment variables from .env file (local environment)
load_dotenv()

# Fetch the API_KEY from environment variable
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY is not set. Please configure GitHub Secrets or local .env file.")
