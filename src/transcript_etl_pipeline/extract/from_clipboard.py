"""Extract transcript text from clipboard.

This module provides clipboard extraction functionality with testability.
Uses tkinter for cross-platform clipboard access on Windows.
"""

from __future__ import annotations

from collections.abc import Callable

_tkinter_available = False
try:
    import tkinter as tk  # type: ignore[reportUnusedImport]  # noqa: F401

    _tkinter_available = True
except ImportError:
    pass


class ClipboardError(Exception):
    """Raised when clipboard operations fail."""

    pass


def _get_clipboard_content_tk() -> str:
    """Get clipboard content using tkinter.

    This is a thin wrapper around tkinter clipboard operations to enable testing.

    Returns:
        The text content from the clipboard

    Raises:
        ClipboardError: If clipboard is empty or inaccessible
    """
    if not _tkinter_available:
        raise ClipboardError(
            "tkinter is not available. Install tkinter or use a different clipboard method."
        )

    # Import here to satisfy type checker
    import tkinter as tk_runtime

    try:
        root = tk_runtime.Tk()
        root.withdraw()  # Hide the main window
        try:
            content = root.clipboard_get()
            if not content or not content.strip():
                raise ClipboardError("Clipboard is empty or contains only whitespace")
            return content
        finally:
            root.destroy()
    except Exception as e:
        if "TclError" in type(e).__name__:
            raise ClipboardError(f"Failed to access clipboard: {e}") from e
        raise ClipboardError(f"Unexpected error accessing clipboard: {e}") from e


def extract_from_clipboard(clipboard_func: Callable[[], str] | None = None) -> str:
    """Extract text content from the system clipboard.

    Args:
        clipboard_func: Optional function to get clipboard content.
                       If None, uses tkinter clipboard. This parameter
                       allows for dependency injection in tests.

    Returns:
        The text content from the clipboard

    Raises:
        ClipboardError: If clipboard is empty or inaccessible
    """
    func: Callable[[], str] = clipboard_func if clipboard_func else _get_clipboard_content_tk

    content = func()

    if not content or not content.strip():
        raise ClipboardError("Clipboard is empty or contains only whitespace")

    return content
