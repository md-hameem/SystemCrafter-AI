import os
import requests
import sys

BASE = os.environ.get("SC_BASE_URL", "http://127.0.0.1:8000/api/v1")


def get_token(session: requests.Session) -> str | None:
    """Obtain a bearer token by logging in. If credentials provided via env, try login, else return None."""
    email = os.environ.get("SC_EMAIL")
    password = os.environ.get("SC_PASSWORD")
    if not email or not password:
        # Try to auto-register a temporary user
        print("No SC_EMAIL/SC_PASSWORD set; attempting auto-register of a temporary user")
        import secrets
        temp_email = f"sc_auto_{secrets.token_hex(4)}@example.com"
        temp_password = secrets.token_urlsafe(12)
        try:
            r = session.post(f"{BASE}/auth/register", json={"email": temp_email, "password": temp_password, "full_name": "Auto Generated"}, timeout=10)
            if r.status_code in (200, 201):
                print("Auto-registered user:", temp_email)
                # set for later token retrieval
                email = temp_email
                password = temp_password
            else:
                print("Auto-register failed (status):", r.status_code, r.text)
                return None
        except Exception as exc:
            print("Auto-register exception:", exc)
            return None

    # Try JSON login endpoint first
    try:
        r = session.post(f"{BASE}/auth/login", json={"email": email, "password": password}, timeout=10)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass

    # Fallback to OAuth2 token endpoint (form)
    try:
        r = session.post(f"{BASE}/auth/token", data={"username": email, "password": password}, timeout=10)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass

    # Could not get token
    return None


def main():
    session = requests.Session()
    token = get_token(session)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("Proceeding unauthenticated — if the API requires auth this will fail with 401.")

    try:
        r = session.get(f"{BASE}/projects?limit=10", headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        projects = data if isinstance(data, list) else data.get("items", [])
        if not projects:
            print("No projects found. Creating a demo project...")
            demo = {
                "name": "Demo Project",
                "description": "Auto-created demo project for testing the pipeline",
            }
            r_create = session.post(f"{BASE}/projects", json=demo, headers=headers, timeout=10)
            if r_create.status_code not in (200, 201):
                print("Failed to create demo project:", r_create.status_code, r_create.text)
                sys.exit(1)
            proj = r_create.json()
        else:
            proj = projects[0]
        proj_id = proj.get("id") or proj.get("project_id")
        print("Starting project:", proj_id)
        r2 = session.post(f"{BASE}/projects/{proj_id}/start", headers=headers, timeout=10)
        print(r2.status_code)
        print(r2.text)
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
