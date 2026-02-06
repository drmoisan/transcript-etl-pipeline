# Feature Delivery Inventory — 2025-12-04-baseline-coverage-20

Audit Timestamp: 2026-02-05T15-30
Epic Root: `docs/features/active/2025-12-04-baseline-coverage-20`

## Summary Table

| Feature Folder | Issue | Versions | Current Version | Current Plan | Doc Completeness | AC Present | Dependencies Declared | Requirements Delivered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | #21 | None | Root | `plan.2026-02-02T11-49.md` | ✅ issue/spec/user-story/plan | ✅ | None | 2/3 (1 partial) | Fail-before dossier stored non-canonically; issue update mirror present. |
| `2025-12-04-speakerless-heuristics-22` | #22 | None | Root | `plan.2026-02-02T12-24.md` | ✅ | ✅ | None | 5/6 | Issue update mirror present. |
| `2025-12-04-identity-normalize-23` | #23 | None | Root | `plan.2026-02-02T13-08.md` | ✅ | ✅ | None | 4/5 | Issue update mirror present. |
| `2025-12-04-multi-speaker-fixtures-24` | #24 | None | Root | `plan.2026-02-02T13-09.md` | ✅ | ✅ | Reuse with #22/#25 | 5/5 | Known gaps captured as xfail. |
| `2025-12-04-e2e-speakerless-notes-25` | #25 | None | Root | `plan.2026-02-02T12-45.md` | ✅ | ✅ | Depends on #24 fixtures | 4/4 | In-memory CLI tests avoid filesystem writes. |
| `2025-12-04-notes-regressions-26` | #26 | None | Root | `plan.2026-02-02T13-09.md` | ✅ | ✅ | None | 0/3 (3 partial) | Fail-before dossier non-canonical; coverage run failed gate. |
| `2025-12-04-formatters-parser-27` | #27 | None | Root | `plan.2026-02-02T13-08.md` | ✅ | ✅ | None | 3/4 (1 partial) | Temp-file usage remains in `tests/formatters/test_notes_formatting.py`. |
| `2025-12-04-ci-coverage-gate-28` | #28 | None | Root | `plan.2025-12-04T11-43.md` | ✅ | ✅ | None | 4/5 (1 partial) | No evidence of CI fail-below-threshold behavior. |

Doc completeness: issue/spec/user-story/plan present. AC Present: acceptance criteria in spec or user-story.

## Alignment Check (Per Feature)

- **#21 enhance-tests:** Supports primary objective (core transform coverage). Dependencies none. Plan actionable.
- **#22 speakerless-heuristics:** Supports primary objective (speakerless coverage). Dependencies none. Plan actionable.
- **#23 identity-normalize:** Supports primary objective (identity/normalize coverage). Dependencies none. Plan actionable.
- **#24 multi-speaker-fixtures:** Supports regression suite expansion. Depends on #22/#25 fixture reuse. Plan actionable.
- **#25 e2e-speakerless-notes:** Supports CLI E2E objective. Depends on #24 fixtures (documented). Plan actionable.
- **#26 notes-regressions:** Supports notes regressions objective. Plan actionable.
- **#27 formatters-parser:** Supports formatter/parser coverage objective. Plan actionable.
- **#28 ci-coverage-gate:** Supports enforcement objective. Plan actionable.

## Acceptance Criteria Delivery (Evidence-Based)

### Feature #21 — enhance-tests

Acceptance criteria (from `user-story.md`):
1. **Fail-before and pass-after for untested behavior** → **Partially Met (Exception recorded)**
   - Evidence: `evidence/remediation-baseline/fail-before-exception.2026-02-05T13-05.md` (non-canonical location; should be under `evidence/regression-testing/`).
2. **Speakerless routing and constraint handling scenarios exercised** → **Met**
   - Evidence: tests present in `tests/transform/test_enhance.py` (e.g., `test_self_identification_with_two_speakers_uses_alternation`, `test_single_sentence_speakerless`).
3. **Coverage report shows ≥70% for `transform/enhance.py`** → **Met**
   - Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` shows 100% module coverage.

### Feature #22 — speakerless-heuristics

Acceptance criteria (from `user-story.md`):
1. **Positive/negative cases for `detect_speaker_changes` heuristics** → **Met**
   - Evidence: tests in `tests/transform/test_speakerless.py` (tag question heuristic present).
2. **Addressee reassignment in `resolve_addresses_other_violations`** → **Met**
   - Evidence: tests in `tests/transform/test_speaker_helpers.py` referencing `resolve_addresses_other_violations`.
3. **Similarity grouping behavior in `group_sentences_by_similarity`** → **Met**
   - Evidence: multiple test cases in `tests/transform/test_speaker_helpers.py`.
4. **Coverage ≥70% for `speakerless.py` and `speaker_helpers.py`** → **Met**
   - Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` shows 95%/92%.
5. **Tests deterministic, no filesystem/external services** → **Met**
   - Evidence: no temp-file usage in `tests/transform/test_speakerless.py` / `test_speaker_helpers.py` (no `tmp_path`/`tempfile` hits).
6. **Issue #22 updated with coverage evidence** → **Met**
   - Evidence: `issue-updates/issue-22.2026-02-04T11-21.md` contains the mirrored issue body and coverage snippet.

### Feature #23 — identity-normalize

Acceptance criteria (from `user-story.md`):
1. **Unit tests cover branches/edge cases in identity/normalize** → **Met**
   - Evidence: tests in `tests/transform/test_identity_constraints.py` and `tests/transform/test_normalize.py` (e.g., `test_thanks_followed_by_name_extracts_name`, `test_normalize_text_applies_all_steps`).
