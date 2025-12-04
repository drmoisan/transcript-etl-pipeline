# addressee-detection-enhancement - Plan

- Issue: #17
- Owner: drmoisan
- Last Updated: 2025-12-04

## Required References (read, do not restate)

- Coding workflow and standards: [docs/code-change.instructions.md](../../code-change.instructions.md)
- Unit test policy: [docs/unit-test-policy.md](../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Pattern expansion [0%]
- [ ] Add lead-in vocatives: "Oh, interesting, [Name]", "Exactly, [Name]", "Good point, [Name]".
- [ ] Add mid-sentence vocatives: "What do you think, [Name], about...".
- [ ] Unit tests for new patterns in `detect_addresses_to_person()`.

### Phase 2: Constraint enforcement [0%]
- [ ] Verify/ensure `addresses_other` constraints are consumed in `group_sentences_by_similarity()`.
- [ ] Verify/ensure post-processing (`resolve_addresses_other_violations`) reassigns when violated.
- [ ] Add unit/integration coverage for enforcement.

### Phase 3: Integration validation [0%]
- [ ] Integration test: "Hey Chris, how are you?" not assigned to Chris.
- [ ] Regression check: no failures in existing speakerless tests.
- [ ] Tooling: black/ruff/pyright/pytest.

## Test Plan

- Unit: new vocative patterns; enforcement path for constraints in grouping/post-processing.
- Integration: speakerless pipeline test for addressed-person reassignment.
- Tooling: black, ruff, pyright, full pytest suite.

## Open Questions / Notes

- Keep patterns narrow to avoid third-person mentions; ensure no regression in 2-speaker cases.
