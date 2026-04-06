import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load .env
ENV_PATH = Path('C:/Users/Bhairavi Salunkhe/Desktop/documind_ai/.env')
load_dotenv(ENV_PATH)

api_key = os.environ.get("GEMINI_API_KEY")
print(f"Testing Gemini Key: {api_key[:10]}...")

if not api_key:
    print("Error: GEMINI_API_KEY is missing!")
    exit(1)

model_name = "gemini-2.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
payload = {"contents": [{"parts": [{"text": "Say test."}]}]}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response:", response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', ''))
    else:
        print("Error Response:", response.text)
except Exception as e:
    print(f"Exception: {str(e)}")
