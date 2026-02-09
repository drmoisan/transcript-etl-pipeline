"""Unit tests for UI helpers without Tkinter."""

from __future__ import annotations

import os
import types

import pytest

from transcript_etl_pipeline import ui


def test_is_debugger_active_with_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    """Detect debugger when sys.gettrace is set."""

    def _gettrace() -> object:
        return object()

    monkeypatch.setattr(ui.sys, "gettrace", _gettrace)
    assert ui._is_debugger_active() is True  # pyright: ignore[reportPrivateUsage]


def test_is_debugger_active_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Detect debugger when PYTHONBREAKPOINT is set."""

    def _gettrace() -> None:
        return None

    monkeypatch.setattr(ui.sys, "gettrace", _gettrace)
    monkeypatch.setitem(os.environ, "PYTHONBREAKPOINT", "1")
    try:
        assert ui._is_debugger_active() is True  # pyright: ignore[reportPrivateUsage]
    finally:
        os.environ.pop("PYTHONBREAKPOINT", None)


def test_check_tkinter_available_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raise when tkinter is unavailable."""
    monkeypatch.setattr(ui, "_tkinter_available", False)
    with pytest.raises(RuntimeError, match="tkinter is not available"):
        ui.check_tkinter_available()


def test_show_error_and_info_use_messagebox(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure show_error/show_info call messagebox functions."""
    calls: list[tuple[str, str]] = []

    class _DummyTk:
        def withdraw(self) -> None:
            return None

        def destroy(self) -> None:
            return None

    def _showerror(title: str, message: str) -> None:
        calls.append((title, message))

    def _showinfo(title: str, message: str) -> None:
        calls.append((title, message))

    dummy_messagebox = types.SimpleNamespace(showerror=_showerror, showinfo=_showinfo)

    monkeypatch.setattr(ui, "_tkinter_available", True)
    monkeypatch.setattr(ui, "tk", types.SimpleNamespace(Tk=_DummyTk))
    monkeypatch.setattr(ui, "messagebox", dummy_messagebox)

    ui.show_error("Error", "Something failed")
    ui.show_info("Info", "All good")

    assert calls == [("Error", "Something failed"), ("Info", "All good")]


def test_prompt_source_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the selected source for yes/no prompt."""

    class _DummyTk:
        def withdraw(self) -> None:
            return None

        def destroy(self) -> None:
            return None

    def _askquestion(*_args: object, **_kwargs: object) -> str:
        return "yes"

    dummy_messagebox = types.SimpleNamespace(askquestion=_askquestion)

    monkeypatch.setattr(ui, "_tkinter_available", True)
    monkeypatch.setattr(ui, "tk", types.SimpleNamespace(Tk=_DummyTk))
    monkeypatch.setattr(ui, "messagebox", dummy_messagebox)

    assert ui.prompt_source_selection() == "clipboard"
