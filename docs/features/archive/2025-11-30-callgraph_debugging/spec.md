# 2025-11-30-callgraph_debugging - Spec

- Issue: N/A
- Owner: drmoisan
- Last Updated: 2025-12-03

## Overview

Provide callgraph debugging utilities to wrap functions, generate DOT and Mermaid outputs, and view in Markdown, with proper package wiring and state reset.

## Behavior

- Import `run_with_callgraph` from `transcript_etl_pipeline.devtools`.
- Wrap a target function; execution produces `callgraph.dot` (Graphviz) and `callgraph.mmd` (Mermaid).
- Support embedding Mermaid output in Markdown.
- Provide `reset_callgraph()` to clear state between runs.

## Inputs / Outputs

- Input: a callable to wrap (e.g., `run_with_callgraph(my_function)`).
- Outputs: `callgraph.dot`, `callgraph.mmd` files; optional Markdown embedding snippet.

## API / CLI Surface

- Python API:
  ```python
  from transcript_etl_pipeline.devtools import run_with_callgraph, reset_callgraph
  result = run_with_callgraph(my_function)
  ```
- Examples: `examples/callgraph_example.py`.
- Docs: `src/transcript_etl_pipeline/devtools/README.md`, `docs/debug_callgraph_fixes.md`.

## Data & State

- Callgraph state resettable via `reset_callgraph()` to avoid cross-run contamination.
- Package path fixed to `transcript_etl_pipeline` for correct module resolution.

## Constraints & Risks

- Must not affect production pipeline runtime; dev-only utility.
- Keep outputs in standard formats (DOT, Mermaid) for compatibility.

## Definition of Done

- [x] Callgraph utilities available via `transcript_etl_pipeline.devtools`.
- [x] Generates DOT and Mermaid outputs; Markdown embedding supported.
- [x] State reset provided.
- [x] Tests/tooling passing (33 tests for callgraph; full suite 347/348 reported).

## Seeded Test Conditions

- [x] run_with_callgraph produces expected DOT/Mermaid files.
- [x] reset_callgraph clears state; repeated runs produce clean outputs.
- [x] Module import path uses `transcript_etl_pipeline` (not `yourpackage`).
