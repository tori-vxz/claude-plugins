#!/usr/bin/env python3
"""Compute a litigation deadline under Fed. R. Civ. P. 6(a) and 6(d).

This does the counting only. It does not decide which rule applies, how long
the period is, or which direction it runs — those come from the researched
rules and are passed in as arguments.

Federal legal holidays are generated from 5 U.S.C. Sec. 6103, including the
weekend-observance shift. State holidays are NOT built in: pass them with
--state-holiday, taken from the official state source the research turned up.

Usage:

  roll_date.py --trigger 2026-03-02 --days 30
  roll_date.py --trigger 2026-03-02 --days 30 --service-days 3
  roll_date.py --trigger 2026-06-01 --days 14 --direction backward
  roll_date.py --trigger 2026-03-02 --days 30 \
      --state-holiday 2026-03-31 "Cesar Chavez Day" \
      --inaccessible 2026-04-01 "clerk's office closed - flooding"
  roll_date.py --trigger 2026-03-02 --days 30 --json

Exit status is 0 on success, 2 on bad input.
"""

import argparse
import datetime as dt
import json
import sys

WEEKEND = (5, 6)  # Saturday, Sunday


def nth_weekday(year, month, weekday, n):
    """The nth <weekday> of a month. n=-1 means the last one."""
    if n > 0:
        d = dt.date(year, month, 1)
        offset = (weekday - d.weekday()) % 7
        return d + dt.timedelta(days=offset + 7 * (n - 1))
    d = dt.date(year, month, 28)
    while (d + dt.timedelta(days=7)).month == month:
        d += dt.timedelta(days=7)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


def observed(d):
    """5 U.S.C. Sec. 6103(b): a fixed-date holiday on a weekend shifts.

    Saturday is observed the preceding Friday, Sunday the following Monday.
    Rule 6(a)(6)(A) points at "the day set aside by statute for observing"
    the holiday, so the shifted day is the legal holiday.
    """
    if d.weekday() == 5:
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + dt.timedelta(days=1)
    return d


def federal_holidays(year):
    """{date: name} for one calendar year, per 5 U.S.C. Sec. 6103(a)."""
    fixed = [
        (dt.date(year, 1, 1), "New Year's Day"),
        (dt.date(year, 6, 19), "Juneteenth National Independence Day"),
        (dt.date(year, 7, 4), "Independence Day"),
        (dt.date(year, 11, 11), "Veterans Day"),
        (dt.date(year, 12, 25), "Christmas Day"),
    ]
    floating = [
        (nth_weekday(year, 1, 0, 3), "Birthday of Martin Luther King, Jr."),
        (nth_weekday(year, 2, 0, 3), "Washington's Birthday"),
        (nth_weekday(year, 5, 0, -1), "Memorial Day"),
        (nth_weekday(year, 9, 0, 1), "Labor Day"),
        (nth_weekday(year, 10, 0, 2), "Columbus Day"),
        (nth_weekday(year, 11, 3, 4), "Thanksgiving Day"),
    ]
    out = {}
    for d, name in fixed:
        shifted = observed(d)
        label = name if shifted == d else f"{name} (observed)"
        out[shifted] = label
    for d, name in floating:
        out[d] = name
    return out


def holiday_table(years, state_holidays):
    """Federal holidays across the given years, plus the supplied state ones."""
    federal = {}
    for y in years:
        federal.update(federal_holidays(y))
        # New Year's Day of the following year can be observed on Dec 31.
        nyd = observed(dt.date(y + 1, 1, 1))
        if nyd.year == y:
            federal[nyd] = "New Year's Day (observed)"
    return federal, dict(state_holidays)


def is_blocked(d, federal, state, count_state):
    """Return a reason string if d cannot be a last day, else None.

    count_state reflects Rule 6(a)(6)(C): a day declared a holiday by the
    state counts only for periods measured AFTER an event. On a backward-
    counted period, a state-only holiday does not block the last day.
    """
    if d.weekday() == 5:
        return "Saturday"
    if d.weekday() == 6:
        return "Sunday"
    if d in federal:
        return f"legal holiday - {federal[d]}"
    if count_state and d in state:
        return f"state legal holiday - {state[d]} (Rule 6(a)(6)(C))"
    return None


def roll(d, federal, state, count_state, inaccessible, direction, trace, label):
    """Roll d under Rule 6(a)(1)(C), 6(a)(5) and 6(a)(3) until it can stand."""
    step = 1 if direction == "forward" else -1
    guard = 0
    while True:
        guard += 1
        if guard > 400:
            raise RuntimeError("roll did not settle - check the holiday inputs")
        reason = is_blocked(d, federal, state, count_state)
        if reason is None and d in inaccessible:
            reason = f"clerk's office inaccessible - {inaccessible[d]} (Rule 6(a)(3))"
        if reason is None:
            return d
        nxt = d + dt.timedelta(days=step)
        trace.append(f"{label}: {d.isoformat()} is a {reason}; "
                     f"rolls {direction} to {nxt.isoformat()}")
        d = nxt


