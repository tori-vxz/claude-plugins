# Citation style — Bluebook, not California Style Manual

All pinpoint citations to the complaint (and to any other document) in this skill's drafts
follow *The Bluebook: A Uniform System of Citation*, not the California Style Manual. This firm
is California-based, so it's an easy habit to slip into state conventions by default; watch for
it specifically.

- **Paragraph/page ranges use an en dash (–), not a hyphen (-).** Bluebook Rule 3.2 requires an
  en dash for continuous number ranges — e.g., `Compl. ¶¶ 22–44.`, not `Compl. ¶¶ 22-44.` This
  applies to every pincite range in the draft, not just the jurisdiction paragraph.
- Use "Compl." (not "Complaint" spelled out, and not "1CT" or other California record-citation
  shorthand) with no comma before the pincite symbol — e.g., `Compl. ¶ 9`, not `Complaint, ¶ 9`
  or `Compl., ¶ 9`.
- Multiple non-consecutive paragraphs: `¶¶ 5, 9` (comma-separated, still double pilcrow).
  Consecutive ranges: `¶¶ 5–9` (en dash, no comma).
- **A citation standing alone as its own sentence is not wrapped in parentheses** under federal
  Bluebook — it is written as its own sentence, terminated by its own period, directly after the
  sentence it supports — e.g., `...in this District. Compl. ¶ 11.` This is a deliberate
  divergence from the California Style Manual, which wraps a standalone citation in parentheses
  with the period inside (`(Compl. ¶ 11.)`); that state-court habit is easy to slip into for a
  California firm, so keep these federal drafts unparenthesized.
- **Introductory signals are italicized.** Under Bluebook Rule 1.2, a signal that introduces a
  citation — `See`, `See also`, `Cf.`, `But see`, `See generally`, etc. — is set in italics,
  e.g., *See* Compl. ¶ 8. The California Style Manual does **not** italicize these signals, so
  this is another Bluebook-vs-state divergence worth flagging explicitly: a signal-italicization
  slip is easy to make even after the parentheses issue is fixed, because the signal sits right
  up against the pincite. In the `docx` build, put the signal in its own italicized `TextRun`
  (`italics: true`), separate from the un-italicized remainder of the citation.
- **Nonbreaking space after every ¶ / ¶¶ / § / §§ symbol.** Whenever a paragraph symbol (¶, ¶¶)
  or section symbol (§, §§) directly precedes the number or letter it points to, join the
  symbol(s) to that number/letter with a **nonbreaking space** (U+00A0, `&#160;`), not an
  ordinary space — so the symbol never gets stranded at the end of a line while its number wraps
  to the next. This applies everywhere the symbols appear: pincites to the complaint (`¶ 9`,
  `¶¶ 22–44`), statutory sections (`28 U.S.C. § 1332(d)(2)(A)`, `Cal. Bus. & Prof. Code
  § 17200`), and any other cited section or paragraph. In the `docx` build, put the nonbreaking
  character directly in the `TextRun` text; when copying one of this skill's fixed template
  sentences (CAFA jurisdiction, venue, etc.), reproduce the nonbreaking space the same way. Only
  the space immediately between the symbol(s) and the following number/letter is nonbreaking —
  ordinary spaces elsewhere in the citation stay ordinary.
