# Litigation Skills System

A coordinated set of Claude AI skills and agents built for legal practice in the U.S. District Court for the Northern District of California.

**Repo layout:** this repo hosts two unrelated, separately installable plugins, each in its own top-level folder — [`litigation/`](litigation/) (this system, described below) and [`trip-itinerary/`](trip-itinerary/) (a personal trip-planning skill, unrelated to litigation work). Both install from this same repo/URL; see `.claude-plugin/marketplace.json` for the full list.

## Overview

This system enables lawyers to automate three core litigation workflows:

1. **Case Management & Deadlines** — Upload a court order and get an intelligent calendar event created on the correct matter calendar, with all applicable deadlines calculated and verified against local and judge-specific rules.
2. **Civil Case Management Statements** — Draft plaintiff-side Joint Case Management Statements (CMSs/JCMSs) in the exact format required by N.D. Cal., populated from the complaint and judge's standing order, with defense-counsel placeholders clearly marked.
3. **Deadline Research & Verification** — Research applicable federal and state rules of civil procedure, judge-specific standing orders, and court local rules for any order or deadline, without making the calculation itself—leaving that to the attorney.

## The Skills & Agents

All six components work together. Three can be invoked directly by name (the "skills"); three are research subagents that run in the background as needed (the "agents").

### Direct-use skills:

**calendar-assistant**  
Watches for uploads of court orders. Extracts the matter number and deadline, dispatches three research agents to gather the applicable civil procedure rules, calculates the deadline, and creates a calendar event on the correct matter calendar with both the judge's calendar and internal matter tracking built in. Takes user approval before modifying existing calendar events. Never drafts anything.

**nd-cal-cmc-stmt-builder**  
Given a complaint and the assigned judge, drafts a plaintiff-side Joint Case Management Statement in the exact format required by N.D. Cal. (Civil L.R. 16-9), with the complaint facts and the judge's standing-order deviations built in, and with defense-counsel positions clearly bracketed so opposing counsel can complete the joint filing. Uses the Rule 26(f) Scheduling Protocol to propose class-certification briefing and trial dates, and optionally creates calendar events for each accepted deadline.

**web**  
A general-purpose research skill that runs multi-angle searches on a legal question and returns one synthesized summary—used by the other agents as needed, and available as a direct tool for any other research task.

### Research subagents (usually invoked automatically):

**civpro-calculator**  
Given a court order, identifies the court and state, then researches the current rules of civil procedure that could govern any deadline in that order. Reports the applicable rule numbers and verbatim text; does not calculate the deadline itself.

**judge-rules-researcher**  
Given a judge's name, searches for and reports that judge's current individual civil rules / standing order—direct from the court's website or the judge's own page, with version dates confirmed.

**local-rules-researcher**  
Given a court name, searches for and reports that court's current, in-effect local rules—with amendments and effective dates confirmed.

## How It Works in Practice

**Workflow 1: Calendar a deadline**

1. Upload a court order → the calendar-assistant asks for your matter number.
2. Behind the scenes, civpro-calculator reads the order and identifies the court and any deadlines. Judge-rules-researcher and local-rules-researcher fetch that judge's standing order and the court's local rules.
3. Calendar-assistant calculates the deadline(s), checks your matter calendar for conflicts, and proposes a calendar event.
4. You approve → the event is created on the correct matter calendar.

**Workflow 2: Draft a CMS**

1. Upload a complaint and name the assigned judge → the nd-cal-cmc-stmt-builder skill starts.
2. It extracts the caption, parties, jurisdiction, and relief from the complaint. Judge-rules-researcher fetches the judge's standing order to spot any deviations from the district baseline.
3. The skill drafts the plaintiff-side Joint CMS in the required format, with defense-counsel positions clearly bracketed for opposing counsel to complete.
4. It proposes class-certification and trial dates using the firm's Rule 26(f) scheduling protocol, with optional calendar-event creation.
5. You review and send to opposing counsel for completion of their portions.

**Workflow 3: Research rules for a deadline**

1. Upload an order → civpro-calculator identifies the court and delivers the applicable rules of civil procedure.
2. Judge-rules-researcher and local-rules-researcher fetch any judge-specific or court-specific deviations.
3. You get a sourced, organized report of the rules; you do the deadline math yourself.

## Technical Details

- **Built in Claude** — these are skills and agents created in Claude.ai, not software libraries.
- **N.D. Cal. focused** — the CMS skill is tailored to N.D. Cal. standing orders, local rules (Civil L.R. 16-9, L.R. 7-2, etc.), and the Rule 26(f) Scheduling Protocol used by this firm; the calendar-assistant and research agents are general enough to apply to other federal and state courts.
- **No drafting beyond CMS** — the research agents never write or draft anything; the calendar-assistant never drafts; only the nd-cal-cmc-stmt-builder drafts court filings.
- **Integration ready** — each skill and agent is scoped to be handed off to a main workflow (via subagent dispatch or direct invocation), or used independently for one-off research tasks.

## Verification

Each skill and agent includes:
- A clear description of its scope (what it does, what it does NOT do)
- Operating instructions for when and how to invoke it
- Memory persistence across sessions, so context from prior cases builds up
- Background-execution capability for research subagents, keeping raw search noise out of the main conversation

See each skill's or agent's own SKILL.md or AGENT.md file for full operating instructions and use cases.

---

**Questions?** This system was built to demonstrate hands-on fluency with AI-assisted legal workflows—both the capabilities and the careful scoping needed to keep AI outputs appropriate for court filings. For questions about use, scope, or deployment in a new setting, contact the builder.
