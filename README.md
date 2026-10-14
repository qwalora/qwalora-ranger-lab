# Qwalora Ranger - Cohort 2026-A lab

> These targets are **deliberately vulnerable**. Run them only on loopback,
> never expose them to a network you care about. This whole repo is hostile by
> design; that is the point.

This cohort has 6 boards. Each board is one scenario you work from
four role perspectives. Your work is graded **answer-free and program-side**:
the program re-measures your repo and signs the result, so nothing here contains
the answers, and editing your own status changes nothing.

| Board | Class | Title |
|---|---|---|
| board1 | bola | Broken Object Level Authorization |
| board2 | bola | Broken Object Level Authorization |
| board3 | ssrf | Server-Side Request Forgery |
| board4 | ssrf | Server-Side Request Forgery |
| board5 | massassign | Mass Assignment Privilege Escalation |
| board6 | massassign | Mass Assignment Privilege Escalation |

## The four roles, per board

All targets are stdlib Python 3; no Docker required. Replace `boardN` below.

**Red Teamer - exploit it**
```
python3 lab/boards/boardN/targets/web-api/app.py &        # starts on PORT (default 8080)
TARGET=http://127.0.0.1:8080 python3 lab/boards/boardN/attacker/exploit_*.py
```
Capture the leaked secret and write your proof to
`evidence/W01/D001/boardN.exploit.json` (see that board's README).

**Detection Engineer - catch it**
Author a Sigma rule from the stub `detections/sigma/boardN-*.yml.stub` (save it
without the `.stub`). It must fire on `fixtures/boardN/access.log` and stay
silent on `fixtures/boardN/access-benign.log`.

**SOC Analyst - triage it**
Analyse `lab/boards/boardN/soc/telemetry.jsonl` (unlabeled). Identify the
malicious events, the attacker, and the incident scope, and submit
`evidence/W01/D001/boardN.triage.json` (format in the triage README).

**Incident Responder - respond to it**
Contain (patch the target so the exploit fails), eradicate (remove the planted
backdoor so `attacker/persistence_probe.py` reports ERADICATED), recover (health
stays green), and reconstruct the incident in `evidence/W01/D001/boardN.ir.json`,
including the attacker source IP.

## Submitting

Open one pull request per day on a `day/Dxxx` branch. The program grades your
repo at cohort sync and publishes a signed result; verify it yourself on the
program's public proof page.
