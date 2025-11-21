"""Text normalization for transcript processing.

This module normalizes raw transcript text by:
1. Converting line endings to Windows CRLF
2. Cleaning up whitespace
3. Normalizing labels (single-word capitalized tokens ending with colon)
4. Ensuring labels appear at the beginning of lines
"""

from __future__ import annotations

import re


def _normalize_line_endings(text: str) -> str:
    """Convert all line endings to Windows CRLF (\\r\\n).

    Args:
        text: Input text with various line ending types

    Returns:
        Text with normalized CRLF line endings
    """
    # First normalize to LF, then convert to CRLF
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\n", "\r\n")
    return text


def _clean_whitespace(text: str) -> str:
    """Clean up whitespace in text.

    Removes:
    - Duplicate spaces within lines
    - Trailing spaces on lines
    - Multiple consecutive blank lines (collapse to single blank line)

    Args:
        text: Input text

    Returns:
        Text with cleaned whitespace
    """
    lines = text.split("\r\n")
    cleaned_lines: list[str] = []
    prev_blank = False

    for line in lines:
        # Remove duplicate spaces and trailing spaces
        line = re.sub(r" {2,}", " ", line)
        line = line.rstrip()

        # Collapse multiple blank lines to single blank line
        is_blank = not line.strip()
        if is_blank:
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False

    # Remove trailing blank lines
    while cleaned_lines and not cleaned_lines[-1]:
        cleaned_lines.pop()

    return "\r\n".join(cleaned_lines)


def _is_label(token: str) -> bool:
    """Check if a token is a valid label.

    A label is a single-word capitalized token ending with colon.

    Args:
        token: Token to check

    Returns:
        True if token is a label
    """
    if not token.endswith(":"):
        return False

    # Remove the colon and check the rest
    word = token[:-1]

    # Must be non-empty
    if not word:
        return False

    # Must not contain whitespace (single word)
    if " " in word or "\t" in word:
        return False

    # First character must be uppercase
    return word[0].isupper()


def _normalize_labels(text: str) -> str:
    """Normalize labels in the text.

    Rules:
    1. Labels must appear at the beginning of a line
    2. Labels must be followed by exactly one space
    3. Mid-line labels get a CRLF inserted before them

    Args:
        text: Input text

    Returns:
        Text with normalized labels
    """
    lines = text.split("\r\n")
    normalized_lines: list[str] = []

    for line in lines:
        # Check if line starts with a label
        match = re.match(r"^([A-Z][^\s:]*:)\s*(.*)", line)
        if match:
            label = match.group(1)
            rest = match.group(2)
            # Ensure exactly one space after label
            normalized_lines.append(f"{label} {rest}".rstrip())
            continue

        # Check for mid-line labels
        # Look for pattern like: "text SomeLabel: more text"
        # Pattern: word boundary + capitalized word + colon
        parts = re.split(r"(\s+[A-Z][^\s:]*:)", line)

        if len(parts) == 1:
            # No mid-line label found
            normalized_lines.append(line)
        else:
            # Process parts - odd indices are the labels (with leading space)
            current_line = parts[0]
            for i in range(1, len(parts)):
                if i % 2 == 1:  # This is a label with leading space
                    label = parts[i].strip()
                    if _is_label(label):
                        # Add current line if non-empty, start new line with label
                        if current_line.strip():
                            normalized_lines.append(current_line.rstrip())
                        current_line = label
                    else:
                        current_line += parts[i]
                else:
                    # Regular text after label - add with single space
                    text_part = parts[i].lstrip()
                    if current_line.endswith(":"):
                        current_line += " " + text_part if text_part else ""
                    else:
                        current_line += " " + text_part if text_part else ""

            if current_line.strip():
                normalized_lines.append(current_line.rstrip())

    return "\r\n".join(normalized_lines)


def normalize_text(text: str) -> str:
    """Normalize raw transcript text.

    Applies all normalization rules:
    1. Normalize line endings to CRLF
    2. Clean up whitespace
    3. Normalize labels

    Args:
        text: Raw transcript text

    Returns:
        Normalized text
    """
    text = _normalize_line_endings(text)
    text = _clean_whitespace(text)
    text = _normalize_labels(text)
    return text
