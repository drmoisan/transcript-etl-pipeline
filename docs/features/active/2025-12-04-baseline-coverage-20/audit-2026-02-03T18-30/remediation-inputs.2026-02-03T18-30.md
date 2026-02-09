# Remediation Inputs — 2025-12-04-baseline-coverage-20

**Generated:** 2026-02-03

## Delivery Gaps (Acceptance Criteria + Plan Items)

### Epic-Level Evidence Gaps

1. **Coverage evidence is stale or missing**
   - **Where:** Feature plans and notes across #21–#28.
   - **Expected:** Verified toolchain outputs with timestamps and commands, stored in canonical `baseline/` locations (epic root for epic baseline; feature root for feature baseline; next to version plan for version baseline).
   - **Done looks like:** Each feature plan references verified coverage outputs; `baseline/` folders populated with toolchain logs.

2. **Issue updates missing for multiple features**
   - **Where:** Issues #21–#28.
   - **Expected:** Issue updates with coverage/test evidence and PR links where applicable.
   - **Done looks like:** Each issue contains links or summaries of evidence (coverage results and test runs).

### Feature-Level Gaps

#### #21 enhance-tests
- **Gap:** Acceptance criteria still missing evidence for fail-before/pass-after and verified coverage.
- **Expected:** Add explicit regression evidence and update Issue #21.

#### #22 speakerless-heuristics
- **Gap:** Coverage evidence for `speakerless.py`/`speaker_helpers.py` missing; Issue #22 update missing; QA phase incomplete.
- **Expected:** Run coverage with module-specific thresholds and update Issue #22.

#### #23 identity-normalize
- **Gap:** Issue #23 update missing; QA phase incomplete; coverage evidence lacks timestamp.
- **Expected:** Capture and store coverage output with timestamp; update Issue #23.

#### #24 multi-speaker-fixtures
- **Gap:** Plan P3-T2 (prompt update) and QA evidence incomplete.
- **Expected:** Update `24-multi-speaker-fixtures.prompt.md` with test results; run QA toolchain and record outputs.

#### #25 e2e-speakerless-notes
- **Gap:** Missing planned scenarios (panel DOCX, additional MD/RTF cases, update-file reader test), coverage evidence missing, prompt update incomplete.
- **Expected:** Implement missing tests, capture coverage evidence, update prompt and Issue #25.

#### #26 notes-regressions
- **Gap:** No fail-before/pass-after evidence; Issue #26 update missing; QA incomplete.
- **Expected:** Capture regression evidence, update Issue #26, and store coverage outputs.

#### #27 formatters-parser
- **Gap:** Issue #27 update missing; QA incomplete; coverage evidence needs verification.
- **Expected:** Run coverage report with fail-under and update Issue #27.

#### #28 ci-coverage-gate
- **Gap:** Documentation update missing (`fail_under` ratchet guidance) and no CI run evidence.
- **Expected:** Update docs in feature folder and capture CI run evidence (logs/summary/artifacts).

## MVP Definition Gaps

- **None explicit** beyond acceptance-criteria evidence and plan completion.

## Orchestration Inconsistencies

- **None identified.** Sequencing in `orchestration.md` aligns with feature plans.

## Feature Doc Gaps

- Missing prompt or doc updates referenced in plan tasks for #24–#28.

## Do Not Do (Scope Guardrails)

- Do not expand scope beyond the defined feature plans.
- Do not change production logic unless required by an explicit plan task.
- Do not weaken coverage thresholds or testing policies.

## Minimum Changes Required for Acceptance Criteria Closure

- Complete missing plan tasks for #21–#28 (evidence runs, issue updates, remaining test scenarios).
- Capture and store baseline and verification outputs in canonical `baseline/` folders.
- Update feature docs and issues with verified evidence.
