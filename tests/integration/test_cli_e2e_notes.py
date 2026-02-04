"""End-to-end CLI tests for notes workflows (in-memory)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pytest

import transcript_etl_pipeline.cli as cli
from tests.fixtures.multi_speaker import SPACEX_DISCUSSION
from transcript_etl_pipeline.document.model import (
    Document,
    DocumentSection,
    Label,
    Paragraph,
    SectionType,
)


def list_documents() -> list[Document]:
    """Create a new list of documents."""
    return []


def list_strings() -> list[str]:
    """Create a new list of strings."""
    return []


def list_paths() -> list[Path]:
    """Create a new list of paths."""
    return []


def list_file_contents() -> dict[str, str]:
    """Create a new file contents mapping."""
    return {}


def noop(*_args: object, **_kwargs: object) -> None:
    """No-op stub for monkeypatched functions."""
    return None


def _document_text(document: Document) -> str:
    text_parts: list[str] = []
    for section in document.sections:  # type: ignore[attr-defined]
        for paragraph in section.paragraphs:
            if paragraph.label is not None:
                text_parts.append(paragraph.label.text)
            if paragraph.text:
                text_parts.append(paragraph.text)
    return " ".join(text_parts)


def _make_notes_document(header: str, body_lines: list[str]) -> Document:
    document = Document()
    header_section = DocumentSection(section_type=SectionType.NOTES_HEADER)
    header_section.add_paragraph(Paragraph(text=header, section_type=SectionType.NOTES_HEADER))
    document.add_section(header_section)

    body_section = DocumentSection(section_type=SectionType.NOTES_BODY)
    for line in body_lines:
        body_section.add_paragraph(
            Paragraph(text=line, section_type=SectionType.NOTES_BODY, is_bullet=True)
        )
    document.add_section(body_section)
    return document


def _make_transcript_document(speaker: str, text: str) -> Document:
    document = Document()
    section = DocumentSection(section_type=SectionType.SPEAKER_PARAGRAPH)
    section.add_paragraph(
        Paragraph(
            label=Label(f"{speaker}:", is_speaker=True),
            text=text,
            section_type=SectionType.SPEAKER_PARAGRAPH,
        )
    )
    document.add_section(section)
    return document


@dataclass
class CliCapture:
    """Capture data from CLI stubs."""

    file_contents: dict[str, str] = field(default_factory=list_file_contents)
    saved_documents: list[Document] = field(default_factory=list_documents)
    saved_formats: list[str] = field(default_factory=list_strings)
    saved_paths: list[Path] = field(default_factory=list_paths)
    read_paths: list[str] = field(default_factory=list_strings)
    path_exists: bool | Callable[[Path], bool] = True
    existing_document: Document | None = None


@pytest.fixture()
def cli_mocks(monkeypatch: pytest.MonkeyPatch) -> CliCapture:
    """Shared CLI stubs for in-memory execution."""
    captured = CliCapture()

    def fake_save_document(document: Document, output_format: str, output_path: Path) -> None:
        captured.saved_documents.append(document)
        captured.saved_formats.append(output_format)
        captured.saved_paths.append(output_path)

    def fake_extract_text(_source: str, file_path: str | None) -> str:
        if file_path is None:
            return ""
        return captured.file_contents.get(file_path, "")

    def fake_read_document(_path: str) -> Document:
        captured.read_paths.append(_path)
        return captured.existing_document or Document()

    def fake_exists(path: Path) -> bool:
        path_exists = captured.path_exists
        if isinstance(path_exists, Callable):
            return path_exists(path)
        return bool(path_exists)

    monkeypatch.setattr(cli, "setup_logging", noop)
    monkeypatch.setattr(cli.config, "save_last_output_folder", noop)
    monkeypatch.setattr(cli, "_save_document", fake_save_document)
    monkeypatch.setattr(cli, "_extract_text", fake_extract_text)
    monkeypatch.setattr(cli, "read_document", fake_read_document)
    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(Path, "is_dir", fake_exists)

    return captured


def run_cli(
    cli_state: CliCapture,
    args: list[str],
    *,
    file_contents: dict[str, str] | None = None,
    existing_document: Document | None = None,
    path_exists: bool | Callable[[Path], bool] = True,
) -> tuple[int, CliCapture]:
    """Run the CLI with in-memory stubs."""
    cli_state.file_contents = file_contents or {}
    cli_state.existing_document = existing_document
    cli_state.path_exists = path_exists
    cli_state.saved_documents.clear()
    cli_state.saved_formats.clear()
    cli_state.saved_paths.clear()
    cli_state.read_paths.clear()

    exit_code = cli.main(args)
    return exit_code, cli_state


class TestCLINotesOnly:
    """Test CLI with notes-only workflows."""

    def test_notes_only_markdown(self, cli_mocks: CliCapture) -> None:
        """Test CLI creating Markdown document with notes only."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--notes-source",
                "file",
                "--notes-file",
                "notes.md",
                "--notes-label",
                "Meeting Notes – 2025-01-10",
                "--format",
                "md",
                "--output-name",
                "notes_output.md",
                "--output-folder",
                "/output",
            ],
            file_contents={
                "notes.md": (
                    "- Action item: Review Q4 results\n"
                    "- Decision: Approve budget increase\n"
                    "- Next meeting: January 15th\n"
                )
            },
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]

        content = _document_text(captured.saved_documents[0])
        assert "Meeting Notes – 2025-01-10" in content
        assert "Action item: Review Q4 results" in content
        assert "Decision: Approve budget increase" in content

    def test_notes_only_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI creating DOCX document with notes only."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--notes-source",
                "file",
                "--notes-file",
                "notes.txt",
                "--notes-label",
                "Project Notes",
                "--format",
                "docx",
                "--output-name",
                "notes_output.docx",
                "--output-folder",
                "/output",
            ],
            file_contents={
                "notes.txt": (
                    "Summary paragraph with important details.\n\n"
                    "* Key point one\n"
                    "* Key point two\n"
                    "* Key point three\n"
                )
            },
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]

        content = _document_text(captured.saved_documents[0])
        assert "Project Notes" in content
        assert "Key point one" in content

    def test_notes_only_rtf(self, cli_mocks: CliCapture) -> None:
        """Test CLI creating RTF document with notes only."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--notes-source",
                "file",
                "--notes-file",
                "notes.txt",
                "--notes-label",
                "Meeting Summary",
                "--format",
                "rtf",
                "--output-name",
                "notes_output.rtf",
                "--output-folder",
                "/output",
            ],
            file_contents={"notes.txt": "- Important decision made\n- Follow-up required\n"},
        )

        assert exit_code == 0
        assert captured.saved_formats == ["rtf"]

        content = _document_text(captured.saved_documents[0])
        assert "Meeting Summary" in content


class TestCLINotesAndTranscript:
    """Test CLI with combined notes and transcript workflows."""

    def test_notes_and_transcript_markdown(self, cli_mocks: CliCapture) -> None:
        """Test CLI creating document with both notes and transcript."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--source",
                "file",
                "--file",
                "transcript.txt",
                "--num-speakers",
                "3",
                "--notes-source",
                "file",
                "--notes-file",
                "notes.md",
                "--notes-label",
                "Discussion Notes",
                "--format",
                "md",
                "--output-name",
                "combined_output.md",
                "--output-folder",
                "/output",
            ],
            file_contents={
                "notes.md": "- Discussed SpaceX launch\n- Team excited about landing\n",
                "transcript.txt": SPACEX_DISCUSSION.input_text,
            },
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]

        content = _document_text(captured.saved_documents[0])
        assert "Discussion Notes" in content
        assert "Discussed SpaceX launch" in content
        assert "Speaker" in content

    def test_notes_and_transcript_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI creating DOCX with both notes and transcript."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--source",
                "file",
                "--file",
                "transcript.txt",
                "--num-speakers",
                "2",
                "--notes-source",
                "file",
                "--notes-file",
                "notes.txt",
                "--notes-label",
                "Quick Notes",
                "--format",
                "docx",
                "--output-name",
                "combined_output.docx",
                "--output-folder",
                "/output",
            ],
            file_contents={
                "notes.txt": "- Meeting overview\n",
                "transcript.txt": "Welcome everyone. Thank you for joining. Let's get started.\n",
            },
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]

        content = _document_text(captured.saved_documents[0])
        assert "Quick Notes" in content
        assert "Speaker" in content


