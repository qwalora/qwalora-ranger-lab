#!/usr/bin/env python3
"""
Qwalora Ranger - progress scanner.

Grades every board in boards/ and rolls the results into a program-wide view:
a branded console table plus evidence/PROGRESS.md (committed, and the source the
Ranger Dossier reads). This is what a candidate runs to see where they stand and
what the cohort sign-off will measure.

Usage: python3 scripts/progress.py [--repo-root .]
"""
import argparse
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

ORANGE = "\033[38;5;208m"; GREEN = "\033[38;5;42m"; RED = "\033[38;5;203m"
AMBER = "\033[38;5;214m"; DIM = "\033[2m"; BOLD = "\033[1m"; RST = "\033[0m"


def grade_all(root):
    validate = importlib.import_module("validate")
    load_yaml = validate.load_yaml
    rows = []
    for manifest in sorted((root / "boards").glob("*.yml")):
        board = load_yaml(manifest)
        earned = possible = 0
        passed_checks = 0
        for chk in board.get("checks", []):
            possible += chk.get("weight", 0)
            fn = validate.DISPATCH.get(chk["kind"])
            ok = False
            if fn:
                try:
                    ok, _ = fn(chk, root, board)
                except Exception:  # noqa: BLE001
                    ok = False
            if ok:
                earned += chk.get("weight", 0)
                passed_checks += 1
        score = round(100 * earned / possible) if possible else 0
        rows.append({
            "board": board["board"], "title": board.get("title", ""),
            "attack": board.get("attack", {}).get("id", ""),
            "week": board.get("week", ""), "score": score,
            "checks": len(board.get("checks", [])), "passed_checks": passed_checks,
            "done": score >= board.get("pass_threshold", 100),
        })
    return rows


def write_markdown(rows, root):
    done = sum(1 for r in rows if r["done"])
    lines = [
        "# Ranger progress", "",
        f"**{done}/{len(rows)} boards complete** - "
        f"{round(100*done/len(rows)) if rows else 0}% of the program", "",
        "| Board | Focus | ATT&CK | Score | Status |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        status = "complete" if r["done"] else (
            "in progress" if r["score"] else "not started")
        lines.append(
            f"| `{r['board']}` | {r['title']} | {r['attack']} | "
            f"{r['score']}/100 | {status} |")
    lines += ["", "_Regenerate with `qrange status`. The cohort sign-off "
              "re-measures these from scratch before signing._", ""]
    (root / "evidence").mkdir(exist_ok=True)
    (root / "evidence" / "PROGRESS.md").write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=str(ROOT))
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()

    rows = grade_all(root)
    write_markdown(rows, root)

    done = sum(1 for r in rows if r["done"])
    print(f"\n{ORANGE}Qwalora Ranger{RST} {DIM}/ progress{RST}\n")
    for r in rows:
        if r["done"]:
            tag = f"{GREEN}complete{RST}"
        elif r["score"]:
            tag = f"{AMBER}in progress{RST}"
        else:
            tag = f"{DIM}not started{RST}"
        print(f"  {BOLD}{r['board']}{RST}  {r['title']:<36} "
              f"{DIM}{r['attack']:<7}{RST} {r['score']:>3}/100  [{tag}]")
    pct = round(100 * done / len(rows)) if rows else 0
    print(f"\n  {BOLD}{done}/{len(rows)} boards complete{RST} {DIM}({pct}%){RST}")
    print(f"  {DIM}written: evidence/PROGRESS.md{RST}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
