# 2025-12-04-identity-normalize - Plan

- **Issue:** #23
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T23:44:20Z
- **Status:** Planned
- **Version:** 0.2

![Status](https://img.shields.io/badge/status-Planned-blue)

Atomic, deterministic execution plan to raise combined coverage for `src/transcript_etl_pipeline/transform/identity_constraints.py` and `src/transcript_etl_pipeline/transform/normalize.py` to at least ~75% using focused unit tests.

## Required References

- Copilot Instructions: [`.github/copilot-instructions.md`](../../../../.github/copilot-instructions.md)
- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Coding Standards: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)

**All work must comply with these policies; do not duplicate their content here.**

## Implementation Plan (Atomic Tasks)

**Requirements Traceability**

| REQ-ID | Description | Source | Mapped Tasks |
| --- | --- | --- | --- |
| REQ-001 | Achieve combined coverage of ~$\ge 75\%$ for `identity_constraints.py` and `normalize.py` via unit tests. | 23-identity-normalize.prompt.md | P2-T1..P2-T11, P3-T1..P3-T9, P4-T1 |
| REQ-002 | Add deterministic unit tests in `tests/transform/` for name extraction and constraint application scenarios. | 23-identity-normalize.prompt.md | P2-T1..P2-T11 |
| REQ-003 | Add deterministic unit tests in `tests/transform/` for normalization edge cases. | 23-identity-normalize.prompt.md | P3-T1..P3-T9 |
| REQ-004 | Run coverage and document results and anomalies; update Issue #23 with evidence. | 23-identity-normalize.prompt.md | P4-T1..P4-T3 |

**Task Index**

| TASK-ID | Mapped Task |
| --- | --- |
| TASK-001 | P0-T1 |
| TASK-002 | P0-T2 |
| TASK-003 | P0-T3 |
| TASK-004 | P0-T4 |
| TASK-005 | P0-T5 |
| TASK-006 | P0-T6 |
| TASK-007 | P0-T7 |
| TASK-008 | P0-T8 |
| TASK-009 | P0-T9 |
| TASK-010 | P1-T1 |
| TASK-011 | P1-T2 |
| TASK-012 | P2-T1 |
| TASK-013 | P2-T2 |
| TASK-014 | P2-T3 |
| TASK-015 | P2-T4 |
| TASK-016 | P2-T5 |
| TASK-017 | P2-T6 |
| TASK-018 | P2-T7 |
| TASK-019 | P2-T8 |
| TASK-020 | P2-T9 |
| TASK-021 | P2-T10 |
| TASK-022 | P2-T11 |
| TASK-023 | P3-T1 |
| TASK-024 | P3-T2 |
| TASK-025 | P3-T3 |
| TASK-026 | P3-T4 |
| TASK-027 | P3-T5 |
| TASK-028 | P3-T6 |
| TASK-029 | P3-T7 |
| TASK-030 | P3-T8 |
| TASK-031 | P3-T9 |
| TASK-032 | P4-T1 |
| TASK-033 | P4-T2 |
| TASK-034 | P4-T3 |
| TASK-035 | P5-T1 |
| TASK-036 | P5-T2 |
| TASK-037 | P5-T3 |
| TASK-038 | P5-T4 |

### Phase 0 — Context & Inputs
- [x] [P0-T1] Read `.github/copilot-instructions.md` to confirm global agent requirements
  - Acceptance: A note is added to `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` stating the file was read with an ISO-8601 timestamp
- [x] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm workflow and toolchain order
  - Acceptance: `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` includes a timestamped entry confirming review
- [x] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm unit test constraints
  - Acceptance: `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` includes a timestamped entry confirming review
