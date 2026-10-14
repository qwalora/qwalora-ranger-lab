"""Submit your triage for the board you are on and print your score.

Runs automatically in CI on every push, and locally with:
    python scripts/submit.py

Grading is server-side and answer-free: the portal re-derives the answer key
from your seed and scores your submission. You never see the key; feedback is
correctness flags only. You need 95% on the objective AND an approved report to
clear the board.
"""
import os
import sys

import yaml  # pip install pyyaml

from _client import post

# Which board are you on? Ask the portal.
code, d = post("/labs/dataset", {})
if code != 200:
    raise SystemExit("Could not reach the portal: %s" % d.get("error", code))
board = d["board"]

path = "boards/board%d/triage.yml" % board
if not os.path.exists(path):
    raise SystemExit("No %s yet. Run: python scripts/fetch.py" % path)

with open(path) as f:
    submission = yaml.safe_load(f) or {}

code, res = post("/grade/submit", {"submission": submission})
if code != 200:
    raise SystemExit("Grader error (%s): %s" % (code, res.get("error", "unknown")))

score = res.get("score", 0.0)
print("Board %d objective score: %.1f%%  (need %s)" % (board, score, "95%"))
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
