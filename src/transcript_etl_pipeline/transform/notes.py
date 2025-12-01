"""Notes transformation module.

This module provides functionality to transform raw Markdown notes
into DocumentSection objects that can be merged into a Document.
"""

from datetime import datetime

from transcript_etl_pipeline.document.model import (
    DocumentSection,
    Paragraph,
    SectionType,
)


def transform_notes(text: str, label: str | None = None) -> list[DocumentSection]:
    """Transform raw Markdown notes text into DocumentSection objects.

    Creates a NOTES_HEADER section with the label (or auto-generated timestamp)
    and a NOTES_BODY section with the parsed content. Lines starting with
    '- ' or '* ' are treated as bullet points.

    Args:
        text: Raw Markdown notes text to transform
        label: Optional label for the notes header (e.g., "Notes – 2025-01-01").
               If None, a label is generated with the current timestamp.

    Returns:
        List of DocumentSection objects [NOTES_HEADER, NOTES_BODY]
        The list may contain only NOTES_HEADER if the text is empty.
    """
    sections: list[DocumentSection] = []

    # Create the header section with label
    header_label = label if label else _generate_notes_label()
    header_section = DocumentSection(
        section_type=SectionType.NOTES_HEADER,
        paragraphs=[Paragraph(text=header_label)],
    )
    sections.append(header_section)

    # Parse the notes body
    body_paragraphs = _parse_notes_body(text)
    if body_paragraphs:
        body_section = DocumentSection(
            section_type=SectionType.NOTES_BODY,
            paragraphs=body_paragraphs,
        )
        sections.append(body_section)

    return sections


def _generate_notes_label() -> str:
    """Generate a notes label with the current timestamp.

    Returns:
        A label string like "Notes – 2025-01-01 14:30"
    """
    now = datetime.now()
    return f"Notes – {now.strftime('%Y-%m-%d %H:%M')}"


def _parse_notes_body(text: str) -> list[Paragraph]:
    """Parse notes text into paragraphs, detecting bullet points.

    Args:
        text: Raw notes text (may contain Markdown bullet points)

    Returns:
        List of Paragraph objects with is_bullet set appropriately
    """
    paragraphs: list[Paragraph] = []

    # Normalize line endings to \n for processing
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")

    current_paragraph_lines: list[str] = []
    current_is_bullet = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines - they separate paragraphs
        if not stripped:
            if current_paragraph_lines:
                # Flush current paragraph
                para_text = " ".join(current_paragraph_lines).strip()
                if para_text:
                    paragraphs.append(Paragraph(text=para_text, is_bullet=current_is_bullet))
                current_paragraph_lines = []
                current_is_bullet = False
            continue

        # Check if this is a bullet point
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")

        if is_bullet:
            # Flush any previous non-bullet paragraph
            if current_paragraph_lines and not current_is_bullet:
                para_text = " ".join(current_paragraph_lines).strip()
                if para_text:
                    paragraphs.append(Paragraph(text=para_text, is_bullet=False))
                current_paragraph_lines = []

            # Extract bullet content (remove the marker)
            bullet_text = stripped[2:].strip()
            if bullet_text:
                # Each bullet is its own paragraph
                if current_is_bullet and current_paragraph_lines:
                    # Flush previous bullet
                    para_text = " ".join(current_paragraph_lines).strip()
                    if para_text:
                        paragraphs.append(Paragraph(text=para_text, is_bullet=True))
                    current_paragraph_lines = []

                current_paragraph_lines.append(bullet_text)
                current_is_bullet = True
        else:
            # Regular line
            if current_is_bullet and current_paragraph_lines:
                # Check if this is a continuation of a bullet (indented)
                if line.startswith("  ") or line.startswith("\t"):
                    # Continuation of previous bullet
                    current_paragraph_lines.append(stripped)
                else:
                    # Flush previous bullet and start new non-bullet paragraph
                    para_text = " ".join(current_paragraph_lines).strip()
                    if para_text:
                        paragraphs.append(Paragraph(text=para_text, is_bullet=True))
                    current_paragraph_lines = [stripped]
                    current_is_bullet = False
            else:
                # Continue or start regular paragraph
                current_paragraph_lines.append(stripped)
                current_is_bullet = False

    # Flush final paragraph
    if current_paragraph_lines:
        para_text = " ".join(current_paragraph_lines).strip()
        if para_text:
            paragraphs.append(Paragraph(text=para_text, is_bullet=current_is_bullet))

    return paragraphs
