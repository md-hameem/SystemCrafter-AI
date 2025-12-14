import os
import sys
import requests

API = os.environ.get('API_URL', 'http://localhost:8000/api/v1')
EMAIL = os.environ.get('TEST_USER_EMAIL', 'test@example.com')
PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'password123')

s = requests.Session()

# login
r = s.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
if r.status_code != 200:
    print('Login failed:', r.status_code, r.text)
    sys.exit(1)

token = r.json().get('access_token')
headers = {'Authorization': 'Bearer ' + token}

# find latest SMOKE Test Project
r = s.get(f"{API}/projects?skip=0&limit=50", headers=headers, timeout=10)
if r.status_code != 200:
    print('Failed to list projects:', r.status_code, r.text); sys.exit(1)
projects = r.json()

proj = None
for p in projects:
    if p.get('name') == 'SMOKE Test Project':
        proj = p
        break

if not proj:
    print('No SMOKE Test Project found')
    sys.exit(2)

proj_id = proj['id']
print('Found project', proj_id)

# get tasks for project
r = s.get(f"{API}/tasks/project/{proj_id}", headers=headers, timeout=10)
print('GET /tasks/project ->', r.status_code)
print(r.text)

# also get project details
r = s.get(f"{API}/projects/{proj_id}", headers=headers, timeout=10)
print('GET /projects/{proj_id} ->', r.status_code)
print(r.text)
