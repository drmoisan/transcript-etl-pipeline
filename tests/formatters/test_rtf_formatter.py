"""Tests for the RTF formatter module (in-memory)."""

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)
from transcript_etl_pipeline.formatters.rtf_formatter import (
    _escape_rtf,  # pyright: ignore[reportPrivateUsage]
    _format_paragraph,  # pyright: ignore[reportPrivateUsage]
    _generate_rtf,  # pyright: ignore[reportPrivateUsage]
)


class TestRtfFormatterInMemory:
    """Tests for RTF formatter helpers."""

    def test_generate_rtf_contains_header(self) -> None:
        """Generated RTF includes header and font table."""
        doc = Document()
        content = _generate_rtf(doc)

        assert r"{\rtf1" in content
        assert r"{\fonttbl" in content
        assert "Calibri" in content

    def test_format_paragraph_speaker_label_bold_and_body_text(self) -> None:
        """Speaker labels render bold and body text is escaped."""
        paragraph = Paragraph(label=Label("Speaker:"), text="Hello {world}.")

        parts = _format_paragraph(paragraph, SectionType.SPEAKER_PARAGRAPH)
        joined = "".join(parts)

        assert r"{\b Speaker: }" in joined
        assert r"Hello \{world\}." in joined

    def test_format_paragraph_notes_header_uses_bold(self) -> None:
        """Notes headers render bold with header font sizing."""
        paragraph = Paragraph(text="Meeting Notes")

        parts = _format_paragraph(paragraph, SectionType.NOTES_HEADER)
        joined = "".join(parts)

        assert r"{\b Meeting Notes}" in joined

    def test_escape_rtf_converts_newlines_to_par(self) -> None:
        """Newlines are converted to RTF paragraph markers."""
        assert _escape_rtf("Line1\nLine2") == r"Line1\par Line2"

    def test_generate_rtf_includes_section_paragraphs(self) -> None:
        """Sections are rendered into the RTF output."""
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Body text"))
        doc.add_section(section)

        content = _generate_rtf(doc)
        assert "Body text" in content
