/**
 * Example Build Script — Selby v. Brand Evangelists for Beauty Inc.
 *
 * This is a worked example demonstrating the use of the docx npm library to build
 * a Joint Case Management Statement for Northern District of California.
 *
 * IMPORTANT: This script is a REFERENCE EXAMPLE ONLY. All values are hardcoded for
 * the Selby test case (Case No. 4:26-cv-05924-AMO, Judge Martínez-Olguín).
 * Every detail must be REPLACED for new matters.
 *
 * Usage:
 *   node example_build_script.js > output.docx
 *
 * Dependencies:
 *   npm install docx
 */

const { Document, Paragraph, Table, TableCell, TableRow, BorderStyle, WidthType, AlignmentType, UnderlineType, convertInchesToTwip, VerticalAlign, PageBreak } = require('docx');
const fs = require('fs');

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * sq() - Apply curly (smart) quotes to text.
 * Note: This is a simplified example. A real implementation should handle nested quotes.
 */
function sq(text) {
  return text.replace(/^"/, '"').replace(/"$/, '"').replace(/^'/, ''').replace(/'$/, ''');
}

/**
 * nbsp() - Insert nonbreaking space after citation symbols.
 * Used for § and ¶ symbols to prevent line breaks between symbol and number.
 */
function nbsp(text) {
  return text.replace(/([§¶])\s+/g, '$1 ');
}

/**
 * bodyParagraph() - Create a body paragraph with N.D. Cal. CMS formatting.
 * - 0.5" first-line indent
 * - Exact 24pt line spacing
 * - Justified alignment
 * - ContextualSpacing enabled
 */
function bodyParagraph(text) {
  return new Paragraph({
    text: text,
    style: 'Normal',
    indent: {
      firstLine: convertInchesToTwip(0.5),
    },
    spacing: {
      line: 240,
      lineRule: 'exact',
      after: 0,
      before: 0,
    },
    alignment: AlignmentType.JUSTIFIED,
    contextualSpacing: true,
  });
}

/**
 * captionElement() - Create a caption paragraph (single-spaced, not justified, no indent).
 * Used for the case caption at the top of the document.
 */
function captionElement(text, bold = false) {
  return new Paragraph({
    text: text,
    bold: bold,
    spacing: {
      line: 240,
      lineRule: 'exact',
      after: 0,
      before: 0,
    },
    alignment: AlignmentType.CENTER,
    contextualSpacing: false,
  });
}

// ============================================================================
// DOCUMENT CONTENT
// ============================================================================

// Case-specific values (REPLACE FOR NEW MATTERS)
const CASE_CAPTION = 'SELBY v. BRAND EVANGELISTS FOR BEAUTY INC., et al.';
const CASE_NUMBER = '4:26-cv-05924-AMO';
const JUDGE_NAME = 'Hon. Arlene Martínez-Olguín';
const CMC_DATE = 'November 15, 2026';
const CMC_TIME = '3:00 p.m.';
const CMC_COURTROOM = 'Courtroom 4, 17th Floor';

// Plaintiff counsel (REPLACE WITH ACTUAL FIRM DETAILS)
const PLAINTIFF_COUNSEL = 'Law Firm LLP\nJohn Doe, Esq. (State Bar No. 123456)\n123 Main Street\nSan Francisco, CA 94105\nTelephone: (415) 555-0100\nFacsimile: (415) 555-0101\nEmail: john.doe@lawfirm.com\n\nAttorneys for Plaintiff';

// Defense counsel (placeholder)
const DEFENSE_COUNSEL = '[TO BE COMPLETED BY DEFENSE COUNSEL]';

// ============================================================================
// DOCUMENT SECTIONS
// ============================================================================

const sections = [
  // ----
  // CAPTION PAGE
  // ----
  captionElement(''),
  captionElement(''),
  captionElement(CASE_CAPTION, true),
  captionElement(''),
  captionElement(CASE_NUMBER, true),
  captionElement(''),
  captionElement(JUDGE_NAME),
  captionElement(''),
  captionElement(''),
  captionElement('JOINT CASE MANAGEMENT STATEMENT', true),
  captionElement(''),
  captionElement(`Case Management Conference: ${CMC_DATE}`),
  captionElement(`Time: ${CMC_TIME}`),
  captionElement(`Location: ${CMC_COURTROOM}`),
  captionElement(''),
  captionElement(''),

  // ----
  // COUNSEL SIGNATURE TABLE (no visible borders)
  // ----
  new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.NONE },
      bottom: { style: BorderStyle.NONE },
      left: { style: BorderStyle.NONE },
      right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.NONE },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [
      new TableRow({
        cells: [
          new TableCell({
            children: [new Paragraph(PLAINTIFF_COUNSEL)],
            verticalAlign: VerticalAlign.TOP,
          }),
          new TableCell({
            children: [new Paragraph(DEFENSE_COUNSEL)],
            verticalAlign: VerticalAlign.TOP,
          }),
        ],
      }),
    ],
  }),

  captionElement(''),
  captionElement(''),

  // ----
  // BODY: TOPIC 1 EXAMPLE (Jurisdiction, Service, and Venue)
  // ----
  bodyParagraph('1. Jurisdiction, Service, and Venue'),
  bodyParagraph(''),
  bodyParagraph('Plaintiffs' Position'),
  bodyParagraph(
    nbsp('Summons and Complaint have been served on all named Defendants. Service was effectuated on ' +
    '[SPECIFY DEFENDANTS AND DATES]. The Court has subject matter jurisdiction over this action pursuant to ' +
    '28 U.S.C. § 1332(d) (Class Action Fairness Act). Plaintiff is a citizen of [STATE], and Defendants are ' +
    'citizens of other states or foreign countries. The amount in controversy exceeds $5,000,000, exclusive of ' +
    'interest and costs. Venue is proper in this District under 28 U.S.C. § 1391(b) because a substantial part ' +
    'of the events giving rise to Plaintiff\'s claims occurred in this District. Compl. ¶¶ [X–Y].')
  ),
  bodyParagraph(''),
  bodyParagraph('Defendants' Position'),
  bodyParagraph('[DEFENDANTS\' POSITION ON JURISDICTION, SERVICE, VENUE, AND PERSONAL JURISDICTION]'),
  bodyParagraph(''),

  // ----
  // TOPIC 6 EXAMPLE: EVIDENCE PRESERVATION
  // ----
  bodyParagraph('6. Evidence Preservation'),
  bodyParagraph(
    'The parties shall preserve all documents, electronically stored information (' + sq('ESI') + '), and tangible things in the possession, custody, or control of each party that are relevant to the subject matter of this litigation. Pursuant to Federal Rule of Civil Procedure 26(f), the parties have met and conferred regarding preservation obligations. Each party shall notify the other parties immediately upon discovery of the loss or destruction of any such evidence.'
  ),
  bodyParagraph(''),

  // ----
  // TOPIC 7 EXAMPLE: DISCLOSURES
  // ----
  bodyParagraph('7. Disclosures and Initial Disclosures Deadline'),
  bodyParagraph(
    'Initial disclosures shall be made by [INITIAL DISCLOSURES DEADLINE: 14 days after Rule 26(f) conference], as calculated under Federal Rule of Civil Procedure 6(a). The parties shall supplement their disclosures as required by Federal Rule of Civil Procedure 26(e).'
  ),
  bodyParagraph(''),

  // ----
  // SIGNATURE BLOCKS (3" indent from left)
  // ----
  captionElement(''),
  captionElement(''),
  captionElement(''),
  bodyParagraph('Respectfully submitted,'),
  bodyParagraph(''),
  bodyParagraph(''),
  bodyParagraph('Dated: [AUTO-DATE FIELD]'),
  bodyParagraph(''),
  bodyParagraph('By: ____________________________'),
  bodyParagraph('[Attorney Name]\n[Firm Name]\n[Address]\n[Phone]\n[Email]'),
];

// ============================================================================
// BUILD DOCUMENT
// ============================================================================

const doc = new Document({
  sections: [
    {
      properties: {
        page: {
          margin: {
            top: convertInchesToTwip(1),
            right: convertInchesToTwip(1),
            bottom: convertInchesToTwip(1),
            left: convertInchesToTwip(1),
          },
        },
      },
      children: sections,
      footers: {
        default: new Paragraph({
          text: `${CASE_NUMBER}  Joint Case Management Statement`,
          fontSize: 20,
          alignment: AlignmentType.LEFT,
          spacing: {
            line: 240,
            lineRule: 'exact',
          },
        }),
      },
    },
  ],
});

// ============================================================================
// OUTPUT
// ============================================================================

/**
 * Write the document to stdout as binary data.
 * The Node.js docx library returns a Blob; convert to buffer and pipe to stdout.
 */
doc.asBlob().then((blob) => {
  const buffer = Buffer.from(blob);
  process.stdout.write(buffer);
}).catch((err) => {
  console.error('Error generating document:', err);
  process.exit(1);
});

// ============================================================================
// IMPORTANT NOTES FOR IMPLEMENTERS
// ============================================================================

/**
 * 1. REPLACE ALL HARDCODED VALUES:
 *    - CASE_CAPTION: Use actual party names and designations
 *    - CASE_NUMBER: Include judge's initials per Civil L.R. 3-4
 *    - JUDGE_NAME: Full name and title from Rule 16 Order
 *    - CMC_DATE, CMC_TIME, CMC_COURTROOM: From Rule 16 Order or placeholders
 *    - PLAINTIFF_COUNSEL: Actual counsel signature block (names, bar numbers, address, email)
 *    - DEFENSE_COUNSEL: Placeholder or actual defense counsel (if available)
 *
 * 2. CITATION FORMATTING:
 *    - All citations should use curly quotes (') and (") via sq() helper
 *    - Nonbreaking spaces after § and ¶ via nbsp() helper
 *    - Bluebook federal style: italicize signals (See, Accord, etc.)
 *    - En dashes for ranges (e.g., ¶¶ 22–44)
 *
 * 3. SPACING AND INDENTATION:
 *    - Body text: bodyParagraph() function ensures 0.5" first-line indent, exact 24pt spacing
 *    - Caption elements: captionElement() for single-spaced, non-indented text
 *    - Tables: Remove all borders (set to BorderStyle.NONE)
 *    - Signature blocks: Typically 3" indent from left margin
 *
 * 4. FOOTER:
 *    - Include document title and case number (with judge initials)
 *    - 10pt Times New Roman font
 *    - Left-aligned
 *    - Page numbering: No number on caption page; starts at 1 on second page
 *
 * 5. DOCUMENT STRUCTURE:
 *    - Caption page: Case caption, case number, judge name, CMC hearing info
 *    - Counsel table: 2 columns (Plaintiff / Defense), no visible borders
 *    - Body: 19 topics with split (Plaintiff Position / Defendant Position) and joint sections
 *    - Signature blocks: Ending of document with dates and attorney names
 *    - Attestations: Signature Attestation + Generative AI Certification (if required by judge)
 *
 * 6. VERIFICATION:
 *    - Render to PDF and verify all formatting visually
 *    - Check: indent, spacing, quotes, citations, page numbering, footer, table borders
 *    - Use a formatting checklist (see references/standing_order_topics.md)
 */
