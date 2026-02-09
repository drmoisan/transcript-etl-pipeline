# pr-context-path-error (Issue #50)

- Date captured: 2026-02-09
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/pr-context-path-error/ (Issue #50)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #50
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/50
- Last Updated: 2026-02-09
## Summary

PR context collector crashes with NotADirectoryError when attempting to iterate over `README.md` file as if it were a directory in `docs/features/active/`.

## Environment

- OS/version: Windows 11
- Python version: Python 3.13
- Command/flags used: `poetry run python -m scripts.dev_tools.pr_context.collector --base origin/master`
- Data source or fixture: docs/features/active/ directory containing both subdirectories and a README.md file

## Steps to Reproduce

1. Ensure `docs/features/active/README.md` exists alongside feature subdirectories
2. Run `poetry run python -m scripts.dev_tools.pr_context.collector --base origin/master`
3. Observe crash during feature docs gathering

## Expected Behavior

The PR context collector should iterate only over feature subdirectories in `docs/features/active/`, ignoring non-directory items like `README.md`, and successfully collect feature documentation excerpts.

## Actual Behavior

The collector crashes with `NotADirectoryError: [WinError 267] The directory name is invalid: 'C:\\Users\\DanMoisan\\source\\repos\\transcript-etl-pipeline\\docs\\features\\active\\README.md'` when `_select_latest_version_dir()` attempts to call `iterdir()` on the README.md file path.

## Logs / Screenshots

- [x] Attached minimal logs or screenshot
- Snippet:

```
NotADirectoryError: [WinError 267] The directory name is invalid: 
'C:\\Users\\DanMoisan\\source\\repos\\transcript-etl-pipeline\\docs\\features\\active\\README.md'

File "C:\...\feature_docs.py", line 188, in gather_feature_excerpts
    resolved_dir = _select_latest_version_dir(active_dir)
File "C:\...\feature_docs.py", line 41, in _select_latest_version_dir
    for child in sorted(base_dir.iterdir()):
```

## Impact / Severity

- [x] Blocker - prevents PR context generation entirely
- [ ] High
- [ ] Medium
- [ ] Low

## Suspected Cause / Notes

In `scripts/dev_tools/pr_context/feature_docs.py`, the `_select_latest_version_dir()` function at line 41 iterates over all children returned by `base_dir.iterdir()` without filtering out files first. When `README.md` is encountered in the sorted iteration, the code later attempts to treat it as a directory, causing the crash.

The `is_dir()` check happens after sorting all items, but the error occurs because somewhere in the call chain a file path is being passed where a directory is expected.

## Proposed Fix / Validation Ideas

**Fix**: In `_select_latest_version_dir()` at line 41, filter to directories before sorting:

```python
# Filter out files immediately - only iterate over directories
dirs = [child for child in base_dir.iterdir() if child.is_dir()]

for child in sorted(dirs):
    # Extract version from directory name (v1, v2, etc.)
    match = re.match(r"^v(\d+)$", child.name)
    if match:
        return child
```

**Validation**:
- [x] Unit coverage: Add test for `_select_latest_version_dir()` with mixed files/directories
- [x] Integration scenario: Run full PR context collector with README.md present
- [x] Manual verification: Verify feature docs are properly extracted without crash

## Next Step

- [ ] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch