# `2025-12-04-formatters-parser` — User Story

- Issue: #27
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-02-02T13-08

## Story Statement

- As a maintainer, I want formatter and parser unit tests, so that spacing/label rules and parsing behavior do not regress.
- As a contributor, I want clear, deterministic test cases, so that I can validate changes without relying on binary output diffs.

## Problem / Why

Formatters and the document parser lack targeted unit coverage, leaving spacing/label rules and parsing behavior vulnerable to regressions.


## Personas & Scenarios

- Persona: Test maintainer
  - who the user is: Maintains formatter/parser behavior and test coverage.
  - what they care about: Stable, non-brittle assertions and clear regression signals.
  - their constraints: Tests must be deterministic and fast, without external dependencies.
  - their goals and frustrations: Wants to avoid binary DOCX comparisons and catch spacing/label regressions early.
  - their context and motivations: Frequent updates to formatting and parsing logic.
- Scenario: Adding coverage for formatting and parsing rules
  - A concrete, step-by-step narrative that describes how a user accomplishes a goal in a real-world context using the system.
  - who is acting? The test maintainer.
  - what triggered the action? A code change touching formatter or parser logic.
  - what steps do they take? They add unit tests under `tests/formatters/` and `tests/document/`, run Pytest, and review coverage.
  - what obstacles or decisions occur? They decide on structure-based assertions instead of binary output comparisons.
  - what outcome do they expect? Tests pass with coverage meeting the target and regressions surface clearly.


## Acceptance Criteria

- [ ] Tests assert on key formatting/spacing rules and parsed structures.
- [ ] Coverage report shows >=70% for formatters and parser modules.
- [ ] Tests avoid brittle assertions on binary DOCX output by using text/structure checks.
- [ ] Tests run deterministically without external dependencies.


## Non-Goals

- Changing formatter/parser runtime behavior beyond what is needed for testability.
- Adding new CLI flags or production configuration.
- Coverage targets outside formatter and parser modules.
