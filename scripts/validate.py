#!/usr/bin/env python3
"""
Qwalora Ranger - board validator (the autograder).

Runs every check in a board manifest with zero manual steps and writes
evidence/_report.json. Each check is deterministic:
  * evidence_json   - the candidate committed a well-formed proof artifact
  * sigma_fires     - their detection catches the recorded attack, not benign
  * exploit_blocked - their patched target refuses the exploit

No server and no Docker are required: exploit_blocked launches the candidate's
own target code directly and re-runs the exploit against it. GitHub Actions is
the only compute; CI is ephemeral, so nothing persists.

Usage:
  python3 scripts/validate.py board2 [--repo-root .] [--json-only]
Exit code is 0 only when the board passes its threshold.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

# ANSI (brand) ---------------------------------------------------------------
ORANGE = "\033[38;5;208m"; PERI = "\033[38;5;99m"; GREEN = "\033[38;5;42m"
RED = "\033[38;5;203m"; DIM = "\033[2m"; BOLD = "\033[1m"; RST = "\033[0m"


def load_yaml(path):
    import yaml
    with open(path) as fh:
        return yaml.safe_load(fh)


# --- check implementations --------------------------------------------------

def check_evidence_json(chk, root):
    path = root / chk["path"]
    if not path.exists():
        return False, f"missing {chk['path']} (run the exploit, then save its JSON here)"
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return False, f"{chk['path']} is not valid JSON: {e}"
    for key, want in chk.get("expect", {}).items():
        if str(data.get(key)) != str(want):
            return False, f"{key!r} should be {want!r}, got {data.get(key)!r}"
    return True, "evidence present and well-formed"


def check_sigma_fires(chk, root):
    import sigma_runner
    rule = root / chk["rule"]
    if not rule.exists():
        return False, f"missing rule {chk['rule']}"
    try:
        hits = sigma_runner.run(str(rule), str(root / chk["events"]))
    except Exception as e:  # noqa: BLE001
        return False, f"rule failed to evaluate: {e}"
    if hits < chk.get("min_matches", 1):
        return False, f"rule matched {hits} attack event(s); need >= {chk.get('min_matches',1)}"
    benign = chk.get("benign_events")
    if benign:
        fp = sigma_runner.run(str(rule), str(root / benign))
        if fp > chk.get("max_false_positives", 0):
            return False, f"rule also flagged {fp} benign event(s); tighten it"
    return True, f"fires on the attack ({hits}), clean on benign traffic"


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def check_exploit_blocked(chk, root, board):
    app = (root / board["target"]["app"]).resolve()
    if not app.exists():
        return False, f"target app not found: {board['target']['app']}"
    port = _free_port()
    env = dict(os.environ, PORT=str(port), QW_ACCESS_LOG="/tmp/qw_validate.log")
    proc = subprocess.Popen(
        ["python3", str(app)], env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        health = board["target"].get("health", "/healthz")
        up = False
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}{health}", timeout=1) as r:
                    if r.status == 200:
                        up = True
                        break
            except Exception:  # noqa: BLE001
                time.sleep(0.1)
        if not up:
            return False, "target did not become healthy (did your patch break it?)"

        harness = (root / chk["harness"]).resolve()
        res = subprocess.run(
            ["python3", str(harness)],
            env=dict(env, TARGET=f"http://127.0.0.1:{port}"),
            capture_output=True, text=True, timeout=30,
        )
        want = chk.get("expect_exit", 3)
        if res.returncode == want:
            return True, "exploit is blocked by your patch"
        if res.returncode == 0:
            return False, "exploit still succeeds - the patch did not close BOLA"
        return False, f"harness exit {res.returncode} (expected {want}); {res.stderr.strip()[:120]}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


DISPATCH = {
    "evidence_json": lambda c, r, b: check_evidence_json(c, r),
    "sigma_fires": lambda c, r, b: check_sigma_fires(c, r),
    "exploit_blocked": lambda c, r, b: check_exploit_blocked(c, r, b),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--repo-root", default=str(ROOT))
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    manifest = root / "boards" / f"{args.board}.yml"
    if not manifest.exists():
        print(f"no such board: {args.board}", file=sys.stderr)
        return 2
    board = load_yaml(manifest)

    results = []
    earned = 0
    possible = 0
    for chk in board.get("checks", []):
        possible += chk.get("weight", 0)
        fn = DISPATCH.get(chk["kind"])
        if not fn:
            ok, msg = False, f"unknown check kind {chk['kind']}"
        else:
            try:
                ok, msg = fn(chk, root, board)
            except Exception as e:  # noqa: BLE001
                ok, msg = False, f"check error: {e}"
        if ok:
            earned += chk.get("weight", 0)
        results.append({"id": chk["id"], "desc": chk.get("desc", ""),
                        "weight": chk.get("weight", 0), "pass": ok, "detail": msg})

    score = round(100 * earned / possible) if possible else 0
    passed = score >= board.get("pass_threshold", 100)
    report = {
        "board": board["board"], "title": board.get("title", ""),
        "attack": board.get("attack", {}), "score": score,
        "earned": earned, "possible": possible, "passed": passed,
        "checks": results, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    report_path = root / "evidence" / "_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    if not args.json_only:
        bar = GREEN if passed else RED
        print(f"\n{ORANGE}Qwalora Ranger{RST} {DIM}/ autograder{RST}")
        print(f"{BOLD}{board['board']} - {board.get('title','')}{RST}  "
              f"{DIM}{board.get('attack',{}).get('id','')}{RST}\n")
        for r in results:
            mark = f"{GREEN}pass{RST}" if r["pass"] else f"{RED}fail{RST}"
            print(f"  [{mark}] {r['id']}  {DIM}({r['weight']} pts){RST}")
            print(f"         {r['detail']}")
        print(f"\n  {bar}{BOLD}score {score}/100  -  {'PASS' if passed else 'INCOMPLETE'}{RST}")
        print(f"  {DIM}report: evidence/_report.json{RST}\n")
    else:
        print(json.dumps(report))

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
