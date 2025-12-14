"""Checks the LLM health endpoint and prints the result.

Usage: poetry run python scripts/check_llm_health.py
"""
import requests
import os

API = os.environ.get("API_URL", "http://localhost:8000/api/v1")

r = requests.get(f"{API}/llm/health", timeout=10)
print(r.status_code)
try:
    print(r.json())
except Exception:
    print(r.text)
