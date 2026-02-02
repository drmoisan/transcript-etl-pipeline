# `multi-speaker-fixtures` — User Story

- Issue: #24
- Owner: Dan Moisan
- Status: In Progress
- Last Updated: 2026-02-02

## Story Statement

- As a maintainer, I want reusable 3+ speaker fixtures, so that I can write regression tests without duplicating transcript data.
- As a contributor, I want deterministic multi-speaker test scenarios, so that I can verify grouping changes safely and quickly.

## Problem / Why

3+ speaker scenarios lack reusable fixtures and regression coverage, so grouping behavior is under-tested and prone to regressions (e.g., SpaceX discussion). Adding shared fixtures and targeted regression tests reduces duplication and catches mis-grouping early.

## Personas & Scenarios

- Persona: Test maintainer
  - who the user is: Maintains grouping heuristics and regression tests.
  - what they care about: Stable, deterministic fixtures and clear pass/fail signals.
  - their constraints: No external data; tests must be fast and deterministic.
  - their goals and frustrations: Wants to prevent regressions without re-creating fixtures for each test suite.
  - their context and motivations: Iterating on speakerless grouping logic while preserving existing behavior.
- Scenario: Adding coverage for a 3+ speaker regression
  - A concrete, step-by-step narrative that describes how a user accomplishes a goal in a real-world context using the system.
  - who is acting? The test maintainer.
  - what triggered the action? A bug report noting a mis-grouped multi-speaker transcript.
  - what steps do they take? They pick a fixture from `tests/fixtures/multi_speaker.py`, add a regression test in `tests/transform/test_multi_speaker_regression.py`, and run Pytest.
  - what obstacles or decisions occur? They decide whether to mark a known gap as `xfail` or update expected outcomes.
  - what outcome do they expect? Deterministic failures for regressions and stable passing tests for known-good behavior.


## Acceptance Criteria

- [ ] A shared fixture module provides deterministic 3+ speaker fixtures (including a SpaceX discussion) for reuse across test suites.
- [ ] Regression tests reference the shared fixtures and assert expected grouping and speaker assignment outcomes.
- [ ] Fixture validation tests fail fast on malformed fixture definitions (e.g., missing expected lines or invalid speaker counts).
- [ ] Known algorithmic gaps are captured as `xfail` tests with documented rationale instead of being silently skipped.
- [ ] Tests run without external dependencies and remain deterministic across repeated runs.

## Non-Goals

- Changing or improving the underlying grouping algorithms.
- Adding new runtime CLI flags or configuration settings.
- Introducing external data sources or non-deterministic fixtures.
