# Building the .docx

Detail for Step 4 of `SKILL.md`. Read `/mnt/skills/public/docx/SKILL.md` before writing any code
and build with the `docx` npm library per that skill's guidance. `references/example_build_script.js`
shows the mechanics end to end — the `P()`/`T()` helpers, the exact-24pt spacing setup, the
caption table border configuration, the footer. It was built for one specific test case
(*Selby v. Brand Evangelists for Beauty Inc.*, Case No. 4:26-cv-05924-AMO, before Judge
Martínez-Olguín) and hardcodes that case's party names, case number, judge initials, and factual
allegations throughout. Use it to see how the mechanics work; replace every Selby-specific value
with the real case's details.

## Document-wide formatting rules

Full OOXML-level detail for the caption, title, and signature-block conventions is in
`references/standing_order_topics.md` under "Formatting baseline."

### 1. First-line indent only

Every substantive text paragraph — intro through Topic 19 — indents only its FIRST line 0.5"
(`w:ind w:firstLine="720"`), with the rest of the paragraph flush to the left margin, fully
justified. Do not use a whole-paragraph left indent. The two exceptions are **Topic 11 (Relief)
in its entirety** (label, intro sentence, and lettered list all keep their own formatting) and
**the Topic 15 schedule table** (the table itself; its lead-in sentence still takes the
first-line indent).

### 2. Continuous exact 24pt — no extra paragraph spacing

Set before- and after-paragraph spacing to zero on every substantive paragraph, including
section headings (no blank line before a heading), and insert no empty "spacer" paragraphs in
the body. The exact-24pt line spacing alone provides all separation, so the whole body reads as
clean continuous double-spacing that meets the ≤28-lines-per-page requirement. The single-spaced
exempt blocks (caption, counsel, signature/attestation) also carry no extra after-spacing or
blank filler beyond the one line needed to separate distinct blocks; Topic 11's relief list keeps
its own list spacing.

Two spacing settings must hold across the whole draft:

(a) the exact-24pt line spacing (`w:spacing w:line="480" w:lineRule="exact"`) is the line spacing
for every substantive text paragraph — intro through Topic 19, headings included — so the body is
uniformly 24pt, not a mix; and

(b) set **`w:contextualSpacing`** ("Don't add space between paragraphs of the same style," exposed
by the `docx` npm library as `contextualSpacing: true`) on **every** paragraph in the document.
Belt-and-suspenders with the zeroed before/after spacing, `contextualSpacing` guarantees Word
never injects a style-based gap between consecutive same-style paragraphs, which is exactly the
clean, gap-free look these pleadings use. Apply it everywhere (body, headings, caption,
counsel/signature blocks, attestations, table lead-ins) — it's harmless on the single-spaced
blocks and prevents surprises if a paragraph's before/after ever gets set nonzero.

The caption box and the Topic 15 schedule table are structural tables, not narrative
"same-style" paragraphs, so they keep their own functional cell/row spacing; the 24pt-line +
`contextualSpacing` rule governs the flowing text of the draft.

### 3. Uniform 10pt Times New Roman footer

Every run in the footer — the title line, the "CASE NO. ..." text, and the page number — is 10pt
(`w:sz="20"`) Times New Roman. Do not leave the case-number/page line at a larger size than the
title.

### 4. Curly quotation marks and apostrophes everywhere

Use typographic ("smart") quotes throughout — “ ” for double quotes, ‘ ’ for single quotes,
and ’ for every apostrophe (possessives and contractions alike). Never leave a straight `"` or `'` in
the visible text. This applies universally: body text, quoted product/advertising claims pulled
from the complaint, defined terms, bracketed placeholders, headings, and signature/counsel
blocks. Put the actual curly Unicode characters in each `TextRun` (a straight quote that opens —
i.e., follows a space, opening bracket, dash, or the start of a run — becomes “ or ‘; any other
becomes ” or ’). The example build script does this with a small `sq()` helper that every text
run is routed through; reuse that pattern so nothing slips through as a straight quote.

### 5. Two spaces after a sentence-ending period

Throughout the draft, put two spaces after any period that ends a sentence (and after other
sentence-ending punctuation, `?` and `!`), before the first word of the next sentence — this
firm's house style for court filings. This applies to the flowing narrative text everywhere: the
intro paragraph, every topic's prose, the jurisdiction/venue sentences, the standard-language
blocks, and the attestation paragraphs.

