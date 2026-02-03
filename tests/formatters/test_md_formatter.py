"""Tests for the Markdown formatter module (in-memory)."""

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)
from transcript_etl_pipeline.formatters.md_formatter import (
    _format_paragraph,  # pyright: ignore[reportPrivateUsage]
    _generate_markdown,  # pyright: ignore[reportPrivateUsage]
)


class TestMarkdownFormatterInMemory:
    """Tests for Markdown formatter helpers."""

    def test_generate_markdown_contains_content(self) -> None:
        """Generated markdown contains paragraph content."""
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="This is a test paragraph."))
        doc.add_section(section)

        content = _generate_markdown(doc)

        assert "This is a test paragraph." in content

    def test_notes_header_inserts_blank_line_and_heading_prefix(self) -> None:
        """Notes header adds blank line and heading prefix when not first."""
        paragraph = Paragraph(text="Notes")

        parts = _format_paragraph(paragraph, SectionType.NOTES_HEADER, is_first=False)

        assert parts[0] == ""
        assert parts[1] == "# Notes"

    def test_transcript_label_gets_blank_line_before_when_not_first(self) -> None:
        """Transcript label gets a blank line above when not first."""
        paragraph = Paragraph(label=Label("Transcript:"), text="")

        parts = _format_paragraph(paragraph, SectionType.REGULAR_PARAGRAPH, is_first=False)

        assert parts[0] == ""
        assert "**Transcript:**" in parts[-1]
