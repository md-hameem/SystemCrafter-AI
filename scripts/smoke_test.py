import os
import sys
import requests

API = os.environ.get('API_URL', 'http://localhost:8000/api/v1')
EMAIL = os.environ.get('TEST_USER_EMAIL', 'test@example.com')
PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'password123')

s = requests.Session()

try:
    r = s.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
except Exception as e:
    print('login request error', e)
    sys.exit(1)

print('POST /auth/login ->', r.status_code)
print(r.text)

if r.status_code == 200:
    token = r.json().get('access_token')
    headers = {'Authorization': 'Bearer ' + token}
else:
    print('Attempting register...')
    r = s.post(f"{API}/auth/register", json={"email": EMAIL, "password": PASSWORD, "full_name": "Test User"}, timeout=10)
    print('POST /auth/register ->', r.status_code)
    print(r.text)
    if r.status_code not in (200, 201):
        sys.exit(1)
    r = s.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    print('POST /auth/login (after register) ->', r.status_code)
    print(r.text)
    if r.status_code != 200:
        sys.exit(1)
    token = r.json().get('access_token')
    headers = {'Authorization': 'Bearer ' + token}

print('Creating project...')
r = s.post(f"{API}/projects", json={"name": "SMOKE Test Project", "description": "Smoke test"}, headers=headers, timeout=20)
print('POST /projects ->', r.status_code)
print(r.text)

if r.status_code not in (200,201):
    sys.exit(2)

print('Done')
