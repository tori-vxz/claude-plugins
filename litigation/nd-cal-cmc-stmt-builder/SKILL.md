---
name: nd-cal-cmc-stmt-builder
description: Draft a Civil Case Management Statement (Joint Case Management Statement / "CMS" / "JCMS") for a case pending in the U.S. District Court for the Northern District of California, given a complaint and the assigned judge. Use this skill whenever the user mentions drafting, preparing, or updating a Case Management Statement, Joint Case Management Statement, or CMS/JCMS for N.D. Cal. — even if they just say "draft the CMS" or paste a complaint and a judge's name without spelling out the full document type. Also trigger if the user asks to research a specific N.D. Cal. judge's standing order or CMS requirements as a step toward preparing this filing, or if the user invokes this skill by name as "/ND Cal CMC Stmt Builder". Produces a court-formatted .docx with plaintiff-side content filled in and clearly marked placeholders for defendant's positions, ready to send to opposing counsel to complete before joint filing.
---

# ND Cal CMC Stmt Builder

Drafts a plaintiff-side Joint Case Management Statement for a case in the Northern District of
California, populated from (1) the complaint and (2) the assigned judge's specific requirements,
built on the district-wide baseline in `references/standing_order_topics.md`.

## Supporting files

Read each one at the step that calls for it — not all upfront.

| File | Read it when |
|---|---|
| `references/intake_and_research.md` | Steps 1–2: matter-number/26(f) lookup, Rule 16 Order priority, case number and judge initials, what to pull from the complaint, docket check, judge research |
| `references/standing_order_topics.md` | Step 3: the 19-topic structure, Civil L.R. 16-9(b) class supplement, formatting baseline |
| `templates/topic_language.md` | Step 3: singular/plural rules and the fixed language for the opening paragraph and Topics 1, 6–14, 16–19 |
| `templates/schedule_table.md` | Step 3: the Topic 15 schedule table — rows, fixed text, placeholder conventions |
| `references/citation_style.md` | Step 3: Bluebook (not California Style Manual) pincite formatting |
| `references/calendar_scheduling.md` | Step 3, only if a calendar tool is connected and the CMC hearing date is real: proposing actual class-cert dates |
| `references/bf_26f_scheduling_protocol.md` | Step 3: the firm's timing rules behind the Topic 15 placeholders. Attorney work product — never quoted, attached, or named in the draft |
| `references/docx_build.md` | Step 4: document-wide formatting, caption, signature blocks, footer, pagination, Word comments, attestations, verification |
| `references/example_build_script.js` | Step 4: worked example of the build mechanics. Built for one specific case — never reuse its values |
| `scripts/frcp6_date.py` | Any date computed from another date — applies Fed. R. Civ. P. 6(a) |
| `scripts/inject_line_numbers.py` | Step 4, only if the draft needs the firm's 28-line pleading-paper number column |

## Workflow

### Step 1 — Gather inputs

**Before anything else, ask for the internal matter number and look up the Rule 26(f)
conference/M&C date from that matter's calendar.** The resulting date (26(f) date + 14 days,
via `scripts/frcp6_date.py`) feeds Topic 7 and the Topic 15 initial-disclosures row, so asking
upfront avoids interrupting the draft partway through. Full lookup procedure, including every
fallback branch: `references/intake_and_research.md`, "26(f) conference date lookup." If the
lookup is skipped or comes up empty, both spots keep their bracketed-placeholder treatment —
that is not a reason to leave the rest of the draft incomplete.

You need, at minimum:

- **The complaint** (uploaded file or pasted text). If it's referenced but not attached, say so
  and ask for it — don't proceed on assumptions about case facts. Never guess at case facts,
  causes of action, relief sought, or jurisdictional basis; pull these only from the complaint.
- **The assigned judge's name** — unless a Rule 16 Order is provided, which supplies it instead.

**A Rule 16 Order, if provided, is the preferred source for the caption's hearing details** —
case number, assigned judge, and CMC hearing date/time/courtroom. If none is provided, take the
case number from the stamped complaint, leave hearing date/time/location as bracketed
placeholders, and prompt the user plainly for what's missing. Never invent a case number, and
derive the judge's initials fresh from the judge actually assigned — never hardcode them. Rules
and edge cases: `references/intake_and_research.md`, "Caption inputs."

Everything to extract from the complaint — caption, jurisdiction and venue as pled, class
allegations, causes of action, relief, related cases, and plaintiffs' counsel identification
block — is listed in the same file under "What to pull from the complaint."

### Step 2 — Research (dispatch as two parallel subagents)

