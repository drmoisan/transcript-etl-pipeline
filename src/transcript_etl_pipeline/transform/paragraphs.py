"""Paragraph detection and formatting for transcript text.

This module implements paragraph detection heuristics for transcript text,
inserting CRLF after detected paragraphs while preserving document structure.
"""

import re

__all__ = [
    "detect_paragraphs",
    "_is_label_line",
    "_ends_with_sentence_terminator",
    "_should_add_paragraph_break",
]


def detect_paragraphs(text: str) -> str:
    """Detect and format paragraphs in transcript text.

    Uses heuristics to identify paragraph boundaries:
    - Sentence endings (., ?, !)
    - Label boundaries (lines starting with capitalized word followed by colon)
    - Metadata termination (first label marks end of metadata)
    - Line length analysis (short lines after long lines may indicate pauses)

    Inserts CRLF after each paragraph but NOT at the very end of the document.

    Args:
        text: Normalized text with CRLF line endings

    Returns:
        Text with paragraph breaks inserted
    """
    if not text or not text.strip():
        return text

    lines = text.split("\r\n")
    result_lines: list[str] = []
    in_metadata = True
    i = 0

    while i < len(lines):
        line = lines[i]
        result_lines.append(line)

        # Check if this is a label (marks end of metadata or speaker change)
        is_label = _is_label_line(line)
        if is_label:
            in_metadata = False

        # Don't add paragraph breaks in metadata (before first label)
        if in_metadata:
            i += 1
            continue

        # Check if we should add a paragraph break after this line
        is_last_line = i == len(lines) - 1
        if not is_last_line and _should_add_paragraph_break(line, lines, i):
            # Add blank line for paragraph break (unless next line is already blank or a label)
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if next_line.strip() and not _is_label_line(next_line):
                result_lines.append("")

        i += 1

    return "\r\n".join(result_lines)


def _is_label_line(line: str) -> bool:
    """Check if a line starts with a label (e.g., 'Speaker:', 'John:').

    Args:
        line: The line to check

    Returns:
        True if line starts with a label
    """
    # Match single-word capitalized token ending with colon at line start
    pattern = r"^[A-Z][A-Za-z0-9]*:\s"
    return bool(re.match(pattern, line))


def _should_add_paragraph_break(
    current_line: str, all_lines: list[str], current_index: int
) -> bool:
    """Determine if a paragraph break should be added after the current line.

    Args:
        current_line: The current line being processed
        all_lines: All lines in the text
        current_index: Index of current line

    Returns:
        True if a paragraph break should be added
    """
    # Empty lines don't need paragraph breaks
    if not current_line.strip():
        return False

    # Check for sentence endings
    if _ends_with_sentence_terminator(current_line):
        return True

    # Check for major pause indicator (long line followed by shorter line)
    if current_index + 1 < len(all_lines):
        next_line = all_lines[current_index + 1].strip()
        if next_line and not _is_label_line(next_line):
            current_len = len(current_line.strip())
            next_len = len(next_line)
            # If current line is long and next is significantly shorter, might be a pause
            if current_len > 60 and next_len < current_len * 0.6:
                return True

    return False


def _ends_with_sentence_terminator(line: str) -> bool:
    """Check if a line ends with a sentence terminator.

    Args:
        line: The line to check

    Returns:
        True if line ends with ., ?, or !
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    return stripped[-1] in ".?!"