class TestCLIUpdateModeNotes:
    """Test CLI update mode for adding/replacing notes."""

    def test_add_notes_to_existing_markdown(self, cli_mocks: CliCapture) -> None:
        """Test CLI adding notes to existing Markdown document."""
        existing_document = _make_notes_document("Initial Notes", ["Initial note"])
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "initial.md",
                "--update-action",
                "add-notes",
                "--notes-source",
                "file",
                "--notes-file",
                "notes.md",
                "--notes-label",
                "Additional Notes",
                "--format",
                "md",
                "--output-name",
                "final.md",
                "--output-folder",
                "/output",
            ],
            existing_document=existing_document,
            file_contents={"notes.md": "- Added note\n"},
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]

        content = _document_text(captured.saved_documents[0])
        assert "Additional Notes" in content
        assert "Added note" in content
        assert "Initial Notes" in content

    def test_replace_notes_in_existing_docx(self, cli_mocks: CliCapture) -> None:
        """Test CLI replacing notes in existing DOCX document."""
        existing_document = _make_notes_document("Old Notes", ["Old note content"])
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "initial.docx",
                "--update-action",
                "replace-notes",
                "--notes-source",
                "file",
                "--notes-file",
                "new_notes.txt",
                "--notes-label",
                "New Notes",
                "--format",
                "docx",
                "--output-name",
                "final.docx",
                "--output-folder",
                "/output",
            ],
            existing_document=existing_document,
            file_contents={"new_notes.txt": "- New note content\n"},
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]

        content = _document_text(captured.saved_documents[0])
        assert "New Notes" in content
        assert "New note content" in content
        assert "Old note content" not in content


