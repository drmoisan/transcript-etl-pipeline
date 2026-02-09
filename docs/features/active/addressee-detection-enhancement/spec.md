# addressee-detection-enhancement - Spec

- Issue: #17
- Owner: drmoisan
- Last Updated: 2025-12-04

## Overview

Improve addressee detection by expanding vocative patterns and ensuring `addresses_other` constraints prevent assigning utterances to the person being addressed during grouping and post-processing. Scope is limited to regex-based heuristics in existing identity-constraint and speakerless grouping logic, with no CLI surface changes.

## Behavior

- Expand `detect_addresses_to_person()` to include:
  - Lead-in vocatives with comma-bound direct address, e.g., "Oh, interesting, [Name]", "Exactly, [Name]", "Good point, [Name]", "Hey, [Name]" and "Hey [Name], …".
  - Mid-sentence vocatives bounded by commas, e.g., "What do you think, [Name], about…".
  - Maintain existing exclusions for self-identification and third-person/appositive patterns (e.g., "is [Name] a/the …").
- Enforce `addresses_other` constraints in:
  - Grouping (`group_sentences_by_similarity`) so the addressed person is not selected when a viable alternative exists.
  - Post-processing (`resolve_addresses_other_violations`) to reassign if a violation slips through grouping (existing behavior applies for $\ge 3$ speakers).
- Add integration coverage: addressed utterances are not assigned to the addressee (e.g., "Hey Chris, how are you?" not assigned to Chris).

## Inputs / Outputs

- Inputs:
  - Existing speakerless transcripts (list of sentence strings) processed through `extract_identity_constraints`.
  - No new CLI flags or configuration.
- Outputs:
  - Unchanged public API and CLI behavior.
  - Improved sentence-to-speaker assignments that respect `addresses_other` constraints during grouping and post-processing.

## API / CLI Surface

- Internal changes only; no new CLI flags.
- Target functions:
  - `identity_constraints.detect_addresses_to_person()`
  - `speaker_helpers.group_sentences_by_similarity()`
  - `speaker_helpers.resolve_addresses_other_violations()`
- Tests live under `tests/transform` and `tests/integration/test_speakerless_integration.py`.

## Data & State

- Uses existing constraint structures in `identity_constraints.py` and consumption in grouping/post-processing.
- `IdentityConstraint` shape (existing): `{sentence_idx: int, constraint_type: "self_identification"|"addresses_other", name: str}`.
- No new persistence or caching; constraints are ephemeral and sentence-indexed.

## Constraints & Risks

- Avoid false positives from third-person mentions or appositives; limit to comma-bounded vocative/address patterns.
- Must not regress existing speakerless accuracy (2-speaker and other cases).
- Keep heuristic lightweight (regex-only); no new dependencies.
- Risk: punctuation variance (missing commas) may still be missed; acceptable for this scope.

## Definition of Done

- [ ] New patterns recognized in `detect_addresses_to_person()`.
- [ ] Constraints prevent addressed-person assignments in grouping/post-processing.
- [ ] Unit tests in `tests/transform/test_identity_constraints.py` cover lead-in, mid-sentence, and negative cases.
- [ ] Integration test in `tests/integration/test_speakerless_integration.py` covers “Hey Chris, how are you?” case.
- [ ] Integration test for addressee handling passes.
- [ ] No regression in existing speakerless tests.
- [ ] Tooling/tests clean (black/ruff/pyright/pytest).

## Seeded Test Conditions

- [ ] Unit: lead-in vocatives (e.g., "Oh, interesting, Chris", "Hey Chris, …") are detected as `addresses_other`.
- [ ] Unit: mid-sentence comma-bounded vocatives (e.g., "What do you think, Chris, about…") are detected.
- [ ] Unit: negative cases (self-identification, appositives, third-person questions) do not trigger `addresses_other`.
- [ ] Integration: "Hey Chris, how are you?" is not assigned to Chris; constraints are honored in grouping/post-processing.
- [ ] Verification of constraint consumption in `group_sentences_by_similarity()` and post-processing functions.
