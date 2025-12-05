"""Tests for the Markdown formatter module."""

import tempfile
from pathlib import Path

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)
from transcript_etl_pipeline.formatters.md_formatter import format_to_md


class TestFormatToMD:
    """Tests for format_to_md function."""

    def test_empty_document(self) -> None:
        """Test formatting an empty document."""
        # Arrange
        doc = Document()

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert content == "\n"
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "This is a test paragraph." in content
        finally:
            Path(output_path).unlink()

    def test_paragraph_with_label(self) -> None:
        """Test formatting a paragraph with a label (bold)."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello world."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "**Speaker:**" in content
            assert "Hello world." in content
        finally:
            Path(output_path).unlink()

    def test_metadata_section(self) -> None:
        """Test formatting metadata section with no extra blank lines."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.METADATA)
        section.add_paragraph(Paragraph(label=Label("Date:"), text="2024-01-01"))
        section.add_paragraph(Paragraph(label=Label("Attendees:"), text="John, Jane"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            lines = content.split("\n")
            # Should have Date: and Attendees: on consecutive lines (no blank line)
            assert "**Date:** 2024-01-01" in lines
            assert "**Attendees:** John, Jane" in lines
            # Check they are consecutive
            date_idx = lines.index("**Date:** 2024-01-01")
            attendees_idx = lines.index("**Attendees:** John, Jane")
            assert attendees_idx == date_idx + 1
        finally:
            Path(output_path).unlink()

    def test_transcript_label_spacing(self) -> None:
        """Test that Transcript: label gets blank line above (when not first)."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Intro text."))
        section.add_paragraph(Paragraph(label=Label("Transcript:"), text=""))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            lines = content.split("\n")
            # Should have blank line before Transcript:
            transcript_idx = next(i for i, line in enumerate(lines) if "Transcript:" in line)
            assert lines[transcript_idx - 1] == ""
        finally:
            Path(output_path).unlink()

    def test_speaker_paragraph_spacing(self) -> None:
        """Test that speaker paragraphs get blank line above (when not first)."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker1:"), text="Hello."))
        section.add_paragraph(Paragraph(label=Label("Speaker2:"), text="Hi there."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            lines = content.split("\n")
            # Second speaker should have blank line before it
            speaker2_idx = next(i for i, line in enumerate(lines) if "Speaker2:" in line)
            assert lines[speaker2_idx - 1] == ""
        finally:
            Path(output_path).unlink()

    def test_regular_paragraph_spacing(self) -> None:
        """Test that regular paragraphs get blank line above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="First paragraph."))
        section.add_paragraph(Paragraph(text="Second paragraph."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            lines = content.split("\n")
            # Second paragraph should have blank line before it
            second_idx = next(i for i, line in enumerate(lines) if "Second paragraph." in line)
            assert lines[second_idx - 1] == ""
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "**Date:** 2024-01-01" in content
            assert "**Transcript:**" in content
            assert "**Speaker:** Hello." in content
        finally:
            Path(output_path).unlink()

    def test_no_extra_blank_line_at_end(self) -> None:
        """Test that document ends with single newline, not extra blank lines."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Test paragraph."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # Should end with exactly one newline
            assert content.endswith("\n")
            assert not content.endswith("\n\n")
        finally:
            Path(output_path).unlink()

    def test_label_only_paragraph(self) -> None:
        """Test paragraph with only a label, no body text."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Transcript:"), text=""))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # Should have bold label with trailing space
            assert "**Transcript:** " in content or "**Transcript:**\n" in content
        finally:
            Path(output_path).unlink()

    def test_preserves_paragraph_structure(self) -> None:
        """Test that paragraph structure is preserved."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker:"), text="Line one.\nLine two."))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            assert "**Speaker:** Line one.\nLine two." in content
        finally:
            Path(output_path).unlink()


class TestNotesSectionFormatting:
    """Tests for notes section formatting edge cases."""

    def test_notes_header_not_first_gets_blank_line(self) -> None:
        """Notes header not first in section gets a blank line before it."""
        # Arrange - two notes header paragraphs in same section
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_HEADER)
        section.add_paragraph(Paragraph(text="First Header"))
        section.add_paragraph(Paragraph(text="Second Header"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            lines = content.split("\n")
            # Find position of Second Header
            second_idx = next(i for i, line in enumerate(lines) if "Second Header" in line)
            # There should be a blank line before Second Header
            assert lines[second_idx - 1] == ""
        finally:
            Path(output_path).unlink()

    def test_multiple_notes_headers_spacing(self) -> None:
        """Multiple notes headers in same section have blank lines between them."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_HEADER)
        section.add_paragraph(Paragraph(text="Header One"))
        section.add_paragraph(Paragraph(text="Header Two"))
        section.add_paragraph(Paragraph(text="Header Three"))
        doc.add_section(section)

        # Act
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            format_to_md(doc, output_path)

            # Assert
            content = Path(output_path).read_text(encoding="utf-8")
            # First header should have no blank line before
            assert content.startswith("# Header One")
            # Subsequent headers should have blank lines
            assert "\n\n# Header Two" in content
            assert "\n\n# Header Three" in content
        finally:
            Path(output_path).unlink()
