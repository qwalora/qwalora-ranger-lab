# Security & containment model

The Qwalora Ranger lab contains **deliberately vulnerable** software. That is the
product: you need something real to exploit. The engineering goal is therefore
not "nothing is vulnerable" - it is that the vulnerable things **stay in the
box**. The lab is built so that, run as intended, the targets cannot reach the
internet, cannot reach your host, and cannot be reached from your network.

We say *safe by design*, not *unhackable*. No containment is absolute. Treat the
whole lab as hostile and never bridge it to a network you care about.

## Containment controls

Every control below is enforced in `docker-compose.yml` and the seccomp profile,
not left to the operator.

| Risk | Control |
|---|---|
| Target reaches the internet | both Docker networks are `internal: true` - there is **no route to egress** |
| Target exposed to your LAN | every published port binds to `127.0.0.1` only, never `0.0.0.0` |
| Container escape to host | non-root (`user: 10001`), `read_only` root fs, `cap_drop: ALL`, `no-new-privileges`, restrictive `seccomp` |
| Docker socket escape | the socket is **never** mounted into any container |
| Resource exhaustion | `mem_limit`, `cpus`, `pids_limit` on every service |
| Supply-chain tampering | images pinned by digest (`./qrange pin`); SBOM + `cosign verify` are board-4 exercises |
| Secret leakage | the Grafana admin password is generated at spin-up, gitignored, passed via a Docker secret file |

The attacker container is the one intentional exception to a few controls: it
holds `NET_RAW`/`NET_ADMIN` so scanning tools work, and a small writable tmpfs
for tool state. It is still on the internal, no-egress network with no host
access.

## What the grader does and does not run

- The autograder (`scripts/validate.py`) runs **your** detection rules and
  launches **your** patched target to re-run the exploit. It does not execute
  arbitrary candidate code paths beyond that, and in CI it runs in GitHub's
  ephemeral, sandboxed runners that are destroyed after the job.
- No candidate input is ever executed on program infrastructure. The program
  side only re-measures and signs (`cohort-sync.yml`); it runs the same checker
  on the committed repo contents.

## Reporting

Found a way the lab escapes its box, or a flaw in the grader or the signing
scheme? That is a real finding - email **security@qwalora.com**. Please do not
open a public issue for containment or signature-forgery bugs.

## Operator checklist

- Run on a machine you control, ideally a throwaway VM.
- Do not change `internal: true` or the `127.0.0.1` binds.
- Run `./qrange pin` before a cohort so everyone runs identical, verified images.
- `./qrange down` wipes the volumes when you are finished.
