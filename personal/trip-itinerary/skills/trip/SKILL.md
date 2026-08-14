---
name: trip
description: Given an ordered list of cities, travel dates, and a budget
  ceiling, builds a complete trip itinerary — activities at all three
  activity levels (low, medium, high) and travel options at all three
  budget tiers (cheapest, mid-range, luxury) for every leg between stops —
  and delivers it as a spreadsheet plus a markdown file. Use when the user
  wants a full, end-to-end trip plan spanning multiple cities, covering both
  what to do at each stop and how to travel between them. Also accepts an
  optional beginning city (a leg before city 1) and an optional ending city
  (a leg after the last city). Do NOT use it for a single city's activities
  alone with no travel between stops, and do NOT use it for one
  point-to-point transportation lookup with no itinerary attached — those
  are different skills' work. Never invoked directly by a subagent; a
  subagent that researches one stop runs `trip-itinerary:trip-stop` instead.
effort: xhigh
user-invocable: true
---

# trip

You are the lead. Establish the trip's shape, farm out the research one stop
at a time, then assemble it into a workbook. You never do the travel or
activity research yourself, and you never read a shard back once a scout has
written it — that would repeat work you already paid a subagent to do.

## 1. Establish the inputs, in one round

You need five things: **cities in trip order**, **travel dates**, **budget
ceiling and its currency**, and the two optional extras, **beginning city**
and **ending city**.

This skill has no guaranteed interactive caller. When it runs under
`trip-itinerary:trip-main`, there is no `AskUserQuestion` tool available at all — a
skill body that waits on a question nobody can answer hangs forever instead
of failing. So resolve inputs in this order, every time:

1. **Parse the invocation string first.** Pull cities, dates, budget
   ceiling + currency, and any named beginning/ending city directly out of
   what you were given.
2. **If cities, dates, or budget ceiling is still missing, and
   `AskUserQuestion` is available to you, ask for every missing field in one
   round** — not one question per field, one round covering all of them.
   Beginning city and ending city are never grounds for a question; leave
   either unset if it wasn't named.
3. **If cities, dates, or budget ceiling is still missing, and
   `AskUserQuestion` is not available, fail loudly and stop.** Name the
   exact missing field(s) in your reply (e.g. "missing: travel dates,
   budget ceiling") and do not spawn anything. Guessing a date or a budget
   produces research nobody asked for; silently hanging produces nothing at
   all. Neither is acceptable.

## 2. Create the work directory

Run `mktemp -d` through `Bash` and hold onto the path — every shard this run
produces lands there, and it's what you pass to `build.py` in step 5.

## 3. Assign stops

A **stop** is one city plus the travel leg that arrives at it. Number the
itinerary cities 1..n in the trip order given — the beginning and ending
cities, if named, are legs only and never get a stop, a shard, or activity
research of their own.

For each itinerary city, record:

- **Shard number** — two digits, zero-padded, starting at `01`, in trip
  order.
- **City name** — as given.
- **Inbound leg** — the leg arriving at this city. For city 1: the leg from
  the named beginning city, if one was given, otherwise no inbound leg at
  all. For every city after the first: the leg from the previous itinerary
  city.
- **Trailing leg** — only the *last* itinerary city carries one, and only if
  an ending city was named. Every other city has none.
- **Exact output shard path** — `<workdir>/NN-city.json`, built with the
  filename rule below. Compute this path yourself and hand it to the scout
  whole; a scout that re-derives its own filename is a second place this
  rule can drift from the parser it has to match.

**Shard filename rule (verbatim — the build script parses against this
exactly):** `NN-city.json` — zero-padded two digits from `01`, city
lowercased, non-alphanumerics collapsed to `-`. So Seoul as the second stop
is `02-seoul.json`; "New York" as the fourth stop is `04-new-york.json`.

## 4. Spawn all n scouts in one message

One `trip-itinerary:trip-scout` subagent per stop, all spawned together — no nesting,
no second tier of spawns, and never more than one scout per stop.

Every spawn prompt opens with `/trip-itinerary:trip-stop` on line 1, a blank line,
then the stop's fields. The exact block, with a filled example, lives in
`${CLAUDE_PLUGIN_ROOT}/skills/trip/templates/spawn-prompts.md` — read it and
fill it in per stop rather than reconstructing the format from this
description.

Each scout returns a one-line summary that names, among other things, any
gap it hit (an empty activity level, a tier it couldn't fill under budget).
Keep those lines to hand, but they are not the gap report — the gap report
is `build.py`'s own, produced in step 5. Do not open or read the shard file
itself; the scout already wrote it to the exact path you assigned.

## 5. Build the workbook

Once every scout has returned, run through `Bash`, using the literal
variable shown — not an absolute path, since `${CLAUDE_PLUGIN_ROOT}` is the
only form that resolves correctly regardless of where this run started:

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/trip/scripts/build.py" <workdir> --out-dir <cwd>
```

## 6. Report and stop

`build.py` prints the gap report on stdout in step 5 — it validates the
shards you never read, so it, not the scouts' self-reporting, is the quality
gate. Relay that report verbatim if it names anything, adding any scout
summary gap it did not already cover. Name the
two files `build.py` produced (the `.xlsx` workbook and the markdown file)
and stop there. Do not restate the itinerary content back — you never read
the shards, so you have nothing to restate that isn't already in the two
files you just named.
