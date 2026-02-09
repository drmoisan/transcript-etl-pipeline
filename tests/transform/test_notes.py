"""Tests for notes transformation module.

Tests the transform_notes function that converts raw Markdown notes
into DocumentSection objects.
"""

import re
from datetime import datetime
from unittest.mock import patch

from transcript_etl_pipeline.document.model import SectionType
from transcript_etl_pipeline.transform.notes import (
    _clean_markdown_text,  # pyright: ignore[reportPrivateUsage]
    _generate_notes_label,  # pyright: ignore[reportPrivateUsage]
    _get_heading_level,  # pyright: ignore[reportPrivateUsage]
    _parse_bullet_line,  # pyright: ignore[reportPrivateUsage]
    _parse_markdown,  # pyright: ignore[reportPrivateUsage]
    transform_notes,
)


class TestTransformNotes:
    """Tests for transform_notes function."""

    def test_transform_notes_simple_text_no_header(self) -> None:
        """transform_notes creates body section for text without headings."""
        text = "This is a note."
        sections = transform_notes(text)

        # Without a label, should just create body section
        assert len(sections) == 1
        assert sections[0].section_type == SectionType.NOTES_BODY
        assert sections[0].paragraphs[0].text == "This is a note."

    def test_transform_notes_with_label_no_heading(self) -> None:
        """transform_notes with label and no heading adds label as header."""
        text = "Note content"
        label = "Meeting Notes"
        sections = transform_notes(text, label=label)

        # Label is added as header when provided (even without H1 in input)
        assert len(sections) == 2
        assert sections[0].section_type == SectionType.NOTES_HEADER
        assert sections[0].paragraphs[0].text == label
        assert sections[1].section_type == SectionType.NOTES_BODY
        assert sections[1].paragraphs[0].text == "Note content"

    def test_transform_notes_with_h1_title(self) -> None:
        """transform_notes adds 'Notes' H2 after H1 title."""
        text = "# Document Title\n\nSome content"
        sections = transform_notes(text)

        # Should have: H1 title, Notes H2, body
        assert len(sections) == 3
        assert sections[0].section_type == SectionType.NOTES_HEADER
        assert sections[0].paragraphs[0].text == "Document Title"
        assert sections[0].paragraphs[0].heading_level == 1
        assert sections[1].section_type == SectionType.NOTES_HEADER
        assert sections[1].paragraphs[0].text == "Notes"
        assert sections[1].paragraphs[0].heading_level == 2
        assert sections[2].section_type == SectionType.NOTES_BODY

    def test_regression_transform_notes_label_after_h1_with_label(self) -> None:
        """Ensure provided label is used for H2 after H1."""
        text = "# Title\n\n- Bullet"
        sections = transform_notes(text, label="Meeting Notes")

        assert sections[0].paragraphs[0].text == "Title"
        assert sections[0].paragraphs[0].heading_level == 1
        assert sections[1].paragraphs[0].text == "Meeting Notes"
        assert sections[1].paragraphs[0].heading_level == 2

    def test_transform_notes_empty_text_with_label(self) -> None:
        """transform_notes returns only header when text is empty with label."""
        sections = transform_notes("", label="Notes")

        assert len(sections) == 1
        assert sections[0].section_type == SectionType.NOTES_HEADER

    def test_transform_notes_empty_text_no_label(self) -> None:
        """transform_notes returns empty when text is empty and no label."""
        sections = transform_notes("")

        assert len(sections) == 0

    def test_transform_notes_whitespace_only_returns_empty(self) -> None:
        """transform_notes returns empty when text is whitespace only."""
        sections = transform_notes("   \n  \n   ")

        assert len(sections) == 0

    def test_transform_notes_bullet_points(self) -> None:
        """transform_notes correctly detects bullet points."""
        text = """- First bullet
- Second bullet
- Third bullet"""
        sections = transform_notes(text)

        body = sections[0]
        assert body.section_type == SectionType.NOTES_BODY
        assert len(body.paragraphs) == 3
        assert all(p.is_bullet for p in body.paragraphs)
        assert body.paragraphs[0].text == "First bullet"
        assert body.paragraphs[1].text == "Second bullet"
        assert body.paragraphs[2].text == "Third bullet"

    def test_transform_notes_nested_bullets(self) -> None:
        """transform_notes correctly detects nested bullets."""
        text = """- Top level
  - Nested level"""
        sections = transform_notes(text)

        body = sections[0]
        assert len(body.paragraphs) == 2
        assert body.paragraphs[0].bullet_level == 1
        assert body.paragraphs[1].bullet_level == 2

    def test_transform_notes_asterisk_bullets(self) -> None:
        """transform_notes correctly detects asterisk bullets."""
        text = """* First item
* Second item"""
        sections = transform_notes(text)

        body = sections[0]
        assert len(body.paragraphs) == 2
        assert all(p.is_bullet for p in body.paragraphs)

    def test_transform_notes_h3_section_headers(self) -> None:
        """transform_notes creates separate sections for H3 headers."""
        text = """### Section One

- Bullet one

### Section Two

- Bullet two"""
        sections = transform_notes(text)

        # Should have: H3, body, H3, body
        assert len(sections) == 4
        assert sections[0].section_type == SectionType.NOTES_HEADER
        assert sections[0].paragraphs[0].heading_level == 3
        assert sections[1].section_type == SectionType.NOTES_BODY
        assert sections[2].section_type == SectionType.NOTES_HEADER
        assert sections[3].section_type == SectionType.NOTES_BODY


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


