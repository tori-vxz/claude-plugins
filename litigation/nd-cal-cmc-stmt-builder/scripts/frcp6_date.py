#!/usr/bin/env python3
"""
frcp6_date.py - Compute a date offset from an anchor date under Fed. R. Civ. P. 6(a),
including the weekend/legal-holiday roll-forward required by Rule 6(a)(1)(C) and the
list of "legal holidays" defined by Rule 6(a)(6)(A)-(B) (which incorporates the federal
holidays set by 5 U.S.C. Sec. 6103, including each holiday's "observed" date when the
nominal date falls on a Saturday or Sunday).

Why a script instead of doing this by eye: calendar-month arithmetic (e.g., "9 months
after March 31") and the weekend/holiday roll-forward both have edge cases (month-end
clamping, a holiday that's itself observed on a shifted day, a roll-forward that crosses
into the next month or year) that are easy to get subtly wrong by hand. This script pins
down the mechanical part so the only judgment calls left for the drafting workflow are
the substantive ones (which candidate month to propose, whether the user accepts it).

Usage:
    python3 frcp6_date.py <anchor-date YYYY-MM-DD> <offset> [--weekday NAME]

Offset is a number followed by "day"/"days" or "month"/"months", e.g.:
    python3 frcp6_date.py 2026-08-13 "9 months"
    python3 frcp6_date.py 2026-08-13 "60 days"

Prints a single JSON object to stdout:
    {
      "anchor_date": "2026-08-13",
      "offset": "9 months",
      "raw_date": "2027-05-13",
      "raw_weekday": "Thursday",
      "adjusted_date": "2027-05-13",
      "adjusted_weekday": "Thursday",
      "adjusted": false,
      "reason": null,
      "note": "Federal legal holidays only ..."
    }

If the raw date lands on a Saturday, Sunday, or federal legal holiday, "adjusted" is
true, "adjusted_date" is the next day that is none of those three, and "reason" names
what pushed it forward (e.g., "Saturday", "Sunday", or the holiday's name).

Optional --weekday NAME (e.g. "Thursday"): use this when a judge's standing order limits
civil motion hearings to one specific day of the week. After computing "adjusted_date" as
above (the earliest day that satisfies the offset/notice period and isn't a weekend or
holiday), this finds the earliest date on or after "adjusted_date" that (a) falls on the
named weekday and (b) is not itself a federal holiday — skipping forward a full week at a
time if a candidate weekday is a holiday, since the constraint is "that weekday specifically,"
not "the next open business day." Adds "weekday_adjusted_date" and
"weekday_adjustment_reason" to the output. This same flag is what you want when walking a
date forward past a calendar conflict one week at a time: pass an anchor of (candidate + 1
day) with an offset of "0 days" and the same --weekday, and it returns the next occurrence of
that weekday after the conflicting one.

Note on Rule 6(a)(6)(C): for periods measured after an event (which is exactly this
script's use case), Rule 6 also treats as a "legal holiday" any day the state where the
district court sits declares a holiday. This script only computes federal holidays --
it does not attempt to track California's separate list of court holidays (e.g.,
certain Judicial Council-observed closures). Always sanity-check the adjusted date
against the current California court holiday calendar before relying on it, and flag
this in the draft the same way the skill flags any other unverified assumption.
"""

import sys
import json
import re
import calendar
import argparse
from datetime import date, timedelta

WEEKDAY_NAMES = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

CA_HOLIDAY_NOTE = (
    "Federal legal holidays only (Fed. R. Civ. P. 6(a)(6)(A)-(B), 5 U.S.C. Sec. 6103). "
    "Rule 6(a)(6)(C) also picks up California-observed court holidays for periods "
    "measured after an event -- confirm none apply before relying on this date."
)


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """weekday: Monday=0 ... Sunday=6. n: 1-indexed occurrence within the month."""
    first_of_month = date(year, month, 1)
    first_weekday = first_of_month.weekday()
    offset = (weekday - first_weekday) % 7
    day = 1 + offset + (n - 1) * 7
    return date(year, month, day)


def last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    last_day_num = calendar.monthrange(year, month)[1]
    last_of_month = date(year, month, last_day_num)
    offset = (last_of_month.weekday() - weekday) % 7
    return last_of_month - timedelta(days=offset)


def observed(fixed_date: date) -> date:
    """5 U.S.C. Sec. 6103(b): if a fixed-date federal holiday falls on Saturday, federal
    employees observe it the preceding Friday; if it falls on Sunday, observe it the
    following Monday. Rule 6(a)(6)(A) tracks the day 'set aside by statute for observing'
    the holiday, i.e. the observed date, not necessarily the nominal calendar date."""
    if fixed_date.weekday() == 5:  # Saturday
        return fixed_date - timedelta(days=1)
    if fixed_date.weekday() == 6:  # Sunday
        return fixed_date + timedelta(days=1)
    return fixed_date


def federal_holidays(year: int) -> dict:
    """Returns {date: name} for federal holidays observed in the given year, per Fed. R.
    Civ. P. 6(a)(6)(A) / 5 U.S.C. Sec. 6103. Floating (Nth-weekday) holidays fall on a
    Monday or Thursday already, so they never need the Saturday/Sunday observed-date shift;
    only the fixed-date holidays do."""
    h = {}
    h[observed(date(year, 1, 1))] = "New Year's Day"
    h[nth_weekday_of_month(year, 1, 0, 3)] = "Martin Luther King Jr.'s Birthday"
    h[nth_weekday_of_month(year, 2, 0, 3)] = "Washington's Birthday"
    h[last_weekday_of_month(year, 5, 0)] = "Memorial Day"
    h[observed(date(year, 6, 19))] = "Juneteenth National Independence Day"
    h[observed(date(year, 7, 4))] = "Independence Day"
    h[nth_weekday_of_month(year, 9, 0, 1)] = "Labor Day"
    h[nth_weekday_of_month(year, 10, 0, 2)] = "Columbus Day"
    h[observed(date(year, 11, 11))] = "Veterans Day"
    h[nth_weekday_of_month(year, 11, 3, 4)] = "Thanksgiving Day"
    h[observed(date(year, 12, 25))] = "Christmas Day"
    return h


