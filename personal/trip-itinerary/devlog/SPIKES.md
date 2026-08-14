# Spikes — trip

Short-form index of every spike branch, merged or discarded. Fuller detail
for each lives in `devlog/NNN-spike.md`.

A discarded spike's commits vanish with its branch, so this file is the only
record that the attempt happened. Both outcomes get an entry — the log's
value is in preserving what was tried and rejected, not just what shipped.

| # | Date | Purpose | Result |
|---|---|---|---|
| — | — | *(no spikes yet)* | — |

## How to add one

1. Branch: `spike/NNN`.
2. Write `devlog/NNN-spike.md` from the template below as you go, not after.
3. A/B the branch against `main` — same question, both branches, compare the
   answers.
4. Add the row here with the outcome — `merged` or `discarded` — then merge
   or delete the branch.

## Template — `devlog/NNN-spike.md`

```markdown
# NNN — <one-line title>

- **Date:** YYYY-MM-DD
- **Branch:** `spike/NNN`
- **Result:** merged | discarded

## Hypothesis
What was believed, and what would be true if it held.

## What changed
Files touched and the substance of the change.

## Test method
The question run on both branches. What was compared.

## Result
What actually happened, including the parts that contradict the hypothesis.

## Decision
Merged or discarded, and why. If discarded, what would have to be different
for it to be worth trying again.
```
