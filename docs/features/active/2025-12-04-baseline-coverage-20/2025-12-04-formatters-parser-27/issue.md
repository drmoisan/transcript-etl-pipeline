# formatters-parser (Issue [#27](https://github.com/drmoisan/transcript-etl-pipeline/issues/27))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/ (Issue #27)

- Issue: #27
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/27](https://github.com/drmoisan/transcript-etl-pipeline/issues/27)
- Last Updated: 2025-12-04

## Problem / Why

Formatters and the document parser lack targeted unit coverage, leaving spacing/label rules and parsing behavior vulnerable to regressions.

## Proposed Behavior

Add unit tests for formatter modules (DOCX/RTF/MD) and document/parser.py that validate key formatting rules and parsed structures, targeting at least 70% coverage in these modules.

## Acceptance Criteria (early draft)

- [ ] Tests assert on key formatting/spacing rules and parsed structures.
- [ ] Coverage report shows >=70% for formatters and parser modules.

## Constraints & Risks

- Avoid brittle assertions tied to binary DOCX output; prefer text/structure checks.
- Keep scope limited to formatters and document parser behaviors.

## Test Conditions to Consider

- [ ] Unit tests for formatting rules in docx_formatter.py, rtf_formatter.py, md_formatter.py.
- [ ] Parser tests for representative sample inputs and expected structure.
- [ ] Optional round-trip parsing assertions where feasible.

## Next Step

- [x] Promote to GitHub issue (Issue #27)
- [ ] Create `docs/features/active/formatters-parser/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** Partially delivered; acceptance criteria not fully evidenced.
- **Evidence highlights:** Formatter/parser tests in `tests/formatters/` and `tests/document/test_parser_unit.py`; coverage evidence recorded in plan Phase 5.
- **Open gaps:** Issue #27 update not recorded; QA toolchain steps not verified.

