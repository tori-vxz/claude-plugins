const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  PageNumber, Header, Footer, TabStopType, TabStopPosition, UnderlineType,
  LineRuleType, LineNumberRestartFormat, Tab, LevelFormat,
  SimpleField, SectionType,
} = require("docx");
const fs = require("fs");

const FONT = "Times New Roman";
const SZ = 24; // 12pt
const SZ_FOOTER = 20; // 10pt — uniform footer size (title + case-number/page lines)

// Main text: exactly 24pt line spacing, 12pt Times New Roman. Exempt blocks (caption box,
// counsel block at the top, signature blocks at the end) explicitly override lineRule to AUTO
// and supply their own (smaller, single-spaced) line values — see each call site below.
const MAIN_LINE = 480; // 24pt in twentieths-of-a-point, used with lineRule EXACT

// Convert straight quotes/apostrophes to their curly (typographic) equivalents so the entire
// document uses “ ” ‘ ’ rather than " ' — the firm's house style, applied universally. Every
// human-readable string is routed through this before it becomes a TextRun (see T(),
// placeholder(), positionLabelPara(), scheduleCell(), sectionHeading()). The heuristic: a double
// or single quote right after whitespace / an opening bracket / a dash / the start of the string
// opens (“ or ‘); any other quote closes or is an apostrophe (” or ’). It is idempotent — the
// curly characters are left untouched — so it's safe to run over text that is already curly.
function sq(text) {
  return String(text)
    .replace(/(^|[\s([{<–—])"/g, "$1“") // opening double quote
    .replace(/"/g, "”")                              // closing double quote
    .replace(/(^|[\s([{<–—])'/g, "$1‘")  // opening single quote
    .replace(/'/g, "’");                             // closing single quote / apostrophe
}

// Double-space after sentence-ending periods (the firm's house style — see the "two spaces
// after a sentence-ending period" rule in SKILL.md Step 4). The hard part is NOT over-firing on
// abbreviations and citations that merely contain a period mid-sentence. The heuristic here only
// doubles a ". " when the next visible character is a capital letter or an opening quote/paren
// (i.e., a new sentence plausibly begins), AND the token immediately before the period is not a
// known abbreviation or a single-letter initial. Followed-by a symbol/digit (e.g. `§ 1332`,
// `¶ 9`, `No. 179586`) never triggers doubling because those aren't capital letters. It is
// idempotent: once a gap is two spaces, the lookahead sees a space (not a capital) and skips it.
const NO_DOUBLE = new Set([
  "Cal", "Civ", "Bus", "Prof", "Code", "No", "Nos", "Inc", "Corp", "Ltd", "Co",
  "v", "vs", "Fed", "R", "P", "U.S.C", "U.S", "Rule", "L.R", "ADR", "St", "Ste",
  "Blvd", "Rd", "Ave", "Dr", "Mr", "Mrs", "Ms", "Hon", "e.g", "i.e", "et", "seq",
  "etc", "Ex", "Am", "P.A", "L.L.P", "L.L.C",
]);
function ds(text) {
  return String(text).replace(/([A-Za-z.&']+)\. (?=[A-Z“"'(])/g, (m, word) => {
    const w = word.replace(/[^A-Za-z.]/g, "");
    if (w.replace(/\./g, "").length === 1) return m; // single-letter initial, e.g. "L." "S."
    if (NO_DOUBLE.has(w) || NO_DOUBLE.has(w.replace(/\.+$/, ""))) return m;
    return `${word}.  `; // sentence-ending period → two spaces
  });
}

// ---------- helpers ----------
// contextualSpacing ("Don't add space between paragraphs of the same style") is set on every
// paragraph-building helper below (item 4 in SKILL.md Step 4) — belt-and-suspenders with the
// zeroed before/after spacing so Word never injects a style-based gap between same-style paras.
function P(children, opts = {}) {
  return new Paragraph({
    spacing: { after: 0, before: 0, line: MAIN_LINE, lineRule: LineRuleType.EXACT, ...opts.spacing },
    alignment: opts.alignment || AlignmentType.LEFT,
    contextualSpacing: true,
    children,
    ...opts,
  });
}

function T(text, opts = {}) {
  return new TextRun({ text: ds(sq(text)), font: FONT, size: SZ, ...opts });
}

// Exempt (caption-adjacent): single-spaced, auto line rule — used only for the court-name
// lines directly above the caption box, not for main text.
function centerLine(text, opts = {}) {
  return P([T(text, opts)], { alignment: AlignmentType.CENTER, spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO } });
}

function bodyPara(text, opts = {}) {
  return P([T(text)], opts);
}

function placeholder(text) {
  return new TextRun({
    text: sq(text),
    font: FONT,
    size: SZ,
    bold: true,
    color: "C00000",
  });
}

function sectionHeading(num, title) {
  // before: 0 — no blank line before a heading; the exact-24pt line rhythm alone separates it
  // from the prior paragraph, keeping the whole body at continuous exact 24pt.
  return new Paragraph({
    spacing: { before: 0, after: 0, line: MAIN_LINE, lineRule: LineRuleType.EXACT },
    contextualSpacing: true,
    children: [
      new TextRun({ text: `${num}.`, font: FONT, size: SZ, bold: true }),
      new TextRun({ text: sq(`\t${title}`), font: FONT, size: SZ, bold: true, underline: { type: UnderlineType.SINGLE } }),
    ],
    tabStops: [{ type: TabStopType.LEFT, position: 720 }],
  });
}

function plaintiffLabel() {
  return new TextRun({ text: "Plaintiffs' Position: ", font: FONT, size: SZ, bold: true, italics: true });
}

// 0.5 inch, used for the document-wide body-paragraph FIRST-LINE indent (everything except
// page 1's caption/counsel block, Section 11 in its entirety, and the Section 15 schedule
// table). Applied as `firstLine`, not `left`, so only the opening line of each paragraph is
// tabbed in and the rest runs the full measure — the classic legal-brief look.
const BODY_INDENT = 720;

// Standalone label paragraph — bold+italic, NOT indented, own line. Used whenever a section
// still splits into "Plaintiffs' Position" / "Defendant's Position".
function positionLabelPara(text) {
  return new Paragraph({
    // before: 0 — continuous exact-24pt spacing, no extra blank line before the label.
    spacing: { before: 0, after: 0, line: MAIN_LINE, lineRule: LineRuleType.EXACT },
    alignment: AlignmentType.LEFT,
    contextualSpacing: true,
    indent: { left: 0 },
    children: [new TextRun({ text: sq(text), font: FONT, size: SZ, bold: true, italics: true })],
  });
}

// Main body-text paragraph: 0.5" FIRST-LINE indent, fully justified, exact-24pt main-text
// spacing, zero before/after spacing (continuous double-spacing — see the "no extra paragraph
// spacing" rule in standing_order_topics.md). This is the default for every narrative paragraph
// in the document except page 1's caption/counsel block, the ending signature block, Section 11
// in its entirety, and the Section 15 schedule table (all of which keep their own formatting).
function bodyP(children, opts = {}) {
  return new Paragraph({
    spacing: { after: 0, before: 0, line: MAIN_LINE, lineRule: LineRuleType.EXACT, ...opts.spacing },
    alignment: AlignmentType.JUSTIFIED,
    contextualSpacing: true,
    indent: { firstLine: BODY_INDENT, ...opts.indent },
    children,
    ...opts,
  });
}

// A full "Plaintiffs' Position" / "Defendant's Position" block: label on its own unindented
// line, then the substantive text as a separate, indented+justified paragraph. Returns an array
// of two paragraphs — spread this into `children`.
function positionBlock(labelText, bodyChildren, bodyOpts = {}) {
  return [positionLabelPara(labelText), bodyP(bodyChildren, bodyOpts)];
}

function defendantPositionBlock(note = "Defendant's Position:") {
  return positionBlock(note, [placeholder("[DEFENDANT'S POSITION: TO BE COMPLETED BY DEFENSE COUNSEL]")]);
}

// ---------- end-of-document attestations (Signature Attestation + conditional AI cert) ----------
// Both exempt from the document-wide indent/justify rule for their titles and signature lines
// (single-spaced, matching the ending signature block's own exemption) — only the body
// paragraph gets the 0.5" indent, per the user's explicit instruction, without full
// justification (this is a short notice, not main narrative text).
function attestationTitle(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: MAIN_LINE, after: MAIN_LINE, line: 240, lineRule: LineRuleType.AUTO },
    contextualSpacing: true,
    children: [new TextRun({ text, font: FONT, size: SZ, bold: true, underline: { type: UnderlineType.SINGLE } })],
  });
}

function attestationBody(runChildren) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    // First-line indent only (matches the document-wide first-line-indent rule and the SKILL.md
    // description of these blocks) — the opening line is tabbed in, the rest flush at 0".
    indent: { firstLine: BODY_INDENT },
    spacing: { after: 200, line: 240, lineRule: LineRuleType.AUTO },
    contextualSpacing: true,
    children: runChildren,
  });
}

// Date/signature line: "<label>: [DATE]" on the left, tabbed to a right-aligned italicized+
// underlined "/s/ Name", with the plain printed name right-aligned on the line below it.
function attestationSignatureLines(dateLabel, name) {
  return [
    new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: 8640 }],
      spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO },
      contextualSpacing: true,
      children: [
        T(`${dateLabel}: [DATE]`),
        new TextRun({ children: [new Tab()], font: FONT, size: SZ }),
        new TextRun({ text: `/s/ ${name}`, font: FONT, size: SZ, italics: true, underline: { type: UnderlineType.SINGLE } }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.RIGHT,
      spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO },
      contextualSpacing: true,
      children: [T(name)],
    }),
  ];
}

