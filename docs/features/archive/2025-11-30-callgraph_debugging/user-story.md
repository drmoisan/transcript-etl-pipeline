# 2025-11-30-callgraph_debugging - User Story

- Issue: N/A
- Owner: drmoisan
- Status: Complete
- Last Updated: 2025-12-03

## Problem / Why

We needed a simple way to run functions with callgraph tracing to visualize pipeline execution (Graphviz/Mermaid) for debugging and documentation, with correct package wiring and state reset.

## Personas & Scenarios

- Persona: Developer debugging pipeline flows  
  - Scenario: Wrap a function with callgraph tracing, generate DOT/Mermaid, and view in Markdown.

## User Stories

- As a developer, I want to run a function with callgraph tracing and get DOT/Mermaid outputs.
- As a developer, I want the callgraph tooling to reset state between runs and use the correct package/module paths.

## Acceptance Criteria

- [x] `run_with_callgraph` available from `transcript_etl_pipeline.devtools`.
- [x] Outputs `callgraph.dot` and `callgraph.mmd` for a wrapped function.
- [x] Supports embedding Mermaid in Markdown easily.
- [x] State reset available (`reset_callgraph()`); package paths fixed.
- [x] Tests/tooling passing for callgraph module (33 tests).

## Non-Goals

- Performance optimization or advanced visualization beyond DOT/Mermaid exports.