- [x] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` to confirm Python-specific rules
  - Acceptance: `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` includes a timestamped entry confirming review
- [x] [P0-T5] Read `.github/instructions/python-unit-test.instructions.md` to confirm Pytest structure and naming
  - Acceptance: `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` includes a timestamped entry confirming review
- [x] [P0-T6] Capture baseline formatting output with `poetry run black .`
  - Acceptance: Command exits with code 0 and output is saved to `artifacts/plan_23_baseline_black.txt`
- [x] [P0-T7] Capture baseline lint output with `poetry run ruff check`
  - Acceptance: Command exits with code 0 and output is saved to `artifacts/plan_23_baseline_ruff.txt`
- [x] [P0-T8] Capture baseline type-check output with `poetry run pyright`
  - Acceptance: Command exits with code 0 and output is saved to `artifacts/plan_23_baseline_pyright.txt`
- [x] [P0-T9] Capture baseline test output with `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing`
  - Acceptance: Command exits with code 0 and output is saved to `artifacts/plan_23_baseline_pytest.txt`

### Phase 1 — Coverage Mapping
- [x] [P1-T1] Create `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` documenting branches in `src/transcript_etl_pipeline/transform/identity_constraints.py` by listing each `detect_self_identification`, `detect_addresses_to_person`, and `extract_identity_constraints` branch condition verbatim
  - Acceptance: File exists and contains a section titled `identity_constraints.py` with bullet points quoting each branch condition from the module
- [x] [P1-T2] Add a `normalize.py` section to `docs/features/active/2025-12-04-identity-normalize-23/coverage-map.md` listing branches in `_normalize_line_endings`, `_clean_whitespace`, `_is_label`, `_normalize_labels`, and `normalize_text`
  - Acceptance: File includes a `normalize.py` section with bullet points quoting each branch condition from the module

### Phase 2 — Identity Constraints Tests
- [x] [P2-T1] Add Pytest case `test_thanks_followed_by_name_extracts_name` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Thanks Frank")` returning `["Frank"]` (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_thanks_followed_by_name_extracts_name` exits with code 0
- [x] [P2-T2] Add Pytest case `test_hello_followed_by_name_extracts_name` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Hello Dana")` returning `["Dana"]` (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_hello_followed_by_name_extracts_name` exits with code 0
- [x] [P2-T3] Add Pytest case `test_short_single_char_name_excluded` in `tests/transform/test_identity_constraints.py` covering exclusion of single-character tokens such as `"A"` from `detect_addresses_to_person` results (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_short_single_char_name_excluded` exits with code 0
- [x] [P2-T4] Add Pytest case `test_standalone_name_question_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Fred?")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_standalone_name_question_excluded` exits with code 0
- [x] [P2-T5] Add Pytest case `test_standalone_name_question_with_context_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Wait, Fred?")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_standalone_name_question_with_context_excluded` exits with code 0
- [x] [P2-T6] Add Pytest case `test_is_name_article_noun_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Is Dan a leader?")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_is_name_article_noun_excluded` exits with code 0
- [x] [P2-T7] Add Pytest case `test_is_name_an_expert_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Is Alice an expert?")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_is_name_an_expert_excluded` exits with code 0
- [x] [P2-T8] Add Pytest case `test_is_name_the_person_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("Is Bob the speaker?")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_is_name_the_person_excluded` exits with code 0
- [x] [P2-T9] Add Pytest case `test_mid_sentence_is_name_article_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("I wonder if Dan is a leader")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_mid_sentence_is_name_article_excluded` exits with code 0
- [x] [P2-T10] Add Pytest case `test_mid_sentence_is_name_an_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("We asked whether Charlie is an expert")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_mid_sentence_is_name_an_excluded` exits with code 0
- [x] [P2-T11] Add Pytest case `test_mid_sentence_is_name_the_excluded` in `tests/transform/test_identity_constraints.py` covering `detect_addresses_to_person("It depends on whether Sarah is the lead")` returning an empty list (REQ-002)
  - Acceptance: `poetry run pytest tests/transform/test_identity_constraints.py -k test_mid_sentence_is_name_the_excluded` exits with code 0

### Phase 3 — Normalize Tests
- [x] [P3-T1] Add Pytest case `test_normalize_line_endings_mixed_inputs` in `tests/transform/test_normalize.py` covering `_normalize_line_endings("a\r\nb\nc\rd") == "a\r\nb\r\nc\r\nd"` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_normalize_line_endings_mixed_inputs` exits with code 0
- [x] [P3-T2] Add Pytest case `test_clean_whitespace_collapses_duplicate_spaces` in `tests/transform/test_normalize.py` covering `_clean_whitespace("A  B\r\nC   D") == "A B\r\nC D"` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_clean_whitespace_collapses_duplicate_spaces` exits with code 0
- [x] [P3-T3] Add Pytest case `test_clean_whitespace_collapses_blank_lines_and_trailing` in `tests/transform/test_normalize.py` covering `_clean_whitespace("A\r\n\r\n\r\nB\r\n\r\n") == "A\r\n\r\nB"` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_clean_whitespace_collapses_blank_lines_and_trailing` exits with code 0
- [x] [P3-T4] Add Pytest case `test_is_label_accepts_capitalized_token` in `tests/transform/test_normalize.py` covering `_is_label("Speaker:") is True` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_is_label_accepts_capitalized_token` exits with code 0
- [x] [P3-T5] Add Pytest case `test_is_label_rejects_lowercase_token` in `tests/transform/test_normalize.py` covering `_is_label("speaker:") is False` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_is_label_rejects_lowercase_token` exits with code 0
- [x] [P3-T6] Add Pytest case `test_is_label_rejects_token_with_spaces` in `tests/transform/test_normalize.py` covering `_is_label("Speaker Name:") is False` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_is_label_rejects_token_with_spaces` exits with code 0
- [x] [P3-T7] Add Pytest case `test_normalize_labels_inserts_space_after_label` in `tests/transform/test_normalize.py` covering `_normalize_labels("Bob:Hello") == "Bob: Hello"` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_normalize_labels_inserts_space_after_label` exits with code 0
- [x] [P3-T8] Add Pytest case `test_normalize_labels_splits_mid_line_label` in `tests/transform/test_normalize.py` covering `_normalize_labels("Hi. Bob: Hello") == "Hi.\r\nBob: Hello"` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_normalize_labels_splits_mid_line_label` exits with code 0
- [x] [P3-T9] Add Pytest case `test_normalize_text_applies_all_steps` in `tests/transform/test_normalize.py` covering `normalize_text("Bob:Hello\n\nA  B") == "Bob: Hello\r\n\r\nA B"` (REQ-003)
  - Acceptance: `poetry run pytest tests/transform/test_normalize.py -k test_normalize_text_applies_all_steps` exits with code 0

### Phase 4 — Coverage Evidence & Reporting
- [x] [P4-T1] Run `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing` and record module-level coverage for `identity_constraints.py` and `normalize.py` in `docs/features/active/2025-12-04-identity-normalize-23/coverage-results.md` (REQ-001, REQ-004)
  - Acceptance: `coverage-results.md` exists and contains a table with per-module statement/missing/coverage values
- [x] [P4-T2] Document any unreachable or anomalous lines found during coverage analysis in `docs/features/active/2025-12-04-identity-normalize-23/coverage-results.md` (REQ-004)
  - Acceptance: `coverage-results.md` contains a section titled `Uncovered Lines Analysis` with numbered entries (or the line `None` if no anomalies)
- [x] [P4-T3] Update Issue #23 with coverage results, test command, and links to `coverage-results.md` (REQ-004).
  - Acceptance: Issue #23 comment includes the exact coverage table values and the command `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing`

### Phase 5 — QA Toolchain
- [x] [P5-T1] Run formatting step `poetry run black .` and restart the toolchain from P5-T1 if any files change or the command fails
  - Acceptance: Command exits with code 0 and produces no file changes
- [x] [P5-T2] Run linting step `poetry run ruff check` and restart the toolchain from P5-T1 if the command fails
  - Acceptance: Command exits with code 0
- [x] [P5-T3] Run type-check step `poetry run pyright` and restart the toolchain from P5-T1 if the command fails
  - Acceptance: Command exits with code 0
- [x] [P5-T4] Run testing step `poetry run pytest` and restart the toolchain from P5-T1 if the command fails
  - Acceptance: Command exits with code 0

## Test Plan

- Unit: `poetry run pytest tests/transform/test_identity_constraints.py` and `poetry run pytest tests/transform/test_normalize.py`
- Integration: `poetry run pytest`
- Manual/CLI: Not required

## Open Questions / Notes

- None