// ---------- ending signature blocks (Hokes template format) ----------
// 3 inches (not 3.5) — chosen because several detail lines (e.g., street addresses, attorney
// names with bar numbers) don't fit on one line if the aligned column starts at 3.5".
const SIG_INDENT = 4320;

// Auto-updating Word date field, formatted "Month d, yyyy" (e.g. "August 13, 2026") — used after
// the "Dated:" label in the ending counsel signature blocks (item 3 in SKILL.md Step 4), in
// place of a literal "[DATE]" placeholder. The field re-evaluates whenever the document is opened.
function dateField() {
  return new SimpleField('DATE \\@ "MMMM d, yyyy"');
}

// "Dated:" at the left margin, then the auto-date field, then a tab to SIG_INDENT where the bold
// firm name begins. (Firm name is bold — item 5.)
function sigDateLine(dateLabel, firmNameRun) {
  return new Paragraph({
    tabStops: [{ type: TabStopType.LEFT, position: SIG_INDENT }],
    spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO },
    contextualSpacing: true,
    children: [
      T(`${dateLabel}: `),
      dateField(),
      new TextRun({ children: [new Tab()], font: FONT, size: SZ }),
      firmNameRun,
    ],
  });
}

// "By:" aligned to the signature block at SIG_INDENT (3"), then a tab to the "/s/ Name" signature
// (or a placeholder run, for the defense block). Item 3 requires "By:" to line up with the block,
// not sit at the far left margin — so a leading tab pushes "By:" itself to SIG_INDENT, and a
// second tab stop carries the signature just past it.
function sigByLine(signatureRun) {
  return new Paragraph({
    tabStops: [
      { type: TabStopType.LEFT, position: SIG_INDENT },
      { type: TabStopType.LEFT, position: SIG_INDENT + 720 },
    ],
    spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO },
    contextualSpacing: true,
    children: [
      new TextRun({ children: [new Tab()], font: FONT, size: SZ }),
      T("By:"),
      new TextRun({ children: [new Tab()], font: FONT, size: SZ }),
      signatureRun,
    ],
  });
}

