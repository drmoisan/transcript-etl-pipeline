# Remediation Inputs — 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-02T15-20

## Delivery gaps (acceptance criteria + plan items)

1. **#21 Enhance tests coverage target not met**
   - **Where:** `coverage.xml`, `tests/transform/test_enhance.py`
   - **Expected content:** Module coverage for `src/transcript_etl_pipeline/transform/enhance.py` ≥ 70%.
   - **Done criteria:** Coverage report shows `enhance.py` ≥ 70%; plan tasks P4-T1/P5-T1..P5-T4 completed.

2. **#22 Speakerless heuristics coverage targets not met**
   - **Where:** `coverage.xml`, `tests/transform/test_speakerless.py`, `tests/transform/test_speaker_helpers.py`
   - **Expected content:** Coverage for `speakerless.py` and `speaker_helpers.py` ≥ 70% with explicit heuristic coverage.
   - **Done criteria:** Coverage report shows both modules ≥ 70%; missing heuristic cases (tag/rhetorical questions) explicitly tested.

3. **#23 Identity + normalize coverage targets not met**
   - **Where:** `coverage.xml`, `tests/transform/test_identity_constraints.py`, `tests/transform/test_normalize.py`
   - **Expected content:** Combined coverage for `identity_constraints.py` and `normalize.py` ≥ 75%.
   - **Done criteria:** Coverage report shows target met; normalize test plan tasks P3-T1..P3-T9 completed.

4. **#26 Notes regressions acceptance criteria not evidenced**
   - **Where:** `tests/transform/test_notes.py`, `2025-12-04-notes-regressions-26/spec.md`
   - **Expected content:** Regression tests that document known failures and now pass; measurable coverage improvement for notes.
   - **Done criteria:** Tests map to known bugs with failing-before evidence; coverage for `notes.py` improved and documented.

5. **#27 Formatters + parser coverage targets not met**
   - **Where:** `coverage.xml`, `tests/formatters/test_*`, `tests/document/test_parser_unit.py`
   - **Expected content:** Coverage ≥ 70% for docx/rtf/md formatters and parser with deterministic, in-memory tests.
   - **Done criteria:** Coverage report shows all modules ≥ 70%; temp-file usage removed per plan.

6. **#25 E2E CLI tests violate unit-test policy**
   - **Where:** `tests/integration/test_cli_e2e_speakerless.py`, `tests/integration/test_cli_e2e_notes.py`
   - **Expected content:** Integration tests avoid temporary files (policy) or a documented approved exception.
   - **Done criteria:** Tests refactored to in-memory stubs OR an explicit policy exception approved and documented in feature spec.

7. **Test-policy violations (temp files + external downloads)**
   - **Where:** `tests/formatters/test_md_formatter.py`, `tests/formatters/test_rtf_formatter.py`, `tests/formatters/test_docx_formatter.py`, `tests/integration/test_cli_e2e_*.py`, `tests/transform/test_speaker_helpers.py`
   - **Expected content:** No temporary filesystem usage; no external downloads.
   - **Done criteria:** All tests comply with no-temp-files rule; NLTK download path removed or mocked.

8. **Plan checklists incomplete**
   - **Where:** `plan.<timestamp>.md` files for #21–#28
   - **Expected content:** Completed plan items checked off with evidence; remaining items either delivered or explicitly deferred.
   - **Done criteria:** Plan items fully reconciled; evidence added where required.

## MVP definition gaps (non-blocking documentation)

9. **MVP boundaries + metrics not explicit in `initiative.md`**
   - **Where:** `initiative.md`
   - **Expected content:** Explicit MVP scope, module list, and measurement criteria.
   - **Done criteria:** MVP definition added with measurable criteria (non-blocking for merge readiness).

## Orchestration inconsistencies

10. **Milestone status mismatch**
   - **Where:** `initiative.md` → “Milestones & Status”
   - **Expected content:** Status aligned with feature plan states (Planned/Draft/In Progress).
   - **Done criteria:** Epic milestone statuses reflect actual feature plan states.

11. **Coverage gate sequencing criteria missing**
   - **Where:** `orchestration.md`, `2025-12-04-ci-coverage-gate-28/spec.md`
   - **Expected content:** Explicit ratchet criteria tied to coverage targets and milestone completion.
   - **Done criteria:** Sequencing criteria documented and consistent.

## Feature-level doc gaps (non-blocking documentation)

12. **#24 fixture ownership & reuse governance**
   - **Where:** `2025-12-04-multi-speaker-fixtures-24/spec.md`
   - **Expected content:** Fixture ownership and update process.
   - **Done criteria:** Section added documenting ownership and reuse rules.

13. **#25 policy compliance decision**
   - **Where:** `2025-12-04-e2e-speakerless-notes-25/spec.md`
   - **Expected content:** Explicit decision on temp-file policy (exception or redesign).
   - **Done criteria:** Policy compliance note added.

## Do-not-do list

- Do not expand scope beyond the baseline coverage epic.
- Do not rewrite feature specs; add missing sections only.
- Do not change policy documents; document exceptions or redesign tests to comply.
