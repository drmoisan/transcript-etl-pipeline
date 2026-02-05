# Remediation Inputs — 2025-12-04-baseline-coverage-20

**Timestamp:** 2026-02-04T18-45

## Delivery Gaps Requiring Remediation

### Feature #21 — enhance-tests

- **Gap:** Fail-before evidence not recorded (documentation-only artifact).
  - **Done Criteria:**
    - Create a fail-before evidence artifact under `2025-12-04-enhance-tests-21/remediation-baseline/` with `Timestamp`, `Command`, and `EXIT_CODE`, or produce a formal Fail-before Exception Dossier if the baseline failure cannot be reproduced.
    - Link the artifact in the feature plan and ensure it matches the acceptance criterion for fail-before evidence.

### Feature #22 — speakerless-heuristics

- **Gap:** Issue #22 update missing.
  - **Done Criteria:**
    - Create a local mirror artifact at `2025-12-04-speakerless-heuristics-22/issue-updates/issue-22.<timestamp>.md` with the required fields.
    - Update the GitHub issue (comment or body) with coverage evidence and test links, then mirror the text locally.

### Feature #23 — identity-normalize

- **Gap:** Issue #23 update missing.
  - **Done Criteria:**
    - Create a local mirror artifact at `2025-12-04-identity-normalize-23/issue-updates/issue-23.<timestamp>.md` with required fields.
    - Update the GitHub issue with the coverage evidence and test command; mirror text locally.

### Feature #26 — notes-regressions

- **Gap:** Fail-before evidence for notes regressions is exception-based and does not explicitly reference the notes regression tests.
  - **Done Criteria:**
    - Update the exception dossier to reference the relevant notes regression tests, or record a fail-before run if possible.
    - Ensure the dossier includes `Timestamp`, `Command`, and `EXIT_CODE` blocks for each proof.
- **Gap:** Issue #26 update missing.
  - **Done Criteria:**
    - Create a local mirror artifact at `2025-12-04-notes-regressions-26/issue-updates/issue-26.<timestamp>.md`.
    - Update the GitHub issue with regression evidence and test links; mirror text locally.

### Feature #27 — formatters-parser

- **Gap:** Issue #27 update missing.
  - **Done Criteria:**
    - Create a local mirror artifact at `2025-12-04-formatters-parser-27/issue-updates/issue-27.<timestamp>.md`.
    - Update the GitHub issue with coverage evidence and test links; mirror text locally.

### Feature #28 — ci-coverage-gate

- **Gap:** CI coverage gate acceptance criteria not verified for `.github/workflows/ci.yml`.
  - **Done Criteria:**
    - Run or locate a CI run for the actual `ci.yml` workflow that includes:
      - pytest-cov execution
      - coverage threshold enforcement
      - step summary with coverage report
      - uploaded `coverage.xml` and `htmlcov/` artifacts
    - Record the run URL and command evidence under `2025-12-04-ci-coverage-gate-28/remediation-baseline/` with `Timestamp`, `Command`, and `EXIT_CODE`.
- **Gap:** Documentation of `fail_under` ratchet plan not confirmed in repo docs beyond feature spec.
  - **Done Criteria:**
    - Update README or feature docs with clear instructions for ratcheting `fail_under` and record evidence of the update.

## Do-Not-Do List

- Do not broaden scope beyond acceptance criteria and required issue updates.
- Do not modify policy documents.
- Do not mark plan items complete without evidence artifacts containing `Timestamp`, `Command`, and `EXIT_CODE`.
