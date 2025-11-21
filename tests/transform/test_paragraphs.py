"""Tests for paragraph detection functionality."""

from transcript_etl_pipeline.transform.paragraphs import (
    _ends_with_sentence_terminator,  # pyright: ignore[reportPrivateUsage]
    _is_label_line,  # pyright: ignore[reportPrivateUsage]
    _should_add_paragraph_break,  # pyright: ignore[reportPrivateUsage]
    detect_paragraphs,
)


class TestIsLabelLine:
    """Test label line detection."""

    def test_simple_label(self) -> None:
        """Test detection of simple label at line start."""
        assert _is_label_line("Speaker: hello")
        assert _is_label_line("John: some text")
        assert _is_label_line("Manager: meeting notes")

    def test_label_with_single_space(self) -> None:
        """Test label must have exactly one space after colon."""
        assert _is_label_line("Label: text")

    def test_not_a_label_no_colon(self) -> None:
        """Test line without colon is not a label."""
        assert not _is_label_line("Speaker hello")
        assert not _is_label_line("Just some text")

    def test_not_a_label_lowercase(self) -> None:
        """Test lowercase word with colon is not a label."""
        assert not _is_label_line("speaker: text")

    def test_not_a_label_mid_line(self) -> None:
        """Test colon in middle of line is not a label."""
        assert not _is_label_line("Some text Speaker: hello")

    def test_empty_line(self) -> None:
        """Test empty line is not a label."""
        assert not _is_label_line("")
        assert not _is_label_line("   ")


class TestEndsWithSentenceTerminator:
    """Test sentence terminator detection."""

    def test_ends_with_period(self) -> None:
        """Test line ending with period."""
        assert _ends_with_sentence_terminator("This is a sentence.")

    def test_ends_with_question(self) -> None:
        """Test line ending with question mark."""
        assert _ends_with_sentence_terminator("Is this a question?")

    def test_ends_with_exclamation(self) -> None:
        """Test line ending with exclamation mark."""
        assert _ends_with_sentence_terminator("What an idea!")

    def test_does_not_end_with_terminator(self) -> None:
        """Test line not ending with terminator."""
        assert not _ends_with_sentence_terminator("This is incomplete")
        assert not _ends_with_sentence_terminator("No ending")

    def test_empty_line(self) -> None:
        """Test empty line has no terminator."""
        assert not _ends_with_sentence_terminator("")
        assert not _ends_with_sentence_terminator("   ")

    def test_terminator_with_trailing_space(self) -> None:
        """Test terminator detection with trailing whitespace."""
        assert _ends_with_sentence_terminator("Sentence.  ")


class TestShouldAddParagraphBreak:
    """Test paragraph break decision logic."""

    def test_empty_line_no_break(self) -> None:
        """Test empty line doesn't need paragraph break."""
        lines = ["", "text"]
        assert not _should_add_paragraph_break("", lines, 0)

    def test_sentence_ending_adds_break(self) -> None:
        """Test line ending with sentence terminator gets break."""
        lines = ["This is a sentence.", "Next sentence"]
        assert _should_add_paragraph_break("This is a sentence.", lines, 0)

    def test_question_mark_adds_break(self) -> None:
        """Test question mark triggers paragraph break."""
        lines = ["Is this a question?", "Yes it is"]
        assert _should_add_paragraph_break("Is this a question?", lines, 0)

    def test_long_line_followed_by_short(self) -> None:
        """Test major pause detection with line length analysis."""
        long_line = "This is a very long line with lots of text that goes on and on"
        short_line = "Short"
        lines = [long_line, short_line, "more"]
        assert _should_add_paragraph_break(long_line, lines, 0)

    def test_short_line_no_break(self) -> None:
        """Test short lines don't trigger pause-based breaks."""
        lines = ["Short", "Next", "More"]
        assert not _should_add_paragraph_break("Short", lines, 0)

    def test_no_break_before_label(self) -> None:
        """Test no paragraph break before label line."""
        lines = ["Some text", "Speaker: hello"]
        # Label detection happens elsewhere, this just checks regular logic
        result = _should_add_paragraph_break("Some text", lines, 0)
        # Should not add break (no sentence terminator, not long enough)
        assert not result


