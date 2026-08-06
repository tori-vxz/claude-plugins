#!/usr/bin/env python3
"""
Word Comment Helper

Helper functions for anchoring Word comments to text in a docx document.
This is a stub that demonstrates the expected interface.

In practice, this integrates with the docx npm library's comment functionality
(or the underlying python-docx library if writing Python-based docx generation).

The main SKILL.md expects comments to be anchored at specific locations:
  - Service status (Topic 1): source of docket check result
  - Jurisdiction basis (Topic 1): confirmation to double-check if non-CAFA
  - Personal jurisdiction (Topic 1): confirmation to double-check
  - Venue (Topic 1): reminder to verify plaintiff domiciles
  - Topic 7 (Disclosures): source of 26(f) date or instruction to fill in
  - Topic 15 scheduling rows: basis for proposed dates (notice period, etc.)

The docx npm library (for JavaScript) includes built-in comment support via
Range.addCommentRangeMark() and similar. For Python-based generation,
python-docx has comment support via the comments part.

This file serves as a reference for the expected comment-anchoring interface.
"""

def add_comment(run, comment_text, author="Claude Code", date=None):
    """
    Anchor a comment to a Run object in a docx document.

    Args:
        run: The TextRun or paragraph element to anchor the comment to.
        comment_text: The text of the comment (string).
        author: Author name (default "Claude Code").
        date: Datetime of the comment (default: today).

    Returns:
        The comment object (implementation-specific).

    Implementation (docx npm library):
        This is typically done via:
          doc.addCommentRangeMark(comment_id, run_start, run_end);
          doc.addComment(comment_id, {
            author: author,
            date: date,
            initials: "CC",
            text: comment_text
          });

    Implementation (python-docx):
        Comments are stored in a separate part of the document and referenced
        via comment_range_start/end elements. The python-docx API is still
        evolving; consult the library's documentation.
    """
    # Placeholder implementation
    print(f"[Comment] {comment_text} (by {author})")
    return None


def comment_on_placeholder(paragraph, placeholder_text, comment_text):
    """
    Helper to find a bracketed placeholder in a paragraph and add a comment to it.

    Args:
        paragraph: The paragraph element containing the placeholder.
        placeholder_text: The bracketed text to find (e.g., "[SERVICE STATUS]").
        comment_text: The comment to anchor.

    Returns:
        The comment object.
    """
    # Placeholder: in a real implementation, locate the placeholder text within
    # the paragraph's runs and anchor a comment to the run(s) spanning it.
    return add_comment(paragraph, comment_text)
