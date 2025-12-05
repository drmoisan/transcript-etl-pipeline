"""Unit tests for document parser helpers."""

from transcript_etl_pipeline.document.model import Label, SectionType
from transcript_etl_pipeline.document.parser import (
    extract_label,  # pyright: ignore[reportPrivateUsage]
    is_metadata_label,  # pyright: ignore[reportPrivateUsage]
    parse_enhanced_text,
)


class TestParseEnhancedTextUnit:
    """Focused tests for parse_enhanced_text behavior."""

    def test_metadata_section_collects_labeled_lines(self) -> None:
        """Ensure metadata lines become individual paragraphs with labels."""
        text = "Date: 2025-11-29\r\nAttendees: Alice Smith, Bob Lee\r\n"

        doc = parse_enhanced_text(text)

        assert len(doc.sections) == 1
        metadata_section = doc.sections[0]
        assert metadata_section.section_type == SectionType.METADATA
        labels = [
            paragraph.label.text for paragraph in metadata_section.paragraphs if paragraph.label
        ]
        texts = [paragraph.text for paragraph in metadata_section.paragraphs]
        assert labels == ["Date:", "Attendees:"]
        assert texts == ["2025-11-29", "Alice Smith, Bob Lee"]

    def test_transcript_label_paragraph_contains_full_body(self) -> None:
        """Ensure transcript paragraph combines subsequent lines into a single block."""
        text = (
            "Date: 2025-11-29\r\n"
            "\r\n"
            "Transcript:\r\n"
            "Speaker A: Opening remarks.\r\n"
            "Speaker B: Follow-up note.\r\n"
        )

        doc = parse_enhanced_text(text)

        assert len(doc.sections) == 2
        transcript_section = doc.sections[1]
        assert transcript_section.section_type == SectionType.TRANSCRIPT_LABEL
        assert len(transcript_section.paragraphs) == 1
        paragraph = transcript_section.paragraphs[0]
        assert paragraph.label and paragraph.label.text == "Transcript:"
        assert paragraph.text == "Speaker A: Opening remarks. Speaker B: Follow-up note."

    def test_blank_lines_split_sections_without_empty_paragraphs(self) -> None:
        """Ensure blank lines trigger new sections while avoiding empty paragraphs."""
        text = "Transcript:\r\n" "Speaker A: First.\r\n" "\r\n" "Speaker B: Second.\r\n" "\r\n"

        doc = parse_enhanced_text(text)

        assert [section.section_type for section in doc.sections] == [
            SectionType.TRANSCRIPT_LABEL,
            SectionType.SPEAKER_PARAGRAPH,
        ]

        first_section_texts = [paragraph.text for paragraph in doc.sections[0].paragraphs]
        second_section_texts = [paragraph.text for paragraph in doc.sections[1].paragraphs]
        assert first_section_texts == ["Speaker A: First."]
        assert second_section_texts == ["Speaker B: Second."]

    def test_metadata_section_not_added_when_empty(self) -> None:
        """Ensure empty metadata sections are not persisted when text starts with a label."""
        text = "Transcript:\r\n" "Discussion points with no metadata\r\n"

        doc = parse_enhanced_text(text)

        assert len(doc.sections) == 1
        transcript_section = doc.sections[0]
        assert transcript_section.section_type == SectionType.TRANSCRIPT_LABEL
        assert [paragraph.text for paragraph in transcript_section.paragraphs] == [
            "Discussion points with no metadata"
        ]

    def test_unlabeled_metadata_lines_are_preserved(self) -> None:
        """Ensure metadata paragraphs without labels remain in the metadata section."""
        text = (
            "Planning call for release\r\n"
            "Date: 2025-09-30\r\n"
            "Time: 10:00 AM\r\n"
            "Transcript:\r\n"
            "Agenda review\r\n"
        )

        doc = parse_enhanced_text(text)

        assert len(doc.sections) == 2
        metadata_section = doc.sections[0]
        assert metadata_section.section_type == SectionType.METADATA
        assert [paragraph.text for paragraph in metadata_section.paragraphs] == [
            "Planning call for release",
            "2025-09-30",
            "10:00 AM",
        ]
        assert metadata_section.paragraphs[0].label is None

    def test_speaker_labels_collect_inline_text_and_continuations(self) -> None:
        """Ensure labeled speaker paragraphs capture inline and subsequent lines."""
        text = (
            "Date: 2025-09-30\r\n"
            "Transcript:\r\n"
            "SpeakerA: Hello there\r\n"
            "Still speaking\r\n"
            "SpeakerB: New item\r\n"
            "Another detail\r\n"
        )

        doc = parse_enhanced_text(text)

        assert len(doc.sections) == 3
        speaker_section = doc.sections[2]
        assert speaker_section.section_type == SectionType.SPEAKER_PARAGRAPH
        assert [
            paragraph.label.text if paragraph.label else None
            for paragraph in speaker_section.paragraphs
        ] == [
            "SpeakerA:",
            "SpeakerB:",
        ]
        assert [paragraph.text for paragraph in speaker_section.paragraphs] == [
            "Hello there Still speaking",
            "New item Another detail",
        ]


