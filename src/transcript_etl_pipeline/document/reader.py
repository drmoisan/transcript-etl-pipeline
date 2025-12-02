"""Document reader module for re-ingesting existing documents.

This module provides functionality to parse existing output files (DOCX, MD)
back into the Document model to support the "Add to Existing" workflow.
"""

import locale
from pathlib import Path
from typing import Any

from docx import Document as DocxDocument  # type: ignore[import-untyped]

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)


def read_document(path: Path | str) -> Document:
    """Read an existing document file and parse it into a Document model.

    Supports Markdown (.md) and DOCX (.docx) files.

    Args:
        path: Path to the document file

    Returns:
        Document model representing the file contents

    Raises:
        ValueError: If the file extension is not supported
        FileNotFoundError: If the file does not exist
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = file_path.suffix.lower()

    if extension == ".md":
        return _read_markdown(file_path)
    elif extension == ".docx":
        return _read_docx(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {extension}. Supported: .md, .docx")


def _read_markdown(path: Path) -> Document:
    """Read a Markdown file and parse it into a Document model.

    Uses header patterns to identify sections:
    - "# Notes" header indicates notes section start
    - "**Transcript:**" or "Transcript:" indicates transcript section start
    - Lines before these are treated as metadata

    Args:
        path: Path to the Markdown file

    Returns:
        Document model representing the file contents
    """
    encodings_to_try = ["utf-8"]
    preferred_encoding = locale.getpreferredencoding(False)
    if preferred_encoding and preferred_encoding.lower() not in ("utf-8", "utf_8"):
        encodings_to_try.append(preferred_encoding)
    encodings_to_try.append("utf-8-sig")

    content: str | None = None
    for enc in encodings_to_try:
        try:
            content = path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        # As a last resort, replace undecodable characters so we still return a document
        content = path.read_text(encoding="utf-8", errors="replace")

    return _parse_markdown_content(content)


def _parse_markdown_content(content: str) -> Document:
    """Parse Markdown content into a Document model.

    Args:
        content: Markdown text content

    Returns:
        Document model representing the content
    """
    doc = Document()
    lines = content.split("\n")

    # State machine to track current section
    current_section_type: SectionType | None = None
    current_paragraphs: list[Paragraph] = []

    # Flags to track if we've seen notes or transcript
    in_notes_header = False
    in_notes_body = False
    in_transcript = False

    for line in lines:
        stripped = line.strip()

        # Check for Notes header (e.g., "# Notes – 2025-01-01")
        if stripped.startswith("# Notes") or stripped.startswith("# notes"):
            # Flush any previous section
            if current_paragraphs:
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []

            # Start new notes header section
            in_notes_header = True
            in_notes_body = False
            in_transcript = False
            current_section_type = SectionType.NOTES_HEADER
            # Remove the # prefix for the paragraph
            header_text = (
                stripped[2:].strip() if stripped.startswith("# ") else stripped[1:].strip()
            )
            current_paragraphs = [Paragraph(text=header_text)]
            continue

        # Check for Transcript header (e.g., "**Transcript:**" or "Transcript:")
        if _is_transcript_label(stripped):
            # Flush any previous section
            if current_paragraphs:
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []

            in_notes_header = False
            in_notes_body = False
            in_transcript = True
            current_section_type = SectionType.TRANSCRIPT_LABEL

            # Create paragraph with label
            label = Label(text="Transcript:", is_speaker=False)
            current_paragraphs = [
                Paragraph(label=label, text="", section_type=SectionType.TRANSCRIPT_LABEL)
            ]
            continue

        # Handle content based on current state
        if not stripped:
            # Empty line - may separate paragraphs or sections
            if in_notes_header and current_paragraphs:
                # End of notes header, start notes body
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []
                in_notes_header = False
                in_notes_body = True
                current_section_type = SectionType.NOTES_BODY
            elif current_section_type == SectionType.TRANSCRIPT_LABEL and current_paragraphs:
                # Flush transcript label section
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []
                current_section_type = SectionType.REGULAR_PARAGRAPH
            continue

        # Parse content based on current section
        if in_notes_body or (current_section_type == SectionType.NOTES_BODY):
            # Parse as notes body content
            in_notes_body = True
            current_section_type = SectionType.NOTES_BODY
            para = _parse_notes_line(stripped)
            current_paragraphs.append(para)
        elif in_transcript or current_section_type in (
            SectionType.TRANSCRIPT_LABEL,
            SectionType.SPEAKER_PARAGRAPH,
            SectionType.REGULAR_PARAGRAPH,
        ):
            # Parse as transcript content
            if current_section_type == SectionType.TRANSCRIPT_LABEL and current_paragraphs:
                # Flush the transcript label first
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []

            para, section_type = _parse_transcript_line(stripped)
            if (
                section_type == SectionType.SPEAKER_PARAGRAPH
                and current_paragraphs
                and current_section_type
            ):
                # Speaker paragraph starts a new section
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []
            current_section_type = section_type
            current_paragraphs.append(para)
        elif current_section_type is None or current_section_type == SectionType.METADATA:
            # Initial content - treat as metadata
            current_section_type = SectionType.METADATA
            para = Paragraph(text=stripped, section_type=SectionType.METADATA)
            current_paragraphs.append(para)
        else:
            # Default: add to current section
            para = Paragraph(text=stripped, section_type=current_section_type)
            current_paragraphs.append(para)

    # Flush final section
    if current_paragraphs:
        _add_section_to_doc(doc, current_section_type, current_paragraphs)

    return doc


def _is_transcript_label(line: str) -> bool:
    """Check if a line is a transcript label.

    Args:
        line: Line of text to check

    Returns:
        True if the line is a transcript label
    """
    lower = line.lower()
    # Check for "**Transcript:**" or "Transcript:"
    return (
        lower == "transcript:" or lower == "**transcript:**" or lower.startswith("**transcript:**")
    )


def _parse_notes_line(line: str) -> Paragraph:
    """Parse a notes line into a Paragraph.

    Args:
        line: Line of text (should be stripped)

    Returns:
        Paragraph with is_bullet set if line starts with bullet marker
    """
    is_bullet = line.startswith("- ") or line.startswith("* ")
    text = line[2:].strip() if is_bullet else line
    return Paragraph(text=text, is_bullet=is_bullet, section_type=SectionType.NOTES_BODY)


def _parse_transcript_line(line: str) -> tuple[Paragraph, SectionType]:
    """Parse a transcript line into a Paragraph and determine section type.

    Args:
        line: Line of text (should be stripped)

    Returns:
        Tuple of (Paragraph, SectionType)
    """
    # Check for speaker label pattern: **Name:** or Name:
    label_match = _extract_speaker_label(line)
    if label_match:
        label_text, remaining = label_match
        label = Label(text=label_text, is_speaker=True)
        return (
            Paragraph(label=label, text=remaining, section_type=SectionType.SPEAKER_PARAGRAPH),
            SectionType.SPEAKER_PARAGRAPH,
        )

    return (
        Paragraph(text=line, section_type=SectionType.REGULAR_PARAGRAPH),
        SectionType.REGULAR_PARAGRAPH,
    )


def _extract_speaker_label(line: str) -> tuple[str, str] | None:
    """Extract a speaker label from a line if present.

    Handles patterns like:
    - "**John:** Hello there"
    - "John: Hello there"
    - "**Dan Moisan:** Some text"

    Args:
        line: Line of text

    Returns:
        Tuple of (label_text with colon, remaining text) or None
    """
    # Pattern for **Name:** format
    if line.startswith("**"):
        end_bold = line.find("**", 2)
        if end_bold > 2:
            potential_label = line[2:end_bold]
            if potential_label.endswith(":"):
                remaining = line[end_bold + 2 :].strip()
                return (potential_label, remaining)

    # Pattern for Name: format (word followed by colon)
    colon_idx = line.find(":")
    if colon_idx > 0:
        potential_label = line[: colon_idx + 1]
        # Check if it looks like a name (capitalize words, no special chars)
        name_part = potential_label[:-1].strip()
        if name_part and _looks_like_name(name_part):
            remaining = line[colon_idx + 1 :].strip()
            return (potential_label, remaining)

    return None


def _looks_like_name(text: str) -> bool:
    """Check if text looks like a person's name.

    Args:
        text: Text to check

    Returns:
        True if text appears to be a name
    """
    # Allow "Speaker A", "Speaker B", etc.
    if text.startswith("Speaker "):
        return True

    # Check if it's capitalized words (like "John" or "Dan Moisan")
    words = text.split()
    if not words:
        return False

    return all(word[0].isupper() for word in words)


def _add_section_to_doc(
    doc: Document, section_type: SectionType | None, paragraphs: list[Paragraph]
) -> None:
    """Add a section to the document.

    Args:
        doc: Document to add section to
        section_type: Type of section
        paragraphs: List of paragraphs in the section
    """
    if section_type is None or not paragraphs:
        return

    section = DocumentSection(section_type=section_type, paragraphs=paragraphs)
    doc.add_section(section)


def _read_docx(path: Path) -> Document:
    """Read a DOCX file and parse it into a Document model.

    Uses paragraph styles and text patterns to identify sections:
    - Notes headers (typically bold or heading style)
    - Bullet points (list paragraph style)
    - Transcript sections (speaker labels)

    Args:
        path: Path to the DOCX file

    Returns:
        Document model representing the file contents
    """
    docx_doc: Any = DocxDocument(str(path))  # type: ignore[no-untyped-call]
    doc = Document()

    current_section_type: SectionType | None = None
    current_paragraphs: list[Paragraph] = []

    in_notes = False
    in_transcript = False

    for para in docx_doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Check for notes header
        if text.startswith("Notes") and ("–" in text or "-" in text):
            # Flush previous section
            if current_paragraphs:
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []

            in_notes = True
            in_transcript = False
            current_section_type = SectionType.NOTES_HEADER
            current_paragraphs = [Paragraph(text=text)]
            continue

        # Check for transcript label
        if text.lower() == "transcript:" or text.lower().startswith("transcript:"):
            # Flush previous section
            if current_paragraphs:
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []

            in_notes = False
            in_transcript = True
            current_section_type = SectionType.TRANSCRIPT_LABEL
            label = Label(text="Transcript:", is_speaker=False)
            current_paragraphs = [
                Paragraph(label=label, text="", section_type=SectionType.TRANSCRIPT_LABEL)
            ]
            continue

        # Parse based on current state
        if in_notes:
            # After notes header, content is notes body
            if current_section_type == SectionType.NOTES_HEADER:
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []
                current_section_type = SectionType.NOTES_BODY

            # Check for bullet (by style or text pattern)
            is_bullet = _is_docx_bullet(para)
            current_paragraphs.append(
                Paragraph(text=text, is_bullet=is_bullet, section_type=SectionType.NOTES_BODY)
            )
        elif in_transcript:
            # Parse as transcript
            if current_section_type == SectionType.TRANSCRIPT_LABEL:
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []

            para_obj, section_type = _parse_transcript_line(text)
            if (
                section_type == SectionType.SPEAKER_PARAGRAPH
                and current_paragraphs
                and current_section_type
            ):
                # Speaker starts new section
                _add_section_to_doc(doc, current_section_type, current_paragraphs)
                current_paragraphs = []
            current_section_type = section_type
            current_paragraphs.append(para_obj)
        else:
            # Initial content - metadata
            current_section_type = SectionType.METADATA
            current_paragraphs.append(Paragraph(text=text, section_type=SectionType.METADATA))

    # Flush final section
    if current_paragraphs:
        _add_section_to_doc(doc, current_section_type, current_paragraphs)

    return doc


def _is_docx_bullet(para: Any) -> bool:
    """Check if a DOCX paragraph is a bullet point.

    Args:
        para: python-docx Paragraph object

    Returns:
        True if the paragraph appears to be a bullet
    """
    # Check for list-related styles
    style_name = para.style.name.lower() if para.style else ""
    if "list" in style_name or "bullet" in style_name:
        return True

    # Check for bullet character at start
    text = para.text.strip()
    if text.startswith("• ") or text.startswith("- ") or text.startswith("* "):
        return True

    # Check for numbering (XML-level check)
    try:
        if (
            para._element.pPr is not None and para._element.pPr.numPr is not None
        ):  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            return True
    except (AttributeError, TypeError):
        pass

    return False
