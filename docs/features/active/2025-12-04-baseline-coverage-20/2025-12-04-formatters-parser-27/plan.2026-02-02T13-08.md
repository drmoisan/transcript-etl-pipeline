---
title: "2025-12-04-formatters-parser - Plan"
issue: "27"
parent: "none"
owner: "drmoisan"
last_updated: "2026-02-02"
status: "Planned"
status_color: "blue"
version: "0.2"
---

# 2025-12-04-formatters-parser - Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

- **Issue:** [#27](https://github.com/drmoisan/transcript-etl-pipeline/issues/27)
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T23:44:20Z
- **Status:** Planned
- **Version:** 0.2

## Required References

- Copilot Instructions: [`.github/copilot-instructions.md`](../../../../.github/copilot-instructions.md)
- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Coding Standards: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- Developer Tooling: [`docs/developer-tooling.md`](../../../developer-tooling.md)
- Prompt Source: [`docs/features/active/2025-12-04-formatters-parser-27/27-formatters-parser.prompt.md`](./27-formatters-parser.prompt.md)

**All work must comply with these policies; do not duplicate their content here.**

## Requirements Traceability

| REQ-ID | Description | Source |
| --- | --- | --- |
| REQ-1 | Add deterministic unit tests for `docx`, `rtf`, `md` formatters and `document/parser.py` validating spacing/label rules and parsing behavior. | `27-formatters-parser.prompt.md` |
| REQ-2 | Avoid filesystem/temp-file usage in tests; rely on in-memory structures and stubs only. | `general-unit-test.instructions.md` |
| REQ-3 | Raise coverage for formatter modules and `document/parser.py` to approximately 70% or higher and capture evidence. | `27-formatters-parser.prompt.md` |
| REQ-4 | Update Issue #27 with PR/test links, scenarios, and coverage evidence. | `27-formatters-parser.prompt.md` |

## Task Index

| TASK-ID | Phase/Task | Summary |
| --- | --- | --- |
| TASK-1 | P1-T1 | Add docx formatter test fakes for paragraphs/runs in `tests/formatters/test_docx_formatter.py`. |
| TASK-2 | P1-T2 | Replace file-based DOCX tests with in-memory `docx_formatter` helper tests. |
| TASK-3 | P1-T3 | Add docx test for notes header heading-level style mapping. |
| TASK-4 | P1-T4 | Add docx test for notes bullet level-2 list style mapping. |
| TASK-5 | P1-T5 | Add docx test for spacing rule application in `_apply_spacing`. |
| TASK-6 | P2-T1 | Replace file-based RTF tests with `_generate_rtf`/`_format_paragraph` tests. |
| TASK-7 | P2-T2 | Add RTF test for label bold wrapper and body escape in `_format_paragraph`. |
| TASK-8 | P2-T3 | Add RTF test for `_escape_rtf` newline handling. |
| TASK-9 | P3-T1 | Replace file-based Markdown tests with `_generate_markdown`/`_format_paragraph` tests. |
| TASK-10 | P3-T2 | Add Markdown test for notes header spacing and heading prefix. |
| TASK-11 | P3-T3 | Add Markdown test for label bolding and transcript spacing rules. |
| TASK-12 | P4-T1 | Add parser test for transcript label with inline body text. |
| TASK-13 | P4-T2 | Add parser test for unlabeled transcript lines in speaker section. |
| TASK-14 | P4-T3 | Add parser test for metadata label classification of meeting-title variants. |
| TASK-15 | P5-T1 | Run coverage evidence for formatter/parser modules and record results. |
| TASK-16 | P5-T2 | Update Issue #27 with PR/test links and coverage evidence. |
| TASK-17 | P5-T3 | Update `27-formatters-parser.prompt.md` with edge cases and outcomes. |

## Implementation Plan (Atomic Tasks)

### Phase 0 — Context & Inputs
- [ ] [P0-T1] Read `.github/copilot-instructions.md` to establish baseline agent rules.
  - Acceptance: `powershell -Command "Test-Path .github/copilot-instructions.md"` exits with code 0.
- [ ] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm workflow requirements.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-code-change.instructions.md"` exits with code 0.
- [ ] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm unit-test policy.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-unit-test.instructions.md"` exits with code 0.
- [ ] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` for Python rules.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-code-change.instructions.md"` exits with code 0.
- [ ] [P0-T5] Read `.github/instructions/python-unit-test.instructions.md` for Pytest rules.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-unit-test.instructions.md"` exits with code 0.
- [ ] [P0-T6] Read `docs/features/active/2025-12-04-formatters-parser-27/27-formatters-parser.prompt.md` for scope and acceptance criteria.
  - Acceptance: `powershell -Command "Test-Path docs/features/active/2025-12-04-formatters-parser-27/27-formatters-parser.prompt.md"` exits with code 0.
- [ ] [P0-T7] Capture baseline formatter output with `poetry run black .` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T8] Capture baseline lint output with `poetry run ruff check` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T9] Capture baseline type-check output with `poetry run pyright` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T10] Capture baseline test output with `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html`.
  - Acceptance: Command exits with code 0.