class TestParserHelpers:
    """Tests for internal parser helper functions."""

    def test_extract_label_detects_capitalized_tokens(self) -> None:
        """Ensure _extract_label captures labels that follow normalization rules."""
        label = extract_label("SpeakerA: Hello")
        assert isinstance(label, Label)
        assert label.text == "SpeakerA:"

    def test_extract_label_rejects_invalid_tokens(self) -> None:
        """Ensure _extract_label returns None for non-label lines."""
        assert extract_label("not a label: value") is None
        assert extract_label("speaker: lowercase start") is None

    def test_extract_label_ignores_leading_whitespace(self) -> None:
        """Ensure _extract_label rejects labels that do not start at column zero."""
        assert extract_label("  SpeakerA: Hello") is None

    def test_is_metadata_label_matches_known_labels(self) -> None:
        """Ensure metadata labels are recognized case-insensitively."""
        assert is_metadata_label("attendees:") is True
        assert is_metadata_label("DATE:") is True
        assert is_metadata_label("Transcript:") is False

    def test_is_metadata_label_handles_meeting_title_entry(self) -> None:
        """Ensure metadata label list supports the meeting title entry without a colon."""
        assert is_metadata_label("Meeting Title") is True
        assert is_metadata_label("Unknown:") is False

    def test_extract_label_empty_line_returns_none(self) -> None:
        """Ensure extract_label returns None for an empty line."""
        assert extract_label("") is None

    def test_extract_label_whitespace_only_returns_none(self) -> None:
        """Ensure extract_label returns None for whitespace-only line."""
        # Empty string case
        assert extract_label("") is None


class TestParserSpeakerParagraphTransition:
    """Tests for parser behavior when transitioning from metadata to speaker sections."""

    def test_non_transcript_label_in_metadata_creates_speaker_section(self) -> None:
        """Non-metadata label creates SPEAKER_PARAGRAPH section."""
        # This tests line 57: current_section_type = SectionType.SPEAKER_PARAGRAPH
        text = "Date: 2025-11-29\r\n" "CustomSpeaker: Hello everyone.\r\n"

        doc = parse_enhanced_text(text)

        # Should have 2 sections: metadata and speaker paragraph
        assert len(doc.sections) == 2
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.sections[1].section_type == SectionType.SPEAKER_PARAGRAPH

        # Verify the speaker paragraph content
        speaker_section = doc.sections[1]
        assert len(speaker_section.paragraphs) == 1
        assert speaker_section.paragraphs[0].label is not None
        assert speaker_section.paragraphs[0].label.text == "CustomSpeaker:"
        assert speaker_section.paragraphs[0].text == "Hello everyone."

    def test_speaker_label_directly_after_metadata(self) -> None:
        """Non-transcript label transitions metadata to speaker section."""
        text = "Date: 2025-01-01\r\n" "Time: 10:00 AM\r\n" "JohnDoe: Starting the discussion.\r\n"

        doc = parse_enhanced_text(text)

        # First section should be metadata with Date and Time
        assert doc.sections[0].section_type == SectionType.METADATA
        assert len(doc.sections[0].paragraphs) == 2

        # Second section should be speaker paragraph
        assert doc.sections[1].section_type == SectionType.SPEAKER_PARAGRAPH
        assert doc.sections[1].paragraphs[0].label is not None
        assert doc.sections[1].paragraphs[0].label.text == "JohnDoe:"

    def test_multiple_speaker_labels_without_transcript(self) -> None:
        """Multiple non-metadata labels create speaker paragraphs."""
        text = "Date: 2025-01-01\r\n" "Alice: Good morning.\r\n" "Bob: Good morning to you too.\r\n"

        doc = parse_enhanced_text(text)

        # Should have 2 sections: metadata and speaker paragraph
        assert len(doc.sections) == 2
        assert doc.sections[0].section_type == SectionType.METADATA
        assert doc.sections[1].section_type == SectionType.SPEAKER_PARAGRAPH

        # Speaker section should contain both speakers
        speaker_section = doc.sections[1]
        labels = [p.label.text if p.label else None for p in speaker_section.paragraphs]
        assert labels == ["Alice:", "Bob:"]
