# Qwalora Ranger Lab

Your working copy of the Qwalora Ranger range. You fork this template once, and
work each board here as you are promoted. Grading is server-side and answer-free:
you submit your analysis, the portal re-derives the answer key from your unique
seed and scores it. You never hold the key, and your scenario is yours alone.

New to the program? Read the handbook first: https://ranger.qwalora.com/handbook

## One-time setup

1. Use this template to create your own repo (keep it private).
2. Add two Actions secrets (Settings → Secrets and variables → Actions):
   - `QWALORA_HANDLE` — your GitHub handle
   - `QWALORA_TOKEN` — your submission token, shown on your portal `/me` page
   (Optional: set a repository variable `QWALORA_PORTAL` to override the portal URL.)

## The loop, every board

```
pip install pyyaml
python scripts/fetch.py     # pulls your seeded dataset + scaffolds the answer file
# ... investigate (in your SIEM session or the fetched data), fill in the answers ...
git commit -am "board N triage" && git push     # CI grades and prints your score
```

You need 95% on the objective and an approved written report to clear a board.
Your current board, progress, badges, and token are on your portal `/me` page.

## Layout

- `boards/board<N>/` — each board's task (`README.md`), your dataset
  (`alerts.json`), and your answer file (`triage.yml`).
- `scripts/fetch.py` — pull your seeded dataset and scaffold answers.
- `scripts/submit.py` — submit your current board for grading.
- `.github/workflows/grade.yml` — runs the grader on every push.

## Rules

No AI assistants. No sharing answers (they wouldn't match anyway, your seed is
unique). Attack only your own range on the red-team boards. See the handbook.
