# addressee-detection-enhancement - Spec

- Issue: #17
- Owner: drmoisan
- Last Updated: 2025-12-04

## Overview

Improve addressee detection by expanding vocative patterns and ensuring constraints prevent assigning utterances to the person being addressed during grouping and post-processing.

## Behavior

- Expand `detect_addresses_to_person()` to include:
  - Lead-in vocatives: "Oh, interesting, [Name]", "Exactly, [Name]", "Good point, [Name]".
  - Mid-sentence vocatives: "What do you think, [Name], about...".
- Enforce `addresses_other` constraints in:
  - Grouping (`group_sentences_by_similarity`) so addressed person is not selected.
  - Post-processing (`resolve_addresses_other_violations`) to reassign if violated.
- Add integration coverage: addressed utterances are not assigned to the addressee (e.g., "Hey Chris, how are you?" not assigned to Chris).

## Inputs / Outputs

- Inputs: existing speakerless transcripts; no new CLI flags.
- Outputs: unchanged API; improved assignments respecting addressee constraints.

## API / CLI Surface

- Internal changes only; tests under `tests/transform` and `tests/integration/test_speakerless_integration.py`.

## Data & State

- Uses constraint structures already in `identity_constraints.py` and consumed by grouping/post-processing.

## Constraints & Risks

- Avoid false positives from third-person mentions; limit to vocative/address patterns.
- Must not regress existing speakerless accuracy (2-speaker and other cases).
- Keep heuristic lightweight; logging optional.

## Definition of Done

- [ ] New patterns recognized in `detect_addresses_to_person()`.
- [ ] Constraints prevent addressed-person assignments in grouping/post-processing.
- [ ] Integration test for addressee handling passes.
- [ ] No regression in existing speakerless tests.
- [ ] Tooling/tests clean (black/ruff/pyright/pytest).

## Seeded Test Conditions

- [ ] Unit: new vocative patterns (lead-in + mid-sentence) in `identity_constraints.detect_addresses_to_person()`.
- [ ] Integration: "Hey Chris, how are you?" not assigned to Chris; constraints honored in grouping/post-processing.
- [ ] Verification of constraint consumption in `group_sentences_by_similarity()` and post-processing functions.
