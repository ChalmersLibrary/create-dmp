import os
from dotenv import load_dotenv

# Load .env file from the package directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

# Optional: expose main function
from .main import main
