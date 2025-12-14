#!/usr/bin/env python3
"""Watch project WebSocket events and print them to stdout.

Usage:
  SC_EMAIL/SC_PASSWORD env vars or --token must be provided.
  python scripts/watch_project_ws.py --project <project_id>
"""
import os
import sys
import requests
from websocket import create_connection

BASE = os.environ.get("SC_BASE_URL", "http://127.0.0.1:8000/api/v1")
API_ROOT = BASE.split("/api/v1")[0]
WS_ROOT = API_ROOT.replace("http://", "ws://").replace("https://", "wss://")


def get_token(session: requests.Session) -> str | None:
    email = os.environ.get("SC_EMAIL")
    password = os.environ.get("SC_PASSWORD")
    if not email or not password:
        return None
    # try JSON login
    try:
        r = session.post(f"{BASE}/auth/login", json={"email": email, "password": password}, timeout=10)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass
    # fallback to oauth token endpoint
    try:
        r = session.post(f"{BASE}/auth/token", data={"username": email, "password": password}, timeout=10)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass
    return None


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--project", "-p", help="Project ID")
    p.add_argument("--token", "-t", help="Bearer token (optional)")
    args = p.parse_args()

    project = args.project or os.environ.get("SC_PROJECT_ID")
    token = args.token

    session = requests.Session()
    if not token:
        token = get_token(session)
        if not token:
            print("No token available. Set SC_EMAIL/SC_PASSWORD or pass --token.")
            sys.exit(1)

    if not project:
        print("Specify project id with --project or SC_PROJECT_ID environment variable")
        sys.exit(1)

    ws_url = f"{WS_ROOT}/api/v1/ws/{project}?token={token}"
    print("Connecting to:", ws_url)
    try:
        ws = create_connection(ws_url)
    except Exception as exc:
        print("Failed to connect to websocket:", exc)
        sys.exit(1)

    try:
        while True:
            msg = ws.recv()
            if not msg:
                break
            print(msg)
    except KeyboardInterrupt:
        print("Interrupted, closing")
    finally:
        try:
            ws.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
