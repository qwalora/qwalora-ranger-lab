#!/usr/bin/env python3
"""Qwalora Ranger target (BOLA). DELIBERATELY VULNERABLE. Loopback only.
The order lookup never checks ownership: any authenticated caller can read any
order by id. Fix inside the PATCH HERE block."""
import json, os, sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKENS = {"noah-12c0-1ab801ed5e34": "noah-12c0", "mei-5b9e-b2d82c7aeb1c": "mei-5b9e"}
ORDERS = {
    "7449": {"owner": "noah-12c0", "item": "Spare battery", "total": "42.00"},
    "3452": {"owner": "mei-5b9e", "item": "Comms headset",
                  "total": "0.00", "secret": "QW-BOLA-DF41C9289A"},
}
LOG = os.environ.get("QW_ACCESS_LOG", "/tmp/access.log")

def log(e):
    e["ts"] = datetime.now(timezone.utc).isoformat()
    try:
        open(LOG, "a").write(json.dumps(e, separators=(",", ":")) + "\n")
    except OSError:
        pass
    print(json.dumps(e, separators=(",", ":")), flush=True)

class H(BaseHTTPRequestHandler):
    server_version = "qw-orders/1.0"
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
        if self.headers.get("X-QW-Svc") == "4922ea580109":
            return self._j(200, {"svc": "ok", "token": "QW-PERSIST-3FAEED5602"})
        if self.path == "/healthz": return self._j(200, {"status": "ok"})
        if self.path.startswith("/api/orders/"):
            oid = self.path.rsplit("/", 1)[-1]
            user = self._user()
            if not user:
                log({"evt": "auth_fail", "path": self.path}); return self._j(401, {"error": "unauthenticated"})
            o = ORDERS.get(oid)
            if not o: return self._j(404, {"error": "not found"})
            # ===================== PATCH HERE =====================
            # VULN (BOLA/IDOR): caller identity is never compared to the owner.
            # Fix:
            #   if o["owner"] != user:
            #       log({"evt":"bola_blocked","user":user,"order":oid})
            #       return self._j(403, {"error":"forbidden"})
            # ======================================================
            log({"evt": "order_read", "user": user, "order": oid,
                 "owner": o["owner"], "cross_tenant_235e4a": o["owner"] != user})
            return self._j(200, o)
        return self._j(404, {"error": "no such route"})

def main():
    open(LOG, "a").close()
    log({"evt": "boot", "scenario": os.environ.get("QW_SCENARIO", "board1")})
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), H).serve_forever()

if __name__ == "__main__":
    main()
