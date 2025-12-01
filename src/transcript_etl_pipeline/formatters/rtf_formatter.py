"""RTF formatter for transcript documents.

This module generates Rich Text Format (.rtf) files with proper formatting
according to the transcript formatting rules using string-based RTF generation.
"""

from transcript_etl_pipeline.document.formatting_rules import (
    BODY_FONT,
    NOTES_HEADER_FONT,
    SPACING_RULES,
)
from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Paragraph,
    SectionType,
)


def format_to_rtf(doc: Document, output_path: str) -> None:
    """Format transcript document to RTF file.

    Applies all formatting rules:
    - 10pt Calibri font
    - Bold labels, normal body text
    - Single line spacing (1.0)
    - No extra spacing for metadata
    - 12pt spacing above Transcript: label and speaker paragraphs
    - 6pt spacing above regular paragraphs
    - Notes headers in bold 14pt
    - Notes body with bullet support

    Args:
        doc: The transcript document to format
        output_path: Path where the RTF file should be saved
    """
    rtf_content = _generate_rtf(doc)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rtf_content)


def _generate_rtf(doc: Document) -> str:
    """Generate RTF content from transcript document.

    Args:
        doc: The transcript document to format

    Returns:
        Complete RTF document as a string
    """
    # RTF header with font table
    rtf_parts = [
        r"{\rtf1\ansi\deff0",
        r"{\fonttbl{\f0\fswiss\fcharset0 Calibri;}}",
        r"\viewkind4\uc1",
    ]

    # Process all sections
    for section in doc.sections:
        rtf_parts.extend(_format_section(section))

    # Close RTF document
    rtf_parts.append("}")

    return "\n".join(rtf_parts)


def _format_section(section: DocumentSection) -> list[str]:
    """Format a document section to RTF.

    Args:
        section: The transcript section to format

    Returns:
        List of RTF strings for the section
    """
    rtf_parts: list[str] = []
    for paragraph in section.paragraphs:
        rtf_parts.extend(_format_paragraph(paragraph, section.section_type))
    return rtf_parts


def _format_paragraph(paragraph: Paragraph, section_type: SectionType) -> list[str]:
    """Format a single paragraph to RTF.

    Args:
        paragraph: The paragraph to format
        section_type: The type of section this paragraph belongs to

    Returns:
        List of RTF strings for the paragraph
    """
    rtf_parts: list[str] = []

    # Determine spacing based on section type
    spacing = SPACING_RULES[section_type]

    # RTF uses twips (1/20 of a point)
    # space_before in points * 20 = twips
    space_before_twips = int(spacing.before_pt * 20)
    space_after_twips = int(spacing.after_pt * 20)

    # Handle notes header (bold, larger font)
    if section_type == SectionType.NOTES_HEADER:
        line_spacing_twips = int(NOTES_HEADER_FONT.size_pt * 20 * spacing.line_spacing)
        rtf_parts.append(
            rf"\pard\sb{space_before_twips}\sa{space_after_twips}"
            rf"\f0\fs{int(NOTES_HEADER_FONT.size_pt * 2)}\sl{line_spacing_twips}\slmult1"
        )
        escaped_text = _escape_rtf(paragraph.text)
        rtf_parts.append(rf"{{\b {escaped_text}}}")
        rtf_parts.append(r"\par")
        return rtf_parts

    # Handle notes body
    if section_type == SectionType.NOTES_BODY:
        line_spacing_twips = int(BODY_FONT.size_pt * 20 * spacing.line_spacing)
        rtf_parts.append(
            rf"\pard\sb{space_before_twips}\sa{space_after_twips}"
            rf"\f0\fs{int(BODY_FONT.size_pt * 2)}\sl{line_spacing_twips}\slmult1"
        )
        if paragraph.is_bullet:
            # Add bullet character
            escaped_text = _escape_rtf(paragraph.text)
            rtf_parts.append(rf"\u8226  {escaped_text}")  # Unicode bullet: •
        else:
            escaped_text = _escape_rtf(paragraph.text)
            rtf_parts.append(escaped_text)
        rtf_parts.append(r"\par")
        return rtf_parts

    # RTF paragraph formatting:
    # \sb<n> = space before in twips
    # \sa<n> = space after in twips
    # \fs<n> = font size in half-points (10pt = 20)
    # \sl<n> = line spacing in twips
    # \slmult1 = line spacing is relative to font size
    line_spacing_twips = int(BODY_FONT.size_pt * 20 * spacing.line_spacing)
    rtf_parts.append(
        rf"\pard\sb{space_before_twips}\sa{space_after_twips}"
        rf"\f0\fs{int(BODY_FONT.size_pt * 2)}\sl{line_spacing_twips}\slmult1"
    )

    # Add label if present (bold)
    if paragraph.label:
        escaped_label = _escape_rtf(paragraph.label.text)
        rtf_parts.append(rf"{{\b {escaped_label} }}")

    # Add body text (normal - not bold)
    if paragraph.text:
        escaped_body = _escape_rtf(paragraph.text)
        rtf_parts.append(escaped_body)

    # End paragraph
    rtf_parts.append(r"\par")

    return rtf_parts


def _escape_rtf(text: str) -> str:
    """Escape special RTF characters.

    Args:
        text: Text to escape

    Returns:
        RTF-escaped text
    """
    # Escape backslash, braces, and other special RTF characters
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("\r\n", r"\par ")
    text = text.replace("\n", r"\par ")
    text = text.replace("\r", r"\par ")
    return text
