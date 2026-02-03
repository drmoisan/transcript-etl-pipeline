# Remediation Plan — 2025-12-04-baseline-coverage-20 (2026-02-03)

## Overview
This plan closes evidence, coverage, and documentation gaps across the baseline coverage epic and linked feature issues. Work is structured into phased, atomic tasks with machine-verifiable acceptance criteria and a final QA toolchain pass.

### Phase 0 — Context & Inputs
- [ ] [P0-T1] Read `.github/copilot-instructions.md` to confirm repo-wide agent policies.
  - Acceptance: Note the read completion by adding a dated confirmation line under "Context Checks" in this plan file.
- [ ] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm change workflow requirements.
  - Acceptance: Add a dated confirmation line under "Context Checks" in this plan file.
- [ ] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm unit-test constraints.
  - Acceptance: Add a dated confirmation line under "Context Checks" in this plan file.
- [ ] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` and `.github/instructions/python-unit-test.instructions.md` to confirm Python toolchain and test rules.
  - Acceptance: Add a dated confirmation line under "Context Checks" in this plan file.
- [ ] [P0-T5] Read `docs/features/active/2025-12-04-baseline-coverage-20/remediation-inputs.2026-02-03T16-10.md` to confirm the remediation scope.
  - Acceptance: Add a dated confirmation line under "Context Checks" in this plan file.
- [ ] [P0-T6] Capture baseline formatter output with `poetry run black .`.
  - Acceptance: Add a fenced output block labeled "Baseline — Black" in this plan file containing the exact command and its output.
- [ ] [P0-T7] Capture baseline lint output with `poetry run ruff check`.
  - Acceptance: Add a fenced output block labeled "Baseline — Ruff" in this plan file containing the exact command and its output.
- [ ] [P0-T8] Capture baseline type-check output with `poetry run pyright`.
  - Acceptance: Add a fenced output block labeled "Baseline — Pyright" in this plan file containing the exact command and its output.
- [ ] [P0-T9] Capture baseline test output with `poetry run pytest --cov=src/lexile_corpus_tuner --cov=scripts/dev_tools --cov-report=term-missing`.
  - Acceptance: Add a fenced output block labeled "Baseline — Pytest (policy command)" in this plan file containing the exact command and its output.

### Phase 1 — Epic Evidence and MVP Gaps
- [ ] [P1-T1] Run `poetry run black .` and record output for the epic evidence requirement.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/initiative.md` contains a fenced block labeled "Epic Evidence — Black" with the exact command and output.
- [ ] [P1-T2] Run `poetry run ruff check` and record output for the epic evidence requirement.
  - Acceptance: `initiative.md` contains a fenced block labeled "Epic Evidence — Ruff" with the exact command and output.
- [ ] [P1-T3] Run `poetry run pyright` and record output for the epic evidence requirement.
  - Acceptance: `initiative.md` contains a fenced block labeled "Epic Evidence — Pyright" with the exact command and output.
- [ ] [P1-T4] Run `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing` and record output for the epic evidence requirement.
  - Acceptance: `initiative.md` contains a fenced block labeled "Epic Evidence — Pytest (initiative command)" with the exact command and output.
- [ ] [P1-T5] Add explicit owner and timebox fields for the epic execution.
  - Acceptance: `initiative.md` contains a section titled "Execution Owner and Timebox" with non-empty owner and timebox lines.
- [ ] [P1-T6] Decide the coverage remediation path (tests vs. exception) and document the decision.
  - Acceptance: `initiative.md` contains a section titled "Coverage Policy Decision" with a single sentence stating the chosen path.
- [ ] [P1-T7] If an exception path is chosen, add the exception request details.
  - Preconditions: [P1-T6] selects the exception path.
  - Acceptance: `initiative.md` contains a section titled "Coverage Exception Request" with requested threshold, duration, and approver placeholders populated.

### Phase 2 — Feature Evidence and Documentation Updates
- [ ] [P2-T1] Record #21 baseline and targeted coverage evidence in `plan.2026-02-02T11-49.md`.
  - Acceptance: The file contains a labeled block "#21 Coverage Evidence" with baseline and targeted command outputs.
- [ ] [P2-T2] Record #22 coverage report output for `speakerless.py` and `speaker_helpers.py`.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-speakerless-heuristics-22/plan.2026-02-02T12-24.md` contains a labeled block "#22 Coverage Evidence" with `coverage report --fail-under=70` output.
- [ ] [P2-T3] Check off Phase 4 toolchain steps in #22 plan after evidence is recorded.
  - Acceptance: In `plan.2026-02-02T12-24.md`, all Phase 4 tasks are marked complete.
- [ ] [P2-T4] Add coverage table and command reference to Issue #23.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/issue.md` contains a "Coverage" section with a table and the exact command used.
- [ ] [P2-T5] Check off Phase 5 toolchain steps in #23 plan after evidence is recorded.
  - Acceptance: In `plan.2026-02-02T13-08.md`, all Phase 5 tasks are marked complete.
