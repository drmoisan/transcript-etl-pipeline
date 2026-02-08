# team-standup-addressing-constraints (Issue #48)

- Date captured: 2026-02-06
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/team-standup-addressing-constraints/ (Issue #48)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #48
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/48
- Last Updated: 2026-02-06
## Summary

Team standup addressing constraints do not reliably keep the meeting lead (Speaker A) as the speaker when addressing team members by name, so the regression remains xfail.

## Environment

- OS/version: Windows 11 (local dev)
- Python version: 3.13.7
- Command/flags used: `poetry run pytest tests/transform/test_multi_speaker_regression.py -k addressing_team_members`
- Data source or fixture: `tests/fixtures/multi_speaker.py` (`TEAM_STANDUP_3SPEAKER`)

## Steps to Reproduce

1. Run `poetry run pytest tests/transform/test_multi_speaker_regression.py -k addressing_team_members`.
2. Observe `TestTeamStandupRegression.test_addressing_team_members`.
3. Note the test is marked xfail due to inconsistent addressing constraints.

## Expected Behavior

Lines like "Sarah, you're next" and "Mike, what about you" should be assigned to Speaker A (the meeting lead), not the addressed speaker.

## Actual Behavior

Addressing lines can be assigned to the addressed speaker, so the strict constraint check fails and remains xfail.

## Logs / Screenshots

- [ ] Attached minimal logs or screenshot
- Snippet: `pytest` reports xfail for `test_addressing_team_members` with reason "Addressing constraints for team members by name requires the algorithm to recognize that 'Sarah, you're next' comes from a different speaker than Sarah."

## Impact / Severity

- [ ] Blocker
- [ ] High
- [x] Medium
- [ ] Low

## Suspected Cause / Notes

Addressing constraints are not enforced strongly enough when name tokens appear in the same sentence as the addressed speaker.

## Proposed Fix / Validation Ideas

- [ ] Unit coverage areas: add addressing-name penalty to speaker assignment when a line explicitly addresses someone.
- [ ] Integration scenario to retest: un-xfail `test_addressing_team_members` once addressing constraints are reinforced.
- [ ] Manual verification notes: confirm the meeting lead retains those addressing lines in labeled output.

## Next Step

- [x] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch