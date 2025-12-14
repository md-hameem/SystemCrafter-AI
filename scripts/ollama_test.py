import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "kimi-k2:1t-cloud",
    "prompt": "Please respond with a short JSON object: {\"status\": \"ok\"}",
    "temperature": 0.0,
    "max_tokens": 64,
}

try:
    resp = requests.post(url, json=payload, timeout=30)
    print(f"STATUS:{resp.status_code}")
    print(resp.text)
except Exception as e:
    print(f"ERROR: {e}")
