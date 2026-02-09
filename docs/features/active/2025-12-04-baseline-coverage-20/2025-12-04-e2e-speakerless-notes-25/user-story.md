# `2025-12-04-e2e-speakerless-notes` — User Story

- Issue: #25
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-02-02T12-45

## Story Statement

- As a maintainer, I want CLI E2E tests for speakerless and notes workflows, so that regressions in output structure are caught before release.
- As a contributor, I want clear, deterministic integration tests covering DOCX/MD/RTF outputs, so that I can validate changes without manual spot checks.

## Problem / Why

There is no end-to-end coverage for CLI speakerless + notes workflows, leaving output validation and integration behavior untested.


## Personas & Scenarios

- Persona: Maintainer validating releases
  - who the user is: Responsible for CI quality and release readiness
  - what they care about: CLI stability, output correctness, and regression prevention
  - their constraints: Limited time; must rely on automated checks
  - their goals and frustrations: Wants fast, deterministic tests; frustrated by brittle binary comparisons
  - their context and motivations: Maintains a growing test suite while raising coverage
- Scenario: Validate speakerless and notes CLI flows before merging
  - who is acting? Maintainer reviewing a PR
  - what triggered the action? A change to CLI, notes processing, or formatting
  - what steps do they take? Run the integration tests for speakerless and notes outputs
  - what obstacles or decisions occur? Ensuring tests avoid UI prompts and brittle file diffs
  - what outcome do they expect? Tests pass with text-marker assertions proving key output structure


## Acceptance Criteria

- [ ] Pytest integration tests cover speakerless CLI flows for DOCX/MD/RTF outputs and pass reliably.
- [ ] Pytest integration tests cover notes-only and notes+transcript CLI flows (including update mode).
- [ ] Tests include explicit error handling cases for missing files and invalid arguments.
- [ ] Output validation asserts stable text markers/sections rather than binary file comparisons.


## Non-Goals

- UI/interactive prompt testing (tests must avoid UI prompts).
- Golden/binary snapshot comparisons for DOCX/RTF outputs.
- Changes to speaker identification logic or note formatting rules.
