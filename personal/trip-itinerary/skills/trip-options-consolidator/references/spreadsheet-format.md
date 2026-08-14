# Spreadsheet format

`scripts/build_itinerary.py` already applies all of this — you shouldn't
need to read this file to run the skill. Read it if you're modifying the
script, or if she asks why the sheet looks the way it does.

## The two formats are one format

The script builds either an Excel workbook (`--format excel`, the default)
or a self-contained web page to publish as a Claude artifact (`--format
artifact`). They are the same sheet: same six columns, same widths, same
tabs, same section headers, same colors, same vertical rules. Both are
built by walking the same flattened row list, so a change to the layout
below lands in both at once — never style one of them separately.

The web page differs only where a browser has no equivalent of a workbook:
the tabs are buttons across the top rather than sheet tabs, and the Link
column is clickable rather than showing a bare address. It commits to the
light look above in both light and dark browsers, because it is a
reproduction of a spreadsheet.

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

**Stop | Type | Item | Budget, Cost, Transfers | Details | Link**

- `Type` is one of `City`, `Activity`, `Tip`, `Day trip`, or `Travel`.
- `Budget, Cost, Transfers` is blank for every row except `Travel` rows.
  On those it stacks three short lines in the one cell — the tier
  (`Cheapest`, `Mid-range`, `Luxury`), then what the journey costs, then
  `Nonstop` or the number of transfers:

  ```
  Mid-range      <- underlined
  $565
  Nonstop
  ```

  So a leg can be compared straight down the column — tier against price
  against changes — without reading across into Details. Any of the three
  that is genuinely unknown is left out rather than shown blank. Column D
  wraps, like column E.

  **The tier word is underlined; the cost and the transfers are not.** In
  the workbook that is a rich-text cell — one underlined run followed by a
  plain one, which is why the budget cell is built as its own value rather
  than a plain string. On the web page it is a `<u>` on the first line.
  Nothing else in the column is underlined, and no other column uses
  underline at all.

## The luxury ceiling

Luxury travel is capped at $10,000 per leg. That is enforced upstream, in
`transportation-researcher`, and repeated in every luxury spawn prompt, so
nothing above it should ever reach the sheet. A luxury row above $10,000
means the leg was researched wrong — it gets dropped and re-spawned, not
formatted.

## One travel service per row

A `Travel` row is one service — one airline, one train, one bus — named in
`Item`, with its own cost, its own transfer count, its own details and its
own link. A tier is not limited to a single row: if the cheapest way of
making a leg turned up a train, a regional service and a coach, that is
three rows, all three reading `Cheapest` at the top of the budget cell,
and the alternating stripe keeps running down through them. Details cells
never carry two journeys.

The data file expresses this by giving a tier an `options` list instead of
a single `details` string; the script emits one row per element, each
inheriting the tier and falling back to the tier's own `item`, `link`,
`cost` and `connections` when an element doesn't set its own. As a backstop it will also split a details
string that contains newlines or ` | ` separators — but those rows repeat
the tier's `Item`, which is why the merge step is told to name each
service properly rather than rely on the split.

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
`Innsbruck_Salzburg_Vienna_Trip_Itinerary.xlsx`), or the same name ending
`.html` for the artifact page, overwriting a prior file of the same name
if she's re-running this for the same trip. The build script derives this
automatically from the city names in `sequence` if `output_filename` isn't
set in the data file — see `../templates/trip_data.example.json`.
