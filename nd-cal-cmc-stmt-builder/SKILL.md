---
name: nd-cal-cmc-stmt-builder
description: Draft a Civil Case Management Statement (Joint Case Management Statement / "CMS" / "JCMS") for a case pending in the U.S. District Court for the Northern District of California, given a complaint and the assigned judge. Use this skill whenever the user mentions drafting, preparing, or updating a Case Management Statement, Joint Case Management Statement, or CMS/JCMS for N.D. Cal. — even if they just say "draft the CMS" or paste a complaint and a judge's name without spelling out the full document type. Also trigger if the user asks to research a specific N.D. Cal. judge's standing order or CMS requirements as a step toward preparing this filing, or if the user invokes this skill by name as "/ND Cal CMC Stmt Builder". Produces a court-formatted .docx with plaintiff-side content filled in and clearly marked placeholders for defendant's positions, ready to send to opposing counsel to complete before joint filing.
---

# ND Cal CMC Stmt Builder

Drafts a plaintiff-side Joint Case Management Statement for a case in the Northern District of California, populated from (1) the complaint and (2) the assigned judge's specific requirements.

## Workflow Overview

This skill runs five steps:

1. **Gather inputs** — Collect the complaint, judge, matter number, and Rule 16 Order (if available). Look up the Rule 26(f) conference date from the matter's calendar.
2. **Dispatch research subagents** — Run the docket check (Step 1a) and judge requirements research (Step 2) in parallel; fall back to inline research if subagents aren't available.
3. **Draft the statement** — Populate the 19 topics with plaintiff positions and defendant placeholders, applying district-wide baseline formatting from `references/standing_order_topics.md`.
4. **Produce the .docx** — Build a court-formatted Word document using the `docx` npm library.
5. **Flag limitations** — Note any missing information, judge-specific deviations, or calendar assistance outcomes.

## Step 1 — Gather Inputs

**Required inputs:**
- **The complaint** (uploaded file or pasted text) — if missing, ask for it and don't proceed without it.
- **The assigned judge's name** — unless a Rule 16 Order is provided (in which case pull the judge from that order).
- **The case number** — use the Rule 16 Order if provided; otherwise use the complaint's stamped court filing. If neither has a stamped number, ask the user to provide it before drafting.

**Before anything else:** ask for the **internal matter number** and look up the **Rule 26(f) conference date** from the matter's calendar. Use this date to compute the initial-disclosures deadline (14 days after the 26(f) conference, FRCP-6-adjusted) for Topic 7 and the Topic 15 scheduling table. See `references/bf_26f_scheduling_protocol.md` for the full lookup procedure and fallback behavior.

**Rule 16 Order (preferred for caption details):** If the user provides a Rule 16 Order, pull the case number, assigned judge, and the CMC hearing date/time/location directly from it. If not provided, leave the hearing date/time/location as bracketed placeholders in the caption and ask the user to either (a) provide the Rule 16 Order, (b) confirm the judge and provide those details directly, or (c) confirm you should proceed with placeholders.

**From the complaint, extract:**
- Full case caption (parties, case number), jurisdictional basis, whether it's a putative class action, causes of action, relief sought, related cases.
- Plaintiffs' counsel signature block (firm name, attorney names, state bar numbers, address, phone, fax, email, "Attorneys for Plaintiff(s)" line) — from the complaint's first and signature pages. This is the authoritative source for every new case; don't reuse prior counsel information.

## Step 1a & Step 2 — Research in Parallel (or inline fallback)

Dispatch these as two independent subagents when possible (neither depends on the other):

**Subagent A — Step 1a: Public docket check.** Given the case number, search CourtListener, PacerMonitor, UniCourt, or Justia Dockets for: (a) whether a summons appears returned executed (with date/ECF number), (b) any related motions filed, (c) any CMC date set. Return findings or "not found" plainly; don't infer facts from absence of a search hit.

**Subagent B — Step 2: Judge requirements research.** Given the judge's name, web search for their individual standing order/civil requirements on `cand.uscourts.gov` and google. Return deviations from the district-wide baseline — stricter page limits, additional topics, required attached orders, special formatting, etc. — or state plainly if no standing order was found.

If subagents aren't available, run Steps 1a and 2 inline in either order.

## Step 3 — Draft the Statement

Use `references/standing_order_topics.md` for:
- The 19-topic structure and joint-statement framework
- Which topics split into "Plaintiffs' Position" / "Defendant's Position" and which stay joint
- Detailed drafting rules for each topic
- Formatting baseline (first-line-indent-only, exact-24pt spacing, curly quotes, two spaces after sentence-ending periods, nonbreaking spaces after section/paragraph symbols)

**Key standard-language blocks** (drafted the same way in every case, adjusted for singular/plural plaintiff/defendant counts):
- Evidence Preservation (Topic 6) — Topic 7 (Disclosures) — Topic 8 (Discovery) — Topic 9 (Class Actions, if applicable) — Topic 10 (Related Cases) — Topic 12 (Settlement & ADR) — Topic 13 (Other References) — Topic 14 (Narrowing of Issues) — Topic 16–19 (Trial, Interested Entities, Professional Conduct, Other Matters)

