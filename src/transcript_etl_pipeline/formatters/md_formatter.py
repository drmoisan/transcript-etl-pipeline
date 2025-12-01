"""Markdown formatter for transcript documents.

This module generates Markdown (.md) files with formatting that approximates
the transcript formatting rules within Markdown's limitations.
"""

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Paragraph,
    SectionType,
)


def format_to_md(doc: Document, output_path: str) -> None:
    """Format transcript document to Markdown file.

    Applies formatting rules adapted for Markdown:
    - Bold labels using **label:**
    - Normal body text
    - Blank lines approximate spacing (no precise point-based spacing)
    - Preserves paragraph structure
    - Notes headers as # heading
    - Notes body with bullet prefix for bullets

    Args:
        doc: The transcript document to format
        output_path: Path where the MD file should be saved
    """
    md_content = _generate_markdown(doc)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)


def _generate_markdown(doc: Document) -> str:
    """Generate Markdown content from transcript document.

    Args:
        doc: The transcript document to format

    Returns:
        Complete Markdown document as a string
    """
    md_parts: list[str] = []

    # Process all sections
    for section in doc.sections:
        md_parts.extend(_format_section(section))

    # Join all parts and ensure no extra blank line at the end
    content = "\n".join(md_parts).rstrip("\n")
    return content + "\n"


def _format_section(section: DocumentSection) -> list[str]:
    """Format a document section to Markdown.

    Args:
        section: The transcript section to format

    Returns:
        List of Markdown strings for the section
    """
    md_parts: list[str] = []
    for i, paragraph in enumerate(section.paragraphs):
        md_parts.extend(_format_paragraph(paragraph, section.section_type, is_first=i == 0))
    return md_parts


def _format_paragraph(paragraph: Paragraph, section_type: SectionType, is_first: bool) -> list[str]:
    """Format a single paragraph to Markdown.

    Args:
        paragraph: The paragraph to format
        section_type: The type of section this paragraph belongs to
        is_first: Whether this is the first paragraph in the section

    Returns:
        List of Markdown strings for the paragraph
    """
    md_parts: list[str] = []

    # Handle notes header (use # heading)
    if section_type == SectionType.NOTES_HEADER:
        if not is_first:
            md_parts.append("")
        md_parts.append(f"# {paragraph.text}")
        return md_parts

    # Handle notes body
    if section_type == SectionType.NOTES_BODY:
        if not is_first:
            # No blank line between consecutive bullets, blank line otherwise
            pass
        if paragraph.is_bullet:
            md_parts.append(f"- {paragraph.text}")
        else:
            md_parts.append(paragraph.text)
        return md_parts

    # Add spacing approximation using blank lines
    # Metadata: no extra blank lines
    # Transcript label: add blank line above (unless first)
    # Speaker paragraphs: add blank line above (unless first)
    # Regular paragraphs: add blank line above (unless first or after metadata)
    if not is_first and section_type != SectionType.METADATA:
        if paragraph.label and paragraph.label.text.lower() == "transcript:":
            # Transcript label gets extra spacing (approximate with blank line)
            md_parts.append("")
        elif paragraph.label:
            # Speaker paragraphs get spacing
            md_parts.append("")
        elif section_type in (SectionType.SPEAKER_PARAGRAPH, SectionType.REGULAR_PARAGRAPH):
            # Regular paragraphs in transcript section
            md_parts.append("")

    # Build paragraph text
    paragraph_text = ""

    # Add label if present (bold)
    if paragraph.label:
        paragraph_text += f"**{paragraph.label.text}** "

    # Add body text
    if paragraph.text:
        paragraph_text += paragraph.text

    md_parts.append(paragraph_text)

    return md_parts