// "Respectfully submitted," aligned to the signature block at SIG_INDENT (3") via a leading tab —
// item 3 requires it to line up with the block rather than sit at the left margin.
function respectfullySubmittedLine() {
  return new Paragraph({
    tabStops: [{ type: TabStopType.LEFT, position: SIG_INDENT }],
    spacing: { after: 300, line: 240, lineRule: LineRuleType.AUTO },
    contextualSpacing: true,
    children: [
      new TextRun({ children: [new Tab()], font: FONT, size: SZ }),
      T("Respectfully submitted,"),
    ],
  });
}

// Detail lines (attorney name/bar number, address, phone, fax, email) — each its own paragraph,
// left-indented directly to SIG_INDENT so they align in a column under the firm name/signature.
function sigDetailLine(run) {
  return new Paragraph({
    indent: { left: SIG_INDENT },
    spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO },
    contextualSpacing: true,
    children: [run],
  });
}

// ---------- caption (EXEMPT from exact 24pt spacing — single-spaced, space after each para) ----------
// Available text width given left=2160 (numbering gutter) and right=1440 margins on a
// 12240-wide page: 12240 - 2160 - 1440 = 8640 dxa. Split ~evenly between the two boxes,
// matching the near-50/50 split in the real Hokes v. Zeus caption table.
const CAPTION_PARA = { after: 200, line: 240, lineRule: LineRuleType.AUTO }; // single-spaced, 10pt after

const captionRows = [
  new TableRow({
    children: [
      new TableCell({
        width: { size: 4320, type: WidthType.DXA },
        borders: leftCellBorders(),
        margins: { top: 100, bottom: 100, left: 100, right: 100 },
        children: [
          P([T("MICHAEL SELBY and CHRISTY CLIFFT, individually and\non behalf of all others similarly situated,", {})], { spacing: CAPTION_PARA }),
          P([T("Plaintiffs,")], { spacing: CAPTION_PARA, indent: { left: 2880 } }),
          P([T("v.")], { spacing: CAPTION_PARA }),
          P([T("BRAND EVANGELISTS FOR BEAUTY INC.,")], { spacing: CAPTION_PARA }),
          P([T("Defendant.")], { spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO }, indent: { left: 2880 } }),
        ],
      }),
      new TableCell({
        width: { size: 4320, type: WidthType.DXA },
        borders: rightCellBorders(),
        margins: { top: 100, bottom: 100, left: 100, right: 100 },
        children: [
          P([T("Case No. 4:26-cv-05924-AMO")], { spacing: CAPTION_PARA }),
          P([T("JOINT CASE MANAGEMENT STATEMENT", { bold: true })], { spacing: CAPTION_PARA }),
          P([T("Date: [CMC DATE]")], { spacing: { after: 100, line: 240, lineRule: LineRuleType.AUTO } }),
          P([T("Time: [CMC TIME]")], { spacing: { after: 100, line: 240, lineRule: LineRuleType.AUTO } }),
          P([T("Courtroom: 10, 19th Floor")], { spacing: CAPTION_PARA }),
          P([T("Judge: Hon. Araceli Martínez-Olguín")], { spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO } }),
        ],
      }),
    ],
  }),
];

function noBorder() {
  const b = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: b, bottom: b, left: b, right: b };
}

// Left box: ONLY bottom + right edges are drawn (matches the real caption table's tcBorders
// exactly — top and left are explicitly none, not just "unset").
function leftCellBorders() {
  const solid = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: none, left: none, bottom: solid, right: solid };
}
// Right box: no border on any edge.
function rightCellBorders() {
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: none, left: none, bottom: none, right: none };
}

const captionTable = new Table({
  width: { size: 8640, type: WidthType.DXA },
  columnWidths: [4320, 4320],
  alignment: AlignmentType.CENTER,
  rows: captionRows,
});

// ---------- scheduling table (Topic 15) ----------
// Matches the real Hokes v. Zeus Networks template: full grid borders, shaded/bold/centered
// header row, body rows with modest before/after spacing (not the exact-24pt main-text rhythm).
function scheduleCell(text, opts = {}) {
  const isPlaceholder = text.trim().startsWith("[") && text.trim().endsWith("]");
  return new TableCell({
    width: { size: opts.width || 4320, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "D9D9D9", color: "auto" } : undefined,
    children: [
      new Paragraph({
        alignment: opts.header || opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
        spacing: opts.header
          ? { line: MAIN_LINE, lineRule: LineRuleType.EXACT, before: 0, after: 0 }
          : { before: 120, after: 120, line: 240, lineRule: LineRuleType.AUTO },
        contextualSpacing: true,
        children: [new TextRun({
          text: sq(text),
          font: FONT,
          size: SZ,
          bold: !!opts.header || isPlaceholder,
          color: isPlaceholder ? "C00000" : undefined,
        })],
      }),
    ],
  });
}

function buildScheduleTable(rows) {
  const gridBorder = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const tableRows = [
    new TableRow({
      children: [
        scheduleCell("Event", { header: true, width: 4320 }),
        scheduleCell("Date", { header: true, width: 4320 }),
      ],
    }),
    ...rows.map(([event, date]) => new TableRow({
      children: [
        scheduleCell(event, { width: 4320 }),
        scheduleCell(date, { center: true, width: 4320 }),
      ],
    })),
  ];
  return new Table({
    width: { size: 8640, type: WidthType.DXA },
    columnWidths: [4320, 4320],
    borders: {
      top: gridBorder, bottom: gridBorder, left: gridBorder, right: gridBorder,
      insideHorizontal: gridBorder, insideVertical: gridBorder,
    },
    rows: tableRows,
  });
}

