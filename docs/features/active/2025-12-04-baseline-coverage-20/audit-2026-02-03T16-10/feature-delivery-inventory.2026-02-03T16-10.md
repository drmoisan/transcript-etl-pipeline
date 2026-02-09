# Feature Delivery Inventory — 2025-12-04-baseline-coverage-20

## Summary table

| Feature folder | Issue | Versions | Current version | Current plan | Doc completeness (issue/spec/user-story/plan) | Acceptance criteria present | Dependency declarations | Requirements delivered (Met/Total) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | #21 | none | root | `plan.2026-02-02T11-49.md` | Yes | Yes | None explicit | 2/3 (1 unknown) | Coverage evidence present in plan; pre/post failure claim not verified. |
| `2025-12-04-speakerless-heuristics-22` | #22 | none | root | `plan.2026-02-02T12-24.md` | Yes | Yes | None explicit | 4/6 (1 unknown, 1 not met) | Coverage gate + issue update not verified. |
| `2025-12-04-identity-normalize-23` | #23 | none | root | `plan.2026-02-02T13-08.md` | Yes | Yes | None explicit | 4/5 (1 not met) | Coverage evidence in `coverage-results.md`; issue update missing. |
| `2025-12-04-multi-speaker-fixtures-24` | #24 | none | root | `plan.2026-02-02T13-09.md` | Yes | Yes | None explicit | 5/5 | Fixtures + regression tests present with xfail gaps documented. |
| `2025-12-04-e2e-speakerless-notes-25` | #25 | none | root | `plan.2026-02-02T12-45.md` | Yes | Yes | Uses #24 fixtures | 4/4 | Tests are in-memory and avoid filesystem; plan partially reconciled. |
| `2025-12-04-notes-regressions-26` | #26 | none | root | `plan.2026-02-02T13-09.md` | Yes | Yes | None explicit | 1/3 (2 unknown) | Regression tests exist; pre/post failure + coverage improvement not verified. |
| `2025-12-04-formatters-parser-27` | #27 | none | root | `plan.2026-02-02T13-08.md` | Yes | Yes | None explicit | 4/4 | In-memory tests replace file I/O; coverage evidence in plan. |
| `2025-12-04-ci-coverage-gate-28` | #28 | none | root | `plan.2025-12-04T11-43.md` | Yes | Yes | Depends on initiative gates | 2/5 (3 partial/unknown) | CI config updated; docs + evidence missing. |

---

## Alignment check (per feature)

### #21 Enhance tests
- **Supports primary objective:** Yes (transform/enhance coverage).
- **Acceptance criteria testable:** Yes; coverage target and specific scenarios.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; several execution/issue update steps remain unchecked.

### #22 Speakerless heuristics
- **Supports primary objective:** Yes (speakerless coverage).
- **Acceptance criteria testable:** Yes; coverage target + heuristic cases.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; coverage evidence + issue update not complete.

### #23 Identity + normalize
- **Supports primary objective:** Yes (core transform coverage).
- **Acceptance criteria testable:** Yes; coverage target + edge cases.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; issue update and QA steps incomplete.

### #24 Multi-speaker fixtures
- **Supports primary objective:** Yes (shared fixtures for regressions).
- **Acceptance criteria testable:** Yes; fixture + regression tests.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Yes; remaining doc updates in plan not completed.

### #25 E2E speakerless + notes
- **Supports primary objective:** Yes (CLI integration coverage).
- **Acceptance criteria testable:** Yes; test files and markers.
- **Dependencies explicit:** Reuses #24 fixtures (see `implementation-summary.md`).
- **Plan actionable:** Partially; some planned scenarios not implemented.

### #26 Notes regressions
- **Supports primary objective:** Yes (notes coverage + regressions).
- **Acceptance criteria testable:** Partially; pre/post failure claims unverified.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; issue update and QA steps incomplete.

### #27 Formatters + parser
- **Supports primary objective:** Yes (formatter/parser coverage).
- **Acceptance criteria testable:** Yes; in-memory tests.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; issue update and QA steps incomplete.

### #28 CI coverage gate
- **Supports primary objective:** Yes (coverage enforcement).
- **Acceptance criteria testable:** Partially; CI evidence missing.
- **Dependencies explicit:** Ratchet gates in `orchestration.md`.
- **Plan actionable:** Partially; doc update and CI evidence missing.

---

## Acceptance criteria delivery (evidence-first)

### Feature #21 — enhance-tests
1. **Tests fail before and pass after (previously untested behavior).** **Status: Unknown** — no pre/post failure evidence captured in repo.
2. **Speakerless routing and constraint handling scenarios exercised.** **Status: Met** — see `tests/transform/test_enhance.py` (speakerless routing + identity constraints).
3. **Coverage >=70% for `transform/enhance.py`.** **Status: Met (documented)** — coverage block in `plan.2026-02-02T11-49.md` shows 100% for module.

### Feature #22 — speakerless-heuristics
1. **Positive/negative heuristic cases for `detect_speaker_changes`.** **Status: Met** — `tests/transform/test_speakerless.py` includes tag-question, pronoun shift, greeting/ack patterns.
2. **Addressee reassignment in `resolve_addresses_other_violations`.** **Status: Met** — `tests/transform/test_speaker_helpers.py` includes follow-through reassignment tests.
3. **Similarity grouping behavior and boundary conditions.** **Status: Met** — `tests/transform/test_speaker_helpers.py` tests round-robin and constraint cases.
4. **Coverage >=70% for `speakerless.py` + `speaker_helpers.py`.** **Status: Unknown** — no recorded coverage report in repo for these modules.
5. **Tests deterministic, no filesystem/temp files/external services.** **Status: Met** — tests are in-memory; NLTK downloads stubbed.
6. **Issue #22 updated with coverage evidence.** **Status: Not met** — plan item remains unchecked.

### Feature #23 — identity-normalize
1. **Unit tests cover main branches and edge cases.** **Status: Met** — `tests/transform/test_identity_constraints.py`, `tests/transform/test_normalize.py`.
2. **Tests assert explicit constraints and normalized outputs.** **Status: Met** — see same test files.
3. **Combined coverage >=75%.** **Status: Met (documented)** — `coverage-results.md` shows 98%/100% (combined 99%).
4. **Tests deterministic, no filesystem/temp files.** **Status: Met** — test-only in-memory strings.
5. **Issue #23 updated with coverage evidence.** **Status: Not met** — plan item unchecked.

### Feature #24 — multi-speaker-fixtures
1. **Shared fixture module for 3+ speakers.** **Status: Met** — `tests/fixtures/multi_speaker.py`.
2. **Regression tests reference shared fixtures.** **Status: Met** — `tests/transform/test_multi_speaker_regression.py`.
3. **Fixture validation tests fail fast on malformed fixtures.** **Status: Met** — fixture validation tests in `test_multi_speaker_regression.py`.
4. **Known gaps captured as `xfail`.** **Status: Met** — `pytest.mark.xfail` in regression tests.
5. **Deterministic tests with no external deps.** **Status: Met** — in-memory fixtures.

### Feature #25 — e2e-speakerless-notes
1. **Speakerless CLI flows for DOCX/MD/RTF outputs.** **Status: Met** — `tests/integration/test_cli_e2e_speakerless.py`.
2. **Notes-only and notes+transcript flows (incl. update mode).** **Status: Met** — `tests/integration/test_cli_e2e_notes.py`.
3. **Error handling cases for missing files/invalid args.** **Status: Met** — error handling tests in `tests/integration/test_cli_e2e_*`.
4. **Output validation via text markers (no binary diffs).** **Status: Met** — tests assert on markers via `_document_text`.

### Feature #26 — notes-regressions
1. **Each known bug has a regression test.** **Status: Met** — `_clean_markdown_text`, `_parse_bullet_line`, `_get_heading_level`, `transform_notes`, `_parse_markdown` tests in `tests/transform/test_notes.py`.
2. **Regression tests demonstrate prior failures and now pass.** **Status: Unknown** — no pre-failure evidence captured.
3. **Coverage improvement on notes paths.** **Status: Unknown** — no current coverage report recorded for notes module in this epic root.

### Feature #27 — formatters-parser
1. **Tests assert formatting/spacing rules and parsed structures.** **Status: Met** — `tests/formatters/*`, `tests/document/test_parser_unit.py`.
2. **Coverage >=70% for formatter/parser modules.** **Status: Met (documented)** — `plan.2026-02-02T13-08.md` reports `coverage report --fail-under=70` pass.
3. **Avoid brittle binary DOCX assertions.** **Status: Met** — in-memory formatter tests (no file I/O).
4. **Deterministic tests without external deps.** **Status: Met** — unit-level tests only.

### Feature #28 — ci-coverage-gate
1. **CI runs pytest-cov and fails below floor.** **Status: Partial/Unknown** — CI config updated, but no run evidence.
2. **CI passes when coverage meets floor.** **Status: Unknown** — no CI run evidence.
3. **CI surfaces coverage results in logs + step summary.** **Status: Met (configured)** — `ci.yml` step summary (`coverage report --format=markdown`).
4. **CI uploads coverage artifacts.** **Status: Met (configured)** — `ci.yml` uploads `htmlcov/` + `coverage.xml`.
5. **Documentation explains how to adjust `fail_under`.** **Status: Not met** — no updated documentation found.

---

## Plan reconciliation (auto-checked items)

**Auto-checked in** `2025-12-04-e2e-speakerless-notes-25/plan.2026-02-02T12-45.md`:
- P1-T1, P1-T2, P1-T3, P1-T4, P1-T6, P1-T10, P1-T11
- P2-T1, P2-T2, P2-T3, P2-T4, P2-T5, P2-T7

**Evidence:** `tests/integration/test_cli_e2e_speakerless.py`, `tests/integration/test_cli_e2e_notes.py` implement the specified tests and helpers.

---

## Merge readiness posture

**Status: Blocked** — multiple acceptance criteria remain not met or unverified (#21, #22, #26, #28), and several plan items are incomplete (coverage evidence, issue updates, CI proof, and QA toolchain steps).
