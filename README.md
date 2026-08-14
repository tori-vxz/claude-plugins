# claude-plugins

My space for building and testing Claude Code skills and agents. Split into two unrelated groups that happen to share this repo because it's convenient to install all of them from one URL: legal-practice tooling, and personal projects.

Each plugin is self-contained and separately installable. See `.claude-plugin/marketplace.json` for the install list.

## What's here

- **[`legal/`](legal/)** — legal-practice plugins for state or federal civil litigation.
  - **[`calendar-assistant/`](legal/calendar-assistant/)** — reads an uploaded court order, dispatches three research agents to gather the applicable civil procedure, judge, and local rules, calculates the resulting deadline(s), and writes a calendar file (`.ics`) for each one for the user to import into whatever calendar she uses. Asks whether anyone should be added as a guest before writing events, and takes explicit approval before treating a conflicting existing date as resolved. Never drafts a filing, and never writes to a personal calendar. Bundles its three research agents (civpro-calculator, judge-rules-researcher, local-rules-researcher) inside the plugin.
- **[`personal/`](personal/)** — unrelated personal projects.
  - **[`web-research/`](personal/web-research/)** — a multi-angle web research chain: web-crawler names every plausible category of explanation for a question and re-searches each until results stabilize, web-consolidator merges multiple crawler reports into one, and web writes the final answer, resolving conflicts by source authority and keeping a URL attached to every fact.
  - **[`trip-itinerary/`](personal/trip-itinerary/)** — researches things to do in a city, transportation between cities, and builds a full multi-city itinerary as a spreadsheet and a markdown file.

(The Joint Case Management Statement drafter, nd-cal-cmc-stmt-builder, lives in its own repo: [litigation-skills-projects](https://github.com/tori-vxz/litigation-skills-projects).)

## Installing

```
/plugin marketplace add tori-vxz/claude-plugins
/plugin install calendar-assistant@tori-vxz-plugins
/plugin install web-research@tori-vxz-plugins
/plugin install trip-itinerary@tori-vxz-plugins
```