def add_months(d: date, n: int) -> date:
    """Calendar-month arithmetic with month-end clamping (e.g., Jan 31 + 1 month -> Feb 28
    in a non-leap year, not an error and not March 3)."""
    total_month_index = d.month - 1 + n
    year = d.year + total_month_index // 12
    month = total_month_index % 12 + 1
    last_day_of_target_month = calendar.monthrange(year, month)[1]
    day = min(d.day, last_day_of_target_month)
    return date(year, month, day)


def roll_forward(d: date):
    """Rule 6(a)(1)(C): if the last day of a period falls on a Saturday, Sunday, or legal
    holiday, the period runs until the next day that is none of those three. Returns
    (adjusted_date, reason_or_None). Loops rather than checking once, since the day after
    a holiday can itself be a weekend day and vice versa."""
    holiday_cache = {}
    cur = d
    reason = None
    while True:
        if cur.year not in holiday_cache:
            holiday_cache[cur.year] = federal_holidays(cur.year)
        if cur.weekday() == 5:
            reason = reason or "Saturday"
            cur = cur + timedelta(days=1)
            continue
        if cur.weekday() == 6:
            reason = reason or "Sunday"
            cur = cur + timedelta(days=1)
            continue
        if cur in holiday_cache[cur.year]:
            reason = reason or holiday_cache[cur.year][cur]
            cur = cur + timedelta(days=1)
            continue
        break
    return cur, reason


def parse_offset(offset_str: str):
    m = re.match(r"^\s*(\d+)\s*(day|days|month|months)\s*$", offset_str, re.IGNORECASE)
    if not m:
        raise ValueError(
            f"Could not parse offset {offset_str!r}. Expected e.g. '9 months' or '60 days'."
        )
    n = int(m.group(1))
    unit = m.group(2).lower()
    return n, ("month" if unit.startswith("month") else "day")


def next_matching_weekday(start: date, weekday: int):
    """Earliest date >= start that falls on `weekday` (Monday=0...Sunday=6) and is not a
    federal holiday. If the first candidate is a holiday, jumps a full week at a time rather
    than to the next business day, since the constraint being satisfied is 'this specific
    weekday,' not 'any open court day.' Returns (date, days_advanced, reason_or_None) where
    reason is set only if a holiday collision forced a jump past the first candidate."""
    days_until = (weekday - start.weekday()) % 7
    candidate = start + timedelta(days=days_until)
    holiday_cache = {}
    reason = None
    while True:
        if candidate.year not in holiday_cache:
            holiday_cache[candidate.year] = federal_holidays(candidate.year)
        if candidate in holiday_cache[candidate.year]:
            reason = holiday_cache[candidate.year][candidate]
            candidate = candidate + timedelta(days=7)
            continue
        break
    return candidate, (candidate - start).days, reason


def main():
    parser = argparse.ArgumentParser(
        description="Compute a date offset under Fed. R. Civ. P. 6(a).",
        add_help=True,
    )
    parser.add_argument("anchor", help="Anchor date, YYYY-MM-DD")
    parser.add_argument("offset", help='e.g. "9 months" or "60 days"')
    parser.add_argument(
        "--weekday",
        default=None,
        help="Align the result to this weekday (e.g. Thursday) after the offset/roll-forward, "
        "for judges whose standing order limits civil motion hearings to one day of the week.",
    )
    args = parser.parse_args()

    try:
        anchor = date.fromisoformat(args.anchor)
    except ValueError:
        print(json.dumps({"error": f"Invalid anchor date {args.anchor!r}; use YYYY-MM-DD."}))
        sys.exit(1)

    try:
        n, unit = parse_offset(args.offset)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    weekday_int = None
    if args.weekday:
        key = args.weekday.strip().lower()
        if key not in WEEKDAY_NAMES:
            print(json.dumps({
                "error": f"Unrecognized --weekday {args.weekday!r}. Use a full or abbreviated "
                         "weekday name, e.g. 'Thursday' or 'Thu'."
            }))
            sys.exit(1)
        weekday_int = WEEKDAY_NAMES[key]

    raw = add_months(anchor, n) if unit == "month" else anchor + timedelta(days=n)
    adjusted, reason = roll_forward(raw)

    result = {
        "anchor_date": anchor.isoformat(),
        "offset": args.offset,
        "raw_date": raw.isoformat(),
        "raw_weekday": raw.strftime("%A"),
        "adjusted_date": adjusted.isoformat(),
        "adjusted_weekday": adjusted.strftime("%A"),
        "adjusted": adjusted != raw,
        "reason": reason,
        "note": CA_HOLIDAY_NOTE,
    }

    if weekday_int is not None:
        weekday_adjusted, days_advanced, weekday_reason = next_matching_weekday(adjusted, weekday_int)
        result["weekday_adjusted_date"] = weekday_adjusted.isoformat()
        result["weekday_adjusted_weekday"] = weekday_adjusted.strftime("%A")
        result["weekday_days_advanced"] = days_advanced
        result["weekday_adjustment_reason"] = weekday_reason

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
