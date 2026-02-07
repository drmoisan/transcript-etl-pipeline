# Issue Update Mirror

Timestamp: 2026-02-04T11-21
IssueNumber: 26
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/26
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/

This file is the **local mirror** for GitHub Issue #26 updates, required even when GitHub access is available.

CapturedVia:
- `gh issue view 26 -R drmoisan/transcript-etl-pipeline --json url,title,updatedAt,body`
- `gh api repos/drmoisan/transcript-etl-pipeline/issues/26/comments`

RemoteVerification:
- GitHub CLI/auth available: Yes
- Comments found: 0

## Exact posted text (machine-preserved)

### Issue JSON (authoritative)

~~~json
{"body":"Scope:\n- Capture known notes conversion issues from prior work/feature_status and add regression tests.\n\nGoals:\n- Each known bug gets a failing-before/passing-after regression test.\n- Expand coverage of transform/notes.py and related paths.\n\nAcceptance:\n- Regression tests demonstrate the prior failure and now pass.\n- Coverage on notes-related paths measurably improves.\n## Regression Cases (Automated)\n\n1. Markdown cleanup removes formatting markers while preserving literal symbols.\n2. Bullet indentation levels are mapped consistently.\n3. Heading level detection ignores leading whitespace.\n4. Notes label is inserted as H2 after an H1 title when a label is provided.\n5. Mixed heading/bullet ordering is preserved.\n\n## Coverage Evidence (Automated)\n\n```Notes Coverage\nThe currently activated Python version 3.10.19 is not supported by the project (^3.12).\nTrying to find and use a compatible version. \nUsing python3.14 (3.14.0)\nSkipping virtualenv creation, as specified in config file.\nName                                             Stmts   Miss  Cover\n--------------------------------------------------------------------\nsrc/transcript_etl_pipeline/transform/notes.py      78      1    99%\n--------------------------------------------------------------------\nTOTAL                                               78      1    99%\n```\n\nFull coverage report: [coverage.2026-02-03T18-30.txt](https://github.com/davidvonthenen/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/remediation-baseline/coverage.2026-02-03T18-30.txt)\n\n## Fail-before evidence\n\nSee [fail-before.2026-02-03T18-30.md](https://github.com/davidvonthenen/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/remediation-baseline/fail-before.2026-02-03T18-30.md)\n\nThis documents the baseline state (commit `3ab288535f1eecea32a940806044ce63afa63f9a`) where the 5 regression tests did not exist. The \"fail-before\" state for new regression tests is the absence of the tests themselves.\n\n## Pass-after evidence\n\nSee [pass-after.2026-02-03T18-30.txt](https://github.com/davidvonthenen/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/remediation-baseline/pass-after.2026-02-03T18-30.txt)\n\nAll 27 tests in `tests/transform/test_notes.py` now pass, including the 5 new regression tests (`test_regression_*` prefix). This demonstrates that the regression tests correctly capture and verify the fixes for the known notes conversion issues.\n","title":"Add regression tests for notes conversion edge cases","updatedAt":"2026-02-04T12:23:58Z","url":"https://github.com/drmoisan/transcript-etl-pipeline/issues/26"}
~~~

### Comments JSON

~~~json
[]
~~~
