# 2025-11-30-identity_aware_speaker_detection - Plan

- Issue: N/A (completed change plan, PR #8)
- Owner: drmoisan
- Last Updated: 2025-12-02

## Required References (read, do not restate)

- Coding workflow and standards: [`docs/code-change.instructions.md`](../../../code-change.instructions.md)
- Unit test policy: [`docs/unit-test-policy.md`](../../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Identity extraction foundation [100%] 🟩
- [x] Create `identity_constraints.py` with `IdentityConstraint` dataclass.
- [x] Implement `detect_self_identification()` and `detect_addresses_to_person()` (vocatives).
- [x] Unit tests (33) for constraint extraction.
- [x] Kept legacy `speakers.py` address detection separate (semantic differences).

### Phase 2: Constraint-aware grouping [100%] 🟩
- [x] Update `group_sentences_by_similarity()` to accept/enforce constraints.
- [x] Add `violates_identity_constraints()` to block merges that conflict with identities.
- [x] Enhance fallback logic for constraint-safe assignment.
- [x] Tests (11) for grouping with constraints.

### Phase 3: Post-processing addresses_other [100%] 🟩
- [x] Implement `resolve_addresses_other_violations()` with conservative reassignment.
- [x] Add `_find_safe_replacement_speaker()` helper; log debug/warnings.
- [x] Tests (6) for post-processing.

### Phase 4: Test enhancement [100%] 🟩
- [x] 50 total new tests across modules (constraints, grouping, post-processing).
- [x] Integration: `test_explicit_three_speakers()` validates end-to-end identity-aware behavior.

### Phase 5: Validation & docs [100%] 🟩
- [x] Tooling: black/ruff/pyright clean; pytest 509 passing.
- [x] README and change plan updated; code documented.

## Test Plan

- Unit: constraint extraction, constraint-aware grouping, post-processing helpers.
- Integration: explicit three-speaker scenarios with self-ID and addressee constraints; baseline no-constraint behavior.
- Tooling: black, ruff, pyright, full pytest suite.

## Open Questions / Notes

- Nice-to-haves (not implemented): performance benchmarks, visual debug output, extended edge-case coverage.