// ---------- counsel block (front page — borderless two-column table) ----------
// Item 1: the front-matter counsel block is a two-column, one-row table with plaintiffs' counsel
// in the LEFT cell and defense counsel in the RIGHT cell, and NO visible borders on any edge.
// Item 5: the firm name (first line of each firm's block) is BOLD; everything below it is normal.
const COUNSEL_PARA = { after: 0, line: 240, lineRule: LineRuleType.AUTO }; // single-spaced

// One line of a counsel block. `firm` bolds it (firm-name lines); `ph` renders it as a bracketed
// placeholder (defense side, when counsel isn't known yet).
function counselLine(text, { firm = false, ph = false, italic = false } = {}) {
  if (ph) return P([placeholder(text)], { spacing: COUNSEL_PARA });
  return P(
    [new TextRun({ text: sq(text), font: FONT, size: SZ, bold: firm, italics: italic })],
    { spacing: COUNSEL_PARA }
  );
}
const blankCounselLine = () => P([], { spacing: COUNSEL_PARA });

// All borders none → the table is invisible in the rendered document (item 1).
function borderlessCounselTable(leftChildren, rightChildren) {
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const cellBorders = { top: none, bottom: none, left: none, right: none };
  return new Table({
    width: { size: 8640, type: WidthType.DXA },
    columnWidths: [4320, 4320],
    borders: {
      top: none, bottom: none, left: none, right: none,
      insideHorizontal: none, insideVertical: none,
    },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 4320, type: WidthType.DXA },
            borders: cellBorders,
            margins: { top: 40, bottom: 40, left: 0, right: 100 },
            children: leftChildren,
          }),
          new TableCell({
            width: { size: 4320, type: WidthType.DXA },
            borders: cellBorders,
            margins: { top: 40, bottom: 40, left: 100, right: 0 },
            children: rightChildren,
          }),
        ],
      }),
    ],
  });
}

function counselBlock() {
  // LEFT cell — plaintiffs' counsel (two firms; each firm name bold). Pulled fresh from the
  // complaint's caption/signature page for a real case (here, the Selby example values).
  const left = [
    counselLine("BURSOR & FISHER, P.A.", { firm: true }),
    counselLine("L. Timothy Fisher (State Bar No. 191626)"),
    counselLine("Daniel S. Guerra (State Bar No. 267559)"),
    counselLine("1990 North California Blvd., 9th Floor"),
    counselLine("Walnut Creek, CA 94596"),
    counselLine("Telephone: (925) 300-4455"),
    counselLine("Facsimile: (925) 407-2700"),
    counselLine("E-mail: ltfisher@bursor.com"),
    counselLine("          dguerra@bursor.com"),
    blankCounselLine(),
    counselLine("SINDERBRAND LAW GROUP, P.C.", { firm: true }),
    counselLine("Greg Sinderbrand (State Bar No. 179586)"),
    counselLine("2829 Townsgate Road, Suite 100"),
    counselLine("Westlake Village, CA 91361"),
    counselLine("Telephone: (818) 370-3912"),
    counselLine("E-mail: greg@sinderbrandlaw.com"),
    blankCounselLine(),
    counselLine("Counsel for Plaintiffs", { italic: true }),
  ];
  // RIGHT cell — defense counsel. Placeholders until defense counsel appears; the firm-name line
  // is still the first line (and would be bolded once real). The layout is built now so it's
  // ready to fill in.
  const right = [
    counselLine("[DEFENSE COUNSEL FIRM]", { ph: true }),
    counselLine("[DEFENSE COUNSEL NAME] ([STATE BAR NO.])", { ph: true }),
    counselLine("[ADDRESS]", { ph: true }),
    counselLine("[PHONE / EMAIL]", { ph: true }),
    blankCounselLine(),
    counselLine("Counsel for Defendant", { italic: true }),
  ];
  return borderlessCounselTable(left, right);
}

// ---------- build doc body ----------
// The document is split into TWO sections so page numbering can start on the second page at "1"
// with no number on the caption page (item 2). page1Children = section 1 (caption page);
// children = section 2 (the body, beginning on page 2). See the `sections` array below.
const page1Children = [];

// Front matter: counsel block (borderless two-column table — item 1)
page1Children.push(counselBlock());
page1Children.push(new Paragraph({ spacing: { after: 300 }, children: [] }));

// Court name
page1Children.push(centerLine("UNITED STATES DISTRICT COURT", { bold: true }));
page1Children.push(centerLine("NORTHERN DISTRICT OF CALIFORNIA", { bold: true }));
page1Children.push(new Paragraph({ spacing: { after: 300 }, children: [] }));

// Caption table
page1Children.push(captionTable);

// ---- Section 2 (body) begins here, on the second page ----
const children = [];

// Intro paragraph
children.push(bodyP([T(
  "Plaintiffs Michael Selby and Christy Clifft and Defendant Brand Evangelists for Beauty Inc., the Parties to the above-titled action (collectively, the \"Parties\"), hereby submit this Joint Case Management Statement pursuant to the Standing Order for All Judges of the Northern District of California, Civil Local Rule 16-9."
)]));

// (AI certification moved to the end of the document, after the signature blocks and
// Signature Attestation — see the end-of-document attestations section below.)

