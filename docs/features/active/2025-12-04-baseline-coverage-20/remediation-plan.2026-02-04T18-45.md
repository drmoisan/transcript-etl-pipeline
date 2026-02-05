# Remediation Plan — 2025-12-04-baseline-coverage-20 (2026-02-04T18-45)

## Overview
Close the remediation gaps listed in `docs/features/active/2025-12-04-baseline-coverage-20/remediation-inputs.2026-02-04T18-45.md` by producing missing evidence artifacts, posting required issue updates, and documenting the CI coverage ratchet plan. The plan is scoped to documentation and evidence capture; it avoids policy changes and does not broaden feature scope.

### Phase 0 — Context & Inputs
- [ ] [P0-T1] Record that `.github/copilot-instructions.md` was read in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/policy-read.2026-02-04T18-45.md`.
  - Acceptance: The file exists and contains the exact line `PolicyRead: .github/copilot-instructions.md`.
- [ ] [P0-T2] Record that `.github/instructions/general-code-change.instructions.md` was read in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/policy-read.2026-02-04T18-45.md`.
  - Acceptance: The file exists and contains the exact line `PolicyRead: .github/instructions/general-code-change.instructions.md`.
- [ ] [P0-T3] Record that `.github/instructions/general-unit-test.instructions.md` was read in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/policy-read.2026-02-04T18-45.md`.
  - Acceptance: The file exists and contains the exact line `PolicyRead: .github/instructions/general-unit-test.instructions.md`.
- [ ] [P0-T4] Record that no language-specific code-change or unit-test policy applies to markdown-only remediation work in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/policy-read.2026-02-04T18-45.md`.
  - Acceptance: The file contains the exact line `LanguageSpecificPolicies: none (markdown-only remediation artifacts)`.
- [ ] [P0-T5] Record that `docs/features/active/2025-12-04-baseline-coverage-20/remediation-inputs.2026-02-04T18-45.md` was read in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/context-read.2026-02-04T18-45.md`.
  - Acceptance: The file exists and contains the exact line `ContextRead: remediation-inputs.2026-02-04T18-45.md`.
- [ ] [P0-T6] Record that `docs/features/active/2025-12-04-baseline-coverage-20/initiative.md` was read in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/context-read.2026-02-04T18-45.md`.
  - Acceptance: The file contains the exact line `ContextRead: initiative.md`.
