#!/usr/bin/env python3
"""Build the trip itinerary workbook + markdown from per-city shard files.

Usage:
    build.py <shard-dir> [--out-dir DIR] [--name PREFIX]

See scripts/USAGE.md for the shard schema, the gap-report semantics
(which gaps are fatal vs. warnings), and the full rendering-format
reference (colours, widths, borders, naming conventions).
"""

import argparse
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# --- rendering code ported verbatim from
# trip-options-consolidator/scripts/build_itinerary.py --------------------
HEADER_FILL = PatternFill("solid", fgColor="404040")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
SECTION_FILL = PatternFill("solid", fgColor="1F4E78")
SECTION_FONT = Font(color="FFFFFF", bold=True, size=12)
TRAVEL_FILLS = [PatternFill("solid", fgColor="D9E1F2"), PatternFill("solid", fgColor="EAF0FA")]
TIP_FILL = PatternFill("solid", fgColor="33CC33")
ORDINARY_FILLS = [PatternFill("solid", fgColor="FFFFFF"), PatternFill("solid", fgColor="F2F2F2")]
NORMAL_FONT = Font(bold=False, size=11)

THIN = Side(style="thin")
ROW_BORDERS = {
    1: Border(left=THIN),
    2: Border(),
    3: Border(right=THIN),
    4: Border(),
    5: Border(left=THIN, right=THIN),
    6: Border(),
}

COLUMN_WIDTHS = {"A": 22, "B": 12, "C": 42, "D": 12, "E": 60, "F": 45}
HEADERS = ["Stop", "Type", "Item", "Budget Tier", "Details", "Link"]

# Not part of the ported constant list, but needed for the one deliberate
# fix below: real hyperlinks on column F instead of a bare string.
HYPERLINK_FONT = Font(color="0563C1", underline="single", size=11)


def apply_row_borders(ws, row):
    for col, border in ROW_BORDERS.items():
        ws.cell(row=row, column=col).border = border


def write_header_row(ws):
    for col_idx, text in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=text)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    apply_row_borders(ws, 1)


