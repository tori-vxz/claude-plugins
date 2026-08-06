# ND Cal CMC Stmt Builder — Refactored Skill Structure

This directory contains a refactored, modularized version of the `nd-cal-cmc-stmt-builder` skill for drafting Joint Case Management Statements for the U.S. District Court for the Northern District of California.

## Directory Structure

```
nd-cal-cmc-stmt-builder/
├── SKILL.md                          # Main skill file (entry point)
├── README.md                         # This file
├── scripts/
│   ├── frcp6_date.py                # FRCP 6(a) date calculator (month arithmetic, weekend/holiday roll-forward)
│   └── comment.py                   # Word comment helper (anchoring comments to document text)
├── templates/
│   └── README.md                    # Template directory (reserved for reusable snippets)
└── references/
    ├── standing_order_topics.md      # 19-topic CMS structure, joint vs. split topics, standard language, formatting baseline
    ├── bf_26f_scheduling_protocol.md # 26(f) scheduling rules, class-cert motion dates, notice periods, calendar workflows
    └── example_build_script.js       # Worked example (Selby v. Brand Evangelists for Beauty Inc., 4:26-cv-05924-AMO)
```

## Files Overview

### SKILL.md (Entry Point)

The main skill definition file. It provides:
- Skill trigger conditions and description
- High-level workflow (Steps 1–5)
- References to supporting documents for detailed procedures
- Notes on when to use bracketed placeholders vs. calendar-assisted dates

This file is concise and directs readers to the appropriate supporting reference for detailed guidance.

### scripts/

**frcp6_date.py** — Standalone Python script for computing FRCP 6(a)-adjusted dates.
- Takes a start date and a human-readable offset (e.g., "14 days", "9 months")
- Applies correct month arithmetic with month-end clamping
- Rolls forward for weekends and federal holidays per Fed. R. Civ. P. 6(a)
- Optional `--weekday` flag to find the next occurrence of a specific weekday
- Returns JSON output with adjusted date(s) and explanatory notes

Usage:
```bash
python3 scripts/frcp6_date.py 2026-08-13 "14 days"
python3 scripts/frcp6_date.py 2026-08-13 "9 months" --weekday Thursday
```

**comment.py** — Helper functions for anchoring Word comments to docx elements.
- Placeholder implementation; integrates with docx npm library or python-docx
- Used to annotate service status, jurisdiction, venue, 26(f) protocol dates, etc.

### references/

**standing_order_topics.md** — Comprehensive reference for the 19-topic CMS structure.
- Complete 19-topic list with joint vs. split designation
- Standard language for 13 topics (exact text to use in every draft)
- Topic-specific drafting rules (jurisdiction, venue, relief, class actions, scheduling)
- Formatting baseline: font, spacing, indents, quotation marks, citation style (Bluebook federal)
- Singular/plural rules and judge's initials in case number
- Civil L.R. 16-9(b) class action supplement guidance

**bf_26f_scheduling_protocol.md** — Firm's 26(f) scheduling protocol and calendar workflows.
- Rule 26(f) conference and initial-disclosures baseline (14-day rule)
- Calendar lookup procedure (how to find the 26(f) date from the matter's calendar)
- Class certification motion scheduling rules (9-month motion, 45–60-day opposition, 30–45-day reply)
- Hearing notice period rules (35 calendar days per Civil L.R. 7-2(a), or judge-specific override)
- Calendar-assisted date computation workflow (conditional on calendar tool + real CMC date)
- Table of when to use bracketed placeholders vs. calendar-assisted dates

**example_build_script.js** — Worked example using the docx npm library.
- Selby v. Brand Evangelists for Beauty Inc., Case No. 4:26-cv-05924-AMO (Judge Martínez-Olguín)
- Demonstrates caption table, counsel signature table (2 columns, no borders), body text with exact 24pt spacing and 0.5″ first-line indent
- Shows how to apply curly quotes, nonbreaking spaces after citation symbols, two spaces after sentence-ending periods
- Includes signature blocks with 3″ indent and footer with document title/case number
- IMPORTANT: All values are hardcoded for the Selby test case; every detail must be replaced for new matters

### templates/

Reserved for reusable template snippets and partial documents.
- Current placeholder documents the planned structure
- Will eventually contain standard-language blocks, topic templates, and signature block layouts

## Quick Start

1. **Read SKILL.md** to understand the workflow and overall structure.
2. **For detailed procedural guidance:**
   - Jurisdiction, venue, citation formatting → `references/standing_order_topics.md`
   - 26(f) scheduling, class-cert timing, calendar workflows → `references/bf_26f_scheduling_protocol.md`
3. **For date calculations:** Use `scripts/frcp6_date.py` with the matter's Rule 26(f) conference date.
4. **For the build mechanics:** Reference `references/example_build_script.js` for docx library patterns (curly quotes, spacing, table structure, etc.).

## Key Principles

- **Modular:** Each piece of procedural guidance lives in its own file, making updates and cross-referencing easier.
- **Testable:** Scripts are standalone and can be tested independently.
- **Template-free code:** The main SKILL.md does not embed large procedural blocks; it directs readers to reference files instead.
- **Example, not template:** The build script is a worked example (Selby case) showing mechanics, not a template to run as-is.

## Future Extensions

- Extract the 13 standard-language blocks into `templates/standard_language_blocks.md`
- Develop topic-specific template files in `templates/topics/`
- Create a JavaScript build helper library to abstract docx mechanics (curly quotes, spacing, comment anchoring)
- Expand `scripts/` with a full docx builder script that orchestrates the steps above

## Notes

- This skill is **N.D. Cal. only**. The 19-topic structure and page limits are specific to this district's Standing Order for All Judges and do not transfer to other districts.
- For putative class actions, confirm that the draft also covers Civil L.R. 16-9(b) supplemental requirements (see `references/standing_order_topics.md`).
- Always use the complaint as the authoritative source for party names, case number, jurisdictional basis, relief requested, and counsel contact information — never reuse or default to values from prior cases or example materials.

---

**Last Updated:** August 5, 2026  
**Location:** `/Users/tori/litigation-skills/nd-cal-cmc-stmt-builder/`
