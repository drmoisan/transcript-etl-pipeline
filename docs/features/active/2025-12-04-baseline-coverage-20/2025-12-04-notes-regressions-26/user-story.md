# `2025-12-04-notes-regressions` — User Story

- Issue: #26
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-02-02T13-09

## Story Statement

- As a maintainer, I want regression tests for notes conversion edge cases, so that past bugs do not reappear.
- As a contributor, I want clear, test-encoded expectations for notes parsing, so that I can change code safely.

## Problem / Why

Known notes conversion edge cases lack regression tests, allowing past bugs to reappear and leaving transform/notes.py under-covered.


## Personas & Scenarios

- Persona: Pipeline maintainer
  - who the user is: Maintains notes conversion behavior in the transcript pipeline.
  - what they care about: Stability of notes parsing and consistent formatting output.
  - their constraints: Tests must be deterministic and avoid filesystem/temp files or external services.
  - their goals and frustrations: Wants coverage that captures prior notes conversion failures.
  - their context and motivations: Uses unit tests to lock in expected behavior for edge cases.
- Scenario: Validate notes conversion after a change
  - who is acting? The maintainer.
  - what triggered the action? A change to notes conversion logic in `transform/notes.py`.
  - what steps do they take? Run `poetry run pytest tests/transform/` and review regression test results.
  - what obstacles or decisions occur? Ensuring ambiguous inputs are handled consistently without new regressions.
  - what outcome do they expect? All regression tests pass and notes-related coverage improves.


## Acceptance Criteria

- [ ] Each known notes conversion bug has a failing-before/passing-after regression test.
- [ ] Regression tests demonstrate prior failures and now pass.
- [ ] Coverage on notes-related paths measurably improves.


## Non-Goals

- No changes to production notes conversion logic beyond adding tests.
- No new CLI flags, configuration, or external dependencies.
- No integration or end-to-end tests beyond notes regression coverage.
