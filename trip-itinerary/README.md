# Trip Itinerary Plugin

Unrelated to the litigation skills elsewhere in this repo — a personal trip-planning skill, kept in its own folder but installed from the same repo/URL.

Four skills working together:

1. **`city-researcher`** — vacation activities and notable places in one city (including day trips up to 2.5 hours out), filtered to an activity level (low/medium/high), each with a link to its official site.
2. **`cities-itinerary`** — given a list of cities, spawns one `city-researcher` per city in parallel.
3. **`transportation-researcher`** — top 5 ranked ways to get between two locations at a given budget, with a purchase link for every segment.
4. **`trip-options-consolidator`** — the top-level skill: given an ordered list of cities, runs the above across every leg and every combination of activity level and budget tier, and delivers the result as a formatted three-tab spreadsheet or directly in the conversation.

## Installing it elsewhere

```
/plugin marketplace add tori-vxz/litigation-skills
/plugin install trip-itinerary@litigation-skills
```
