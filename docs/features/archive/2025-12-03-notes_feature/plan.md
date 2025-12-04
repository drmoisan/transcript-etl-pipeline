# notes_feature - Plan

- Issue: #14
- Owner: drmoisan
- Last Updated: 2025-12-03

## Required References (read, do not restate)

- Coding workflow and standards: [docs/code-change.instructions.md](../../code-change.instructions.md)
- Unit test policy: [docs/unit-test-policy.md](../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Core domain model (notes-aware document model, merge logic) [100%] 🟩
- [x] Add SectionType entries for notes header/body; paragraph bullet support
- [x] Implement Document.merge_notes / merge_transcript with ordering (Metadata → Notes → Transcript)
- [x] Unit tests for merge behaviors

### Phase 2: Notes pipeline (extract/transform) [100%] 🟩
- [x] Reuse file/clipboard ingest for notes
- [x] Implement transform/notes.py to parse markdown notes (headers, bullets)
- [x] Auto-generate notes headers with timestamp when absent
- [x] Unit tests for notes transformation

### Phase 3: Document reader (re-ingestion) [100%] 🟩
- [x] Implement document/reader.py to parse existing DOCX/MD into Document
- [x] Detect section boundaries via headers/styles
- [x] Unit tests for MD and DOCX parsing

### Phase 4: Formatters [100%] 🟩
- [x] Update DOCX/MD/RTF formatters for notes sections (headers, bullets)
- [x] Unit tests for formatter output

### Phase 5: CLI & UI wiring [100%] 🟩
- [x] Add flags for notes source/file, mode (new/update), update actions
- [x] Implement run_unified_pipeline orchestration for notes + transcript

### Phase 6: End-to-end testing [100%] 🟩
- [x] E2E flows: notes → new doc; transcript → update doc; notes → replace/add; multi-step workflows
- [x] Keep transcript-only flows intact

## Test Plan

- Unit: merge logic (notes/transcript), notes transformation, reader parsing (MD/DOCX), formatter rendering.
- Integration: new vs existing document; notes-only, transcript-only, both; add vs replace variants.
- CLI/UX examples: flags for notes/transcript source/file; mode new/update; add/replace actions; labels/timestamps.
- Performance/edge cases: unparsable docs; empty clipboard; non-markdown notes; deterministic ordering and headers.

## Open Questions / Notes

- Risks: DOCX re-ingestion can be lossy—mitigate with strict header/style matching; clipboard reliability handled by existing abstraction.
- Summary from prior plan: ~94 new tests (merge 20, notes transform 23, reader 30, formatter 10, end-to-end 11); all checks green (pyright/ruff/black/pytest).