class TestCLIUpdateModeTranscript:
    """Test CLI update mode for adding/replacing transcript."""

    def test_add_transcript_to_existing_notes(self, cli_mocks: CliCapture) -> None:
        """Test CLI adding transcript to document with notes only."""
        existing_document = _make_notes_document("Notes", ["Meeting notes"])
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "initial.md",
                "--update-action",
                "add-transcript",
                "--source",
                "file",
                "--file",
                "transcript.txt",
                "--num-speakers",
                "2",
                "--format",
                "md",
                "--output-name",
                "final.md",
                "--output-folder",
                "/output",
            ],
            existing_document=existing_document,
            file_contents={
                "transcript.txt": "New transcript content here. Added later for testing.\n"
            },
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]

        content = _document_text(captured.saved_documents[0])
        assert "Notes" in content
        assert "Speaker" in content

    def test_replace_transcript_in_existing_document(self, cli_mocks: CliCapture) -> None:
        """Test CLI replacing transcript in existing document."""
        existing_document = _make_transcript_document("Speaker A", "Old content.")
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "initial.md",
                "--update-action",
                "replace-transcript",
                "--source",
                "file",
                "--file",
                "new_transcript.txt",
                "--format",
                "md",
                "--output-name",
                "final.md",
                "--output-folder",
                "/output",
            ],
            existing_document=existing_document,
            file_contents={"new_transcript.txt": "Speaker B: New content.\n"},
        )

        assert exit_code == 0
        assert captured.saved_formats == ["md"]

        content = _document_text(captured.saved_documents[0])
        assert "New content" in content
        assert "Old content" not in content


class TestCLIUpdateModeDOCX:
    """Test CLI update mode with DOCX format."""

    def test_add_notes_to_docx_document(self, cli_mocks: CliCapture) -> None:
        """Test CLI adding notes to existing DOCX document."""
        existing_document = _make_notes_document("Initial Notes", ["Initial content"])
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "initial.docx",
                "--update-action",
                "add-notes",
                "--notes-source",
                "file",
                "--notes-file",
                "notes.txt",
                "--notes-label",
                "Additional DOCX Notes",
                "--format",
                "docx",
                "--output-name",
                "final.docx",
                "--output-folder",
                "/output",
            ],
            existing_document=existing_document,
            file_contents={"notes.txt": "- DOCX note added\n"},
        )

        assert exit_code == 0
        assert captured.saved_formats == ["docx"]

        content = _document_text(captured.saved_documents[0])
        assert "DOCX note added" in content

    def test_docx_reader_path(self, cli_mocks: CliCapture) -> None:
        """Test CLI update mode reads from the provided DOCX update path."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "docx_reader_path.docx",
                "--update-action",
                "add-notes",
                "--notes-source",
                "file",
                "--notes-file",
                "notes.txt",
                "--notes-label",
                "DOCX Reader Path Notes",
                "--format",
                "docx",
                "--output-name",
                "final.docx",
                "--output-folder",
                "/output",
            ],
            file_contents={"notes.txt": "- Note added via update\n"},
        )

        assert exit_code == 0
        assert captured.read_paths == ["docx_reader_path.docx"]
        assert captured.saved_formats == ["docx"]

        content = _document_text(captured.saved_documents[0])
        assert "DOCX Reader Path Notes" in content
        assert "Note added via update" in content


class TestCLINotesErrorHandling:
    """Test CLI error handling for notes workflows."""

    def test_update_mode_missing_update_file(self, cli_mocks: CliCapture) -> None:
        """Test CLI handles missing update file gracefully."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "missing.md",
                "--update-action",
                "add-notes",
                "--notes-source",
                "file",
                "--notes-file",
                "notes.txt",
                "--format",
                "md",
                "--output-name",
                "output.md",
                "--output-folder",
                "/output",
            ],
            file_contents={"notes.txt": "- Note\n"},
            path_exists=lambda path: path.name != "missing.md",
        )

        assert exit_code != 0
        assert captured.saved_documents == []

    def test_update_mode_missing_notes_file(self, cli_mocks: CliCapture) -> None:
        """Test CLI handles missing notes file gracefully."""
        exit_code, captured = run_cli(
            cli_mocks,
            [
                "--mode",
                "update",
                "--update-file",
                "initial.md",
                "--update-action",
                "add-notes",
                "--notes-source",
                "file",
                "--notes-file",
                "missing.txt",
                "--format",
                "md",
                "--output-name",
                "output.md",
                "--output-folder",
                "/output",
            ],
            file_contents={"initial.md": "# Initial"},
            path_exists=lambda path: path.name not in {"missing.txt"},
        )

        assert exit_code != 0
        assert captured.saved_documents == []
