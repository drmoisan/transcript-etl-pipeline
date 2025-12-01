"""Tests for notes transformation module.

Tests the transform_notes function that converts raw Markdown notes
into DocumentSection objects.
"""

import re
from datetime import datetime
from unittest.mock import patch

from transcript_etl_pipeline.document.model import SectionType
from transcript_etl_pipeline.transform.notes import (
    _generate_notes_label,  # pyright: ignore[reportPrivateUsage]
    _parse_notes_body,  # pyright: ignore[reportPrivateUsage]
    transform_notes,
)


class TestTransformNotes:
    """Tests for transform_notes function."""

    def test_transform_notes_creates_header_and_body(self) -> None:
        """transform_notes creates both header and body sections."""
        text = "This is a note."
        sections = transform_notes(text, label="Notes – 2025-01-01")

        assert len(sections) == 2
        assert sections[0].section_type == SectionType.NOTES_HEADER
        assert sections[1].section_type == SectionType.NOTES_BODY

    def test_transform_notes_uses_provided_label(self) -> None:
        """transform_notes uses the provided label for header."""
        text = "Note content"
        label = "Meeting Notes – 2025-01-15"
        sections = transform_notes(text, label=label)

        assert sections[0].paragraphs[0].text == label

    def test_transform_notes_generates_label_when_none(self) -> None:
        """transform_notes generates timestamp label when none provided."""
        text = "Note content"

        with patch("transcript_etl_pipeline.transform.notes.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 20, 14, 30)
            sections = transform_notes(text, label=None)

        assert sections[0].paragraphs[0].text == "Notes – 2025-01-20 14:30"

    def test_transform_notes_empty_text_returns_header_only(self) -> None:
        """transform_notes returns only header when text is empty."""
        sections = transform_notes("", label="Notes")

        assert len(sections) == 1
        assert sections[0].section_type == SectionType.NOTES_HEADER

    def test_transform_notes_whitespace_only_returns_header_only(self) -> None:
        """transform_notes returns only header when text is whitespace only."""
        sections = transform_notes("   \n  \n   ", label="Notes")

        assert len(sections) == 1
        assert sections[0].section_type == SectionType.NOTES_HEADER

    def test_transform_notes_simple_text(self) -> None:
        """transform_notes correctly parses simple text."""
        text = "This is a simple note."
        sections = transform_notes(text, label="Notes")

        body = sections[1]
        assert len(body.paragraphs) == 1
        assert body.paragraphs[0].text == "This is a simple note."
        assert body.paragraphs[0].is_bullet is False

    def test_transform_notes_bullet_points(self) -> None:
        """transform_notes correctly detects bullet points."""
        text = """- First bullet
- Second bullet
- Third bullet"""
        sections = transform_notes(text, label="Notes")

        body = sections[1]
        assert len(body.paragraphs) == 3
        assert all(p.is_bullet for p in body.paragraphs)
        assert body.paragraphs[0].text == "First bullet"
        assert body.paragraphs[1].text == "Second bullet"
        assert body.paragraphs[2].text == "Third bullet"

    def test_transform_notes_asterisk_bullets(self) -> None:
        """transform_notes correctly detects asterisk bullets."""
        text = """* First item
* Second item"""
        sections = transform_notes(text, label="Notes")

        body = sections[1]
        assert len(body.paragraphs) == 2
        assert all(p.is_bullet for p in body.paragraphs)

    def test_transform_notes_mixed_content(self) -> None:
        """transform_notes handles mixed bullets and regular text."""
        text = """Introduction paragraph.

- Bullet one
- Bullet two

Conclusion paragraph."""
        sections = transform_notes(text, label="Notes")

        body = sections[1]
        assert len(body.paragraphs) == 4
        assert body.paragraphs[0].is_bullet is False
        assert body.paragraphs[0].text == "Introduction paragraph."
        assert body.paragraphs[1].is_bullet is True
        assert body.paragraphs[1].text == "Bullet one"
        assert body.paragraphs[2].is_bullet is True
        assert body.paragraphs[2].text == "Bullet two"
        assert body.paragraphs[3].is_bullet is False
        assert body.paragraphs[3].text == "Conclusion paragraph."

    def test_transform_notes_multiline_paragraph(self) -> None:
        """transform_notes joins multiple lines into single paragraph."""
        text = """This is a paragraph
that spans multiple lines
and should be joined."""
        sections = transform_notes(text, label="Notes")

        body = sections[1]
        assert len(body.paragraphs) == 1
        expected = "This is a paragraph that spans multiple lines and should be joined."
        assert body.paragraphs[0].text == expected

    def test_transform_notes_crlf_line_endings(self) -> None:
        """transform_notes handles Windows CRLF line endings."""
        text = "Line one\r\nLine two\r\nLine three"
        sections = transform_notes(text, label="Notes")

        body = sections[1]
        assert len(body.paragraphs) == 1
        assert body.paragraphs[0].text == "Line one Line two Line three"


class TestGenerateNotesLabel:
    """Tests for _generate_notes_label helper function."""

    def test_generate_notes_label_format(self) -> None:
        """_generate_notes_label produces correct format."""
        with patch("transcript_etl_pipeline.transform.notes.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 6, 15, 9, 5)
            label = _generate_notes_label()

        assert label == "Notes – 2025-06-15 09:05"

    def test_generate_notes_label_uses_current_time(self) -> None:
        """_generate_notes_label uses current datetime."""
        label = _generate_notes_label()

        # Should contain "Notes –" prefix
        assert label.startswith("Notes – ")

        # Should have date pattern
        date_pattern = r"Notes – \d{4}-\d{2}-\d{2} \d{2}:\d{2}"
        assert re.match(date_pattern, label)


class TestParseNotesBody:
    """Tests for _parse_notes_body helper function."""

    def test_parse_notes_body_empty_returns_empty_list(self) -> None:
        """_parse_notes_body returns empty list for empty input."""
        result = _parse_notes_body("")
        assert result == []

    def test_parse_notes_body_single_line(self) -> None:
        """_parse_notes_body handles single line."""
        result = _parse_notes_body("Single line")
        assert len(result) == 1
        assert result[0].text == "Single line"
        assert result[0].is_bullet is False

    def test_parse_notes_body_multiple_paragraphs(self) -> None:
        """_parse_notes_body splits on blank lines."""
        text = """First paragraph.

Second paragraph."""
        result = _parse_notes_body(text)
        assert len(result) == 2
        assert result[0].text == "First paragraph."
        assert result[1].text == "Second paragraph."

    def test_parse_notes_body_bullet_continuation(self) -> None:
        """_parse_notes_body handles indented bullet continuation."""
        text = """- This is a bullet
  that continues on the next line"""
        result = _parse_notes_body(text)
        assert len(result) == 1
        assert result[0].is_bullet is True
        assert result[0].text == "This is a bullet that continues on the next line"

    def test_parse_notes_body_strips_whitespace(self) -> None:
        """_parse_notes_body strips leading/trailing whitespace."""
        text = "  Line with spaces  "
        result = _parse_notes_body(text)
        assert len(result) == 1
        assert result[0].text == "Line with spaces"

    def test_parse_notes_body_consecutive_bullets(self) -> None:
        """_parse_notes_body creates separate paragraphs for consecutive bullets."""
        text = """- First
- Second
- Third"""
        result = _parse_notes_body(text)
        assert len(result) == 3
        assert all(p.is_bullet for p in result)

    def test_parse_notes_body_bullet_after_text(self) -> None:
        """_parse_notes_body correctly transitions from text to bullet."""
        text = """Regular text
- Bullet point"""
        result = _parse_notes_body(text)
        assert len(result) == 2
        assert result[0].is_bullet is False
        assert result[0].text == "Regular text"
        assert result[1].is_bullet is True
        assert result[1].text == "Bullet point"

    def test_parse_notes_body_text_after_bullet(self) -> None:
        """_parse_notes_body correctly transitions from bullet to text."""
        text = """- Bullet point
Regular text"""
        result = _parse_notes_body(text)
        assert len(result) == 2
        assert result[0].is_bullet is True
        assert result[0].text == "Bullet point"
        assert result[1].is_bullet is False
        assert result[1].text == "Regular text"

    def test_parse_notes_body_empty_bullet_ignored(self) -> None:
        """_parse_notes_body handles bullet with just whitespace after marker."""
        text = """- First bullet
-
- Third bullet"""
        result = _parse_notes_body(text)
        # Empty bullet line ("-" alone) should be treated as non-bullet text
        # The result depends on how we handle transition from bullet
        assert len(result) >= 2
        # First bullet should be captured
        assert result[0].text == "First bullet"
        assert result[0].is_bullet is True

    def test_parse_notes_body_multiple_blank_lines(self) -> None:
        """_parse_notes_body handles multiple consecutive blank lines."""
        text = """First paragraph.



Second paragraph."""
        result = _parse_notes_body(text)
        assert len(result) == 2
