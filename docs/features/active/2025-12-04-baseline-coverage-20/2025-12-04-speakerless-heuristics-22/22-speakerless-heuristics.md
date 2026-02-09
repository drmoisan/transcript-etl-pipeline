Agent B Objective: Strengthen tests for speakerless heuristics (`transform/speakerless.py`, `transform/speaker_helpers.py`) covering rhetorical/tag questions, addressees, continuation, and clustering helpers to ≈70% coverage.

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
- Enumerate heuristics and helpers (rhetorical/tag detection, addressee detection, continuation rules, clustering helpers).
- Add positive/negative unit tests for each heuristic and helper to drive coverage to ≈70%+ on both modules.
- Use realistic fixtures (e.g., SpaceX/multi-speaker snippets) where helpful; keep tests in `tests/transform/`.
- Run coverage (`poetry run pytest --cov=src_transcript_etl_pipeline --cov-report=term`) to confirm lift.
- Record edge cases/surprises here and in issue #22; link PR(s).

## Acceptance Criteria
- New tests cover each heuristic path with clear positive/negative cases.
- Coverage for `transform/speakerless.py` and `transform/speaker_helpers.py` reaches roughly 70%+ (cite report).
- Tests follow unit-test policy; deterministic and scoped.
- Issue #22 updated with findings, PR/test links, and coverage evidence.

## Edge cases
- Tag-question phrasing like "Right?" should be treated as an acknowledgment cue for speaker shifts, while continuation phrasing such as "You know I agree." should not introduce a new change point on its own.
