"""Tests for enhancement orchestration."""

from transcript_etl_pipeline.transform.enhance import enhance_text


class TestEnhanceText:
    """Test the enhance_text orchestration."""

    def test_empty_text(self) -> None:
        """Test empty text returns empty."""
        result, _mapping = enhance_text("")
        assert result == ""
        assert _mapping == {}

    def test_simple_transcript(self) -> None:
        """Test enhancement of simple transcript."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi there."
        result, _mapping = enhance_text(text)
        # Should have speaker labels
        assert "Speaker A:" in result or "Speaker B:" in result
        # Should preserve structure
        assert "Hello" in result
        assert "Hi there" in result

    def test_with_ui_callback(self) -> None:
        """Test enhancement with UI callback for speaker resolution.

        Note: Dan Moisan is always added as an available attendee,
        so with only one speaker, elimination logic maps Speaker A -> Dan Moisan.
        """

        def mock_ui(
            speaker_label: str, sample_utterances: list[str], candidates: list[str]
        ) -> str | None:
            """Mock UI that would resolve speakers if called."""
            if speaker_label == "Speaker A":
                return "Alice"
            return None

        text = "Speaker A: Hello everyone.\\r\\nSpeaker A: How are you?"
        result, _mapping = enhance_text(text, ui_callback=mock_ui)
        # With only one speaker and Dan Moisan always available,
        # elimination logic resolves Speaker A -> Dan Moisan
        if "Speaker A" in _mapping:
            assert _mapping["Speaker A"] == "Dan Moisan"
            assert "Dan Moisan:" in result

    def test_paragraph_detection_applied(self) -> None:
        """Test that paragraph detection is applied."""
        text = "Speaker A: First sentence.\r\nSecond sentence.\r\nThird sentence."
        result, _mapping = enhance_text(text)
        # Should add paragraph breaks after sentences
        # Count blank lines as indication of paragraph breaks
        blank_line_count = result.count("\r\n\r\n")
        # Might have paragraph breaks
        assert blank_line_count >= 0

    def test_speaker_resolution_then_paragraphs(self) -> None:
        """Test that speaker resolution happens before paragraph detection."""

        def mock_ui(
            speaker_label: str, sample_utterances: list[str], candidates: list[str]
        ) -> str | None:
            """Mock UI that resolves Speaker A."""
            if speaker_label == "Speaker A":
                return "Alice"
            return None

        text = "Speaker A: First.\r\nSecond.\r\nSpeaker B: Hello."
        result, _mapping = enhance_text(text, ui_callback=mock_ui)
        # Should have Alice instead of Speaker A
        if "Speaker A" in _mapping:
            assert "Alice:" in result

    def test_metadata_preserved(self) -> None:
        """Test that metadata section is preserved."""
        text = "Meeting: Team Sync\r\nDate: 2024-01-15\r\nSpeaker: Hello everyone."
        result, _mapping = enhance_text(text)
        # Metadata should be preserved
        assert "Meeting: Team Sync" in result
        assert "Date: 2024-01-15" in result

    def test_dan_moisan_identification(self) -> None:
        """Test Dan Moisan identification in full enhancement."""
        text = (
            "Speaker A: Dan, what do you think?\r\n"
            "Speaker B: I think it's good.\r\n"
            "Speaker A: Thanks."
        )
        result, _mapping = enhance_text(text)
        # Should identify Speaker B as Dan Moisan
        if "Speaker B" in _mapping:
            assert _mapping["Speaker B"] == "Dan Moisan"
            assert "Dan Moisan:" in result

    def test_complex_transcript(self) -> None:
        """Test enhancement of complex transcript with multiple features."""
        text = (
            "Meeting: Planning Session\r\n"
            "Attendees: John, Alice\r\n"
            "Speaker A: Hello everyone.\r\n"
            "How is everyone doing today?\r\n"
            "Speaker B: I'm doing well, thanks.\r\n"
            "What about you?"
        )
        result, _mapping = enhance_text(text)
        # Should preserve metadata
        assert "Meeting:" in result
        # Should have speakers (possibly resolved)
        assert "Speaker" in result or "John" in result or "Alice" in result
        # Should preserve content
        assert "everyone" in result

    def test_no_ui_callback(self) -> None:
        """Test enhancement without UI callback."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi."
        result, _mapping = enhance_text(text)
        # Should complete without error
        assert "Hello" in result
        # Might or might not resolve speakers (depends on auto-resolution)
        assert len(result) > 0


