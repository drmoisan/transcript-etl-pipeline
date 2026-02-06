"""Tests for clipboard extraction."""

from collections.abc import Callable
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from transcript_etl_pipeline.extract.from_clipboard import (
    ClipboardError,
    _get_clipboard_content_tk,  # pyright: ignore[reportPrivateUsage]
    extract_from_clipboard,
)


class _TkinterStub(ModuleType):
    """Typed tkinter stub module for tests.

    Purpose:
        Provide a minimal, typed module that emulates the tkinter surface used
        by clipboard tests without requiring the real tkinter installation.

    Usage:
        Instantiate with the module name and assign a MagicMock to Tk, then
        patch sys.modules with the instance during tests.

    Flow:
        The test creates the stub, assigns Tk, and patches sys.modules so
        runtime imports resolve to this module.

    Invariants / Constraints:
        Tk must be set to a callable mock that returns a Tk root mock.

    Side Effects:
        None. Callers control sys.modules patching and teardown.

    Attributes:
        Tk (Callable[..., MagicMock]): Mock constructor for Tk root objects.
    """

    Tk: Callable[..., MagicMock]


def _create_tkinter_stub(tk_class: MagicMock) -> ModuleType:
    """Create a minimal tkinter stub module for tests.

    Purpose:
        Provide a synthetic tkinter module so tests can patch Tk usage even
        when tkinter is not installed in the runtime environment.

    Args:
        tk_class (MagicMock): Mock class to expose as tkinter.Tk.

    Returns:
        ModuleType: A stub module with a Tk attribute.

    Raises:
        None: This helper does not raise exceptions.

    Side Effects:
        None: The caller controls sys.modules patching.
    """
    stub = _TkinterStub("tkinter")
    stub.__dict__["Tk"] = tk_class
    return stub


class TestGetClipboardContentTk:
    """Tests for the tkinter clipboard wrapper function."""

    def test_get_clipboard_success(self) -> None:
        """Test successful clipboard retrieval with tkinter."""
        mock_tk_class = MagicMock()
        tkinter_stub = _create_tkinter_stub(mock_tk_class)
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch.dict("sys.modules", {"tkinter": tkinter_stub}),
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
        mock_tk_class = MagicMock()
        tkinter_stub = _create_tkinter_stub(mock_tk_class)
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch.dict("sys.modules", {"tkinter": tkinter_stub}),
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.return_value = ""

            with pytest.raises(ClipboardError, match="Clipboard is empty"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_clipboard_whitespace_only_raises_error(self) -> None:
        """Test that whitespace-only clipboard raises ClipboardError."""
        mock_tk_class = MagicMock()
        tkinter_stub = _create_tkinter_stub(mock_tk_class)
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch.dict("sys.modules", {"tkinter": tkinter_stub}),
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.return_value = "   \n\t  "

            with pytest.raises(ClipboardError, match="Clipboard is empty"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_tcl_error_wrapped_in_clipboard_error(self) -> None:
        """Test that TclError is wrapped in ClipboardError."""
        mock_tk_class = MagicMock()
        tkinter_stub = _create_tkinter_stub(mock_tk_class)
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch.dict("sys.modules", {"tkinter": tkinter_stub}),
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
        mock_tk_class = MagicMock()
        tkinter_stub = _create_tkinter_stub(mock_tk_class)
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch.dict("sys.modules", {"tkinter": tkinter_stub}),
        ):
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.clipboard_get.side_effect = RuntimeError("Unexpected error")

            with pytest.raises(ClipboardError, match="Unexpected error accessing clipboard"):
                _get_clipboard_content_tk()
            mock_root.destroy.assert_called_once()

    def test_root_destroyed_even_on_error(self) -> None:
        """Test that Tk root is destroyed even when an error occurs."""
        mock_tk_class = MagicMock()
        tkinter_stub = _create_tkinter_stub(mock_tk_class)
        with (
            patch("transcript_etl_pipeline.extract.from_clipboard._tkinter_available", True),
            patch.dict("sys.modules", {"tkinter": tkinter_stub}),
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
