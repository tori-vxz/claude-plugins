# Intake and research

Detail for Steps 1 and 2 of `SKILL.md`.

## 26(f) conference date lookup

Runs at the very start of every use of this skill, before anything else in Step 1, because the
date it produces feeds two later spots in the draft (Topic 7's initial-disclosures sentence and
the Topic 15 scheduling table). Asking upfront avoids interrupting drafting partway through.

1. Ask the user for the case's internal matter number.
2. **Resolve the matter number to a calendar, not to an event search across everything — but
   resolve it against the full calendar list, not just the first page.**
   - Call `list_calendars` and follow every `nextPageToken` until a call returns none,
     collecting all calendars' `id`/`summary` before matching anything. `list_calendars` caps at
     roughly 100 results per page, and the firm has more matters than that — a first-page-only
     lookup will silently miss any matter whose calendar falls past page one.
   - If a page-token request errors (e.g. a "precondition check failed" response), retry it
     once. If it errors again, treat the collected list as **partial** rather than complete, and
     say so — don't report "no calendar found" on an incomplete list.
   - Match the matter number as a whole leading token against each calendar's `summary` (a
     pattern like `^\s*(\d+)\b`) — this firm keeps one dedicated calendar per matter, named like
     "3696 Sling TV" (matter number + short case name), though a few shared calendars (e.g.,
     "Appellate Cases") pool multiple matters together and would need an event-title match
     instead. Compare the whole token, not a substring — "423" must not match "4235."
   - If the full list yields no match, or the list is partial because a page token failed, fall
     back to `search_events` with the matter number as the query. This searches event text and
     organizer fields and can surface a calendar the paginated list didn't fully reach (via the
     event's `organizer.displayName`/`organizer.email`). If that turns up an event whose
     organizer calendar's leading number matches exactly, use that calendar — but say explicitly
     that it was found via event search rather than the calendar list, since this route is a
     fallback, not a primary confirmation.
   - If no exact match turns up through either route, tell the user plainly that you couldn't
     find a calendar for that matter number and ask them to double-check it and enter it again
     — don't fall through to a different matter's calendar or guess.
3. **Within that matter's calendar, search for an event referencing the Rule 26(f) conference** —
   titles like "26F," "26F M&C," "26F Call," "26(f) Conference," or similar; match on the
   substring "26F" (or "26(f)") case-insensitively rather than requiring an exact label, since
   different timekeepers phrase this differently.
   - **If you find one event that clearly and unambiguously references the 26(f)
     conference/M&C, use its date** — no need to check in with the user first when the match is
     this clean.
   - **If nothing in that calendar references 26(f) at all, or you find something but aren't
     confident it's the right event** (multiple candidates, or a title that's ambiguous about
     whether it's actually the 26(f) conference), tell the user what you found (or that you
     found nothing) and ask directly: is [this event / a 26(f) conference] the one to use for
     this calculation?
     - If yes: use that event's date.
     - If no: ask the user to type in the actual date of the 26(f) conference directly.
       - If they don't provide one, drop this feature for the rest of the draft — leave Topic 7
         and the Topic 15 initial-disclosures row with their standard bracketed-placeholder
         treatment rather than guessing or re-asking repeatedly.
4. Once you have a governing 26(f) conference date (from the calendar or from the user
   directly), compute 14 days after it using `scripts/frcp6_date.py <date> "14 days"` — the same
   script used for the Topic 15 class-cert dates, with the same FRCP 6(a) weekend/holiday
   roll-forward logic. This resulting date is what gets inserted in Topic 7 and in the Topic 15
   initial-disclosures row; both must always show the same value, sourced the same way.

If this whole lookup is skipped or abandoned per the branches above, both of those spots keep
their existing bracketed-placeholder behavior — don't treat the absence of a matter-number-based
date as a reason to leave the rest of the draft incomplete.

## Caption inputs

### Rule 16 Order takes priority

