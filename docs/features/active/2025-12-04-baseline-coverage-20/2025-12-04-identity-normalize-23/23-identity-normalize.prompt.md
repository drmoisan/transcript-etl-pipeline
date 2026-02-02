Agent C Objective: Increase coverage for `transform/identity_constraints.py` and `transform/normalize.py` (name extraction, constraint application, normalization edge cases) to ~75% combined.

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
- [x] Map key paths in `identity_constraints.py` (name extraction, constraint application) and `normalize.py` (edge cases).
- [x] Add unit tests for primary branches and tricky inputs to reach ~75% combined coverage.
- [x] Keep tests in `tests/transform/`; prefer small, deterministic cases.
- [x] Run coverage to confirm lift (`poetry run pytest --cov=src_transcript_etl_pipeline --cov-report=term`).
- [x] Document anomalies or unexpected behaviors here and in issue #23; link PR(s).

## Acceptance Criteria
- [x] Tests added/updated to cover main branches and edge cases for both modules.
- [x] Combined coverage ~75%+ (cite coverage report).
- [x] Tests conform to unit-test policy and are deterministic.
- [ ] Issue #23 updated with findings, PR/test links, and coverage evidence.

## Coverage Results

Final coverage achieved: **98% combined** (target was ~75%)

| Module | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| `identity_constraints.py` | 81 | 2 | 98% |
| `normalize.py` | 47 | 0 | 100% |
| **Combined** | **128** | **2** | **98%** |

### Uncovered Lines Analysis

The 2 uncovered lines in `identity_constraints.py` are essentially unreachable:

1. **Line 177** (`if len(name) < 2: continue`): Dead code. The regex pattern `[A-Z][a-z]+` requires at least 2 characters (1 uppercase + 1 lowercase), so this check can never trigger.

2. **Line 198** (`continue` after `^\s*is {name_lower}\b` check): Unreachable due to how the regex captures names. When a sentence starts with "Is Name...", the name extraction pattern captures "Is Name" as a single two-word name, preventing the "Is Name" at-start exclusion logic from being applied to "Name" alone.

### Tests Added (11 new tests)

All new tests follow the unit-test-policy (docstrings, AAA pattern, deterministic, isolated):

1. `test_thanks_followed_by_name_extracts_name` - Tests name extraction from "Thanks Frank" pattern
2. `test_hello_followed_by_name_extracts_name` - Tests name extraction after "Hello" prefix
3. `test_short_single_char_name_excluded` - Verifies single-character tokens are excluded
4. `test_standalone_name_question_excluded` - Tests "Fred?" pattern is not a direct address
5. `test_standalone_name_question_with_context_excluded` - Tests "Wait, Fred?" is not a direct address
6. `test_is_name_article_noun_excluded` - Tests "Is Dan a..." pattern at sentence start
7. `test_is_name_an_expert_excluded` - Tests "Is Alice an..." pattern at sentence start
8. `test_is_name_the_person_excluded` - Tests "Is Bob the..." pattern at sentence start
9. `test_mid_sentence_is_name_article_excluded` - Tests "...is Dan a..." mid-sentence
10. `test_mid_sentence_is_name_an_excluded` - Tests "...is Charlie an..." mid-sentence
11. `test_mid_sentence_is_name_the_excluded` - Tests "...is Sarah the..." mid-sentence

### Validation

- All 71 tests for the two modules pass
- All 628 project tests pass (plus 1 expected failure)
- Black formatting: ✅
- Ruff linting: ✅
- Pyright type checking: ✅
