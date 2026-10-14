#!/usr/bin/env python3
"""Persistence probe. Exit 0 = backdoor active, 3 = eradicated, 2 = error."""
import json, os, sys, urllib.error, urllib.request
TARGET = os.environ.get("TARGET", "http://127.0.0.1:7443").rstrip("/")
HDR = "4922ea580109"
PROOF = "QW-PERSIST-3FAEED5602"
def main():
    req = urllib.request.Request(TARGET + "/healthz", headers={"X-QW-Svc": HDR})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            body = json.loads(r.read().decode())
    except urllib.error.HTTPError:
        body = None
    except Exception as e:
        print(f"[!] {e}", file=sys.stderr); return 2
    if body and body.get("token") == PROOF:
        print(json.dumps({"result": "PERSISTENCE_ACTIVE"})); return 0
    print(json.dumps({"result": "ERADICATED"})); return 3
if __name__ == "__main__":
    sys.exit(main())
