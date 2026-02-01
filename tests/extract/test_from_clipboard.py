"""Tests for clipboard extraction."""

from unittest.mock import MagicMock, patch

import pytest

from transcript_etl_pipeline.extract.from_clipboard import (
    ClipboardError,
    _get_clipboard_content_tk,  # pyright: ignore[reportPrivateUsage]
    extract_from_clipboard,
)


class TestGetClipboardContentTk:
    """Tests for the tkinter clipboard wrapper function."""

    def test_get_clipboard_success(self) -> None:
        """Test successful clipboard retrieval with tkinter."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch("tkinter.Tk") as mock_tk_class,
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.return_value = "Clipboard content"

            result = _get_clipboard_content_tk()
            assert result == "Clipboard content"
            mock_root.withdraw.assert_called_once()
            mock_root.destroy.assert_called_once()

    def test_tkinter_not_available(self) -> None:
        """Test that ClipboardError is raised when tkinter is unavailable."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", False),
            pytest.raises(ClipboardError, match="tkinter is not available"),
        ):
            _get_clipboard_content_tk()

    def test_clipboard_empty_raises_error(self) -> None:
        """Test that empty clipboard raises ClipboardError."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch("tkinter.Tk") as mock_tk_class,
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.return_value = ""

            with pytest.raises(ClipboardError, match="Clipboard is empty"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_clipboard_whitespace_only_raises_error(self) -> None:
        """Test that whitespace-only clipboard raises ClipboardError."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch("tkinter.Tk") as mock_tk_class,
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.return_value = "   \n\t  "

            with pytest.raises(ClipboardError, match="Clipboard is empty"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_tcl_error_wrapped_in_clipboard_error(self) -> None:
        """Test that TclError is wrapped in ClipboardError."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch("tkinter.Tk") as mock_tk_class,
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root

            # Create a mock TclError
            class TclError(Exception):
                pass

            mock_root.clipboard_get.side_effect = TclError("selection owner didn't respond")

            with pytest.raises(ClipboardError, match="Failed to access clipboard"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_generic_exception_wrapped(self) -> None:
        """Test that generic exceptions are wrapped in ClipboardError."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch("tkinter.Tk") as mock_tk_class,
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.side_effect = RuntimeError("Unexpected error")

            with pytest.raises(ClipboardError, match="Unexpected error accessing clipboard"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_root_destroyed_even_on_error(self) -> None:
        """Test that Tk root is destroyed even when an error occurs."""
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch("tkinter.Tk") as mock_tk_class,
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.side_effect = RuntimeError("Error")

            with pytest.raises(ClipboardError):
                _get_clipboard_content_tk()
            # Verify destroy was called even though an exception occurred
            mock_root.destroy.assert_called_once()


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
        """Test that default clipboard function is used when none provided."""
        # Mock the default tk function to avoid actual clipboard access
        with patch(
            "transcript_etl_pipeline.extract.from_clipboard._get_clipboard_content_tk"
        ) as mock_tk_func:
            mock_tk_func.return_value = "Default clipboard content"

            result = extract_from_clipboard()
            assert result == "Default clipboard content"
            mock_tk_func.assert_called_once()

    def test_extract_with_unicode_content(self) -> None:
        """Test extracting Unicode content including emojis and special characters."""

        def mock_clipboard() -> str:
            return "Hello 世界 🌍 café naïve"

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == "Hello 世界 🌍 café naïve"

    def test_extract_with_very_long_content(self) -> None:
        """Test extracting very long clipboard content."""
        # Simulate a large clipboard content
        long_content = "A" * 100000  # 100K characters

        def mock_clipboard() -> str:
            return long_content

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == long_content
        assert len(result) == 100000

    def test_extract_with_mixed_line_endings(self) -> None:
        """Test extracting content with mixed line endings (CRLF and LF)."""

        def mock_clipboard() -> str:
            return "Line 1\r\nLine 2\nLine 3\r\nLine 4"

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == "Line 1\r\nLine 2\nLine 3\r\nLine 4"

    def test_extract_with_tabs_and_special_whitespace(self) -> None:
        """Test extracting content with tabs and special whitespace."""

        def mock_clipboard() -> str:
            return "Column1\tColumn2\tColumn3\nData1\tData2\tData3"

        result = extract_from_clipboard(clipboard_func=mock_clipboard)
        assert result == "Column1\tColumn2\tColumn3\nData1\tData2\tData3"

    def test_none_return_treated_as_empty(self) -> None:
        """Test that None returned from clipboard function is treated as empty.

        This tests the edge case where a clipboard function might return None.
        """

        def mock_none_clipboard() -> str:
            return None  # type: ignore[return-value]

        # The function checks `not content` which catches None
        with pytest.raises(ClipboardError, match="empty or contains only whitespace"):
            extract_from_clipboard(clipboard_func=mock_none_clipboard)
