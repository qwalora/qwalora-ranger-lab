# Board 2 — Tracker (Threat Hunter)

No alert fired. That is the point. The `corp.local` estate looks quiet, but an
intruder is already inside and living off the land: signed binaries, valid
accounts, nothing that trips a signature. You are promoted from triaging a queue
to **hunting** the intrusion out of the noise.

Your dataset is **seeded to you**. Your estate, the compromised account, the
patient-zero host, the lateral target and the C2 differ from every other
ranger's, so there is no answer to copy. Grading is server-side and answer-free.

## What you get

`boards/board2/alerts.json` is raw telemetry: 45-60 events, each with an `id`,
`timestamp`, `host`, `user`, `event_type` (`process` / `auth` / `network` /
`dns`) and a `detail` line. Most are normal business. A 7-10 step kill chain is
woven through them: initial execution, ingress, discovery, credential access,
lateral movement, persistence, command-and-control, exfiltration. Read the
`detail`; the tradecraft is visible if you know what normal looks like.

## What to do

1. Secrets set once (same as board 1): `QWALORA_HANDLE` and `QWALORA_TOKEN`
   (from your portal `/me` page) as Actions secrets.
2. Pull your telemetry and scaffold your answer file:
   ```
   pip install pyyaml
   python scripts/fetch.py
   ```
   This writes `boards/board2/alerts.json` and a `boards/board2/triage.yml` with
   one row per event.
3. **Hunting, not triage.** You do not have to classify all 50+ events. Fill in
   a row **only** for an event you assess as part of the intrusion
   (`verdict: true_positive`). Every row you leave blank is read as benign. So a
   clean hunt is a short answer file: just your confirmed findings. For each
   finding set:
   - `verdict`: `true_positive`
   - `severity`: `low` / `medium` / `high` / `critical` (your call on the find)
   - `attack_technique`: the MITRE ATT&CK id, e.g. `T1003.001`
   - `iocs`: what you'd pivot on, e.g. the host, the account like `corp\okafor`,
     and the C2 domain for network/DNS events
4. Write a short `summary`: the story of the intrusion, start to finish.
5. Commit and push. The grader runs and prints your score. Re-push freely; your
   best score counts.

## How you're scored

This is a detection problem, scored on both halves of a good hunt:

- **Find the whole chain** (recall) and **don't chase ghosts** (precision). The
  objective is an F1 over the real intrusion set, so missing steps *and*
  flagging benign events both cost you. Flagging everything "to be safe" fails,
  and so does flagging nothing.
- On the events you correctly flag: **technique** correctness and **IOC**
  overlap add the rest.

You need **95%** on the objective, plus an approved written report, to clear the
board and earn the **Tracker** badge. Feedback tells you which of your calls are
off, never the answer. Hunt deliberately: a precise, complete chain beats a pile
of guesses.
