---
name: trip-options-consolidator
description: Given an ordered list of cities, builds one combined itinerary
  covering all three activity levels (low, medium, high), each with all
  three travel budget options (cheapest, mid-range, luxury) shown for how
  to get to the next city, in the order the cities were given, with a link
  on every activity and every travel option — always as a spreadsheet,
  either an Excel workbook or a Claude artifact, whichever she picks. Also
  offers to add a travel
  leg before city 1 or after the last city if she names a beginning or
  ending city. Runs cities-itinerary three
  times and transportation-researcher three times per leg, and merges what
  they return. Use when the user names three or more cities in a trip order
  and wants a deliverable covering what to do and how to get between them.
  Do NOT use it when she only wants activities (cities-itinerary alone),
  only wants routes between two places (transportation-researcher alone),
  or only wants one activity level instead of all three.
allowed-tools: Task, Bash, Write, Read, AskUserQuestion, Artifact
model: opus
---

Take the cities she names, in the order she names them — that order is the
trip order, and it decides both the transportation legs and the final
layout.

The deliverable always covers all three activity levels, each on its own
tab, and every tab shows all three travel budget tiers for every leg — a
tab never picks one budget over another, since the budget choice is hers
to make while looking at the sheet, independent of the activity level:

- **Low activity** — with cheapest, mid-range, and luxury travel options
  shown for every leg
- **Medium activity** — same three travel options for every leg
- **High activity** — same three travel options for every leg

Do not ask her to pick one level — she gets all three, side by side, so she
can compare. If she's given a constraint beyond the cities themselves (a
season, an interest, travel dates), ask for it up front if missing, since
transportation-researcher needs dates to search — and carry that constraint
into every spawn below, not just the first.

The deliverable is always a spreadsheet. Ask her, up front, which of the
two she wants it as:

- an **Excel file** she opens on her machine, or
- a **Claude artifact** she opens in the browser and can share by link.

Ask it alongside whatever else you're asking for (dates, constraints) so
it's one round of questions, not two. It is the same spreadsheet either
way — same six columns, same three tabs, same section headers, same
colors — built from the same merged data by the same script, so the choice
is only about where she wants to read it. Never offer a third option of
writing the itinerary out in the conversation instead; she gets a
spreadsheet.

In that same round of questions, ask whether there's a beginning city she's
traveling from before city 1, or an ending city she's traveling to after
the last city — she can give one, both, or neither. These are not part of
the itinerary — no activities are researched for them, and cities-itinerary
never runs for them — they only add a travel leg at the very start or very
end of the trip. If she gives one or both, carry the city name(s) into the
spawning step below as extra legs.

## Spawning

Spawn every subagent below in the same message, all at once.

**Three cities-itinerary subagents**, one per activity level, each covering
every city:

```
/cities-itinerary

cities: <city 1>, <city 2>, <city 3>, ...
activity level: low
```

Repeat with `activity level: medium` and `activity level: high` — three
spawns total, same city list each time.

**Three transportation-researcher subagents per consecutive pair of
cities** — one per budget tier, for every leg. For `n` cities that's
`(n - 1) × 3` spawns:

```
/transportation-researcher

from: <city 1>
to: <city 2>
budget: cheapest
```

Repeat with `budget: mid-range` and `budget: luxury` for that same leg, then
do all three again for city 2 → city 3, city 3 → city 4, and so on.

**Every luxury spawn carries the ceiling.** Write it into the prompt, on
its own line, exactly:

```
budget: luxury
ceiling: $10,000 — never report an option above this, whatever she has said her budget is
```

$10,000 is the cap on luxury travel for this trip, per leg. It is the same
ceiling transportation-researcher already applies, said again here so the
subagent has it in front of it — a subagent inherits nothing from this
conversation. If a luxury leg comes back with an option above $10,000,
that leg is a mis-spawn: drop the option and re-spawn that leg rather than
carrying it into the sheet. Nothing over the ceiling reaches her, and it
is never raised to fill out a leg — a leg with two luxury options, or
none, is the honest answer.

**If she gave a beginning city**, add three more transportation-researcher
spawns, same as any other leg, for beginning city → city 1:

```
/transportation-researcher

from: <beginning city>
to: <city 1>
budget: cheapest
```

Repeat with `budget: mid-range` and `budget: luxury`. Spawn these alongside
everything else in the same message, not as a separate round.

**If she gave an ending city**, add three more traveler-in-between
spawns the same way, for the last city → ending city:

```
/transportation-researcher

from: <last city>
to: <ending city>
budget: cheapest
```

Repeat with `budget: mid-range` and `budget: luxury`, spawned in that same
message too.

