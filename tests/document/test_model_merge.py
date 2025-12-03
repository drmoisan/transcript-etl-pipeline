"""Tests for Document merge functionality.

Tests the merge_notes and merge_transcript methods that support
adding or replacing notes/transcript sections in existing documents.
"""

import pytest

from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Paragraph,
    SectionType,
)


class TestDocumentMergeNotes:
    """Tests for Document.merge_notes() method."""

    def test_merge_notes_add_to_empty_document(self) -> None:
        """Adding notes to an empty document places them at the start."""
        doc = Document()
        notes_header = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Notes – 2025-01-01")],
        )
        notes_body = DocumentSection(
            section_type=SectionType.NOTES_BODY,
            paragraphs=[Paragraph(text="First note", is_bullet=True)],
        )

        doc.merge_notes([notes_header, notes_body], mode="add")

        assert len(doc.sections) == 2
        assert doc.sections[0].section_type == SectionType.NOTES_HEADER
        assert doc.sections[1].section_type == SectionType.NOTES_BODY

    def test_merge_notes_add_inserts_after_metadata(self) -> None:
        """Adding notes inserts them after metadata section."""
        doc = Document()
        metadata = DocumentSection(
            section_type=SectionType.METADATA,
            paragraphs=[Paragraph(text="Meeting info")],
        )
        doc.add_section(metadata)

        notes_header = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Notes – 2025-01-01")],
        )

        doc.merge_notes([notes_header], mode="add")

        assert len(doc.sections) == 2
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.sections[1].section_type == SectionType.NOTES_HEADER

    def test_merge_notes_add_inserts_before_existing_notes(self) -> None:
        """Adding notes places new notes above existing notes (at top of notes)."""
        doc = Document()
        # Add existing notes
        old_header = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Old Notes – 2025-01-01")],
        )
        old_body = DocumentSection(
            section_type=SectionType.NOTES_BODY,
            paragraphs=[Paragraph(text="Old note content")],
        )
        doc.add_section(old_header)
        doc.add_section(old_body)

        # Add new notes
        new_header = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="New Notes – 2025-01-02")],
        )
        new_body = DocumentSection(
            section_type=SectionType.NOTES_BODY,
            paragraphs=[Paragraph(text="New note content")],
        )

        doc.merge_notes([new_header, new_body], mode="add")

        assert len(doc.sections) == 4
        # New notes should be at the top
        assert doc.sections[0].section_type == SectionType.NOTES_HEADER
        assert doc.sections[0].paragraphs[0].text == "New Notes – 2025-01-02"
        assert doc.sections[1].section_type == SectionType.NOTES_BODY
        assert doc.sections[1].paragraphs[0].text == "New note content"
        # Old notes follow
        assert doc.sections[2].section_type == SectionType.NOTES_HEADER
        assert doc.sections[2].paragraphs[0].text == "Old Notes – 2025-01-01"

    def test_merge_notes_add_with_metadata_and_existing_notes(self) -> None:
        """Adding notes after metadata but before existing notes."""
        doc = Document()
        metadata = DocumentSection(
            section_type=SectionType.METADATA,
            paragraphs=[Paragraph(text="Meeting info")],
        )
        old_notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Old Notes")],
        )
        doc.add_section(metadata)
        doc.add_section(old_notes)

        new_notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="New Notes")],
        )

        doc.merge_notes([new_notes], mode="add")

        assert len(doc.sections) == 3
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.sections[1].paragraphs[0].text == "New Notes"
        assert doc.sections[2].paragraphs[0].text == "Old Notes"

    def test_merge_notes_replace_removes_existing_notes(self) -> None:
        """Replace mode removes all existing notes before adding new ones."""
        doc = Document()
        old_header = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Old Notes")],
        )
        old_body = DocumentSection(
            section_type=SectionType.NOTES_BODY,
            paragraphs=[Paragraph(text="Old content")],
        )
        doc.add_section(old_header)
        doc.add_section(old_body)

        new_header = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="New Notes")],
        )

        doc.merge_notes([new_header], mode="replace")

        assert len(doc.sections) == 1
        assert doc.sections[0].paragraphs[0].text == "New Notes"

    def test_merge_notes_replace_preserves_metadata_and_transcript(self) -> None:
        """Replace mode only removes notes, not metadata or transcript."""
        doc = Document()
        metadata = DocumentSection(
            section_type=SectionType.METADATA,
            paragraphs=[Paragraph(text="Meeting info")],
        )
        old_notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Old Notes")],
        )
        transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Transcript content")],
        )
        doc.add_section(metadata)
        doc.add_section(old_notes)
        doc.add_section(transcript)

        new_notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="New Notes")],
        )

        doc.merge_notes([new_notes], mode="replace")

        assert len(doc.sections) == 3
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.sections[1].section_type == SectionType.NOTES_HEADER
        assert doc.sections[1].paragraphs[0].text == "New Notes"
        assert doc.sections[2].section_type == SectionType.TRANSCRIPT_LABEL

    def test_merge_notes_invalid_mode_raises_error(self) -> None:
        """Invalid mode raises ValueError."""
        doc = Document()
        notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Notes")],
        )

        with pytest.raises(ValueError, match="Invalid mode"):
            doc.merge_notes([notes], mode="invalid")


