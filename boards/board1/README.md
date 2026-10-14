# Board 1 — Sentinel (SOC Analyst)

You are the first line. A stream of alerts has fired across the
`sevenkingdoms.local` estate. Some are a real intrusion; most are noise. Your
job is to triage every alert correctly.

This dataset is **seeded to you**. Your alerts, hosts, time window and the
intrusion itself differ from every other ranger's, so there is no answer to
copy. Grading is server-side and answer-free.

## What to do

1. Make sure your secrets are set (once): in this repo, Settings → Secrets and
   variables → Actions, add `QWALORA_HANDLE` (your GitHub handle) and
   `QWALORA_TOKEN` (from your portal `/me` page).
2. Pull your dataset and scaffold your answer file:
   ```
   pip install pyyaml
   QWALORA_HANDLE=you QWALORA_TOKEN=... python scripts/fetch.py
   ```
   This writes `boards/board1/alerts.json` (your alerts) and a
   `boards/board1/triage.yml` skeleton. You can also investigate the same alerts
   in your SIEM session from the portal.
3. For every alert in `triage.yml`, fill in:
   - `verdict`: `true_positive` or `false_positive`
   - `severity`: `low`, `medium`, `high`, or `critical`
   - `attack_technique`: the MITRE ATT&CK id (true positives only, e.g. `T1110.003`)
   - `iocs`: the indicators you'd pivot on (true positives only), e.g. the source
     host and the account like `winterfell\jon`
4. Write a short `summary` of what happened.
5. Commit and push. The grader runs automatically and prints your score in the
   Actions log. Re-push as many times as you like; your best score counts.

## How you're scored

Per alert: verdict (most weight), severity, technique (true positives), and IOC
overlap (true positives). You need **95%** on the objective, plus an approved
written report, to clear the board and earn the **Sentinel** badge.

Feedback tells you *which* alerts are off, never the correct answer. Read the
raw log on each alert: it contains the signal you need to classify it.
