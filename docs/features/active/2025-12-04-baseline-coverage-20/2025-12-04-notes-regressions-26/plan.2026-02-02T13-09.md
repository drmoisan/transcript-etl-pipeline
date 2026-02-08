---
title: "2025-12-04-notes-regressions - Plan"
issue: "26"
parent: "none"
owner: "drmoisan"
last_updated: "2026-02-02T23:44:20Z"
status: "Completed"
status_color: "green"
version: "1.0"
---

# 2025-12-04-notes-regressions - Plan

![Status: Completed](https://img.shields.io/badge/status-Completed-green)

- **Issue:** [#26](https://github.com/drmoisan/transcript-etl-pipeline/issues/26)
- **Parent (optional):** [#20](https://github.com/drmoisan/transcript-etl-pipeline/issues/20)
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T23:44:20Z
- **Status:** Completed
- **Version:** 1.0

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
| REQ-1 | Add regression tests for notes conversion edge cases in `src/transcript_etl_pipeline/transform/notes.py`. | `26-notes-regressions.prompt.md` |
| REQ-2 | Increase coverage for notes-related paths and capture evidence. | `26-notes-regressions.prompt.md` |
| REQ-3 | Ensure tests are deterministic and avoid filesystem/temp files. | `26-notes-regressions.prompt.md` |
| REQ-4 | Update Issue #26 with PR/test links and outcomes. | `26-notes-regressions.prompt.md` |

## Task Index

| TASK-ID | Phase/Task | Summary |
| --- | --- | --- |
| TASK-1 | P1-T1 | Add regression test for `_clean_markdown_text` removing escaped dollars and bold markers. |
| TASK-2 | P1-T2 | Add regression test for `_parse_bullet_line` indentation levels and bullet text extraction. |
| TASK-3 | P1-T3 | Add regression test for `_get_heading_level` with leading whitespace and heading tokens. |
| TASK-4 | P1-T4 | Add regression test for `transform_notes` adding label after H1 when label is provided. |
| TASK-5 | P1-T5 | Add regression test for `_parse_markdown` preserving order with mixed headers and bullets. |
| TASK-6 | P2-T1 | Run coverage and capture evidence for notes-related paths. |
| TASK-7 | P2-T2 | Update Issue #26 with links and outcomes. |
| TASK-8 | P2-T3 | Update `26-notes-regressions.prompt.md` with edge cases or outcomes. |

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
- [x] [P0-T6] Read `docs/features/active/2025-12-04-notes-regressions-26/26-notes-regressions.prompt.md` for scope and acceptance criteria.
  - Acceptance: `powershell -Command "Test-Path docs/features/active/2025-12-04-notes-regressions-26/26-notes-regressions.prompt.md"` exits with code 0.
- [x] [P0-T7] Capture baseline formatter output with `poetry run black .` from repo root.
  - Acceptance: Command exits with code 0.
- [x] [P0-T8] Capture baseline lint output with `poetry run ruff check` from repo root.
  - Acceptance: Command exits with code 0.
- [x] [P0-T9] Capture baseline type-check output with `poetry run pyright` from repo root.
  - Acceptance: Command exits with code 0.
- [x] [P0-T10] Capture baseline test output with `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html`.
  - Acceptance: Command exits with code 0.

### Phase 1 — Notes Regression Tests (`tests/transform/test_notes.py`)
- [x] [P1-T1] TASK-1 Add a Pytest case in `tests/transform/test_notes.py` that calls `_clean_markdown_text` with input `"\\$100 **bold** __strong__"` and asserts output equals `"$100 bold strong"` (REQ-1, REQ-3).
  - Acceptance: `Select-String -Path tests/transform/test_notes.py -Pattern 'clean_markdown_text'` returns a match and the test asserts the exact cleaned string.
- [x] [P1-T2] TASK-2 Add a Pytest case in `tests/transform/test_notes.py` that calls `_parse_bullet_line` with `"- Item"` and `"  - Nested"` and asserts bullet levels `(1, "Item")` and `(2, "Nested")` (REQ-1, REQ-3).
  - Acceptance: `Select-String -Path tests/transform/test_notes.py -Pattern 'parse_bullet_line'` returns a match and the test asserts exact tuples.
- [x] [P1-T3] TASK-3 Add a Pytest case in `tests/transform/test_notes.py` that calls `_get_heading_level` with `"  ## Heading"` and asserts heading level `2` (REQ-1, REQ-3).
  - Acceptance: `Select-String -Path tests/transform/test_notes.py -Pattern 'get_heading_level'` returns a match and the test asserts `== 2`.
- [x] [P1-T4] TASK-4 Add a Pytest case in `tests/transform/test_notes.py` that calls `transform_notes` with text `"# Title\n\n- Bullet"` and label `"Meeting Notes"` and asserts an H2 notes header uses the provided label (REQ-1, REQ-3).
  - Acceptance: `Select-String -Path tests/transform/test_notes.py -Pattern 'Meeting Notes'` returns a match and the test asserts the H2 header text equals `"Meeting Notes"`.
- [x] [P1-T5] TASK-5 Add a Pytest case in `tests/transform/test_notes.py` that calls `_parse_markdown` with mixed input `"# Title\n- One\n## Section\n- Two"` and asserts paragraph ordering and heading levels are preserved (REQ-1, REQ-3).
  - Acceptance: `Select-String -Path tests/transform/test_notes.py -Pattern 'parse_markdown_mixed'` returns a match and the test asserts the expected sequence of heading levels and bullet flags.

### Phase 2 — Coverage Evidence and Issue Updates
- [x] [P2-T1] TASK-6 Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and capture coverage for `src/transcript_etl_pipeline/transform/notes.py` (REQ-2).
  - Acceptance: `Select-String -Path coverage.xml -Pattern 'transform/notes.py'` returns a match.
- [x] [P2-T2] TASK-7 Update Issue #26 with PR/test links and outcomes (REQ-4).
  - Acceptance: `gh issue view 26 --json body -q ".body"` output contains a PR URL matching `https://github.com/drmoisan/transcript-etl-pipeline/pull/` and mentions "notes regressions".
- [x] [P2-T3] TASK-8 Update `docs/features/active/2025-12-04-notes-regressions-26/26-notes-regressions.prompt.md` with edge cases or outcomes discovered during test authoring.
  - Acceptance: `Select-String -Path docs/features/active/2025-12-04-notes-regressions-26/26-notes-regressions.prompt.md -Pattern 'Edge cases|Outcomes'` returns a match.

### Phase 3 — QA (Python Toolchain)
- [x] [P3-T1] Run `poetry run black .` and confirm the formatter exits with code 0; if it modifies files or fails, fix issues and restart from [P3-T1].
  - Acceptance: Command exits with code 0 on a pass where no files are modified.
- [x] [P3-T2] Run `poetry run ruff check` and confirm the linter exits with code 0; if it fails, fix issues and restart from [P3-T1].
  - Acceptance: Command exits with code 0.
- [x] [P3-T3] Run `poetry run pyright` and confirm type checking exits with code 0; if it fails, fix issues and restart from [P3-T1].
  - Acceptance: Command exits with code 0.
- [x] [P3-T4] Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and confirm tests exit with code 0; if it fails, fix issues and restart from [P3-T1].
  - Acceptance: Command exits with code 0.

## Test Plan

- Unit: `poetry run pytest tests/transform/test_notes.py`.
- Integration: Not applicable (unit-test-only change).
- Manual/CLI: `gh issue view 26 --json body -q ".body"` to confirm Issue #26 update content.

## Open Questions / Notes

- None.
