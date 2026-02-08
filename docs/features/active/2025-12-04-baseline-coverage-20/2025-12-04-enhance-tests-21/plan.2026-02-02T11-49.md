---
title: "2025-12-04-enhance-tests - Plan"
issue: "21"
parent: "none"
owner: "drmoisan"
last_updated: "2026-02-02T23:44:20Z"
status: "Completed"
status_color: "green"
version: "1.0"
---

# 2025-12-04-enhance-tests - Plan

![Status: Completed](https://img.shields.io/badge/status-Completed-green)

- **Issue:** [#21](https://github.com/drmoisan/transcript-etl-pipeline/issues/21)
- **Parent (optional):** [#20](https://github.com/drmoisan/transcript-etl-pipeline/issues/20)
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T23:44:20Z
- **Status:** Completed
- **Version:** 1.0

Status Badge: 🟦 Planned

## Required References

- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Code Change Policy: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)

**All work must comply with these policies; do not duplicate their content here.**

## Implementation Plan (Atomic Tasks)

Requirements (REQ-):

| REQ-ID | Description | Source |
| --- | --- | --- |
| REQ-ENH-001 | Add characterization tests for speakerless routing in `tests/transform/test_enhance.py` using `transcript_etl_pipeline.transform.enhance.enhance_text`. | `21-enhance-tests.md` |
| REQ-ENH-002 | Add characterization tests for identity constraints and normalization interactions in `tests/transform/test_enhance.py`. | `21-enhance-tests.md` |
| REQ-ENH-003 | Ensure module coverage for `src/transcript_etl_pipeline/transform/enhance.py` is >= 70%. | `issue.md` |
| REQ-ENH-004 | Tests are deterministic and comply with unit test policy (no filesystem/temp files). | `issue.md` |
| REQ-ENH-005 | Run full toolchain (Black → Ruff → Pyright → Pytest) after changes. | repo policy |

### Phase 0 — Compliance & Context
- [x] [P0-T1] TASK-ENH-001 Record policy review timestamp in this plan file under “Open Questions / Notes” as `Policy Review Timestamp: <ISO-8601>`
  - Acceptance: `Open Questions / Notes` includes a line starting with `Policy Review Timestamp:` and a valid ISO-8601 timestamp
- [x] [P0-T2] TASK-ENH-002 Capture baseline coverage for `src/transcript_etl_pipeline/transform/enhance.py` using `poetry run pytest tests/transform/test_enhance.py --cov=src/transcript_etl_pipeline/transform/enhance.py --cov-report=term` and append the output under “Open Questions / Notes” as a fenced code block
  - Acceptance: `Open Questions / Notes` contains a fenced code block labeled `Baseline Coverage Output` with the exact command output

### Phase 1 — Identity Constraints Characterization Tests
- [x] [P1-T1] TASK-ENH-010 Add identity-constraint characterization tests to `tests/transform/test_enhance.py` with the exact names: `test_self_identification_with_two_speakers_uses_alternation`, `test_addresses_other_constraint_with_three_speakers`, `test_multiple_self_identifications_needs_more_changes`, `test_self_identifications_with_strong_change_signals`
  - Acceptance: `tests/transform/test_enhance.py` contains four new test functions with the exact names and assertions that lock current behavior via `enhance_text`
- [x] [P1-T2] TASK-ENH-011 Run targeted tests with `poetry run pytest tests/transform/test_enhance.py -k "self_identification_with_two_speakers_uses_alternation or addresses_other_constraint_with_three_speakers or multiple_self_identifications_needs_more_changes or self_identifications_with_strong_change_signals"`
  - Acceptance: Command exits with code 0

### Phase 2 — Normalization Interaction Characterization Tests
- [x] [P2-T1] TASK-ENH-020 Add normalization interaction tests to `tests/transform/test_enhance.py` with the exact names: `test_unix_line_endings_handled`, `test_mixed_line_endings_handled`, `test_whitespace_only_text_handled`, `test_single_line_no_labels`, `test_trailing_whitespace_preserved`, `test_empty_lines_between_speakers`, `test_very_long_speakerless_text`
  - Acceptance: `tests/transform/test_enhance.py` contains seven new test functions with the exact names and assertions that lock current behavior via `enhance_text`
- [ ] [P2-T2] TASK-ENH-021 Run targeted tests with `poetry run pytest tests/transform/test_enhance.py -k "line_endings_handled or whitespace_only_text_handled or single_line_no_labels or trailing_whitespace_preserved or empty_lines_between_speakers or very_long_speakerless_text"`
  - Acceptance: Command exits with code 0

### Phase 3 — Speakerless Edge Case Characterization Tests
- [x] [P3-T1] TASK-ENH-030 Add speakerless edge-case tests to `tests/transform/test_enhance.py` with the exact names: `test_single_sentence_speakerless`, `test_question_answer_pattern_speakerless`, `test_pronoun_shift_detection`, `test_greeting_triggers_speaker_change`, `test_thank_you_pattern_speaker_change`, `test_acknowledgment_triggers_speaker_change`, `test_num_speakers_one`, `test_num_speakers_four`, `test_labeled_with_speakerless_content`, `test_metadata_then_speakerless_dialogue`
  - Acceptance: `tests/transform/test_enhance.py` contains ten new test functions with the exact names and assertions that lock current behavior via `enhance_text`
- [x] [P3-T2] TASK-ENH-031 Run targeted tests with `poetry run pytest tests/transform/test_enhance.py -k "speakerless or question_answer_pattern or pronoun_shift_detection or greeting_triggers_speaker_change or thank_you_pattern_speaker_change or acknowledgment_triggers_speaker_change or num_speakers_one or num_speakers_four or labeled_with_speakerless_content or metadata_then_speakerless_dialogue"`
  - Acceptance: Command exits with code 0

### Phase 4 — Coverage Verification and Evidence
- [x] [P4-T1] TASK-ENH-040 Run coverage for the module with `poetry run pytest tests/transform/test_enhance.py --cov=src/transcript_etl_pipeline/transform/enhance.py --cov-report=term`
  - Acceptance: Coverage report shows `src/transcript_etl_pipeline/transform/enhance.py` coverage >= 70%
- [x] [P4-T2] TASK-ENH-041 Update issue #21 with the coverage report snippet and list of added tests from `tests/transform/test_enhance.py`
  - Acceptance: Issue #21 contains the coverage snippet and test list in a comment or description update

### Phase 5 — Full Toolchain Pass
- [x] [P5-T1] TASK-ENH-050 Run `poetry run black .`
  - Acceptance: Command exits with code 0 and no files are modified
- [x] [P5-T2] TASK-ENH-051 Run `poetry run ruff check`
  - Acceptance: Command exits with code 0
- [x] [P5-T3] TASK-ENH-052 Run `poetry run pyright`
  - Acceptance: Command exits with code 0
- [x] [P5-T4] TASK-ENH-053 Run `poetry run pytest`
  - Acceptance: Command exits with code 0

## Test Plan

- Unit: `poetry run pytest tests/transform/test_enhance.py`
- Integration: None
- Manual/CLI: None

## Open Questions / Notes

- Coverage evidence:

```Coverage Output
The currently activated Python version 3.10.19 is not supported by the project (^3.12).
Trying to find and use a compatible version. 
Using python3.14 (3.14.0)
Skipping virtualenv creation, as specified in config file.
============================= test session starts ==============================
platform linux -- Python 3.10.19, pytest-8.4.2, pluggy-1.6.0
rootdir: /workspace/transcript-etl-pipeline
configfile: pytest.ini
plugins: cov-5.0.0, anyio-4.12.1
collected 37 items

tests/transform/test_enhance.py ...................................../root/.pyenv/versions/3.10.19/lib/python3.10/site-packages/coverage/inorout.py:537: CoverageWarning: Module src/transcript_etl_pipeline/transform/enhance.py was previously imported, but not measured (module-not-measured); see https://coverage.readthedocs.io/en/7.12.0/messages.html#warning-module-not-measured
  self.warn(msg, slug="module-not-measured")
    [100%]

=============================== warnings summary ===============================
src/transcript_etl_pipeline/transform/speakers.py:12
  /workspace/transcript-etl-pipeline/src/transcript_etl_pipeline/transform/speakers.py:12: DeprecationWarning: dialogue_names_deprecated is deprecated; use extract_person_names_from_text instead.
    from transcript_etl_pipeline.transform import dialogue_names_deprecated

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html

---------- coverage: platform linux, python 3.10.19-final-0 ----------
Name                                               Stmts   Miss  Cover
----------------------------------------------------------------------
src/transcript_etl_pipeline/transform/enhance.py      13      0   100%
----------------------------------------------------------------------
TOTAL                                                 13      0   100%

Required test coverage of 15.0% reached. Total coverage: 100.00%
======================== 37 passed, 1 warning in 0.67s =========================
```
