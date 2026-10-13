<!-- Qwalora Ranger - lab scaffold -->
<div align="center">

# Qwalora Ranger · Lab

**Exploit it. Detect it. Patch it. Prove it.**

A self-contained, hardened cyber range you spin up with one command. You attack
a deliberately vulnerable target, catch yourself doing it, close the hole, and a
machine checks your work - pass or fail, no human grader, no server to run.

`safe by design` · `one-click` · `graded in CI` · `verifiable badges`

</div>

---

## Quick start

> Requires Docker (Desktop or Engine + Compose v2) and Python 3.11+.
> Grading alone (`check` / `status`) needs only Python.

```bash
# 1. Use this template -> create your own repo -> clone it
git clone https://github.com/<you>/qwalora-ranger-lab && cd qwalora-ranger-lab

# 2. Preflight
./qrange doctor

# 3. Bring up board 2 (loopback only) and attack it
./qrange up board2
./qrange exploit board2

# 4. Write your detection + patch, then grade yourself
./qrange check board2        # -> score x/100
./qrange status              # -> whole-program view, writes evidence/PROGRESS.md
```

Open a pull request on your fork and the autograder re-runs the same checks and
posts the result. That is the entire submission flow.

## How it works (and why there is no server)

```
  you (local)                         GitHub Actions (ephemeral)        program
  ──────────────                      ──────────────────────────        ───────
  ./qrange up      docker, loopback   validate.yml  grade each board     cohort-sync.yml
  ./qrange exploit     only           (no server, CI is the compute)     re-measure + Ed25519 sign
  edit detection                      comment pass/fail on the PR        -> verifiable badge
  edit patch          ▲                                                        │
  ./qrange check ─────┘ same checker runs here and in CI ────────────────► dossier verifies
```

- **You run the lab locally.** Everything Docker-related happens on your machine,
  bound to `127.0.0.1`. We host nothing.
- **Grading is deterministic.** The attack is a recorded fixture; the patch is
  proven by re-running the exploit against *your* code. Same result every time,
  on your laptop and in CI.
- **CI is the only compute.** `validate.yml` grades every push/PR. No persistent
  infrastructure, nothing to pay for, nothing to keep patched.
- **Badges are signed, not claimed.** The program re-measures from scratch and
  signs the result with an Ed25519 key. The public dossier verifies that
  signature in the browser, so a badge cannot be forged.

## What is in the box

| Path | What it is |
|---|---|
| `qrange` | the one-click CLI (`up`, `down`, `exploit`, `check`, `status`, `pack`, `pin`, `doctor`) |
| `docker-compose.yml` | the hardened range: vulnerable target, attacker, Suricata, Wazuh, Grafana |
| `boards/` | board manifests - each defines the checks that grade it |
| `lab/targets/` | the deliberately vulnerable targets (the things you exploit) |
| `lab/attacker/toolbox/` | exploit harnesses (also used headless by the grader) |
| `detections/` | where your Sigma / Suricata rules go, plus shipped references |
| `evidence/` | your proof artifacts; `PROGRESS.md` and the signed `attestation.json` land here |
| `scripts/` | the autograder (`validate.py`), progress scanner, signer, image pinner |
| `.github/workflows/` | `validate` (per-PR autograder) and `cohort-sync` (signed sign-off) |
| `brand/tokens.css` | the single source of brand truth, mirrored from the site |

## Offline / air-gapped

```bash
./qrange pin     # resolve image digests for reproducible, verifiable builds
./qrange pack    # -> qwalora-ranger-offline.zip (images + repo, no registry needed)
```

## Boards

| Board | Focus | ATT&CK |
|---|---|---|
| `board2` | Broken Object Level Authorization (BOLA / IDOR) | T1190 |
| _more_ | added as weeks unlock; the threat feed on the site maps current KEV entries to boards | |

---

Part of **Qwalora Ranger** · [ranger.qwalora.com](https://ranger.qwalora.com) ·
see [`SECURITY.md`](SECURITY.md) for the containment model.
