# Establishing the holiday list

A deadline is only as good as the holiday list behind it. This is the part
most easily got wrong from memory, because the dates move every year and the
state lists are genuinely obscure.

## What Rule 6(a)(6) counts

- **(A)** the day set aside by statute for observing New Year's Day, Martin
  Luther King Jr.'s Birthday, Washington's Birthday, Memorial Day, Juneteenth,
  Independence Day, Labor Day, Columbus Day, Veterans' Day, Thanksgiving, or
  Christmas.
- **(B)** any other day declared a holiday by the President or Congress.
- **(C)** for periods measured *after* an event, any other day declared a
  holiday by the state where the district court sits.

Two things follow. First, (A) points at the day *set aside for observing* the
holiday, so when a fixed-date holiday falls on a weekend, the observed day is
the legal holiday. Second, (C) is one-directional — see
`references/rule-6-counting.md`, trap 2.

## Federal holidays: generated, not researched

`scripts/roll_date.py` generates the federal list from 5 U.S.C. § 6103 for
whatever years the calculation touches, including the weekend-observance
shift (Saturday observed the preceding Friday, Sunday the following Monday).
Do not hand it a federal holiday list; it has one.

Watch the year boundary: when 1 January falls on a Saturday, the observed
holiday is 31 December of the *previous* year. The script handles this, but
it is worth recognising in the output rather than assuming a mistake.

## State holidays: always researched

These are passed in with `--state-holiday`, and they must come from an
official source for the specific years in play — the state's own statute,
the governor's proclamation, or the state court system's published calendar.
Not a general reference site, and never from memory.

Ask `civpro-calculator` for:

- the statutory or official list of that state's legal holidays,
- the specific calendar dates they fall on in each year the deadlines touch,
- the observance rule the state applies when one lands on a weekend,
- the source URL for each.

## The ones that actually bite

Holidays that exist in a state but not federally are the whole reason this
step exists. Examples worth expecting rather than being surprised by: Cesar
Chavez Day (California, 31 March), Patriots' Day (Massachusetts and Maine,
third Monday in April), Emancipation Day (District of Columbia, 16 April —
which also shifts federal tax deadlines), Mardi Gras (parts of Louisiana),
Pioneer Day (Utah, 24 July), Lincoln's Birthday and Election Day (varies).

Treat that list as a prompt for the research, not as the research. It is
neither current nor complete, and states add and drop days.

## Court-specific closures

Beyond 6(a)(6), a particular court may close for its own reasons — weather,
a building problem, a local observance. That is Rule 6(a)(3) territory rather
than a holiday, and it is passed in with `--inaccessible`. Check the court's
own website for closure notices when a deadline lands near one, and say
plainly in the worksheet when this could not be determined.
