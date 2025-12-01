"""Tests for document reader module.

Tests the read_document function that parses existing DOCX/MD files
back into the Document model.
"""

from pathlib import Path

import pytest
from docx import Document as DocxDocument  # type: ignore[import-untyped]

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Paragraph,
    SectionType,
)
from transcript_etl_pipeline.document.reader import (
    _is_transcript_label,  # pyright: ignore[reportPrivateUsage]
    _looks_like_name,  # pyright: ignore[reportPrivateUsage]
    _parse_markdown_content,  # pyright: ignore[reportPrivateUsage]
    read_document,
)


class TestReadDocument:
    """Tests for read_document function."""

    def test_read_document_file_not_found(self) -> None:
        """read_document raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            read_document(Path("/nonexistent/file.md"))

    def test_read_document_unsupported_extension(self, tmp_path: Path) -> None:
        """read_document raises ValueError for unsupported extension."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")

        with pytest.raises(ValueError, match="Unsupported file extension"):
            read_document(txt_file)

    def test_read_document_markdown_file(self, tmp_path: Path) -> None:
        """read_document reads a Markdown file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Notes – 2025-01-01\n\n- First bullet\n")

        doc = read_document(md_file)

        assert isinstance(doc, Document)
        assert doc.has_notes()

    def test_read_document_docx_file(self, tmp_path: Path) -> None:
        """read_document reads a DOCX file."""
        docx_file = tmp_path / "test.docx"

        # Create a simple DOCX file
        docx_doc = DocxDocument()  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Notes – 2025-01-01")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("First bullet")  # type: ignore[no-untyped-call]
        docx_doc.save(str(docx_file))  # type: ignore[no-untyped-call]

        doc = read_document(docx_file)

        assert isinstance(doc, Document)
        assert len(doc.sections) > 0


class TestParseMarkdownContent:
    """Tests for Markdown content parsing."""

    def test_parse_markdown_empty_content(self) -> None:
        """Empty content returns empty document."""
        doc = _parse_markdown_content("")
        assert len(doc.sections) == 0

    def test_parse_markdown_notes_header_only(self) -> None:
        """Notes header alone creates a notes header section."""
        content = "# Notes – 2025-01-01"
        doc = _parse_markdown_content(content)

        assert len(doc.sections) == 1
        assert doc.sections[0].section_type == SectionType.NOTES_HEADER
        assert doc.sections[0].paragraphs[0].text == "Notes – 2025-01-01"

    def test_parse_markdown_notes_with_body(self) -> None:
        """Notes header with body creates both sections."""
        content = """# Notes – 2025-01-01

- First bullet
- Second bullet"""

        doc = _parse_markdown_content(content)

        assert len(doc.sections) == 2
        assert doc.sections[0].section_type == SectionType.NOTES_HEADER
        assert doc.sections[1].section_type == SectionType.NOTES_BODY
        assert len(doc.sections[1].paragraphs) == 2

    def test_parse_markdown_notes_bullets_detected(self) -> None:
        """Bullet points in notes are detected correctly."""
        content = """# Notes

- First bullet
* Second bullet
Regular text"""

        doc = _parse_markdown_content(content)

        body = doc.sections[1]
        assert body.paragraphs[0].is_bullet is True
        assert body.paragraphs[0].text == "First bullet"
        assert body.paragraphs[1].is_bullet is True
        assert body.paragraphs[1].text == "Second bullet"
        assert body.paragraphs[2].is_bullet is False
        assert body.paragraphs[2].text == "Regular text"

    def test_parse_markdown_transcript_label(self) -> None:
        """Transcript label creates transcript section."""
        content = "**Transcript:**"
        doc = _parse_markdown_content(content)

        assert len(doc.sections) == 1
        assert doc.sections[0].section_type == SectionType.TRANSCRIPT_LABEL

    def test_parse_markdown_transcript_with_content(self) -> None:
        """Transcript with speaker content."""
        content = """**Transcript:**

**John:** Hello there.
**Jane:** Hi John."""

        doc = _parse_markdown_content(content)

        # Should have transcript label + speaker sections
        assert doc.has_transcript()

    def test_parse_markdown_metadata_before_notes(self) -> None:
        """Content before notes header is treated as metadata."""
        content = """Meeting: Team Standup
Date: 2025-01-01

# Notes – 2025-01-01

Some notes."""

        doc = _parse_markdown_content(content)

        # First section should be metadata
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.has_notes()

    def test_parse_markdown_full_document(self) -> None:
        """Parse a complete document with metadata, notes, and transcript."""
        content = """Meeting: Team Standup
Date: 2025-01-01

# Notes – 2025-01-01

- Action item one
- Action item two

**Transcript:**

