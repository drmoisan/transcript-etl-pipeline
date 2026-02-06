# atomic-executor-audit-bug (Potential Bug)

- Date captured: 2026-02-06
- Author: Dan Moisan
- Status: Draft

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

## Summary

Preflight checks did not enforce Phase 0 baseline evidence location/schema consistently with planning guidance.

## Environment

- OS/version:
- Python version:
- Command/flags used:
- Data source or fixture:

## Steps to Reproduce

1. ...
2. ...
3. ...

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened (include key error text).

## Logs / Screenshots

- [ ] Attached minimal logs or screenshot
- Snippet:

## Impact / Severity

- [ ] Blocker
- [ ] High
- [ ] Medium
- [ ] Low

## Suspected Cause / Notes

Updated `.github/agents/atomic_executor.agent.md` to require Phase 0 baseline artifacts in `<FEATURE>/evidence/baseline/` with `Timestamp`, `Command`, and `EXIT_CODE` fields for preflight consistency.

## Proposed Fix / Validation Ideas

- [ ] Unit coverage areas
- [ ] Integration scenario to retest
- [ ] Manual verification notes

## Next Step

- [ ] Promote to GitHub issue (bug-report template)
- [ ] Move to active fix folder / branch