// 1. Jurisdiction and Service
children.push(sectionHeading(1, "Jurisdiction and Service"));
children.push(bodyP([
  T("This Court has subject matter jurisdiction pursuant to 28 U.S.C. § 1332(d)(2)(A) because this is a putative class action in which the aggregate claims of all members of the proposed Classes exceed $5,000,000, exclusive of interest and costs, and at least one member of the proposed Classes is a citizen of a state different from Defendant. Compl. ¶ 9. "),
  T("Personal jurisdiction over Defendant is proper because Defendant purposefully avails itself of the benefits of this forum by selling its product to consumers, including Plaintiffs, in California, and derives substantial revenue from sales of the product in this State. Compl. ¶ 10."),
  T(" Venue is proper in this District pursuant to 28 U.S.C. § 1391 because a substantial part of the events alleged in the Complaint giving rise to Plaintiffs' claims are alleged to have occurred in this District and Plaintiff Michael Selby resides in this District."),
]));
children.push(bodyP([
  T("Service: "),
  placeholder("[STATE WHETHER DEFENDANT HAS BEEN SERVED AND, IF NOT, PROPOSED DEADLINE FOR SERVICE.]"),
]));

// 2. Facts
children.push(sectionHeading(2, "Facts"));
children.push(...positionBlock("Plaintiffs' Position:", [
  T("This is a putative class action concerning Defendant's marketing and sale of The INKEY List Exosome Hydro-Glow Complex (the \"Product\"). Plaintiffs allege that Defendant's advertising claims for the Product—including that it \"boost[s] collagen production by 300%,\" \"reduce[s] inflammation by 55%,\" \"improve[s] skin repair by 63% in eight hours,\" provides \"up to 12 hours of hydration,\" and delivers \"[s]kin rejuvenation in 14 days, clinically proven\"—are false and misleading because the Product's plant-derived exosome ingredients cannot achieve these effects at the concentrations used in an over-the-counter, topically applied cosmetic. Compl. ¶¶ 1–4, 22–44. Plaintiff Selby purchased the Product on January 17, 2026; Plaintiff Clifft purchased the Product on September 2, 2025; both allege they viewed and relied on Defendant's representations before purchasing. Compl. ¶¶ 5–6. Plaintiffs sent Defendant a pre-suit notice letter under Cal. Civ. Code § 1782 on March 2, 2026, and allege Defendant failed to cure. Compl. ¶ 62."),
]));
children.push(...defendantPositionBlock());

// 3. Legal Issues
children.push(sectionHeading(3, "Legal Issues"));
children.push(...positionBlock("Plaintiffs' Position:", [
  T("The principal disputed legal issues include: (a) whether Defendant's Advertised Claims regarding the Product were false and misleading and scientifically unachievable; (b) whether a reasonable consumer would be misled by Defendant's representations and warranties; (c) whether Defendant's conduct violates the California Consumers Legal Remedies Act, Cal. Civ. Code § 1750, et seq.; the California Unfair Competition Law, Cal. Bus. & Prof. Code § 17200, et seq.; and the California False Advertising Law, Cal. Bus. & Prof. Code § 17500, et seq.; (d) whether Defendant breached an express warranty; (e) whether Defendant was unjustly enriched; and (f) whether the proposed Classes may be certified under Fed. R. Civ. P. 23."),
]));
children.push(...defendantPositionBlock());

// 4. Motions
children.push(sectionHeading(4, "Motions"));
children.push(...positionBlock("Plaintiffs' Position:", [
  T("No motions have been filed to date. Plaintiffs anticipate that Defendant may file a motion to dismiss the Complaint. "),
  placeholder("[UPDATE WITH ACTUAL STATUS/ANTICIPATED MOTIONS.]"),
]));
children.push(...defendantPositionBlock());

// 5. Amendment of Pleadings
children.push(sectionHeading(5, "Amendment of Pleadings"));
children.push(...positionBlock("Plaintiffs' Position:", [
  placeholder("[STATE WHETHER PLAINTIFFS ANTICIPATE AMENDING AND PROPOSE A DEADLINE FOR AMENDMENT OF PLEADINGS.]"),
]));
children.push(...defendantPositionBlock());

// 6. Evidence Preservation
children.push(sectionHeading(6, "Evidence Preservation"));
children.push(...positionBlock("Plaintiffs' Position:", [
  T("Plaintiffs certify that Plaintiffs have reviewed the Guidelines Relating to the Discovery of Electronically Stored Information. Plaintiffs' counsel has taken steps to advise Plaintiffs about the need to preserve evidence."),
]));
children.push(...defendantPositionBlock());

// 7. Disclosures
children.push(sectionHeading(7, "Disclosures"));
children.push(bodyP([
  T("The Parties will exchange initial disclosures by "),
  new TextRun({ text: "                    ", font: FONT, size: SZ, underline: { type: UnderlineType.SINGLE } }),
  T("."),
]));

// 8. Discovery
children.push(sectionHeading(8, "Discovery"));
children.push(bodyP([
  T("The Parties have agreed to accept service of discovery requests and responses via email. The Parties further agree to cooperate and work in good faith toward reaching an agreement on a stipulation regarding the preservation and production of electronically stored information, as well as a protective order governing the discovery and use of confidential information. If an agreement cannot be reached, the Parties will seek Court intervention."),
]));

// 9. Class Actions
children.push(sectionHeading(9, "Class Actions"));
children.push(...positionBlock("Plaintiffs' Position:", [
  T("Dates for Plaintiffs' Motion for Class Certification and Defendant's Opposition are proposed below. All attorneys of record have reviewed the Procedural Guidance for Class Action Settlements."),
]));
children.push(...defendantPositionBlock());

// 10. Related Cases
children.push(sectionHeading(10, "Related Cases"));
children.push(bodyP([
  T("The Parties are not aware of any related cases."),
]));

