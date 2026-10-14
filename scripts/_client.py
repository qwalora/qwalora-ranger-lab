"""Shared client for talking to the Qwalora Ranger portal.

Reads your identity from the environment (set as GitHub Actions secrets, or
export them locally):

    QWALORA_HANDLE   your GitHub handle
    QWALORA_TOKEN    your submission token (from your portal /me page)
    QWALORA_PORTAL   optional, defaults to https://portal.qwalora.com
"""
import json
import os
import urllib.error
import urllib.request

PORTAL = os.environ.get("QWALORA_PORTAL", "https://portal.qwalora.com").rstrip("/")


def _creds():
    handle = os.environ.get("QWALORA_HANDLE")
    token = os.environ.get("QWALORA_TOKEN")
    if not handle or not token:
        raise SystemExit("Set QWALORA_HANDLE and QWALORA_TOKEN (GitHub Actions secrets, "
                         "or export them). Get your token from your portal /me page.")
    return handle, token


def post(path, body):
    handle, token = _creds()
    body = dict(body or {})
    body.setdefault("handle", handle)
    req = urllib.request.Request(
        PORTAL + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "X-Candidate-Token": token},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except ValueError:
            return e.code, {"error": "http %d" % e.code}
