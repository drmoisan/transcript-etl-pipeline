---
title: "2025-12-04-speakerless-heuristics - Plan"
issue: "22"
parent: "none"
owner: "drmoisan"
last_updated: "2026-02-02"
status: "Planned"
status_color: "blue"
version: "0.2"
---

# 2025-12-04-speakerless-heuristics - Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

- **Issue:** [#22](https://github.com/drmoisan/transcript-etl-pipeline/issues/22)
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02
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
| REQ-1 | Add unit tests covering rhetorical/tag questions, addressee handling, continuation rules, and clustering helpers for `transform/speakerless.py` and `transform/speaker_helpers.py`. | `22-speakerless-heuristics.md` |
| REQ-2 | Raise coverage for `speakerless.py` and `speaker_helpers.py` to $\ge 70\%$ and capture evidence. | `22-speakerless-heuristics.md` |
| REQ-3 | Keep tests deterministic, isolated, and free of filesystem/temp files or external dependencies. | `22-speakerless-heuristics.md` |
| REQ-4 | Update Issue #22 with findings, PR/test links, and coverage evidence. | `22-speakerless-heuristics.md` |

## Task Index

| TASK-ID | Phase/Task | Summary |
| --- | --- | --- |
| TASK-1 | P1-T1 | Add rhetorical/tag question test for `detect_speaker_changes` in `tests/transform/test_speakerless.py`. |
| TASK-2 | P1-T2 | Add continuation/anti-shift test for `detect_speaker_changes` in `tests/transform/test_speakerless.py`. |
| TASK-3 | P1-T3 | Add addressee reassignment test for `assign_speaker_labels` in `tests/transform/test_speakerless.py`. |
| TASK-4 | P1-T4 | Add closing/continuation test for organizer reassignment in `tests/transform/test_speakerless.py`. |
| TASK-5 | P2-T1 | Add tag-question acknowledgment marker test for `detect_dialogue_markers` in `tests/transform/test_speaker_helpers.py`. |
| TASK-6 | P2-T2 | Add follow-through reassignment test for `resolve_addresses_other_violations` in `tests/transform/test_speaker_helpers.py`. |
| TASK-7 | P2-T3 | Add round-robin segmentation test for `group_sentences_by_similarity` in `tests/transform/test_speaker_helpers.py`. |
| TASK-8 | P2-T4 | Add similarity-grouping constraint boundary test for `group_sentences_by_similarity` in `tests/transform/test_speaker_helpers.py`. |
| TASK-9 | P3-T1 | Run coverage gating for the two modules and record evidence. |
| TASK-10 | P3-T2 | Update Issue #22 with coverage evidence and links. |
| TASK-11 | P3-T3 | Update `22-speakerless-heuristics.md` with edge cases or surprises discovered. |

> **Instructions for this section:**
> - Break work into **Phases** (broad buckets) and **Atomic Tasks** (binary, 5-30 min units).
> - Use `- [ ] [P#-T#]` for every task.
> - Start every task with a **strong verb** (Implement, Create, Update, Verify).
> - No "bucket" tasks like "Refactor module" or "Write tests"; split them into specific, verifiable steps.
> - **Self-Validating Phases:** Include necessary test creation/update tasks *within* the phase that implements the code. Do not defer verification to a final "Testing" phase.

### Phase 0 — Context & Inputs
- [ ] [P0-T1] TASK-0 Read `.github/copilot-instructions.md` to establish baseline agent rules.
  - Acceptance: `powershell -Command "Test-Path .github/copilot-instructions.md"` exits with code 0.
- [ ] [P0-T2] TASK-0 Read `.github/instructions/general-code-change.instructions.md` to confirm workflow requirements.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-code-change.instructions.md"` exits with code 0.
- [ ] [P0-T3] TASK-0 Read `.github/instructions/general-unit-test.instructions.md` to confirm unit-test policy.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-unit-test.instructions.md"` exits with code 0.
- [ ] [P0-T4] TASK-0 Read `.github/instructions/python-code-change.instructions.md` for Python rules.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-code-change.instructions.md"` exits with code 0.
- [ ] [P0-T5] TASK-0 Read `.github/instructions/python-unit-test.instructions.md` for Pytest rules.
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-unit-test.instructions.md"` exits with code 0.
- [ ] [P0-T6] TASK-0 Read `docs/features/active/2025-12-04-speakerless-heuristics-22/22-speakerless-heuristics.md` for scope and acceptance criteria.
  - Acceptance: `powershell -Command "Test-Path docs/features/active/2025-12-04-speakerless-heuristics-22/22-speakerless-heuristics.md"` exits with code 0.
- [ ] [P0-T7] TASK-0 Capture baseline formatting output with `poetry run black .` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T8] TASK-0 Capture baseline lint output with `poetry run ruff check` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T9] TASK-0 Capture baseline type-check output with `poetry run pyright` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T10] TASK-0 Capture baseline test output with `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html`.
  - Acceptance: Command exits with code 0.