class TestParseMarkdown:
    """Tests for _parse_markdown helper function."""

    def test_parse_markdown_empty_returns_empty_list(self) -> None:
        """_parse_markdown returns empty list for empty input."""
        result = _parse_markdown("")
        assert result == []

    def test_parse_markdown_single_line(self) -> None:
        """_parse_markdown handles single line."""
        result = _parse_markdown("Single line")
        assert len(result) == 1
        assert result[0].text == "Single line"
        assert result[0].is_bullet is False

    def test_parse_markdown_h1_heading(self) -> None:
        """_parse_markdown detects H1 heading."""
        result = _parse_markdown("# Title")
        assert len(result) == 1
        assert result[0].heading_level == 1
        assert result[0].text == "Title"

    def test_parse_markdown_h2_heading(self) -> None:
        """_parse_markdown detects H2 heading."""
        result = _parse_markdown("## Section")
        assert len(result) == 1
        assert result[0].heading_level == 2
        assert result[0].text == "Section"

    def test_parse_markdown_h3_heading(self) -> None:
        """_parse_markdown detects H3 heading."""
        result = _parse_markdown("### Subsection")
        assert len(result) == 1
        assert result[0].heading_level == 3
        assert result[0].text == "Subsection"

    def test_parse_markdown_bullet_level_1(self) -> None:
        """_parse_markdown detects top-level bullets."""
        result = _parse_markdown("- Item")
        assert len(result) == 1
        assert result[0].is_bullet is True
        assert result[0].bullet_level == 1
        assert result[0].text == "Item"

    def test_regression_parse_markdown_mixed_order(self) -> None:
        """_parse_markdown preserves heading/bullet ordering."""
        result = _parse_markdown("# Title\n- One\n## Section\n- Two")
        assert [item.text for item in result] == ["Title", "One", "Section", "Two"]
        assert result[0].heading_level == 1
        assert result[2].heading_level == 2
        assert result[1].is_bullet is True
        assert result[3].is_bullet is True


class TestCleanMarkdownText:
    """Tests for markdown cleanup helper."""

    def test_regression_clean_markdown_text_escapes(self) -> None:
        """_clean_markdown_text strips markdown emphasis and escapes."""
        result = _clean_markdown_text("\\$100 **bold** __strong__")
        assert result == "$100 bold strong"


class TestHeadingAndBulletHelpers:
    """Tests for heading and bullet parsing helpers."""

    def test_regression_get_heading_level_leading_whitespace(self) -> None:
        """_get_heading_level ignores leading whitespace."""
        assert _get_heading_level("  ## Heading") == 2

    def test_regression_parse_bullet_line_indentation_levels(self) -> None:
        """_parse_bullet_line returns expected indentation levels."""
        assert _parse_bullet_line("- Item") == (1, "Item")
        assert _parse_bullet_line("  - Nested") == (2, "Nested")

    def test_parse_markdown_bullet_level_2(self) -> None:
        """_parse_markdown detects nested bullets."""
        result = _parse_markdown("  - Nested item")
        assert len(result) == 1
        assert result[0].is_bullet is True
        assert result[0].bullet_level == 2

    def test_parse_markdown_consecutive_bullets(self) -> None:
        """_parse_markdown creates separate paragraphs for consecutive bullets."""
        text = """- First
- Second
- Third"""
        result = _parse_markdown(text)
        assert len(result) == 3
        assert all(p.is_bullet for p in result)

    def test_parse_markdown_mixed_bullet_levels(self) -> None:
        """_parse_markdown handles mixed bullet levels."""
        text = """- Top
  - Nested
- Top again"""
        result = _parse_markdown(text)
        assert len(result) == 3
        assert result[0].bullet_level == 1
        assert result[1].bullet_level == 2
        assert result[2].bullet_level == 1

    def test_parse_markdown_strips_whitespace(self) -> None:
        """_parse_markdown strips leading/trailing whitespace."""
        text = "  Line with spaces  "
        result = _parse_markdown(text)
        assert len(result) == 1
        assert result[0].text == "Line with spaces"