class TestDocumentMergeTranscript:
    """Tests for Document.merge_transcript() method."""

    def test_merge_transcript_add_to_empty_document(self) -> None:
        """Adding transcript to an empty document appends it."""
        doc = Document()
        transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Transcript content")],
        )

        doc.merge_transcript([transcript], mode="add")

        assert len(doc.sections) == 1
        assert doc.sections[0].section_type == SectionType.TRANSCRIPT_LABEL

    def test_merge_transcript_add_appends_at_end(self) -> None:
        """Adding transcript appends after existing content."""
        doc = Document()
        metadata = DocumentSection(
            section_type=SectionType.METADATA,
            paragraphs=[Paragraph(text="Meeting info")],
        )
        notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Notes")],
        )
        doc.add_section(metadata)
        doc.add_section(notes)

        transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Transcript")],
        )

        doc.merge_transcript([transcript], mode="add")

        assert len(doc.sections) == 3
        assert doc.sections[2].section_type == SectionType.TRANSCRIPT_LABEL

    def test_merge_transcript_add_appends_to_existing_transcript(self) -> None:
        """Adding transcript appends new sections after existing transcript."""
        doc = Document()
        old_transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Part 1")],
        )
        doc.add_section(old_transcript)

        new_transcript = DocumentSection(
            section_type=SectionType.SPEAKER_PARAGRAPH,
            paragraphs=[Paragraph(text="Part 2")],
        )

        doc.merge_transcript([new_transcript], mode="add")

        assert len(doc.sections) == 2
        assert doc.sections[0].paragraphs[0].text == "Part 1"
        assert doc.sections[1].paragraphs[0].text == "Part 2"

    def test_merge_transcript_replace_removes_existing_transcript(self) -> None:
        """Replace mode removes all existing transcript sections."""
        doc = Document()
        old_label = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Old Transcript")],
        )
        old_speaker = DocumentSection(
            section_type=SectionType.SPEAKER_PARAGRAPH,
            paragraphs=[Paragraph(text="Old speaker text")],
        )
        old_regular = DocumentSection(
            section_type=SectionType.REGULAR_PARAGRAPH,
            paragraphs=[Paragraph(text="Old regular text")],
        )
        doc.add_section(old_label)
        doc.add_section(old_speaker)
        doc.add_section(old_regular)

        new_transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="New Transcript")],
        )

        doc.merge_transcript([new_transcript], mode="replace")

        assert len(doc.sections) == 1
        assert doc.sections[0].paragraphs[0].text == "New Transcript"

    def test_merge_transcript_replace_preserves_metadata_and_notes(self) -> None:
        """Replace mode only removes transcript, not metadata or notes."""
        doc = Document()
        metadata = DocumentSection(
            section_type=SectionType.METADATA,
            paragraphs=[Paragraph(text="Meeting info")],
        )
        notes = DocumentSection(
            section_type=SectionType.NOTES_HEADER,
            paragraphs=[Paragraph(text="Notes")],
        )
        old_transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Old Transcript")],
        )
        doc.add_section(metadata)
        doc.add_section(notes)
        doc.add_section(old_transcript)

        new_transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="New Transcript")],
        )

        doc.merge_transcript([new_transcript], mode="replace")

        assert len(doc.sections) == 3
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.sections[1].section_type == SectionType.NOTES_HEADER
        assert doc.sections[2].section_type == SectionType.TRANSCRIPT_LABEL
        assert doc.sections[2].paragraphs[0].text == "New Transcript"

    def test_merge_transcript_invalid_mode_raises_error(self) -> None:
        """Invalid mode raises ValueError."""
        doc = Document()
        transcript = DocumentSection(
            section_type=SectionType.TRANSCRIPT_LABEL,
            paragraphs=[Paragraph(text="Transcript")],
        )

        with pytest.raises(ValueError, match="Invalid mode"):
            doc.merge_transcript([transcript], mode="invalid")


class TestDocumentHelpers:
    """Tests for Document helper methods."""

    def test_has_notes_returns_true_when_notes_exist(self) -> None:
        """has_notes returns True when notes sections are present."""
        doc = Document()
        doc.add_section(
            DocumentSection(
                section_type=SectionType.NOTES_HEADER,
                paragraphs=[Paragraph(text="Notes")],
            )
        )

        assert doc.has_notes() is True

    def test_has_notes_returns_false_when_no_notes(self) -> None:
        """has_notes returns False when no notes sections are present."""
        doc = Document()
        doc.add_section(
            DocumentSection(
                section_type=SectionType.METADATA,
                paragraphs=[Paragraph(text="Metadata")],
            )
        )

        assert doc.has_notes() is False

    def test_has_transcript_returns_true_when_transcript_exists(self) -> None:
        """has_transcript returns True when transcript sections are present."""
        doc = Document()
        doc.add_section(
            DocumentSection(
                section_type=SectionType.TRANSCRIPT_LABEL,
                paragraphs=[Paragraph(text="Transcript")],
            )
        )

        assert doc.has_transcript() is True

    def test_has_transcript_returns_false_when_no_transcript(self) -> None:
        """has_transcript returns False when no transcript sections are present."""
        doc = Document()
        doc.add_section(
            DocumentSection(
                section_type=SectionType.NOTES_HEADER,
                paragraphs=[Paragraph(text="Notes")],
            )
        )

        assert doc.has_transcript() is False

    def test_is_bullet_field_on_paragraph(self) -> None:
        """Paragraph.is_bullet field works correctly."""
        bullet_para = Paragraph(text="Bullet point", is_bullet=True)
        regular_para = Paragraph(text="Regular paragraph", is_bullet=False)
        default_para = Paragraph(text="Default paragraph")

        assert bullet_para.is_bullet is True
        assert regular_para.is_bullet is False
        assert default_para.is_bullet is False


class TestSectionTypeEnumExtensions:
    """Tests for new SectionType enum values."""

    def test_notes_header_section_type_exists(self) -> None:
        """NOTES_HEADER section type is defined."""
        assert SectionType.NOTES_HEADER.value == "notes_header"

    def test_notes_body_section_type_exists(self) -> None:
        """NOTES_BODY section type is defined."""
        assert SectionType.NOTES_BODY.value == "notes_body"
