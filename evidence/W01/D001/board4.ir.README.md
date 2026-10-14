# Incident response - board4

Respond to the incident in `lab/boards/board4/soc/telemetry.jsonl`.

1. CONTAIN: patch the target so re-running the attack fails.
2. RECOVER: keep the service healthy.
3. RECONSTRUCT: submit `board4.ir.json` here:

    {"verdict":"incident","flagged":["<eid>",...],"scope":{"accounts":[...],"objects":[...],"techniques":[...],"source_ips":[...]}}
