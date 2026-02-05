# Fail-before Exception Dossier — notes-regressions-26

BaselineCommit: 3ab288535f1eecea32a940806044ce63afa63f9a
WhyFailingRunImpossible: The failing regression tests referenced in this feature did not exist at the baseline commit, so a direct fail-before run cannot be reproduced from that revision.
AlternativeProof: The command evidence below demonstrates the absence of the relevant tests and file paths at the baseline commit, which is the authoritative basis for the fail-before exception.

## Command Evidence

(Blocks added below.)

### Evidence: git grep test name absence

Command: git grep -n "test_cli_e2e_notes" 3ab288535f1eecea32a940806044ce63afa63f9a -- tests/integration

Output:
```
EXIT_CODE: 1
```

Timestamp: 2026-02-05T02:52:44Z
EXIT_CODE: 1

### Evidence: git show file path absence

Command: git show 3ab288535f1eecea32a940806044ce63afa63f9a:tests/integration/test_cli_e2e_notes.py

Output:
```
fatal: path 'tests/integration/test_cli_e2e_notes.py' exists on disk, but not in '3ab288535f1eecea32a940806044ce63afa63f9a'
EXIT_CODE: 128
```

Timestamp: 2026-02-05T02:53:04Z
EXIT_CODE: 128
