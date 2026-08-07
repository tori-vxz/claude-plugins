"""
Injects the firm's exact 28-line pleading-paper number column, plus the three vertical divider
lines, into a generated .docx's header1.xml — replicating the mechanism found in the firm's
real filed CMS (2026_07_07_FINAL_Zeus_CMC_Statement.docx). NOT Word's dynamic line-numbering
feature, and NOT a single frame with line breaks (both were tried first and rejected/broken).

Usage:
    1. Generate the base .docx with docx-js as usual (no lineNumbers section property).
    2. Unpack it: unzip -q file.docx -d unpacked/
    3. Run: python inject_line_numbers.py unpacked/word/header1.xml
    4. Rezip and run scripts/office/validate.py to confirm structural validity.

Two independent mechanisms are injected:
  (a) 28 separate paragraphs, each floated via legacy w:framePr with a fixed horizontal
      position (w:hAnchor="page", explicit w:x) and w:yAlign="top" — no explicit w:y — so they
      stack in normal paragraph order instead of using absolute Y coordinates. First paragraph
      uses auto (single) spacing; paragraphs 2-28 use exact 24pt spacing matching the main text.
  (b) Three page-anchored vertical line drawings (modern DrawingML wordprocessingShape,
      without the legacy VML fallback block): two closely-spaced lines flanking the number
      column (matching the real template's double-rule divider) and one line positioned in the
      right margin outside the body text (matching the real template's right-margin rule).

Known verification limitation: LibreOffice-headless (the only rendering tool available here)
does not reliably render w:framePr inside a header (observed page-count explosion and
horizontal misplacement in testing on an earlier attempt). The vertical-line drawings are a
different, more standard DrawingML mechanism and were not observed to cause the same failure,
but the numbering paragraphs specifically could not be visually verified. Say so explicitly
when using this — don't assert the render is correct without the user confirming in real Word.

Adjust the X_* constants below to match the document's actual margins.
"""
import sys

FRAME_WIDTH = 500       # twips, width of the number "column"
X_POSITION = 1150       # twips from left page edge — tune to sit left of the body margin
IND_RIGHT = 150         # twips, small gap between number and the divider lines
LINE_EXACT = 480        # 24pt exact, in twentieths of a point — MUST match main text line height

# Vertical line positions, in EMU (914400 EMU = 1 inch), relativeFrom="page".
# Tuned for left margin = 2160 twips (1.5in) and right margin = 1440 twips (1.0in) on a
# 12240-twip-wide (8.5in) page — adjust if margins change.
LEFT_LINE_A_EMU = 1234440   # 1.35in from left edge — first of the double rule by the numbers
LEFT_LINE_B_EMU = 1280160   # 1.40in from left edge — second of the double rule
RIGHT_LINE_EMU = 7040880    # 7.70in from left edge — single rule in the right margin, outside text
LINE_HEIGHT_EMU = 10058400  # ~11in, full page height (matches the real template's value)


def build_number_paragraphs(count=28):
    paras = []
    for i in range(1, count + 1):
        spacing = (
            '<w:spacing w:line="240" w:lineRule="auto"/>'
            if i == 1
            else f'<w:spacing w:line="{LINE_EXACT}" w:lineRule="exact"/>'
        )
        p = (
            "<w:p><w:pPr>"
            f'<w:framePr w:w="{FRAME_WIDTH}" w:hSpace="100" w:vSpace="100" w:wrap="around" '
            f'w:hAnchor="page" w:x="{X_POSITION}" w:yAlign="top"/>'
            f"{spacing}"
            f'<w:ind w:right="{IND_RIGHT}"/>'
            '<w:jc w:val="right"/>'
            "</w:pPr>"
            '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" '
            'w:cs="Times New Roman"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
            f"<w:t>{i}</w:t></w:r></w:p>"
        )
        paras.append(p)
    return "".join(paras)


def build_vertical_line(x_emu, name, rel_id):
    return (
        "<w:p><w:r><w:drawing>"
        f'<wp:anchor distT="0" distB="0" distL="114300" distR="114300" simplePos="0" '
        f'relativeHeight="{rel_id}" behindDoc="0" locked="1" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        f'<wp:positionH relativeFrom="page"><wp:posOffset>{x_emu}</wp:posOffset></wp:positionH>'
        '<wp:positionV relativeFrom="page"><wp:posOffset>2540</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="0" cy="{LINE_HEIGHT_EMU}"/>'
        '<wp:effectExtent l="9525" t="0" r="9525" b="0"/>'
        "<wp:wrapNone/>"
        f'<wp:docPr id="{rel_id}" name="{name}"/>'
        "<wp:cNvGraphicFramePr/>"
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        '<wps:wsp xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
        "<wps:cNvCnPr/><wps:spPr>"
        f'<a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="{LINE_HEIGHT_EMU}"/></a:xfrm>'
        '<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
        '<a:ln w="9525"><a:solidFill><a:srgbClr val="000000"/></a:solidFill></a:ln>'
        "</wps:spPr><wps:bodyPr/></wps:wsp></a:graphicData></a:graphic>"
        "</wp:anchor></w:drawing></w:r></w:p>"
    )


def build_all_lines():
    return (
        build_vertical_line(LEFT_LINE_A_EMU, "Line Left A", 900101)
        + build_vertical_line(LEFT_LINE_B_EMU, "Line Left B", 900102)
        + build_vertical_line(RIGHT_LINE_EMU, "Line Right", 900103)
    )


def inject(header_path, count=28):
    with open(header_path, encoding="utf-8") as f:
        content = f.read()
    if "</w:hdr>" not in content:
        raise ValueError(f"{header_path} has no </w:hdr> closing tag — is this a valid header part?")
    injection = build_number_paragraphs(count) + build_all_lines()
    content = content.replace("</w:hdr>", injection + "</w:hdr>")
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Injected {count} line-number paragraphs and 3 vertical line drawings into {header_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inject_line_numbers.py <path-to-header1.xml> [count]")
        sys.exit(1)
    header_path = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 28
    inject(header_path, count)