If the user provides the court's Order Setting Initial Case Management Conference (a "Rule 16
Order" — issued under Fed. R. Civ. P. 16 and Civil L.R. 16-2), pull the case number, the
assigned judge, and the CMC hearing date, time, and location (courtroom) directly from that
order rather than from the complaint or from asking the user separately — the Rule 16 Order is
the authoritative source for these specific fields since the court itself sets them. Use it in
preference to any conflicting information elsewhere (e.g., if the complaint predates a judge
reassignment, the Rule 16 Order's judge controls).

**If no Rule 16 Order is provided:** pull only the case number from the stamped complaint (per
the rule below), and leave the hearing date, time, and courtroom/location fields as bracketed
placeholders in the caption box — do not guess or invent them. In the same response, explicitly
prompt the user to (a) confirm the assigned judge if not already provided, (b) supply the
Rule 16 Order so the hearing date, time, and location can be filled in, or (c) provide the
date/time/location directly if the order isn't available. Don't bury this prompt — say it
plainly, the same way Claude would flag any other missing required input.

### Case number

Use the Rule 16 Order if one was provided; otherwise use the complaint's stamped filing. Look
for the court-stamped case number (e.g., in the caption box or in a "Case X:XX-cv-XXXXX" ECF
stamp/header on the page) on whichever of those two documents takes priority. Use that exact
number verbatim in the caption box and footer — never invent, reuse, or carry over a case number
from a prior conversation, a different case, or an example in this skill's own reference
materials.

If neither document contains a stamped case number (e.g., an unstamped drafting copy, or the
field is blank because the complaint hasn't been filed/assigned yet), stop and ask the user to
provide the stamped case number before drafting the caption — do not proceed with a placeholder
case number silently, since getting this wrong on a real filing is a serious, avoidable error.

### Judge's initials — derived fresh every time, never hardcoded

Civil L.R. 3-4(a)(3)(C) requires the case number to be followed by the assigned judge's initials
(e.g., "4:26-cv-05924-AMO" for Judge Martínez-Olguín). This skill was originally developed and
tested using Judge Martínez-Olguín (initials "AMO") as the example judge, but that is not a
default — it is only one example. For every new draft:

1. Confirm the initials actually used in this district for the specific judge named by the user
   in this conversation (check a real case number involving that judge via web search, or ask
   the user if uncertain — don't guess at a judge's initials from their name).
2. Use those initials consistently everywhere a case number appears in the draft: the caption
   box, the footer (Civil L.R. 3-4(c)(3)), and anywhere else the case number is cited (Word
   comments, the front-matter counsel block if it references the case number, etc.).
3. If the judge assigned to this case changes from a prior draft in the same conversation (e.g.,
   the user corrects the judge, or the case gets reassigned), update every case-number citation
   in the new draft accordingly — don't leave stale initials from an earlier version.

## What to pull from the complaint

- Full case caption (parties; case number per the rule above), basis for jurisdiction and venue
  as pled, whether it's a putative class action (and under what Rule 23 theory), causes of
  action and the statutes/legal theories invoked, relief and damages sought, any related-case
  references, whether defendants appear to be served (usually unknown from the complaint alone —
  flag as a placeholder).
- **Plaintiffs' counsel signature/identification information** (firm name(s), attorney name(s)
  and state bar number(s), address, phone, fax, email, and the "Attorneys for Plaintiff(s)"
  line) — from the complaint's first page and signature page. This populates both the
  front-matter counsel block and the ending signature block in the CMS (see
  `references/docx_build.md`); pull it fresh from this complaint every time, never from a prior
  case or this skill's own examples.

## Docket check (Subagent A)

No PACER/ECF tool is available, so Claude cannot pull the docket directly. As a courtesy, web
search public docket-tracking mirrors (CourtListener, PacerMonitor, UniCourt, Justia Dockets)
for the case number to see if a summons has been returned executed, if related motions have been
filed, or if a CMC date has been set. This is especially likely to come up empty for recently
filed cases (mirrors lag actual PACER, and service returns aren't always separately indexed even
when filed).

Return: whether a summons appears returned executed (with date and ECF number if so), any
related motions found, and any CMC date found — or a plain statement that nothing was found.

**Critical: an empty or unhelpful search result means "not found," not "not yet served" or "no
CMC date set."** Never present the absence of a search hit as confirmation of a fact. State
plainly, in the same terms Claude would use with the user directly, that this specific
information (service status, docket number, scheduled dates) requires either the attorney's own
knowledge of the case or a direct PACER pull, and leave it as a bracketed placeholder in the
draft rather than guessing or implying the search was dispositive.

The result of this check drives the Word comment anchored to the Topic 1 service placeholder —
see `references/docx_build.md`, "Word comment on service status."

## Judge requirements research (Subagent B)

Web search for the judge's individual standing order / civil case management requirements, e.g.
search `"[Judge Name]" standing order case management N.D. Cal.` and
`site:cand.uscourts.gov "[Judge Name]"`. Judges post these at
https://cand.uscourts.gov/judges/ — fetch the judge's page and any linked standing order PDF.

Look specifically for deviations from the district-wide baseline:

- Page limits stricter than the standard 10 pages
- Additional required topics or a required attached proposed order
- Formatting requirements (font, margins, specific caption format)
- Whether a joint proposed case management order must be lodged separately
- Any minimum motion-notice period or fixed civil motion calendar day (needed for the Topic 15
  class-cert hearing row)
- Any requirement that AI-assisted filings carry a certification (needed for the end-of-document
  Generative AI Certification)

Return a short digest of the deviations found — not the full standing order text.

If no judge-specific standing order turns up after a reasonable search, say so explicitly in
your response and in a footnote/comment in the draft — don't silently assume the baseline is
complete. This is a citation-sensitive, court-facing document; flag the gap rather than paper
over it.
