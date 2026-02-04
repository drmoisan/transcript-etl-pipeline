---
title: "2025-12-04-e2e-speakerless-notes - Plan"
issue: "25"
parent: "none"
owner: "drmoisan"
last_updated: "2026-02-03T13:47:57Z"
status: "Planned"
status_color: "blue"
version: "0.2"
---

# 2025-12-04-e2e-speakerless-notes - Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

- **Issue:** [#25](https://github.com/drmoisan/transcript-etl-pipeline/issues/25)
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-03T13:47:57Z
- **Status:** Planned
- **Version:** 0.2

## Required References

- Copilot Instructions: [`.github/copilot-instructions.md`](../../../../.github/copilot-instructions.md)
- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Coding Standards: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- Developer Tooling: [`docs/developer-tooling.md`](../../../developer-tooling.md)

**All work must comply with these policies; do not duplicate their content here.**

## Requirements Traceability

| REQ-ID | Description | Source |
| --- | --- | --- |
| REQ-1 | Add CLI E2E tests for speakerless flows producing DOCX/MD/RTF outputs without filesystem writes (mocked output) in `tests/integration/`. | `25-e2e-speakerless-notes.prompt.md` |
| REQ-2 | Add CLI E2E tests for notes-only and notes+transcript flows with output validation and update-mode coverage. | `25-e2e-speakerless-notes.prompt.md` |
| REQ-3 | Ensure tests are deterministic, avoid temporary files, and follow unit-test policy. | `25-e2e-speakerless-notes.prompt.md` |
| REQ-4 | Update Issue #25 with PR/test links and scenario notes. | `25-e2e-speakerless-notes.prompt.md` |

## Task Index

| TASK-ID | Phase/Task | Summary |
| --- | --- | --- |
| TASK-1 | P1-T1 | Add shared CLI test helper and fixtures in `tests/integration/test_cli_e2e_speakerless.py`. |
| TASK-2 | P1-T2 | Add DOCX speakerless 3-speaker test for SPACEX_DISCUSSION. |
| TASK-3 | P1-T3 | Add DOCX speakerless 3-speaker test for GENERIC_MEETING_3SPEAKER. |
| TASK-4 | P1-T4 | Add DOCX speakerless 3-speaker test for TEAM_STANDUP_3SPEAKER. |
| TASK-5 | P1-T5 | Add DOCX speakerless 4-speaker test for PANEL_DISCUSSION_4SPEAKER. |
| TASK-6 | P1-T6 | Add MD speakerless test for SPACEX_DISCUSSION. |
| TASK-7 | P1-T7 | Add MD speakerless test for GENERIC_MEETING_3SPEAKER. |
| TASK-8 | P1-T8 | Add RTF speakerless test for SPACEX_DISCUSSION. |
| TASK-9 | P1-T9 | Add RTF speakerless test for TEAM_STANDUP_3SPEAKER. |
| TASK-10 | P1-T10 | Add speakerless auto-detect test without --num-speakers flag. |
| TASK-11 | P1-T11 | Add CLI error tests for missing file and invalid args. |
| TASK-12 | P2-T1 | Add shared CLI test helper and fixtures in `tests/integration/test_cli_e2e_notes.py`. |
| TASK-13 | P2-T2 | Add notes-only DOCX/MD/RTF tests. |
| TASK-14 | P2-T3 | Add notes+transcript DOCX/MD tests. |
| TASK-15 | P2-T4 | Add update-mode notes add/replace tests (MD/DOCX). |
| TASK-16 | P2-T5 | Add update-mode transcript add/replace tests (MD/DOCX). |
| TASK-17 | P2-T6 | Add update-mode DOCX reader test via `read_document` usage. |
| TASK-18 | P2-T7 | Add notes error-handling tests for missing file/invalid args. |
| TASK-19 | P3-T1 | Run coverage and record evidence for cli/reader/notes/formatters. |
| TASK-20 | P3-T2 | Update Issue #25 with links and scenario notes. |
| TASK-21 | P3-T3 | Update `25-e2e-speakerless-notes.prompt.md` with edge cases or runtime notes. |

> **Instructions for this section:**
> - Break work into **Phases** (broad buckets) and **Atomic Tasks** (binary, 5-30 min units).
> - Use `- [ ] [P#-T#]` for every task.
> - Start every task with a **strong verb** (Implement, Create, Update, Verify).
> - No "bucket" tasks like "Refactor module" or "Write tests"; split them into specific, verifiable steps.
> - **Self-Validating Phases:** Include necessary test creation/update tasks *within* the phase that implements the code. Do not defer verification to a final "Testing" phase.

### Phase 0 — Context & Inputs
- [x] [P0-T1] Read `.github/copilot-instructions.md` to establish baseline agent rules.
  - Acceptance: `powershell -Command "Test-Path .github/copilot-instructions.md"` exits with code 0.
- [x] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm workflow requirements.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-code-change.instructions.md"` exits with code 0.
- [x] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm unit-test policy.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-unit-test.instructions.md"` exits with code 0.
- [x] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` for Python rules.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-code-change.instructions.md"` exits with code 0.
- [x] [P0-T5] Read `.github/instructions/python-unit-test.instructions.md` for Pytest rules.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-unit-test.instructions.md"` exits with code 0.
- [x] [P0-T6] Read `docs/features/active/2025-12-04-e2e-speakerless-notes-25/25-e2e-speakerless-notes.prompt.md` for scope and acceptance criteria.
  - Acceptance: `powershell -Command "Test-Path docs/features/active/2025-12-04-e2e-speakerless-notes-25/25-e2e-speakerless-notes.prompt.md"` exits with code 0.
- [ ] [P0-T7] Capture baseline formatter output with `poetry run black .` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T8] Capture baseline lint output with `poetry run ruff check` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T9] Capture baseline type-check output with `poetry run pyright` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T10] Capture baseline test output with `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html`.
  - Acceptance: Command exits with code 0.

