---
name: nd-cal-cmc-stmt-builder
description: Draft a Civil Case Management Statement (Joint Case Management Statement / "CMS" / "JCMS") for a case pending in the U.S. District Court for the Northern District of California, given a complaint and the assigned judge. Use this skill whenever the user mentions drafting, preparing, or updating a Case Management Statement, Joint Case Management Statement, or CMS/JCMS for N.D. Cal. — even if they just say "draft the CMS" or paste a complaint and a judge's name without spelling out the full document type. Also trigger if the user asks to research a specific N.D. Cal. judge's standing order or CMS requirements as a step toward preparing this filing, or if the user invokes this skill by name as "/ND Cal CMC Stmt Builder". Produces a court-formatted .docx with plaintiff-side content filled in and clearly marked placeholders for defendant's positions, ready to send to opposing counsel to complete before joint filing.
---
 
# ND Cal CMC Stmt Builder
 
Drafts a plaintiff-side Joint Case Management Statement for a case in the Northern District of
California, populated from (1) the complaint and (2) the assigned judge's specific requirements,
built on the district-wide baseline in the N.D. Cal. Standing Order for All Judges, Civil Local Rule 16-9.
 
## Scope & Outputs

This skill drafts plaintiff-side CMS content only. It extracts facts from the complaint (caption, parties, jurisdiction, relief sought), crosses those with the judge's standing order to spot deviations from the district baseline, and produces a .docx file formatted to N.D. Cal. specifications with:

- **Completed plaintiff sections** — drawn from the complaint and the judge's standing order research
- **Clearly marked defense-counsel placeholders** — [DEFENDANT'S POSITION: TO BE COMPLETED BY DEFENSE COUNSEL] for every joint topic that needs both sides' input
- **Proposed class-certification and trial dates** — per the firm's Rule 26(f) Scheduling Protocol
- **Optional calendar events** — for each accepted deadline, created on the user's calendar

The document is ready to send to opposing counsel for completion of their portions before joint filing.

## Operating Instructions

### Step 1 — Gather inputs

**At the very start of every use of this skill, ask for the internal matter number and look up the Rule 26(f) conference/M&C date from the matter's calendar.** This runs before anything else in Step 1, because it feeds a date used in two places later in the draft (Topic 7's initial disclosures sentence and the Topic 15 scheduling table), and asking for it upfront avoids having to interrupt drafting partway through. The lookup:

1. Ask the user for the case's internal matter number.
2. **Resolve the matter number to a calendar, not to an event search across everything.** Call the calendar tool's `list_calendars` and look for a calendar whose name (`summary`) starts with or contains that matter number — this firm keeps one dedicated calendar per matter, named like "3696 Sling TV" (matter number + short case name), though a few shared calendars (e.g., "Appellate Cases") pool multiple matters together and would need an event-title match instead. Try the calendar-name match first.
   - If no calendar's name matches the matter number, tell the user plainly that you couldn't find a calendar for that matter number and ask them to double-check it and enter it again — don't fall through to a different matter's calendar or guess.
3. **Within that matter's calendar, search for an event referencing the Rule 26(f) conference** — titles like "26F," "26F M&C," "26F Call," "26(f) Conference," or similar; match on the substring "26F" (or "26(f)") case-insensitively rather than requiring an exact label, since different timekeepers phrase this differently.
   - **If you find one event that clearly and unambiguously references the 26(f) conference/M&C, use its date** — no need to check in with the user first when the match is this clean.
   - **If nothing in that calendar references 26(f) at all, or you find something but aren't confident it's the right event** (multiple candidates, or a title that's ambiguous about whether it's actually the 26(f) conference), tell the user what you found (or that you found nothing) and ask directly: is [this event / a 26(f) conference] the one to use for this calculation?
     - If yes: use that event's date.
     - If no: ask the user to type in the actual date of the 26(f) conference directly.
       - If they don't provide one, drop this feature for the rest of the draft — leave Topic 7 and the Topic 15 initial-disclosures row with their standard bracketed-placeholder treatment (described in each topic's own section below) rather than guessing or re-asking repeatedly.
4. Once you have a governing 26(f) conference date (from the calendar or from the user directly), compute 14 days after it using FRCP 6(a) math (the same script used for the Topic 15 class-cert dates below). This resulting date is what gets inserted in Topic 7 and Topic 15; see those sections for exactly where.

If this whole lookup is skipped or abandoned per the branches above, both of those spots keep their existing bracketed-placeholder behavior — don't treat the absence of a matter-number-based date as a reason to leave the rest of the draft incomplete.

