"""Unit tests for CLI helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from transcript_etl_pipeline import cli


def test_generate_default_filename_uses_date(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the default filename uses the provided format."""

    class _FixedDateTime:
        @staticmethod
        def now() -> Any:
            return type("Fixed", (), {"year": 2024, "month": 1, "day": 15})()

    monkeypatch.setattr(cli, "datetime", _FixedDateTime)

    assert cli.generate_default_filename("docx") == "2024 01 15 Transcript.docx"


def test_extract_text_from_clipboard(monkeypatch: pytest.MonkeyPatch) -> None:
    """Extract clipboard text using the helper."""

    def _extract() -> str:
        return "clipboard text"

    monkeypatch.setattr(cli, "extract_from_clipboard", _extract)

    assert (
        cli._extract_text(  # pyright: ignore[reportPrivateUsage]
            "clipboard",
            None,
        )
        == "clipboard text"
    )


def test_extract_text_requires_file_path() -> None:
    """Raise error when file source lacks file path."""
    with pytest.raises(ValueError, match="File path is required"):
        cli._extract_text("file", None)  # pyright: ignore[reportPrivateUsage]


def test_extract_text_invalid_source() -> None:
    """Raise error for invalid source values."""
    with pytest.raises(ValueError, match="Invalid source"):
        cli._extract_text("invalid", None)  # pyright: ignore[reportPrivateUsage]


def test_save_document_dispatches_to_formatter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Dispatch the save operation to the correct formatter."""
    called: dict[str, str] = {}

    def _save_docx(_doc: object, path: str) -> None:
        called.update(docx=path)

    def _save_rtf(_doc: object, path: str) -> None:
        called.update(rtf=path)

    def _save_md(_doc: object, path: str) -> None:
        called.update(md=path)

    monkeypatch.setattr(cli, "format_to_docx", _save_docx)
    monkeypatch.setattr(cli, "format_to_rtf", _save_rtf)
    monkeypatch.setattr(cli, "format_to_md", _save_md)

    from transcript_etl_pipeline.document.model import Document

    dummy_doc = Document()
    cli._save_document(  # pyright: ignore[reportPrivateUsage]
        dummy_doc,
        "docx",
        Path("output.docx"),
    )
    cli._save_document(  # pyright: ignore[reportPrivateUsage]
        dummy_doc,
        "rtf",
        Path("output.rtf"),
    )
    cli._save_document(  # pyright: ignore[reportPrivateUsage]
        dummy_doc,
        "md",
        Path("output.md"),
    )

    assert called["docx"] == "output.docx"
    assert called["rtf"] == "output.rtf"
    assert called["md"] == "output.md"


def test_main_returns_error_for_missing_update_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure update mode validates required arguments."""

    def _setup_logging(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(cli, "setup_logging", _setup_logging)

    result = cli.main(
        [
            "--mode",
            "update",
            "--update-action",
            "add-notes",
            "--output-folder",
            "out",
            "--source",
            "clipboard",
        ]
    )

    assert result == 1
    assert "update-file is required" in capsys.readouterr().out


def test_main_runs_pipeline_with_explicit_args(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure main executes pipeline when arguments are provided."""

    def _setup_logging(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(cli, "setup_logging", _setup_logging)

    calls: dict[str, Any] = {}

    def _run_unified_pipeline(**kwargs: Any) -> None:
        calls.update(kwargs)

    monkeypatch.setattr(cli, "run_unified_pipeline", _run_unified_pipeline)
    monkeypatch.setattr(cli.config, "load_last_output_folder", lambda: None)

    def _exists(self: Path) -> bool:
        return True

    monkeypatch.setattr(Path, "exists", _exists, raising=False)

    def _is_dir(self: Path) -> bool:
        return True

    monkeypatch.setattr(Path, "is_dir", _is_dir, raising=False)

    result = cli.main(
        [
            "--source",
            "file",
            "--file",
            "input.txt",
            "--format",
            "md",
            "--output-name",
            "output",
            "--output-folder",
            "out",
        ]
    )

    assert result == 0
    assert calls["output_format"] == "md"
    assert calls["transcript_file"] == "input.txt"
    assert capsys.readouterr().out == ""
