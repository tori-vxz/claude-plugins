# Web Research Plugin

**Status:** Packaged here as an installable Claude Code plugin (`web-research`), sourced from this directory. The same skills also run from `~/.claude/skills/` and `~/.claude/agents/` locally — this directory is the distributable copy.

Three parts working together, chained by whichever agent is leading the session:

1. **`web-crawler`** (skill + agent) names every distinct category of explanation a question could have (e.g., for a "why doesn't X work" question: technical/user-side causes, and business/legal/news causes), spawns one search per category, and keeps rephrasing and re-searching each one until the results stop changing before reporting raw findings back.
2. **`web-consolidator`** (skill + agent) merges multiple `web-crawler` reports into one, keeping every finding tied to which search it came from and flagging any disagreements between categories rather than picking a winner.
3. **`web`** (skill) takes the consolidated findings and writes the final answer — resolving conflicts by source authority (official sources beat unofficial ones), keeping a URL attached to every fact, capped at three pages.

Used by the calendar-assistant and nd-cal-cmc-stmt-builder skills as needed for research tasks, and also available as a direct tool for any other one-off research task. It's thorough by design — expect more searches and a longer run for a fuller answer, rather than a quick shallow sweep.

## Installing it elsewhere

From any Claude Code session:

```
/plugin marketplace add tori-vxz/litigation-skills
/plugin install web-research@litigation-skills
```

## Layout

```
web-research/
  .claude-plugin/plugin.json     — plugin manifest
  skills/web/SKILL.md            — final-answer writer
  skills/web-crawler/SKILL.md    — multi-angle search
  skills/web-consolidator/SKILL.md — merges crawler reports
  agents/web-crawler.md          — web-crawler as a background agent
  agents/web-consolidator.md     — web-consolidator as a background agent
```

The repo-root `.claude-plugin/marketplace.json` lists this directory as the one plugin this repo offers.
