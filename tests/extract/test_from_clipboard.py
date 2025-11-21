"""Tests for clipboard extraction."""

import pytest

from transcript_etl_pipeline.extract.from_clipboard import (
    ClipboardError,
    extract_from_clipboard,
)


class TestExtractFromClipboard:
    """Tests for clipboard extraction functionality."""

    def test_extract_with_valid_content(self) -> None:
        """Test extracting valid text from clipboard."""

        def mock_clipboard() -> str:
            return "This is clipboard content"

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == "This is clipboard content"

    def test_extract_with_multiline_content(self) -> None:
        """Test extracting multiline text from clipboard."""

        def mock_clipboard() -> str:
            return "Line 1\nLine 2\nLine 3"

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == "Line 1\nLine 2\nLine 3"

    def test_empty_clipboard_raises_error(self) -> None:
        """Test that empty clipboard raises ClipboardError."""

        def mock_empty_clipboard() -> str:
            return ""

        with pytest.raises(ClipboardError, match="empty or contains only whitespace"):
            extract_from_clipboard(clipboard_func=mock_empty_clipboard)

    def test_whitespace_only_clipboard_raises_error(self) -> None:
        """Test that whitespace-only clipboard raises ClipboardError."""

        def mock_whitespace_clipboard() -> str:
            return "   \n\t  "

        with pytest.raises(ClipboardError, match="empty or contains only whitespace"):
            extract_from_clipboard(clipboard_func=mock_whitespace_clipboard)

    def test_clipboard_with_leading_trailing_whitespace(self) -> None:
        """Test that content with leading/trailing whitespace is preserved."""

        def mock_clipboard() -> str:
            return "  Content with spaces  "

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == "  Content with spaces  "

    def test_clipboard_error_propagates(self) -> None:
        """Test that ClipboardError from clipboard function propagates."""

        def mock_error_clipboard() -> str:
            raise ClipboardError("Mock clipboard error")

        with pytest.raises(ClipboardError, match="Mock clipboard error"):
            extract_from_clipboard(clipboard_func=mock_error_clipboard)

    def test_uses_default_clipboard_when_no_func_provided(self) -> None:
        """Test that default clipboard function is used when none provided.

        Note: This test may fail in headless environments where tkinter is unavailable.
        We expect a ClipboardError in such cases, which is acceptable.
        """
        # This will attempt to use tkinter clipboard
        # In a headless test environment, this should raise ClipboardError
        # In a normal environment with clipboard access, it will return clipboard content
        try:
            result = extract_from_clipboard()
            # If we get here, clipboard was accessible
            assert isinstance(result, str)
        except ClipboardError:
            # Expected in headless/CI environments
            pass
