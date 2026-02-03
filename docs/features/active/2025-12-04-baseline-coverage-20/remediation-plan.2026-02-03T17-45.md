# Remediation Plan — 2025-12-04-baseline-coverage-20 (2026-02-03)

## Overview

Remediate the baseline coverage epic by closing evidence gaps, completing outstanding plan items, and recording verified toolchain and coverage results across epic and child features without expanding scope.

## Success Criteria

- Verified toolchain evidence exists for a single clean pass of format → lint → type-check → test, with timestamps and references in epic audit docs and relevant feature plans.
- Verified coverage evidence (overall and per-module targets) is captured from current tool output and linked in epic and child feature issue/plan documents.
- `initiative.md` explicitly lists an execution owner and timebox.
- Each child feature (#21–#28) has its plan and issue updated to reflect completed QA steps and evidence links.
- Missing E2E scenarios for #25 are implemented and recorded, or clearly scoped with documented evidence.
- CI coverage gate guidance and run evidence are documented for #28.
- Final QA log documents doc-structure checks, doc linting, and link checks (when available), plus a clean Python toolchain pass.

## Plan

### Phase 0 — Context & Inputs
- [ ] [P0-T1] Read `.github/copilot-instructions.md` to confirm repo-wide policies and scope guardrails.
  - Acceptance: Notes in this plan’s “Success Criteria” align with the policy stated in `.github/copilot-instructions.md`.
- [ ] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm workflow and toolchain requirements.
  - Acceptance: This plan references the format → lint → type-check → test sequence and restart-on-failure behavior.
- [ ] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm test constraints (no temp files, isolation, coverage rules).
  - Acceptance: Any test-related tasks in this plan explicitly avoid filesystem temp usage and external dependencies.
- [ ] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` to confirm Python formatting, linting, and typing rules.
  - Acceptance: QA tasks in this plan use Black, Ruff, and Pyright in the required order.
- [ ] [P0-T5] Read `.github/instructions/python-unit-test.instructions.md` to confirm approved Pytest command and coverage expectations.
  - Acceptance: The QA testing task uses the approved Pytest command verbatim.
- [ ] [P0-T6] Read `.github/instructions/python-suppressions.instructions.md` to confirm suppression rules.
  - Acceptance: Any planned test/code tasks avoid adding new suppressions without approval.
- [ ] [P0-T7] Read `.github/instructions/self-explanatory-code-commenting.instructions.md` to confirm docstring and comment expectations.
  - Acceptance: Test-related tasks explicitly include docstrings and intent-level comments where required.
- [ ] [P0-T8] Read `docs/features/active/2025-12-04-baseline-coverage-20/remediation-inputs.2026-02-03T17-45.md` to confirm remediation gaps.
  - Acceptance: All gap categories in the remediation inputs appear as task groups in Phases 2–5.
- [ ] [P0-T9] Read `docs/features/active/2025-12-04-baseline-coverage-20/initiative.md` to confirm epic scope and module targets.
  - Acceptance: Success Criteria and coverage evidence tasks align with the module targets listed in the initiative doc.
- [ ] [P0-T10] Read `docs/features/active/2025-12-04-baseline-coverage-20/issue.md` to confirm epic tracking requirements.
  - Acceptance: Epic issue update tasks reference this file path explicitly.
- [ ] [P0-T11] Read `docs/features/active/2025-12-04-baseline-coverage-20/orchestration.md` to confirm sequencing and ratchet gates.
  - Acceptance: Evidence capture tasks respect the sequencing and gating noted in orchestration.
- [ ] [P0-T12] Read `docs/features/active/2025-12-04-baseline-coverage-20/epic-audit.2026-02-03T17-45.md` for audit findings and evidence expectations.
  - Acceptance: Epic audit update tasks target this exact file.
- [ ] [P0-T13] Read `docs/features/active/2025-12-04-baseline-coverage-20/policy-audit.2026-02-03T17-45.md` for policy evidence requirements.
  - Acceptance: Toolchain evidence tasks include updates to this file.
- [ ] [P0-T14] Read `docs/features/active/2025-12-04-baseline-coverage-20/feature-delivery-inventory.2026-02-03T17-45.md` to confirm per-feature tracking.
  - Acceptance: Feature update tasks reference the tracked issues and artifacts listed in the inventory.
- [ ] [P0-T15] Update the “Success Criteria” section in this plan with any missing measurable outcomes discovered in Phase 0.
  - Acceptance: The “Success Criteria” section reflects any additions with explicit, verifiable outcomes.
- [ ] [P0-T16] Create `docs/features/active/2025-12-04-baseline-coverage-20/audit-2026-02-03T17-45/` to store remediation evidence.
  - Acceptance: The new directory exists at the specified path.
- [ ] [P0-T17] Create `docs/features/active/2025-12-04-baseline-coverage-20/audit-2026-02-03T17-45/toolchain-baseline.md` with a timestamped header.
  - Acceptance: The file exists and contains a timestamped header and an empty “Baseline Outputs” section.
- [ ] [P0-T18] Run `poetry run black .` and append output to `toolchain-baseline.md`.
  - Acceptance: `toolchain-baseline.md` contains the command output and timestamp for the Black run.
- [ ] [P0-T19] Run `poetry run ruff check` and append output to `toolchain-baseline.md`.
  - Acceptance: `toolchain-baseline.md` contains the command output and timestamp for the Ruff run.
- [ ] [P0-T20] Run `poetry run pyright` and append output to `toolchain-baseline.md`.
  - Acceptance: `toolchain-baseline.md` contains the command output and timestamp for the Pyright run.
- [ ] [P0-T21] Run `poetry run pytest --cov=src/lexile_corpus_tuner --cov=scripts/dev_tools --cov-report=term-missing` and append output to `toolchain-baseline.md`.
  - Acceptance: `toolchain-baseline.md` contains the command output and timestamp for the Pytest run.

### Phase 1 — Discovery & Target Mapping
- [ ] [P1-T1] Identify any existing doc structure check tooling in `docs/` and `scripts/` and record the command in this plan’s “Doc QA Tools” section.
  - Acceptance: The “Doc QA Tools” section lists a doc-structure command or explicitly states “Not available.”
- [ ] [P1-T2] Identify any Markdown lint tooling in repo scripts or docs and record the command in this plan’s “Doc QA Tools” section.
  - Acceptance: The “Doc QA Tools” section lists a doc-lint command or explicitly states “Not available.”
- [ ] [P1-T3] Identify any link-check tooling in repo scripts or docs and record the command in this plan’s “Doc QA Tools” section.
  - Acceptance: The “Doc QA Tools” section lists a link-check command or explicitly states “Not available.”
- [ ] [P1-T4] Record the insertion points for epic-level evidence updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `initiative.md`, `issue.md`, `epic-audit.2026-02-03T17-45.md`, and `policy-audit.2026-02-03T17-45.md`.
- [ ] [P1-T5] Record insertion points for #21 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md` and `2025-12-04-enhance-tests-21/issue.md`.
- [ ] [P1-T6] Record insertion points for #22 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-speakerless-heuristics-22/plan.2026-02-02T12-24.md` and `2025-12-04-speakerless-heuristics-22/issue.md`.
- [ ] [P1-T7] Record insertion points for #23 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-identity-normalize-23/plan.2026-02-02T13-08.md`, `2025-12-04-identity-normalize-23/coverage-results.md`, and `2025-12-04-identity-normalize-23/issue.md`.
- [ ] [P1-T8] Record insertion points for #24 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-multi-speaker-fixtures-24/plan.2026-02-02T13-09.md` and `2025-12-04-multi-speaker-fixtures-24/issue.md`.
- [ ] [P1-T9] Record insertion points for #25 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-e2e-speakerless-notes-25/plan.2026-02-02T12-45.md`, `2025-12-04-e2e-speakerless-notes-25/issue.md`, and `2025-12-04-e2e-speakerless-notes-25/25-e2e-speakerless-notes.prompt.md`.
- [ ] [P1-T10] Record insertion points for #26 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-notes-regressions-26/plan.2026-02-02T13-09.md` and `2025-12-04-notes-regressions-26/issue.md`.
- [ ] [P1-T11] Record insertion points for #27 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-formatters-parser-27/plan.2026-02-02T13-08.md` and `2025-12-04-formatters-parser-27/issue.md`.
- [ ] [P1-T12] Record insertion points for #28 updates in this plan’s “Update Map” section.
  - Acceptance: The “Update Map” section lists target headings/anchors for `2025-12-04-ci-coverage-gate-28/plan.2025-12-04T11-43.md`, `2025-12-04-ci-coverage-gate-28/issue.md`, and the new CI guidance doc in Phase 4.

### Phase 2 — Test/Code Remediation (#25)
- [ ] [P2-T1] Add the panel DOCX scenario test to `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: The test file contains a new test case for the panel DOCX scenario with no temporary filesystem usage.
- [ ] [P2-T2] Add the additional Markdown scenario test to `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: The test file contains a new test case for the additional Markdown scenario with no temporary filesystem usage.
- [ ] [P2-T3] Add the additional RTF scenario test to `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: The test file contains a new test case for the additional RTF scenario with no temporary filesystem usage.
- [ ] [P2-T4] Add the update-file reader test to `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: The test file contains a new test case for the update-file reader scenario with no temporary filesystem usage.

### Phase 3 — Evidence Capture (Toolchain + Coverage)
- [ ] [P3-T1] Create `docs/features/active/2025-12-04-baseline-coverage-20/audit-2026-02-03T17-45/toolchain-final.md` with a timestamped header.
  - Acceptance: The file exists and contains a timestamped header and an empty “Final Outputs” section.
- [ ] [P3-T2] Run `poetry run black .` and append output to `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` contains the command output and timestamp for the Black run.
- [ ] [P3-T3] Run `poetry run ruff check` and append output to `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` contains the command output and timestamp for the Ruff run.
- [ ] [P3-T4] Run `poetry run pyright` and append output to `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` contains the command output and timestamp for the Pyright run.
- [ ] [P3-T5] Run `poetry run pytest --cov=src/lexile_corpus_tuner --cov=scripts/dev_tools --cov-report=term-missing` and append output to `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` contains the command output and timestamp for the Pytest run.
- [ ] [P3-T6] Create `docs/features/active/2025-12-04-baseline-coverage-20/audit-2026-02-03T17-45/coverage-evidence.md` with a timestamped header.
  - Acceptance: The file exists and contains a timestamped header and an empty “Coverage Outputs” section.
- [ ] [P3-T7] Run coverage with XML output using `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing --cov-report=xml` and append terminal output to `coverage-evidence.md`.
  - Acceptance: `coverage.xml` timestamp is on/after the run and `coverage-evidence.md` contains the command output and timestamp.
- [ ] [P3-T8] Record per-module coverage percentages for the initiative targets in `coverage-evidence.md` using `coverage.xml`.
  - Acceptance: `coverage-evidence.md` includes a table with coverage percentages for all modules listed in `initiative.md`.

### Phase 4 — Documentation Updates (Epic + Feature Evidence)
- [ ] [P4-T1] Update `initiative.md` to include an execution owner and explicit timebox.
  - Acceptance: The initiative document lists an owner name and a timebox window with dates.
- [ ] [P4-T2] Update `epic-audit.2026-02-03T17-45.md` with links to `toolchain-final.md` and `coverage-evidence.md`.
  - Acceptance: The epic audit includes references to both evidence files.
- [ ] [P4-T3] Update `policy-audit.2026-02-03T17-45.md` with links to `toolchain-final.md` and `coverage-evidence.md`.
  - Acceptance: The policy audit includes references to both evidence files.
- [ ] [P4-T4] Update `issue.md` (epic root) with links to `toolchain-final.md` and `coverage-evidence.md`.
  - Acceptance: The epic issue includes references to both evidence files.
- [ ] [P4-T5] Update `2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md` with pre/post regression evidence links.
  - Acceptance: The plan includes timestamps and links to evidence files for the regression runs.
- [ ] [P4-T6] Update `2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md` with verified coverage evidence links.
  - Acceptance: The plan references `coverage-evidence.md` with the relevant coverage values.
- [ ] [P4-T7] Update `2025-12-04-enhance-tests-21/issue.md` with links to the regression and coverage evidence.
  - Acceptance: The issue lists evidence links and timestamps.
- [ ] [P4-T8] Update `2025-12-04-speakerless-heuristics-22/plan.2026-02-02T12-24.md` with coverage evidence for `speakerless.py` and `speaker_helpers.py`.
  - Acceptance: The plan references `coverage-evidence.md` and includes the two module percentages.
- [ ] [P4-T9] Update `2025-12-04-speakerless-heuristics-22/plan.2026-02-02T12-24.md` to mark QA toolchain steps complete with evidence links.
  - Acceptance: The QA phase tasks are checked with a link to `toolchain-final.md`.
- [ ] [P4-T10] Update `2025-12-04-speakerless-heuristics-22/issue.md` with coverage evidence links.
  - Acceptance: The issue references `coverage-evidence.md` and module percentages.
- [ ] [P4-T11] Update `2025-12-04-identity-normalize-23/coverage-results.md` with verified coverage values from `coverage-evidence.md`.
  - Acceptance: The coverage results doc includes current percentages and a timestamp.
- [ ] [P4-T12] Update `2025-12-04-identity-normalize-23/plan.2026-02-02T13-08.md` to mark QA toolchain steps complete with evidence links.
  - Acceptance: The plan’s QA tasks are checked with a link to `toolchain-final.md`.
- [ ] [P4-T13] Update `2025-12-04-identity-normalize-23/issue.md` with verified coverage evidence links.
  - Acceptance: The issue references `coverage-results.md` and `coverage-evidence.md` with timestamps.
- [ ] [P4-T14] Update `2025-12-04-multi-speaker-fixtures-24/plan.2026-02-02T13-09.md` to mark QA toolchain steps complete with evidence links.
  - Acceptance: The plan’s QA tasks are checked with a link to `toolchain-final.md`.
- [ ] [P4-T15] Update `2025-12-04-e2e-speakerless-notes-25/plan.2026-02-02T12-45.md` to mark the new scenario tasks complete with evidence links.
  - Acceptance: The plan references the new test cases and includes evidence links.
- [ ] [P4-T16] Update `2025-12-04-e2e-speakerless-notes-25/plan.2026-02-02T12-45.md` with verified coverage evidence for CLI/reader/notes/formatters.
  - Acceptance: The plan references `coverage-evidence.md` and lists the relevant module percentages.
- [ ] [P4-T17] Update `2025-12-04-e2e-speakerless-notes-25/25-e2e-speakerless-notes.prompt.md` with runtime and edge-case notes.
  - Acceptance: The prompt doc contains a “Runtime/Edge Cases” section with at least two specific notes.
- [ ] [P4-T18] Update `2025-12-04-e2e-speakerless-notes-25/issue.md` with scenario completion and coverage evidence links.
  - Acceptance: The issue references the plan updates and `coverage-evidence.md`.
- [ ] [P4-T19] Update `2025-12-04-notes-regressions-26/plan.2026-02-02T13-09.md` with pre/post regression evidence links.
  - Acceptance: The plan includes timestamps and links to evidence files for the regression runs.
- [ ] [P4-T20] Update `2025-12-04-notes-regressions-26/issue.md` with regression evidence links.
  - Acceptance: The issue references the plan evidence with timestamps.
- [ ] [P4-T21] Update `2025-12-04-formatters-parser-27/plan.2026-02-02T13-08.md` to mark QA toolchain steps complete with evidence links.
  - Acceptance: The plan’s QA tasks are checked with a link to `toolchain-final.md`.
- [ ] [P4-T22] Update `2025-12-04-formatters-parser-27/issue.md` with verified coverage evidence links.
  - Acceptance: The issue references `coverage-evidence.md` and module percentages.
- [ ] [P4-T23] Create `2025-12-04-ci-coverage-gate-28/28-ci-coverage-gate.md` documenting `fail_under` ratchet guidance.
  - Acceptance: The new doc explains how to adjust `fail_under` and includes milestone guidance.
- [ ] [P4-T24] Update `2025-12-04-ci-coverage-gate-28/issue.md` with a link to the ratchet guidance doc and CI run evidence.
  - Acceptance: The issue includes the new doc link and at least one CI run URL with coverage summary reference.
- [ ] [P4-T25] Update `2025-12-04-ci-coverage-gate-28/plan.2025-12-04T11-43.md` to mark QA toolchain steps complete with evidence links.
  - Acceptance: The plan’s QA tasks are checked with a link to `toolchain-final.md`.

### Phase 5 — QA & Evidence Validation
- [ ] [P5-T1] Run the doc structure check command from the “Doc QA Tools” section and record the result in `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` includes the command output or a “Not available” note matching Phase 1.
- [ ] [P5-T2] Run the doc lint command from the “Doc QA Tools” section and record the result in `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` includes the command output or a “Not available” note matching Phase 1.
- [ ] [P5-T3] Run the link-check command from the “Doc QA Tools” section and record the result in `toolchain-final.md`.
  - Acceptance: `toolchain-final.md` includes the command output or a “Not available” note matching Phase 1.
- [ ] [P5-T4] Run `poetry run black .` as the first step of the final toolchain loop.
  - Acceptance: The command exits with code 0; if it modifies files, rerun the loop starting at [P5-T4] after committing fixes.
- [ ] [P5-T5] Run `poetry run ruff check` as the second step of the final toolchain loop.
  - Acceptance: The command exits with code 0; if it fails or modifies files, rerun the loop starting at [P5-T4] after committing fixes.
- [ ] [P5-T6] Run `poetry run pyright` as the third step of the final toolchain loop.
  - Acceptance: The command exits with code 0; if it fails, rerun the loop starting at [P5-T4] after committing fixes.
- [ ] [P5-T7] Run `poetry run pytest --cov=src/lexile_corpus_tuner --cov=scripts/dev_tools --cov-report=term-missing` as the fourth step of the final toolchain loop.
  - Acceptance: The command exits with code 0; if it fails, rerun the loop starting at [P5-T4] after committing fixes.

## Doc QA Tools

- Doc structure check: Not available (to be confirmed in Phase 1).
- Doc lint: Not available (to be confirmed in Phase 1).
- Link check: Not available (to be confirmed in Phase 1).

## Update Map

(To be filled in Phase 1 with target headings/anchors for each file.)