**Speaker A:** Hello everyone.
**Speaker B:** Good morning."""

        doc = _parse_markdown_content(content)

        assert doc.has_notes()
        assert doc.has_transcript()

        # Check section ordering
        section_types = [s.section_type for s in doc.sections]
        assert SectionType.METADATA in section_types
        assert SectionType.NOTES_HEADER in section_types
        assert SectionType.NOTES_BODY in section_types

    def test_parse_markdown_lowercase_notes_header(self) -> None:
        """Lowercase notes header is also recognized."""
        content = "# notes – 2025-01-01"
        doc = _parse_markdown_content(content)

        assert len(doc.sections) == 1
        assert doc.sections[0].section_type == SectionType.NOTES_HEADER

    def test_parse_markdown_plain_transcript_label(self) -> None:
        """Plain 'Transcript:' is recognized."""
        content = "Transcript:"
        doc = _parse_markdown_content(content)

        assert len(doc.sections) == 1
        assert doc.sections[0].section_type == SectionType.TRANSCRIPT_LABEL


class TestIsTranscriptLabel:
    """Tests for _is_transcript_label helper function."""

    def test_transcript_colon_only(self) -> None:
        """'Transcript:' is recognized."""
        assert _is_transcript_label("Transcript:") is True

    def test_transcript_bold_format(self) -> None:
        """'**Transcript:**' is recognized."""
        assert _is_transcript_label("**Transcript:**") is True

    def test_transcript_with_space(self) -> None:
        """'**Transcript:** ' with trailing content is recognized."""
        assert _is_transcript_label("**Transcript:** Some text") is True

    def test_not_transcript(self) -> None:
        """Regular text is not recognized as transcript label."""
        assert _is_transcript_label("Hello there") is False

    def test_partial_match(self) -> None:
        """Partial 'Transcript' without colon is not recognized."""
        assert _is_transcript_label("Transcript") is False


class TestLooksLikeName:
    """Tests for _looks_like_name helper function."""

    def test_simple_name(self) -> None:
        """Simple capitalized name is recognized."""
        assert _looks_like_name("John") is True

    def test_full_name(self) -> None:
        """Full name with spaces is recognized."""
        assert _looks_like_name("Dan Moisan") is True

    def test_speaker_label(self) -> None:
        """'Speaker A' pattern is recognized."""
        assert _looks_like_name("Speaker A") is True
        assert _looks_like_name("Speaker B") is True

    def test_lowercase_not_name(self) -> None:
        """Lowercase word is not recognized as name."""
        assert _looks_like_name("hello") is False

    def test_empty_not_name(self) -> None:
        """Empty string is not a name."""
        assert _looks_like_name("") is False


class TestDocxReader:
    """Tests for DOCX file reading."""

    def test_read_docx_notes_section(self, tmp_path: Path) -> None:
        """DOCX with notes header is parsed correctly."""
        docx_file = tmp_path / "test.docx"

        docx_doc = DocxDocument()  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Notes – 2025-01-01")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("First note content")  # type: ignore[no-untyped-call]
        docx_doc.save(str(docx_file))  # type: ignore[no-untyped-call]

        doc = read_document(docx_file)

        assert doc.has_notes()
        # Should have notes header and notes body
        section_types = [s.section_type for s in doc.sections]
        assert SectionType.NOTES_HEADER in section_types
        assert SectionType.NOTES_BODY in section_types

    def test_read_docx_transcript_section(self, tmp_path: Path) -> None:
        """DOCX with transcript is parsed correctly."""
        docx_file = tmp_path / "test.docx"

        docx_doc = DocxDocument()  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Transcript:")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Speaker A: Hello.")  # type: ignore[no-untyped-call]
        docx_doc.save(str(docx_file))  # type: ignore[no-untyped-call]

        doc = read_document(docx_file)

        assert doc.has_transcript()

    def test_read_docx_metadata_section(self, tmp_path: Path) -> None:
        """DOCX with metadata before notes is parsed correctly."""
        docx_file = tmp_path / "test.docx"

        docx_doc = DocxDocument()  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Meeting: Team Standup")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Notes – 2025-01-01")  # type: ignore[no-untyped-call]
        docx_doc.save(str(docx_file))  # type: ignore[no-untyped-call]

        doc = read_document(docx_file)

        section_types = [s.section_type for s in doc.sections]
        assert SectionType.METADATA in section_types
        assert SectionType.NOTES_HEADER in section_types

    def test_read_docx_full_document(self, tmp_path: Path) -> None:
        """DOCX with all sections is parsed correctly."""
        docx_file = tmp_path / "test.docx"

        docx_doc = DocxDocument()  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Meeting: Team Standup")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Notes – 2025-01-01")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("- Action item one")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Transcript:")  # type: ignore[no-untyped-call]
        docx_doc.add_paragraph("Speaker A: Hello.")  # type: ignore[no-untyped-call]
        docx_doc.save(str(docx_file))  # type: ignore[no-untyped-call]

        doc = read_document(docx_file)

        assert doc.has_notes()
        assert doc.has_transcript()


class TestRoundTrip:
    """Tests for round-trip (write then read) scenarios."""

    def test_roundtrip_notes_sections_preserved(self, tmp_path: Path) -> None:
        """Notes sections survive a write-then-read cycle."""
        # Create original document
        original = Document()
        original.add_section(
            DocumentSection(
                section_type=SectionType.NOTES_HEADER,
                paragraphs=[Paragraph(text="Notes – 2025-01-01")],
            )
        )
        original.add_section(
            DocumentSection(
                section_type=SectionType.NOTES_BODY,
                paragraphs=[
                    Paragraph(text="First bullet", is_bullet=True),
                    Paragraph(text="Second bullet", is_bullet=True),
                ],
            )
        )

        # Write to Markdown (simulate)
        md_file = tmp_path / "test.md"
        md_content = """# Notes – 2025-01-01

- First bullet
- Second bullet"""
        md_file.write_text(md_content)

        # Read back
        restored = read_document(md_file)

        assert restored.has_notes()
        section_types = [s.section_type for s in restored.sections]
        assert SectionType.NOTES_HEADER in section_types
        assert SectionType.NOTES_BODY in section_types

    def test_roundtrip_transcript_sections_preserved(self, tmp_path: Path) -> None:
        """Transcript sections survive a write-then-read cycle."""
        md_file = tmp_path / "test.md"
        md_content = """**Transcript:**

**Speaker A:** Hello everyone.
**Speaker B:** Good morning."""
        md_file.write_text(md_content)

        restored = read_document(md_file)

        assert restored.has_transcript()