- [ ] [P2-T6] Document fixture locations and usage for #24.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-multi-speaker-fixtures-24/issue.md` includes paths to `tests/fixtures/multi_speaker.py` and `tests/transform/test_multi_speaker_regression.py`.
- [ ] [P2-T7] Record #26 pre/post regression evidence in the plan or issue.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/plan.2026-02-02T13-08.md` contains a "#26 Regression Evidence" block with failing and passing test output.
- [ ] [P2-T8] Update Issue #26 with results and links.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/issue.md` includes a "Results" section with evidence references and PR/commit links.
- [ ] [P2-T9] Record #27 coverage evidence and toolchain completion.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/issue.md` includes `coverage report --fail-under=70` output and `plan.2026-02-02T13-08.md` Phase 6 tasks are marked complete.
- [ ] [P2-T10] Add CI coverage gate documentation for #28.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/issue.md` (or a new `28-ci-coverage-gate.md` in the same folder) contains an explicit section describing how to adjust `fail_under` and the ratchet plan.
- [ ] [P2-T11] Link a CI run with coverage evidence for #28.
  - Acceptance: The #28 issue doc includes a URL to a CI run and a short summary line stating the coverage summary and artifact location.

### Phase 3 — #25 Missing E2E Scenarios
- [ ] [P3-T1] Add the panel DOCX scenario test in `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: `poetry run pytest tests/integration/test_cli_e2e_speakerless.py -k panel_docx` exits with code 0.
- [ ] [P3-T2] Add the additional Markdown scenario test in `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: `poetry run pytest tests/integration/test_cli_e2e_speakerless.py -k additional_md` exits with code 0.
- [ ] [P3-T3] Add the additional RTF scenario test in `tests/integration/test_cli_e2e_speakerless.py`.
  - Acceptance: `poetry run pytest tests/integration/test_cli_e2e_speakerless.py -k additional_rtf` exits with code 0.
- [ ] [P3-T4] Record #25 coverage evidence for CLI/reader/notes/formatters.
  - Acceptance: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-e2e-speakerless-notes-25/plan.2026-02-02T12-45.md` contains a labeled block "#25 Coverage Evidence" with `coverage.xml` or `coverage report` summaries.
- [ ] [P3-T5] Update #25 plan notes with runtime and edge-case observations.
  - Acceptance: `plan.2026-02-02T12-45.md` contains a section titled "Runtime and Edge Case Notes" with at least two bullet points.
- [ ] [P3-T6] Verify new E2E tests avoid temporary files and disallowed filesystem usage.
  - Acceptance: `git grep -n "tmp_path|tempfile|TemporaryDirectory" tests/integration/test_cli_e2e_speakerless.py` returns no matches.

### Phase 4 — Coverage Remediation (>= 80%)
- [ ] [P4-T1] Generate a coverage report that identifies the lowest-coverage modules.
  - Acceptance: `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing` output is captured in `initiative.md` under "Coverage Hotspots".
- [ ] [P4-T2] Select the top three modules to remediate and list them with target percentages.
  - Acceptance: `initiative.md` contains a table "Coverage Targets" with three module rows and target percentages.
- [ ] [P4-T3] Add a focused test for the first target module’s primary function.
  - Acceptance: `initiative.md` contains a "Coverage Target 1 Test Run" block with a pytest command and its passing output, and the referenced test name exists in the test file.
- [ ] [P4-T4] Add a focused test for the second target module’s primary function.
  - Acceptance: `initiative.md` contains a "Coverage Target 2 Test Run" block with a pytest command and its passing output, and the referenced test name exists in the test file.
- [ ] [P4-T5] Add a focused test for the third target module’s primary function.
  - Acceptance: `initiative.md` contains a "Coverage Target 3 Test Run" block with a pytest command and its passing output, and the referenced test name exists in the test file.
- [ ] [P4-T6] Re-run coverage to confirm the repo-wide threshold.
  - Acceptance: `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing` output shows total coverage >= 80%.

### Phase 5 — Final QA (Toolchain Loop)
- [ ] [P5-T1] Run `poetry run black .` and restart the QA loop if files change.
  - Acceptance: Command exits with code 0 and no files are modified after this step.
- [ ] [P5-T2] Run `poetry run ruff check` and restart the QA loop from P5-T1 if it fails or auto-fixes.
  - Acceptance: Command exits with code 0 and reports no fixes.
- [ ] [P5-T3] Run `poetry run pyright` and restart the QA loop from P5-T1 if it fails.
  - Acceptance: Command exits with code 0.
- [ ] [P5-T4] Run `poetry run pytest --cov=src/lexile_corpus_tuner --cov=scripts/dev_tools --cov-report=term-missing` and restart the QA loop from P5-T1 if it fails.
  - Acceptance: Command exits with code 0 and the run is part of a single clean pass with P5-T1 through P5-T4.

## Context Checks
- 

## Evidence Blocks
- 