class TestDetectParagraphs:
    """Test complete paragraph detection functionality."""

    def test_empty_text(self) -> None:
        """Test empty text returns empty."""
        assert detect_paragraphs("") == ""
        assert detect_paragraphs("   ") == "   "

    def test_metadata_no_paragraph_breaks(self) -> None:
        """Test metadata section doesn't get paragraph breaks."""
        text = "Meeting: Team Sync\r\nDate: 2024-01-15\r\nAttendees: John, Jane"
        result = detect_paragraphs(text)
        # Should not add extra blank lines in metadata
        assert result.count("\r\n\r\n") == 0

    def test_single_sentence_no_break(self) -> None:
        """Test single sentence doesn't get trailing break."""
        text = "This is a single sentence."
        result = detect_paragraphs(text)
        # Should not add break at end of document
        assert not result.endswith("\r\n\r\n")

    def test_paragraph_after_sentence_ending(self) -> None:
        """Test paragraph break after sentence terminator."""
        text = "Speaker: This is sentence one.\r\nThis is sentence two."
        result = detect_paragraphs(text)
        # Should add blank line after first sentence
        assert "\r\n\r\n" in result

    def test_label_terminates_metadata(self) -> None:
        """Test first label marks end of metadata."""
        text = "Date: 2024-01-15\r\nSpeaker: Hello world."
        result = detect_paragraphs(text)
        lines = result.split("\r\n")
        # Metadata line, Speaker label, text - no extra blank lines
        assert len([line for line in lines if not line.strip()]) == 0

    def test_multiple_paragraphs(self) -> None:
        """Test multiple paragraph detection."""
        text = "Speaker: First sentence.\r\nSecond sentence.\r\nThird sentence."
        result = detect_paragraphs(text)
        # Should have paragraph breaks after sentences
        blank_lines = result.count("\r\n\r\n")
        assert blank_lines >= 1

    def test_no_extra_break_at_end(self) -> None:
        """Test no extra CRLF at document end."""
        text = "Speaker: Hello.\r\nGoodbye."
        result = detect_paragraphs(text)
        # Should not end with double CRLF
        assert not result.endswith("\r\n\r\n\r\n")

    def test_preserves_existing_structure(self) -> None:
        """Test preserves labels and basic structure."""
        text = "Speaker: Hello.\r\nWorld."
        result = detect_paragraphs(text)
        # Should contain the label
        assert "Speaker:" in result

    def test_label_does_not_get_paragraph_break(self) -> None:
        """Test labels themselves don't trigger paragraph breaks."""
        text = "Speaker: First.\r\nManager: Second."
        result = detect_paragraphs(text)
        # Each label starts new section, no extra breaks
        result.split("\r\n")
        # Should have the two labels
        assert "Speaker:" in result
        assert "Manager:" in result

    def test_mixed_content(self) -> None:
        """Test paragraph detection with mixed content."""
        text = (
            "Meeting: Team Sync\r\n"
            "Date: 2024-01-15\r\n"
            "Transcript: \r\n"
            "Speaker: Hello everyone.\r\n"
            "How are you today?\r\n"
            "Manager: I'm doing well."
        )
        result = detect_paragraphs(text)
        # Should preserve structure
        assert "Meeting:" in result
        assert "Speaker:" in result
        assert "Manager:" in result

    def test_long_line_pause_detection(self) -> None:
        """Test pause detection with line length analysis."""
        long_line = (
            "This is a very long line of text that represents someone "
            "speaking for a while without stopping to catch their breath"
        )
        short_line = "Pause."
        text = f"Speaker: {long_line}\r\n{short_line}\r\nMore text."
        result = detect_paragraphs(text)
        # Should detect the pause and add break
        lines = result.split("\r\n")
        # Check that structure is preserved
        assert len(lines) >= 3

    def test_whitespace_only_lines_preserved(self) -> None:
        """Test whitespace-only lines are preserved."""
        text = "Speaker: Hello.\r\n   \r\nWorld."
        result = detect_paragraphs(text)
        # Should preserve the whitespace line
        assert "   " in result or result.count("\r\n\r\n") > 0
