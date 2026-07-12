import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# Retrieve the key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in .env file")
elif not api_key.startswith("sk-"):
    print("WARNING: Key does not look like an OpenAI key (should start with 'sk-')")
else:
    masked = api_key[:7] + "..." + api_key[-4:]
    print(f"Key loaded successfully: {masked}")
    print(f"Length: {len(api_key)} characters")
    echo "OPENAI_API_KEY=sk-your-key-here" > .env
printf "%s\n" ".env" "venv/" "__pycache__/" "*.pyc" > .gitignore