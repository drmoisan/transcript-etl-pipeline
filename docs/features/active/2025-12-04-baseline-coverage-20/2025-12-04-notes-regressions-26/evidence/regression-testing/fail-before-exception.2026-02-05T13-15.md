# Fail-before Exception Dossier — notes-regressions-26

BaselineCommit: 3ab288535f1eecea32a940806044ce63afa63f9a
Timestamp: 2026-02-05T13:15:57Z
Command: documentation-only
EXIT_CODE: 0
WhyFailingRunImpossible: The regression tests for notes conversion were introduced after the baseline commit, so the baseline revision cannot run the new tests to produce a strict fail-before failure.
AlternativeProof: Absence-of-test proof via `git grep` at the baseline commit, plus commit evidence showing when the regression tests were added.

## Command Evidence

### Evidence: baseline commit does not include test_regression_clean_markdown_text_escapes

Command: git -C /workspaces/transcript-etl-pipeline grep -n "test_regression_clean_markdown_text_escapes" 3ab288535f1eecea32a940806044ce63afa63f9a -- tests/transform/test_notes.py

Output:
```
EXIT_CODE:1
```

Timestamp: 2026-02-05T13:15:57Z
EXIT_CODE: 1

### Evidence: baseline commit does not include test_regression_parse_markdown_mixed_order

Command: git -C /workspaces/transcript-etl-pipeline grep -n "test_regression_parse_markdown_mixed_order" 3ab288535f1eecea32a940806044ce63afa63f9a -- tests/transform/test_notes.py

Output:
```
EXIT_CODE:1
```

Timestamp: 2026-02-05T13:15:57Z
EXIT_CODE: 1

### Evidence: commit introducing regression tests in test_notes.py

Command: git -C /workspaces/transcript-etl-pipeline show --name-status 6a3ebdcffd132ad076c25b464ac21a2ec11e3baa -- tests/transform/test_notes.py

Output:
```
commit 6a3ebdcffd132ad076c25b464ac21a2ec11e3baa
Author: drmoisan <54180981+drmoisan@users.noreply.github.com>
Date:   Mon Feb 2 19:21:39 2026 -0500

    Update parser metadata handling and coverage docs

M       tests/transform/test_notes.py
EXIT_CODE:0
```

Timestamp: 2026-02-05T13:15:57Z
EXIT_CODE: 0
