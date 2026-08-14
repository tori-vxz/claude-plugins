# build.py usage

`build.py` reads one JSON shard per city from a directory, validates them,
prints a gap report, and — unless a fatal gap was found — renders one
workbook (`.xlsx`) and one markdown file (`.md`) covering the whole trip.

This file also absorbs the whole of the old
`trip-options-consolidator/references/spreadsheet-format.md`: the
colours, widths, border rules, and naming conventions below are the same
format that script used, ported here without redesign.

## CLI

```
build.py <shard-dir> [--out-dir DIR] [--name PREFIX]
```

- `<shard-dir>` — directory containing the `NN-city.json` shard files.
  Required.
- `--out-dir DIR` — directory to write the `.xlsx`/`.md` into. Defaults to
  `<shard-dir>` itself. Created if it doesn't exist.
- `--name PREFIX` — overrides the derived filename stem. Output files are
  named `<PREFIX>_Trip_Itinerary.xlsx` and `<PREFIX>_Trip_Itinerary.md`.
  Without `--name`, the stem is derived from the cities in shard order,
  e.g. shards `01-busan.json`, `02-seoul.json`, `03-incheon.json` produce
  `Busan_Seoul_Incheon_Trip_Itinerary.xlsx`.
- `--help` — argparse-generated usage text.

Exit code is `0` on success (including a run with only warnings) and
non-zero if any fatal gap was found — see below.

## Shard schema

One JSON file per city, named `NN-city.json`: zero-padded two-digit
sequence number starting at `01`, then a hyphen, then the city name
lowercased with every run of non-alphanumeric characters collapsed to a
single `-` (e.g. `01-busan.json`, `02-seoul.json`, `03-incheon.json`).
`build.py` globs `[0-9][0-9]-*.json` in the shard directory and sorts the
matches lexicographically; that sort order is the trip order.

```json
{
  "city": "Seoul",
  "inbound_leg": { "label": "Busan to Seoul", "options": [ {"tier": "...", "item": "...", "details": "...", "link": "..."} ] },
  "trailing_leg": null,
  "activities": {
    "Low Activity":    [ {"type": "...", "item": "...", "details": "...", "link": "..."} ],
    "Medium Activity": [ ],
    "High Activity":   [ ]
  }
}
```

- `inbound_leg` and `trailing_leg` are two separate, optional keys; each
  is `null` when absent, and a missing key is tolerated as equivalent to
  `null`. `inbound_leg` is the leg arriving at this city (normally from
  the previous shard's city, or from a named starting point on shard
  `01`). `trailing_leg` is only meaningful on the *last* shard — it's the
  leg leaving the trip after the final city. A `trailing_leg` on any
  earlier shard is dropped from the built sequence (see Gap report
  below).
- Each leg's `options` array should have exactly 3 entries, one per tier.
- `type` (activity items) ∈ `Activity`, `Day trip`, `Tip`.
- `tier` (travel options) ∈ `Cheapest`, `Mid-range`, `Luxury`.
- Activity level keys are exactly `Low Activity`, `Medium Activity`,
  `High Activity` — three fixed levels, each an array (empty if there's
  nothing at that level for that city).

Note the shard's `type` enum (`Activity`/`Day trip`/`Tip`) is a different
thing from the rendered sheet's `Type` column, which also carries
`Travel` for leg rows — `Travel` is written by the renderer itself, never
present in a shard.

## Gap report

`build.py` never raises `KeyError` on a malformed shard — every check
below is caught, reported, and, for anything short of fatal, patched with
a safe default (empty string / empty list) so rendering can proceed.

**Fatal** (printed under `FATAL`, exit code non-zero, no `.xlsx`/`.md`
written at all):

- No files in `<shard-dir>` match `NN-city.json`.
- A shard file's filename doesn't start with two digits.
- A shard file isn't parseable JSON.
- A shard is missing a usable `city` field (missing, empty, or not a
  string) — without it the shard can't be placed in any tab.

**Warning** (printed under `WARNINGS`, exit code stays `0`, build
continues with the gap visibly patched):

- An activity or travel option missing `link`, or whose `link` doesn't
  start with `http`.
- A leg whose `options` count isn't exactly 3, or whose tiers aren't
  exactly `Cheapest`/`Mid-range`/`Luxury`.
