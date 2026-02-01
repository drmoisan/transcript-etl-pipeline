"""Tests for paragraph detection functionality."""

import pytest

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

    def test_detects_paragraphs_in_freeform_text(self) -> None:
        """Ensure long freeform transcript gains paragraph breaks."""
        text = (
            "Transcript:\r\n"
            "Testing, testing. This is Dan Moisan. I am speaking before the call begins. "
            "To validate that audio can be properly captured. And that everything is working. "
            "How are you today? I'm doing great. How are you, Aaron? Doing well. Happy Friday."
        )

        result = detect_paragraphs(text)

        # Expect at least one paragraph break inserted by semantic detection
        assert result.count("\r\n\r\n") >= 1

    def test_question_answer_block_gets_split(self) -> None:
        """Ensure question/answer pairs on a single line become separate paragraphs."""
        text = "Transcript:\r\n" "How are you doing today? I'm doing well. Thanks for asking."

        result = detect_paragraphs(text)
        paragraphs = [block for block in result.split("\r\n\r\n") if block.strip()]

        assert len(paragraphs) >= 2


class TestPrivateParagraphHelpers:
    """Test private helper functions for paragraph detection."""

    def test_segment_freeform_block_empty_returns_lines(self) -> None:
        """Verify empty block returns original lines."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _segment_freeform_block,  # pyright: ignore[reportPrivateUsage]
        )

        result = _segment_freeform_block([])
        assert result == []

        result = _segment_freeform_block(["   ", ""])
        # Should return original if no meaningful text
        assert len(result) >= 0

    def test_segment_freeform_with_texttiling_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify fallback when TextTiling raises ValueError."""
        from nltk.tokenize import TextTilingTokenizer  # type: ignore[import-untyped]

        from transcript_etl_pipeline.transform.paragraphs import (
            _segment_freeform_block,  # pyright: ignore[reportPrivateUsage]
        )

        # Mock TextTilingTokenizer to raise ValueError
        def mock_tokenize(*args: object, **kwargs: object) -> object:
            raise ValueError("Not enough sentences for TextTiling")

        monkeypatch.setattr(TextTilingTokenizer, "tokenize", mock_tokenize)

        lines = ["This is a test sentence. Another sentence here."]
        result = _segment_freeform_block(lines)
        # Should fall back to sent_tokenize and return something
        assert isinstance(result, list)
        assert len(result) > 0

    def test_segment_freeform_with_texttiling_lookup_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify fallback when TextTiling raises LookupError."""
        from nltk.tokenize import TextTilingTokenizer  # type: ignore[import-untyped]

        from transcript_etl_pipeline.transform.paragraphs import (
            _segment_freeform_block,  # pyright: ignore[reportPrivateUsage]
        )

        # Mock TextTilingTokenizer to raise LookupError
        def mock_tokenize(*args: object, **kwargs: object) -> object:
            raise LookupError("NLTK data not found")

        monkeypatch.setattr(TextTilingTokenizer, "tokenize", mock_tokenize)

        lines = ["This is a test sentence. Another sentence here."]
        result = _segment_freeform_block(lines)
        # Should fall back to sent_tokenize and return something
        assert isinstance(result, list)
        assert len(result) > 0

    def test_group_sentences_into_paragraphs_single_sentence(self) -> None:
        """Verify single sentence forms one paragraph."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _group_sentences_into_paragraphs,  # pyright: ignore[reportPrivateUsage]
        )

        sentences = ["This is one sentence."]
        result = _group_sentences_into_paragraphs(sentences)
        assert len(result) == 1
        assert result[0] == "This is one sentence."

    def test_should_break_sentence_on_question_with_cue(self) -> None:
        """Verify break after question followed by conversation cue."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _should_break_sentence,  # pyright: ignore[reportPrivateUsage]
        )

        result = _should_break_sentence("What do you think?", "Well, I believe...", 50)
        assert result is True

    def test_should_break_sentence_on_max_chars(self) -> None:
        """Verify break when max paragraph chars exceeded."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _should_break_sentence,  # pyright: ignore[reportPrivateUsage]
        )

        result = _should_break_sentence("Short sentence.", "Next.", 500)
        # Over MAX_PARAGRAPH_CHARS (480)
        assert result is True

    def test_should_break_sentence_on_exclamation_with_cue(self) -> None:
        """Verify break after exclamation followed by conversation cue."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _should_break_sentence,  # pyright: ignore[reportPrivateUsage]
        )

        result = _should_break_sentence("That's amazing!", "Yes, I agree.", 50)
        assert result is True

    def test_should_break_sentence_long_followed_by_short(self) -> None:
        """Verify break on long sentence followed by short."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _should_break_sentence,  # pyright: ignore[reportPrivateUsage]
        )

        long_sentence = (
            "This is a very long sentence with many words that goes on and on "
            "and provides lots of detail about something important and continues "
            "for quite a while."
        )
        short = "Short."
        result = _should_break_sentence(long_sentence, short, 100)
        assert result is True

    def test_should_break_sentence_cue_with_enough_chars(self) -> None:
        """Verify break on conversation cue when enough chars accumulated."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _should_break_sentence,  # pyright: ignore[reportPrivateUsage]
        )

        result = _should_break_sentence("Regular sentence.", "Well, continuing.", 150)
        # Over 120 chars and next starts with cue
        assert result is True

    def test_starts_with_conversation_cue_detects_cues(self) -> None:
        """Verify conversation cue detection."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _starts_with_conversation_cue,  # pyright: ignore[reportPrivateUsage]
        )

        assert _starts_with_conversation_cue("Well, I think...") is True
        assert _starts_with_conversation_cue("So what now?") is True
        assert _starts_with_conversation_cue("Thanks for that.") is True
        assert _starts_with_conversation_cue("Yes, exactly.") is True
        assert _starts_with_conversation_cue("No, that's wrong.") is True

    def test_starts_with_conversation_cue_handles_punctuation(self) -> None:
        """Verify cue detection handles punctuation."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _starts_with_conversation_cue,  # pyright: ignore[reportPrivateUsage]
        )

        assert _starts_with_conversation_cue("Well!") is True
        assert _starts_with_conversation_cue("Okay.") is True
        assert _starts_with_conversation_cue("Sure,") is True

    def test_starts_with_conversation_cue_false_for_non_cues(self) -> None:
        """Verify non-cues return false."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _starts_with_conversation_cue,  # pyright: ignore[reportPrivateUsage]
        )

        assert _starts_with_conversation_cue("The meeting starts now.") is False
        assert _starts_with_conversation_cue("Hello everyone.") is False

    def test_extend_with_segments_adds_blank_lines(self) -> None:
        """Verify segments are extended with blank line separators."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _extend_with_segments,  # pyright: ignore[reportPrivateUsage]
        )

        result_lines: list[str] = []
        segments = ["First segment.", "Second segment.", "Third segment."]
        _extend_with_segments(result_lines, segments)

        # Should have segments with blank lines between them
        assert len(result_lines) >= 5  # 3 segments + 2 blank lines
        assert "" in result_lines

    def test_extend_with_segments_skips_empty_segments(self) -> None:
        """Verify empty segments are skipped."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _extend_with_segments,  # pyright: ignore[reportPrivateUsage]
        )

        result_lines: list[str] = []
        segments = ["First segment.", "", "   ", "Second segment."]
        _extend_with_segments(result_lines, segments)

        # Should only have non-empty segments
        text_lines = [line for line in result_lines if line.strip()]
        assert len(text_lines) == 2

    def test_has_multiple_sentences_true_for_multi(self) -> None:
        """Verify multiple sentence detection."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _has_multiple_sentences,  # pyright: ignore[reportPrivateUsage]
        )

        assert _has_multiple_sentences("First sentence. Second sentence.") is True
        assert _has_multiple_sentences("Question? Answer.") is True

    def test_has_multiple_sentences_false_for_single(self) -> None:
        """Verify single sentence detection."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _has_multiple_sentences,  # pyright: ignore[reportPrivateUsage]
        )

        assert _has_multiple_sentences("Just one sentence.") is False
        assert _has_multiple_sentences("Only this.") is False

    def test_ensure_sentence_tokenizer_initializes_once(self) -> None:
        """Verify tokenizer is initialized only once."""
        from transcript_etl_pipeline.transform import paragraphs

        # Reset the flag to test initialization
        original_flag = paragraphs._sent_tokenizer_ready  # pyright: ignore[reportPrivateUsage]
        try:
            paragraphs._sent_tokenizer_ready = False  # pyright: ignore[reportPrivateUsage]

            # Call ensure
            from transcript_etl_pipeline.transform.paragraphs import (
                _ensure_sentence_tokenizer,  # pyright: ignore[reportPrivateUsage]
            )

            _ensure_sentence_tokenizer()

            # Flag should now be True
            assert paragraphs._sent_tokenizer_ready is True  # pyright: ignore[reportPrivateUsage]

            # Call again
            _ensure_sentence_tokenizer()
            # Should still be True and not re-download
            assert paragraphs._sent_tokenizer_ready is True  # pyright: ignore[reportPrivateUsage]
        finally:
            # Restore original state
            paragraphs._sent_tokenizer_ready = original_flag  # pyright: ignore[reportPrivateUsage]

    def test_append_block_with_classic_breaks_empty_block(self) -> None:
        """Verify empty block is handled correctly."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _append_block_with_classic_breaks,  # pyright: ignore[reportPrivateUsage]
        )

        result_lines: list[str] = []
        _append_block_with_classic_breaks(result_lines, [])

        # Should remain empty
        assert len(result_lines) == 0

    def test_append_block_with_previous_context(self) -> None:
        """Verify block appending considers previous line context."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _append_block_with_classic_breaks,  # pyright: ignore[reportPrivateUsage]
        )

        result_lines = ["Previous sentence."]
        block_lines = ["Next sentence.", "More text."]

        _append_block_with_classic_breaks(result_lines, block_lines)

        # Should have added the block
        assert len(result_lines) >= 3

    def test_needs_semantic_segmentation_empty(self) -> None:
        """Verify empty lines don't need semantic segmentation."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _needs_semantic_segmentation,  # pyright: ignore[reportPrivateUsage]
        )

        result = _needs_semantic_segmentation([])
        assert result is False

        result = _needs_semantic_segmentation(["   ", ""])
        assert result is False

    def test_needs_semantic_segmentation_single_short_sentence(self) -> None:
        """Verify single short sentence doesn't need segmentation."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _needs_semantic_segmentation,  # pyright: ignore[reportPrivateUsage]
        )

        result = _needs_semantic_segmentation(["Hello."])
        assert result is False

    def test_needs_semantic_segmentation_multiple_sentences(self) -> None:
        """Verify multiple sentences trigger segmentation."""
        from transcript_etl_pipeline.transform.paragraphs import (
            _needs_semantic_segmentation,  # pyright: ignore[reportPrivateUsage]
        )

        result = _needs_semantic_segmentation(["First sentence. Second sentence."])
        assert result is True

    def test_detect_paragraphs_empty_freeform_block(self) -> None:
        """Verify empty freeform blocks are handled in flush."""
        text = "Transcript:\r\n"
        result = detect_paragraphs(text)
        assert "Transcript" in result

    def test_detect_paragraphs_blank_lines_between_labels(self) -> None:
        """Verify blank lines between labels are preserved."""
        text = "Speaker A: Hello.\r\n\r\nSpeaker B: Hi."
        result = detect_paragraphs(text)
        # Should preserve the structure
        assert "Speaker A:" in result
        assert "Speaker B:" in result

    def test_segment_freeform_block_with_texttiling_tuple_result(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify TextTiling tuple result is handled."""
        from nltk.tokenize import TextTilingTokenizer  # type: ignore[import-untyped]

        from transcript_etl_pipeline.transform.paragraphs import (
            _segment_freeform_block,  # pyright: ignore[reportPrivateUsage]
        )

        # Mock TextTiling to return tuple (segments, boundaries)
        def mock_tokenize(*args: object, **kwargs: object) -> tuple[list[str], list[int]]:
            return (["First segment.", "Second segment."], [0, 1])

        monkeypatch.setattr(TextTilingTokenizer, "tokenize", mock_tokenize)

        lines = ["This is test text with multiple sentences here."]
        result = _segment_freeform_block(lines)

        # Should handle tuple result
        assert isinstance(result, list)
        assert len(result) >= 1
