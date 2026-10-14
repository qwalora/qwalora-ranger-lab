"""Fetch your seeded dataset for the board you are on, and scaffold the answer
file. Run:  python scripts/fetch.py

Writes boards/board<N>/alerts.json (your dataset, no answers) and a
boards/board<N>/triage.yml skeleton for you to fill in.
"""
import json
import os

from _client import post

code, d = post("/labs/dataset", {})
if code != 200:
    raise SystemExit("Could not fetch dataset: %s" % d.get("error", code))

board = d["board"]
ds = d["dataset"]
outdir = "boards/board%d" % board
os.makedirs(outdir, exist_ok=True)

with open(os.path.join(outdir, "alerts.json"), "w") as f:
    json.dump(ds, f, indent=2)

triage = os.path.join(outdir, "triage.yml")
if os.path.exists(triage):
    print("Kept existing %s (not overwriting your work). Dataset refreshed." % triage)
else:
    lines = [
        "# Board %d triage. For each alert set:" % board,
        "#   verdict:          true_positive | false_positive",
        "#   severity:         low | medium | high | critical",
        "#   attack_technique: MITRE ATT&CK id (true positives only, e.g. T1110.003)",
        "#   iocs:             list of indicators (true positives only)",
        "alerts:",
    ]
    for a in ds["alerts"]:
        lines += ["  - id: %s" % a["id"],
                  "    verdict: ",
                  "    severity: ",
                  "    attack_technique: ",
                  "    iocs: []"]
    lines += ['summary: ""']
    with open(triage, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("Wrote %s and %s/alerts.json for board %d (%d alerts)."
          % (triage, outdir, board, len(ds["alerts"])))
print("Investigate, fill in the verdicts, then commit and push to be graded.")
