# 2025-11-30-callgraph_debugging - User Story

- Issue: N/A
- Owner: drmoisan
- Status: Complete
- Last Updated: 2025-12-03

## Story Statement

- As a developer debugging the ETL pipeline, I want to trace function calls and generate visual callgraphs (DOT/Mermaid), so that I can understand execution flow and identify bottlenecks.
- As a developer, I want callgraph state to reset between runs with correct module paths, so that I get accurate, isolated traces for each debugging session.

## Problem / Why

We needed a simple way to run functions with callgraph tracing to visualize pipeline execution (Graphviz/Mermaid) for debugging and documentation, with correct package wiring and state reset.

## Personas & Scenarios

- **Persona: Pipeline Developer**
  - **Who they are**: A software engineer maintaining and extending the transcript ETL pipeline
  - **What they care about**: Understanding complex execution flows; identifying performance bottlenecks; documenting architectural decisions
  - **Their constraints**: Pipeline has deep call stacks across multiple modules; manual tracing is time-consuming and error-prone
  - **Their goals**: Generate accurate visual callgraphs for debugging; export diagrams for documentation; isolate traces without state pollution
  - **Their frustrations**: Standard debuggers don't provide visual execution flow; manual call tracing is tedious; state leaks between test runs corrupt traces
  - **Their context**: Debugging speaker detection algorithms and pipeline integration; needs tooling for both development and documentation

- **Scenario: Debugging Speaker Detection Flow**
  - **Who is acting?** Alex, a developer investigating a speaker assignment bug
  - **What triggered the action?** Alex needs to understand the call sequence in the speakerless detection algorithm to identify where incorrect assignments occur
  - **What steps do they take?**
    1. Alex wraps the speakerless detection function with `run_with_callgraph()`
    2. The tool traces all function calls during execution
    3. Callgraph outputs are generated: `callgraph.dot` (Graphviz) and `callgraph.mmd` (Mermaid)
    4. Alex opens the Mermaid diagram in VS Code to visualize execution flow
    5. Alex identifies the problematic call sequence and the bug location
    6. For the next debugging session, state resets cleanly with correct package paths
  - **What obstacles or decisions occur?**
    - Deep call stacks require filtering to focus on relevant modules
    - State from previous traces must not corrupt new traces
    - Module paths must reflect actual package structure (not relative paths)
    - Need both Graphviz (DOT) and Mermaid formats for different tools
  - **What outcome do they expect?**
    - Visual callgraph showing complete execution flow
    - DOT and Mermaid exports for different viewers
    - Clean state reset between debugging sessions
    - Correct package/module paths in trace output
    - Embeddable Mermaid diagrams for documentation

## Acceptance Criteria

- [x] `run_with_callgraph` available from `transcript_etl_pipeline.devtools`.
- [x] Outputs `callgraph.dot` and `callgraph.mmd` for a wrapped function.
- [x] Supports embedding Mermaid in Markdown easily.
- [x] State reset available (`reset_callgraph()`); package paths fixed.
- [x] Tests/tooling passing for callgraph module (33 tests).

## Non-Goals

- Performance optimization or advanced visualization beyond DOT/Mermaid exports.