### Phase 1 — Speakerless CLI E2E Tests (`tests/integration/test_cli_e2e_speakerless.py`)
- [x] [P1-T1] TASK-1 Create `tests/integration/test_cli_e2e_speakerless.py` with shared fixtures: `SPACEX_DISCUSSION`, `GENERIC_MEETING_3SPEAKER`, `TEAM_STANDUP_3SPEAKER`, `PANEL_DISCUSSION_4SPEAKER`, and a helper `run_cli(args: list[str]) -> int` that calls `transcript_etl_pipeline.cli.main` while monkeypatching `setup_logging`, `config.save_last_output_folder`, and `_save_document` to avoid filesystem writes (REQ-1, REQ-3).
  - Acceptance: `powershell -Command "Test-Path tests/integration/test_cli_e2e_speakerless.py"` exits with code 0 and `Select-String` finds `def run_cli(`, `SPACEX_DISCUSSION`, and `_save_document`.
- [x] [P1-T2] TASK-2 Add `TestCLISpeakerless3SpeakersDOCX.test_spacex_discussion_docx` that runs `main` with `--source file`, `--file artifacts/transcript.txt`, `--num-speakers 3`, `--format docx`, `--output-folder artifacts`, `--output-name spacex_docx` and asserts `_save_document` was called with `output_format == "docx"` and document contains speaker labels.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'spacex_discussion_docx'` returns a match and the test asserts `"Speaker"` in captured document text.
- [x] [P1-T3] TASK-3 Add `TestCLISpeakerless3SpeakersDOCX.test_generic_meeting_docx` using `GENERIC_MEETING_3SPEAKER` with `--num-speakers 3` and asserts `_save_document` receives `output_format == "docx"` and transcript sections are present.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'generic_meeting_docx'` returns a match and the test asserts transcript section count > 0.
- [x] [P1-T4] TASK-4 Add `TestCLISpeakerless3SpeakersDOCX.test_team_standup_docx` using `TEAM_STANDUP_3SPEAKER` with `--num-speakers 3` and asserts `_save_document` called once and includes multiple sections.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'team_standup_docx'` returns a match and the test asserts captured section count >= 2.
- [x] [P1-T5] TASK-5 Add `TestCLISpeakerless4SpeakersDOCX.test_panel_discussion_docx` using `PANEL_DISCUSSION_4SPEAKER` with `--num-speakers 4` and asserts `_save_document` receives a document with at least 4 speaker labels.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'panel_discussion_docx'` returns a match and the test asserts distinct speaker labels count >= 4.
- [x] [P1-T6] TASK-6 Add `TestCLISpeakerlessMarkdown.test_spacex_md` using `SPACEX_DISCUSSION` with `--format md` and assert `_save_document` called with `output_format == "md"`.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'spacex_md'` returns a match and the test asserts `output_format == "md"`.
- [x] [P1-T7] TASK-7 Add `TestCLISpeakerlessMarkdown.test_generic_meeting_md` using `GENERIC_MEETING_3SPEAKER` with `--format md` and assert `_save_document` called once.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'generic_meeting_md'` returns a match and the test asserts `_save_document` call count == 1.
- [x] [P1-T8] TASK-8 Add `TestCLISpeakerlessRTF.test_spacex_rtf` using `SPACEX_DISCUSSION` with `--format rtf` and assert `_save_document` called with `output_format == "rtf"`.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'spacex_rtf'` returns a match and the test asserts `output_format == "rtf"`.
- [x] [P1-T9] TASK-9 Add `TestCLISpeakerlessRTF.test_team_standup_rtf` using `TEAM_STANDUP_3SPEAKER` with `--format rtf` and assert `_save_document` called once.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'team_standup_rtf'` returns a match and the test asserts `_save_document` call count == 1.
- [x] [P1-T10] TASK-10 Add `TestCLISpeakerlessAutoDetect.test_auto_detect_no_num_speakers` that runs with `--source file` and no `--num-speakers` flag and asserts `_save_document` called with a document containing speaker labels.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'auto_detect_no_num_speakers'` returns a match and the test asserts `"Speaker"` in captured document text.
- [x] [P1-T11] TASK-11 Add `TestCLIErrorHandling` with `test_missing_file_returns_error` (nonexistent `--file`) and `test_invalid_args_returns_error` (missing `--output-folder`) asserting `main` returns non-zero exit code.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_speakerless.py -Pattern 'missing_file_returns_error|invalid_args_returns_error'` returns matches and each test asserts `exit_code != 0`.

