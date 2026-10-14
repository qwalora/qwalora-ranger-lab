"""Fetch your seeded material for the board you are on, and scaffold the file
you fill in. Run:  python scripts/fetch.py

Boards differ by kind:
  triage    (boards 1-2): writes boards/board<N>/alerts.json (your dataset) and
            a boards/board<N>/triage.yml skeleton (one row per event).
  detection (board 3):    writes boards/board<N>/threats.json + baseline.json
            (your detection requirements) and a boards/board<N>/rules.yml
            starter you author your Sigma-style rules in.
Your work files are never overwritten once they exist.
"""
import json
import os

from _client import post

code, d = post("/labs/dataset", {})
if code != 200:
    raise SystemExit("Could not fetch dataset: %s" % d.get("error", code))

board = d["board"]
kind = d.get("kind", "triage")
ds = d["dataset"]
outdir = "boards/board%d" % board
os.makedirs(outdir, exist_ok=True)


def _write_json(name, obj):
    with open(os.path.join(outdir, name), "w") as f:
        json.dump(obj, f, indent=2)


if kind == "ir":
    _write_json("evidence.json", ds)
    ir = os.path.join(outdir, "ir.yml")
    n_ev = len(ds.get("alerts", []))
    if os.path.exists(ir):
        print("Kept existing %s (not overwriting your work). Evidence refreshed." % ir)
    else:
        lines = [
            "# Board %d incident report. The breach already happened; evidence.json" % board,
            "# holds %d forensic events across the estate, most of them noise. Scope" % n_ev,
            "# the compromise and reconstruct what happened. Reference events by id.",
            "patient_zero:            # the host where the intrusion began, e.g. WKS-0471",
            "initial_access:          # MITRE ATT&CK id of the entry vector, e.g. T1566.001",
            "affected_hosts: []       # every host the adversary touched (list)",
            "affected_accounts: []    # every account they compromised, e.g. corp\\\\m.okafor",
            "timeline: []             # incident event ids in CHRONOLOGICAL order",
            "persistence: []          # event id(s) that establish persistence to remove",
            'summary: ""              # the incident, start to finish',
        ]
        with open(ir, "w") as f:
            f.write("\n".join(lines) + "\n")
        print("Wrote %s and %s/evidence.json for board %d (%d events)."
              % (ir, outdir, board, n_ev))
    print("Scope it, build the timeline, then commit and push to be graded.")
    raise SystemExit(0)

if kind == "detection":
    _write_json("threats.json", ds.get("threats", []))
    _write_json("baseline.json", ds.get("baseline", []))
    fields = ", ".join(ds.get("detectable_fields", []))
    rules = os.path.join(outdir, "rules.yml")
    if os.path.exists(rules):
        print("Kept existing %s (not overwriting your work). Requirements refreshed." % rules)
    else:
        lines = [
            "# Board %d detection rules. Author one or more rules that catch the" % board,
            "# behaviors in threats.json and stay quiet on baseline.json. You are",
            "# graded on UNSEEN variants of the same techniques, so key on the",
            "# invariant tradecraft (image + command tokens), not the exact sample.",
            "#",
            "# Detectable fields: %s" % fields,
            "# Modifiers: field|contains, field|startswith, field|endswith; add |all",
            "#   to require every value (default is any). A bare field is equality.",
            "# condition: selection names with and/or/not and parentheses, or",
            "#   'all of them' / 'any of them' / 'N of them'.",
            "rules:",
            "  - name: encoded_powershell",
            "    technique: T1059.001",
            "    detection:",
            "      sel:",
            "        image: powershell.exe",
            "        command|contains|all:",
            "          - \"-enc\"",
            "          - \"-w hidden\"",
            "      condition: sel",
            "  # add a rule per technique in threats.json ...",
        ]
        with open(rules, "w") as f:
            f.write("\n".join(lines) + "\n")
        print("Wrote %s, %s/threats.json (%d) and %s/baseline.json (%d)."
              % (rules, outdir, len(ds.get("threats", [])), outdir, len(ds.get("baseline", []))))
    print("Write your rules, then commit and push to be graded on the holdout.")
    raise SystemExit(0)

# triage kind (boards 1-2)
_write_json("alerts.json", ds)
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