**Custom sections** (derived from complaint/judge requirements):
- Topic 1 (Jurisdiction and Service and Venue) — Topic 11 (Relief, from complaint's Prayer for Relief) — Topic 15 (Scheduling, with class-cert dates computed per `references/bf_26f_scheduling_protocol.md`)

**Bluebook citation formatting** (federal style, not California):
- En dash for ranges (not hyphen): `Compl. ¶¶ 22–44.`
- "Compl." (not "Complaint") with no comma before the pincite: `Compl. ¶ 9`
- Introductory signals italicized: *See* Compl. ¶ 8
- Nonbreaking space after ¶/¶¶/§/§§ and their numbers

## Step 3a (Calendar-assisted class-cert scheduling, Topic 15 only)

If a calendar tool is connected AND a real CMC hearing date exists (from Rule 16 Order or user input), compute proposed dates for Plaintiff's Motion for Class Certification, Opposition, Reply, and Hearing using `scripts/frcp6_date.py` with the firm's 26(f) scheduling protocol. Check against the user's calendar for conflicts, confirm each date with the user, and create calendar events for accepted dates.

If either condition fails (no calendar tool, or CMC date is still bracketed/unknown), leave these four rows as standard bracketed placeholders per the protocol.

See `references/bf_26f_scheduling_protocol.md` for notice periods, weekday constraints per judge, and the full date-confirmation flow.

## Step 4 — Produce the .docx

Read `/mnt/skills/public/docx/SKILL.md` for the docx npm library guidance.

Build the document with these key requirements:
- **Caption box** with party names, case number (with judge initials per Civil L.R. 3-4), judge, document title, and CMC hearing date/time/courtroom (per Rule 16 Order or placeholders).
- **Counsel signature table** (2 columns, 1 row, no visible borders) — plaintiffs' counsel in left cell, defense counsel placeholder in right cell.
- **Signature blocks** (ending of document, 3″ indent) with auto-updating date fields.
- **Footer** with document title and case number (with judge initials), 10pt Times New Roman, uniformly left column and right-aligned page number (page 1 starts on the second physical page; caption page has no number).
- **Two document-ending attestations** (Signature Attestation always; Generative AI Certification only if the judge's standing order requires one).

**Formatting baseline** (full detail in `references/standing_order_topics.md`):
- First-line indent only (0.5″, except Section 11 Relief and Section 15 table).
- Exact 24pt line spacing everywhere in body text; no extra before/after spacing.
- ContextualSpacing enabled on every paragraph.
- Curly quotes throughout (never straight " or ').
- Two spaces after sentence-ending periods (not after abbreviations/citations mid-sentence).
- Uniform 10pt Times New Roman footer.

**Verification:** Dispatch the rendered PDF to a subagent with the formatting checklist (indent-only, exact-24pt, 10pt footer, curly quotes, two-space sentence endings, page numbering, table borders, bold firm names, 3″ signature indent, auto-date fields) and have it report pass/fail with any deviations flagged by page. Fix anything before presenting.

## Step 5 — Flag Limitations

In your final response, note:
- Whether a judge-specific standing order was found and where.
- Any topics where you used bracketed placeholders due to missing information.
- Whether calendar-assisted scheduling (Topic 15) ran, and if not, why (no calendar tool or no confirmed CMC date). If it did run, which rows got real dates vs. brackets, and which calendar events were created.
- Whether the Step 1 matter-number/26(f) lookup produced a date, its source, and whether Topics 7 and 15's initial-disclosures row are on standard bracket treatment.
- A reminder that this is plaintiff-side working draft for meet-and-confer, not filing-ready until defense counsel completes their portions.

## Key Files

- `references/standing_order_topics.md` — 19-topic structure, joint vs. split topics, formatting rules, standard language for each topic.
- `references/bf_26f_scheduling_protocol.md` — 26(f) scheduling timing rules, class-cert motion dates, notice periods per judge.
- `references/example_build_script.js` — Worked example (Selby v. Brand Evangelists for Beauty Inc., Case No. 4:26-cv-05924-AMO) showing the docx build mechanics; values are case-specific and must be replaced for any new matter.
- `scripts/frcp6_date.py` — Computes FRCP 6(a)-adjusted dates (month arithmetic, weekend/holiday roll-forward).
- `scripts/comment.py` — Helper for anchoring Word comments to text (or reference the docx skill's equivalent).

## Notes

- **N.D. Cal. only.** If the case is in a different district, stop and confirm — the 19-topic structure and page limits are specific to this district's Standing Order and won't transfer.
- **Class action supplement (if applicable).** For putative class actions, confirm Step 3 also covers Civil L.R. 16-9(b) supplemental requirements (see `references/standing_order_topics.md` for details).
- **Living draft precedent.** If the user has provided prior case management orders, old CMS filings, or judge templates in this or past conversations, prefer those over generic web research for formatting conventions.
- **Example is not a template.** `references/example_build_script.js` is hardcoded for one test case and serves as a mechanics reference only; replace every case-specific value for new matters.
