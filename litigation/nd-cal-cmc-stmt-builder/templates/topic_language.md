# Fixed language by topic

Standard text for the opening paragraph and Topics 1, 6–14, and 16–19. Every block below is a
global default used in **every** draft, adjusted only for singular vs. plural per the counting
rules at the top of this file. Topic 15 has its own file: `templates/schedule_table.md`.

**Which topics get a position split.** Topics 1, 7, 8, 10, 12, 13, 14, and 16–19 are written as
one continuous joint statement — no "Plaintiffs' Position" / "Defendant's Position" labels and
no bracketed defendant placeholder — matching the real *Hokes v. Zeus Networks* filing. Every
other topic gets Plaintiff's position followed by the standard bracketed defendant placeholder.

---

## Counting rules — singular vs. plural, and pronoun style

Applies to the whole draft, not just the blocks below.

**Plaintiffs.** Count the named plaintiffs from the complaint's caption: on the first page, the
caption block lists the plaintiff(s) in its opening line(s), with multiple named plaintiffs
separated by commas (e.g., "MICHAEL SELBY and CHRISTY CLIFFT, individually and on behalf of all
others similarly situated," names two plaintiffs). Count only the named individuals/entities,
not the "on behalf of all others similarly situated" class language. Use that count to drive
"Plaintiff" vs. "Plaintiffs" (and "Plaintiff's" vs. "Plaintiffs'") consistently across every
section of the draft.

**Defendants.** Count the named defendants from the caption after the "v." (or "vs."), with
multiple named defendants separated by commas (e.g., "v. BRAND EVANGELISTS FOR BEAUTY INC.,"
names one defendant; "v. ACME CORP., JOHN SMITH, and WIDGET LLC," would name three). Use that
count to drive "Defendant" vs. "Defendants" (and "Defendant's" vs. "Defendants'") consistently
across every section — the caption box, the footer references, the standard-language paragraphs
below, and every Defendant's Position placeholder.

**The two counts are independent.** A case can have one plaintiff and multiple defendants,
multiple plaintiffs and one defendant, or any other combination. Determine each separately from
its own side of the caption and don't assume they match.

**Pronouns.** Prefer repeating "Plaintiff"/"Plaintiffs" and "Defendant"/"Defendants" over
pronouns wherever the sentence reads naturally that way (this also sidesteps gendering the
individual parties). Where a pronoun is genuinely needed for readability, use gender-neutral
"they/them/their" regardless of how many named parties there are or their individual genders —
never "he/she" or gendered pronouns, never guess an individual's gender from their name, and
never use a personal pronoun for an entity defendant at all.

---

## Opening paragraph

Goes before Topic 1, at the very start of the draft's substantive text — after the caption box.
Format like the rest of the main text (12pt Times New Roman, exact 24pt double-spacing); no
special treatment.

> Plaintiff[s] [name(s)] and Defendant[s] [name(s)], the Parties to the above-titled action
> (collectively, the "Parties"), hereby submit this Joint Case Management Statement pursuant to
> the Standing Order for All Judges of the Northern District of California, Civil Local Rule
> 16-9.

- Pull every named plaintiff and every named defendant from the complaint's caption and name all
  of them here — don't stop at the first name or abbreviate to "et al." List two names joined by
  "and" with no comma; three or more with a serial comma (e.g., "A, B, and C").
- "Plaintiff"/"Plaintiffs" and "Defendant"/"Defendants" each take their own singular/plural
  form independently, based on that side's own party count.
- This replaces the more expansive explanatory paragraph used in earlier drafts (the one noting
  that Defendant's positions are placeholders pending defense counsel's input) — use this exact
  template instead, matching the real *Hokes v. Zeus Networks* filing.

---

## Topic 1 — Jurisdiction and Service

No position split. One continuous joint statement, in this order: subject matter jurisdiction,
personal jurisdiction, venue, service — all in the same unlabeled paragraph.

### 1. Subject matter jurisdiction sentence

Check the complaint's own jurisdictional paragraph first.

**If the complaint invokes CAFA, 28 U.S.C. § 1332(d)(2)(A):** use this fixed template sentence,
adjusted for singular vs. plural based on how many classes the complaint actually defines (count
the complaint's own named classes/subclasses in its class definitions — e.g., a complaint
defining both a "Nationwide Class" and a "California Subclass" has two classes and takes the
plural form; don't default to either form without checking):

> Singular: This Court has subject matter jurisdiction pursuant to 28 U.S.C. § 1332(d)(2)(A)
> because this is a putative class action in which the aggregate claims of all members of the
> proposed Class exceeds $5,000,000, exclusive of interest and costs, and at least one member of
> the proposed Class is a citizen of a state different from Defendant.
>
> Plural: This Court has subject matter jurisdiction pursuant to 28 U.S.C. § 1332(d)(2)(A)
> because this is a putative class action in which the aggregate claims of all members of the
> proposed Classes exceed $5,000,000, exclusive of interest and costs, and at least one member
> of the proposed Classes is a citizen of a state different from Defendant.

Immediately after this sentence, add a Bluebook-format pinpoint citation to the complaint's
jurisdictional paragraph — e.g., `Compl. ¶ 9.` — using whatever paragraph number that complaint
actually uses (don't assume ¶ 9; check).

**If the complaint invokes a different jurisdictional basis** (federal question under 28 U.S.C.
§ 1331, diversity under § 1332(a), a specific federal statute, etc.): copy the complaint's own
jurisdictional language as the basis for this sentence (paraphrasing lightly is fine; this is
the client's own pleading, not a third-party copyrighted source, so faithfulness to its
substance matters more than avoiding quotation), cite the complaint's jurisdictional paragraph
in Bluebook format the same way, and **anchor a Word comment to this sentence reminding the user
to double-check subject matter jurisdiction** — this skill's standard template is built around
CAFA, so any other basis is a deviation worth flagging rather than silently treating as routine.

### 2. Personal jurisdiction sentence

Follows immediately after the subject matter jurisdiction sentence, same unlabeled paragraph.

**If the complaint states that Defendant is domiciled in, headquartered in, incorporated in, or
has its (primary) place of business in California**, use this fixed template, filling in
`[insert why]` with whichever of those bases the complaint actually alleges, in the complaint's
own words as closely as possible:

> Personal jurisdiction over Defendant is proper because Defendant [insert why] in California.
> *See* Compl. ¶ [cite].

Example: if the complaint alleges the defendant's primary place of business is in Antioch,
California, at paragraph 8, write: "Personal jurisdiction over Defendant is proper because
Defendant's primary place of business is located in California. *See* Compl. ¶ 8." (En dash for
any pincite range; no comma before the pincite — see `references/citation_style.md`.)

**Otherwise** (e.g., the theory rests on purposeful availment/minimum contacts rather than
domicile — a foreign or out-of-state defendant that sells into California, for instance): copy
the complaint's own personal jurisdiction allegations as close to verbatim as its wording allows
(don't paraphrase this one into different language — this "other" category has no fixed template
the way the California-domicile case does, so the complaint's own phrasing is the standard),
with a Bluebook pincite the same way, and **anchor a Word comment to this sentence reminding the
user to double-check the personal jurisdiction portion** — the same treatment given to a
non-CAFA subject matter jurisdiction basis above. Do not use the domicile-based template for a
defendant the complaint doesn't actually allege is domiciled/headquartered/incorporated/based in
California — check rather than defaulting to either form.

### 3. Venue sentence

Immediately after the personal jurisdiction sentence and before the service sentence. Fixed
global template, normal main-text formatting:

> Venue is proper in this District pursuant to 28 U.S.C. § 1391 because a substantial part of
> the events alleged in the Complaint giving rise to Plaintiff[s'/'s] claim[s] [are/is] alleged
> to have occurred in this District and Plaintiff[s] [name(s)] reside[s] in this District.

- The "events giving rise to claims" clause takes its singular/plural form from the total
  plaintiff count — "Plaintiffs' claims are" for multiple plaintiffs, "Plaintiff's claim is" for
  one.
- The "resides in this District" clause is different: it must name only the plaintiff(s) the
  complaint actually alleges reside in *this specific district*, not just this state or the total
  plaintiff count. California has four federal districts (Northern, Eastern, Central, Southern)
  — check each named plaintiff's alleged city/county of residence against which district that
  location actually falls in (e.g., Antioch is in Contra Costa County, N.D. Cal.; Encino is in
  Los Angeles, C.D. Cal. — a plaintiff residing in Encino would NOT support this clause and
  should be omitted from it even though they're still a plaintiff in the case).
  - If exactly one plaintiff resides in this district, use their full name and "resides"
    (singular), even if the case has multiple plaintiffs overall — e.g., "Plaintiff Michael
    Selby resides in this District."
  - If more than one plaintiff resides in this district, name all of them in full and use
    "reside" (plural).
  - If no named plaintiff is alleged to reside in this district, do not force this clause — flag
    it explicitly in the Word comment below instead, since venue would then rest on the
    events-based basis alone, and say so rather than silently dropping the residency clause.
- **Always anchor a Word comment to this sentence** reminding the user to double-check venue and
  the domicile of the plaintiffs — this determination depends on matching alleged residences to
  federal districts, which is exactly the kind of detail worth a second look before filing,
  regardless of how confident the analysis seems.

### 4. Service sentence

Follows the venue sentence in the same unlabeled paragraph, still with no position split.
Service status isn't knowable from the complaint alone, so this stays a placeholder per the
docket-check workflow in `references/intake_and_research.md` — just without a "Plaintiffs'
Position:" label prefix. Anchor the service-status Word comment described in
`references/docx_build.md`.

---

## Topic 6 — Evidence Preservation

Plaintiff's portion, every draft:

> Singular: Plaintiff certifies that Plaintiff has reviewed the Guidelines Relating to the
> Discovery of Electronically Stored Information. Plaintiff's counsel has taken steps to advise
> Plaintiff about the need to preserve evidence.
>
> Plural: Plaintiffs certify that Plaintiffs have reviewed the Guidelines Relating to the
> Discovery of Electronically Stored Information. Plaintiffs' counsel has taken steps to advise
> Plaintiffs about the need to preserve evidence.

Still leave Defendant's portion as the standard bracketed placeholder — this topic requires an
actual joint certification once both sides have conferred, and Defendant's confirmation that it
has done the same cannot be assumed.

---

## Topic 7 — Disclosures

No position split. Normal main-text formatting.

> The Parties will exchange initial disclosures by [ ].

**If the 26(f) lookup produced a governing conference date,** fill in the blank with the
resulting 14-days-after date (already FRCP-6-adjusted) instead of leaving it blank, and anchor a
Word comment there stating the source: the 26(f) conference/M&C date used, where it came from
(the matter's calendar event, or the date the user typed in directly), and that it's 14 days out
per the firm's 26(f) protocol, adjusted for weekends/holidays under FRCP 6(a) if applicable —
e.g., "Initial disclosures date calculated as 14 days after the 26(f) conference on [date], per
calendar event '[event title]' on the matter [number] calendar." A filled-in date without an
explanation of where it came from is just as easy to misplace trust in as an unexplained blank.

**Otherwise** (the lookup was skipped, abandoned, or never produced a date), leave the date as a
bracketed blank — not a filled-in date and not the usual red/bold placeholder wording. Do not
fabricate or estimate a date, since it depends on when the Rule 26(f) conference and/or Rule 16
CMC actually occur. Anchor a Word comment to that blank instructing the user to fill in the date
initial disclosures are due, e.g., "Insert the date initial disclosures are due (see the 26(f)
Protocol summary in `references/bf_26f_scheduling_protocol.md` for the standard 14-day timing
rule)." Do not skip this comment — a bare blank with no explanation is easy to miss on review.

Whichever branch applies, the Topic 15 initial-disclosures row must show the same value.

---

## Topic 8 — Discovery

No position split. Normal main-text formatting.

> The Parties have agreed to accept service of discovery requests and responses via email. The
> Parties further agree to cooperate and work in good faith toward reaching an agreement on a
> stipulation regarding the preservation and production of electronically stored information, as
> well as a protective order governing the discovery and use of confidential information. If an
> agreement cannot be reached, the Parties will seek Court intervention.

---

## Topic 9 — Class Actions

For every putative class action draft, in place of case-specific narrative:

> Singular: Dates for Plaintiff's Motion for Class Certification and Defendant's Opposition are
> proposed below. All attorneys of record have reviewed the Procedural Guidance for Class Action
> Settlements.
>
> Plural: Dates for Plaintiffs' Motion for Class Certification and Defendants' Opposition are
> proposed below. All attorneys of record have reviewed the Procedural Guidance for Class Action
> Settlements.

This replaces the more detailed case-specific class-description narrative previously used here
(proposed class definitions, Rule 23 theory, etc.) — that substantive detail belongs in Topic 2
(Facts) and the Civil L.R. 16-9(b) class-action supplement discussion, not repeated again in
Topic 9. Keep Topic 9 this short and procedural, matching the real *Hokes v. Zeus Networks*
filing exactly. Still propose actual class-certification briefing dates in Topic 15, since the
dates "proposed below" referenced here need to actually appear somewhere in the document.

---

## Topic 10 — Related Cases

No position split, no bracketed placeholder. Normal main-text formatting.

> The Parties are not aware of any related cases.

---

## Topic 11 — Relief

Different internal structure from every other section, matching the real *Hokes v. Zeus
Networks* template exactly — don't use the usual inline "Plaintiffs' Position: [text...]"
pattern here. Instead:

1. **"Plaintiff's Position" / "Plaintiffs' Position"** stands alone on its own line — bold and
   italicized, NOT indented, singular/plural per the counting rules. (This part matches the rest
   of the draft; just don't put the next sentence on the same line/paragraph as it.)
2. On the **next line**, indented so the text starts half an inch in (one default tab stop — use
   an actual tab character/element, not a paragraph indent, matching the template), the
   sentence: "Plaintiff[s] ha[s/ve] requested the following relief as set forth in the
   Complaint:" — singular/plural per the counting rules.
3. **The list of requested relief itself**, copied from the complaint's **"PRAYER FOR RELIEF"**
   section (or equivalent heading — sometimes titled "WHEREFORE" or "Prayer for Relief"), one
   list item per lettered sub-paragraph in the complaint, in the same order, as close to verbatim
   as the complaint's own wording allows. Use a lowercase-letter list format — "(a)", "(b)",
   "(c)"... — matching the real template's list style (12pt Times New Roman, same font/size as
   the rest of the draft; the list itself uses tighter spacing than the double-spaced main
   narrative — after=240/line=280-exact rather than the usual 480-exact — matching this firm's
   actual convention for prayer-for-relief lists specifically).

Do not paraphrase or summarize the relief list into a single running sentence (the prior version
of this template did that, and it doesn't match the real filing) — pull the actual lettered items
from the complaint and list them out. If the complaint's Prayer for Relief doesn't cleanly break
into lettered items (e.g., it's plain prose), preserve its structure as faithfully as possible
rather than forcing artificial letters, and note the deviation to the user.

Defendant's Position for this topic keeps its usual bracketed-placeholder treatment, including
the note about damages methodology — only Plaintiff's side gets this restructured format.

Topic 11 is also exempt, in its entirety (label, intro sentence, and lettered list), from the
document-wide first-line-indent rule — see `references/docx_build.md`.

---

## Topic 12 — Settlement and ADR

No position split and no separate Defendant placeholder — a single joint "The Parties"
statement, normal double-spaced main-text formatting (not the tighter Relief-list spacing). This
is a deliberate change from an earlier version that split the topic and, on a "no" answer,
dropped in a bracketed placeholder — don't do that anymore.

Every time this skill drafts Topic 12, still ask the user directly (a single yes/no question is
enough — use the elicitation tool if available) whether they have "discussed ADR and would
mediate with a private mediator." Ask fresh each time — don't assume an answer from context or a
prior draft, since this is a case-specific fact that can change.

**The text of the section is the same regardless of the answer** (adjusted only for
singular/plural):

> The Parties have reviewed the ADR procedures in ADR L.R. 3-5. The Parties are open to engaging
> in settlement discussions with a private mediator, provided there is a sufficient exchange of
> information to permit informed discussions.

The answer changes only whether part of that text is highlighted:

- **If yes** (they have agreed to mediate with a private mediator): use the language above with
  no highlighting; it's an accurate statement of the Parties' position.
- **If no / not yet**: use the *exact same* language, but apply a yellow text highlight to
  everything **after the first sentence** — i.e., highlight the second sentence ("The Parties are
  open to engaging in settlement discussions with a private mediator, provided there is a
  sufficient exchange of information to permit informed discussions."), leaving the first
  sentence ("The Parties have reviewed the ADR procedures in ADR L.R. 3-5.") unhighlighted. The
  highlight flags for the user that this forward-looking statement about private mediation is
  drafted language they still need to confirm or revise, since agreement hasn't been reached. In
  the `docx` build, apply the highlight with `w:highlight w:val="yellow"` on the run(s) carrying
  the second sentence (the `docx` npm library exposes this as `highlight: "yellow"` on the
  `TextRun`).

---

## Topic 13 — Other References

No position split, no bracketed placeholder. Normal double-spaced main-text formatting.

> The Parties do not believe that the case is suitable for reference to binding arbitration or a
> special master at this time. The Parties have not consented to the jurisdiction of a
> magistrate judge.

---

## Topic 14 — Narrowing of Issues

No position split, no bracketed placeholder. Normal double-spaced main-text formatting.

> The Parties are not aware of any issues that may be narrowed at this time.

---

## Topics 16–19

None of these four get a position split. Exact global language in every draft, adjusted for
singular/plural, normal main-text formatting.

- **Topic 16 (Trial):** "Plaintiff[s] ha[s/ve] demanded a jury trial of any claims triable by a
  jury, and the Parties estimate the trial to last approximately 5-7 court days."
- **Topic 17 (Disclosure of Non-Party Interested Entities or Persons):** "The Parties are not
  aware of any non-party interested entities or person, other than putative class members."
  **Do not include the real template's second sentence** ("Plaintiff's Counsel is forwarding the
  costs and expenses associated with prosecuting her claims.") — omit it entirely; this is the
  one deliberate deviation from the template for these four topics, since litigation
  funding/cost arrangements are case-specific and shouldn't be asserted as a global default.
- **Topic 18 (Professional Conduct):** "Counsel for the Parties have reviewed the Guidelines for
  Professional Conduct for the Northern District of California and agree to comply with them."
- **Topic 19 (Such Other Matters):** "The Parties are not presently aware of any other matters
  that may facilitate the just, speedy, and inexpensive disposition of this matter."