### Phase 1 — DOCX Formatter Tests (`tests/formatters/test_docx_formatter.py`)
- [x] [P1-T1] TASK-1 Add lightweight fake classes (`FakeDocxDocument`, `FakeDocxParagraph`, `FakeDocxRun`, `FakeParagraphFormat`) in `tests/formatters/test_docx_formatter.py` to capture `add_paragraph`, `add_run`, and spacing/font assignments without touching the filesystem (REQ-1, REQ-2).
  - Acceptance: `Select-String -Path tests/formatters/test_docx_formatter.py -Pattern 'class FakeDocxDocument|class FakeDocxParagraph|class FakeDocxRun|class FakeParagraphFormat'` returns matches.
- [x] [P1-T2] TASK-2 Replace file-based `format_to_docx` tests with in-memory tests that call `_format_paragraph`, `_apply_spacing`, and `_apply_font` using the fake classes; remove all `tmp_path` usage and direct `DocxDocument` reads (REQ-1, REQ-2).
  - Acceptance: `Select-String -Path tests/formatters/test_docx_formatter.py -Pattern 'tmp_path|DocxDocument\('` returns no matches.
- [x] [P1-T3] TASK-3 Add docx test `test_format_paragraph_notes_header_heading_level` that calls `_format_paragraph` with `SectionType.NOTES_HEADER` and `Paragraph(heading_level=3)` and asserts the fake paragraph style equals `HEADING_STYLES[3]` (`Heading 3`).
  - Acceptance: `Select-String -Path tests/formatters/test_docx_formatter.py -Pattern 'notes_header_heading_level'` returns a match and the test asserts `Heading 3`.
- [x] [P1-T4] TASK-4 Add docx test `test_format_paragraph_notes_body_bullet_level_two` that calls `_format_paragraph` with `SectionType.NOTES_BODY` and `Paragraph(is_bullet=True, bullet_level=2)` and asserts `List Bullet 2` is used.
  - Acceptance: `Select-String -Path tests/formatters/test_docx_formatter.py -Pattern 'notes_body_bullet_level_two'` returns a match and the test asserts `List Bullet 2`.
- [x] [P1-T5] TASK-5 Add docx test `test_apply_spacing_sets_before_after_and_single_spacing` that calls `_apply_spacing` with `SpacingRule(before_pt=12.0, after_pt=0.0, line_spacing=1.0)` and asserts `space_before`, `space_after`, and `line_spacing_rule` are set on the fake paragraph format.
  - Acceptance: `Select-String -Path tests/formatters/test_docx_formatter.py -Pattern 'apply_spacing_sets_before_after_and_single_spacing'` returns a match and the test asserts `space_before == 12` and `space_after == 0`.

### Phase 2 — RTF Formatter Tests (`tests/formatters/test_rtf_formatter.py`)
- [x] [P2-T1] TASK-6 Replace file-based RTF tests with unit tests for `_generate_rtf`, `_format_paragraph`, and `_escape_rtf` in `tests/formatters/test_rtf_formatter.py`; remove all `tempfile` and `Path(...).unlink()` usage (REQ-1, REQ-2).
  - Acceptance: `Select-String -Path tests/formatters/test_rtf_formatter.py -Pattern 'tempfile|NamedTemporaryFile|unlink'` returns no matches.
- [x] [P2-T2] TASK-7 Add RTF test `test_format_paragraph_speaker_label_bold_and_body_text` that calls `_format_paragraph` with `SectionType.SPEAKER_PARAGRAPH` and `Label("Speaker:")` and asserts the returned RTF contains `{"\\b Speaker: "}` and the escaped body text.
  - Acceptance: `Select-String -Path tests/formatters/test_rtf_formatter.py -Pattern 'speaker_label_bold_and_body_text'` returns a match and asserts the bold wrapper.
- [x] [P2-T3] TASK-8 Add RTF test `test_escape_rtf_converts_newlines_to_par` that calls `_escape_rtf("Line1\nLine2")` and asserts it returns `"Line1\\par Line2"`.
  - Acceptance: `Select-String -Path tests/formatters/test_rtf_formatter.py -Pattern 'escape_rtf_converts_newlines_to_par'` returns a match and asserts exact output.

### Phase 3 — Markdown Formatter Tests (`tests/formatters/test_md_formatter.py`)
- [x] [P3-T1] TASK-9 Replace file-based Markdown tests with unit tests for `_generate_markdown` and `_format_paragraph` in `tests/formatters/test_md_formatter.py`; remove all `tempfile` and `Path(...).unlink()` usage (REQ-1, REQ-2).
  - Acceptance: `Select-String -Path tests/formatters/test_md_formatter.py -Pattern 'tempfile|NamedTemporaryFile|unlink'` returns no matches.
