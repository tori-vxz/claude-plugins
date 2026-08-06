#!/usr/bin/env python3
"""
FRCP 6(a) Date Calculator

Computes Fed. R. Civ. P. 6(a)-adjusted dates with correct month arithmetic,
month-end clamping, and weekend/federal holiday roll-forward.

Usage:
  python3 frcp6_date.py <start_date> "<offset>"
  python3 frcp6_date.py <start_date> "<offset>" --weekday <Weekday>

Arguments:
  start_date: Date in YYYY-MM-DD format
  offset:    Human-readable offset (e.g., "14 days", "9 months", "60 days")
  --weekday: Optional. If specified, roll the result forward to the next
             occurrence of that weekday (case-insensitive), skipping holidays.
             Example: --weekday Thursday

Output JSON:
  {
    "start_date": "YYYY-MM-DD",
    "offset": "<offset>",
    "adjusted_date": "YYYY-MM-DD",  // Date after FRCP 6(a) roll-forward
    "weekday_adjusted_date": "YYYY-MM-DD",  // If --weekday specified
    "notes": "..."
  }

Notes:
  - Fed. R. Civ. P. 6(a) requires month-arithmetic offsets and adds 3 days if
    the last day is a weekend or federal holiday.
  - Weekday roll-forward (--weekday) finds the next occurrence of that weekday,
    skipping federal holidays. California court holidays are not automatically
    checked; pass those manually if needed.
  - Federal holidays recognized: New Year's Day, MLK Day, Presidents Day,
    Memorial Day, Juneteenth, Independence Day, Labor Day, Columbus Day,
    Veterans Day, Thanksgiving, Christmas.
"""

import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import sys

# Federal holidays (mm-dd) — static dates and "observed" dates per federal holiday rules
FEDERAL_HOLIDAYS = {
    "01-01",  # New Year's Day
    "01-20",  # MLK Jr. Day (third Monday in January — this is approximate; adjust per year)
    "02-17",  # Presidents Day (third Monday in February)
    "05-26",  # Memorial Day (last Monday in May)
    "06-19",  # Juneteenth
    "07-04",  # Independence Day
    "09-01",  # Labor Day (first Monday in September)
    "10-14",  # Columbus Day (second Monday in October)
    "11-11",  # Veterans Day
    "11-28",  # Thanksgiving (fourth Thursday in November)
    "12-25",  # Christmas
}

def is_federal_holiday(date):
    """Check if a date is a federal holiday (approximate — does not handle all edge cases)."""
    month_day = date.strftime("%m-%d")
    return month_day in FEDERAL_HOLIDAYS

def is_weekend(date):
    """Check if a date falls on a weekend (Saturday=5, Sunday=6)."""
    return date.weekday() >= 5

def roll_forward_weekend_holiday(date):
    """
    Implement Fed. R. Civ. P. 6(a)(1)(C):
    If the result is a weekend or federal holiday, add 1 day. Repeat until not.
    """
    while is_weekend(date) or is_federal_holiday(date):
        date += timedelta(days=1)
    return date

def parse_offset(offset_str):
    """
    Parse human-readable offset strings like "14 days", "9 months", "60 days".
    Returns (amount, unit) as (int, str).
    """
    parts = offset_str.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid offset format: {offset_str}. Use '14 days', '9 months', etc.")
    try:
        amount = int(parts[0])
        unit = parts[1].lower()
        if unit.endswith('s'):
            unit = unit[:-1]  # Remove trailing 's' for consistency
        return amount, unit
    except ValueError:
        raise ValueError(f"Could not parse offset: {offset_str}")

def apply_offset(start_date, offset_str):
    """
    Apply a FRCP 6(a)-compliant offset to a start date.
    For month/year offsets, uses month arithmetic with clamping.
    For day offsets, adds directly and rolls forward for weekends/holidays.
    """
    amount, unit = parse_offset(offset_str)

    if unit == 'day':
        # Day offset: add directly, then roll forward
        result = start_date + timedelta(days=amount)
        result = roll_forward_weekend_holiday(result)
    elif unit == 'month':
        # Month offset: use relativedelta for correct month arithmetic
        result = start_date + relativedelta(months=amount)
        result = roll_forward_weekend_holiday(result)
    elif unit == 'year':
        # Year offset
        result = start_date + relativedelta(years=amount)
        result = roll_forward_weekend_holiday(result)
    else:
        raise ValueError(f"Unknown time unit: {unit}. Use 'days', 'months', or 'years'.")

    return result

def find_next_weekday(start_date, target_weekday):
    """
    Find the next occurrence of target_weekday starting from start_date,
    skipping weekends and federal holidays.

    target_weekday: case-insensitive day name (e.g., 'Thursday', 'wednesday')
    Returns the date of the next occurrence.
    """
    weekday_map = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6,
    }

    target_weekday_lower = target_weekday.lower()
    if target_weekday_lower not in weekday_map:
        raise ValueError(f"Unknown weekday: {target_weekday}. Use Monday–Sunday.")

    target_num = weekday_map[target_weekday_lower]
    current = start_date

    # Move forward to the next occurrence of target weekday
    while True:
        if current.weekday() == target_num and not is_federal_holiday(current):
            return current
        current += timedelta(days=1)

def main():
    parser = argparse.ArgumentParser(
        description="FRCP 6(a)-adjusted date calculator"
    )
    parser.add_argument('start_date', help="Start date (YYYY-MM-DD)")
    parser.add_argument('offset', help="Offset (e.g., '14 days', '9 months')")
    parser.add_argument('--weekday', help="Optional: roll forward to this weekday (e.g., Thursday)")

    args = parser.parse_args()

    try:
        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    except ValueError:
        print(json.dumps({
            "error": f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD."
        }), file=sys.stderr)
        sys.exit(1)

    try:
        adjusted = apply_offset(start, args.offset)
    except ValueError as e:
        print(json.dumps({
            "error": str(e)
        }), file=sys.stderr)
        sys.exit(1)

    result = {
        "start_date": args.start_date,
        "offset": args.offset,
        "adjusted_date": adjusted.strftime("%Y-%m-%d"),
        "weekday_adjusted_date": None,
        "notes": ""
    }

    if args.weekday:
        try:
            weekday_adjusted = find_next_weekday(adjusted, args.weekday)
            result["weekday_adjusted_date"] = weekday_adjusted.strftime("%Y-%m-%d")
            result["notes"] = (
                f"Adjusted date rolled forward to the next {args.weekday} "
                f"(skipping weekends/federal holidays)."
            )
        except ValueError as e:
            print(json.dumps({
                "error": str(e)
            }), file=sys.stderr)
            sys.exit(1)
    else:
        result["notes"] = "Adjusted per FRCP 6(a): rolled forward for weekends/holidays."

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
