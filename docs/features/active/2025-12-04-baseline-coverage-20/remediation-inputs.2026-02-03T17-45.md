# Remediation Inputs — 2025-12-04-baseline-coverage-20

## Trigger

Remediation required due to unmet/unknown acceptance criteria, incomplete plan items, and policy non-compliance (toolchain evidence and verified coverage metrics missing).

---

## Delivery gaps (acceptance criteria + plan items)

### Epic-level
1. **Run full toolchain and capture verified evidence**
   - **Why:** Policy requires format → lint → type-check → test in a single clean pass.
   - **Where:** Repo root; record outputs in feature plans and audit evidence.
   - **Done when:** Commands `poetry run black .`, `poetry run ruff check`, `poetry run pyright`, `poetry run pytest` all pass in sequence and outputs recorded with timestamps.

2. **Capture verified coverage metrics (replace stale doc-only claims)**
   - **Why:** Current coverage claims are doc-only and **Stale**; cannot be used to satisfy acceptance criteria.
   - **Where:** Coverage outputs (`coverage.xml`, CI run URLs) referenced in feature docs.
   - **Done when:** Verified coverage evidence exists for epic-wide coverage and feature-specific targets.

3. **Add execution owner/timebox to the initiative**
   - **Why:** Initiative lacks capacity/ownership, impacting delivery planning.
   - **Where:** `initiative.md`.
   - **Done when:** Owner and timebox are explicit and current.

### #21 enhance-tests
1. **Record pre/post regression evidence and update Issue #21**
   - **Where:** `plan.2026-02-02T11-49.md` and `issue.md`.
   - **Done when:** Test-run outputs are recorded with timestamps and Issue #21 references evidence.

2. **Verify coverage ≥70% with current tool output**
   - **Where:** Coverage output recorded in plan or issue.
   - **Done when:** Verified output (toolchain or coverage.xml) shows target met.

### #22 speakerless-heuristics
1. **Record coverage evidence for `speakerless.py` + `speaker_helpers.py`**
   - **Where:** `plan.2026-02-02T12-24.md` and Issue #22.
   - **Done when:** Verified output shows ≥70% and issue updated with evidence.

2. **Complete QA toolchain steps in plan**
   - **Where:** `plan.2026-02-02T12-24.md`.
   - **Done when:** Phase 4 tasks are checked with evidence notes.

### #23 identity-normalize
1. **Update Issue #23 with verified coverage evidence**
   - **Where:** `issue.md` referencing `coverage-results.md` plus tool output.
   - **Done when:** Issue includes command + verified coverage values.

2. **Complete QA toolchain steps in plan**
   - **Where:** `plan.2026-02-02T13-08.md`.
   - **Done when:** Phase 5 tasks are checked with evidence notes.

### #24 multi-speaker-fixtures
1. **Complete QA toolchain steps**
   - **Where:** `plan.2026-02-02T13-09.md`.
   - **Done when:** QA phase tasks are checked with evidence notes.

### #25 e2e-speakerless-notes
1. **Complete remaining plan scenarios (if still required)**
   - **Where:** `tests/integration/test_cli_e2e_speakerless.py` + plan tasks.
   - **Gaps:** panel DOCX scenario, additional MD/RTF scenarios, update-file reader test.
   - **Done when:** P1-T5, P1-T7, P1-T8, P1-T9, P2-T6 implemented or plan updated to reflect scope change.

2. **Capture verified coverage evidence for CLI/reader/notes/formatters**
   - **Where:** Plan Phase 3 and `coverage.xml`.
   - **Done when:** Verified outputs recorded with timestamps.

3. **Update prompt doc with runtime/edge-case notes**
   - **Where:** `25-e2e-speakerless-notes.prompt.md`.
   - **Done when:** Runtime/edge cases noted and referenced in plan.

### #26 notes-regressions
1. **Document pre/post regression evidence**
   - **Where:** Plan Phase 2 notes or issue update.
   - **Done when:** Failing-before and passing-after outputs recorded.

2. **Update Issue #26 with results and links**
   - **Where:** `issue.md`.
   - **Done when:** Issue includes evidence and references.

### #27 formatters-parser
1. **Update Issue #27 with verified coverage evidence**
   - **Where:** `issue.md`.
   - **Done when:** Issue includes coverage output and command.

2. **Complete QA toolchain steps in plan**
   - **Where:** `plan.2026-02-02T13-08.md`.
   - **Done when:** Phase 6 tasks checked with evidence notes.

### #28 ci-coverage-gate
1. **Document `fail_under` ratchet guidance**
   - **Where:** `issue.md` or a new `28-ci-coverage-gate.md` in the feature folder.
   - **Done when:** Documentation explains how to adjust `fail_under` and ratchet milestones.

2. **Attach CI run evidence**
   - **Where:** Issue #28 or feature doc.
   - **Done when:** CI run link includes coverage summary and artifact references.

---

## MVP definition gaps

- Explicit owner/timebox for epic execution.
- Verified coverage evidence for coverage floor ratchet and CI proof.

---

## Orchestration inconsistencies

- None found; sequencing is documented. Evidence missing for gates.

---

## Feature-level doc gaps

- Multiple issue update tasks remain incomplete (#21, #22, #23, #25, #26, #27, #28).
- CI coverage gate documentation missing in feature folder (#28).

---

## Do-not-do list

- Do not expand scope beyond baseline coverage initiative.
- Do not treat stale, doc-only metrics as blocking evidence.
- Do not relax coverage policy without explicit approval.
- Do not add filesystem-based tests that violate unit-test policy.
