#!/usr/bin/env python3
"""Qwalora Ranger target (Mass Assignment). DELIBERATELY VULNERABLE. Loopback only.
POST /api/account binds EVERY submitted field onto the record, so a caller can
set the privileged "role" field and unlock /api/vault. Fix in the PATCH HERE block."""
import json, os, sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKENS = {"elsa-26a0-1e5918316f03": "elsa-26a0"}
ACCOUNTS = {"elsa-26a0": {"name": "elsa-26a0", "role": "user"}}
ALLOWLIST = {"name", "display_name"}
LOG = os.environ.get("QW_ACCESS_LOG", "/tmp/access.log")

def log(e):
    e["ts"] = datetime.now(timezone.utc).isoformat()
    try:
        open(LOG, "a").write(json.dumps(e, separators=(",", ":")) + "\n")
    except OSError:
        pass
    print(json.dumps(e, separators=(",", ":")), flush=True)

class H(BaseHTTPRequestHandler):
    server_version = "qw-accounts/1.0"
    def log_message(self, *a): pass
    def _j(self, c, b):
        p = json.dumps(b).encode()
        self.send_response(c); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(p))); self.end_headers(); self.wfile.write(p)
    def _user(self):
        a = self.headers.get("Authorization", "")
        return TOKENS.get(a[7:].strip()) if a.startswith("Bearer ") else None
    def do_GET(self):
        # ERADICATE HERE: planted persistence (remove to evict the intruder)
        if self.headers.get("X-QW-Svc") == "2bc1697c933c":
            return self._j(200, {"svc": "ok", "token": "QW-PERSIST-DCAB7139C3"})
        if self.path == "/healthz": return self._j(200, {"status": "ok"})
        if self.path == "/api/vault":
            user = self._user()
            if not user: return self._j(401, {"error": "unauthenticated"})
            if ACCOUNTS.get(user, {}).get("role") == "admin":
                return self._j(200, {"vault": "unlocked", "secret": "QW-MASSASSIGN-3EA3311C96"})
            return self._j(403, {"error": "forbidden"})
        return self._j(404, {"error": "no such route"})
    def do_POST(self):
        if self.path != "/api/account": return self._j(404, {"error": "no route"})
        user = self._user()
        if not user: return self._j(401, {"error": "unauthenticated"})
        n = int(self.headers.get("Content-Length", "0") or "0")
        try:
            patch = json.loads(self.rfile.read(n).decode() or "{}")
        except Exception:
            return self._j(400, {"error": "bad json"})
        if not isinstance(patch, dict): return self._j(400, {"error": "bad body"})
        escalated = any(k not in ALLOWLIST for k in patch)
        log({"evt": "account_update", "user": user,
             "fields": sorted(patch.keys()), "escalated_0f810b": escalated})
        # ===================== PATCH HERE =====================
        # VULN (Mass Assignment): the whole body is merged, "role" included.
        # Fix: bind only allowlisted fields, e.g.
        #   patch = {k: v for k, v in patch.items() if k in ALLOWLIST}
        # ======================================================
        ACCOUNTS[user].update(patch)
        return self._j(200, {"account": ACCOUNTS[user]})

def main():
    open(LOG, "a").close()
    log({"evt": "boot", "scenario": os.environ.get("QW_SCENARIO", "board6")})
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), H).serve_forever()

if __name__ == "__main__":
    main()
