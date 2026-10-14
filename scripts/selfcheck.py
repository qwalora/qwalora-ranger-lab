#!/usr/bin/env python3
"""Template smoke-check (secret-free). Boots each board target on loopback,
confirms /healthz, and verifies each board ships its fixtures, detection stub,
and harnesses. This is TEMPLATE integrity only; authoritative, answer-free
grading happens program-side at cohort sync. No secrets or answers are read."""
import os, socket, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def _boots(app: Path) -> bool:
    port = _port()
    proc = subprocess.Popen([sys.executable, str(app)],
                            env=dict(os.environ, PORT=str(port), QW_ACCESS_LOG="/tmp/sc.log"),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if proc.poll() is not None:
                return False
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=1) as r:
                    if r.status == 200:
                        return True
            except Exception:
                time.sleep(0.1)
        return False
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def main():
    boards = sorted((ROOT / "lab" / "boards").glob("board*"))
    if not boards:
        print("no boards found"); return 1
    ok = True
    for b in boards:
        name = b.name
        app = b / "targets" / "web-api" / "app.py"
        checks = {
            "target boots": app.exists() and _boots(app),
            "attacker tools": any((b / "attacker").glob("*.py")),
            "telemetry corpus": (b / "soc" / "telemetry.jsonl").exists(),
            "fixtures": (ROOT / "fixtures" / name / "access.log").exists()
                        and (ROOT / "fixtures" / name / "access-benign.log").exists(),
            "detection stub": any((ROOT / "detections" / "sigma").glob(f"{name}-*.yml.stub")),
        }
        for label, good in checks.items():
            print(f"[{'ok' if good else 'XX'}] {name}: {label}")
            ok = ok and good
    print("SMOKE OK" if ok else "SMOKE FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
