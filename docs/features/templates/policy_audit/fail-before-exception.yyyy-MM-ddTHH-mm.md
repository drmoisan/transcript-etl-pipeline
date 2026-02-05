# Fail-before Exception Dossier — [feature-name]

BaselineCommit: [SHA]
Timestamp: [YYYY-MM-DDTHH:MM:SSZ]
Command: documentation-only
EXIT_CODE: 0
WhyFailingRunImpossible: [1–3 sentences explaining why a fail-before run cannot be reproduced at the baseline commit.]
AlternativeProof: [Describe the absence-of-test proof or other alternative evidence.]

## Command Evidence

### Evidence: baseline commit does not include [test-name-1]

Command: git -C [repo-root] grep -n "[test-name-1]" [BaselineCommit] -- [test-file-path]

Output:
```
EXIT_CODE:[int]
```

Timestamp: [YYYY-MM-DDTHH:MM:SSZ]
EXIT_CODE: [int]

### Evidence: baseline commit does not include [test-name-2]

Command: git -C [repo-root] grep -n "[test-name-2]" [BaselineCommit] -- [test-file-path]

Output:
```
EXIT_CODE:[int]
```

Timestamp: [YYYY-MM-DDTHH:MM:SSZ]
EXIT_CODE: [int]

### Evidence: commit introducing characterization tests

Command: git -C [repo-root] show --name-status [commit-introducing-tests] -- [test-file-path]

Output:
```
commit [commit-introducing-tests]
Author: [author]
Date:   [date]

    [commit subject]

M       [test-file-path]
EXIT_CODE:[int]
```

Timestamp: [YYYY-MM-DDTHH:MM:SSZ]
EXIT_CODE: [int]
