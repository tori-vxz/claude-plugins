# litigation-skills

My space for building and testing Claude Code skills and agents. Split into two unrelated groups that happen to share this repo because it's convenient to install all of them from one URL: legal-practice tooling, and personal projects.

Each plugin is self-contained and separately installable. See `.claude-plugin/marketplace.json` for the install list.

## What's here

- **[`legal/`](legal/)** — legal-practice plugins for the U.S. District Court for the Northern District of California.
  - **[`calendar-assistant/`](legal/calendar-assistant/)** — reads an uploaded court order, dispatches three research agents to gather the applicable civil procedure, judge, and local rules, calculates the resulting deadline(s), and calendars them on the correct matter calendar through a provider-agnostic calendar connector (Google Calendar, Microsoft 365/Outlook, iCloud, and others). Asks whether anyone should be added as a guest before creating events, and takes explicit approval before changing or deleting any existing event. Never drafts a filing, and never calendars to a personal calendar. Bundles its three research agents (civpro-calculator, judge-rules-researcher, local-rules-researcher) inside the plugin.
- **[`personal/`](personal/)** — unrelated personal projects.
  - **[`web-research/`](personal/web-research/)** — a multi-angle web research chain: web-crawler names every plausible category of explanation for a question and re-searches each until results stabilize, web-consolidator merges multiple crawler reports into one, and web writes the final answer, resolving conflicts by source authority and keeping a URL attached to every fact.
  - **[`trip-itinerary/`](personal/trip-itinerary/)** — researches things to do in a city, transportation between cities, and builds a full multi-city itinerary as a spreadsheet.

(The Joint Case Management Statement drafter, nd-cal-cmc-stmt-builder, lives in its own repo: [litigation-skills-projects](https://github.com/tori-vxz/litigation-skills-projects).)

## Installing

```
/plugin marketplace add tori-vxz/litigation-skills
/plugin install calendar-assistant@litigation-skills
/plugin install web-research@litigation-skills
/plugin install trip-itinerary@litigation-skills
```
