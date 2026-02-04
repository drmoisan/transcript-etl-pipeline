"""End-to-end CLI tests for speakerless transcript workflows (in-memory)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pytest

import transcript_etl_pipeline.cli as cli
from tests.fixtures.multi_speaker import (
    GENERIC_MEETING_3SPEAKER,
    PANEL_DISCUSSION_4SPEAKER,
    SPACEX_DISCUSSION,
    TEAM_STANDUP_3SPEAKER,
)
from transcript_etl_pipeline.document.model import Document


def list_documents() -> list[Document]:
    """Create a new list of documents."""
    return []


def list_strings() -> list[str]:
    """Create a new list of strings."""
    return []


def list_paths() -> list[Path]:
    """Create a new list of paths."""
    return []


def noop(*_args: object, **_kwargs: object) -> None:
    """No-op stub for monkeypatched functions."""
    return None


def _document_text(document: Document) -> str:
    text_parts: list[str] = []
    for section in document.sections:  # type: ignore[attr-defined]
        for paragraph in section.paragraphs:
            text_parts.append(paragraph.text)
            if paragraph.label is not None:
                text_parts.append(paragraph.label.text)
    return " ".join(part for part in text_parts if part)


@dataclass
class CliCapture:
    """Capture data from CLI stubs."""

    input_text: str = ""
    saved_documents: list[Document] = field(default_factory=list_documents)
    saved_formats: list[str] = field(default_factory=list_strings)
    saved_paths: list[Path] = field(default_factory=list_paths)
    path_exists: bool | Callable[[Path], bool] = True


@pytest.fixture()
def cli_mocks(monkeypatch: pytest.MonkeyPatch) -> CliCapture:
    """Shared CLI stubs for in-memory execution."""
    captured = CliCapture()

    def fake_save_document(document: Document, output_format: str, output_path: Path) -> None:
        captured.saved_documents.append(document)
        captured.saved_formats.append(output_format)
        captured.saved_paths.append(output_path)

    def fake_extract_text(_source: str, _file_path: str | None) -> str:
        return captured.input_text

    def fake_exists(path: Path) -> bool:
        path_exists = captured.path_exists
        if isinstance(path_exists, Callable):
            return path_exists(path)
        return bool(path_exists)

    monkeypatch.setattr(cli, "setup_logging", noop)
    monkeypatch.setattr(cli.config, "save_last_output_folder", noop)
    monkeypatch.setattr(cli, "_save_document", fake_save_document)
    monkeypatch.setattr(cli, "_extract_text", fake_extract_text)
    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(Path, "is_dir", fake_exists)

    return captured


def run_cli(
    cli_state: CliCapture,
    input_text: str,
    args: list[str],
    *,
    path_exists: bool | Callable[[Path], bool] = True,
) -> tuple[int, CliCapture]:
    """Run the CLI with in-memory stubs."""
    cli_state.input_text = input_text
    cli_state.path_exists = path_exists
    cli_state.saved_documents.clear()
    cli_state.saved_formats.clear()
    cli_state.saved_paths.clear()

    exit_code = cli.main(args)
    return exit_code, cli_state


class TestCLISpeakerless3SpeakersDOCX:
    """Test CLI with 3-speaker speakerless transcripts - DOCX output."""

    def test_spacex_discussion_3speakers_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI with SpaceX discussion producing DOCX output."""
        exit_code, captured = run_cli(
            cli_mocks,
            SPACEX_DISCUSSION.input_text,
            [
                "--source",
                "file",
                "--file",
                "spacex_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "docx",
                "--output-name",
                "spacex_output.docx",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]
        assert "Speaker" in _document_text(captured.saved_documents[0])

    def test_generic_meeting_3speakers_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI with generic meeting transcript producing DOCX."""
        exit_code, captured = run_cli(
            cli_mocks,
            GENERIC_MEETING_3SPEAKER.input_text,
            [
                "--source",
                "file",
                "--file",
                "meeting_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "docx",
                "--output-name",
                "meeting_output.docx",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]
        assert "Speaker" in _document_text(captured.saved_documents[0])

    def test_team_standup_3speakers_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI with team standup transcript producing DOCX."""
        exit_code, captured = run_cli(
            cli_mocks,
            TEAM_STANDUP_3SPEAKER.input_text,
            [
                "--source",
                "file",
                "--file",
                "standup_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "docx",
                "--output-name",
                "standup_output.docx",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]
        assert "Speaker" in _document_text(captured.saved_documents[0])

    def test_panel_discussion_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI with panel discussion transcript producing DOCX output."""
        exit_code, captured = run_cli(
            cli_mocks,
            PANEL_DISCUSSION_4SPEAKER.input_text,
            [
                "--source",
                "file",
                "--file",
                "panel_input.txt",
                "--num-speakers",
                "4",
                "--format",
                "docx",
                "--output-name",
                "panel_output.docx",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]
        assert "Speaker" in _document_text(captured.saved_documents[0])


class TestCLISpeakerlessMarkdown:
    """Test CLI with speakerless transcripts - Markdown output."""

    def test_spacex_discussion_3speakers_md(self, cli_mocks: CliCapture) -> None:
        """Test CLI with SpaceX discussion producing Markdown output."""
        exit_code, captured = run_cli(
            cli_mocks,
            SPACEX_DISCUSSION.input_text,
            [
                "--source",
                "file",
                "--file",
                "spacex_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "md",
                "--output-name",
                "spacex_output.md",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]

    def test_generic_meeting_md(self, cli_mocks: CliCapture) -> None:
        """Test CLI with generic meeting transcript producing Markdown output."""
        exit_code, captured = run_cli(
            cli_mocks,
            GENERIC_MEETING_3SPEAKER.input_text,
            [
                "--source",
                "file",
                "--file",
                "meeting_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "md",
                "--output-name",
                "meeting_output.md",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]


class TestCLISpeakerlessRTF:
    """Test CLI with speakerless transcripts - RTF output."""

    def test_panel_discussion_4speakers_rtf(self, cli_mocks: CliCapture) -> None:
        """Test CLI with panel discussion producing RTF output."""
        exit_code, captured = run_cli(
            cli_mocks,
            PANEL_DISCUSSION_4SPEAKER.input_text,
            [
                "--source",
                "file",
                "--file",
                "panel_input.txt",
                "--num-speakers",
                "4",
                "--format",
                "rtf",
                "--output-name",
                "panel_output.rtf",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["rtf"]

    def test_spacex_rtf(self, cli_mocks: CliCapture) -> None:
        """Test CLI with SpaceX discussion producing RTF output."""
        exit_code, captured = run_cli(
            cli_mocks,
            SPACEX_DISCUSSION.input_text,
            [
                "--source",
                "file",
                "--file",
                "spacex_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "rtf",
                "--output-name",
                "spacex_output.rtf",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["rtf"]

    def test_team_standup_rtf(self, cli_mocks: CliCapture) -> None:
        """Test CLI with team standup transcript producing RTF output."""
        exit_code, captured = run_cli(
            cli_mocks,
            TEAM_STANDUP_3SPEAKER.input_text,
            [
                "--source",
                "file",
                "--file",
                "standup_input.txt",
                "--num-speakers",
                "3",
                "--format",
                "rtf",
                "--output-name",
                "standup_output.rtf",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert captured.saved_formats == ["rtf"]


class TestCLISpeakerlessAutoDetect:
    """Test CLI speakerless detection without explicit num-speakers."""

    def test_auto_detect_3speakers(self, cli_mocks: CliCapture) -> None:
        """Test CLI auto-detects speakers without --num-speakers flag."""
        exit_code, captured = run_cli(
            cli_mocks,
            SPACEX_DISCUSSION.input_text,
            [
                "--source",
                "file",
                "--file",
                "spacex_input.txt",
                "--format",
                "md",
                "--output-name",
                "spacex_auto.md",
                "--output-folder",
                "/output",
            ],
        )

        assert exit_code == 0
        assert "Speaker" in _document_text(captured.saved_documents[0])


class TestCLIErrorHandling:
    """Test CLI error handling for invalid inputs."""

    def test_missing_input_file(self, cli_mocks: CliCapture) -> None:
        """Missing input file returns non-zero exit code."""

        def path_exists(path: Path) -> bool:
            return path.name != "missing.txt"

        exit_code, _captured = run_cli(
            cli_mocks,
            "Unused",
            [
                "--source",
                "file",
                "--file",
                "missing.txt",
                "--format",
                "md",
                "--output-name",
                "output.md",
                "--output-folder",
                "/output",
            ],
            path_exists=path_exists,
        )

        assert exit_code != 0

    def test_invalid_format(self, cli_mocks: CliCapture) -> None:
        """Invalid format raises SystemExit."""
        with pytest.raises(SystemExit):
            run_cli(
                cli_mocks,
                "Test content",
                [
                    "--source",
                    "file",
                    "--file",
                    "input.txt",
                    "--format",
                    "invalid",
                    "--output-name",
                    "output.md",
                    "--output-folder",
                    "/output",
                ],
            )
