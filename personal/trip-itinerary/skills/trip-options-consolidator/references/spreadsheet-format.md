# Spreadsheet format

`scripts/build_itinerary.py` already applies all of this — you shouldn't
need to read this file to run the skill. Read it if you're modifying the
script, or if she asks why the sheet looks the way it does.

## Provenance

This is the format the Low Activity tab of `Vancouver_Anchorage_Trip_
Itinerary copy.xlsx` used — matched exactly rather than the older, denser
style (title/subtitle rows, no vertical borders, frozen header rows) used
in earlier files like `Innsbruck_Salzburg_Vienna_Trip_Itinerary.xlsx`, and
rather than the plainer style (no section-header merges, no vertical
borders) used in the non-`copy` version of `Vancouver_Anchorage_Trip_
Itinerary.xlsx`.

## Layout

One workbook, one sheet per activity level, named `Low Activity`, `Medium
Activity`, and `High Activity`. No title row, no subtitle row, no freeze
panes. Six columns on every sheet:

**Stop | Type | Item | Budget Tier | Details | Link**

- `Type` is one of `City`, `Activity`, `Tip`, `Day trip`, or `Travel`.
- `Budget Tier` is blank for every row except `Travel` rows, where it
  reads `Cheapest`, `Mid-range`, or `Luxury`, so the three options for a
  leg are easy to tell apart at a glance.

## Column widths

Stop 22, Type 12, Item 42, Budget Tier 12, Details 60, Link 45.

## Colors and fonts

- **Row 1 (column headers)** — solid fill `#404040` (dark gray), font
  white (`#FFFFFF`), bold, size 11.
- **Section-header rows** — one merged row, spanning all six columns
  (A:F) into a single cell, placed directly above every new section:
  above each city's activity block and above each travel block (e.g.
  "Travel: Vancouver to Anchorage"). Solid fill `#1F4E78` (dark blue),
  font white (`#FFFFFF`), bold, size 12.
- **Travel rows** (the individual cheapest/mid-range/luxury line items
  under a travel section-header row) — alternate solid fill between
  `#D9E1F2` (light blue) and `#EAF0FA` (lighter blue), row by row within
  each travel block, restarting the alternation at the first row of each
  new travel section. Font default (automatic black), not bold, size 11.
- **Tip rows** — any row where `Type` is `Tip`, on any tab — solid fill
  `#33CC33` (slightly saturated bright green), across all six columns
  (A–F), font default, not bold, size 11. This overrides the ordinary-row
  stripe below — a Tip row is always green, never striped.
- **Ordinary rows** (`Activity`, `Day trip`) — alternate solid fill
  between `#FFFFFF` (white) and `#F2F2F2` (light gray), row by row within
  each city's activity block, restarting the alternation at the first row
  of each new city section. This is a separate color pair from the travel
  rows' stripe — never reuse the travel blues here. Font default, not
  bold, size 11.

## Borders

Thin vertical borders only — no horizontal/top/bottom borders anywhere: a
left border on column A, a right border on column C, and left+right
borders bracketing column E, on every data row. Section-header and
column-header rows follow the same vertical border pattern.

## File naming

Saved into the project folder as `<Cities>_Trip_Itinerary.xlsx` (e.g.
`Innsbruck_Salzburg_Vienna_Trip_Itinerary.xlsx`), overwriting a prior file
of the same name if she's re-running this for the same trip. The build
script derives this automatically from the city names in `sequence` if
`output_filename` isn't set in the data file — see
`../templates/trip_data.example.json`.