**A Rule 16 Order, if provided, is the preferred source for the caption's hearing details.** If the user provides the court's Order Setting Initial Case Management Conference (a "Rule 16 Order" — issued under Fed. R. Civ. P. 16 and Civil L.R. 16-2), pull the case number, the assigned judge, and the CMC hearing date, time, and location (courtroom) directly from that order rather than from the complaint or from asking the user separately — the Rule 16 Order is the authoritative source for these specific fields since the court itself sets them. Use it in preference to any conflicting information elsewhere (e.g., if the complaint predates a judge reassignment, the Rule 16 Order's judge controls).

**If no Rule 16 Order is provided:** pull only the case number from the stamped complaint (per the rule above), and leave the hearing date, time, and courtroom/location fields as bracketed placeholders in the caption box — do not guess or invent them. In the same response, explicitly prompt the user to (a) confirm the assigned judge if not already provided, (b) supply the Rule 16 Order so the hearing date, time, and location can be filled in, or (c) provide the date/time/location directly if the order isn't available. Don't bury this prompt — say it plainly, the same way Claude would flag any other missing required input.

You need, at minimum:
- **The complaint** (uploaded file, or pasted text). If it's referenced but not actually attached, say so and ask for it — don't proceed on assumptions about case facts.
- **The assigned judge's name** — unless a Rule 16 Order is provided, in which case pull the judge from that order instead of asking separately.

If the complaint is missing, ask for it before drafting. Don't guess at case facts, causes of action, relief sought, or jurisdictional basis — pull these only from the complaint itself.

**The case number: use the Rule 16 Order if one was provided; otherwise use the complaint's stamped filing.** Look for the court-stamped case number (e.g., in the caption box or in a "Case X:XX-cv-XXXXX" ECF stamp/header on the page) on whichever of these two documents takes priority per the rule above. Use that exact number verbatim in the caption box and footer — never invent, reuse, or carry over a case number from a prior conversation, a different case, or an example in this skill's own reference materials. If neither document contains a stamped case number (e.g., an unstamped drafting copy, or the case number field is blank because the complaint hasn't been filed/assigned yet), stop and ask the user to provide the stamped case number before drafting the caption — do not proceed with a placeholder case number silently, since getting this wrong on a real filing is a serious, avoidable error.

**Judge's initials must be derived fresh from the judge actually provided, every time — never hardcoded.** Civil L.R. 3-4(a)(3)(C) requires the case number to be followed by the assigned judge's initials (e.g., "4:26-cv-05924-AMO" for Judge Martínez-Olguín). For every new draft:
1. Confirm the initials actually used in this district for the specific judge named by the user in this conversation (check a real case number involving that judge via web search, or ask the user if uncertain — don't guess at a judge's initials from their name).
2. Use those initials consistently everywhere a case number appears in the draft: the caption box, the footer, and anywhere else the case number is cited.
3. If the judge assigned to this case changes from a prior draft in the same conversation (e.g., the user corrects the judge, or the case gets reassigned), update every case-number citation in the new draft accordingly — don't leave stale initials from an earlier version.

**Extract from complaint:**
- Full case caption (parties; case number per the rule above), basis for jurisdiction and venue as pled, whether it's a putative class action (and under what Rule 23 theory), causes of action and the statutes/legal theories invoked, relief and damages sought, any related-case references, whether defendants appear to be served (usually unknown from the complaint alone — flag as a placeholder).
- **Plaintiffs' counsel signature/identification information** (firm name(s), attorney name(s) and state bar number(s), address, phone, fax, email, and the "Attorneys for Plaintiff(s)" line) — from the complaint's first page and signature page. Pull it fresh from this complaint every time, never from a prior case or this skill's own examples.

### Step 1a and Step 2 — dispatch as two parallel subagents

Once Step 1 has produced the case number and the assigned judge's name, run **Steps 1a and 2 as two independent subagents launched at the same time**, rather than doing this research inline. Neither depends on the other's output — one only needs the case number, the other only needs the judge's name.

- **Subagent A — Step 1a, public docket check.** Check public docket-tracking mirrors for service status and any related motions or CMC date set.
- **Subagent B — Step 2, judge requirements research.** Fetch the judge's standing order and report deviations from the district-wide baseline.

#### Step 1a — Check for public docket information (service status, related filings)

Web search public docket-tracking mirrors (CourtListener, PacerMonitor, UniCourt, Justia Dockets) for the case number to see if a summons has been returned executed, if related motions have been filed, or if a CMC date has been set. Note: an empty search result means "not found," not "not yet served." State plainly that this information requires either the attorney's own knowledge of the case or a direct PACER pull, and leave it as a bracketed placeholder in the draft rather than guessing.

#### Step 2 — Research the assigned judge's requirements

Web search for the judge's individual standing order / civil case management requirements. Look specifically for deviations from the district-wide baseline (page limits, additional required topics, formatting requirements, whether a joint proposed order must be lodged separately). If no judge-specific standing order turns up, say so explicitly rather than silently assuming the baseline is complete.

### Step 3 — Draft the statement

Draft the CMS with the structure, formatting, and language described in the judge-specific standing order or the N.D. Cal. district-wide baseline. Populate each topic with plaintiff's position (drawn from the complaint and step 2 research) and clearly bracketed placeholders for defense-counsel positions. Do not fabricate specific dates, damages figures, or procedural history — use bracketed placeholders for anything that requires party negotiation.

### Step 4 — Produce the .docx

Build the document using professional legal formatting:
- US Letter page size
- Standard N.D. Cal. caption format with the actual stamped case number and assigned judge's initials
- Numbered/lettered sections per the topics
- Placeholder text visually distinguished (bold + bracket + color, or Word comments)
- Signature blocks for plaintiff's counsel and (if applicable) defense counsel
- Footer with case number and page number per Civil L.R. 3-4(c)(3)
- Page numbering starts on the second page (caption page is unnumbered)
- Curly quotation marks throughout
- Two spaces after sentence-ending periods
- Plaintiff-side content completed, defense-side positions clearly bracketed

### Step 5 — Flag limitations

In your final response, note:
- Whether a judge-specific standing order was found
- Any topics where a placeholder was needed due to missing information
- Whether the Rule 26(f) conference date lookup succeeded and what it produced
- A reminder that this is a plaintiff-side working draft, not a filing-ready joint statement until defense counsel completes their portions
