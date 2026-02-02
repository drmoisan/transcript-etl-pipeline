# 2025-12-04-speakerless-heuristics — User Story

- Issue: #22
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-02-02

## Story Statement

- As a maintainer, I want targeted unit tests for speakerless heuristics, so that regressions in speaker grouping are detected early.
- As a contributor, I want explicit, test-encoded expectations for heuristics, so that I can change code safely without guessing behavior.

## Problem / Why

`transform/speakerless.py` and `transform/speaker_helpers.py` lack focused unit tests for key heuristics (pronoun shifts, question/answer handling, dialogue markers, addressee reassignment, and similarity grouping). Without these tests, behavior is under-specified and regressions can slip into speakerless grouping.

## Personas & Scenarios

- Persona: Pipeline maintainer
  - who the user is: Maintains the transcript ETL pipeline and reviews changes to speakerless logic.
  - what they care about: Preventing regressions in speaker grouping and keeping tests deterministic and fast.
  - their constraints: Must avoid external dependencies, network calls, and filesystem/temp files in unit tests.
  - their goals and frustrations: Wants clear, stable tests that cover heuristics without brittle fixtures.
  - their context and motivations: Uses tests as a spec for behavior in `speakerless.py` and `speaker_helpers.py`.
- Scenario: Validate heuristic behavior after a code change
  - who is acting? The maintainer.
  - what triggered the action? A change to speakerless heuristics or helper functions.
  - what steps do they take? Run `poetry run pytest tests/transform/` and review coverage output for the two modules.
  - what obstacles or decisions occur? Ensuring tests cover addressee reassignment and similarity grouping without using external resources.
  - what outcome do they expect? Tests pass and coverage for both modules is $\ge 70\%$.


## Acceptance Criteria

- [ ] Unit tests in `tests/transform/` cover positive and negative cases for `detect_speaker_changes` heuristics (pronoun shifts, question/answer transitions, dialogue markers, and acknowledgment/thanks patterns).
- [ ] Unit tests cover addressee reassignment behavior in `resolve_addresses_other_violations`, including the follow-through behavior for short continuation sentences.
- [ ] Unit tests cover similarity grouping behavior in `group_sentences_by_similarity`, including boundary conditions when segments are fewer than speakers.
- [ ] Coverage for `src/transcript_etl_pipeline/transform/speakerless.py` and `src/transcript_etl_pipeline/transform/speaker_helpers.py` is $\ge 70\%$ in the coverage report.
- [ ] Tests are deterministic and do not use filesystem/temp files or external services.
- [ ] Issue #22 is updated with coverage evidence and test/PR links.

## Non-Goals

- No changes to production heuristic logic in `speakerless.py` or `speaker_helpers.py`.
- No new CLI flags, configuration options, or external dependencies.
- No integration or end-to-end test expansion beyond unit tests for the two target modules.
