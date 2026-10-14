# Board 6 — Vanguard (Capstone)

Everything you have built converges here. Board 6 is a full, isolated
**multi-forest Active Directory estate**: the `sevenkingdoms.local` forest with
its `north.sevenkingdoms.local` child, plus a trust to the separate
`essos.local` forest. You own all of it, cross the trusts, and prove each step
with a flag. This is the final board. Clear it and you are a Qwalora Ranger,
Certified.

Like board 5, there is no dataset and no analysis to submit for the objective:
you are on a live range over WireGuard, and proof is a captured `QR6{...}` flag,
seeded to you, planted where only completing the objective can reach it.

## Getting on the range

Same as board 5: Start lab on the portal `/me` page, wait for Deployed,
download WireGuard, bring the tunnel up. Then
`pip install pyyaml && python scripts/fetch.py` writes
`boards/board6/objectives.json` and scaffolds `boards/board6/flags.yml`.

## The objectives

Ten objectives, 100 points, escalating from a foothold to total forest
compromise and cross-forest pivot:

1. Map the forest and its trusts
2. Establish a foothold in the child domain
3. Harvest service and AS-REP tickets across the forest
4. Become Domain Admin of the child
5. Abuse the child to parent trust (inter-realm ticket / SID history)
6. Seize Enterprise Admin on the parent
7. Establish forest persistence (DCSync krbtgt, golden ticket)
8. Pivot across the trust into the second forest
9. Compromise the second forest (Domain Admin)
10. Capture the crown jewels from the root DC

`objectives.json` names the specific targets seeded to your range.

## Submitting and clearing

Paste each captured flag next to its objective id in `flags.yml`, write your
`summary` (the full engagement narrative, foothold to cross-forest DA), commit
and push. Points-weighted: you need **95%** (you can miss at most the 5-point
recon flag) plus an approved capstone report.

The capstone report is the real deliverable, the one you could hand a client or
put in a portfolio: scope, methodology, the full attack path with evidence, and
prioritized remediation across both forests. It is reviewed to the highest bar
in the program.

Rules of engagement are unchanged and absolute: attack **only your own range**.
Clearing board 6 earns the **Vanguard** badge and your certification.
