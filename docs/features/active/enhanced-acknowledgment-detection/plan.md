# enhanced-acknowledgment-detection - Plan

- Issue: #18
- Owner: drmoisan
- Last Updated: 2025-12-04

## Required References (read, do not restate)

- Coding workflow and standards: [docs/code-change.instructions.md](../../code-change.instructions.md)
- Unit test policy: [docs/unit-test-policy.md](../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Expand acknowledgment lexicon [0%]
- [ ] Add missing words: “exactly”, “true”, “fair”, “definitely”, “certainly”, “agreed”, “correct”, “indeed”.
- [ ] Unit tests to confirm detection.

### Phase 2: Exclamation acknowledgments [0%]
- [ ] Detect “Ha!”, “Wow!”, “Nice!”, “Cool!” as acknowledgments that can signal speaker change.
- [ ] Unit tests for exclamation handling.

### Phase 3: Context-aware handling [0%]
- [ ] Add simple context check (comma/short utterance) to differentiate filler vs acknowledgment.
- [ ] Adjust detection to avoid over-triggering on “yeah I think…” cases.
- [ ] Unit tests for context-sensitive logic.

### Phase 4: Integration & regression [0%]
- [ ] Integration tests for acknowledgment scenarios; ensure no regression on existing speakerless tests.
- [ ] Validate 3-speaker SpaceX test trends toward 18 lines.
- [ ] Tooling: black/ruff/pyright/pytest.

## Test Plan

- Unit: new words, exclamation detection, context-aware acknowledgment logic, boundary cases.
- Integration: speakerless pipeline grouping with acknowledgments; 2-speaker regression checks; target fixture (`test_3speaker_spacex_discussion.py`) improves line count/assignments.
- Tooling: black, ruff, pyright, full pytest suite.

## Open Questions / Notes

- Keep heuristics narrow to avoid third-person mentions; ensure minimal runtime impact. 
