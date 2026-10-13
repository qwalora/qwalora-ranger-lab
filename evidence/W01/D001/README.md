# W01 / D001 - Board 2: Broken Object Level Authorization

**ATT&CK:** T1190 Exploit Public-Facing Application · **Points:** 100

The Orders API (`lab/targets/web-api`) lets any authenticated user read any
order by id. You will exploit that, detect it, and close it - then prove all
three automatically.

## The loop

1. **Bring it up**
   ```bash
   ./qrange up board2
   ```
   The target is at `http://127.0.0.1:7443` (loopback only).

2. **Exploit it**
   ```bash
   ./qrange exploit board2
   ```
   You authenticate as `alice` and read `mallory`'s order `2001`. Save the
   harness output here as proof:
   ```bash
   TARGET=http://127.0.0.1:7443 python3 lab/attacker/toolbox/exploit_bola.py \
     > evidence/W01/D001/board2.exploit.json
   ```

3. **Detect it** - edit `detections/sigma/board2-bola.yml` so it fires on the
   cross-tenant read in `fixtures/board2/access.log` but stays clean on
   `fixtures/board2/access-benign.log`.

4. **Patch it** - edit `lab/targets/web-api/app.py` at the `PATCH HERE` block so
   the API refuses to return an order the caller does not own (return `403`).

5. **Grade yourself** (no server, runs locally and in CI):
   ```bash
   ./qrange check board2
   ```

## Submit

Commit your changes and open a pull request on your fork. The `validate`
workflow re-runs the exact same checks and posts the result on the PR. A green
check means the board is complete; the program's weekly `cohort-sync` then
signs your progress into a verifiable badge.

## What "done" looks like

- `board2.exploit.json` shows `"result": "EXPLOITED"` with the leaked secret
- your Sigma rule catches the attack and nothing benign
- the exploit returns `BLOCKED` against your patched target
- `./qrange check board2` prints **score 100/100 - PASS**
