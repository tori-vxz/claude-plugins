# Calendar-assisted dates

An exception to the bracketed-26(f)-protocol default in `templates/schedule_table.md`. Four
Topic 15 rows — Motion for Class Certification, Opposition, Reply, and the Class-Cert Hearing —
can get an actual proposed date instead of a bracket.

## Preconditions

Both must hold:

(a) a calendar tool is connected in this session, and
(b) the CMC hearing date used in the caption is a real date rather than a bracketed placeholder
    (i.e., a Rule 16 Order was provided) — per the general rule against computing a date from
    another unknown/bracketed date.

If either fails, skip this whole file, leave all four rows as the standard bracketed
placeholders, and say so plainly in your response rather than silently omitting the
calendar-based attempt. The Hearing row has a second, independent precondition of its own — see
step 4.

## Always compute with the script

Before doing any of the date arithmetic below by hand, run `scripts/frcp6_date.py <anchor-date>
<offset>` (e.g., `python3 scripts/frcp6_date.py 2026-08-13 "9 months"`) for **every** date
computed here. It applies Fed. R. Civ. P. 6(a) correctly — calendar-month arithmetic with
month-end clamping, plus the weekend/legal-holiday roll-forward required by Rule 6(a)(1)(C) —
which is easy to get subtly wrong by eyeballing a calendar (a holiday that's itself "observed"
on a shifted day, a roll-forward that crosses into the next month, etc.).

The script's output also flags that it only checks federal holidays: Rule 6(a)(6)(C)
additionally picks up California-observed court holidays for periods measured after an event
(which every date here is), so mention that caveat to the user rather than treating the script's
output as the final word.

The weekend/holiday roll-forward itself is mechanical — apply it automatically every time; it
doesn't need separate user approval the way the underlying date *choice* does in steps 1 and 3.

## Search the calendar narrowly, not with a blind full-month dump

The firm's primary calendar carries a large volume of matter-level events (one calendar per
case/matter, plus a shared primary calendar), so an unscoped `list_events` call bounded only by
a month's start/end time can return more data than fits in context.

- Bound every query by `startTime`/`endTime` to the specific calendar month in question.
- Narrow further by content — either call `list_events` with `fullText` set to **one**
  dispositive-motion term at a time (its matching is an AND across all terms in a single call,
  so one keyword per call: one for "summary judgment," another for "class certification,"
  another for "Daubert"), or use `search_events` for a semantic query like "dispositive motion
  deadline."
- Read only the fields you need from the results (event title/summary and date), not the full
  raw response.
- If a query still comes back large, do the filtering in a subagent or script rather than
  pulling the whole thing into your own context.
- **Dispatch each month-scoped conflict search to its own subagent** (steps 1, 3, and step 4's
  conflict re-checks are each a self-contained lookup-and-summarize task) and have it return just
  the short list of conflicting deadlines, or "none found" — not the raw event payload. Because
  each search depends on the date settled on by the step before it, run them one at a time rather
  than in parallel with each other.

## Step 1 — Motion for Class Certification

