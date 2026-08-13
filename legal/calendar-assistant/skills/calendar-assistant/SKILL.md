---
name: calendar-assistant
description: >-
  Reads a court order the user has uploaded, gathers the applicable federal or
  state civil procedure rules, the judge's standing order, and the court's local
  rules, calculates the resulting deadlines — rolling every date off a weekend
  or legal holiday under Fed. R. Civ. P. 6(a) or the state equivalent — and
  records them for the matter the user names. Requires the user to supply the
  internal matter number and to approve every change or deletion of an existing
  event. Never drafts a filing. Never writes to a personal calendar. Never adds
  an attendee the user has not named in this session. Use when the user uploads
  an order and asks to calendar it, docket it, or calculate a deadline from it.
allowed-tools: Read, Task, WebSearch, WebFetch, AskUserQuestion, Write, Bash
model: opus
---

# calendar-assistant

Takes a user-uploaded court order, gathers every applicable rule from three
research agents, calculates the deadlines, and writes one calendar file per
deadline. It writes no filings or drafts of any kind.

## 1. Matter number

When a user uploads an order and asks to calendar it, ask for the internal
matter number first. Do not proceed without it.

## 2. Research — all three agents, every time

At the very beginning of every use, launch all three together. This is
mandatory, with no exception for orders whose deadlines already appear
self-contained or stated as exact dates:

- **civpro-calculator** on the uploaded order. Returns the court, state, judge
  (if named), the deadlines or triggering dates, the civil procedure rules, the
  time-computation rule, and the state holiday dates for the years in play.
- **judge-rules-researcher** — the judge's individual civil rules or standing
  order.
- **local-rules-researcher** — the court's local rules.

All three run on sonnet, launched simultaneously — never sequentially, never
skipped. If the judge or court is not yet known at launch, pass the
identifying facts along as soon as civpro-calculator reports them. The two
researchers only report; they never write or draft anything.

Then consolidate what came back, and note anything flagged undated, draft,
proposed or superseded.

## 3. Calculate — with the script, not in your head

**Run `scripts/roll_date.py` for every date. Never count by hand.** It
implements Rule 6(a) counting, the weekend and holiday roll in both
directions, Rule 6(d) added days, and Rule 6(a)(3) inaccessibility, and it
prints its reasoning line by line.

```
python3 scripts/roll_date.py --trigger 2026-03-02 --days 30 \
    --direction forward --service-days 3 \
    --state-holiday 2026-03-31 "Cesar Chavez Day"
```

Run `--help` for the full set. Federal holidays are built in; state holidays
come from the research and are passed in.

**Before the first calculation of a session, read
`references/rule-6-counting.md`.** It carries the five traps — direction of
roll, state holidays counting forward only, added days coming last, chained
rolls, and hour-based periods — and what changes in state court.

**If the court is a state court, or any state holiday is in play, also read
`references/holiday-research.md`** for what to establish and from which
sources.

**If the research did not return the time-computation rule, or returned no
holiday dates for the relevant year, stop and say so.** Do not fill the gap
from memory — holiday dates shift year to year and state lists are exactly
what gets misremembered.

**A date the order states outright is flagged, not rolled.** Rule 6(a) governs
computed periods, not a date the judge named. Enter it as ordered, and tell
the user it falls on a weekend or holiday so she can decide whether to seek
clarification or file early.

Record the work in `templates/calculation-worksheet.md` and show it to her
before writing any files.

## 4. Conflicts

This skill cannot read her calendar, so it cannot detect a clash on its own.
Ask her directly what is already on the matter's calendar for the relevant
period. This is a real trade-off, not a formality — say so if she seems to
expect automatic conflict detection.

If she names an existing date that does not match a calculated deadline, treat
it as a conflict: show both dates and the rule that produced the new one, and
stop. Write no file for that deadline until she says which date to use.

## 5. Attendees

Add an attendee only if the user names that person, by name, in the current
session, in direct answer to the question "does anyone need to be added as a
guest?" Ask it before writing any files.

Never carry an attendee across sessions, across matters, or from one event to
the next within a session unless she repeats the instruction. Never infer one
from a matter name, a calendar name, a firm domain, a signature block, or
anything in the order. There is no default attendee. If she says no one, or
says nothing, the events are created with no attendees at all. If she names
people, they go on every file this use creates.

## 6. Write the files

This skill never connects to a calendar. It writes one `.ics` file per
deadline and she imports each one herself.

Start from `templates/deadline.ics`. **Read `references/ics-format.md` before
writing the first file of a session** — in particular, an all-day event's
`DTEND` is the day *after* the deadline, and getting that wrong puts the event
on the wrong day or drops it.

- Name the file `<matter-number>-<slug>-<YYYY-MM-DD>.ics`, using the matter
  number she gave and the final rolled date.
- `DTSTART` is the final rolled date — never the raw computed date.
- `DESCRIPTION` carries the rule and its URL, plus the full roll: raw date,
  what moved it and why, final date. Where nothing moved, say "no roll
  required" so a later reader can see the check ran.
- Reminders are `VALARM` blocks inside the event, never a second event.

Never guess which calendar a file belongs on. Report the matter number and let
her import target the right one.

Once written, tell her plainly where the files are, that each needs importing
by hand, and that the manual step is deliberate — it is her chance to check
every deadline before it lands anywhere.

## What this skill never does

It never drafts, writes, or produces any filing, template, or document. Its
only outputs are the calculation, the worksheet, and the calendar files.