### Phase 1 — Speakerless Heuristic Tests (`tests/transform/test_speakerless.py`)
- [ ] [P1-T1] TASK-1 Add a Pytest case in `tests/transform/test_speakerless.py` for `detect_speaker_changes` using a rhetorical/tag question input `"We should proceed, right?\r\nYes, let's do it."` and assert change points include index `1`.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speakerless.py -Pattern 'rhetorical|tag question'"` returns a match and the test asserts `1 in changes`.
- [ ] [P1-T2] TASK-2 Add a Pytest case in `tests/transform/test_speakerless.py` for `detect_speaker_changes` using continuation text `"I think we should proceed.\r\nYou know I agree."` and assert `changes == [0]` to validate the anti-shift rule (current sentence contains both first and second person).
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speakerless.py -Pattern 'anti-shift|continuation'"` returns a match and the test asserts `changes == [0]`.
- [ ] [P1-T3] TASK-3 Add a Pytest case in `tests/transform/test_speakerless.py` for `assign_speaker_labels` with `num_speakers=3` that includes a self-identification and an addressee line (e.g., `"I'm Frank Oz. Thanks Frank."`) and assert the addressee line is not assigned to Frank’s speaker.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speakerless.py -Pattern 'Thanks Frank'"` returns a match and the test asserts the addressee line’s speaker label differs from the self-identified speaker.
- [ ] [P1-T4] TASK-4 Add a Pytest case in `tests/transform/test_speakerless.py` for `assign_speaker_labels` that includes a short closing statement (e.g., `"Great. Thank you both."`) after self-identifications and assert the closing sentence is assigned to the organizer’s speaker.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speakerless.py -Pattern 'closing statement|Thank you both'"` returns a match and the test asserts the closing line’s speaker equals the organizer’s speaker.

### Phase 2 — Helper Heuristic Tests (`tests/transform/test_speaker_helpers.py`)
- [ ] [P2-T1] TASK-5 Add a Pytest case in `tests/transform/test_speaker_helpers.py` for `detect_dialogue_markers` using `"Right?"` and assert `is_acknowledgment` is `True` to cover tag-question acknowledgments.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speaker_helpers.py -Pattern 'Right\?"'"` returns a match and the test asserts `markers["is_acknowledgment"] is True`.
- [ ] [P2-T2] TASK-6 Add a Pytest case in `tests/transform/test_speaker_helpers.py` for `resolve_addresses_other_violations` with sentences `"I'm Frank.", "Thanks Frank.", "Fred?"` and assignments that initially assign the addressee lines to Frank; assert both the address and follow-through lines are reassigned away from Frank.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speaker_helpers.py -Pattern 'follow-through|Thanks Frank'"` returns a match and the test asserts both indices are not assigned to Frank’s speaker.
- [ ] [P2-T3] TASK-7 Add a Pytest case in `tests/transform/test_speaker_helpers.py` for `group_sentences_by_similarity` where `sentences = ["A.", "B."]`, `change_points = [0, 1]`, `num_speakers = 3`, and assert assignments are `[0, 1]` to validate the round-robin branch for `len(segments) <= num_speakers`.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speaker_helpers.py -Pattern 'round-robin'"` returns a match and the test asserts assignments equal `[0, 1]`.
- [ ] [P2-T4] TASK-8 Add a Pytest case in `tests/transform/test_speaker_helpers.py` for `group_sentences_by_similarity` with self-identification constraints for three distinct names and assert the resulting assignments keep those three indices mapped to three distinct speakers.
  - Acceptance: `powershell -Command "Select-String -Path tests/transform/test_speaker_helpers.py -Pattern 'distinct speakers'"` returns a match and the test asserts `len(set(...)) == 3` for the three self-identified indices.

### Phase 3 — Coverage Evidence and Issue Updates
- [ ] [P3-T1] TASK-9 Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` followed by `poetry run coverage report --include=src/transcript_etl_pipeline/transform/speakerless.py,src/transcript_etl_pipeline/transform/speaker_helpers.py --fail-under=70` and capture the output in the task notes (REQ-2).
  - Acceptance: The `coverage report --fail-under=70` command exits with code 0.
- [ ] [P3-T2] TASK-10 Update Issue #22 with coverage evidence and links to tests/PRs (REQ-4).
  - Acceptance: `gh issue view 22 --json body -q ".body"` output contains a PR URL matching `https://github.com/drmoisan/transcript-etl-pipeline/pull/` and mentions `coverage report --fail-under=70`.
- [ ] [P3-T3] TASK-11 Update `docs/features/active/2025-12-04-speakerless-heuristics-22/22-speakerless-heuristics.md` with any edge cases or surprises discovered during test authoring.
  - Acceptance: `powershell -Command "Select-String -Path docs/features/active/2025-12-04-speakerless-heuristics-22/22-speakerless-heuristics.md -Pattern 'Edge cases|Surprises'"` returns a match.

### Phase 4 — QA (Python Toolchain)
- [ ] [P4-T1] TASK-12 Run `poetry run black .` and confirm the formatter exits with code 0; if it modifies files or fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0 on a pass where no files are modified.
- [ ] [P4-T2] TASK-13 Run `poetry run ruff check` and confirm the linter exits with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.
- [ ] [P4-T3] TASK-14 Run `poetry run pyright` and confirm type checking exits with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.
- [ ] [P4-T4] TASK-15 Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and confirm tests exit with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.

## Test Plan

- Unit: `poetry run pytest tests/transform/ -k speakerless` (local focus) and `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` (full run).
- Integration: Not applicable (unit-test-only change).
- Manual/CLI: `gh issue view 22 --json body -q ".body"` to confirm the Issue #22 update content.

## Open Questions / Notes

- None.
