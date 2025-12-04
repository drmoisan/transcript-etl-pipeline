# 2025-11-30-callgraph_debugging - Plan

- Issue: N/A
- Owner: drmoisan
- Last Updated: 2025-12-03

## Required References (read, do not restate)

- Coding workflow and standards: [`docs/code-change.instructions.md`](../../../code-change.instructions.md)
- Unit test policy: [`docs/unit-test-policy.md`](../../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Fix package wiring and state management [100%] 🟩
- [x] Update package name from `yourpackage` to `transcript_etl_pipeline`.
- [x] Add `reset_callgraph()` to clear state between runs.

### Phase 2: Outputs and docs [100%] 🟩
- [x] Ensure `run_with_callgraph` emits `callgraph.dot` and `callgraph.mmd`.
- [x] Document Markdown embedding for Mermaid output.
- [x] Provide examples and fix docs (`devtools/README`, `debug_callgraph_fixes.md`, `examples/callgraph_example.py`).

### Phase 3: Testing and validation [100%] 🟩
- [x] Add/verify 33 tests for callgraph utilities.
- [x] Full suite reported 347/348 passing at completion.
- [x] Tooling clean (black/ruff/pyright).

## Test Plan

- Unit: callgraph capture, file outputs (DOT/Mermaid), state reset behavior.
- Integration: sample function wrapped via `run_with_callgraph`; Markdown embedding snippet validated.
- Tooling: black, ruff, pyright, pytest (callgraph suite).

## Open Questions / Notes

- Dev-only utility; no production runtime impact. 
