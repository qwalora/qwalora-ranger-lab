"""Submit your work for the board you are on and print your score.

Runs automatically in CI on every push, and locally with:
    python scripts/submit.py

Grading is server-side. For triage boards the portal re-derives the answer key
from your seed; for detection boards it runs your rules against an unseen
holdout. Either way you never see the key, feedback is correctness/validation
only, and you need 95% on the objective AND an approved report to clear a board.
"""
import os
import sys

import yaml  # pip install pyyaml

from _client import post

# Which board are you on, and what kind of exercise is it? Ask the portal.
code, d = post("/labs/dataset", {})
if code != 200:
    raise SystemExit("Could not reach the portal: %s" % d.get("error", code))
board = d["board"]
kind = d.get("kind", "triage")

fname = {"detection": "rules.yml", "ir": "ir.yml", "flags": "flags.yml"}.get(kind, "triage.yml")
path = "boards/board%d/%s" % (board, fname)
if not os.path.exists(path):
    raise SystemExit("No %s yet. Run: python scripts/fetch.py" % path)

with open(path) as f:
    submission = yaml.safe_load(f) or {}

code, res = post("/grade/submit", {"submission": submission})
if code != 200:
    raise SystemExit("Grader error (%s): %s" % (code, res.get("error", "unknown")))

score = res.get("score", 0.0)
print("Board %d objective score: %.1f%%  (need 95%%)" % (board, score))

rkind = res.get("kind") or kind
if rkind == "flags":
    fb = (res.get("per_alert") or [{}])[0]
    print("  objectives captured: %s | points: %s"
          % (fb.get("objectives_captured", "?"), fb.get("points", "?")))
    for o in fb.get("objectives", []):
        mark = "captured" if o.get("captured") else "open"
        print("    [%-8s] %-28s %s pts" % (mark, o.get("name"), o.get("points")))
elif rkind == "ir":
    fb = (res.get("per_alert") or [{}])[0]
    def _mark(ok):
        return "ok" if ok else "off"
    print("  patient zero: %s | initial access: %s"
          % (_mark(fb.get("patient_zero_correct")), _mark(fb.get("initial_access_correct"))))
    print("  affected hosts F1: %s | accounts F1: %s"
          % (fb.get("affected_hosts_f1", "?"), fb.get("affected_accounts_f1", "?")))
    print("  timeline membership F1: %s | order: %s | persistence F1: %s"
          % (fb.get("timeline_membership_f1", "?"), fb.get("timeline_order_score", "?"),
             fb.get("persistence_f1", "?")))
elif rkind == "detection":
    fb = (res.get("per_alert") or [{}])[0]
    print("  techniques covered: %s | validation false positives: %s"
          % (fb.get("techniques_covered", "?"), fb.get("validation_false_positives", "?")))
    print("  macro-recall: %s | precision: %s"
          % (fb.get("macro_recall", "?"), fb.get("precision", "?")))
    for r in fb.get("rules", []):
        flag = "  <- fires on benign, tighten it" if r.get("fired_benign") else ""
        if not r.get("fired_malicious") and not r.get("fired_benign"):
            flag = "  <- fires on nothing (overfit or wrong field)"
        print("    rule %-24s malicious=%s benign=%s%s"
              % (r.get("name"), r.get("fired_malicious"), r.get("fired_benign"), flag))
    for e in fb.get("rule_errors", []):
        print("    ERROR %s: %s" % (e.get("rule"), e.get("error")))
else:
    wrong = [a["id"] for a in res.get("per_alert", [])
             if not a.get("verdict_correct") or not a.get("severity_correct")
             or a.get("technique_correct") is False]
    if wrong:
        print("Review these alerts (verdict/severity/technique off): %s" % ", ".join(wrong))

print(res.get("note", ""))

if res.get("promoted"):
    print("Cleared the board. You have been promoted to board %d." % res.get("current_board"))
    sys.exit(0)
if res.get("passed"):
    print("Objective passed. Get your report approved to clear the board.")
    sys.exit(0)
# Below the bar: fail the check so the red X flags it, then try again.
sys.exit(1)
