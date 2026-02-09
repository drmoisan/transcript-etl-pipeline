# Issue Update Mirror

Timestamp: 2026-02-06T22-22
IssueNumber: 24
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/24
PostedAs: body
IssueUpdatedAt: 2026-02-07T03:21:58Z
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-multi-speaker-fixtures-24/

## Exact posted text (machine-preserved)

~~~markdown
Scope:
- Add reusable fixtures for multi-speaker (3+) cases (e.g., SpaceX discussion) and regression tests.

Goals:
- Fixtures usable by speakerless/speaker_helpers tests.
- Integration assertions for expected grouping to prevent regressions.

Acceptance:
- Fixture assets checked in and referenced by tests.
- Regression tests fail on known bad behavior and pass after fixes.



## XFAIL Issue Mapping (multi-speaker regression)

The following xfail tests in `tests/transform/test_multi_speaker_regression.py` are tracked as dedicated bug issues:

- `TestIdentityAwareAssignment.test_generic_meeting_identity_constraints` → #45 (identity-constraint-ordering)
- `TestIdentityAwareAssignment.test_generic_meeting_addressing_constraints` → #46 (addressing-constraints-generic-meeting)
- `TestSpaceXDiscussionRegression.test_expected_speaker_rotation_pattern` → #47 (spacex-rotation-pattern)
- `TestTeamStandupRegression.test_addressing_team_members` → #48 (team-standup-addressing-constraints)
~~~

