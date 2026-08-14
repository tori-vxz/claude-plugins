<!--
Copy-ready spawn prompt for a `trip-itinerary:trip-scout` subagent, one per stop.
Fill in every field from what step 3 of `skills/trip/SKILL.md` computed for
that stop, then send all n of these in a single message — never one at a
time. "none" is the literal string to write when a field doesn't apply;
`trip-itinerary:trip-stop` is the one that turns it into JSON `null`, not you.
-->

## Block

```
/trip-itinerary:trip-stop

shard number: <NN>
city: <city name>
inbound leg: <"<from city> to <this city>", or "none">
trailing leg: <"<this city> to <to city>", or "none">
travel dates: <the trip's travel dates>
budget ceiling: <amount and currency>
output path: <the exact absolute shard path from step 3, e.g. <workdir>/NN-city.json>
```

## Filled example

A middle stop, city 2 of an itinerary that began in Busan with no ending
city named:

```
/trip-itinerary:trip-stop

shard number: 02
city: Seoul
inbound leg: Busan to Seoul
trailing leg: none
travel dates: 2026-09-10 to 2026-09-20
budget ceiling: 4000 USD
output path: /tmp/tmp.a1B2c3D4/02-seoul.json
```
