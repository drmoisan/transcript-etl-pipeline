# atomic-executor-audit-bug (Issue #43)

- Date captured: 2026-02-06
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/atomic-executor-audit-bug/ (Issue #43)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #43
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/43
- Last Updated: 2026-02-06

## Summary

Atomic executor agent docs now reference shared skills for policy order, evidence locations, and canonical evidence headers, but the hybrid `atomic_executor` package still embeds older guidance. The package does not incorporate the new skills-based sources or updated canonical evidence conventions, so generated prompts and preflight expectations can drift from the updated agent instructions.

## Environment

- OS/version: Windows (per local dev environment)
- Python version: 3.13.7 (observed in recent pytest evidence)
- Command/flags used: N/A (doc/package review; no executor run captured)
- Data source or fixture: N/A

## Steps to Reproduce

1. Update agent docs to reference shared skills for policy order, canonical evidence locations, and evidence header schema (as in the recent commit).
2. Run the hybrid `atomic_executor` CLI or prompt builder to generate execution guidance for a feature plan.
3. Compare the generated guidance and preflight expectations to the updated agent instructions/skills (e.g., required `<FEATURE>/evidence/baseline/` location and `Timestamp/Command/EXIT_CODE` headers).

## Expected Behavior

The hybrid `atomic_executor` package should load or embed the same shared skills content as the updated agent docs, so generated prompts and preflight checks align with canonical evidence locations and required header fields.

## Actual Behavior

The hybrid `atomic_executor` package still uses older, embedded guidance that does not reference the shared skills or updated evidence conventions. As a result, prompts and preflight expectations can point at outdated locations or omit the required header schema.

## Logs / Screenshots

- [ ] Attached minimal logs or screenshot
- Snippet:
	- N/A (doc/package diff identified; no runtime log captured)

## Impact / Severity

- [ ] Blocker
- [ ] High
- [x] Medium
- [ ] Low

## Suspected Cause / Notes

Agent documentation now references shared skills (policy order, evidence locations, canonical header schema), but the hybrid `atomic_executor` package did not get corresponding updates. The prompt generation and preflight logic in `scripts/dev_tools/atomic_executor/` still rely on older embedded rules instead of reading the shared skills or the updated agent instructions.

## Proposed Fix / Validation Ideas

- [ ] Update prompt generation to reference shared skills (policy order, evidence location, evidence header schema) instead of duplicated text in the hybrid package.
- [ ] Update preflight QC expectations in the hybrid package to enforce `<FEATURE>/evidence/baseline/` and `Timestamp/Command/EXIT_CODE` headers for Phase 0 evidence.
- [ ] Add/adjust tests in `tests/dev_tools/atomic_executor/` to verify skills-based text is present in prompt output and that preflight expectations match canonical evidence rules.
- [ ] Manual verification: run `atomic_executor` against a feature plan and confirm generated prompt references skills, and preflight rejects evidence missing canonical headers.

## Next Step

- [ ] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch