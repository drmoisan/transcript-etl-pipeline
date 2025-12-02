"""Notes transformation module.

This module provides functionality to transform raw Markdown notes
into DocumentSection objects that can be merged into a Document.
"""

import re
from datetime import datetime

from transcript_etl_pipeline.document.model import (
    DocumentSection,
    Paragraph,
    SectionType,
)


def transform_notes(text: str, label: str | None = None) -> list[DocumentSection]:
    """Transform raw Markdown notes text into DocumentSection objects.

    Parses markdown headers (# ## ###) and bullet points (- *) with nesting support.
    Creates appropriate DocumentSection objects for each element.

    If a label is provided and the input doesn't start with a heading, the label
    is added as an H2 header before the content.

    If the input starts with a H1 heading, adds the label (or "Notes") as H2 after it.

    Args:
        text: Raw Markdown notes text to transform
        label: Optional label for the notes header (e.g., "Notes – 2025-01-01").
               If None, no label header is added unless input has an H1.

    Returns:
        List of DocumentSection objects representing the markdown structure.
    """
    sections: list[DocumentSection] = []

    # Parse the markdown content
    paragraphs = _parse_markdown(text)

    # If no paragraphs, return empty (or just the label header)
    if not paragraphs:
        # Add a header if label is provided
        if label:
            header_section = DocumentSection(
                section_type=SectionType.NOTES_HEADER,
                paragraphs=[Paragraph(text=label, heading_level=2)],
            )
            sections.append(header_section)
        return sections

    # Check if first paragraph is a H1 heading (title)
    first_is_h1 = paragraphs and paragraphs[0].heading_level == 1

    # If there's no H1 heading and a label is provided, add it as the header first
    if not first_is_h1 and label:
        sections.append(
            DocumentSection(
                section_type=SectionType.NOTES_HEADER,
                paragraphs=[Paragraph(text=label, heading_level=2)],
            )
        )

    # Track if we've added the notes H2 after an H1 title
    added_notes_header = False

    # Group paragraphs into sections
    current_body_paragraphs: list[Paragraph] = []

    for para in paragraphs:
        if para.heading_level > 0:
            # Flush any body paragraphs
            if current_body_paragraphs:
                sections.append(
                    DocumentSection(
                        section_type=SectionType.NOTES_BODY,
                        paragraphs=current_body_paragraphs,
                    )
                )
                current_body_paragraphs = []

            # Add heading section
            sections.append(
                DocumentSection(
                    section_type=SectionType.NOTES_HEADER,
                    paragraphs=[para],
                )
            )

            # If this was the H1 title, add "Notes" H2 header after it
            if first_is_h1 and para.heading_level == 1 and not added_notes_header:
                notes_label = label if label else "Notes"
                sections.append(
                    DocumentSection(
                        section_type=SectionType.NOTES_HEADER,
                        paragraphs=[Paragraph(text=notes_label, heading_level=2)],
                    )
                )
                added_notes_header = True
        else:
            # Add to body
            current_body_paragraphs.append(para)

    # Flush remaining body paragraphs
    if current_body_paragraphs:
        sections.append(
            DocumentSection(
                section_type=SectionType.NOTES_BODY,
                paragraphs=current_body_paragraphs,
            )
        )

    return sections


def _generate_notes_label() -> str:
    """Generate a notes label with the current timestamp.

    Returns:
        A label string like "Notes – 2025-01-01 14:30"
    """
    now = datetime.now()
    return f"Notes – {now.strftime('%Y-%m-%d %H:%M')}"


def _parse_markdown(text: str) -> list[Paragraph]:
    """Parse markdown text into paragraphs with heading and bullet support.

    Args:
        text: Raw markdown text

    Returns:
        List of Paragraph objects with appropriate flags set
    """
    paragraphs: list[Paragraph] = []

    # Normalize line endings to \n for processing
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Check for headings (# ## ###)
        heading_level = _get_heading_level(line)
        if heading_level > 0:
            # Extract heading text (remove # prefix)
            heading_text = line.lstrip("#").strip()
            paragraphs.append(
                Paragraph(
                    text=heading_text,
                    heading_level=heading_level,
                    section_type=SectionType.NOTES_HEADER,
                )
            )
            continue

        # Check for bullet points
        bullet_level, bullet_text = _parse_bullet_line(line)
        if bullet_level > 0:
            # Clean up the bullet text
            cleaned_text = _clean_markdown_text(bullet_text)
            paragraphs.append(
                Paragraph(
                    text=cleaned_text,
                    is_bullet=True,
                    bullet_level=bullet_level,
                    section_type=SectionType.NOTES_BODY,
                )
            )
            continue

        # Regular paragraph
        cleaned_text = _clean_markdown_text(line.strip())
        paragraphs.append(
            Paragraph(
                text=cleaned_text,
                section_type=SectionType.NOTES_BODY,
            )
        )

    return paragraphs


def _clean_markdown_text(text: str) -> str:
    """Clean markdown formatting from text.

    Removes or converts:
    - Escaped dollar signs (\\$) -> $
    - Bold markers (**text**) -> text

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove escaped dollar signs
    cleaned = text.replace("\\$", "$")

    # Remove bold markers (** and __)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)

    return cleaned


def _get_heading_level(line: str) -> int:
    """Determine the heading level from a line.

    Args:
        line: Line of text

    Returns:
        Heading level (1, 2, 3) or 0 if not a heading
    """
    stripped = line.lstrip()
    if stripped.startswith("### "):
        return 3
    elif stripped.startswith("## "):
        return 2
    elif stripped.startswith("# "):
        return 1
    return 0


def _parse_bullet_line(line: str) -> tuple[int, str]:
    """Parse a bullet line and determine its level.

    Args:
        line: Line of text

    Returns:
        Tuple of (bullet_level, bullet_text) where bullet_level is:
        - 0 if not a bullet
        - 1 for top-level bullet (no indentation)
        - 2 for nested bullet (indented with spaces)
    """
    # Count leading spaces to determine nesting
    stripped = line.lstrip()

    # Check if it's a bullet
    if not (stripped.startswith("- ") or stripped.startswith("* ")):
        return (0, "")

    # Count leading whitespace
    leading_spaces = len(line) - len(stripped)

    # Determine bullet level based on indentation
    # 0-1 spaces = level 1, 2+ spaces = level 2
    bullet_level = 2 if leading_spaces >= 2 else 1

    # Extract bullet text (remove the marker)
    bullet_text = stripped[2:].strip()

    return (bullet_level, bullet_text)


# Keep legacy function for backward compatibility
def _parse_notes_body(text: str) -> list[Paragraph]:
    """Parse notes text into paragraphs, detecting bullet points.

    This is a legacy function kept for backward compatibility.
    Use _parse_markdown for new code.

    Args:
        text: Raw notes text (may contain Markdown bullet points)

    Returns:
        List of Paragraph objects with is_bullet set appropriately
    """
    return _parse_markdown(text)
