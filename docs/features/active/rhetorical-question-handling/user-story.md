# `rhetorical-question-handling` — User Story

- Issue: #19
- Owner: drmoisan
- Status: Draft | In Progress | Complete
- Last Updated: 2025-12-04

## Story Statement

- As a ..., I want ..., so that ...
- As a ..., I want ..., so that ...

## Problem / Why

Rhetorical/tag questions (e.g., “Right?”, “You know?”, “..., didn’t it?”) are currently treated as speaker changes, causing over-splitting of multi-sentence turns (SpaceX test: 12 lines vs 18 expected).


## Personas & Scenarios

- Persona: ...
  - who the user is
  - what they care about
  - their constraints
  - their goals and frustrations
  - their context and motivations
- Scenario: ...
  - A concrete, step-by-step narrative that describes how a user accomplishes a goal in a real-world context using the system.
  - who is acting?
  - what triggered the action?
  - what steps do they take?
  - what obstacles or decisions occur?
  - what outcome do they expect?


## Acceptance Criteria

- [ ] Rhetorical question detection prevents speaker change on short/tag questions.
- [ ] Trailing tag questions do not trigger a change when they continue prior content.
- [ ] SpaceX test trend improves toward 18 lines (currently 12); no regressions in other speakerless tests.


## Non-Goals

Call out what is explicitly excluded from this feature.

