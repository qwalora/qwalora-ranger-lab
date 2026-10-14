#!/usr/bin/env python3
"""Qwalora Ranger target (BOLA). DELIBERATELY VULNERABLE. Loopback only.
The order lookup never checks ownership: any authenticated caller can read any
order by id. Fix inside the PATCH HERE block."""
import json, os, sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKENS = {"juno-5a26-89a26e31b3b2": "juno-5a26", "tariq-ee9d-e5dfd18decc8": "tariq-ee9d"}
ORDERS = {
    "4135": {"owner": "juno-5a26", "item": "Spare battery", "total": "42.00"},
    "3834": {"owner": "tariq-ee9d", "item": "Cipher dongle",
                  "total": "0.00", "secret": "QW-BOLA-6BE96D5BCF"},
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
        if self.headers.get("X-QW-Svc") == "da38b54ffaa9":
            return self._j(200, {"svc": "ok", "token": "QW-PERSIST-8ED73CCBA4"})
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
                 "owner": o["owner"], "cross_tenant_940205": o["owner"] != user})
            return self._j(200, o)
        return self._j(404, {"error": "no such route"})

def main():
    open(LOG, "a").close()
    log({"evt": "boot", "scenario": os.environ.get("QW_SCENARIO", "board2")})
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), H).serve_forever()

if __name__ == "__main__":
    main()
