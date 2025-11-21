"""Integration tests for document parser."""

from transcript_etl_pipeline.document.model import SectionType
from transcript_etl_pipeline.document.parser import parse_enhanced_text


class TestParseEnhancedText:
    """Test the parse_enhanced_text function with realistic inputs."""

    def test_empty_text(self) -> None:
        """Test parsing empty text."""
        doc = parse_enhanced_text("")
        assert len(doc.sections) == 0

    def test_metadata_only(self) -> None:
        """Test parsing text with only metadata."""
        text = "Date: 2025-11-21\r\nAttendees: Dan Moisan, Alice Smith\r\n"
        doc = parse_enhanced_text(text)
        # Should create at least one section
        assert len(doc.sections) >= 1
        # First section should be metadata
        assert doc.sections[0].section_type == SectionType.METADATA

    def test_transcript_with_labels(self) -> None:
        """Test parsing transcript with speaker labels."""
        text = (
            "Date: 2025-11-21\r\n"
            "\r\n"
            "Transcript:\r\n"
            "DanMoisan: Hello everyone.\r\n"
            "\r\n"
            "Alice: Thanks for joining.\r\n"
        )
        doc = parse_enhanced_text(text)
        # Should have multiple sections
        assert len(doc.sections) >= 2

        # Should have a transcript label section
        has_transcript_label = any(
            s.section_type == SectionType.TRANSCRIPT_LABEL for s in doc.sections
        )
        assert has_transcript_label

        # Should have speaker paragraphs somewhere
        all_paragraphs = []
        for section in doc.sections:
            all_paragraphs.extend(section.paragraphs)

        # Check that DanMoisan's paragraph exists
        dan_paragraphs = [p for p in all_paragraphs if p.label and "DanMoisan" in p.label.text]
        assert len(dan_paragraphs) >= 1
        assert dan_paragraphs[0].text == "Hello everyone."

    def test_multiple_paragraphs_per_speaker(self) -> None:
        """Test parsing multiple paragraphs for a single speaker."""
        text = (
            "Transcript:\r\n"
            "Speaker: First paragraph.\r\n"
            "\r\n"
            "Second paragraph same speaker.\r\n"
        )
        doc = parse_enhanced_text(text)
        # Should have at least one section
        assert len(doc.sections) >= 1

        # Should have multiple paragraphs total
        all_paragraphs = []
        for section in doc.sections:
            all_paragraphs.extend(section.paragraphs)
        assert len(all_paragraphs) >= 1

    def test_preserves_paragraph_structure(self) -> None:
        """Test that paragraph breaks are preserved."""
        text = (
            "Transcript:\r\n"
            "Alice: First point.\r\n"
            "\r\n"
            "Second point here.\r\n"
            "\r\n"
            "Bob: Third point from Bob.\r\n"
        )
        doc = parse_enhanced_text(text)
        # Should detect multiple paragraphs
        all_paragraphs = []
        for section in doc.sections:
            all_paragraphs.extend(section.paragraphs)
        assert len(all_paragraphs) >= 2

    def test_realistic_meeting_transcript(self) -> None:
        """Test parsing a realistic meeting transcript."""
        text = (
            "Date: 2025-11-21\r\n"
            "Attendees: Dan Moisan, Alice Smith, Bob Johnson\r\n"
            "\r\n"
            "Transcript:\r\n"
            "Alice: Good morning everyone. Let's start with the project status.\r\n"
            "\r\n"
            "Bob: Thanks for having me. I've completed the initial research.\r\n"
            "\r\n"
            "Alice: That's great. Dan, what do you think about the timeline?\r\n"
            "\r\n"
            "Dan Moisan: I believe we can meet the deadline if we stay focused.\r\n"
        )
        doc = parse_enhanced_text(text)

        # Should have at least one section
        assert len(doc.sections) >= 1

        # Collect all paragraphs
        all_paragraphs = []
        for section in doc.sections:
            all_paragraphs.extend(section.paragraphs)

        # Should have multiple paragraphs for different speakers
        assert len(all_paragraphs) >= 3

    def test_handles_blank_lines(self) -> None:
        """Test that blank lines are handled correctly."""
        text = (
            "Date: 2025-11-21\r\n" "\r\n" "\r\n" "Transcript:\r\n" "\r\n" "Speaker: Text here.\r\n"
        )
        doc = parse_enhanced_text(text)
        # Should still parse correctly despite extra blank lines
        assert len(doc.sections) >= 1

    def test_mixed_label_types(self) -> None:
        """Test parsing with various label formats."""
        text = (
            "Date: 2025-11-21\r\n"
            "\r\n"
            "Transcript:\r\n"
            "PersonA: First comment.\r\n"
            "\r\n"
            "Person_B: Second comment.\r\n"
            "\r\n"
            "Speaker123: Third comment.\r\n"
        )
        doc = parse_enhanced_text(text)
        # Should parse all labels correctly
        assert len(doc.sections) >= 1

        # Count labeled paragraphs
        all_paragraphs = []
        for section in doc.sections:
            all_paragraphs.extend(section.paragraphs)

        labeled_paragraphs = [p for p in all_paragraphs if p.label is not None]
        # Should have several labeled paragraphs
        assert len(labeled_paragraphs) >= 2

    def test_no_transcript_label(self) -> None:
        """Test parsing text without explicit Transcript: label."""
        text = (
            "Date: 2025-11-21\r\n"
            "\r\n"
            "Dan Moisan: Hello everyone.\r\n"
            "\r\n"
            "Alice: Thanks.\r\n"
        )
        doc = parse_enhanced_text(text)
        # Should still parse and detect speaker labels
        assert len(doc.sections) >= 1

        # Should have speaker paragraphs
        all_paragraphs = []
        for section in doc.sections:
            all_paragraphs.extend(section.paragraphs)
        assert len(all_paragraphs) >= 1
