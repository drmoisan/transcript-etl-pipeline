"""
Example demonstrating debug_callgraph usage.

This shows how to use the callgraph tracing to visualize
function call flows in the transcript ETL pipeline.
"""

from transcript_etl_pipeline.devtools import run_with_callgraph


def example_function_a() -> int:
    """Example function A that calls B."""
    return example_function_b() + 10


def example_function_b() -> int:
    """Example function B that calls C."""
    return example_function_c() * 2


def example_function_c() -> int:
    """Example function C (leaf function)."""
    return 5


def main() -> int:
    """Main entry point."""
    print("Running example with callgraph tracing...")
    result = example_function_a()
    print(f"Result: {result}")
    return 0


if __name__ == "__main__":
    # This will trace all function calls and generate:
    # - callgraph.dot (Graphviz format)
    # - callgraph.mmd (Mermaid format)
    exit_code = run_with_callgraph(main)
    print("\nGenerated files:")
    print("  - callgraph.dot (Graphviz DOT format)")
    print("  - callgraph.mmd (Mermaid flowchart)")
    print("\nTo view the Mermaid diagram:")
    print("  Copy the contents of callgraph.mmd into a markdown file")
    print("  and wrap it with ```mermaid ... ```")
    raise SystemExit(exit_code)
