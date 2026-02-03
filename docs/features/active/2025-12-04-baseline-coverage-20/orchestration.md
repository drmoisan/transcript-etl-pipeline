# Coverage Epic Orchestration (issues #20, #21–#28)

Purpose: sequencing/parallelization plan for coverage work. Not for agents; use to decide which cloud agents to start and in what order.

## Parallel tracks (start in parallel)

- #21 `transform/enhance.py` tests (Agent A)
- #22 speakerless heuristics/helpers tests (Agent B)
- #23 identity_constraints/normalize tests (Agent C)
- #27 formatters + parser tests (Agent G)
- #28 CI coverage gate (Agent H)

These have minimal cross-dependencies and can run concurrently.

## Sequenced / intertwined work

- #24 3+ speaker fixtures/regressions (Agent D)
  - Can start in parallel, but coordinate with #22 to reuse heuristics inputs.
- #25 E2E speakerless + notes CLI flows (Agent E)
  - Benefits from fixtures in #24 but not strictly blocked; use existing fixtures and refit once #24 lands.
- #26 notes regressions (Agent F)
  - Independent, but align with #25 if overlapping notes workflows.

## Suggested launch order

1) Kick off #21, #22, #23, #27, #28 immediately (independent).
2) Start #24 soon after; sync with #22 to reuse multi-speaker snippets.
3) Start #25 once a baseline CLI fixture set is identified; can iterate when #24 adds richer fixtures.
4) Start #26 in parallel; coordinate with #25 if overlapping notes cases.

## Coordination tips

- Keep tests in `tests/...`; use the per-issue `*.agent.md` for scope/policies/acceptance.
- Update issue #20 checklist as each child issue progresses.
- If two issues touch the same fixtures, nominate one owner (e.g., #24) to host them and have others import/reuse.

## Coverage Gate Sequencing Criteria

Coverage gate ratchets should follow milestone completion and module targets:

1. **Baseline gate (15%)** — current CI default while #21–#23 are in progress.
2. **Gate to 20%** — after #21–#23 reach their per-module targets and M1 is marked complete.
3. **Gate to 30%** — after #26–#27 coverage targets are met and M2 is marked complete.
4. **Gate to 50%** — after #24–#25 regression/E2E fixtures stabilize and M3 is marked complete.

Each ratchet requires updated coverage evidence in the relevant plan/spec files and an initiative milestone status update.
