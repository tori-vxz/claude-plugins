# Writing the .ics file

The calendar files follow RFC 5545. Every calendar worth importing into reads
it, so nothing here is vendor-specific.

Start from `templates/deadline.ics` and fill the placeholders. The notes below
are the parts that go wrong.

## All-day events: DTEND is exclusive

This is the one real trap. For an all-day event, `DTEND` is the day *after*
the event, not the event's own date:

```
DTSTART;VALUE=DATE:20260401
DTEND;VALUE=DATE:20260402
```

That is a one-day event on 1 April. Setting both to `20260401` produces a
zero-length event, which some calendars silently drop and others show on the
wrong day. Always advance `DTEND` by one day.

Dates in `VALUE=DATE` form carry no dashes: `20260401`, not `2026-04-01`.

## The fields

| Field | What goes in it |
|---|---|
| `UID` | must be unique per event; matter number, slug and date make a good one |
| `DTSTAMP` | UTC timestamp of when the file was written, `20260401T143000Z` |
| `SUMMARY` | matter number, then the deadline in plain terms |
| `DTSTART` / `DTEND` | the **final rolled** date, and the day after it |
| `DESCRIPTION` | the rule, its URL, and the full roll — see below |
| `TRANSP:TRANSPARENT` | a deadline does not make the day look busy |
| `VALARM` | the reminder, inside the event — never a second event |

## The description carries the reasoning

The event outlives this session, so the description records how the date was
reached: the triggering date and event, the period and direction, the rule
that set it with its URL, the raw computed date, what moved it and why (named
holiday or which weekend day), and the final date. Where nothing moved, say
"no roll required" — a later reader needs to see the check ran.

Line breaks inside a value are written `\n`, not actual newlines.

`templates/deadline.ics` leaves the long `DESCRIPTION` on one line on purpose:
folding it in the template would split the `{{PLACEHOLDER}}` names across
lines and break substitution. Fill the placeholders first; fold afterwards if
at all. A single long line imports fine everywhere in practice, so folding is
optional — but if you do fold, the rule is a line break followed by exactly
one space, at no more than 75 octets per line, and the space is *not* part of
the value.

## Reminders

`TRIGGER:-P14D` fires 14 days before. Use `-PT9H` style only if a specific
time of day is genuinely required, which for an all-day event it usually is
not. One `VALARM` per reminder, all inside the same `VEVENT`.

## Attendees

Only per the attendee rule in `SKILL.md` — never inferred, never carried over.
The form is:

```
ATTENDEE;CN=Full Name;ROLE=REQ-PARTICIPANT:mailto:address@example.com
```

If the user names someone without an address, ask for it rather than guessing
one from a firm domain. Never write an `ORGANIZER` line with a guessed
address.

## Before handing the file over

Check that `DTEND` is one day after `DTSTART`, that the dates in the filename,
`UID`, `DTSTART` and `DESCRIPTION` all agree, and that `BEGIN`/`END` pairs
match for `VCALENDAR`, `VEVENT` and `VALARM`.
