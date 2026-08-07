# litigation-skills

My space for building and testing Claude Code skills and agents. Not a single coordinated product — the folders here are separate, unrelated projects that happen to share this repo because it's convenient to install both from one URL. What ties them together is just that: this is where I mess around with Claude.

Each folder is its own self-contained, separately installable plugin. See `.claude-plugin/marketplace.json` for the install list.

## What's here

- **[`litigation/`](litigation/)** — a coordinated set of skills and agents for legal practice in the U.S. District Court for the Northern District of California: case-management deadlines, Joint Case Management Statement drafting, and civil-procedure rule research. See its own [README](litigation/README.md) for the full picture.
- **[`trip-itinerary/`](trip-itinerary/)** — a personal trip-planning skill set: researches things to do in a city, transportation between cities, and builds a full multi-city itinerary as a spreadsheet. See its own [README](trip-itinerary/README.md).

## Installing

```
/plugin marketplace add tori-vxz/litigation-skills
/plugin install web-research@litigation-skills      # from litigation/
/plugin install trip-itinerary@litigation-skills
```