- [x] [P3-T2] TASK-10 Add Markdown test `test_notes_header_inserts_blank_line_and_heading_prefix` that calls `_format_paragraph` with `SectionType.NOTES_HEADER` and `is_first=False`, asserting a leading blank line and `# {text}` output.
  - Acceptance: `Select-String -Path tests/formatters/test_md_formatter.py -Pattern 'notes_header_inserts_blank_line'` returns a match and asserts `""` then `"# "`.
- [x] [P3-T3] TASK-11 Add Markdown test `test_transcript_label_gets_blank_line_before_when_not_first` that uses `_format_paragraph` with `SectionType.REGULAR_PARAGRAPH`, `Label("Transcript:")`, `is_first=False`, and asserts a blank line precedes `**Transcript:**` output.
  - Acceptance: `Select-String -Path tests/formatters/test_md_formatter.py -Pattern 'transcript_label_gets_blank_line'` returns a match and asserts the blank-line rule.

### Phase 4 — Parser Tests (`tests/document/test_parser_unit.py`)
- [x] [P4-T1] TASK-12 Add parser test `test_transcript_label_inline_text_is_preserved` that passes `"Transcript: Intro text\r\nSpeaker A: More"` to `parse_enhanced_text` and asserts the transcript section paragraph text starts with `"Intro text"` and includes subsequent lines joined by spaces (REQ-1).
  - Acceptance: `Select-String -Path tests/document/test_parser_unit.py -Pattern 'transcript_label_inline_text_is_preserved'` returns a match and asserts expected paragraph text.
- [x] [P4-T2] TASK-13 Add parser test `test_unlabeled_transcript_lines_create_regular_paragraphs` that provides transcript lines without labels after a labeled speaker and asserts those lines are appended to the current paragraph rather than creating new labeled paragraphs (REQ-1).
  - Acceptance: `Select-String -Path tests/document/test_parser_unit.py -Pattern 'unlabeled_transcript_lines_create_regular_paragraphs'` returns a match and asserts paragraph count remains 1.
- [x] [P4-T3] TASK-14 Add parser test `test_is_metadata_label_accepts_meeting_title_variants` that calls `is_metadata_label("meeting title")` and `is_metadata_label("Meeting Title")` and asserts `True` for both, while `"Meeting Title:"` remains `False` (REQ-1).
  - Acceptance: `Select-String -Path tests/document/test_parser_unit.py -Pattern 'metadata_label_accepts_meeting_title_variants'` returns a match and asserts expected booleans.

### Phase 5 — Coverage Evidence and Issue Updates
- [x] [P5-T1] TASK-15 Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` followed by `poetry run coverage report --include=src/transcript_etl_pipeline/formatters/docx_formatter.py,src/transcript_etl_pipeline/formatters/rtf_formatter.py,src/transcript_etl_pipeline/formatters/md_formatter.py,src/transcript_etl_pipeline/document/parser.py --fail-under=70` and capture the output (REQ-3).
  - Acceptance: The `coverage report --fail-under=70` command exits with code 0.
- [x] [P5-T2] TASK-16 Update Issue #27 with PR/test links and coverage evidence (REQ-4).
  - Acceptance: `gh issue view 27 --json body -q ".body"` output contains a PR URL matching `https://github.com/drmoisan/transcript-etl-pipeline/pull/` and mentions `coverage report --fail-under=70`.
- [x] [P5-T3] TASK-17 Update `docs/features/active/2025-12-04-formatters-parser-27/27-formatters-parser.prompt.md` with edge cases or outcomes discovered during test authoring.
  - Acceptance: `Select-String -Path docs/features/active/2025-12-04-formatters-parser-27/27-formatters-parser.prompt.md -Pattern 'Edge cases|Outcomes'` returns a match.

### Phase 6 — QA (Python Toolchain)
- [x] [P6-T1] Run `poetry run black .` and confirm the formatter exits with code 0; if it modifies files or fails, fix issues and restart from [P6-T1].
  - Acceptance: Command exits with code 0 on a pass where no files are modified.
- [x] [P6-T2] Run `poetry run ruff check` and confirm the linter exits with code 0; if it fails, fix issues and restart from [P6-T1].
  - Acceptance: Command exits with code 0.
- [x] [P6-T3] Run `poetry run pyright` and confirm type checking exits with code 0; if it fails, fix issues and restart from [P6-T1].
  - Acceptance: Command exits with code 0.
- [x] [P6-T4] Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and confirm tests exit with code 0; if it fails, fix issues and restart from [P6-T1].
  - Acceptance: Command exits with code 0.

## Test Plan

- Unit: `poetry run pytest tests/formatters/test_docx_formatter.py tests/formatters/test_rtf_formatter.py tests/formatters/test_md_formatter.py tests/document/test_parser_unit.py`.
- Integration: Not applicable (unit-test-only change).
- Manual/CLI: `gh issue view 27 --json body -q ".body"` to confirm Issue #27 update content.

## Open Questions / Notes

- None.