// 11. Relief
children.push(sectionHeading(11, "Relief"));
// Heading is its own paragraph — bold+italic, NOT indented (matches the real template exactly;
// unlike every other section, the intro sentence that follows goes on a separate, indented line).
children.push(positionLabelPara("Plaintiffs' Position"));
// Intro sentence. Section 11 is a whole-section exception to the document-wide first-line-indent
// rule, so this intro is built explicitly (NOT via bodyP) to preserve Section 11's own
// established formatting: a 0.5" left indent, justified, exact-24pt, no before/after spacing.
// (For a one-line sentence this is visually identical to a first-line indent, but keeping it
// off bodyP means future changes to the document-wide rule won't silently alter Section 11.)
children.push(new Paragraph({
  spacing: { after: 0, before: 0, line: MAIN_LINE, lineRule: LineRuleType.EXACT },
  alignment: AlignmentType.JUSTIFIED,
  indent: { left: BODY_INDENT },
  children: [T("Plaintiffs have requested the following relief as set forth in the Complaint:")],
}));
// Relief list — copied verbatim from the complaint's "PRAYER FOR RELIEF" section, one list
// item per lettered sub-paragraph in the complaint, in the same order. Uses a lowerLetter
// "(a)", "(b)"... list matching the real template's numbering (numId 17 / abstractNumId 2 in
// the reference filing), 12pt Times New Roman, spacing after=240/line=280 exact (this list
// uses tighter line spacing than the main double-spaced narrative text, matching the firm's
// actual convention for prayer-for-relief lists specifically). This list's own indent scheme
// is intentionally left unchanged by the document-wide 0.5" body-indent rule — it already has
// its own established indent matching the real template exactly.
const reliefItems = [
  "For an order certifying the Classes under Fed. R. Civ. P. 23 and naming Plaintiffs as representatives of the Classes, and Plaintiffs' Counsel as Class Counsel;",
  "For an order declaring that Defendant's conduct violates each of the statutes referenced herein;",
  "For an order finding in favor of Plaintiffs and the Classes on all counts asserted herein;",
  "For compensatory, statutory, and punitive damages in amounts to be determined by the Court and/or jury;",
  "For prejudgment interest on all amounts awarded;",
  "For an order of restitution and all other forms of equitable monetary relief;",
  "For injunctive relief as pleaded or as the Court may deem proper; and",
  "For an order awarding Plaintiffs and the Classes their reasonable attorneys' fees and expenses and costs of suit.",
];
reliefItems.forEach((item) => {
  children.push(new Paragraph({
    numbering: { reference: "reliefList", level: 0 },
    spacing: { after: 240, line: 280, lineRule: LineRuleType.EXACT },
    children: [T(item)],
  }));
});
children.push(...defendantPositionBlock("Defendant's Position (including basis on which Defendant contends damages should be calculated if liability is established):"));

// 12. Settlement and ADR — joint statement, NO position split (item 7). The text is identical
// regardless of the user's yes/no answer to "have you agreed to mediate with a private
// mediator?" The ONLY difference: on a "no / not yet" answer, everything after the first
// sentence (the sentence about being open to a private mediator) is highlighted yellow to flag
// that it still needs the user's confirmation. This example shows the "no" variant. For a "yes"
// answer, build the identical text but drop the `highlight: "yellow"` option on the second run.
children.push(sectionHeading(12, "Settlement and ADR"));
children.push(bodyP([
  // First sentence (always unhighlighted). Two trailing spaces = the double space before the next
  // sentence (item 6), applied here explicitly because the sentence boundary spans two runs.
  T("The Parties have reviewed the ADR procedures in ADR L.R. 3-5.  "),
  // Second sentence — highlighted only because the user answered "no / not yet." Omit `highlight`
  // for a "yes" answer.
  T("The Parties are open to engaging in settlement discussions with a private mediator, provided there is a sufficient exchange of information to permit informed discussions.", { highlight: "yellow" }),
]));

// 13. Other References
children.push(sectionHeading(13, "Other References"));
children.push(bodyP([
  T("The Parties do not believe that the case is suitable for reference to binding arbitration or a special master at this time. The Parties have not consented to the jurisdiction of a magistrate judge."),
]));

// 14. Narrowing of Issues
children.push(sectionHeading(14, "Narrowing of Issues"));
children.push(bodyP([
  T("The Parties are not aware of any issues that may be narrowed at this time."),
]));

