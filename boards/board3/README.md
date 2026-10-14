# Board 3 — Warden (Detection Engineer)

You have triaged alerts and hunted quiet intrusions. Now you build the thing
that catches them for everyone: detections. You are given the adversary's
tradecraft and must write rules that fire on it reliably and never cry wolf on
normal business.

Your requirements are **seeded to you**, and you are graded on an **unseen
holdout**: fresh variants of the same techniques (different hosts, users,
payload blobs, C2 domains) plus a fresh benign baseline. A rule that keys on the
invariant tradecraft generalizes and scores; a rule overfit to the exact sample
string catches nothing on the holdout. This is the whole discipline: write
detections that survive contact with a real environment.

## What you get

`scripts/fetch.py` writes three files into `boards/board3/`:

- `threats.json` — one labeled malicious sample per technique (the behaviors you
  must detect, with their MITRE ATT&CK ids). This is your intel.
- `baseline.json` — benign activity your rules must stay quiet on. Read it
  closely: some entries are **near-misses** (a legitimate `certutil -hashfile`,
  a normal `schtasks /query`, an admin `net use`). A lazy rule that keys only on
  the process name will false-positive on these and lose precision.
- `rules.yml` — a starter you fill in with your detections.

Events expose these fields, and your rules may match only on these:
`event_type`, `host`, `user`, `image`, `parent`, `command`, `dest`, `domain`.
(`id` and `timestamp` are deliberately not matchable, so you cannot overfit to a
unique event.)

## The rule format (a safe Sigma subset)

```yaml
rules:
  - name: lsass_comsvcs_minidump
    technique: T1003.001
    detection:
      sel:
        command|contains|all:      # every value must be present (AND)
          - comsvcs.dll
          - MiniDump
      condition: sel
  - name: ingress_certutil
    technique: T1105
    detection:
      sel:
        image: certutil.exe        # bare field = case-insensitive equality
        command|contains|all: ["-urlcache", "-split"]
      condition: sel
```

- Modifiers on a field: `|contains`, `|startswith`, `|endswith`. Add `|all` to
  require every value; without it a list means any (OR). A bare field is
  equality.
- Across keys in one selection the logic is AND. For OR across patterns, use
  several selections and a `condition` like `sel_a or sel_b`.
- `condition` supports selection names with `and` / `or` / `not` and
  parentheses, plus `all of them`, `any of them`, `N of them`.
- No regex (by design, to keep grading safe and fast).

## The loop

```
pip install pyyaml
python scripts/fetch.py            # pulls threats.json, baseline.json, rules.yml
# ... write a rule per technique, keyed on the durable tradecraft ...
git commit -am "board 3 detections" && git push
```

## How you're scored

Your rules run against the holdout. Your score is the F1 of:

- **macro-recall** — the mean per-technique detection rate, so you must cover
  *every* technique; ignoring one caps your score hard.
- **precision** — benign events your rules must not fire on. The near-miss
  decoys are where lazy rules bleed precision.

CI prints, per rule, how many malicious and benign holdout events it fired on,
so you can tighten a noisy rule or fix a dead one. A rule that fires on nothing
is overfit or points at the wrong field. You need **95%** plus an approved
report to clear the board and earn the **Warden** badge.
