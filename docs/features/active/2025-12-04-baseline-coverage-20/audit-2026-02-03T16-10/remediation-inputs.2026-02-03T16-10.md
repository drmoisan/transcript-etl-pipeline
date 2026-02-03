# Remediation Inputs — 2025-12-04-baseline-coverage-20

## Trigger

Remediation required due to unmet/unknown acceptance criteria and incomplete plan items across features, plus policy non-compliance (coverage minimum and toolchain execution).

---

## Delivery gaps (acceptance criteria + plan items)

### Epic-level
1. **Run full toolchain and capture evidence**
   - **Why:** Policy requires format → lint → type-check → test in a single clean pass.
   - **Where:** Repo root; record in feature plans and policy audit.
   - **Done when:** Commands `poetry run black .`, `poetry run ruff check`, `poetry run pyright`, `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing` all pass in sequence and outputs recorded.

2. **Address repo-wide coverage minimum (80%) policy gap**
   - **Why:** Current reported coverage (~45%) fails policy requirement (>=80%).
   - **Where:** Additional tests in core modules; update epic `initiative.md` or create explicit exception plan if policy allows.
   - **Done when:** Coverage report shows >=80% or a formally approved exception is documented.

### #21 enhance-tests
1. **Capture pre/post regression evidence and targeted test run outputs**
   - **Where:** `plan.2026-02-02T11-49.md` Open Questions / Notes section.
   - **Done when:** Baseline coverage block (labeled) and targeted test runs recorded; issue #21 updated.

### #22 speakerless-heuristics
1. **Record coverage evidence for `speakerless.py` + `speaker_helpers.py`**
   - **Where:** Add report output to plan notes; update Issue #22.
   - **Done when:** `coverage report --fail-under=70` passes with recorded output.

2. **Complete plan QA steps**
   - **Where:** `plan.2026-02-02T12-24.md`.
   - **Done when:** P4 toolchain steps are checked with evidence.

### #23 identity-normalize
1. **Update Issue #23 with coverage results**
   - **Where:** Issue #23; link `coverage-results.md`.
   - **Done when:** Issue includes coverage table and command.

2. **Complete QA steps in plan**
   - **Where:** `plan.2026-02-02T13-08.md`.
   - **Done when:** P5 toolchain steps recorded and checked.

### #24 multi-speaker-fixtures
1. **Update issue doc with fixture locations/usage**
   - **Where:** `2025-12-04-multi-speaker-fixtures-24/issue.md`.
   - **Done when:** paths to `tests/fixtures/multi_speaker.py` and `tests/transform/test_multi_speaker_regression.py` are documented.

### #25 e2e-speakerless-notes
1. **Complete remaining planned scenarios (if still required)**
   - **Where:** `tests/integration/test_cli_e2e_speakerless.py`.
   - **Gap:** Missing panel DOCX test, additional MD/RTF scenarios per plan.
   - **Done when:** P1-T5, P1-T7, P1-T8, P1-T9 implemented or plan updated to reflect scope change.

2. **Coverage evidence capture**
   - **Where:** Plan Phase 3; record coverage.xml/summary for CLI/reader/notes/formatters.
   - **Done when:** coverage evidence recorded and plan tasks checked.

3. **Doc updates**
   - **Where:** Feature docs in `2025-12-04-e2e-speakerless-notes-25/`.
   - **Done when:** plan P3-T3 updated with runtime/edge case notes.

### #26 notes-regressions
1. **Document pre/post regression evidence**
   - **Where:** Plan Phase 2 notes or issue update.
   - **Done when:** tests show prior failure and current pass, recorded in plan/issue.

2. **Update Issue #26**
   - **Where:** Issue #26 with results and PR links.
   - **Done when:** issue updated and plan task checked.

### #27 formatters-parser
1. **Update Issue #27 with coverage evidence**
   - **Where:** Issue #27; include `coverage report --fail-under=70` output.
   - **Done when:** issue updated and plan task checked.

2. **Complete QA toolchain steps**
   - **Where:** `plan.2026-02-02T13-08.md` Phase 6.
   - **Done when:** toolchain steps recorded and checked.

### #28 ci-coverage-gate
1. **Documentation update explaining `fail_under` ratchet**
   - **Where:** Feature doc referenced in plan (missing in folder); update `issue.md` or create `28-ci-coverage-gate.md` with guidance.
   - **Done when:** documentation explicitly explains how to adjust `fail_under` and ratchet plan.

2. **CI evidence**
   - **Where:** Link CI run in issue #28 or feature doc.
   - **Done when:** CI logs show coverage summary + artifacts; issue updated.

---

## MVP definition gaps

- Explicit owner/timebox for epic execution.
- Explicit acceptance evidence for coverage floor ratchet and CI proof.

---

## Orchestration inconsistencies

- None found; sequencing is documented. Evidence missing for gates.

---

## Feature-level doc gaps

- Multiple issue update tasks remain incomplete (#21, #22, #23, #26, #27, #28).
- CI coverage gate documentation missing in feature folder (#28).

---

## Do-not-do list

- Do not expand scope beyond baseline coverage initiative.
- Do not relax coverage policy without explicit approval.
- Do not add filesystem-based tests that violate unit-test policy.