- [ ] [P0-T7] Record that `docs/features/active/2025-12-04-baseline-coverage-20/orchestration.md` was read in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/context-read.2026-02-04T18-45.md`.
  - Acceptance: The file contains the exact line `ContextRead: orchestration.md`.

### Phase 1 — Feature #21 Fail-Before Evidence (enhance-tests)
- [ ] [P1-T1] Capture baseline test availability evidence for feature #21 in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-21/remediation-baseline/fail-before-availability.2026-02-04T18-45.md`.
  - Preconditions: Use the baseline commit referenced in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE` fields and includes command output showing whether the target regression tests exist at the baseline commit.
- [ ] [P1-T2] When [P1-T1] shows the tests exist at the baseline commit, run the fail-before command and save evidence to `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-21/remediation-baseline/fail-before.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE` fields, the command matches the fail-before command documented in the feature plan, and `EXIT_CODE` is non-zero.
- [ ] [P1-T3] When [P1-T1] shows the tests do not exist at the baseline commit, create a formal exception dossier at `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-21/remediation-baseline/fail-before-exception-dossier.2026-02-04T18-45.md`.
  - Acceptance: The dossier explains why the fail-before run is impossible, explicitly names the missing test files, and includes at least two evidence blocks that each contain `Timestamp`, `Command`, and `EXIT_CODE`.
- [ ] [P1-T4] Update `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md` to link the new fail-before evidence artifact from [P1-T2] or [P1-T3].
  - Acceptance: The plan file contains the exact artifact path (with the 2026-02-04T18-45 timestamp) and a short sentence mapping it to the fail-before acceptance criterion.

### Phase 2 — Issue Updates with Local Mirrors (#22, #23, #26, #27)
- [ ] [P2-T1] Post the Issue #22 update (coverage evidence + test links) and capture command evidence in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-speakerless-heuristics-22/issue-updates/issue-22.post.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, and the captured command text shows the posted update payload.
- [ ] [P2-T2] Create the local mirror at `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-speakerless-heuristics-22/issue-updates/issue-22.2026-02-04T18-45.md`.
  - Acceptance: The file includes `Timestamp`, `IssueNumber`, `IssueURL`, `FeatureFolder`, `CapturedVia`, `RemoteVerification`, `Issue JSON`, and `Comments JSON`, plus an `EvidenceSchemaAddendum` block containing `Timestamp`, `Command`, and `EXIT_CODE`, and the Issue JSON body includes coverage evidence and test links.
- [ ] [P2-T3] Post the Issue #23 update (coverage evidence + test links) and capture command evidence in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/issue-updates/issue-23.post.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, and the captured command text shows the posted update payload.
- [ ] [P2-T4] Create the local mirror at `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/issue-updates/issue-23.2026-02-04T18-45.md`.
  - Acceptance: The file includes `Timestamp`, `IssueNumber`, `IssueURL`, `FeatureFolder`, `CapturedVia`, `RemoteVerification`, `Issue JSON`, and `Comments JSON`, plus an `EvidenceSchemaAddendum` block containing `Timestamp`, `Command`, and `EXIT_CODE`, and the Issue JSON body includes coverage evidence and test links.
- [ ] [P2-T5] Post the Issue #26 update (regression evidence + test links) and capture command evidence in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/issue-updates/issue-26.post.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, and the captured command text shows the posted update payload.
- [ ] [P2-T6] Create the local mirror at `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/issue-updates/issue-26.2026-02-04T18-45.md`.
  - Acceptance: The file includes `Timestamp`, `IssueNumber`, `IssueURL`, `FeatureFolder`, `CapturedVia`, `RemoteVerification`, `Issue JSON`, and `Comments JSON`, plus an `EvidenceSchemaAddendum` block containing `Timestamp`, `Command`, and `EXIT_CODE`, and the Issue JSON body includes regression evidence and test links.
- [ ] [P2-T7] Post the Issue #27 update (coverage evidence + test links) and capture command evidence in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/issue-updates/issue-27.post.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, and the captured command text shows the posted update payload.
- [ ] [P2-T8] Create the local mirror at `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/issue-updates/issue-27.2026-02-04T18-45.md`.
  - Acceptance: The file includes `Timestamp`, `IssueNumber`, `IssueURL`, `FeatureFolder`, `CapturedVia`, `RemoteVerification`, `Issue JSON`, and `Comments JSON`, plus an `EvidenceSchemaAddendum` block containing `Timestamp`, `Command`, and `EXIT_CODE`, and the Issue JSON body includes coverage evidence and test links.

### Phase 3 — Feature #26 Fail-Before Exception Dossier Update (notes-regressions)
- [ ] [P3-T1] Identify the exact notes regression tests referenced by feature #26 and record them in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/remediation-baseline/notes-regression-tests.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, and lists each test name with its file path.
- [ ] [P3-T2] Update `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/remediation-baseline/fail-before-exception-dossier.2026-02-04T16-53.md` to explicitly reference the tests from [P3-T1].
  - Acceptance: The dossier includes a new section named `Referenced Regression Tests` listing the test names and file paths, and adds at least one new evidence block containing `Timestamp`, `Command`, and `EXIT_CODE` that proves the tests are absent at the baseline commit.

### Phase 4 — Feature #28 CI Coverage Gate Evidence + Ratchet Documentation
- [ ] [P4-T1] Capture CI run evidence for the actual `.github/workflows/ci.yml` workflow in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run-evidence.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, plus the CI run URL, and includes CLI output proving pytest-cov executed and coverage artifacts (`coverage.xml`, `htmlcov/`) were produced.
- [ ] [P4-T2] Record the CI step summary excerpt that shows coverage threshold enforcement in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-coverage-threshold.2026-02-04T18-45.md`.
  - Acceptance: The file contains `Timestamp`, `Command`, and `EXIT_CODE`, plus a pasted step-summary excerpt that explicitly states the coverage threshold check or `fail_under` value.
- [ ] [P4-T3] Document the `fail_under` ratchet plan in `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md`.
  - Acceptance: The spec file contains a new section titled `Fail-under Ratchet Plan` that names the configuration location (for example `.github/workflows/ci.yml`), specifies the incrementing process, and references the evidence artifacts created in [P4-T1] and [P4-T2].

### Phase 5 — Evidence QA (artifact verification)
- [ ] [P5-T1] Verify that all remediation evidence artifacts created in Phases 1–4 contain `Timestamp`, `Command`, and `EXIT_CODE` fields and record the verification output in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/qa-evidence.2026-02-04T18-45.md`.
  - Acceptance: The QA file contains `Timestamp`, `Command`, and `EXIT_CODE`, plus a list of every artifact path verified.
- [ ] [P5-T2] Verify that all required issue update mirrors were created with the correct timestamp suffix and record the check results in `docs/features/active/2025-12-04-baseline-coverage-20/baseline/qa-issue-updates.2026-02-04T18-45.md`.
  - Acceptance: The QA file contains `Timestamp`, `Command`, and `EXIT_CODE`, plus the four required mirror file paths for issues 22, 23, 26, and 27.
