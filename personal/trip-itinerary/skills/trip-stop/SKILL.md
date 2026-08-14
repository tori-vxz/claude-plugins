---
name: trip-stop
description: Given one stop — a city plus the travel leg arriving at it, and
  optionally a trailing leg departing it — researches that city's activities
  at all three activity levels and the leg(s) at all three budget tiers, in
  a single context, then writes one JSON shard to an exact assigned path.
  Use only when spawned by `trip-itinerary:trip` as a `trip-itinerary:trip-scout` subagent for
  one stop of a multi-city itinerary. Do NOT use it for a standalone city's
  activities with no shard to write (that's city-researcher), for a
  point-to-point transportation lookup outside a shard workflow (that's
  transportation-researcher), or for more than one stop in a single run —
  one scout owns exactly one stop.
effort: high
user-invocable: true
---

# trip-stop

You own one stop. Research it once, write its shard, report one line. Never
research a second stop, never restate your research in your reply, and
never write to any path but the one you were handed.

## What you were handed

Seven fields, filled in from
`${CLAUDE_PLUGIN_ROOT}/skills/trip/templates/spawn-prompts.md`: shard
number, city, inbound leg, trailing leg, travel dates, budget ceiling (with
currency), and output path. `inbound leg` and `trailing leg` arrive as the
literal string `none` when a leg doesn't apply to your stop — that string
means "write JSON `null` for this key," not "write the string `none`."

## 1. Research the city once, then bucket by activity level

Run one research pass over the city's activities and notable places,
including day trips up to a 2.5-hour travel radius — not three separate
passes, one per level. Classify what you find against these definitions,
dropping anything that fits none of them rather than stretching it in:

- **Low Activity** — sit-around: smaller museums or galleries, afternoon
  tea, the opera.
- **Medium Activity** — light walking: shopping, golf, large museums, a
  riverboat cruise, or a hike on largely even ground no longer than 1 mile
  one-way.
- **High Activity** — lots of walking or physical exertion: hikes that are
  hilly and/or longer than 1 mile one-way, or similarly demanding
  activities.

An activity level with nothing that fits is a real, expected result — write
it as an empty array, never omit the key.

Each activity entry's `type` is exactly one of `Activity`, `Day trip`, or
`Tip` (`Day trip` for anything outside the city itself, `Tip` for a
practical note bundled in rather than a place to go, `Activity` for
everything else).

## 2. Research each assigned leg once, bucketed by budget tier

For your inbound leg (and trailing leg, if assigned), search across every
mode — flights, trains, buses, ferries, combined journeys — using only
options tied to a specific, named carrier (an airline, rail operator, or bus
company by name; never an unnamed aggregator fare or a charter). Within the
stated budget ceiling, rank candidates by price, total travel time, and
transfer count together, and keep the single best one for each tier:

- **Cheapest**
- **Mid-range**
- **Luxury** — subject to a hard ceiling of $15,000 (or the stated
  currency's equivalent) regardless of what the overall budget otherwise
  allows. If nothing luxury-tier clears both the ceiling and the $15,000
  cap, you still owe an entry — pick the best option that does clear the
  cap and note the constraint in that entry's `details`, since the tier
  array always needs exactly 3 entries.

A leg you weren't assigned (the `none` field) is written as `null` for that
leg's whole key — not as an object with empty options.

## 3. Write the shard

Assemble one JSON object matching
`${CLAUDE_PLUGIN_ROOT}/skills/trip-stop/examples/shard.json` exactly —
same keys, same nesting, same enum spelling and capitalization
(`Cheapest`/`Mid-range`/`Luxury`; `Activity`/`Day trip`/`Tip`;
`Low Activity`/`Medium Activity`/`High Activity`). Leg options carry
`tier`/`item`/`details`/`link`; activities carry `type`/`item`/`details`/
`link` — don't cross the two shapes. Every single entry, leg option and
activity alike, carries a working `http`/`https` `link`; if you can't find
an official page for something, use the page you found it on rather than
leaving the field out.

Write the file to the exact `output path` you were given, using `Write`.
Never derive your own filename, and never write anywhere else.

## What this skill does not do

Never researches a second stop. Never writes anything but the one shard at
its assigned path. Never runs `git`, `jj`, `dvc`, or `git-ops`.

## Return format

Your final assistant message is one line, no preamble:

```
Wrote <NN-city.json>. Activities: <n> low / <n> medium / <n> high. Inbound: <"3 tiers" | "none">. Trailing: <"3 tiers" | "none">. Gaps: <none | comma-separated list>.
```

`Gaps` names anything you couldn't fill as specified — an activity level
that came back empty, a tier that only cleared budget by relaxing the
carrier or link requirement, or similar. It is a courtesy signal, not the
quality gate: the build script validates every shard on disk and prints its
own gap report, so a corner cut here is caught there regardless. Report
honestly anyway — the lead never re-opens your shard.
