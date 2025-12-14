import requests, json

url = "http://localhost:11434/api/models"
try:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print("ERROR:", e)