Once Step 1 has produced the case number and the judge's name, run these two as **independent
subagents launched at the same time**. Neither needs the other's output, and dispatching them
keeps raw search noise out of the main conversation. Each returns only its distilled finding,
not its search transcript. Wait for both before Step 3.

- **Subagent A — public docket check.** Give it the case number; it reports service status,
  related motions, and any CMC date found — or plainly that nothing was found.
- **Subagent B — judge requirements.** Give it the judge's name; it reports a short digest of
  deviations from the district-wide baseline.

Full instructions for both, including the rule that an empty search result means "not found"
and never "not served": `references/intake_and_research.md`, "Docket check" and "Judge
requirements research." If subagents aren't available, run both inline in either order.

### Step 3 — Draft the statement

Read `references/standing_order_topics.md` for the 19-topic structure and
`templates/topic_language.md` for the fixed language. For each topic:

- **Plaintiff's position**, drawn from the complaint and Step 2 research, written in the
  register of an actual filed CMS — concise, no extended argument.
- **A clearly bracketed placeholder** for defendant's position, e.g.
  `[DEFENDANT'S POSITION: TO BE COMPLETED BY DEFENSE COUNSEL]`, in every topic that normally
  carries both sides' views. Topics 1, 7, 8, 10, 12, 13, 14, and 16–19 are written as single
  joint statements with no position split and no defendant placeholder — see the template file.
- **Renumber or relabel** sections to match the judge's individual variant if Step 2 found one;
  otherwise use the standard 19-topic order.

Do not fabricate dates, damages figures, or procedural history unsupported by the complaint or
your research. Use bracketed placeholders (e.g. `[PROPOSED DISCOVERY CUTOFF]`) for anything
requiring party negotiation or information outside the four corners of the complaint.

Topic 15 (Scheduling) has its own structure and table — see `templates/schedule_table.md`. Its
dates normally stay bracketed; they become real dates only under the conditions in
`references/calendar_scheduling.md`.

All pincites follow **Bluebook**, not the California Style Manual — see
`references/citation_style.md` before writing any citation.

### Step 4 — Produce the .docx

Read `/mnt/skills/public/docx/SKILL.md` before writing any code, then build with the `docx` npm
library per that skill's guidance and the full build rules in `references/docx_build.md`. The
five document-wide rules that govern every draft:

1. **First-line indent only** — 0.5" on the first line of each substantive paragraph, rest flush
   left, fully justified. Exceptions: all of Topic 11 (Relief) and the Topic 15 table.
2. **Continuous exact 24pt line spacing**, zero before/after spacing, `contextualSpacing` on
   every paragraph, no spacer paragraphs.
3. **Uniform 10pt Times New Roman footer**, every run.
4. **Curly quotation marks and apostrophes everywhere** — never a straight `"` or `'` in
   visible text.
5. **Two spaces after a sentence-ending period** — but not after abbreviations mid-sentence.

`references/docx_build.md` also covers the caption, the counsel and signature blocks, the
footer and page numbering, the Word comments that must be anchored, the end-of-document
attestations, and the subagent verification pass to run before presenting the file.

### Step 5 — Flag limitations

In your final response — not just in the document — note:

- Whether a judge-specific standing order was found, and where.
- Any topic left with a placeholder because the complaint didn't supply the information.
- Whether the calendar-assisted class-cert scheduling ran; if not, why (no calendar tool, or no
  confirmed CMC hearing date); if it did, which of the four rows got real dates and which stayed
  bracketed, plus any calendar events created — including whether the user separately confirmed
  creating the Hearing event, which is an independent yes/no from accepting the Hearing date.
- Whether the Step 1 matter-number/26(f) lookup produced a date and where it came from; if it
  didn't, confirm Topic 7 and the Topic 15 initial-disclosures row are still bracketed.
- A reminder that this is a plaintiff-side working draft for the meet-and-confer process, not a
  filing-ready joint statement until defense counsel completes their portions.

## Notes

- **N.D. Cal. only.** If the case is in a different district, stop and confirm — the 19-topic
  structure and page limits come from this district's Standing Order for All Judges and won't
  transfer.
- If the case is a putative class action, cover the Civil L.R. 16-9(b) supplemental requirements
  described in `references/standing_order_topics.md`.
- Treat this as a living draft: if the user has previously supplied case management orders,
  prior CMS filings, or judge-specific templates — in this conversation or a past session —
  prefer those over generic web research for formatting conventions.
- **Never carry values between cases.** Case number, judge initials, party names, and counsel
  information come fresh from the current case's own complaint and Rule 16 Order every time —
  never from a prior conversation, a different matter, or this skill's own example materials.
