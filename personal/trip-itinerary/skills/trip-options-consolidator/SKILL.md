---
name: trip-options-consolidator
description: Given an ordered list of cities, builds one combined itinerary
  covering all three activity levels (low, medium, high), each with all
  three travel budget options (cheapest, mid-range, luxury) shown for how
  to get to the next city, in the order the cities were given, with a link
  on every activity and every travel option — as a spreadsheet if she wants
  one, or in the conversation if she doesn't. Also offers to add a travel
  leg before city 1 or after the last city if she names a beginning or
  ending city. Runs cities-itinerary three
  times and transportation-researcher three times per leg, and merges what
  they return. Use when the user names three or more cities in a trip order
  and wants a deliverable covering what to do and how to get between them.
  Do NOT use it when she only wants activities (cities-itinerary alone),
  only wants routes between two places (transportation-researcher alone),
  or only wants one activity level instead of all three.
allowed-tools: Task, Bash, Write, Read, AskUserQuestion
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

Also ask her, up front, whether she wants this as a spreadsheet or just
the answer in the conversation. Ask it alongside whatever else you're
asking for (dates, constraints) so it's one round of questions, not two.
Her answer decides which of the two "Delivering the result" paths below
you follow once the merge is done — don't build a spreadsheet she didn't
ask for, and don't withhold one she did.

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

Assemble all of this into one JSON file matching the shape in
`templates/trip_data.example.json` — `sequence` from above, `travel_legs`
keyed by the same labels used in `sequence`, and `activities` with one
entry per tab, each keyed by city name. That JSON file is what the next
step runs on, whether or not she asked for a spreadsheet.

## Delivering the result

**If she asked for a spreadsheet:** run

```
python3 scripts/build_itinerary.py <path to the merged JSON>
```

from inside this skill's folder. It writes the workbook next to the JSON
file, one sheet per activity level, fully formatted — column widths,
section-header rows, alternating stripes, borders, all of it. You don't
need to reproduce any of that formatting by hand; the script is the single
source of truth for it. If she asks why the sheet looks the way it does,
or you're changing the format itself, see
`references/spreadsheet-format.md`.

Tell her in plain English, once the file is saved: where it is, that it has
three tabs, and to open it and give it a look — don't repeat the whole
itinerary back to her in the conversation, the spreadsheet is the
deliverable.

**If she did not ask for a spreadsheet:** give her the three itineraries
directly in the conversation, in plain English, activity level by activity
level — low, then medium, then high — each covering city by city and leg
by leg with all three travel options. Nothing gets written to a file in
this case; the conversation is the deliverable, and the merged JSON is
just working memory you don't need to keep.
