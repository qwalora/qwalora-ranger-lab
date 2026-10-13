# Architecture

Three planes, one principle: **the program hosts nothing, and nothing the
candidate runs can leave the box.**

## 1. The range (candidate's machine)

`docker-compose.yml` brings up five services on two `internal: true` networks:

- **target-webapi** - the deliberately vulnerable app you exploit. Loopback bind
  `127.0.0.1:7443`. Non-root, read-only, seccomp-confined.
- **attacker** - offensive toolbox on the internal net (no egress). You `exec`
  in, or let the grader drive the harness headless.
- **suricata** - IDS sharing the target's network namespace (red traffic in).
- **wazuh** - single-node SIEM (host/app telemetry).
- **grafana** - dashboards, loopback bind `127.0.0.1:3000`, generated secret.

The candidate never needs all of it at once; `./qrange up <board>` starts only
what a board requires.

## 2. Grading (deterministic, runs anywhere)

`scripts/validate.py` reads a board manifest (`boards/<board>.yml`) and runs its
checks:

- `evidence_json` - a well-formed proof artifact was committed.
- `sigma_fires` - the candidate's rule matches the recorded attack fixture and
  **not** the benign fixture (guards against match-everything rules).
- `exploit_blocked` - the grader launches the candidate's patched target and
  re-runs the real exploit harness, expecting it to be refused.

Because the attack is a fixture and the patch is proven against the candidate's
own code, the score is identical on a laptop and in CI. No server, no Docker
required for grading itself.

## 3. Attestation (program side)

`cohort-sync.yml` re-measures every board from scratch - it trusts no committed
report - and `scripts/sign_attestation.py` signs the canonical result with the
cohort's Ed25519 key. The public dossier (ranger.qwalora.com) imports the raw
public key and verifies the signature with WebCrypto. Tampering with any field
invalidates the signature, so a badge is a cryptographic claim, not a screenshot.

## Why this shape

- **No servers to run or patch** - CI is ephemeral compute; the program's only
  standing asset is a signing key.
- **Reproducible** - images pinned by digest (`./qrange pin`); the same bytes run
  for every candidate and in CI.
- **Offline-capable** - `./qrange pack` bundles images + repo for air-gapped use.
- **Brand-consistent** - `brand/tokens.css` is the single source of truth shared
  with the site, so CLI output, reports, and badges read as one system.

## Adding a board

1. Add the vulnerable target under `lab/targets/<name>/`.
2. Add an exploit harness under `lab/attacker/toolbox/` (exit `0` = exploited,
   `3` = blocked).
3. Record attack + benign fixtures under `fixtures/<board>/`.
4. Write `boards/<board>.yml` listing the checks.
5. Ship a detection template under `detections/` and a day brief under
   `evidence/Wnn/Dnnn/README.md`.

The autograder and CI pick it up automatically - no workflow changes needed.
