"""Tests for text normalization."""

from transcript_etl_pipeline.transform.normalize import (
    _clean_whitespace,
    _is_label,
    _normalize_labels,
    _normalize_line_endings,
    normalize_text,
)


class TestNormalizeLineEndings:
    """Tests for line ending normalization."""

    def test_unix_to_crlf(self) -> None:
        """Test converting Unix LF to Windows CRLF."""
        text = "Line 1\nLine 2\nLine 3"
        result = _normalize_line_endings(text)
        assert result == "Line 1\r\nLine 2\r\nLine 3"

    def test_mac_to_crlf(self) -> None:
        """Test converting old Mac CR to Windows CRLF."""
        text = "Line 1\rLine 2\rLine 3"
        result = _normalize_line_endings(text)
        assert result == "Line 1\r\nLine 2\r\nLine 3"

    def test_crlf_unchanged(self) -> None:
        """Test that CRLF is preserved."""
        text = "Line 1\r\nLine 2\r\nLine 3"
        result = _normalize_line_endings(text)
        assert result == text

    def test_mixed_line_endings(self) -> None:
        """Test converting mixed line endings to CRLF."""
        text = "Line 1\nLine 2\r\nLine 3\rLine 4"
        result = _normalize_line_endings(text)
        assert result == "Line 1\r\nLine 2\r\nLine 3\r\nLine 4"

    def test_empty_text(self) -> None:
        """Test with empty text."""
        assert _normalize_line_endings("") == ""


class TestCleanWhitespace:
    """Tests for whitespace cleaning."""

    def test_remove_duplicate_spaces(self) -> None:
        """Test removing duplicate spaces within lines."""
        text = "Hello    world  with   spaces"
        result = _clean_whitespace(text)
        assert result == "Hello world with spaces"

    def test_remove_trailing_spaces(self) -> None:
        """Test removing trailing spaces."""
        text = "Line 1   \r\nLine 2  \r\nLine 3    "
        result = _clean_whitespace(text)
        assert result == "Line 1\r\nLine 2\r\nLine 3"

    def test_collapse_multiple_blank_lines(self) -> None:
        """Test collapsing multiple blank lines to single blank line."""
        text = "Line 1\r\n\r\n\r\n\r\nLine 2"
        result = _clean_whitespace(text)
        assert result == "Line 1\r\n\r\nLine 2"

    def test_remove_trailing_blank_lines(self) -> None:
        """Test removing trailing blank lines."""
        text = "Line 1\r\nLine 2\r\n\r\n\r\n"
        result = _clean_whitespace(text)
        assert result == "Line 1\r\nLine 2"

    def test_preserve_single_blank_line(self) -> None:
        """Test that single blank lines are preserved."""
        text = "Line 1\r\n\r\nLine 2\r\n\r\nLine 3"
        result = _clean_whitespace(text)
        assert result == text

    def test_empty_text(self) -> None:
        """Test with empty text."""
        assert _clean_whitespace("") == ""


class TestIsLabel:
    """Tests for label detection."""

    def test_valid_label(self) -> None:
        """Test detecting valid labels."""
        assert _is_label("John:") is True
        assert _is_label("Speaker:") is True
        assert _is_label("Manager:") is True

    def test_lowercase_not_label(self) -> None:
        """Test that lowercase words are not labels."""
        assert _is_label("john:") is False
        assert _is_label("speaker:") is False

    def test_no_colon_not_label(self) -> None:
        """Test that words without colon are not labels."""
        assert _is_label("John") is False
        assert _is_label("Speaker") is False

    def test_multi_word_not_label(self) -> None:
        """Test that multi-word tokens are not labels."""
        assert _is_label("John Smith:") is False
        assert _is_label("Speaker A:") is False

    def test_empty_not_label(self) -> None:
        """Test that empty or colon-only is not a label."""
        assert _is_label(":") is False
        assert _is_label("") is False

    def test_label_with_numbers(self) -> None:
        """Test labels with numbers."""
        assert _is_label("Speaker1:") is True
        assert _is_label("Manager2:") is True


class TestNormalizeLabels:
    """Tests for label normalization."""

    def test_label_at_line_start(self) -> None:
        """Test label already at line start."""
        text = "John: Hello world"
        result = _normalize_labels(text)
        assert result == "John: Hello world"

    def test_label_with_multiple_spaces(self) -> None:
        """Test normalizing spaces after label."""
        text = "John:    Hello world"
        result = _normalize_labels(text)
        assert result == "John: Hello world"

    def test_mid_line_label_gets_newline(self) -> None:
        """Test that mid-line label gets CRLF before it."""
        text = "Some text John: Hello world"
        result = _normalize_labels(text)
        assert result == "Some text\r\nJohn: Hello world"

    def test_multiple_mid_line_labels(self) -> None:
        """Test multiple mid-line labels."""
        text = "Intro text Speaker1: Hello Speaker2: Hi"
        result = _normalize_labels(text)
        lines = result.split("\r\n")
        assert len(lines) == 3
        assert lines[0] == "Intro text"
        assert lines[1] == "Speaker1: Hello"
        assert lines[2] == "Speaker2: Hi"

    def test_label_only_line(self) -> None:
        """Test line with only a label."""
        text = "John:"
        result = _normalize_labels(text)
        assert result == "John:"

    def test_no_label_unchanged(self) -> None:
        """Test text without labels remains unchanged."""
        text = "This is just regular text"
        result = _normalize_labels(text)
        assert result == text

    def test_preserve_multiline(self) -> None:
        """Test multiline text with labels."""
        text = "John: First line\r\nMary: Second line"
        result = _normalize_labels(text)
        assert result == text


class TestNormalizeText:
    """Tests for complete normalization."""

    def test_complete_normalization(self) -> None:
        """Test full normalization pipeline."""
        text = "Meeting: 2024-01-01\n\n\nJohn:   Hello  Mary Mary: Hi there"
        result = normalize_text(text)

        # Should have CRLF line endings
        assert "\r\n" in result
        assert "\n" not in result.replace("\r\n", "")

        # Should have collapsed blank lines
        assert "\r\n\r\n\r\n" not in result

        # Should have normalized labels
        lines = result.split("\r\n")
        assert any("John:" in line for line in lines)
        assert any("Mary:" in line for line in lines)

    def test_empty_text(self) -> None:
        """Test normalizing empty text."""
        assert normalize_text("") == ""

    def test_metadata_and_transcript(self) -> None:
        """Test normalizing text with metadata and transcript sections."""
        text = "Title: Meeting Notes\nDate: 2024-01-01\n\n\nTranscript: Speaker1: Hello world"
        result = normalize_text(text)

        lines = result.split("\r\n")
        # Should have Title, Date, blank line, Transcript, Speaker1
        assert len(lines) >= 4
        assert lines[0] == "Title: Meeting Notes"
        assert lines[1] == "Date: 2024-01-01"
