# addressing-constraints-generic-meeting (Issue #46)

- Date captured: 2026-02-06
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/addressing-constraints-generic-meeting/ (Issue #46)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #46
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/46
- Last Updated: 2026-02-06
## Summary

Addressing constraints in the generic meeting fixture do not reliably prevent assigning the addressed speaker to the addressing line, so the regression remains xfail.

## Environment

- OS/version: Windows 11 (local dev)
- Python version: 3.13.7
- Command/flags used: `poetry run pytest tests/transform/test_multi_speaker_regression.py -k addressing_constraints`
- Data source or fixture: `tests/fixtures/multi_speaker.py` (`GENERIC_MEETING_3SPEAKER`)

## Steps to Reproduce

1. Run `poetry run pytest tests/transform/test_multi_speaker_regression.py -k addressing_constraints`.
2. Observe `TestIdentityAwareAssignment.test_generic_meeting_addressing_constraints`.
3. Note the test is marked xfail because addressing-other constraints are not consistently enforced.

## Expected Behavior

Lines like "Thanks Frank" should not be assigned to Speaker B (Frank), and "Fred?" should not be assigned to Speaker C (Fred).

## Actual Behavior

Addressing lines can be assigned to the addressed speaker when identities are established mid-conversation, so the strict constraint check fails and remains xfail.

## Logs / Screenshots

- [ ] Attached minimal logs or screenshot
- Snippet: `pytest` reports xfail for `test_generic_meeting_addressing_constraints` with reason "Addresses-other constraint enforcement may not work when speaker identity is established mid-conversation."

## Impact / Severity

- [ ] Blocker
- [ ] High
- [x] Medium
- [ ] Low

## Suspected Cause / Notes

Addressing constraints are evaluated before identity stabilization for all speakers, allowing addressed names to be mis-assigned.

## Proposed Fix / Validation Ideas

- [ ] Unit coverage areas: enforce addressing constraints after identity stabilization or re-score lines with addressed-name penalties.
- [ ] Integration scenario to retest: un-xfail `test_generic_meeting_addressing_constraints` once constraint enforcement is updated.
- [ ] Manual verification notes: confirm "Thanks Frank" is not assigned to Speaker B in labeled output.

## Next Step

- [x] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch