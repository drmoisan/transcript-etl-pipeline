"""Tests for the RTF formatter module."""

import tempfile
from pathlib import Path

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)
from transcript_etl_pipeline.formatters.rtf_formatter import format_to_rtf


class TestFormatToRTF:
    """Tests for format_to_rtf function."""

    def test_empty_document(self) -> None:
        """Test formatting an empty document."""
        # Arrange
        doc = Document()

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert r"{\rtf1" in content
            assert r"{\fonttbl" in content
            assert "Calibri" in content
        finally:
            Path(output_path).unlink()

    def test_simple_paragraph(self) -> None:
        """Test formatting a document with a simple paragraph."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="This is a test paragraph."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "This is a test paragraph." in content
            assert r"\par" in content
        finally:
            Path(output_path).unlink()

    def test_paragraph_with_label(self) -> None:
        """Test formatting a paragraph with a label."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello world."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "Speaker:" in content
            assert "Hello world." in content
            # Check that label is bold (enclosed in {\b })
            assert r"{\b Speaker: }" in content
        finally:
            Path(output_path).unlink()

    def test_metadata_section(self) -> None:
        """Test formatting metadata section with no extra spacing."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.METADATA)
        section.add_paragraph(Paragraph(label=Label("Date:"), text="2024-01-01"))
        section.add_paragraph(Paragraph(label=Label("Attendees:"), text="John, Jane"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "Date:" in content
            assert "2024-01-01" in content
            assert "Attendees:" in content
            assert "John, Jane" in content
            # Metadata should have \sb0 (no space before)
            assert r"\sb0" in content
        finally:
            Path(output_path).unlink()

    def test_transcript_label_spacing(self) -> None:
        """Test that Transcript: label gets 12pt spacing above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.TRANSCRIPT_LABEL)
        section.add_paragraph(Paragraph(label=Label("Transcript:"), text=""))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # 12pt * 20 twips/pt = 240 twips
            assert r"\sb240" in content
        finally:
            Path(output_path).unlink()

    def test_speaker_paragraph_spacing(self) -> None:
        """Test that speaker paragraphs get 12pt spacing above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # 12pt * 20 twips/pt = 240 twips
            assert r"\sb240" in content
        finally:
            Path(output_path).unlink()

    def test_regular_paragraph_spacing(self) -> None:
        """Test that regular paragraphs get 6pt spacing above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Regular paragraph."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # 6pt * 20 twips/pt = 120 twips
            assert r"\sb120" in content
        finally:
            Path(output_path).unlink()

    def test_special_characters_escaped(self) -> None:
        """Test that special RTF characters are properly escaped."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Test {braces} and \\backslash."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert r"\{braces\}" in content
            assert r"\\backslash" in content
        finally:
            Path(output_path).unlink()

    def test_multiple_sections(self) -> None:
        """Test formatting document with multiple sections."""
        # Arrange
        doc = Document()

        # Metadata section
        metadata = DocumentSection(section_type=SectionType.METADATA)
        metadata.add_paragraph(Paragraph(label=Label("Date:"), text="2024-01-01"))
        doc.add_section(metadata)

        # Transcript section
        transcript = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        transcript.add_paragraph(Paragraph(label=Label("Transcript:"), text=""))
        transcript.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello."))
        doc.add_section(transcript)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "Date:" in content
            assert "Transcript:" in content
            assert "Speaker:" in content
        finally:
            Path(output_path).unlink()

    def test_font_size(self) -> None:
        """Test that 10pt font size is set (20 half-points)."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Test text."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # 10pt * 2 = 20 half-points
            assert r"\fs20" in content
        finally:
            Path(output_path).unlink()


class TestRtfNotesFormatting:
    """Tests for RTF notes section formatting edge cases."""

    def test_notes_body_non_bullet_paragraph(self) -> None:
        """Notes body with non-bullet paragraph has regular text (no bullet char)."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_BODY)
        section.add_paragraph(Paragraph(text="Regular notes text.", is_bullet=False))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # Text should be present
            assert "Regular notes text." in content
            # Should NOT have bullet character
            assert r"\u8226" not in content
            # Should have paragraph end marker
            assert r"\par" in content
        finally:
            Path(output_path).unlink()

    def test_notes_body_mixed_bullet_and_regular(self) -> None:
        """Notes body with mix of bullet and non-bullet paragraphs."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_BODY)
        section.add_paragraph(Paragraph(text="Intro text", is_bullet=False))
        section.add_paragraph(Paragraph(text="Bullet point", is_bullet=True))
        section.add_paragraph(Paragraph(text="More regular text", is_bullet=False))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # All text should be present
            assert "Intro text" in content
            assert "Bullet point" in content
            assert "More regular text" in content
            # Only the bullet point should have bullet character
            assert content.count(r"\u8226") == 1
        finally:
            Path(output_path).unlink()

    def test_notes_body_spacing(self) -> None:
        """Notes body uses 6pt spacing above (120 twips)."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_BODY)
        section.add_paragraph(Paragraph(text="Notes text", is_bullet=False))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # 6pt * 20 twips/pt = 120 twips
            assert r"\sb120" in content
        finally:
            Path(output_path).unlink()

    def test_newline_escaping_in_rtf(self) -> None:
        """Newlines in text are properly escaped to RTF paragraph markers."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Line one\nLine two"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # \n should be escaped to \par
            assert r"Line one\par Line two" in content
        finally:
            Path(output_path).unlink()

    def test_crlf_escaping_in_rtf(self) -> None:
        """CRLF in text are properly escaped to RTF paragraph markers."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Line one\r\nLine two"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # \r\n should be escaped to \par
            assert r"Line one\par Line two" in content
        finally:
            Path(output_path).unlink()

    def test_carriage_return_escaping_in_rtf(self) -> None:
        """Carriage returns in text are properly escaped to RTF paragraph markers."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Line one\rLine two"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rtf", delete=False) as f:
            output_path = f.name

        try:
            format_to_rtf(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # \r should be escaped to \par
            assert r"Line one\par Line two" in content
        finally:
            Path(output_path).unlink()
