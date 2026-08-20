from __future__ import annotations

import json
import os
import sys
from urllib import error, request


BASE_URL = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.getenv("ZEMAZAP_SMOKE_BASE_URL", "http://127.0.0.1:3000")
).rstrip("/")
CHECKS = [
    ("frontend health", "/api/health", {200}),
    ("home", "/", {200}),
    ("catalog", "/catalog", {200}),
    ("request", "/request", {200}),
    ("contacts", "/contacts", {200}),
    ("admin handoff", "/admin", {200, 301, 302, 307, 308}),
    ("not found", "/definitely-not-a-real-zemazap-route", {404}),
]


def check(name: str, path: str, expected: set[int]) -> dict:
    url = f"{BASE_URL}{path}"
    try:
        response = request.urlopen(url, timeout=15)
        status = response.status
    except error.HTTPError as exc:
        status = exc.code
    if status not in expected:
        raise RuntimeError(f"{name}: expected {sorted(expected)}, got {status} ({url})")
    return {"name": name, "status": status, "url": url}


try:
    results = [check(name, path, expected) for name, path, expected in CHECKS]
except Exception as exc:
    print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False))
    sys.exit(1)

print(json.dumps({"status": "ok", "checks": results}, ensure_ascii=False))
