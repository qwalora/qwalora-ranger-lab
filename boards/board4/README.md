# Board 4 — Reclaimer (Incident Responder)

The breach already happened. You are called in after the fact with a pile of
forensic evidence and one job: tell the organization what happened, how far it
spread, and what to rip out. This is the responder's discipline, scope,
timeline, root cause, remediation.

Your evidence is **seeded to you**: the incident, the hosts and accounts it
touched, and the entry vector all differ from every other ranger's. Grading is
server-side and answer-free, against the incident's ground truth.

## What you get

`scripts/fetch.py` writes `boards/board4/evidence.json`: a few dozen forensic
events across the estate (`id`, `timestamp`, `host`, `user`, `event_type`,
`detail`). Most are normal business. One coherent intrusion runs through them,
across more than one host, using more than one account. It also scaffolds
`boards/board4/ir.yml` for your findings.

## What to do

1. Secrets set once (same as the other boards): `QWALORA_HANDLE` and
   `QWALORA_TOKEN`.
2. `pip install pyyaml && python scripts/fetch.py`.
3. Work the evidence and fill in `ir.yml`, referencing events by `id`:
   - `patient_zero` — the host where the intrusion began.
   - `initial_access` — the MITRE ATT&CK id of the entry vector (e.g. a
     phishing attachment, valid-account abuse, or a public-app exploit).
   - `affected_hosts` — every host the adversary touched. Follow the lateral
     movement; do not stop at patient zero.
   - `affected_accounts` — every account they compromised, e.g.
     `corp\m.okafor`. Watch for privilege escalation to a service or admin
     account.
   - `timeline` — the incident event ids in **chronological order**. Correlate
     across hosts using the timestamps; this is the story of the attack.
   - `persistence` — the event id(s) that establish persistence (what must be
     removed so the adversary cannot return).
   - `summary` — the incident start to finish, in a few sentences.
4. Commit and push. The grader scores each section and prints where you are off.

## How you're scored

Weighted across the report: patient zero and initial-access vector (exact),
affected hosts and accounts (set overlap), the timeline (correct membership
**and** correct ordering), and the persistence you flagged. Feedback tells you
which sections are weak, never the answer. Scoping too narrow (missing a host,
an account, or the second half of the chain) is the most common way to fall
short. You need **95%** plus an approved report to clear the board and earn the
**Reclaimer** badge.