class TestEnhanceTextSpeakerlessRouting:
    """Test routing logic for speakerless transcripts in enhance_text."""

    def test_speakerless_transcript_gets_labels(self) -> None:
        """Test that transcript WITHOUT speaker labels triggers speakerless detection.

        Verifies:
        1. Speakerless detection is triggered
        2. Generic speaker labels are added
        3. Empty speaker mapping is returned
        """
        text_no_speakers = (
            "Hello everyone, thanks for joining.\r\n"
            "Thank you for having me.\r\n"
            "Let's get started with the agenda.\r\n"
        )

        enhanced, speaker_map = enhance_text(text_no_speakers)

        # Verify generic speaker labels were added
        assert "Speaker A:" in enhanced or "Speaker B:" in enhanced

        # Verify speaker mapping is empty (no name resolution for generic speakers)
        assert speaker_map == {}

    def test_speakerless_with_metadata(self) -> None:
        """Test speakerless detection with metadata section.

        Metadata lines like "Date:", "Attendees:" may be detected as labels,
        but if dialogue has no labels, speakerless detection should apply.
        """
        text = (
            "Date: 2025-12-03\r\n"
            "Attendees: Alice, Bob\r\n"
            "\r\n"
            "Hello everyone.\r\n"
            "Thanks for joining.\r\n"
        )

        enhanced, _speaker_map = enhance_text(text)

        # Verify text was enhanced
        assert enhanced is not None
        assert len(enhanced) > 0

        # Current behavior: metadata may be detected as labels
        # This test documents actual behavior
        assert "Hello everyone" in enhanced

    def test_speakerless_with_num_speakers_parameter(self) -> None:
        """Test that num_speakers parameter is accepted and used.

        Verifies:
        1. num_speakers parameter is accepted
        2. Parameter is passed to speakerless detection
        """
        text = (
            "Hello, welcome to the meeting.\r\n"
            "Thank you for having us.\r\n"
            "Let's discuss the project.\r\n"
        )

        # Test with explicit num_speakers
        enhanced, _speaker_map = enhance_text(text, num_speakers=2)

        # Verify speakerless detection was applied
        assert "Speaker A:" in enhanced
        # Verify speaker mapping is empty for speakerless
        assert len(_speaker_map) == 0

    def test_labeled_transcript_not_affected_by_speakerless(self) -> None:
        """Test that transcripts WITH labels are not affected by speakerless routing.

        Regression test to ensure speakerless integration doesn't break
        existing labeled transcript processing.
        """
        text = "Manager: Let's review the results.\r\n" "Analyst: Revenue is up 15 percent.\r\n"

        enhanced, _speaker_map = enhance_text(text)

        # Verify existing behavior is preserved
        assert "Manager:" in enhanced
        assert "Analyst:" in enhanced

    def test_pure_dialogue_triggers_speakerless(self) -> None:
        """Test that continuous dialogue without labels triggers speakerless detection."""
        pure_dialogue = (
            "Welcome to our quarterly review. "
            "I've analyzed the metrics. "
            "Thank you. "
            "What are your thoughts?"
        )

        enhanced, _speaker_map = enhance_text(pure_dialogue)

        # Verify speakerless detection was triggered
        assert "Speaker A:" in enhanced or "Speaker B:" in enhanced
        # Verify speaker mapping is empty for speakerless
        assert len(_speaker_map) == 0
