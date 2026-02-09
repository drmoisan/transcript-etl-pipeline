# spacex-rotation-pattern (Issue #47)

- Date captured: 2026-02-06
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/spacex-rotation-pattern/ (Issue #47)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #47
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/47
- Last Updated: 2026-02-06
## Summary

SpaceX 3-speaker regression expects a strict A/B/C rotation pattern that the current heuristics do not reliably achieve, so the regression remains xfail.

## Environment

- OS/version: Windows 11 (local dev)
- Python version: 3.13.7
- Command/flags used: `poetry run pytest tests/transform/test_multi_speaker_regression.py -k rotation_pattern`
- Data source or fixture: `tests/fixtures/multi_speaker.py` (`SPACEX_DISCUSSION`)

## Steps to Reproduce

1. Run `poetry run pytest tests/transform/test_multi_speaker_regression.py -k rotation_pattern`.
2. Observe `TestSpaceXDiscussionRegression.test_expected_speaker_rotation_pattern`.
3. Note the test is marked xfail due to imperfect rotation in natural conversation.

## Expected Behavior

The speaker labels should match the expected A/B/C rotation pattern defined in the SpaceX fixture for each line.

## Actual Behavior

Heuristic assignment can drift from the strict rotation pattern, producing mismatches and keeping the test xfail.

## Logs / Screenshots

- [ ] Attached minimal logs or screenshot
- Snippet: `pytest` reports xfail for `test_expected_speaker_rotation_pattern` with reason "Perfect A/B/C rotation in natural conversation is algorithmically challenging."

## Impact / Severity

- [ ] Blocker
- [ ] High
- [x] Medium
- [ ] Low

## Suspected Cause / Notes

Rotation enforcement is not a primary objective of current heuristics; ambiguous turn-taking can legitimately deviate from strict ordering.

## Proposed Fix / Validation Ideas

- [ ] Unit coverage areas: add a rotation-scoring heuristic or relax expected rotation pattern to tolerate ambiguous turns.
- [ ] Integration scenario to retest: un-xfail `test_expected_speaker_rotation_pattern` once rotation scoring is implemented.
- [ ] Manual verification notes: compare labeled output to `SPACEX_DISCUSSION.expected_lines`.

## Next Step

- [x] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch