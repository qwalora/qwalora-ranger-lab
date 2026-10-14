#!/usr/bin/env python3
"""Qwalora Ranger target (SSRF). DELIBERATELY VULNERABLE. Loopback only.
/api/fetch?url= retrieves any URL server-side with no destination policy, so it
can be aimed at the internal metadata route. Fix inside the PATCH HERE block."""
import json, os, sys, urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

LOG = os.environ.get("QW_ACCESS_LOG", "/tmp/access.log")

def log(e):
    e["ts"] = datetime.now(timezone.utc).isoformat()
    try:
        open(LOG, "a").write(json.dumps(e, separators=(",", ":")) + "\n")
    except OSError:
        pass
    print(json.dumps(e, separators=(",", ":")), flush=True)

def is_internal(url):
    host = (urlsplit(url).hostname or "").lower()
    path = urlsplit(url).path
    return (host in ("127.0.0.1", "localhost", "::1", "0.0.0.0")
            or host.startswith("169.254.") or host.startswith("10.")
            or host.startswith("192.168.") or path.startswith("/internal"))

class H(BaseHTTPRequestHandler):
    server_version = "qw-preview/1.0"
    def log_message(self, *a): pass
    def _j(self, c, b):
        p = json.dumps(b).encode()
        self.send_response(c); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(p))); self.end_headers(); self.wfile.write(p)
    def do_GET(self):
        # ERADICATE HERE: planted persistence (remove to evict the intruder)
        if self.headers.get("X-QW-Svc") == "1e02b9733fa5":
            return self._j(200, {"svc": "ok", "token": "QW-PERSIST-04BE7BA2A1"})
        sp = urlsplit(self.path)
        if sp.path == "/healthz": return self._j(200, {"status": "ok"})
        if sp.path == "/internal/meta":
            # internal metadata service; NEVER meant to be reachable by callers
            return self._j(200, {"service": "board3-meta", "token": "QW-SSRF-38BC603380"})
        if sp.path == "/api/fetch":
            url = (parse_qs(sp.query).get("url", [""])[0]).strip()
            if not url: return self._j(400, {"error": "url required"})
            internal = is_internal(url)
            # ===================== PATCH HERE =====================
            # VULN (SSRF): any destination is fetched, internal included.
            # Fix:
            #   if internal:
            #       log({"evt":"fetch","url":url,"internal_target_5f4fa3":True,"blocked":True})
            #       return self._j(403, {"error":"destination not allowed"})
            # ======================================================
            log({"evt": "fetch", "url": url, "internal_target_5f4fa3": internal})
            try:
                with urllib.request.urlopen(url, timeout=3) as r:
                    body = r.read(65536).decode("utf-8", "replace")
            except Exception as e:
                return self._j(502, {"error": "fetch failed", "detail": str(e)[:80]})
            return self._j(200, {"fetched": body})
        return self._j(404, {"error": "no such route"})

def main():
    open(LOG, "a").close()
    log({"evt": "boot", "scenario": os.environ.get("QW_SCENARIO", "board3")})
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), H).serve_forever()

if __name__ == "__main__":
    main()
