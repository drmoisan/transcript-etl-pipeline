# identity-constraint-ordering (Issue #45)

- Date captured: 2026-02-06
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/identity-constraint-ordering/ (Issue #45)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #45
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/45
- Last Updated: 2026-02-06
## Summary

Identity constraint ordering in multi-speaker assignment does not consistently map the first self-identified speaker to Speaker A, so the identity-aware regression check remains xfail.

## Environment

- OS/version: Windows 11 (local dev)
- Python version: 3.13.7
- Command/flags used: `poetry run pytest tests/transform/test_multi_speaker_regression.py -k identity_constraints`
- Data source or fixture: `tests/fixtures/multi_speaker.py` (`GENERIC_MEETING_3SPEAKER`)

## Steps to Reproduce

1. Run `poetry run pytest tests/transform/test_multi_speaker_regression.py -k identity_constraints`.
2. Observe `TestIdentityAwareAssignment.test_generic_meeting_identity_constraints`.
3. Note the test is marked xfail due to ordering of self-identification vs speaker label assignment.

## Expected Behavior

Self-identification should deterministically map "I'm Peter Parker" → Speaker A, "My name is Frank Oz" → Speaker B, "I'm Fred Flintstone" → Speaker C.

## Actual Behavior

Speaker labels can be assigned out of order relative to the first self-identification turn, so the strict identity constraints fail and the test remains xfail.

## Logs / Screenshots

- [ ] Attached minimal logs or screenshot
- Snippet: `pytest` reports xfail for `test_generic_meeting_identity_constraints` with reason "Identity constraint ordering: first speaker identification may not map to Speaker A due to sentence tokenization and change detection order."

## Impact / Severity

- [ ] Blocker
- [ ] High
- [x] Medium
- [ ] Low

## Suspected Cause / Notes

Speaker label assignment order depends on change detection order and sentence tokenization, so self-identification does not anchor Speaker A deterministically.

## Proposed Fix / Validation Ideas

- [ ] Unit coverage areas: add deterministic anchoring for first self-identification to Speaker A when `num_speakers` is provided.
- [ ] Integration scenario to retest: re-run `test_generic_meeting_identity_constraints` without xfail once anchoring is implemented.
- [ ] Manual verification notes: confirm labeled output assigns Peter/Frank/Fred to A/B/C in `GENERIC_MEETING_3SPEAKER`.

## Next Step

- [x] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch