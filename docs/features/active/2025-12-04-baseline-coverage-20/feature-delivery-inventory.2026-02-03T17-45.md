# Feature Delivery Inventory — 2025-12-04-baseline-coverage-20

## Summary table

| Feature folder | Issue | Versions | Current version | Current plan | Doc completeness (issue/spec/user-story/plan) | Acceptance criteria present | Dependency declarations | Requirements delivered (Met/Total) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | #21 | none | root | `plan.2026-02-02T11-49.md` | Yes | Yes | None explicit | 1/3 (2 unknown) | Coverage evidence in plan is doc-only and stale. Issue update missing. |
| `2025-12-04-speakerless-heuristics-22` | #22 | none | root | `plan.2026-02-02T12-24.md` | Yes | Yes | None explicit | 4/6 (2 unknown) | Tests exist; coverage evidence missing; issue update missing. |
| `2025-12-04-identity-normalize-23` | #23 | none | root | `plan.2026-02-02T13-08.md` | Yes | Yes | None explicit | 4/5 (1 unknown) | Coverage results doc-only and stale; issue update missing. |
| `2025-12-04-multi-speaker-fixtures-24` | #24 | none | root | `plan.2026-02-02T13-09.md` | Yes | Yes | None explicit | 5/5 | Fixture and regression tests present; doc update task checked. |
| `2025-12-04-e2e-speakerless-notes-25` | #25 | none | root | `plan.2026-02-02T12-45.md` | Yes | Yes | Uses #24 fixtures | 4/4 | Tests in-memory; plan still lists missing scenarios. Implementation summary metrics are stale. |
| `2025-12-04-notes-regressions-26` | #26 | none | root | `plan.2026-02-02T13-09.md` | Yes | Yes | None explicit | 1/3 (2 unknown) | Tests exist; coverage evidence and issue update missing. |
| `2025-12-04-formatters-parser-27` | #27 | none | root | `plan.2026-02-02T13-08.md` | Yes | Yes | None explicit | 3/4 (1 unknown) | Coverage evidence recorded in plan is doc-only; issue update missing. |
| `2025-12-04-ci-coverage-gate-28` | #28 | none | root | `plan.2025-12-04T11-43.md` | Yes | Yes | Depends on initiative gates | 2/5 (3 unknown/not met) | CI config updated; documentation + run evidence missing. |

---

## Alignment check (per feature)

### #21 Enhance tests
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Yes.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; coverage capture and issue update tasks remain.

### #22 Speakerless heuristics
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Yes.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; coverage evidence and issue update missing.

### #23 Identity + normalize
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Yes.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; issue update and QA steps incomplete.

### #24 Multi-speaker fixtures
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Yes.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Mostly; remaining QA steps not verified.

### #25 E2E speakerless + notes
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Yes.
- **Dependencies explicit:** Uses #24 fixtures.
- **Plan actionable:** Partially; several scenario tasks remain unchecked.

### #26 Notes regressions
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Partially; pre/post failure evidence missing.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; issue update and QA steps incomplete.

### #27 Formatters + parser
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Yes.
- **Dependencies explicit:** Not required.
- **Plan actionable:** Partially; issue update and QA steps incomplete.

### #28 CI coverage gate
- **Supports primary objective:** Yes.
- **Acceptance criteria testable:** Partially; CI evidence missing.
- **Dependencies explicit:** Ratchet gates in `orchestration.md`.
- **Plan actionable:** Partially; documentation and evidence missing.

---

## Acceptance criteria delivery (evidence-first)

### Feature #21 — enhance-tests
1. **Tests fail before and pass after.** **Status: Unknown** — no pre/post failure evidence recorded.
2. **Speakerless routing and constraint handling scenarios exercised.** **Status: Met** — `tests/transform/test_enhance.py` includes speakerless and constraint tests.
3. **Coverage report shows ≥70% for `transform/enhance.py`.** **Status: Unknown (stale metric)** — coverage output in `plan.2026-02-02T11-49.md` is doc-only and dated 2026-02-02.

### Feature #22 — speakerless-heuristics
1. **Positive/negative cases for heuristics.** **Status: Met** — tests in `tests/transform/test_speakerless.py`.
2. **Addressee reassignment behavior covered.** **Status: Met** — tests in `tests/transform/test_speaker_helpers.py`.
3. **Similarity grouping boundary cases covered.** **Status: Met** — tests in `tests/transform/test_speaker_helpers.py`.
4. **Coverage ≥70% for `speakerless.py` and `speaker_helpers.py`.** **Status: Unknown** — no recorded coverage report.
5. **Deterministic tests without filesystem/temp files.** **Status: Met** — tests are in-memory.
6. **Issue #22 updated with coverage evidence and links.** **Status: Not met** — no issue update recorded.

### Feature #23 — identity-normalize
1. **Tests cover branches and edge cases.** **Status: Met** — `tests/transform/test_identity_constraints.py`, `tests/transform/test_normalize.py`.
2. **Tests assert explicit constraints and normalized outputs.** **Status: Met** — same files.
3. **Combined coverage ≥75%.** **Status: Unknown (stale metric)** — `coverage-results.md` is doc-only and lacks timestamp.
4. **Deterministic tests without filesystem/temp files.** **Status: Met** — in-memory tests.
5. **Issue #23 updated with coverage evidence and links.** **Status: Not met** — no issue update recorded.

### Feature #24 — multi-speaker-fixtures
1. **Shared fixtures for 3+ speakers.** **Status: Met** — `tests/fixtures/multi_speaker.py`.
2. **Regression tests reference fixtures.** **Status: Met** — `tests/transform/test_multi_speaker_regression.py`.
3. **Fixture validation tests fail fast on malformed data.** **Status: Met** — fixture validation tests present.
4. **Known gaps captured as `xfail`.** **Status: Met** — xfail cases in regression suite.
5. **Deterministic tests without external deps.** **Status: Met** — in-memory fixtures.

### Feature #25 — e2e-speakerless-notes
1. **Speakerless CLI flows for DOCX/MD/RTF.** **Status: Met** — `tests/integration/test_cli_e2e_speakerless.py` (DOCX, MD, RTF). 
2. **Notes-only and notes+transcript flows (incl. update mode).** **Status: Met** — `tests/integration/test_cli_e2e_notes.py`.
3. **Error handling for missing files/invalid args.** **Status: Met** — error handling tests in both integration suites.
4. **Output validation via text markers.** **Status: Met** — `_document_text` assertions on markers.

### Feature #26 — notes-regressions
1. **Each known bug has a regression test.** **Status: Met** — `tests/transform/test_notes.py`.
2. **Regression tests demonstrate prior failures and now pass.** **Status: Unknown** — no pre-failure evidence recorded.
3. **Coverage improves on notes paths.** **Status: Unknown** — no recorded coverage evidence tied to notes module.

### Feature #27 — formatters-parser
1. **Tests assert formatting/spacing rules and parsed structures.** **Status: Met** — `tests/formatters/*`, `tests/document/test_parser_unit.py`.
2. **Coverage ≥70% for formatter/parser modules.** **Status: Unknown (stale metric)** — plan references coverage but no fresh report.
3. **Avoid brittle DOCX binary assertions.** **Status: Met** — tests are in-memory.
4. **Deterministic tests without external deps.** **Status: Met** — unit-level tests only.

### Feature #28 — ci-coverage-gate
1. **CI runs pytest-cov and fails below floor.** **Status: Partial/Unknown** — CI config updated, no run evidence.
2. **CI passes when coverage meets/exceeds floor.** **Status: Unknown** — no run evidence.
3. **CI surfaces coverage results in logs + step summary.** **Status: Met (configured)** — `ci.yml` summary step exists.
4. **CI uploads coverage artifacts.** **Status: Met (configured)** — `ci.yml` artifact upload steps exist.
5. **Documentation explains how to adjust `fail_under`.** **Status: Not met** — documentation update missing.

---

## Plan reconciliation (auto-checked items)

**Auto-checked in this audit:**
- `2025-12-04-multi-speaker-fixtures-24/plan.2026-02-02T13-09.md` — `TASK-P3-T1` (issue doc updated with fixture/test paths).

**Evidence:** `2025-12-04-multi-speaker-fixtures-24/issue.md` Sync Summary includes paths to `tests/fixtures/multi_speaker.py` and `tests/transform/test_multi_speaker_regression.py`.

---

## Merge readiness posture

**Status: Blocked** — multiple acceptance criteria remain not met or unverified (#21, #22, #23, #26, #27, #28), and several plan items remain incomplete (coverage evidence, issue updates, CI proof, and QA toolchain steps).