Two cautions so it doesn't over-fire: (a) it's only for periods that actually *end a sentence* —
do not add a second space after the period in an abbreviation or citation that continues the same
sentence (e.g., `28 U.S.C. § 1332`, `Cal. Bus. & Prof. Code § 17200`, `L.R. 3-4`, `No.`, `Inc.`,
`v.`, or a mid-sentence `Compl. ¶ 9` reference), and (b) a citation sentence that stands on its
own (e.g. `... in this District. Compl. ¶ 11.`) does get two spaces before it, because the
preceding period ends a sentence. When in doubt, ask whether a new sentence starts after the
period; if yes, two spaces, if no, one. Put the two spaces directly in the `TextRun` text.

## Other build requirements

- US Letter page size.
- Standard N.D. Cal. caption format (party names, case number, judge, document title in caps).
  Use the actual stamped case number from the complaint and the actual assigned judge's initials
  — do not copy the "4:26-cv-05924-AMO" example number/initials from this skill's own reference
  materials or from a prior case worked on in this conversation.
- Numbered/lettered sections per Step 3.
- Placeholder text visually distinguished (e.g. bold + bracket + a different color, or a Word
  comment) so it's unmistakable which content still needs defense counsel input.
- Signature blocks for plaintiff's counsel; a blank signature line for defense counsel if a joint
  proposed order convention calls for it in this district. **Always pull the plaintiffs' counsel
  signature/identification blocks — both the front-matter counsel block at the very top of the
  document and the ending signature block after the numbered sections — directly from the
  complaint the user uploads for that case.** The complaint's own first page (firm name(s),
  attorney name(s), state bar number(s), address, phone, fax, email, and the "Attorneys for
  Plaintiff(s)" line) and signature page are the authoritative source. Do not reuse, carry over,
  or default to counsel information from a prior case in this conversation, from this skill's own
  example materials (e.g., Bursor & Fisher's Selby-case contact details in
  `references/example_build_script.js`), or from general familiarity with a firm.

## Signature-block formatting

Applies to both the caption-page counsel block and the ending signature blocks.

- **Caption-page counsel block is a two-column, one-row, borderless table.** At the very top of
  the first (caption) page, lay out counsel in a table with two columns and a single row:
  **plaintiffs' counsel signature/identification block in the left cell, defense counsel's
  signature block in the right cell.** The table must have **no visible borders at all** — set
  every border (top, bottom, left, right, and both inside borders) to none/nil so nothing prints
  (`w:tblBorders` with each edge `w:val="none"`; the `docx` npm library takes a `borders` config
  with each side `style: BorderStyle.NONE`/`none`). This mirrors the uploaded exemplar, whose
  caption-page counsel table is a 2×1 grid with all borders set to none. If defense counsel isn't
  yet known, still create the two-cell table and put a clearly bracketed placeholder (e.g.,
  `[DEFENSE COUNSEL SIGNATURE BLOCK — TO BE COMPLETED]`) in the right cell so the layout is right
  for when it's filled in.
- **Bold the firm name — the first line of every signature block.** In every signature block,
  wherever it appears (the caption-page counsel table on both sides, and the ending signature
  blocks for both plaintiffs' and defendants' counsel), the **first line, which is the law-firm
  name, is bold** (e.g., **BURSOR & FISHER, P.A.**, **HOLLAND LAW LLP**). The attorney names, bar
  numbers, address, phone/fax/email, and the "Counsel for …" line that follow stay in normal
  (non-bold) weight. Apply this every single time a signature block is rendered — don't bold the
  firm name in one block and forget it in another.
- **Ending signature-block layout — align the block, and "Respectfully submitted" and "By:", at a
  3″ indent.** In the ending signature blocks (after the numbered topics), the whole signature
  block sits indented to about **3 inches** from the left margin (the uploaded exemplar uses a
  4320-twip left indent / left tab stop, i.e. exactly 3.0″; anywhere in the 3″–3.5″ range is
  acceptable, but be consistent). Align all of these to that same 3″ position: the "Respectfully
  submitted," line, the "Dated: …" line's firm name, and the "By: [SIGNATURE]" line, plus the
  attorney/address lines beneath (set their paragraph left indent to the same 3″). Concretely,
  matching the exemplar: one line reads `Respectfully submitted,`; the next reads
  `Dated: <auto-date field>` then a tab to the 3″ stop followed by the **bold firm name**; the
  next reads a tab to 3″ then `By:` then a tab then `[SIGNATURE]`; then the attorney name, bar
  number, address, phone, fax, email lines each left-indented to 3″; then the `Counsel for
  Plaintiff[s]` / `Counsel for Defendant[s]` line. Keep these blocks single-spaced (they are
  exempt from the 24pt body line spacing) but carry `contextualSpacing` like everything else.