// 15. Scheduling
children.push(sectionHeading(15, "Scheduling"));
children.push(bodyP([
  T("The Parties propose the following schedule:"),
]));
children.push(buildScheduleTable([
  ["Deadline to Exchange Initial Disclosures", "[INSERT DATE: 14 DAYS AFTER THE RULE 26(f) CONFERENCE (PRESUMPTIVE DEADLINE), OR 14 DAYS AFTER THE RULE 16/CASE MANAGEMENT CONFERENCE, PER THE 26(f) PROTOCOL]"],
  ["Deadline to Amend Pleadings", "[INSERT DATE: PROPOSED DEADLINE TO AMEND PLEADINGS — TYPICALLY TIED TO RESOLUTION OF ANY PENDING MOTION TO DISMISS, IF APPLICABLE]"],
  ["Deadline to file Plaintiffs' Motion for Class Certification, including expert reports upon which Plaintiffs rely in their Motion", "[INSERT DATE: 8–10 MONTHS AFTER THE RULE 16 CONFERENCE (UP TO 12 MONTHS IF AN UNUSUALLY LARGE AMOUNT OF DISCOVERY IS EXPECTED), PER THE 26(f) PROTOCOL]"],
  ["Deadline to file Defendant's Opposition to Class Certification, including any counter expert reports upon which Defendant relies in its Motion", "[INSERT DATE: 45–60 DAYS AFTER THE FILING OF PLAINTIFFS' MOTION FOR CLASS CERTIFICATION, PER THE 26(f) PROTOCOL]"],
  ["Deadline to file Plaintiffs' Reply in Support of Class Certification, including any rebuttal expert reports upon which Plaintiffs rely in their Motion", "[INSERT DATE: 45 DAYS AFTER THE FILING OF DEFENDANT'S OPPOSITION TO CLASS CERTIFICATION, PER THE 26(f) PROTOCOL]"],
  // Item 8: the hearing-date cell states the notice requirement (a class-cert hearing must
  // satisfy the minimum notice period for putting a motion on the judge's calendar), checked
  // against BOTH the local rules and the judge's standing order (standing order controls if it
  // differs), with the day-counting basis made explicit. The district-wide baseline is Civil
  // L.R. 7-2(a): a motion must be noticed for hearing not less than 35 CALENDAR days after
  // filing (Fed. R. Civ. P. 6(d) does not extend it). Expressed as a bracketed instruction, not
  // a computed date, because the motion filing date is itself a placeholder.
  ["Hearing on Motion for Class Certification", "[INSERT DATE: AT LEAST 35 CALENDAR DAYS AFTER THE FILING OF THE MOTION FOR CLASS CERTIFICATION AND SET ON JUDGE MARTÍNEZ-OLGUÍN'S CIVIL MOTION CALENDAR, PER CIVIL L.R. 7-2(a); CONFIRM AGAINST THE JUDGE'S STANDING ORDER, WHICH CONTROLS IF IT SETS A DIFFERENT NOTICE PERIOD OR HEARING DAY]"],
  ["Close of Fact Discovery", "90 days after decision on class certification"],
  ["Expert Disclosures", "120 days after decision on class certification"],
  ["Rebuttal Expert Disclosures", "180 days after decision on class certification"],
  ["Expert Discovery Cut-Off", "240 days after decision on class certification"],
  ["Deadline for Dispositive Motions", "60 days after expert discovery cutoff"],
  ["Pre-trial conference", "TBD"],
  ["Trial", "TBD"],
]));

// 16. Trial
children.push(sectionHeading(16, "Trial"));
children.push(bodyP([
  T("Plaintiffs have demanded a jury trial of any claims triable by a jury, and the Parties estimate the trial to last approximately 5-7 court days."),
]));

// 17. Disclosure of Non-Party Interested Entities or Persons
children.push(sectionHeading(17, "Disclosure of Non-Party Interested Entities or Persons"));
children.push(bodyP([
  T("The Parties are not aware of any non-party interested entities or person, other than putative class members."),
]));

// 18. Professional Conduct
children.push(sectionHeading(18, "Professional Conduct"));
children.push(bodyP([
  T("Counsel for the Parties have reviewed the Guidelines for Professional Conduct for the Northern District of California and agree to comply with them."),
]));

// 19. Such Other Matters
children.push(sectionHeading(19, "Such Other Matters"));
children.push(bodyP([
  T("The Parties are not presently aware of any other matters that may facilitate the just, speedy, and inexpensive disposition of this matter."),
]));

// Signature block (EXEMPT — single-spaced, auto). "Respectfully submitted," is aligned to the
// 3" signature column (item 3), same as the "By:" line below.
children.push(new Paragraph({ spacing: { before: 400, after: 200 }, children: [] }));
children.push(respectfullySubmittedLine());

// Plaintiffs' signature block — L. Timothy Fisher is the assumed signer (see the Word comment
// on the Signature Attestation reflecting the same assumption). Bursor & Fisher's second
// attorney (Daniel S. Guerra) and Sinderbrand Law Group are listed as additional counsel of
// record without their own separate "By:"/s/" line, matching the real template's convention.
children.push(sigDateLine("Dated", new TextRun({ text: "BURSOR & FISHER, P.A.", font: FONT, size: SZ, bold: true })));
children.push(sigByLine(new TextRun({ text: "/s/ L. Timothy Fisher", font: FONT, size: SZ, italics: true, underline: { type: UnderlineType.SINGLE } })));
[
  "L. Timothy Fisher (State Bar No. 191626)",
  "Daniel S. Guerra (State Bar No. 267559)",
  "1990 North California Blvd., 9th Floor",
  "Walnut Creek, CA 94596",
  "Telephone: (925) 300-4455",
  "Facsimile: (925) 407-2700",
  "E-mail: ltfisher@bursor.com",
  "          dguerra@bursor.com",
].forEach((line) => children.push(sigDetailLine(T(line))));
children.push(new Paragraph({ spacing: { after: 0 }, children: [] }));
[
  "SINDERBRAND LAW GROUP, P.C.",
  "Greg Sinderbrand (State Bar No. 179586)",
  "2829 Townsgate Road, Suite 100",
  "Westlake Village, CA 91361",
  "Telephone: (818) 370-3912",
  "E-mail: greg@sinderbrandlaw.com",
].forEach((line) => children.push(sigDetailLine(T(line))));
children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
// End-of-document counsel label — left-indented to SIG_INDENT so it aligns under the signature
// block it follows (not flush at the left margin). Uses the same fixed column as the firm
// name/signature/detail lines above it.
children.push(P([new TextRun({ text: "Counsel for Plaintiffs", font: FONT, size: SZ, italics: true })], { spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO }, indent: { left: SIG_INDENT } }));

