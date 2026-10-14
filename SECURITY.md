# Security model

Qwalora Ranger is a verifiable training program. The security properties below
are what make a passing grade mean something, so they are enforced on the
portal, not left to this repo.

## Grading is server-side and answer-free

- Your dataset is **seeded to you**. The portal derives it from an immutable
  per-person seed, so your alerts, hosts, time window, and the intrusion itself
  differ from every other ranger's. There is no answer to copy, and sharing a
  solution does not transfer because your seed is different.
- The **answer key never leaves the portal.** `scripts/fetch.py` pulls only the
  dataset; the portal strips the key before it is sent. `scripts/submit.py`
  sends your analysis back, and the portal re-derives the key from your seed to
  score it. Nothing in this repo lets you or anyone else read the key, and
  nothing here grades you locally.
- Feedback is **correctness flags only** — which alerts are off, never the
  correct value. You cannot binary-search the key out of the grader.

## Identity

- Enrollment and the reviewer side are **GitHub-only** (OAuth), with a verified
  primary email, 2FA, and a minimum account age required. That is how the
  program knows a ranger is a real, distinct person and ties every submission to
  one identity.
- Your submission token (portal `/me` page) authenticates this repo's CI to the
  portal. Treat it like a password: it lives only in GitHub Actions secrets,
  never in committed files. Rotate it from `/me` if it leaks.

## What CI runs

- The grader does not execute arbitrary code. `scripts/submit.py` reads your
  `triage.yml`, posts it to the portal, and prints your score. It runs in
  GitHub's ephemeral, sandboxed runners, which are destroyed after the job.
- The portal only re-measures and scores the submitted analysis. No candidate
  input is executed on program infrastructure.

## Reporting

Found a way to read a key, score without doing the work, or submit as another
ranger? That is exactly what we want to hear about. Open a private report to the
program (or email security@qwalora.com) rather than a public issue.
