Agent G Objective: Add tests for formatters (`docx`, `rtf`, `md`) and `document/parser.py` to validate spacing/label rules and parsing, targeting ≈70% coverage.

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
- Identify key spacing/label rules and parsing expectations for docx/rtf/md formatters and `document/parser.py`.
- Add unit tests in `tests/formatters/` and `tests/document/` to cover representative samples and edge cases.
- Include round-trip checks where feasible; otherwise assert on parsed/ formatted structures.
- Drive module coverage toward ≈70%+; run coverage and note results.
- Document scenarios, edge cases, and PR/test links here and in issue #27.

## Acceptance Criteria
- New tests validate formatting/parsing rules across docx/rtf/md and parser paths.
- Coverage for these modules reaches roughly 70%+ (cite report).
- Tests are deterministic and comply with unit-test policy.
- Issue #27 updated with PR/test links and coverage evidence.