### Phase 2 — Notes CLI E2E Tests (`tests/integration/test_cli_e2e_notes.py`)
- [x] [P2-T1] TASK-12 Create `tests/integration/test_cli_e2e_notes.py` with shared fixtures `NOTES_ONLY_TEXT`, `NOTES_AND_TRANSCRIPT_TEXT`, `NOTES_UPDATE_TEXT`, and helper `run_cli(args: list[str]) -> int` that monkeypatches `setup_logging`, `config.save_last_output_folder`, `_save_document`, and `read_document` as needed to avoid filesystem writes (REQ-2, REQ-3).
  - Acceptance: `powershell -Command "Test-Path tests/integration/test_cli_e2e_notes.py"` exits with code 0 and `Select-String` finds `NOTES_ONLY_TEXT` and `_save_document`.
- [x] [P2-T2] TASK-13 Add `TestCLINotesOnly` with three tests for DOCX/MD/RTF formats that pass `--notes-source file` and assert `_save_document` called with expected `output_format` per test.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_notes.py -Pattern 'TestCLINotesOnly'` returns a match and each test asserts the expected `output_format`.
- [x] [P2-T3] TASK-14 Add `TestCLINotesAndTranscript` with two tests for DOCX and MD that pass both transcript and notes sources and assert both notes and transcript sections are present in the captured document.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_notes.py -Pattern 'TestCLINotesAndTranscript'` returns a match and each test asserts notes and transcript section types exist.
- [x] [P2-T4] TASK-15 Add `TestCLIUpdateModeNotes` with `add-notes` and `replace-notes` tests that monkeypatch `read_document` to return a `Document` with existing notes and assert resulting document has the correct notes section count.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_notes.py -Pattern 'TestCLIUpdateModeNotes'` returns a match and each test asserts the notes section count matches the action.
- [x] [P2-T5] TASK-16 Add `TestCLIUpdateModeTranscript` with `add-transcript` and `replace-transcript` tests that monkeypatch `read_document` and assert transcript sections are merged or replaced as expected.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_notes.py -Pattern 'TestCLIUpdateModeTranscript'` returns a match and each test asserts transcript section count matches the action.
- [x] [P2-T6] TASK-17 Add `TestCLIUpdateModeDOCX.test_docx_reader_path` that uses a committed fixture path (e.g., `tests/fixtures/sample.docx`) for `--update-file` and asserts `read_document` is invoked and `_save_document` called.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_notes.py -Pattern 'docx_reader_path'` returns a match and the test asserts `read_document` was called.
- [x] [P2-T7] TASK-18 Add `TestCLINotesErrorHandling` with `test_notes_missing_file_returns_error` and `test_invalid_update_args_returns_error` asserting `main` returns non-zero exit codes.
  - Acceptance: `Select-String -Path tests/integration/test_cli_e2e_notes.py -Pattern 'NotesErrorHandling'` returns a match and each test asserts `exit_code != 0`.

### Phase 3 — Coverage Evidence and Issue Updates
- [x] [P3-T1] TASK-19 Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and record coverage for `src/transcript_etl_pipeline/cli.py`, `src/transcript_etl_pipeline/document/reader.py`, `src/transcript_etl_pipeline/extract/from_file.py`, and `src/transcript_etl_pipeline/transform/notes.py` (REQ-2).
  - Acceptance: `coverage.xml` exists and `Select-String -Path coverage.xml -Pattern 'cli.py|reader.py|from_file.py|notes.py'` returns matches.
- [x] [P3-T2] TASK-20 Update Issue #25 with PR/test links and scenario notes (REQ-4).
  - Acceptance: `gh issue view 25 --json body -q ".body"` output contains a PR URL matching `https://github.com/drmoisan/transcript-etl-pipeline/pull/` and mentions "speakerless" and "notes".
- [x] [P3-T3] TASK-21 Update `docs/features/active/2025-12-04-e2e-speakerless-notes-25/25-e2e-speakerless-notes.prompt.md` with any edge cases or runtime/env notes (REQ-3).
  - Acceptance: `Select-String -Path docs/features/active/2025-12-04-e2e-speakerless-notes-25/25-e2e-speakerless-notes.prompt.md -Pattern 'Runtime|Environment|Edge cases'` returns a match.

### Phase 4 — QA (Python Toolchain)
- [ ] [P4-T1] Run `poetry run black .` and confirm the formatter exits with code 0; if it modifies files or fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0 on a pass where no files are modified.
- [ ] [P4-T2] Run `poetry run ruff check` and confirm the linter exits with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.
- [ ] [P4-T3] Run `poetry run pyright` and confirm type checking exits with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.
- [ ] [P4-T4] Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and confirm tests exit with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.

## Test Plan

- Unit: Not applicable (integration CLI tests).
- Integration: `poetry run pytest tests/integration/test_cli_e2e_speakerless.py tests/integration/test_cli_e2e_notes.py`.
- Manual/CLI: `gh issue view 25 --json body -q ".body"` to confirm Issue #25 update content.

## Open Questions / Notes

- None.
