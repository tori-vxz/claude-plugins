# Counting a period under Rule 6(a) — working notes

**This file is a checklist, not authority.** It exists so the traps are not
re-derived from memory each time. The text that governs is the verbatim,
current rule `civpro-calculator` fetched for the case in hand. Where this file
and the researched text disagree, the researched text wins, and the
disagreement is worth saying out loud.

## The shape of the federal rule

Rule 6(a) applies to any period stated in the rules, in a local rule, in a
court order, or in a statute that does not specify its own method.

- **6(a)(1)** — periods in days or longer. Exclude the triggering day. Count
  every day after it, including weekends and holidays. Include the last day,
  but if the last day is a Saturday, Sunday, or legal holiday, the period runs
  to the end of the next day that is none of those.
- **6(a)(2)** — periods in hours. Begin immediately. Run continuously through
  weekends and holidays. Only 6(a)(3) stops them.
- **6(a)(3)** — clerk's office inaccessible on the last day: the period runs
  to the first accessible day that is not a Saturday, Sunday, or holiday.
- **6(a)(4)** — when the last day ends: midnight for electronic filing,
  when the clerk's office closes for anything filed on paper.
- **6(a)(5)** — "next day" is found by counting forward for a period measured
  after an event, and backward for one measured before an event.
- **6(a)(6)** — what counts as a legal holiday. See
  `references/holiday-research.md`.
- **6(d)** — three days added after service by certain methods.

## The five traps

**1. Direction changes which way the roll goes.** A period measured *before*
an event — a pretrial filing due 14 days before a hearing — rolls *backward*
off a weekend or holiday. Rolling it forward shortens the period and can miss
the deadline. This is 6(a)(5), and it is the easiest one to get wrong.

**2. State holidays only count forward.** Rule 6(a)(6)(C) makes a state
holiday a legal holiday only "for periods that are measured after an event."
On a backward-counted period, a state-only holiday does not move the date;
a federal holiday and a weekend still do.

**3. Added days come last, not first.** Rule 6(d) adds its three days *after*
the base period has already expired under 6(a) — not to the triggering date.
Compute the period, roll it, then add the days, then roll again if the result
lands badly. Adding first gives a different and wrong answer whenever a
weekend sits inside the difference.

**4. One roll is often not enough.** A holiday observed on a Friday rolls to
Saturday, then Sunday, then Monday. Keep rolling until the day is clear.

**5. Hour-based periods do not roll.** Under 6(a)(2) they run straight
through the weekend. Do not apply the weekend rule to them.

## A date the order states outright

Rule 6(a) governs *computed periods*. A date the judge simply named is not a
computed period. If an ordered date falls on a weekend or a holiday, do not
move it — record it as ordered and flag it, so the user can decide whether to
seek clarification or file early. Moving it silently substitutes our
arithmetic for the court's instruction.

## State courts

The same shape usually holds, but the details vary: some states count only
court days for short periods, some define holidays differently, some add a
different number of days for service, and some have a distinct rule for
periods measured backward. Never assume the federal answer transfers. Use the
state provision `civpro-calculator` returned, and say in the worksheet where
it departs from the federal rule.

## Doing the arithmetic

Do not count by hand or in your head. Run `scripts/roll_date.py`, which
implements the above and prints its reasoning line by line. Its output is what
goes in the worksheet and the event description.
