# Board 5 — Raider (Red Teamer)

You have defended long enough. Now you attack. Board 5 is a live **Game of
Active Directory** range, isolated to you, reached over WireGuard. You compromise
`sevenkingdoms.local` end to end and prove each step by capturing its flag.

This is the first board with no dataset to download and no analysis to write up
for the objective. You are on a real network. Proof is a **captured flag**: a
`QR5{...}` token planted where only completing the objective can reach it. Each
flag is **seeded to you**, so it is unique to your range, cannot be guessed, and
is worthless to anyone else.

## Getting on the range

1. On the portal `/me` page, **Start lab**. The range provisions for you (it may
   queue briefly for a slot). When it shows Deployed, **Download WireGuard** and
   bring the tunnel up. Everything in the range is reachable only through that
   tunnel; nothing is exposed to the internet.
2. `pip install pyyaml && python scripts/fetch.py` writes
   `boards/board5/objectives.json` (your mission brief: objectives, targets,
   points) and scaffolds `boards/board5/flags.yml`.

## The objectives

Nine objectives, 100 points, following the GOAD kill chain: enumerate the
domain, land a foothold, AS-REP roast, Kerberoast a service account, move
laterally to a server, dump credentials, abuse a dangerous ACL, become Domain
Admin, and DCSync the krbtgt. `objectives.json` names the specific targets
seeded to your range (which service account is roastable, which server to pivot
to). Bring your own tooling; this is your tradecraft.

## Submitting

Paste each captured flag next to its objective id in `flags.yml`, write your
`summary` (the attack path from foothold to DA), then commit and push. The
grader checks each flag against your range's planted secret and prints which
objectives are captured, never the flag you are missing.

Rules of engagement: attack **only your own range**. Scanning or attacking any
other host, the portal included, is an immediate washout, that is the one line
you do not cross in this program.

## Clearing the board

Points-weighted: you need **95%** (so you can miss at most the 5-point recon
flag) plus an approved report, to clear the board and earn the **Raider** badge.
The report is your professional deliverable: the attack narrative, the evidence,
and the remediation you would hand a client.
