# 2025-12-04-identity-normalize — User Story

- Issue: #23
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-02-02

## Story Statement

- As a maintainer, I want focused tests for identity constraints and normalization, so that regressions are caught early.
- As a contributor, I want explicit, test-encoded expectations for tricky inputs, so that I can update logic safely.

## Problem / Why

`transform/identity_constraints.py` and `transform/normalize.py` lack targeted unit coverage for name extraction, constraint application, and normalization edge cases. This leaves expected behavior under-specified and makes regressions easy to miss for ambiguous inputs.

## Personas & Scenarios

- Persona: Pipeline maintainer
  - who the user is: Maintains speaker identity and normalization logic in the transcript pipeline.
  - what they care about: Correct identity constraint behavior and predictable text normalization outcomes.
  - their constraints: Tests must be deterministic and avoid filesystem/temp files or external services.
  - their goals and frustrations: Wants coverage that clarifies edge cases like "Is Name a..." and standalone name questions.
  - their context and motivations: Uses unit tests as a behavioral spec when reviewing changes.
- Scenario: Validate identity normalization after a change
  - who is acting? The maintainer.
  - what triggered the action? A modification to identity constraint extraction or normalization logic.
  - what steps do they take? Run `poetry run pytest tests/transform/` and inspect the assertions for tricky inputs.
  - what obstacles or decisions occur? Ensuring ambiguous inputs are handled consistently without overfitting.
  - what outcome do they expect? Tests pass and combined module coverage reaches $\ge 75\%$.


## Acceptance Criteria

- [ ] Unit tests cover main branches and edge cases in `transform/identity_constraints.py` and `transform/normalize.py`.
- [ ] Tests assert explicit constraints and normalized outputs for tricky inputs (e.g., "Thanks Name", "Is Name a...", standalone "Name?").
- [ ] Combined coverage for the two modules is $\ge 75\%$ (cite coverage report).
- [ ] Tests are deterministic and avoid filesystem/temp files or external services.
- [ ] Issue #23 is updated with coverage evidence and test/PR links.

## Non-Goals

- No changes to production logic in `identity_constraints.py` or `normalize.py`.
- No new CLI flags, configuration, or external dependencies.
- No integration or end-to-end tests beyond unit coverage for the two target modules.