def write_section_header(ws, row, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    for col in range(1, 7):
        cell = ws.cell(row=row, column=col)
        cell.fill = SECTION_FILL
    top_left = ws.cell(row=row, column=1, value=text)
    top_left.font = SECTION_FONT
    top_left.alignment = Alignment(vertical="center")
    apply_row_borders(ws, row)


def write_data_row(ws, row, stop, type_, item, tier, details, link, fill):
    for col_idx, value in enumerate([stop, type_, item, tier, details, link], start=1):
        cell = ws.cell(row=row, column=col_idx, value=value)
        cell.font = NORMAL_FONT
        cell.fill = fill
        cell.alignment = Alignment(vertical="top", wrap_text=(col_idx == 5))
    apply_row_borders(ws, row)
    # Fix while porting: real openpyxl hyperlink on column F, not a bare
    # string. Set link + font by hand (rather than the "Hyperlink" named
    # style) so the row's fill/border set above survive untouched.
    link_cell = ws.cell(row=row, column=6)
    if isinstance(link, str) and link.startswith("http"):
        link_cell.hyperlink = link
        link_cell.font = HYPERLINK_FONT


def write_travel_block(ws, row, label, options):
    write_section_header(ws, row, f"Travel: {label}")
    row += 1
    for i, opt in enumerate(options):
        fill = TRAVEL_FILLS[i % 2]
        write_data_row(ws, row, label, "Travel", opt["item"], opt["tier"], opt["details"], opt["link"], fill)
        row += 1
    return row


def write_city_block(ws, row, city, items):
    write_section_header(ws, row, city)
    row += 1
    ord_i = 0
    for item in items:
        if item["type"] == "Tip":
            fill = TIP_FILL
        else:
            fill = ORDINARY_FILLS[ord_i % 2]
            ord_i += 1
        write_data_row(ws, row, city, item["type"], item["item"], "", item["details"], item["link"], fill)
        row += 1
    return row


def build_sheet(ws, sequence, travel_legs, activities_for_tab):
    write_header_row(ws)
    for col, width in COLUMN_WIDTHS.items():
        ws.column_dimensions[col].width = width
    row = 2
    for step in sequence:
        if step["type"] == "leg":
            row = write_travel_block(ws, row, step["label"], travel_legs[step["label"]])
        elif step["type"] == "city":
            row = write_city_block(ws, row, step["name"], activities_for_tab[step["name"]])
        else:
            raise ValueError(f"Unknown sequence step type: {step['type']!r}")


def build_workbook(data):
    wb = Workbook()
    wb.remove(wb.active)
    sequence = data["sequence"]
    travel_legs = data["travel_legs"]
    for tab_name, activities_for_tab in data["activities"].items():
        ws = wb.create_sheet(tab_name)
        build_sheet(ws, sequence, travel_legs, activities_for_tab)
    return wb


# --- end ported rendering code --------------------------------------------

ACTIVITY_LEVELS = ["Low Activity", "Medium Activity", "High Activity"]
TIERS = ["Cheapest", "Mid-range", "Luxury"]
TYPES = ["Activity", "Day trip", "Tip"]


def load_shards(shard_dir):
    """Glob, sort, and JSON-load shard files.

    Returns (shards, fatals, warnings) where shards is a list of
    (filename, number, raw_dict) tuples in trip order. Any shard that
    can't be parsed or lacks a usable 'city' is excluded from shards and
    recorded as fatal instead.
    """
    fatals = []
    warnings = []
    shard_files = sorted(shard_dir.glob("[0-9][0-9]-*.json"))
    if not shard_files:
        fatals.append(f"no shard files found in {shard_dir} matching NN-city.json")
        return [], fatals, warnings

    shards = []
    numbers = []
    for f in shard_files:
        try:
            num = int(f.name[:2])
        except ValueError:
            fatals.append(f"{f.name}: filename does not start with two digits")
            continue

        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fatals.append(f"{f.name}: invalid JSON ({exc})")
            continue

        if not isinstance(raw, dict) or not isinstance(raw.get("city"), str) or not raw.get("city"):
            fatals.append(f"{f.name}: missing or invalid required 'city' field — shard cannot be placed in any tab")
            continue

        numbers.append(num)
        shards.append((f.name, num, raw))

    if numbers:
        if numbers[0] != 1:
            warnings.append(f"shard numbering does not start at 01 (starts at {numbers[0]:02d})")
        seen = set()
        dupes = set()
        for n in numbers:
            (dupes if n in seen else seen).add(n)
        if dupes:
            warnings.append(f"duplicate shard number(s): {', '.join(f'{n:02d}' for n in sorted(dupes))}")
        expected = set(range(numbers[0], max(numbers) + 1))
        missing = sorted(expected - set(numbers))
        if missing:
            warnings.append(f"sequence gap: missing shard number(s) {', '.join(f'{n:02d}' for n in missing)}")

    return shards, fatals, warnings


def normalize_travel_option(opt, context, warnings):
    if not isinstance(opt, dict):
        warnings.append(f"{context}: travel option is not an object — treated as empty")
        opt = {}
    tier = opt.get("tier")
    if not isinstance(tier, str) or not tier:
        warnings.append(f"{context}: travel option missing 'tier'")
        tier = ""
    elif tier not in TIERS:
        warnings.append(f"{context}: unknown tier value {tier!r}")

    link = opt.get("link")
    if not isinstance(link, str) or not link:
        warnings.append(f"{context} ({tier or 'unknown tier'}): missing link")
        link = ""
    elif not link.startswith("http"):
        warnings.append(f"{context} ({tier or 'unknown tier'}): link does not start with http: {link!r}")

    return {
        "tier": tier,
        "item": opt.get("item") if isinstance(opt.get("item"), str) else "",
        "details": opt.get("details") if isinstance(opt.get("details"), str) else "",
        "link": link,
    }


def normalize_leg(leg, context, warnings):
    """Validate + normalize an inbound_leg/trailing_leg dict.

    Returns (label, options) or (None, None) if the leg is unusable.
    """
    if not isinstance(leg, dict):
        warnings.append(f"{context}: leg is not an object — skipped")
        return None, None

    label = leg.get("label")
    if not isinstance(label, str) or not label:
        label = context
        warnings.append(f"{context}: leg missing 'label' — using fallback label {label!r}")

    raw_options = leg.get("options")
    if not isinstance(raw_options, list):
        warnings.append(f"{context}: leg missing 'options' list — treated as empty")
        raw_options = []

    if len(raw_options) != 3:
        warnings.append(f"{context}: leg has {len(raw_options)} option(s), expected exactly 3")

    options = [normalize_travel_option(o, context, warnings) for o in raw_options]
    tiers_seen = {o["tier"] for o in options}
    if tiers_seen != set(TIERS) and raw_options:
        warnings.append(
            f"{context}: leg tiers are {sorted(t for t in tiers_seen if t)}, expected exactly {TIERS}"
        )

    return label, options


def normalize_activity_item(item, context, warnings):
    if not isinstance(item, dict):
        warnings.append(f"{context}: activity item is not an object — treated as empty")
        item = {}

    type_ = item.get("type")
    if not isinstance(type_, str) or not type_:
        warnings.append(f"{context}: activity item missing 'type'")
        type_ = ""
    elif type_ not in TYPES:
        warnings.append(f"{context}: unknown type value {type_!r}")

    name = item.get("item") if isinstance(item.get("item"), str) else ""
    if not name:
        warnings.append(f"{context}: activity item missing 'item' (name)")

    link = item.get("link")
    if not isinstance(link, str) or not link:
        warnings.append(f"{context} ({name or 'unnamed'}): missing link")
        link = ""
    elif not link.startswith("http"):
        warnings.append(f"{context} ({name or 'unnamed'}): link does not start with http: {link!r}")

    return {
        "type": type_,
        "item": name,
        "details": item.get("details") if isinstance(item.get("details"), str) else "",
        "link": link,
    }


def assemble(shards, warnings):
    """Transpose city-major shards into the level-major shape build_workbook
    expects: {sequence, travel_legs, activities}."""
    sequence = []
    travel_legs = {}
    activities = {level: {} for level in ACTIVITY_LEVELS}
    cities_order = []

    trailing_step = None
    num_shards = len(shards)
    seen_cities = set()

    for idx, (fname, num, raw) in enumerate(shards):
        city = raw["city"]
        if city in seen_cities:
            warnings.append(
                f"{fname}: duplicate city name {city!r} — its activities overwrite the earlier "
                f"shard's for {city!r}, and both sequence steps render the later shard's data"
            )
        seen_cities.add(city)
        cities_order.append(city)
        is_last = idx == num_shards - 1

        inbound = raw.get("inbound_leg")
        if inbound:
            label, options = normalize_leg(inbound, f"{fname} inbound_leg", warnings)
            if label is not None:
                if label in travel_legs:
                    warnings.append(f"{fname}: duplicate leg label {label!r} — overwriting previous entry")
                travel_legs[label] = options
                sequence.append({"type": "leg", "label": label})

        sequence.append({"type": "city", "name": city})

        trailing = raw.get("trailing_leg")
        if trailing:
            if is_last:
                label, options = normalize_leg(trailing, f"{fname} trailing_leg", warnings)
                if label is not None:
                    if label in travel_legs:
                        warnings.append(f"{fname}: duplicate leg label {label!r} — overwriting previous entry")
                    travel_legs[label] = options
                    trailing_step = {"type": "leg", "label": label}
            else:
                warnings.append(
                    f"{fname}: trailing_leg present on a non-final shard — ignored, "
                    "will not appear in the sequence"
                )

        raw_activities = raw.get("activities")
        if not isinstance(raw_activities, dict):
            warnings.append(f"{fname}: missing or invalid 'activities' object — all levels treated as empty")
            raw_activities = {}

        for level in ACTIVITY_LEVELS:
            items = raw_activities.get(level)
            if items is None:
                warnings.append(f"{fname}: activity level {level!r} missing for {city!r}")
                items = []
            elif not isinstance(items, list) or not items:
                warnings.append(f"{fname}: activity level {level!r} is empty for {city!r}")
                items = []
            activities[level][city] = [
                normalize_activity_item(it, f"{fname} {level}", warnings) for it in items
            ]

    if trailing_step is not None:
        sequence.append(trailing_step)

    return {"sequence": sequence, "travel_legs": travel_legs, "activities": activities}, cities_order


def render_markdown(data, path):
    lines = ["# Trip Itinerary", ""]

    def esc(v):
        return str(v).replace("|", "\\|").replace("\n", " ")

    def link_cell(v):
        if isinstance(v, str) and v.startswith("http"):
            return f"[{esc(v)}]({v})"
        return esc(v) if v else ""

    for level, activities_for_tab in data["activities"].items():
        lines.append(f"## {level}")
        lines.append("")
        for step in data["sequence"]:
            if step["type"] == "leg":
                label = step["label"]
                lines.append(f"### Travel: {label}")
                lines.append("")
                lines.append("| Stop | Type | Item | Budget Tier | Details | Link |")
                lines.append("|---|---|---|---|---|---|")
                for opt in data["travel_legs"][label]:
                    lines.append(
                        f"| {esc(label)} | Travel | {esc(opt['item'])} | {esc(opt['tier'])} "
                        f"| {esc(opt['details'])} | {link_cell(opt['link'])} |"
                    )
                lines.append("")
            else:
                city = step["name"]
                lines.append(f"### {city}")
                lines.append("")
                lines.append("| Stop | Type | Item | Budget Tier | Details | Link |")
                lines.append("|---|---|---|---|---|---|")
                for item in activities_for_tab[city]:
                    lines.append(
                        f"| {esc(city)} | {esc(item['type'])} | {esc(item['item'])} | "
                        f"| {esc(item['details'])} | {link_cell(item['link'])} |"
                    )
                lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_gap_report(fatals, warnings):
    print("=== Gap report ===")
    if fatals:
        print(f"FATAL ({len(fatals)}):")
        for f in fatals:
            print(f"  - {f}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    if not fatals and not warnings:
        print("No gaps found.")
    print("===================")


def main():
    parser = argparse.ArgumentParser(
        description="Build the trip itinerary workbook + markdown from per-city shard files.",
    )
    parser.add_argument("shard_dir", type=Path, help="Directory containing NN-city.json shard files")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory (default: shard-dir)")
    parser.add_argument(
        "--name",
        default=None,
        help="Filename prefix (default: derived from city names, e.g. Busan_Seoul_Incheon)",
    )
    args = parser.parse_args()

    shard_dir = args.shard_dir
    if not shard_dir.is_dir():
        print(f"FATAL: {shard_dir} is not a directory")
        sys.exit(1)

    shards, fatals, warnings = load_shards(shard_dir)

    data = None
    cities_order = []
    if not fatals:
        data, cities_order = assemble(shards, warnings)

    print_gap_report(fatals, warnings)

    if fatals:
        sys.exit(1)

    out_dir = args.out_dir or shard_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.name:
        stem = f"{args.name}_Trip_Itinerary"
    elif cities_order:
        stem = f"{'_'.join(cities_order)}_Trip_Itinerary"
    else:
        stem = "Trip_Itinerary"

    xlsx_path = out_dir / f"{stem}.xlsx"
    md_path = out_dir / f"{stem}.md"

    wb = build_workbook(data)
    wb.save(xlsx_path)
    render_markdown(data, md_path)

    print(f"Saved: {xlsx_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
