# Topic 15 — Scheduling

No position split. Structure:

1. A single sentence, normal main-text formatting: "The Parties propose the following
   schedule:"
2. On the next line, a table matching the format used in the real *Hokes v. Zeus Networks*
   filing: two columns ("Event" | "Date"), full grid borders, header row shaded light gray and
   bold/centered, body rows left column normal alignment and right column centered, with modest
   before/after paragraph spacing — not the exact-24pt main-text spacing; this table uses
   tighter, single-line spacing matching the real template. The table is exempt from the
   document-wide first-line-indent rule; its lead-in sentence still takes the indent.

## Left column — the event rows

The same line items as the real template, adapted for this case's actual plaintiff/defendant
counts:

- Deadline to Exchange Initial Disclosures
- Deadline to Amend Pleadings
- Deadline to file Plaintiff('s/s') Motion for Class Certification (incl. expert reports)
- Deadline to file Defendant('s/s') Opposition to Class Certification (incl. counter expert
  reports)
- Deadline to file Plaintiff('s/s') Reply in Support of Class Certification (incl. rebuttal
  expert reports)
- Hearing on Motion for Class Certification
- Close of Fact Discovery
- Expert Disclosures
- Rebuttal Expert Disclosures
- Expert Discovery Cut-Off
- Deadline for Dispositive Motions
- Pre-trial conference
- Trial

## Right column — the default rule

Populate using the firm's Rule 26(f) Scheduling Report Protocol — see
`references/bf_26f_scheduling_protocol.md` for the distilled timing rules. Where the protocol
gives a timing rule relative to an anchor event (e.g., "45–60 days after the filing of the class
certification motion"), use a bracketed placeholder stating that rule rather than inventing an
actual calendar date — e.g.:

```
[INSERT DATE: 45–60 DAYS AFTER THE FILING OF PLAINTIFFS' MOTION FOR CLASS CERTIFICATION, PER
THE 26(f) PROTOCOL]
```

Where the protocol doesn't address a line item (e.g., deadline to amend pleadings, which
typically depends on resolution of a pending motion to dismiss), use a generic bracketed
placeholder instead of forcing a protocol citation that doesn't apply.

**Never compute an actual date from another bracketed/unknown date** — that arithmetic is for
the attorney to do once real anchor dates exist and the firm calendar has been checked for
conflicts, per the protocol's own instruction.

**The protocol document itself is attorney work product, privileged and confidential** — never
quote from it, attach it, or reference it by name in the actual CMS draft. It's a drafting aid
used to derive the bracketed guidance, not something that appears in the filed document.

## Exception — Initial Disclosures row

If the 26(f) matter-number lookup in Step 1 produced a date, use that same
14-days-after-the-26(f)-conference date here — the identical value inserted into Topic 7's blank
— instead of the usual bracketed placeholder. This row and the Topic 7 sentence describe the
same deadline, so they must always show the same date, sourced the same way. If the lookup
didn't produce a date, this row falls back to the standard bracketed placeholder like any other
line item the protocol addresses.

## Exception — fixed global text, Close of Fact Discovery through Trial

For these seven rows, do NOT use a bracketed placeholder. Use this exact text from the real
*Hokes v. Zeus Networks* template as the global default in every draft, formatted like normal
(non-placeholder) table text:

| Event | Date |
|---|---|
| Close of Fact Discovery | 90 days after decision on class certification |
| Expert Disclosures | 120 days after decision on class certification |
| Rebuttal Expert Disclosures | 180 days after decision on class certification |
| Expert Discovery Cut-Off | 240 days after decision on class certification |
| Deadline for Dispositive Motions | 60 days after expert discovery cutoff |
| Pre-trial conference | TBD |
| Trial | TBD |

The earlier rows (Initial Disclosures through Hearing on Motion for Class Certification) still
use the bracketed 26(f)-Protocol-derived guidance above — only these seven rows get fixed text.

## Special handling — the "Hearing on Motion for Class Certification" Date cell

A class-cert hearing can't just be set the day after the reply brief is due; it has to satisfy
the minimum *notice* period for putting a motion on the judge's calendar. So this Date cell must
state that notice requirement rather than a bare guessed date.

The bullets below establish the notice period and any judge-specific hearing-day constraint —
groundwork shared by both possible outcomes for this cell: a bracketed instruction (the default,
and the only option when the Motion date itself is still unknown) or an actual computed date
(only possible when the Motion row already has a real date — see
`references/calendar_scheduling.md`, step 4).

- **Check both sources, and check them fresh for the actually-assigned judge.** Review (a) the
  assigned judge's individual standing order / civil standing order (from Step 2) and (b) the
  N.D. Cal. Civil Local Rules, for the minimum time that must elapse between filing a motion and
  the hearing, and for any judge-specific motion/hearing calendar (many judges hear civil motions
  only on a set weekday).
- **District-wide baseline: Civil L.R. 7-2(a).** Absent a contrary rule, a motion must be filed,
  served, and noticed for hearing "not less than 35 days after filing of the motion." Those 35
  days are **calendar days**, not court days, and Fed. R. Civ. P. 6(d) does not extend them. Use
  this as the default when nothing more specific applies.
- **Standing order controls if it differs.** If the judge's standing order sets a different
  (often longer) notice period, restricts hearings to a particular calendar day, or otherwise
  deviates from L.R. 7-2(a), the standing order governs — prioritize it over the local-rule
  baseline, and say in the cell that you're following the standing order.
- **Always state the day-counting basis explicitly.** Say whether the period is counted in court
  days, calendar/regular days, or weekdays, exactly as the governing rule or standing order
  specifies (per Fed. R. Civ. P. 6(a) and the rule's own text). Don't leave it ambiguous — the
  whole point of the cell is that the attorney can drop in a real date once the motion filing
  date is fixed, and that requires knowing how to count.
- **If the rule or standing order is unclear** on the count or the mechanics, reproduce the
  **exact language** of the applicable rule and/or standing order verbatim in this same Date
  cell, so the attorney sees the source text and can apply it rather than relying on a paraphrase
  that might be wrong.
- **Default — express it as a bracketed instruction, not a computed date.** Whenever the Motion
  for Class Certification row is itself still a bracketed placeholder, or no calendar tool is
  connected, never do date arithmetic off an unknown date — state the rule instead. For example:

  ```
  [INSERT DATE: AT LEAST 35 CALENDAR DAYS AFTER THE FILING OF THE MOTION FOR CLASS
  CERTIFICATION AND SET ON JUDGE [NAME]'S CIVIL MOTION CALENDAR, PER CIVIL L.R. 7-2(a);
  CONFIRM AGAINST JUDGE [NAME]'S STANDING ORDER, WHICH CONTROLS IF IT SETS A DIFFERENT NOTICE
  PERIOD OR HEARING DAY]
  ```

  This is also where you land back if the computed-date procedure runs but the user ultimately
  says the proposed date doesn't work — revert to this same bracketed form rather than leaving a
  rejected date in the cell.

## When real dates are possible

Four rows — Motion, Opposition, Reply, and the Hearing — can carry actual proposed dates instead
of brackets, but only under the conditions in `references/calendar_scheduling.md`. If those
conditions don't hold, everything above applies unchanged.
