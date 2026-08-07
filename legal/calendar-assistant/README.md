# Calendar Assistant Plugin

Reads an uploaded court order, works out what deadlines it creates, and writes a calendar file for each one for you to import yourself.

## What it does

1. **`civpro-calculator`** reads the order and researches the applicable federal or state rules of civil procedure.
2. **`judge-rules-researcher`** researches the judge's individual civil rules or standing order.
3. **`local-rules-researcher`** researches the court's local rules.
4. **`calendar-assistant`** (skill) runs all three at once, calculates every resulting deadline from the consolidated rules, and writes one `.ics` file per deadline. You import each file into whatever calendar you use — nothing is connected or written automatically.

## What it is not

This is a calendaring aid, not a docketing system of record. It does not replace your firm's docketing process or a docketing clerk's review, and it should never be the only check standing between a case and a missed deadline. A missed deadline is malpractice regardless of what this tool calculated — always confirm every deadline it produces against the order itself and your firm's own docketing procedure before relying on it.

Specific limits:

- It never touches a live calendar. It cannot detect a conflicting event on its own — you're asked what's already on the matter's calendar so you can catch conflicts, but that depends on what you tell it.
- It never drafts or writes any filing.
- It never writes to a personal calendar, and it never guesses which matter a deadline belongs to — you name the matter number every time.
- It never adds anyone as a guest on an event unless you name that person, by name, in that session. It does not remember guests from one matter or one event to the next.

## Installing it elsewhere

```
/plugin marketplace add tori-vxz/claude-plugins
/plugin install calendar-assistant@tori-vxz-plugins
```

## Layout

```
calendar-assistant/
  .claude-plugin/plugin.json                 — plugin manifest
  skills/calendar-assistant/SKILL.md         — reads the order, calculates deadlines, writes .ics files
  agents/civpro-calculator.md                — researches civil procedure rules
  agents/judge-rules-researcher.md           — researches the judge's standing order
  agents/local-rules-researcher.md           — researches the court's local rules
```