One skill per spawn: nothing else runs alongside cities-itinerary or
transportation-researcher in these subagents. Each spawn prompt is
everything that subagent needs — a subagent starts fresh, inherits nothing
from this conversation, and cannot ask a follow-up question. Every travel
leg spawns as `traveler-in-between` running the transportation-researcher
skill — confirm this before sending the batch, since a leg spawned as a
plain/default agent or without the skill invocation is a mis-spawn, not a
usable substitute.

## Merging

Build a `sequence` describing the sheet from top to bottom, once — it's
reused on every tab:

1. A `leg` step for the beginning city to city 1, only if she gave a
   beginning city
2. A `city` step for city 1
3. A `leg` step for city 1 to city 2
4. A `city` step for city 2
... and so on through the last city, followed by:

- A `leg` step for the last city to the ending city, only if she gave an
  ending city

The beginning-city and ending-city legs are travel rows only — no `city`
step gets added for the beginning or ending city itself.

Pull each city's activities out of the matching cities-itinerary result —
low activities only go under `city` steps on the low tab, medium only on
the medium tab, high only on the high tab. For each leg, pull all three
transportation-researcher results (cheapest, mid-range, luxury) — they're
shared across all three tabs unchanged, since travel budget doesn't depend
on activity level. Never mix an activity level onto the wrong tab.

**Keep the link with every item.** cities-itinerary reports an official
website link for every activity; transportation-researcher reports a
purchase link for every travel segment. Carry both through untouched — an
activity or a segment with no link is a gap to flag, not something to drop
silently.

**One travel service per row.** A budget tier often comes back with more
than one way of making the journey — a train and a bus that are both the
cheapest sort of option, two airlines that are both mid-range. Never pack
those into a single Details cell. Give each one its own entry, and name it
in `item` by the service actually being taken — the airline and flight
number, the specific train, the specific bus line — not a summary like
"train or bus". Every one of those entries keeps the tier it belongs to,
so three cheapest options are three rows all reading `Cheapest`, each with
its own details and its own booking link.

**Cost and transfers sit with the tier, not in the prose.** Every travel
entry carries two more fields alongside `tier`, and they go in the budget
column with it rather than being left to Details:

- `cost` — what that option costs in total, as one figure with its
  currency, e.g. `$245` or `EUR18.90`.
- `connections` — `Nonstop`, or `1 transfer`, `2 transfers`, counting
  every change of vehicle across the whole journey.

transportation-researcher reports both for every option it finds; carry
them across rather than working them out yourself, and if one is genuinely
missing for an option, leave the field out rather than guessing. Details
then covers what the other two don't — comfort, timings, frequency, what
makes this option worth considering — instead of repeating the price back.

To do that, put a list under `options` on the tier, as
`templates/trip_data.example.json` shows for one leg. The build script
turns each element into its own row.

Assemble all of this into one JSON file matching the shape in
`templates/trip_data.example.json` — `sequence` from above, `travel_legs`
keyed by the same labels used in `sequence`, and `activities` with one
entry per tab, each keyed by city name. That JSON file is what the next
step runs on, in either format.

## Delivering the result

Both formats come out of the same script, run from inside this skill's
folder. It writes the file next to the JSON file, one tab per activity
level, fully formatted — column widths, section-header rows, alternating
stripes, borders, all of it. You don't need to reproduce any of that
formatting by hand; the script is the single source of truth for it, and
it is what keeps the two formats identical. If she asks why the sheet
looks the way it does, or you're changing the format itself, see
`references/spreadsheet-format.md`.

**If she asked for an Excel file:** run

```
python3 scripts/build_itinerary.py <path to the merged JSON>
```

**If she asked for a Claude artifact:** run

```
python3 scripts/build_itinerary.py <path to the merged JSON> --format artifact
```

which writes a finished, self-contained web page — the same sheet, with
the three activity levels as tabs across the top. Publish that file with
the Artifact tool, using the trip name as the title (e.g. "Venice Florence
Itinerary") and 🧳 as the favicon, and give her the link. The page is
generated whole by the script, so there is no design work to do and
nothing to hand-write into it.

**Then, before you tell her it's done**, open what you built and read down
the travel rows. Each one must be a single service, named in the Item
column, with its tier, its cost and its transfers in the budget column. If
any Details cell has ended up holding two journeys, that's a merge that
packed them together: split them into separate entries in the JSON, one
per service, each keeping the same tier, and run the script again. Check
too that no luxury row is above $10,000 — if one is, it should not have
come back at all, so drop it and re-spawn that leg.

Tell her in plain English, once it's built: where the file is or what the
link is, that it has three tabs, and to open it and give it a look — don't
repeat the whole itinerary back to her in the conversation, the
spreadsheet is the deliverable.
