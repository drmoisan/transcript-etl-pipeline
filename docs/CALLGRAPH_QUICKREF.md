# Debug Callgraph - Quick Reference

## Import
```python
from transcript_etl_pipeline.devtools import run_with_callgraph
```

## Basic Usage
```python
def my_function() -> int:
    # Your code
    return 42

if __name__ == "__main__":
    result = run_with_callgraph(my_function)
```

## Output Files
- `callgraph.dot` - Graphviz format
- `callgraph.mmd` - Mermaid format

## View in Markdown
````markdown
```mermaid
<paste contents of callgraph.mmd here>
```
````

## What Was Fixed
1. ✅ Package name: `yourpackage` → `transcript_etl_pipeline`
2. ✅ State management: Added `reset_callgraph()`
3. ✅ Test coverage: 0 → 33 tests

## Test Results
- 33/33 tests passing
- Black ✅ | Ruff ✅ | Pyright ✅
- Full test suite: 347/348 passing

## Documentation
- Module docs: `src/transcript_etl_pipeline/devtools/README.md`
- Fix details: `docs/debug_callgraph_fixes.md`
- Example: `examples/callgraph_example.py`
