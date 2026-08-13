# Calendar Assistant Plugin

Reads an uploaded court order, works out what deadlines it creates, and writes a calendar file for each one for you to import yourself.

## What it does

1. **`civpro-calculator`** reads the order and researches the applicable federal or state rules of civil procedure, always including the time-computation rule — Fed. R. Civ. P. 6 or the state equivalent — and the federal and state legal holiday dates for the years the deadlines touch.
2. **`judge-rules-researcher`** researches the judge's individual civil rules or standing order.
3. **`local-rules-researcher`** researches the court's local rules.
4. **`calendar-assistant`** (skill) runs all three at once, calculates every resulting deadline from the consolidated rules, rolls each date off any Saturday, Sunday, or legal holiday under Rule 6(a)(1)(C) or the state equivalent, and writes one `.ics` file per deadline. You import each file into whatever calendar you use — nothing is connected or written automatically.

Every event records both the raw computed date and the final rolled date, along with the rule that moved it, so you can check the count instead of taking it on trust. A date the order states outright is never silently moved — if it falls on a weekend or a holiday you are told, and the call is yours.

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
  agents/civpro-calculator.md                — researches civil procedure rules
  agents/judge-rules-researcher.md           — researches the judge's standing order
  agents/local-rules-researcher.md           — researches the court's local rules
  skills/calendar-assistant/
    SKILL.md                                 — the procedure, start to finish
    scripts/roll_date.py                     — does the counting under Rule 6(a) and 6(d)
    templates/deadline.ics                   — the calendar event
    templates/calculation-worksheet.md       — how each date was reached
    references/rule-6-counting.md            — the counting traps, read before calculating
    references/holiday-research.md           — establishing the holiday list
    references/ics-format.md                 — writing the calendar file
```

### The date arithmetic is a script, not a guess

`scripts/roll_date.py` does the counting, so it comes out identical every
time. It knows Rule 6(a)(1) counting, the weekend and holiday roll in both
directions, the Rule 6(a)(6)(C) limit that state holidays only count on
forward-measured periods, Rule 6(d) added days in the right order, and Rule
6(a)(3) clerk inaccessibility. Federal holidays are generated from
5 U.S.C. § 6103 including the weekend-observance shift; state holidays are
passed in from the research, never assumed.

You can run it yourself to check any date:

```
python3 ~/claude-plugins/legal/calendar-assistant/skills/calendar-assistant/scripts/roll_date.py \
    --trigger 2026-03-02 --days 30 --service-days 3
```

It prints every step it took and reminds you that it counts only — it does not
decide which rule applies or how long the period is.
