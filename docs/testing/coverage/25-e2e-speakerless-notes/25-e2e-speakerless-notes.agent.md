Agent E Objective: Add end-to-end CLI tests for speakerless + notes workflows (DOCX/MD outputs) to protect key flows.

## Policies: Always Follow These

CRITICAL: When implementing any code, tests, or tasks, you must adhere to these repo policies without exception. These are not guidelines-they are requirements.

Read each policy document thoroughly before starting work. Implement them exactly as written. Do not interpret, modify, or skip any requirements.

* Coding Standards, Workflow, PR/commit procedures:  
  [code-change.instructions.md](../../../code-change.instructions.md)
  
  This document defines the complete development workflow including:  
  - Pre-implementation requirements (clarify objectives, document plans)  
  - Python coding standards (formatting, linting, typing, testing)  
  - Design principles (simplicity, reusability, extensibility, separation of concerns)  
  - Post-implementation requirements (quality checks, documentation updates)

* Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:  
  [developer-tooling.md](../../../developer-tooling.md)
  
  This document covers all tooling setup and usage.

* Unit Test Policy (independence, determinism, clarity, AAA, etc.):  
  [unit-test-policy.md](../../../unit-test-policy.md)
  
  This document defines mandatory testing standards. Every test must comply.

Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.

## Workplan
- Identify representative speakerless and notes transcripts for CLI E2E runs.
- Add pytest integration tests (e.g., under `tests/integration/`) that invoke the CLI to produce DOCX/MD.
- Assert on outputs via text extraction/markers (golden files optional if brittle).
- Ensure tests are deterministic and runnable via existing tasks.
- Link scenarios, PR(s), and results in issue #25; note any runtime/env considerations.

## Acceptance Criteria
- New E2E tests cover at least one speakerless and one notes CLI flow.
- Tests pass reliably in CI and locally; assertions verify key outputs.
- Issue #25 updated with PR/test links and a brief scenario description.