- Compute the FRCP-6-adjusted date 9 months after the CMC hearing date (the midpoint of the
  26(f) protocol's 8–10 month range) using the script.
- Search the user's calendar for the calendar month containing that date, for any other
  dispositive-motion deadlines already on it — motions for summary judgment, motions for class
  certification, Daubert motions or Daubert oppositions, replies in support of class
  certification, and the like (non-exhaustive — search broadly for dispositive-motion language,
  not just this exact list). This is a search for deadlines already labeled on the calendar, not
  a general busy/free lookup.
- If that search turns up any such deadlines, tell the user plainly which dates and which motions
  are due that month (a short list is enough — this is a quick "here's what else is due" flag,
  not a formal report), then ask whether the 9-month date is still preferable given everything
  else due that month. Use the elicitation/AskUserQuestion tool if available; otherwise ask
  directly in your response and wait for an answer before continuing.
  - **If yes (or if the search found nothing that month):** use the 9-month FRCP-6-adjusted date
    for this cell. Continue to step 2.
  - **If no:** compute the FRCP-6-adjusted dates 8 months and 10 months after the CMC hearing
    date the same way, and run the same dispositive-motion search for each of those two months.
    - Compare the two months' dispositive-motion loads and present the user with whichever month
      has *fewer* such deadlines, along with the full list of what's due that month, and ask if
      that month is preferable.
      - If yes: use that month's FRCP-6-adjusted date for this cell. Continue to step 2.
      - If no: leave this cell as the standard bracketed 26(f)-protocol placeholder rather than
        forcing a date the user has now twice indicated isn't workable. Also leave steps 2 and 3
        as bracketed placeholders, and skip the rest of this file for this row set.
    - If the 8-month and 10-month searches turn up the same number of dispositive deadlines, say
      so and ask the user to choose between the two directly rather than picking one arbitrarily.

## Step 2 — Opposition to Class Certification

- Only run this step if step 1 actually settled on a date (not a placeholder) — an offset from an
  unknown/bracketed anchor can't be computed. If step 1 ended in a placeholder, leave this cell
  as the standard bracketed placeholder too and skip to step 3.
- Otherwise, use the script to compute the FRCP-6-adjusted date 60 days after whatever date step
  1 settled on, and use that for this cell. No calendar conflict search or separate user
  confirmation is needed here — the 26(f) protocol's 45–60 day range is narrow, and once the
  anchor date has been confirmed with the user in step 1, a fixed offset off of it is routine
  rather than something to re-litigate with another round of questions.

## Step 3 — Reply in Support of Class Certification

- Only run this step if step 2 actually settled on a date; otherwise leave this cell as the
  standard bracketed placeholder as well.
- Use the script to compute the FRCP-6-adjusted date 45 days after the Opposition date from step
  2.
- Run the same dispositive-motion calendar search and confirmation process as step 1 (search that
  month, tell the user what else is due, ask if the date is still acceptable) — but there is no
  8/10-month-style fallback here. If the user says no, leave this cell as the standard bracketed
  placeholder rather than proposing an alternative offset.

## Step 4 — Hearing on Motion for Class Certification

- Only run this step if step 1 actually settled on a date; if the Motion row is still a
  placeholder, this row falls back to the bracketed instruction in `templates/schedule_table.md`
  and the rest of this step doesn't apply.
- Determine the notice period (and any judge-specific hearing weekday/time) using the "Check both
  sources" / "District-wide baseline" / "Standing order controls" bullets in
  `templates/schedule_table.md` — that groundwork is the same either way; the only thing that
  changes here is that you now have a real Motion date to compute from.
- **Compute the first candidate date.** If the judge has no fixed hearing weekday, run
  `scripts/frcp6_date.py <motion-date> "<N> days"` and use `adjusted_date`. If the judge does
  hear civil motions only on a specific weekday, run `scripts/frcp6_date.py <motion-date>
  "<N> days" --weekday <Weekday>` and use `weekday_adjusted_date` instead — this finds the
  earliest occurrence of that weekday that still satisfies the notice period and isn't itself a
  federal holiday.
- **Check the candidate date (and time, if the standing order specifies one) against the user's
  calendar for a conflict.** Search narrowly per the guidance above — a single day's query,
  optionally bounded to the specific hearing time if one is known; if no specific time is stated
  anywhere, check the whole day for an existing conflicting event and say so when you present the
  date to the user (the exact time will still need confirming once the court sets it).
- **If there's a conflict, walk the candidate forward and recheck** rather than picking the very
  next open day: if the judge has a fixed hearing weekday, call the script again with an anchor
  of (candidate + 1 day), offset `"0 days"`, and the same `--weekday`, which returns the next
  occurrence of that weekday; if there's no fixed weekday, call the script again with anchor
  (candidate + 1 day) and offset `"0 days"` (no `--weekday`), which reapplies the weekend/holiday
  roll-forward to find the next open day. Repeat until you find a date with no conflict.
- **Once you have a conflict-free candidate, ask the user two separate questions** (use the
  elicitation/AskUserQuestion tool if available; otherwise ask directly and wait for both
  answers) — don't collapse these into one, since a "yes" to the first doesn't imply a "yes" to
  the second:
  1. Does this date (and time, if known) work?
     - **No:** revert this cell entirely to the bracketed-instruction default in
       `templates/schedule_table.md` — not the rejected date, not a note about the rejection,
       just the same bracketed cell that would exist if this whole procedure had never run. Don't
       ask the second question.
     - **Yes:** insert this date into the cell (formatted like the rest of the table), and
       continue to the second question.
  2. Would you like me to create a calendar event for this hearing date now, before I add
     anything to your calendar?
     - **Yes:** create the event via the connected calendar tool (e.g., "Hearing: Plaintiff's
       Motion for Class Certification – [short case name]," with the case number and caption in
       the description, at the confirmed time if one is known).
     - **No:** leave the calendar alone — the date still goes in the cell either way; this
       question only controls whether an event gets created.
- Anchor a Word comment to the cell noting the basis for the date (the notice period and source —
  L.R. 7-2(a) or the judge's standing order, plus the weekday constraint if any) and that it was
  checked against the calendar for conflicts as of today, so the reviewing attorney can see how it
  was derived rather than just seeing a bare date.

## Creating calendar events for accepted dates (Motion, Opposition, and Reply only)

As soon as the user accepts a date for one of these three cells (a "yes" answer in the flow
above), create a corresponding event on the user's calendar via the connected calendar tool
before moving on to the next row — e.g., an all-day event titled "Deadline: Plaintiff's Motion
for Class Certification – [short case name]" (substituting the row's actual event name and the
case's short name), with the case number and case caption in the event description so it's
identifiable later.

Create each event right after its date is accepted rather than batching all three at the end, so
that an early "no" which short-circuits steps 2–3 doesn't leave stray events to walk back
afterward. Never create an event for a cell that ends up as a bracketed placeholder.

**The Hearing row (step 4) does not follow this paragraph** — it has its own separate, explicit
confirmation for calendar-event creation, distinct from accepting the date itself, because unlike
the other three rows a hearing date carries a real court appearance that shouldn't land on the
calendar just because the date looked fine in the document.
