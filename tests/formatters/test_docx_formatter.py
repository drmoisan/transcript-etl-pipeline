"""Tests for the DOCX formatter module.

This module tests DOCX output formatting including spacing, fonts, labels,
and section handling for transcript documents.
"""

from pathlib import Path

from docx import Document as DocxDocument  # type: ignore[import-untyped]
from docx.shared import Pt  # type: ignore[import-untyped]

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx


class TestFormatToDocx:
    """Tests for format_to_docx function."""

    def test_empty_document(self, tmp_path: Path) -> None:
        """Formatting an empty document produces a valid DOCX file."""
        # Arrange
        doc = Document()
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        assert output_path.exists()
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        assert len(docx_doc.paragraphs) == 0

    def test_simple_paragraph_text(self, tmp_path: Path) -> None:
        """Regular paragraph text appears in the DOCX output."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="This is a test paragraph."))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        assert len(docx_doc.paragraphs) == 1
        assert docx_doc.paragraphs[0].text == "This is a test paragraph."

    def test_paragraph_with_label_bold(self, tmp_path: Path) -> None:
        """Paragraph with label has bold label text and normal body text."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello world."))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        # Paragraph should have two runs: label (bold) and body (normal)
        assert len(para.runs) == 2
        label_run = para.runs[0]
        body_run = para.runs[1]
        # Label should be bold
        assert label_run.bold is True
        assert "Speaker:" in label_run.text
        # Body should not be bold
        assert body_run.bold is False
        assert "Hello world." in body_run.text

    def test_metadata_section_no_extra_spacing(self, tmp_path: Path) -> None:
        """Metadata section has no extra spacing before paragraphs."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.METADATA)
        section.add_paragraph(Paragraph(label=Label("Date:"), text="2024-01-01"))
        section.add_paragraph(Paragraph(label=Label("Attendees:"), text="John, Jane"))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        for para in docx_doc.paragraphs:
            # Metadata should have 0pt space before
            # pyright: ignore[reportUnknownMemberType] - python-docx is untyped
            assert para.paragraph_format.space_before == Pt(0)  # type: ignore[reportUnknownMemberType]

    def test_transcript_label_spacing(self, tmp_path: Path) -> None:
        """Transcript label section has 12pt spacing above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.TRANSCRIPT_LABEL)
        section.add_paragraph(Paragraph(label=Label("Transcript:"), text=""))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        # python-docx is untyped - space_before has unknown type
        assert para.paragraph_format.space_before == Pt(12)  # type: ignore[reportUnknownMemberType]

    def test_speaker_paragraph_spacing(self, tmp_path: Path) -> None:
        """Speaker paragraphs have 12pt spacing above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello."))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        # python-docx is untyped - space_before has unknown type
        assert para.paragraph_format.space_before == Pt(12)  # type: ignore[reportUnknownMemberType]

    def test_regular_paragraph_spacing(self, tmp_path: Path) -> None:
        """Regular paragraphs have 6pt spacing above."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Regular paragraph."))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        # python-docx is untyped - space_before has unknown type
        assert para.paragraph_format.space_before == Pt(6)  # type: ignore[reportUnknownMemberType]

    def test_multiple_sections(self, tmp_path: Path) -> None:
        """Document with multiple sections formats correctly."""
        # Arrange
        doc = Document()

        # Metadata section
        metadata = DocumentSection(section_type=SectionType.METADATA)
        metadata.add_paragraph(Paragraph(label=Label("Date:"), text="2024-01-01"))
        doc.add_section(metadata)

        # Transcript section
        transcript = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        transcript.add_paragraph(Paragraph(label=Label("Speaker:"), text="Hello."))
        doc.add_section(transcript)

        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        assert len(docx_doc.paragraphs) == 2

    def test_label_only_paragraph(self, tmp_path: Path) -> None:
        """Paragraph with only a label (no body text) formats correctly."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.TRANSCRIPT_LABEL)
        section.add_paragraph(Paragraph(label=Label("Transcript:"), text=""))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        # Should have one run with the label (bold)
        assert len(para.runs) == 1
        assert para.runs[0].bold is True

    def test_font_calibri_10pt(self, tmp_path: Path) -> None:
        """Body text uses Calibri 10pt font."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section.add_paragraph(Paragraph(text="Test text."))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        run = para.runs[0]
        assert run.font.name == "Calibri"
        assert run.font.size == Pt(10)

    def test_heading_level_uses_heading_style(self, tmp_path: Path) -> None:
        """Paragraph with heading_level uses Word heading styles."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_HEADER)
        section.add_paragraph(Paragraph(text="Section Title", heading_level=1))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "Heading 1"

    def test_heading_level_3_uses_heading3_style(self, tmp_path: Path) -> None:
        """Paragraph with heading_level=3 uses Heading 3 Word style."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_HEADER)
        section.add_paragraph(Paragraph(text="Sub-section Title", heading_level=3))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "Heading 3"

    def test_notes_header_without_heading_level_defaults_to_heading2(self, tmp_path: Path) -> None:
        """Notes header section without heading_level uses Heading 2 by default."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_HEADER)
        section.add_paragraph(Paragraph(text="Notes Header"))  # No heading_level set
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "Heading 2"

    def test_notes_body_non_bullet_paragraph(self, tmp_path: Path) -> None:
        """Notes body section with non-bullet paragraph formats as regular text."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_BODY)
        section.add_paragraph(Paragraph(text="Regular notes text.", is_bullet=False))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.text == "Regular notes text."
        # Non-bullet should use regular paragraph formatting, not list style

    def test_notes_body_bullet_default_level(self, tmp_path: Path) -> None:
        """Notes body bullet without bullet_level set uses List Bullet style."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_BODY)
        section.add_paragraph(Paragraph(text="Bullet item", is_bullet=True))  # No bullet_level set
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "List Bullet"

    def test_regular_paragraph_with_heading_level_uses_heading_style(self, tmp_path: Path) -> None:
        """Regular paragraph with heading_level > 0 uses heading style."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.REGULAR_PARAGRAPH)
        # A regular paragraph with a heading level should still use heading style
        section.add_paragraph(Paragraph(text="Section Header", heading_level=2))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "Heading 2"

    def test_unsupported_heading_level_defaults_to_heading2(self, tmp_path: Path) -> None:
        """Heading level outside of 1-3 range defaults to Heading 2."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_HEADER)
        # Use a heading level that isn't in the HEADING_STYLES mapping
        section.add_paragraph(Paragraph(text="Unknown Level Header", heading_level=5))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "Heading 2"

    def test_unsupported_bullet_level_defaults_to_list_bullet(self, tmp_path: Path) -> None:
        """Bullet level outside of 1-2 range defaults to List Bullet."""
        # Arrange
        doc = Document()
        section = DocumentSection(section_type=SectionType.NOTES_BODY)
        # Use a bullet level that isn't in the BULLET_STYLES mapping
        section.add_paragraph(Paragraph(text="Deep nested bullet", is_bullet=True, bullet_level=5))
        doc.add_section(section)
        output_path = tmp_path / "test.docx"

        # Act
        format_to_docx(doc, str(output_path))

        # Assert
        docx_doc = DocxDocument(str(output_path))  # type: ignore[no-untyped-call]
        para = docx_doc.paragraphs[0]
        assert para.style is not None
        assert para.style.name == "List Bullet"