- An activity level key missing or empty for a city.
- A sequence gap: shard numbering not starting at `01`, a missing number,
  or a duplicate number.
- An unknown `type` or `tier` value (kept in the output as given, not
  blanked).
- A `trailing_leg` present on a non-final shard (dropped from the built
  sequence).
- A leg missing `label` (a fallback label is synthesized) or `options`
  (treated as empty).
- Two legs sharing the same `label` (the later one overwrites the earlier
  in the rendered output).
- Two shards sharing the same `city` name (the later shard's activities
  overwrite the earlier one's for that city, and both sequence steps
  render the later shard's data).

## Layout

This is the format the Low Activity tab of `Vancouver_Anchorage_Trip_
Itinerary copy.xlsx` used — matched exactly rather than older, denser
styles seen in earlier itinerary spreadsheets (title/subtitle rows, no
vertical borders, frozen header rows; or no section-header merges, no
vertical borders).

One workbook, one sheet per activity level, named `Low Activity`,
`Medium Activity`, and `High Activity`. No title row, no subtitle row, no
freeze panes. Six columns on every sheet:

**Stop | Type | Item | Budget Tier | Details | Link**

- `Type` is one of `Activity`, `Tip`, `Day trip`, or `Travel` in the
  rendered sheet (see the schema note above on how this differs from a
  shard's own `type` field). The city name itself appears in the section
  header and the Stop column, not as a `Type` value.
- `Budget Tier` is blank for every row except `Travel` rows, where it
  reads `Cheapest`, `Mid-range`, or `Luxury`, so the three options for a
  leg are easy to tell apart at a glance.

The markdown rendering mirrors this: one `##` section per activity level,
one `###` subsection per travel leg or city, each followed by a table
with the same six columns in the same order.

## Column widths

Stop 22, Type 12, Item 42, Budget Tier 12, Details 60, Link 45.

## Colors and fonts

- **Row 1 (column headers)** — solid fill `#404040` (dark gray), font
  white (`#FFFFFF`), bold, size 11.
- **Section-header rows** — one merged row, spanning all six columns
  (A:F) into a single cell, placed directly above every new section:
  above each city's activity block and above each travel block (e.g.
  "Travel: Busan to Seoul"). Solid fill `#1F4E78` (dark blue), font white
  (`#FFFFFF`), bold, size 12.
- **Travel rows** (the individual cheapest/mid-range/luxury line items
  under a travel section-header row) — alternate solid fill between
  `#D9E1F2` (light blue) and `#EAF0FA` (lighter blue), row by row within
  each travel block, restarting the alternation at the first row of each
  new travel section. Font default (automatic black), not bold, size 11.
- **Tip rows** — any row where `Type` is `Tip`, on any tab — solid fill
  `#33CC33` (slightly saturated bright green), across all six columns
  (A-F), font default, not bold, size 11. This overrides the
  ordinary-row stripe below — a Tip row is always green, never striped.
- **Ordinary rows** (`Activity`, `Day trip`) — alternate solid fill
  between `#FFFFFF` (white) and `#F2F2F2` (light gray), row by row within
  each city's activity block, restarting the alternation at the first row
  of each new city section. This is a separate color pair from the
  travel rows' stripe — never reuse the travel blues here. Font default,
  not bold, size 11.
- **Link column (F)** — where a row has a link starting with `http`, the
  cell carries a real openpyxl hyperlink (`cell.hyperlink = url`), with
  hyperlink-styled text (`#0563C1`, underlined) layered on top of —not
  replacing— that row's fill, so the alternating stripe still shows
  through. A missing or non-`http` link is left as a plain cell (that gap
  is what the gap report is for).

## Borders

Thin vertical borders only — no horizontal/top/bottom borders anywhere: a
left border on column A, a right border on column C, and left+right
borders bracketing column E, on every data row. Section-header and
column-header rows follow the same vertical border pattern.

## File naming

Saved as `<Cities>_Trip_Itinerary.xlsx` and `<Cities>_Trip_Itinerary.md`
(e.g. `Busan_Seoul_Incheon_Trip_Itinerary.xlsx`), into `--out-dir` if
given, otherwise into the shard directory itself — overwriting prior
files of the same name if the script is re-run for the same trip.
