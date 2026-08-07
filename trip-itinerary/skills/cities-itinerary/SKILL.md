---
name: cities-itinerary
description: Given a list of cities, spawns one city-researcher subagent per
  city, in parallel, to find vacation activities within a 2.5 hour radius of
  each one. Use when the user names two or more cities and wants ideas for
  what to do at or near each of them. Do NOT use it for a single city with
  no comparison needed — city-researcher alone covers that — and do NOT use
  it for transportation between the cities, which is transportation-researcher.
effort: medium
user-invocable: true
---

Take the cities she names. If she has not said what activity level she
wants — low, medium, or high — ask her before spawning anything; every
city-researcher call needs the same answer, so get it once up front rather
than per city.

Spawn one subagent per named city, all in the same message so they run at
once. Each spawn prompt opens with `/city-researcher` on its own line, a
blank line, then the city and the activity level:

```
/city-researcher

city: <city name>
activity level: <low, medium, or high>
```

The 2.5 hour radius and the day-trip framing are already part of what
city-researcher does — do not repeat them in the prompt, and do not add
anything else to it.

One skill per spawn: nothing else runs alongside city-researcher in these
subagents. Everything each one needs is in its own prompt — a subagent
starts fresh and cannot ask a follow-up question, so if she gave a
constraint (a season, a budget, an interest), put it in every prompt, not
just the first.

Once every subagent has returned, read through what came back and give her
the answer directly in plain English, city by city. Each city-researcher
result includes an official website link for every activity it reports —
keep that link with its activity when you report back; don't summarize an
activity down to its name and description alone. Nothing gets written to
a file — this skill produces an answer for the conversation, not a
document.
