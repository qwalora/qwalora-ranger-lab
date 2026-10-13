#!/usr/bin/env python3
"""
Qwalora Ranger - board2 target: Orders API

This service is DELIBERATELY VULNERABLE. It is the thing you exploit, detect,
and then patch. It has one planted flaw (BOLA / IDOR): the order lookup returns
any order by id without checking that the caller owns it.

Design notes for the range:
  - stdlib only  -> tiny image, no dependency CVEs of its own, fast spin-up
  - deterministic data -> CI can exploit + verify patch the same way every time
  - the fix lives in ONE clearly marked block (search: PATCH HERE)
  - access.log is JSON lines so the SOC side (Suricata/Wazuh/Sigma) has signal

Never expose this beyond the lab's loopback bind. It is hostile on purpose.
"""
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- seed data -------------------------------------------------------------
# token -> user.  In a real app these would be signed sessions; here they are
# fixed so the exercise is reproducible.
TOKENS = {
    "alice-token-7b2f": "alice",
    "mallory-token-9c1a": "mallory",
}

# order id -> record.  Note order 2001 belongs to mallory and holds the
# sensitive field the exploit is meant to reach.
ORDERS = {
    "1001": {"owner": "alice",   "item": "Field kit",      "total": "42.00"},
    "1002": {"owner": "alice",   "item": "Spare battery",  "total": "18.50"},
    "2001": {"owner": "mallory", "item": "Signed console",
             "total": "0.00", "secret": "QW-BOLA-PROOF-2001"},
}

ACCESS_LOG = os.environ.get("QW_ACCESS_LOG", "/tmp/access.log")


def log(event):
    event["ts"] = datetime.now(timezone.utc).isoformat()
    line = json.dumps(event, separators=(",", ":"))
    try:
        with open(ACCESS_LOG, "a") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
    # also to stdout so `docker logs` / CI can see it
    print(line, flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "qw-orders/1.0"

    def _json(self, code, body):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _user(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return TOKENS.get(auth[7:].strip())
        return None

    def log_message(self, *args):
        pass  # we do our own structured logging

    def do_GET(self):
        if self.path == "/healthz":
            return self._json(200, {"status": "ok"})

        if self.path.startswith("/api/orders/"):
            order_id = self.path.rsplit("/", 1)[-1]
            user = self._user()
            if not user:
                log({"evt": "auth_fail", "path": self.path})
                return self._json(401, {"error": "unauthenticated"})

            order = ORDERS.get(order_id)
            if not order:
                return self._json(404, {"error": "not found"})

            # ============================ PATCH HERE ============================
            # VULNERABILITY (BOLA / IDOR): the caller's identity is never
            # compared against the order owner, so any authenticated user can
            # read any order by guessing/enumerating the id.
            #
            # To patch: require that the order belongs to the caller, e.g.
            #     if order["owner"] != user:
            #         log({"evt":"bola_blocked","user":user,"order":order_id})
            #         return self._json(403, {"error": "forbidden"})
            # ====================================================================
            cross = order["owner"] != user
            log({"evt": "order_read", "user": user, "order": order_id,
                 "owner": order["owner"], "cross_tenant": cross})
            return self._json(200, order)

        return self._json(404, {"error": "no such route"})


def main():
    port = int(os.environ.get("PORT", "8080"))
    open(ACCESS_LOG, "a").close()
    log({"evt": "boot", "scenario": os.environ.get("QW_SCENARIO", "board2")})
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"qw-orders listening on :{port}", file=sys.stderr, flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
