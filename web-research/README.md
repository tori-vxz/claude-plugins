# Web Research Skill

**Status:** Available from Claude Code local skills library (`~/.claude/skills/web`, `web-crawler`, `web-consolidator`).

There are now two ways to run web research from this system: the local skill chain this repo was built on, and an optional third-party plugin. Neither is duplicated here — both run from your local Claude Code environment where they're installed. This page explains what each one is and which to reach for.

## Option A: the local skill chain (default)

Three skills working together, chained by whichever agent is leading the session:

1. **`web-crawler`** names every distinct category of explanation a question could have (e.g., for a "why doesn't X work" question: technical/user-side causes, and business/legal/news causes), spawns one search per category, and keeps rephrasing and re-searching each one until the results stop changing before reporting raw findings back.
2. **`web-consolidator`** merges multiple `web-crawler` reports into one, keeping every finding tied to which search it came from and flagging any disagreements between categories rather than picking a winner.
3. **`web`** takes the consolidated findings and writes the final answer — resolving conflicts by source authority (official sources beat unofficial ones), keeping a URL attached to every fact, capped at three pages.

This is used by the calendar-assistant and nd-cal-cmc-stmt-builder skills as needed for research tasks, and is also available as a direct tool for any other one-off research task. It's thorough by design — expect more searches and a longer run for a fuller answer.

## Option B: the `web` plugin (third party, optional)

A separate, single-command alternative from `github.com/taliskerpruighe/web-plugin`, installed via `/plugin install web@web-plugin`. Invoked as `/web:web <question>`, or headless (no interactive session, for scripted/unattended runs) as:

```
claude -p --agent web:web-main "/web:web <question>"
```

It runs the same shape of pipeline — search, fetch, consolidate, answer — but leaner: at most 3 fixed search queries with no rephrasing, page-fetching handled by a script rather than a model (so page content never reaches a model until the final write-up), and a dedicated headless lead agent that can't ask clarifying questions, so an unattended run can't stall waiting on a person. It's faster and cheaper per run, but shallower — fewer searches, no built-in "keep going until results stabilize" bar.

**Rule of thumb:** use the local chain (Option A) for anything going into a filing or a client deliverable, where thoroughness matters more than speed. Reach for the plugin (Option B) for a quick unattended or scripted lookup where a leaner sweep is good enough.

See `examples/chorki-com-video-playback.md` for a side-by-side run of both on the same question — they landed on the same core answer, but the local chain surfaced more supporting detail.