def parse_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"date must be YYYY-MM-DD, got {s!r}")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Compute a deadline under Fed. R. Civ. P. 6(a) and 6(d).")
    p.add_argument("--trigger", required=True, type=parse_date,
                   help="the triggering date (YYYY-MM-DD). Not counted; "
                        "counting starts the next day, per Rule 6(a)(1)(A).")
    p.add_argument("--days", required=True, type=int,
                   help="length of the period in days, from the governing rule")
    p.add_argument("--direction", choices=("forward", "backward"),
                   default="forward",
                   help="forward for a period measured after an event, "
                        "backward for one measured before it (default forward)")
    p.add_argument("--service-days", type=int, default=0,
                   help="days added under Rule 6(d) or a state equivalent. "
                        "Added AFTER the base period expires under 6(a).")
    p.add_argument("--state-holiday", nargs=2, action="append",
                   metavar=("YYYY-MM-DD", "NAME"), default=[],
                   help="a day declared a holiday by the state where the court "
                        "sits; repeatable")
    p.add_argument("--inaccessible", nargs=2, action="append",
                   metavar=("YYYY-MM-DD", "REASON"), default=[],
                   help="a day the clerk's office was inaccessible under "
                        "Rule 6(a)(3); repeatable")
    p.add_argument("--json", action="store_true",
                   help="emit JSON instead of prose")
    a = p.parse_args(argv)

    if a.days < 0 or a.service_days < 0:
        p.error("--days and --service-days cannot be negative")

    state = {}
    for raw, name in a.state_holiday:
        state[parse_date(raw)] = name
    inaccessible = {}
    for raw, reason in a.inaccessible:
        inaccessible[parse_date(raw)] = reason

    span = 2 + (a.days + a.service_days) // 365
    years = range(a.trigger.year - span, a.trigger.year + span + 1)
    federal, state = holiday_table(years, state)

    # Rule 6(a)(6)(C): state holidays count only for forward-measured periods.
    count_state = a.direction == "forward"
    trace = []
    if state and not count_state:
        trace.append("state holidays ignored: Rule 6(a)(6)(C) applies them "
                     "only to periods measured after an event")

    step = 1 if a.direction == "forward" else -1
    raw = a.trigger + dt.timedelta(days=step * a.days)
    trace.append(f"trigger {a.trigger.isoformat()} is not counted "
                 f"(Rule 6(a)(1)(A)); {a.days} days {a.direction} lands on "
                 f"{raw.isoformat()} ({raw.strftime('%A')})")

    base = roll(raw, federal, state, count_state, inaccessible,
                a.direction, trace, "base period")
    if base == raw:
        trace.append(f"base period: {raw.isoformat()} is a "
                     f"{raw.strftime('%A')} and is not a legal holiday; "
                     f"no roll required")

    final = base
    if a.service_days:
        # Rule 6(d): the added days run after the period expires under 6(a).
        added = base + dt.timedelta(days=step * a.service_days)
        trace.append(f"Rule 6(d): {a.service_days} days added after the base "
                     f"period expires, giving {added.isoformat()} "
                     f"({added.strftime('%A')})")
        final = roll(added, federal, state, count_state, inaccessible,
                     a.direction, trace, "after added days")
        if final == added:
            trace.append(f"after added days: {added.isoformat()} is a "
                         f"{added.strftime('%A')} and is not a legal holiday; "
                         f"no further roll")

    result = {
        "trigger": a.trigger.isoformat(),
        "days": a.days,
        "direction": a.direction,
        "service_days": a.service_days,
        "raw_date": raw.isoformat(),
        "base_after_roll": base.isoformat(),
        "final_date": final.isoformat(),
        "final_weekday": final.strftime("%A"),
        "moved": final != raw,
        "trace": trace,
        "federal_holidays_in_window": {
            d.isoformat(): n for d, n in sorted(federal.items())
            if min(raw, final, a.trigger) - dt.timedelta(days=10)
            <= d <= max(raw, final, a.trigger) + dt.timedelta(days=10)
        },
        "caveat": "Counting only. Confirm the period, direction and rule "
                  "against the researched text before relying on this.",
    }

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        for line in trace:
            print(f"  {line}")
        print()
        print(f"  raw computed date : {raw.isoformat()} ({raw.strftime('%A')})")
        print(f"  FINAL DEADLINE    : {final.isoformat()} "
              f"({final.strftime('%A')})")
        print(f"  moved             : {'yes' if final != raw else 'no'}")
        print()
        print("  Counting only. Confirm the period, direction and rule against")
        print("  the researched text before relying on this.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (argparse.ArgumentTypeError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
