# src/transcript_etl_pipeline/devtools/debug_callgraph.py

from __future__ import annotations

import os
import sys
from collections import defaultdict
from collections.abc import Callable, Iterable
from types import FrameType
from typing import Optional, TypeVar

T = TypeVar("T")

Node = str
Edge = tuple[Node, Node]

EDGES: set[Edge] = set()
NODES: set[Node] = set()

TraceFunc = Callable[[FrameType, str, object], Optional["TraceFunc"]]


# ... keep your existing imports, Node, Edge, EDGES, NODES, etc.


def _build_adjacency() -> defaultdict[Node, list[Node]]:
    """
    Build a caller -> [callees...] adjacency list from EDGES.
    """
    adj: defaultdict[Node, list[Node]] = defaultdict(list)
    for caller, callee in _iter_sorted_edges():
        if callee not in adj[caller]:
            adj[caller].append(callee)
    return adj


def _find_roots(adj: dict[Node, list[Node]]) -> list[Node]:
    """
    Find nodes that never appear as callees (likely entry points).
    """
    all_callers = set(adj.keys())
    all_callees = {callee for _, callee in EDGES}
    roots = sorted(all_callers - all_callees)
    # Fallback: if everything is a callee somehow, just pick sorted callers.
    return roots or sorted(all_callers)


def write_outline(path: str = "artifacts/callgraph_outline.txt") -> None:
    """
    Write a text outline of the call graph:

        RootFunc
          ChildFunc
            GrandChildFunc
          SiblingFunc

    The node labels are the same as used in Mermaid/DOT.
    """
    adj = _build_adjacency()
    roots = _find_roots(adj)

    visited: set[Node] = set()

    def _dfs(node: Node, depth: int) -> None:
        indent = "  " * depth
        # node is something like "yourpackage.module:file.py:10:func"
        print_label = node
        # Optionally shorten label here if you want
        # e.g., print_label = node.split(":")[-1]

        lines.append(f"{indent}{print_label}")
        visited.add(node)

        for child in adj.get(node, []):
            if child not in visited:
                _dfs(child, depth + 1)

    lines: list[str] = []
    for root in roots:
        _dfs(root, depth=0)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")


def reset_callgraph() -> None:
    """
    Reset the global call graph state.

    This should be called before starting a new trace to avoid
    pollution from previous runs.
    """
    EDGES.clear()
    NODES.clear()


def _is_project_module(module_name: str) -> bool:
    """
    Restrict the graph to transcript_etl_pipeline package.

    Returns True if the module name starts with 'transcript_etl_pipeline.',
    False otherwise.
    """
    return module_name.startswith("transcript_etl_pipeline.")


def _label(frame: FrameType) -> Node | None:
    code = frame.f_code
    module_name = frame.f_globals.get("__name__", "")

    if not isinstance(module_name, str):
        return None

    if not _is_project_module(module_name):
        return None

    filename = os.path.basename(code.co_filename)
    first_line = code.co_firstlineno
    func_name = code.co_name

    # This is the *human* label we’ll show in the Mermaid box.
    return f"{module_name}:{filename}:{first_line}:{func_name}"


def tracer(frame: FrameType, event: str, arg: object) -> TraceFunc | None:
    if event != "call":
        return tracer

    callee = _label(frame)
    if callee is None:
        return tracer

    caller_frame = frame.f_back
    caller = _label(caller_frame) if caller_frame is not None else None

    if caller is not None:
        EDGES.add((caller, callee))
        NODES.add(caller)

    NODES.add(callee)
    return tracer


def _iter_sorted_nodes() -> Iterable[Node]:
    return sorted(NODES)


def _iter_sorted_edges() -> Iterable[Edge]:
    return sorted(EDGES)


def write_dot(path: str = "artifacts/callgraph.dot") -> None:
    """
    Optional: keep Graphviz DOT output around if you still want it.
    """
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("digraph G {\n")
        f.write("  graph [rankdir=LR];\n")
        for node in _iter_sorted_nodes():
            f.write(f'  "{node}";\n')
        for src, dst in _iter_sorted_edges():
            f.write(f'  "{src}" -> "{dst}";\n')
        f.write("}\n")


def _build_node_id_map() -> dict[Node, str]:
    """
    Mermaid needs *IDs* that are simple (no spaces/colons), and
    *labels* that can be arbitrary.

    We’ll map each node string to an ID like n1, n2, ...
    """
    mapping: dict[Node, str] = {}
    for idx, node in enumerate(_iter_sorted_nodes(), start=1):
        mapping[node] = f"n{idx}"
    return mapping


def write_mermaid(path: str = "artifacts/callgraph.mmd") -> None:
    """
    Write the recorded call graph as a Mermaid flowchart definition.

    Example output usage (Markdown):

        ```mermaid
        <contents of callgraph.mmd>
        ```
    """
    node_ids = _build_node_id_map()

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("flowchart LR\n")

        # Declare nodes with labels.
        for node, node_id in node_ids.items():
            # Escape quotes inside labels
            label = node.replace('"', r"\"")
            f.write(f'    {node_id}["{label}"]\n')

        # Declare edges.
        for src, dst in _iter_sorted_edges():
            src_id = node_ids[src]
            dst_id = node_ids[dst]
            f.write(f"    {src_id} --> {dst_id}\n")


def run_with_callgraph(func: Callable[..., T], *args: object, **kwargs: object) -> T:
    """
    Run `func(*args, **kwargs)` under a tracing hook that records a call graph,
    then emit it as both Graphviz DOT and Mermaid.

    Resets the call graph state before tracing to ensure clean output.

    Example:

        from transcript_etl_pipeline.devtools.debug_callgraph import run_with_callgraph

        def main() -> int:
            ...

        if __name__ == "__main__":
            raise SystemExit(run_with_callgraph(main))
    """
    # Reset state before tracing to avoid pollution from previous runs
    reset_callgraph()

    # Save the current trace function (e.g., coverage.py's tracer) to restore it later
    old_trace = sys.gettrace()
    sys.settrace(tracer)
    try:
        result = func(*args, **kwargs)
    finally:
        # Restore the previous trace function instead of setting to None
        sys.settrace(old_trace)
        write_dot("artifacts/callgraph.dot")  # optional, keep if you like
        write_mermaid("artifacts/callgraph.mmd")  # Mermaid output
        write_outline("artifacts/callgraph_outline.txt")
    return result
