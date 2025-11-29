"""Parser for converting enhanced text into Document model.

This module parses enhanced transcript text (after normalization and enhancement)
into the structured Document model for formatting.
"""

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)


def parse_enhanced_text(text: str) -> Document:
    """Parse enhanced transcript text into Document model.

    Args:
        text: Enhanced text with CRLF line endings, normalized labels, paragraphs

    Returns:
        Document model ready for formatting
    """
    doc = Document()
    lines = text.split("\r\n")

    # Determine sections
    in_metadata = True
    current_section_type = SectionType.METADATA
    current_section = DocumentSection(section_type=current_section_type)

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines between sections
        if not line.strip():
            i += 1
            continue

        # Check if this is a label line
        label = extract_label(line)

        # If we find a non-metadata label, switch to transcript section
        if in_metadata and label and not is_metadata_label(label.text):
            # Save metadata section
            if current_section.paragraphs:
                doc.add_section(current_section)

            in_metadata = False

            # Determine section type based on label
            if label.text.lower() == "transcript:":
                current_section_type = SectionType.TRANSCRIPT_LABEL
            else:
                current_section_type = SectionType.SPEAKER_PARAGRAPH

            current_section = DocumentSection(section_type=current_section_type)

        # Collect paragraph lines
        paragraph_lines: list[str] = []
        para_label = label

        # Add the rest of the first line if it has content after label
        if label:
            rest_of_line = line[len(label.text) + 1 :].strip()  # +1 for space after colon
            if rest_of_line:
                paragraph_lines.append(rest_of_line)
        else:
            paragraph_lines.append(line)

        # Look ahead for continuation lines
        i += 1
        while i < len(lines):
            next_line = lines[i]

            # Stop if we hit a blank line or another label
            if not next_line.strip() or extract_label(next_line):
                break

            paragraph_lines.append(next_line)
            i += 1

        # Create paragraph
        para_text = " ".join(paragraph_lines).strip()
        paragraph = Paragraph(label=para_label, text=para_text)

        current_section.add_paragraph(paragraph)

        # After adding paragraph, check if we should start a new section
        # If this was Transcript: label, next section should be speaker/regular
        if para_label and para_label.text.lower() == "transcript:":
            doc.add_section(current_section)
            current_section_type = SectionType.SPEAKER_PARAGRAPH
            current_section = DocumentSection(section_type=current_section_type)

    # Add final section
    if current_section.paragraphs:
        doc.add_section(current_section)

    return doc


def extract_label(line: str) -> Label | None:
    """Extract a label from a line if it starts with one.

    A label is defined as:
    - Starts at the beginning of the line
    - Single word (no whitespace) ending with ':'
    - First character is uppercase
    - Matches the definition in normalize.py

    Args:
        line: Line to check

    Returns:
        Label if found, None otherwise
    """
    if not line:
        return None

    import re

    # Match: start of line, uppercase letter, any non-whitespace chars, colon
    # This matches the normalize.py definition: single word, starts with capital, ends with :
    m = re.match(r"^([A-Z][^\s:]*?):", line)

    if m:
        return Label(text=m.group(1) + ":")

    return None


def is_metadata_label(label_text: str) -> bool:
    """Check if a label is a metadata label.

    Args:
        label_text: Label text including colon

    Returns:
        True if it's a metadata label
    """
    metadata_labels = {
        "date:",
        "time:",
        "attendees:",
        "participants:",
        "location:",
        "subject:",
        "meeting title",
    }
    return label_text.lower() in metadata_labels
