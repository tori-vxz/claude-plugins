# Trip Itinerary Plugin

Unrelated to the litigation skills elsewhere in this repo — a personal trip-planning plugin, kept in its own folder but installed from the same repo/URL.

Give it an ordered list of cities and it produces one itinerary covering all three activity levels (low, medium, high), each showing all three travel budget tiers (cheapest, mid-range, luxury) for every leg, with a link on every activity and every travel option. The deliverable is an `.xlsx` workbook with one tab per activity level, plus the same itinerary as markdown.

## How it is put together

A **stop** is a city plus the travel leg arriving at it. One subagent owns one stop, start to finish, in a single fresh context — the city's activities at all three activity levels in one research pass, and its inbound leg at all three budget tiers. The last city additionally owns the trailing leg to an ending city, if one was named. For `n` cities that is exactly `n` subagents, spawned together, none of them nested.

Each subagent writes one JSON shard to disk and returns a single line. The lead never reads the research prose. A shard is named by trip position (`01-busan.json`, `02-seoul.json`, …) so sorting them lexicographically reconstructs the trip order.

The lead then runs one script over the shard directory. That script validates every shard and prints a shortfall report — missing links, a leg without all three tiers, an empty activity level — which is the quality gate, since nothing else reads the shards. It derives the sequence, renders the workbook and the markdown, and stops.

### Two skills

1. **`trip`** — the door skill and the lead's body: establishes the inputs, assigns the stops, spawns the subagents, runs the build script, relays the report.
2. **`trip-stop`** — the worker skill: research one stop, write one shard, report one line.

### Two agents

1. **`trip-main`** — the lead, for running the whole thing headless with no human present to answer questions:

   ```
   claude -p --agent trip-itinerary:trip-main "/trip-itinerary:trip Busan, Seoul, Incheon. Dates 2026-09-10 to 2026-09-24. Budget USD 2000."
   ```

2. **`trip-scout`** — one spawned per stop, running `trip-stop`.

Interactively, invoke `/trip-itinerary:trip` and answer the one round of questions it asks.

## Requirements

`openpyxl` (see `skills/trip/requirements.txt`) for the workbook. Everything else is standard library.

## Installing it elsewhere

```
/plugin marketplace add tori-vxz/claude-plugins
/plugin install trip-itinerary@tori-vxz-plugins
```
