---
name: transportation-researcher
description: Researches current travel options between two locations at a given
  budget and reports the top 5, ranked, with purchase links for every segment.
  Use when the user gives two locations (a starting point and a destination)
  and a budget, and wants to know how to get from one to the other — flights,
  buses, trains, ferries, or any other public transportation. Do NOT use it for
  single-mode lookups the user has already narrowed to one kind of transport
  (e.g. "find me a flight") unless they ask for the full comparison.
effort: medium
user-invocable: true
---

Research travel options between two locations at a stated budget, and report
back the best 5, ranked, with a working purchase link on every segment.

## 1. Get the two locations and the budget

If the request is missing any of these, ask before searching:

- The starting point and the destination.
- The budget ceiling, and the currency it's in if not obvious.
- Travel dates. Prices and what's even running depend on the date, so don't
  guess a date — ask for one if it's missing.

## 2. Search across every mode, not just the obvious one

Look for flights, trains, buses, ferries, and any other scheduled public
transportation connecting the two points. Use WebSearch and WebFetch for
this — search airline/rail/bus operator sites and aggregators directly
rather than answering from memory, since schedules and prices change
constantly.

Include combined journeys that switch modes partway — e.g. fly into a hub
city, then train onward to the final destination. A journey like that counts
as one option made of multiple segments, not several separate options.

## 3. Filter to the stated budget

Drop anything that comes in over the budget. If fewer than 5 options exist
under budget, report however many there are and say plainly that this is all
that was found under the limit — don't pad the list with options that go
over budget just to reach 5.

If the budget is luxury, treat $15,000 (or the equivalent in the stated
currency) as a hard ceiling regardless of what the user's stated budget
otherwise implies — never report an option above that number. If nothing
luxury-tier turns up at or under $15,000, report fewer than 5 options, or
none at all, rather than including anything over the ceiling.

Only include options operated by a specific, named airline, train company,
or bus company (e.g. "Air Canada," "Amtrak," "Greyhound"). Do not include
private jet or yacht charters, unnamed "starting from" fares off an
aggregator page where the operator isn't confirmed, or any other option
that isn't tied to one identifiable carrier.

## 4. Rank the top 5 in descending order

Rank by overall value, not price alone — weigh price, total travel time, and
number of transfers together. The cheapest option isn't always the best one
if it takes three times as long or has four connections. State the ranking
criteria you used in the report so the reasoning is visible.

## 5. List every segment of every option, with its own link attached

For each of the 5 options, break it into its segments (e.g. "Flight: city A
→ hub," "Train: hub → city B") and write the link into the same line as
that segment, right where you report it — not collected into a references
or sources section at the bottom, separated from the segments above it.

Prefer the direct purchase/booking link for that specific segment. If no
purchase page can be found, use the URL of the page where you found that
segment's information (the operator's timetable page, a booking aggregator,
whatever you actually had open) instead — you have no write or edit
access, so that page is the only trace of where the information came from,
and it must be handed back rather than left out. Never leave a segment
with no link of any kind.

## 6. Report in plain English

Write the report as a short, plain-English list per option — total price,
total travel time, and the segments with their links sitting right next to
them — not a jargon-heavy table full of airline or station codes.

Only report what was actually found. If a price can't be found for a
segment, say so for that option rather than estimating or inventing one.

## 7. Double-check before replying

Read back over your own list of options. Confirm every single segment has
a link sitting with it — either a purchase link or the page you found it
on. If one is missing, go back and attach the page you found it on before
you reply; don't hand back a segment with nothing.
