"""Tests for document model structures."""

import pytest

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)


class TestLabel:
    """Tests for Label class."""

    def test_valid_label_creation(self) -> None:
        """Test creating a valid label."""
        label = Label(text="John:", is_speaker=True)
        assert label.text == "John:"
        assert label.is_speaker is True

    def test_label_must_end_with_colon(self) -> None:
        """Test that label without colon raises error."""
        with pytest.raises(ValueError, match="must end with colon"):
            Label(text="John")

    def test_label_cannot_be_empty(self) -> None:
        """Test that empty label raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Label(text=":")

    def test_label_with_whitespace(self) -> None:
        """Test that label with only whitespace before colon raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Label(text="  :")


class TestParagraph:
    """Tests for Paragraph class."""

    def test_paragraph_with_label_and_text(self) -> None:
        """Test paragraph containing both label and text."""
        label = Label(text="Speaker:", is_speaker=True)
        para = Paragraph(label=label, text="Hello world")
        assert para.full_text() == "Speaker: Hello world"
        assert para.has_speaker_label() is True

    def test_paragraph_with_only_text(self) -> None:
        """Test paragraph with no label."""
        para = Paragraph(text="Just some text")
        assert para.full_text() == "Just some text"
        assert para.has_speaker_label() is False

    def test_paragraph_empty(self) -> None:
        """Test empty paragraph."""
        para = Paragraph()
        assert para.full_text() == ""
        assert para.has_speaker_label() is False

    def test_paragraph_with_non_speaker_label(self) -> None:
        """Test paragraph with non-speaker label."""
        label = Label(text="Note:", is_speaker=False)
        para = Paragraph(label=label, text="This is a note")
        assert para.full_text() == "Note: This is a note"
        assert para.has_speaker_label() is False

    def test_paragraph_section_type_default(self) -> None:
        """Test paragraph has default section type."""
        para = Paragraph(text="Text")
        assert para.section_type == SectionType.REGULAR_PARAGRAPH


class TestDocumentSection:
    """Tests for DocumentSection class."""

    def test_create_empty_section(self) -> None:
        """Test creating an empty document section."""
        section = DocumentSection(section_type=SectionType.METADATA)
        assert section.section_type == SectionType.METADATA
        assert len(section.paragraphs) == 0

    def test_add_paragraph_to_section(self) -> None:
        """Test adding paragraphs to a section."""
        section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        para1 = Paragraph(text="First paragraph")
        para2 = Paragraph(text="Second paragraph")

        section.add_paragraph(para1)
        section.add_paragraph(para2)

        assert len(section.paragraphs) == 2
        assert section.paragraphs[0] is para1
        assert section.paragraphs[1] is para2


class TestDocument:
    """Tests for Document class."""

    def test_create_empty_document(self) -> None:
        """Test creating an empty document."""
        doc = Document()
        assert len(doc.sections) == 0
        assert doc.title == ""
        assert doc.date == ""

    def test_add_section_to_document(self) -> None:
        """Test adding sections to document."""
        doc = Document(title="Meeting Notes", date="2024-01-01")
        metadata_section = DocumentSection(section_type=SectionType.METADATA)
        content_section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)

        doc.add_section(metadata_section)
        doc.add_section(content_section)

        assert len(doc.sections) == 2
        assert doc.title == "Meeting Notes"
        assert doc.date == "2024-01-01"

    def test_get_metadata_section(self) -> None:
        """Test retrieving the metadata section."""
        doc = Document()
        metadata = DocumentSection(section_type=SectionType.METADATA)
        content = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)

        doc.add_section(metadata)
        doc.add_section(content)

        retrieved = doc.get_metadata_section()
        assert retrieved is metadata

    def test_get_metadata_section_when_none(self) -> None:
        """Test getting metadata section when it doesn't exist."""
        doc = Document()
        content = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        doc.add_section(content)

        assert doc.get_metadata_section() is None

    def test_all_paragraphs(self) -> None:
        """Test getting all paragraphs from all sections."""
        doc = Document()

        section1 = DocumentSection(section_type=SectionType.METADATA)
        section1.add_paragraph(Paragraph(text="Meta 1"))
        section1.add_paragraph(Paragraph(text="Meta 2"))

        section2 = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
        section2.add_paragraph(Paragraph(text="Content 1"))

        doc.add_section(section1)
        doc.add_section(section2)

        all_paras = doc.all_paragraphs()
        assert len(all_paras) == 3
        assert all_paras[0].text == "Meta 1"
        assert all_paras[1].text == "Meta 2"
        assert all_paras[2].text == "Content 1"