- **Auto-updating date field after "Date:"/"Dated:" in the ending signature blocks.** After the
  "Dated:" (or "Date:") label, insert a **Word date field that auto-updates**, formatted as month,
  day, year — i.e., the field code `DATE \@ "MMMM d, yyyy"`, which renders like "August 13, 2026"
  — instead of a literal `[DATE]` placeholder. This matches the uploaded exemplar, whose counsel
  signature blocks use exactly this field. In the `docx` npm library, build it as a
  `SimpleField`/field run with instruction `DATE \@ "MMMM d, yyyy"` (or emit the
  `w:fldSimple`/`fldChar`+`instrText` field directly). Apply this in both the plaintiffs' and the
  defendants' ending signature blocks. (The end-of-document Signature Attestation and any
  Generative AI Certification keep their own "Dated: [DATE]" treatment described below unless the
  firm's convention says otherwise — the auto-date field is specifically for the counsel signature
  blocks.)

## Footer and page numbering

- Footer stating the title of the paper and the case number (with judge's initials), per Civil
  L.R. 3-4(c)(3) — see the Civil L.R. 3-4 compliance section in
  `references/standing_order_topics.md`. Double-check the case number and initials in the footer
  match the caption box exactly; a mismatch between the two is an easy, embarrassing error to
  introduce when copying values into two different places in the script.
- **Page numbering starts on the second page, numbered "1," with no page number on the caption
  page.** The caption (first) page carries no page number in its footer at all; the page that
  follows it is page "1," and numbering runs consecutively (2, 3, 4 …) from there. Implement this
  with a **next-page section break placed right after the caption** (so the caption page is its
  own first section and the body begins in a second section), then in the second section restart
  page numbering at 1 (`w:pgNumType w:start="1"` in that section's `sectPr`) and suppress the
  number on the caption page (either give the first section a footer with no PAGE field, or set
  that section's footer to omit it). Keep everything else about the footer identical: the PAGE
  field stays right-aligned at the same tab position (right tab at 8640 twips) on the "CASE NO. …"
  line, and the page number keeps the same 10pt Times New Roman size/font as the rest of the
  footer. The only change is *where numbering starts and that the caption page has none* — not the
  footer's position, size, or font. (In the `docx` npm library this means two sections: section 1
  = caption page, section 2 = body with `pageNumberStart: 1`; the caption-page footer simply
  doesn't include the `PageNumber` field.)

## Line-numbered pleading paper (optional)

If the draft needs the firm's exact 28-line pleading-paper number column and vertical divider
rules, run `scripts/inject_line_numbers.py` on the generated file's `word/header1.xml` — see the
usage notes at the top of that script, including its verification limitation (LibreOffice-headless
does not reliably render the framed numbering paragraphs, so say so rather than asserting the
render is correct without the user confirming in real Word).

## Word comments to anchor

Use the docx skill's `scripts/comment.py`.

**Service status (ties back to the Step 2 docket check).** Anchor a comment to the Service
placeholder text in Topic 1:

- If the docket check found a service date: the comment must state which docket-tracking site was
  used (e.g., CourtListener, PacerMonitor, UniCourt), the service date(s) found, and the ECF
  document number where the return of service appears — e.g., "Found via CourtListener docket for
  Case No. [X]: summons returned executed [date], ECF No. [Y]. Confirm against PACER before
  filing."
- If the docket check found nothing or wasn't attempted: the comment must say so plainly and
  instruct the user to check the docket themselves and insert the service date(s) directly — e.g.,
  "No service information found via public docket search. Confirm service status and insert
  date(s) directly from PACER or your own records before filing."

Do not skip this comment in either case — the point is to make the sourcing of that placeholder
traceable, not to leave it silently unresolved.

**The other required comments**, each described where its text is defined:

| Anchor | Defined in |
|---|---|
| Non-CAFA subject matter jurisdiction sentence | `templates/topic_language.md`, Topic 1 |
| Non-domicile personal jurisdiction sentence | `templates/topic_language.md`, Topic 1 |
| Venue sentence (always) | `templates/topic_language.md`, Topic 1 |
| Topic 7 initial-disclosures date or blank (always) | `templates/topic_language.md`, Topic 7 |
| Class-cert hearing date, when computed | `references/calendar_scheduling.md`, step 4 |
| Filer name in the Signature Attestation | below |
| Lead trial counsel name in the AI Certification | below |

## End-of-document attestations

Two distinct blocks, in this order, after the ending signature blocks. Both are exempt from the
document-wide 0.5" first-line-indent/justify rule for their titles and signature lines, the same
way the signature block is (single-spaced, not justified) — only the body paragraph of each gets
a 0.5" first-line indent (first line only; the rest flush at the 0" left margin).

### 1. Signature Attestation — always included, every draft

Copy word-for-word and in the same format as the real *Hokes v. Zeus Networks* template:

- Title "SIGNATURE ATTESTATION" — bold, underlined, all caps, centered.
- Indented paragraph: "I, [filer name], as the ECF user and filer of this document, attest
  pursuant to N.D. Cal. L.R. 5(i)(3) that each of the other signatories have concurred in the
  filing of the document." Use the first-listed/lead attorney from the signature block as the
  filer (matching the real template's convention, where the filer is the same person who signs
  first) — and anchor a Word comment to this name confirming the user should verify who will
  actually be the ECF filer, since this is an assumption, not a fact pulled from the complaint.
- Skip a line, then: "Dated: [DATE]" followed by three or four tabs to right-align an italicized,
  underlined "/s/ [filer name]" on the same line, with the filer's name printed (not italicized)
  directly beneath it, aligned under the signature.

### 2. Generative AI Certification — conditional, only if required

Check the assigned judge's standing order (from Step 2) and the N.D. Cal. local rules for any
requirement that AI-assisted filings include a certification of this kind (Judge
Martínez-Olguín's Standing Order for Civil Cases, Section H.4, is a confirmed example — but check
fresh for whatever judge is actually assigned, since this varies by judge and isn't a
district-wide rule). If required:

- **Remove any earlier inline AI-certification placeholder from the top of the document** (this
  skill previously placed a "CERTIFICATION REGARDING USE OF GENERATIVE ARTIFICIAL INTELLIGENCE"
  notice near the top, right after the intro paragraph — that placement was superseded; the
  certification belongs at the very end now, after the Signature Attestation, not duplicated at
  both places).
- Title "GENERATIVE AI CERTIFICATION" — bold, underlined, all caps, centered (same styling as the
  Signature Attestation title).
- Indented paragraph: "This document was produced in part using generative AI. I, [name of
  attorney] and lead trial counsel, certify pursuant to [Section/Rule citation] that I have
  personally verified the accuracy of the AI-generated content in this submission." Fill in the
  attorney's name (use the same lead attorney assumption as the Signature Attestation, flagged the
  same way with a Word comment reminding the user to confirm who is actually designated lead trial
  counsel) and the specific section/rule citation from whichever standing order or local rule
  actually imposes the requirement (e.g., "Section H.4 of Judge Martínez-Olguín's Standing Order
  for Civil Cases").
- Skip two lines, then the same "Date: [DATE]" + tabs + italicized/underlined "/s/ [name]" + plain
  printed name pattern as the Signature Attestation.
- **If no such requirement is found** for the assigned judge or under the local rules, omit this
  block entirely — don't include a placeholder AI-certification notice anywhere in the document if
  nothing in the applicable rules actually requires one.

## Verification before presenting

Convert to PDF and view the pages per the docx skill's verification step. **Dispatch this
verification to a subagent** rather than reviewing inline: hand it the rendered PDF plus this
checklist and have it report back only the pass/fail list and any specific pages/lines that
deviate.

- First-line-indent-only body text
- Continuous exact-24pt spacing
- Uniform 10pt footer
- Curly quotes throughout
- Two spaces after sentence-ending periods
- Correct page-numbering start (none on the caption page, "1" on the next)
- Caption-page counsel table borders invisible
- Bold firm names in every signature block
- 3″ signature-block indent
- Auto-date fields present in both ending signature blocks

This is a good subagent boundary because the check is mechanical, independent of the drafting
judgment calls made earlier, and its page-by-page detail would otherwise clutter the main
conversation. Fix anything it flags before presenting the document.
