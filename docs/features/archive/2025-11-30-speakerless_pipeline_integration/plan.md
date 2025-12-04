# 2025-11-30-speakerless_pipeline_integration - Plan

- Issue: N/A
- Owner: drmoisan
- Last Updated: 2025-12-03

## Required References (read, do not restate)

- Coding workflow and standards: [`docs/code-change.instructions.md`](../../../code-change.instructions.md)
- Unit test policy: [`docs/unit-test-policy.md`](../../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Integrate speakerless detection entry point [100%] 🟩
- [x] Detect absence of speaker labels and invoke speakerless assignment (2–4 speakers).
- [x] Ensure assigned labels flow into downstream parsing/formatting.

### Phase 2: Validation and tooling [100%] 🟩
- [x] Integration tests for speakerless transcripts; ensure labeled transcripts bypass detection.
- [x] Tooling clean: black/ruff/pyright/pytest.

## Test Plan

- Integration: speakerless transcripts (2–4 speakers) through full pipeline to DOCX/RTF/MD; labeled transcripts unchanged.
- Tooling: black, ruff, pyright, full pytest suite.

## Open Questions / Notes

- Advanced multi-speaker accuracy improvements tracked separately (speaker logic enhancement). 
