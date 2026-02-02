# 2025-12-04-speakerless-heuristics — Spec

- **Issue:** [#22](https://github.com/drmoisan/transcript-etl-pipeline/issues/22)
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T12-24
- **Status:** Draft
- **Version:** 0.1

## Overview

Add targeted Pytest unit coverage for speakerless heuristics and helpers in `src/transcript_etl_pipeline/transform/speakerless.py` and `src/transcript_etl_pipeline/transform/speaker_helpers.py`, specifying expected behavior with deterministic tests and raising coverage for both modules to $\ge 70\%$.
- Target users/personas and primary use cases: Maintainers and contributors who need regression protection for speakerless grouping behavior and clarity on heuristic expectations.
- Success metrics or expected impact: Coverage for both modules reaches $\ge 70\%$ and tests document positive/negative cases for each heuristic.

## Behavior

Tests define and verify the behavior of speakerless heuristics without changing production logic.
- Main user flow (happy path): Running Pytest executes new unit tests that exercise `detect_speaker_changes`, `assign_speaker_labels`, and helper functions with positive and negative examples for pronoun shifts, question/answer transitions, dialogue markers, and acknowledgment/thanks patterns.
- Alternate/edge flows: Tests cover addressee-based reassignment in `resolve_addresses_other_violations` (including follow-through for short continuations) and similarity grouping behavior in `group_sentences_by_similarity` when segments are fewer than speakers or similarity scores are high.
- Error handling and recovery behavior: Tests verify deterministic behavior for empty/whitespace inputs and ensure no network or filesystem dependencies are introduced.

## Inputs / Outputs

- Inputs (CLI flags, files, env vars): In-memory sentence strings defined in Pytest tests under `tests/transform/`; no new CLI flags, files, or environment variables.
- Outputs (artifacts, logs, telemetry): Pytest results and coverage reports produced by the existing test toolchain.
- Config keys and defaults: None.
- Versioning or backward-compatibility constraints: No production API or output changes; tests only.

## API / CLI Surface

No public API or CLI surface changes.
- Example invocations with expected outputs (concise): `poetry run pytest tests/transform/` runs the new unit tests and should pass with coverage reports enabled by the existing workflow.
- Contracts and validation rules: Tests assert exact speaker-change indices or speaker assignments produced by the existing heuristics; no new runtime validation logic.

## Data & State

No new data storage or state. Tests operate on in-memory strings and lists.
- Data transformations and invariants: Tests codify existing heuristics in `detect_speaker_changes`, `detect_dialogue_markers`, `compute_sentence_similarity`, and `group_sentences_by_similarity`.
- Caching or persistence details: None.
- Migration or backfill requirements (if any): None.

## Constraints & Risks

Tests must remain deterministic and avoid filesystem or temporary files per unit-test policy.
- Limits (latency/throughput/memory) and acceptable trade-offs: Keep test inputs small and focused to maintain fast execution.
- Security/privacy considerations: No external services or sensitive data.
- Operational/rollout risks and mitigations: Risk of NLTK downloads during tests; mitigate by structuring tests to use deterministic inputs and avoid network dependency.

## Implementation Strategy

- Implementation scope (what changes, not sequencing): Add Pytest unit tests in `tests/transform/` for the existing heuristics and helpers in `speakerless.py` and `speaker_helpers.py`.
- New classes/functions/commands to add or update: New Pytest test functions targeting `has_speaker_labels`, `detect_speaker_changes`, `assign_speaker_labels`, `tokenize_into_sentences`, `detect_dialogue_markers`, `extract_sentence_features`, `compute_sentence_similarity`, `group_sentences_by_similarity`, and `resolve_addresses_other_violations`.
- Dependency changes (new/removed packages) and rationale: None.
- Logging/telemetry additions and locations: None.
- Rollout plan (feature flags, staged deploys, fallback path): Not applicable; tests only.

## Definition of Done

- [ ] Acceptance criteria documented and mapped to tests or demos (link new tests to each criterion in `user-story.md`).
- [ ] Behavior matches acceptance criteria in all documented environments (local runs per `docs/developer-tooling.md`).
- [ ] Tests updated/added (unit/integration as applicable) with new Pytest coverage in `tests/transform/`.
- [ ] Edge cases and error handling covered by tests (empty input, no-change scenarios, and addressee reassignment paths).
- [ ] Docs updated (README, docs/features/active/... links) if any test or coverage guidance changes.
- [ ] Telemetry/logging added or updated (if applicable) — not applicable for test-only changes.
- [ ] Toolchain pass completed (format → lint → type-check → test) per `docs/developer-tooling.md`.
