"""Smoke script: register/login, create a project, then call /projects/{id}/start

Usage:
  poetry run python scripts/start_project.py

Reads TEST_USER_EMAIL and TEST_USER_PASSWORD from env if present.
"""
import os
import sys
import requests

API = os.environ.get("API_URL", "http://localhost:8000/api/v1")
EMAIL = os.environ.get("TEST_USER_EMAIL", "test@example.com")
PW = os.environ.get("TEST_USER_PASSWORD", "password123")

s = requests.Session()

# Try login
print("Attempting login...")
r = s.post(f"{API}/auth/login", json={"email": EMAIL, "password": PW}, timeout=10)
print("POST /auth/login ->", r.status_code)
print(r.text)
if r.status_code == 200:
    token = r.json().get("access_token")
    headers = {"Authorization": "Bearer " + token}
else:
    print("Registering user...")
    r = s.post(f"{API}/auth/register", json={"email": EMAIL, "password": PW, "full_name": "Smoke Tester"}, timeout=10)
    print("POST /auth/register ->", r.status_code)
    print(r.text)
    if r.status_code not in (200, 201):
        sys.exit(1)
    r = s.post(f"{API}/auth/login", json={"email": EMAIL, "password": PW}, timeout=10)
    print("POST /auth/login ->", r.status_code)
    print(r.text)
    if r.status_code != 200:
        sys.exit(1)
    token = r.json().get("access_token")
    headers = {"Authorization": "Bearer " + token}

print("Creating project...")
r = s.post(f"{API}/projects", json={"name": "SMOKE Start Project", "description": "Start endpoint test"}, headers=headers, timeout=10)
print("POST /projects ->", r.status_code)
print(r.text)
if r.status_code not in (200, 201):
    sys.exit(1)
project = r.json()
project_id = project.get("id")

print("Calling start endpoint for project:", project_id)
r = s.post(f"{API}/projects/{project_id}/start", headers=headers, timeout=10)
print("POST /projects/{id}/start ->", r.status_code)
print(r.text)

if r.status_code in (200, 202):
    print("Start request accepted; tail server logs to follow pipeline progress.")
else:
    print("Start request failed; check Authorization token and ownership.")
    sys.exit(1)
