# 2025-12-04-multi-speaker-fixtures - Plan

- **Issue:** #24
- **Parent (optional):** [#20](https://github.com/drmoisan/transcript-etl-pipeline/issues/20)
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T23:44:20Z
- **Status:** Completed
- **Version:** 1.0

![Status: Completed](https://img.shields.io/badge/status-Completed-green)

## Required References

- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Coding Standards: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)

**All work must comply with these policies; do not duplicate their content here.**

## Implementation Plan (Atomic Tasks)

> **Instructions for this section:**
> - Break work into **Phases** (broad buckets) and **Atomic Tasks** (binary, 5-30 min units).
> - Use `- [ ] [P#-T#]` for every task.
> - Start every task with a **strong verb** (Implement, Create, Update, Verify).
> - No "bucket" tasks like "Refactor module" or "Write tests"; split them into specific, verifiable steps.
> - **Self-Validating Phases:** Include necessary test creation/update tasks *within* the phase that implements the code. Do not defer verification to a final "Testing" phase.

REQ-001 | Provide reusable 3+ speaker fixtures for regression tests in `tests/fixtures/multi_speaker.py` | Source: Issue #24 | Validation: Fixtures are importable and referenced by tests
REQ-002 | Add regression tests in `tests/transform/test_multi_speaker_regression.py` covering grouping behavior | Source: Issue #24 | Validation: Tests assert expected speaker labeling/grouping outcomes
REQ-003 | Capture known algorithmic gaps as `xfail` tests with documented rationale | Source: 24-multi-speaker-fixtures.prompt.md | Validation: `pytest -q` reports xfailed tests with reasons
REQ-004 | Keep fixtures deterministic and synthetic with no sensitive data | Source: Issue #24 constraints | Validation: Fixtures are static strings and do not require I/O
REQ-005 | Document fixture location and usage in `docs/features/active/2025-12-04-multi-speaker-fixtures-24/issue.md` | Source: 24-multi-speaker-fixtures.prompt.md | Validation: Issue doc includes links/notes

### Phase 0: Compliance & Context
- [x] [TASK-P0-T1] Confirm alignment with repo policies by reading `.github/instructions/general-code-change.instructions.md`, `.github/instructions/python-code-change.instructions.md`, `.github/instructions/general-unit-test.instructions.md`, and `.github/instructions/python-unit-test.instructions.md` before touching code
  - Acceptance: Development log contains policy review timestamp prior to Phase 1 commits

### Phase 1: Fixture Module Creation
- [x] [TASK-P1-T1] Create `tests/fixtures/multi_speaker.py` (new file, line numbers N/A) with `@dataclass(frozen=True)` definitions for `ExpectedSpeakerLine` and `MultiSpeakerFixture` and a `get_fixture_by_name(name: str) -> MultiSpeakerFixture` lookup function
  - Acceptance: `from tests.fixtures.multi_speaker import ExpectedSpeakerLine, MultiSpeakerFixture, get_fixture_by_name` imports succeed
- [x] [TASK-P1-T2] Define fixture constants in `tests/fixtures/multi_speaker.py` for `SPACEX_DISCUSSION`, `GENERIC_MEETING_3SPEAKER`, `TEAM_STANDUP_3SPEAKER`, and `PANEL_DISCUSSION_4SPEAKER` with `input_text`, `expected_lines`, and `num_speakers` values
  - Acceptance: Each fixture has `num_speakers >= 3` and non-empty `input_text` and `expected_lines`
- [x] [TASK-P1-T3] Add collection tuples `ALL_3SPEAKER_FIXTURES`, `ALL_4SPEAKER_FIXTURES`, and `ALL_MULTI_SPEAKER_FIXTURES` in `tests/fixtures/multi_speaker.py`
  - Acceptance: `len(ALL_MULTI_SPEAKER_FIXTURES) == len(ALL_3SPEAKER_FIXTURES) + len(ALL_4SPEAKER_FIXTURES)`

### Phase 2: Regression Test Suite
- [x] [TASK-P2-T1] Create `tests/transform/test_multi_speaker_regression.py` (new file, line numbers N/A) with fixture validation tests that assert structure, counts, and content constraints for each fixture
  - Acceptance: `pytest -q tests/transform/test_multi_speaker_regression.py -k fixture` passes
- [x] [TASK-P2-T2] Add parametrized tests in `tests/transform/test_multi_speaker_regression.py` that call existing speaker assignment/grouping functions using each fixture’s `input_text` and validate expected speaker counts and content preservation
  - Acceptance: Tests assert speaker count equals `fixture.num_speakers` and all expected lines appear in output
- [x] [TASK-P2-T3] Add scenario-specific regression tests for SpaceX, standup, and panel fixtures to verify grouping boundaries and identity constraints
  - Acceptance: Each scenario has at least one targeted assertion on grouping behavior
- [x] [TASK-P2-T4] Mark known algorithmic limitations as `pytest.mark.xfail` with explicit reason strings in `tests/transform/test_multi_speaker_regression.py`
  - Acceptance: `pytest -q` reports xfailed tests with those reasons and no xpasses

### Phase 3: Documentation Updates
- [x] [TASK-P3-T1] Update `docs/features/active/2025-12-04-multi-speaker-fixtures-24/issue.md` to document fixture locations, usage, and test suite location
  - Acceptance: Issue doc includes explicit paths to `tests/fixtures/multi_speaker.py` and `tests/transform/test_multi_speaker_regression.py`
  - Evidence (status_updater, 2026-02-03T17-30): `issue.md` updated with fixture and regression test paths in Sync Summary.
- [x] [TASK-P3-T2] Update `docs/features/active/2025-12-04-multi-speaker-fixtures-24/24-multi-speaker-fixtures.prompt.md` with final test counts and results once tests pass
  - Acceptance: Prompt doc includes test result summary and xfail list

## Test Plan

- Unit: `pytest -q tests/transform/test_multi_speaker_regression.py` validates fixture structure and grouping behavior
- Integration: None (not required for test-only fixture coverage)
- Manual/CLI: `pytest -q` full suite run after changes to confirm no regressions

## Open Questions / Notes

- None.