// Defendant's signature block — everything is a placeholder pending defense counsel's input.
children.push(new Paragraph({ spacing: { before: 400, after: 200 }, children: [] }));
children.push(sigDateLine("Dated", placeholder("[DEFENSE COUNSEL FIRM]")));
children.push(sigByLine(placeholder("[SIGNATURE]")));
[
  "[DEFENSE COUNSEL NAME] ([STATE BAR NO.])",
  "[ADDRESS]",
  "[TELEPHONE]",
  "[FACSIMILE]",
  "[E-MAIL]",
].forEach((line) => children.push(sigDetailLine(placeholder(line))));
children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
// End-of-document counsel label — left-indented to SIG_INDENT to align under the defense
// signature block it follows.
children.push(P([new TextRun({ text: "Counsel for Defendant", font: FONT, size: SZ, italics: true })], { spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO }, indent: { left: SIG_INDENT } }));

// ---------- Signature Attestation (global, every draft) ----------
// Copied word-for-word/format from the real Hokes v. Zeus Networks template. Filer assumed to
// be the first-listed/lead attorney in the signature block (L. Timothy Fisher) — flagged with
// a Word comment since this is an assumption, not a fact pulled from the complaint.
children.push(new Paragraph({ spacing: { before: 400, after: 200 }, children: [] }));
children.push(attestationTitle("SIGNATURE ATTESTATION"));
children.push(attestationBody([
  T("I, "),
  T("L. Timothy Fisher"),
  T(", as the ECF user and filer of this document, attest pursuant to N.D. Cal. L.R. 5(i)(3) that each of the other signatories have concurred in the filing of the document."),
]));
children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
children.push(...attestationSignatureLines("Dated", "L. Timothy Fisher"));

// ---------- Generative AI Certification (conditional) ----------
// Included here because Judge Martínez-Olguín's Standing Order for Civil Cases, Section H.4,
// requires any AI-assisted submission to include this certification. Check fresh for whatever
// judge is actually assigned in a future case — omit this block entirely if no such
// requirement is found in that judge's standing order or the N.D. Cal. local rules.
children.push(new Paragraph({ spacing: { before: 400, after: 200 }, children: [] }));
children.push(attestationTitle("GENERATIVE AI CERTIFICATION"));
children.push(attestationBody([
  T("This document was produced in part using generative AI. I, "),
  T("L. Timothy Fisher"),
  T(" and lead trial counsel, certify pursuant to Section H.4 of Judge Martínez-Olguín's Standing Order for Civil Cases that I have personally verified the accuracy of the AI-generated content in this submission."),
]));
children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
children.push(...attestationSignatureLines("Date", "L. Timothy Fisher"));

// ---------- document ----------
const NUMBERING = {
  config: [
    {
      reference: "reliefList",
      levels: [
        {
          level: 0,
          format: LevelFormat.LOWER_LETTER,
          text: "(%1)",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 2160, hanging: 720 } } },
        },
      ],
    },
  ],
};

// Two sections so page numbering starts on the SECOND page at "1," with no number on the caption
// page (item 2). Section 1 = caption page (footer has the title + case-number lines but NO page
// number). Section 2 = body, starting on a new page with page numbering restarted at 1. The
// footer's position (right tab at 8640), 10pt size, and Times New Roman font are identical in both
// sections — only the presence and starting value of the page number changes.
function buildFooter({ withPageNumber }) {
  // Civil L.R. 3-4(c)(3): footer states the paper's title and, once assigned, the case number.
  // Civil L.R. 3-4(a)(3)(C): case number followed by the assigned judge's initials (here
  // "AMO" — derive fresh per case, see SKILL.md Step 1; do not hardcode for a different judge).
  const caseLineChildren = [
    new TextRun({ text: "CASE NO. 4:26-cv-05924-AMO", font: FONT, size: SZ_FOOTER }),
  ];
  if (withPageNumber) {
    caseLineChildren.push(new TextRun({ children: [new Tab()], font: FONT, size: SZ_FOOTER }));
    caseLineChildren.push(new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SZ_FOOTER }));
  }
  return new Footer({
    children: [
      new Paragraph({
        alignment: AlignmentType.LEFT,
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: "000000", space: 1 } },
        children: [
          // Entire footer is uniform 10pt (size 20 half-points) Times New Roman.
          new TextRun({ text: "Joint Case Management Statement", font: FONT, size: SZ_FOOTER, smallCaps: true }),
        ],
      }),
      new Paragraph({
        alignment: AlignmentType.LEFT,
        tabStops: [{ type: TabStopType.RIGHT, position: 8640 }],
        children: caseLineChildren,
      }),
    ],
  });
}

// No running title in the header — the title/case number go in the FOOTER per Civil L.R.
// 3-4(c)(3). The header is reserved for the pleading-paper line-number column (injected via
// inject_line_numbers.py post-processing).
const emptyHeader = () => new Header({ children: [new Paragraph({ children: [] })] });
const PAGE_PROPS = {
  size: { width: 12240, height: 15840 }, // US Letter
  margin: { top: 1200, bottom: 1200, left: 2160, right: 1440 }, // top/bottom ~0.833" -> 28 lines
};

function buildSections() {
  return [
    // Section 1 — caption page. Footer omits the page number, so the caption page shows none.
    {
      properties: { page: PAGE_PROPS },
      headers: { default: emptyHeader() },
      footers: { default: buildFooter({ withPageNumber: false }) },
      children: page1Children,
    },
    // Section 2 — body. Starts on the next page (SectionType.NEXT_PAGE) and restarts page
    // numbering at 1, so the first body page reads "1" and the rest continue 2, 3, 4 ….
    {
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { ...PAGE_PROPS, pageNumbers: { start: 1 } },
      },
      headers: { default: emptyHeader() },
      footers: { default: buildFooter({ withPageNumber: true }) },
      children,
    },
  ];
}

const doc = new Document({
  numbering: NUMBERING,
  sections: buildSections(),
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("/home/claude/cms-draft/Selby_v_BrandEvangelists_JointCMS_DRAFT.docx", buf);
  console.log("done");
});
