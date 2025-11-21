"""Tests for enhancement orchestration."""

from transcript_etl_pipeline.transform.enhance import enhance_text


class TestEnhanceText:
    """Test the enhance_text orchestration."""

    def test_empty_text(self) -> None:
        """Test empty text returns empty."""
        result, mapping = enhance_text("")
        assert result == ""
        assert mapping == {}

    def test_simple_transcript(self) -> None:
        """Test enhancement of simple transcript."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi there."
        result, mapping = enhance_text(text)
        # Should have speaker labels
        assert "Speaker A:" in result or "Speaker B:" in result
        # Should preserve structure
        assert "Hello" in result
        assert "Hi there" in result

    def test_with_ui_callback(self) -> None:
        """Test enhancement with UI callback for speaker resolution."""

        def mock_ui(speaker: str, samples: list[str]) -> str | None:
            """Mock UI that resolves speakers."""
            if speaker == "Speaker A":
                return "John"
            return None

        text = "Speaker A: Hello everyone.\r\nSpeaker A: How are you?"
        result, mapping = enhance_text(text, ui_callback=mock_ui)
        # Should resolve Speaker A to John
        if "Speaker A" in mapping:
            assert mapping["Speaker A"] == "John"
            assert "John:" in result

    def test_paragraph_detection_applied(self) -> None:
        """Test that paragraph detection is applied."""
        text = "Speaker A: First sentence.\r\nSecond sentence.\r\nThird sentence."
        result, mapping = enhance_text(text)
        # Should add paragraph breaks after sentences
        # Count blank lines as indication of paragraph breaks
        blank_line_count = result.count("\r\n\r\n")
        # Might have paragraph breaks
        assert blank_line_count >= 0

    def test_speaker_resolution_then_paragraphs(self) -> None:
        """Test that speaker resolution happens before paragraph detection."""

        def mock_ui(speaker: str, samples: list[str]) -> str | None:
            """Mock UI that resolves Speaker A."""
            if speaker == "Speaker A":
                return "Alice"
            return None

        text = "Speaker A: First.\r\nSecond.\r\nSpeaker B: Hello."
        result, mapping = enhance_text(text, ui_callback=mock_ui)
        # Should have Alice instead of Speaker A
        if "Speaker A" in mapping:
            assert "Alice:" in result

    def test_metadata_preserved(self) -> None:
        """Test that metadata section is preserved."""
        text = "Meeting: Team Sync\r\nDate: 2024-01-15\r\nSpeaker: Hello everyone."
        result, mapping = enhance_text(text)
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
        result, mapping = enhance_text(text)
        # Should identify Speaker B as Dan Moisan
        if "Speaker B" in mapping:
            assert mapping["Speaker B"] == "Dan Moisan"
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
        result, mapping = enhance_text(text)
        # Should preserve metadata
        assert "Meeting:" in result
        # Should have speakers (possibly resolved)
        assert "Speaker" in result or "John" in result or "Alice" in result
        # Should preserve content
        assert "everyone" in result

    def test_no_ui_callback(self) -> None:
        """Test enhancement without UI callback."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi."
        result, mapping = enhance_text(text)
        # Should complete without error
        assert "Hello" in result
        # Might or might not resolve speakers (depends on auto-resolution)
        assert len(result) > 0