2. **Tests assert constraints/normalized outputs for tricky inputs** → **Met**
   - Evidence: test assertions in files above.
3. **Combined coverage ≥75% for `identity_constraints.py` and `normalize.py`** → **Met**
   - Evidence: `evidence/remediation-baseline/qa-pytest.2026-02-03T18-30.txt` shows 98% and 100%.
4. **Tests deterministic, no filesystem/external services** → **Met**
   - Evidence: no temp-file usage in the two test modules (no `tmp_path`/`tempfile` hits).
5. **Issue #23 updated with coverage evidence** → **Met**
   - Evidence: `issue-updates/issue-23.2026-02-04T11-21.md` contains the mirrored issue body and coverage snippet.

### Feature #24 — multi-speaker-fixtures

Acceptance criteria (from `user-story.md`):
1. **Shared fixture module with deterministic 3+ speaker fixtures** → **Met**
   - Evidence: `tests/fixtures/multi_speaker.py` defines fixtures and `get_fixture_by_name`.
2. **Regression tests reference shared fixtures and assert grouping outcomes** → **Met**
   - Evidence: `tests/transform/test_multi_speaker_regression.py` imports and uses fixtures.
3. **Fixture validation tests fail fast on malformed fixtures** → **Met**
   - Evidence: `TestMultiSpeakerFixtureValidation` in `tests/transform/test_multi_speaker_regression.py`.
4. **Known algorithmic gaps captured as xfail with rationale** → **Met**
   - Evidence: `pytest.mark.xfail` cases in `tests/transform/test_multi_speaker_regression.py`.
5. **Tests deterministic, no external dependencies** → **Met**
   - Evidence: fixtures are in-memory strings; no temp-file usage in this suite.

### Feature #25 — e2e-speakerless-notes

Acceptance criteria (from `user-story.md`):
1. **Speakerless CLI flows for DOCX/MD/RTF covered and pass** → **Met**
   - Evidence: `tests/integration/test_cli_e2e_speakerless.py` cases for DOCX/MD/RTF.
2. **Notes-only and notes+transcript flows (including update mode)** → **Met**
   - Evidence: `tests/integration/test_cli_e2e_notes.py` includes notes-only, combined, update-mode cases.
3. **Error handling for missing files/invalid args** → **Met**
   - Evidence: `TestCLIErrorHandling` and `TestCLINotesErrorHandling` in integration tests.
4. **Output validation uses stable text markers** → **Met**
   - Evidence: Assertions use text markers in document text extraction.

### Feature #26 — notes-regressions

Acceptance criteria (from `user-story.md`):
1. **Fail-before / pass-after regression tests** → **Partially Met (Exception recorded)**
   - Evidence: `evidence/remediation-baseline/fail-before-exception.2026-02-05T13-15.md` (non-canonical location).
2. **Regression tests demonstrate prior failures and now pass** → **Partially Met**
   - Evidence: `evidence/remediation-baseline/pass-after.2026-02-03T18-30.txt` shows passing tests; fail-before evidence is non-canonical.
3. **Coverage on notes-related paths improves** → **Met**
   - Evidence: `evidence/regression-testing/notes-coverage.2026-02-05T16-10.txt` shows `transform/notes.py` at 99% with EXIT_CODE 0.

### Feature #27 — formatters-parser

Acceptance criteria (from `user-story.md`):
1. **Tests assert key formatting/spacing rules and parsed structures** → **Met**
   - Evidence: coverage run includes `tests/formatters/*` and `tests/document/test_parser_unit.py` with 125 passing tests (`evidence/remediation-baseline/coverage.2026-02-03T18-30.txt`).
2. **Coverage ≥70% for formatters and parser** → **Met**
   - Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` shows 93.83% for target modules.
3. **Avoid brittle binary DOCX output assertions** → **Partially Met**
   - Evidence: New formatter tests are in-memory, but `tests/formatters/test_notes_formatting.py` still uses `tmp_path` and file outputs (unit-test policy conflict).
4. **Tests deterministic without external dependencies** → **Partially Met**
   - Evidence: temp-file usage remains in `tests/formatters/test_notes_formatting.py`.

### Feature #28 — ci-coverage-gate

Acceptance criteria (from `user-story.md`):
1. **CI runs pytest-cov and fails below configured floor** → **Partially Met**
   - Evidence: CI config and success run exist (`evidence/qa-gates/ci-config.2026-02-05T14-40.md`, `ci-run.2026-02-06T01-41.md`), but no failing run captured.
2. **CI passes when coverage meets/exceeds floor** → **Met**
   - Evidence: `ci-run.2026-02-06T01-41.md` (success).
3. **CI surfaces coverage results in logs and step summary** → **Met**
   - Evidence: `ci-config.2026-02-05T14-40.md` shows step summary step.
4. **CI uploads coverage artifacts** → **Met**
   - Evidence: `ci-run.2026-02-06T01-41.md` lists HTML/XML artifacts.
5. **Docs explain `fail_under` adjustments** → **Met**
   - Evidence: ratchet strategy documented in `spec.md`.

## Plan Reconciliation

- **Auto-checked items:** None. Evidence artifacts with required schema exist for coverage/test runs, but plan items were not auto-checked because:
  - Fail-before exception dossiers are stored in non-canonical locations (must be in `evidence/regression-testing/`).
  - Issue update tasks require local mirror artifacts and/or GH updates that are not present.

## Merge Readiness Posture

- **Blocking:** Unmet acceptance criteria in #26, #27, #28 (fail-before evidence locations, CI fail-below proof, and unit-test policy conflicts).
- **Non-blocking:** Business-case doc gaps or missing narrative updates.
