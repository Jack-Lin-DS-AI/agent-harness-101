# Code Snippets — Extraction Methodology

These annotated Python snippets are extracted from [instructkr/claw-code](https://github.com/instructkr/claw-code), a clean-room Python/Rust reimplementation of Claude Code's architecture.

## Extraction Rules

1. **50-80 lines max** per snippet — trimmed for teaching clarity
2. **`# ←` inline annotations** highlight key harness patterns
3. **Source citation** in header comments (file + approximate line numbers)
4. **Multiple files combined** where a concept spans several small modules
5. **Teaching implementations** clearly labeled when claw-code doesn't implement a layer

## Snippet Map

| File | Layer | Primary claw-code Sources |
|------|-------|--------------------------|
| `01_loop.py` | Loop | `runtime.py`, `query_engine.py` |
| `02_tools.py` | Tools | `tools.py`, `tool_pool.py`, `execution_registry.py` |
| `03_context.py` | Context | `context.py`, `system_init.py`, `prefetch.py`, `setup.py` |
| `04_persistence.py` | Persistence | `session_store.py`, `transcript.py`, `history.py`, `query_engine.py` |
| `05_verification.py` | Verification | `costHook.py`, `cost_tracker.py`, `parity_audit.py` + teaching impl |
| `06_constraints.py` | Constraints | `permissions.py`, `tools.py`, `models.py` + teaching impl |

## Teaching Implementations

Parts marked `[Teaching Implementation]` are NOT from claw-code. They are minimal implementations (~20-30 lines) derived from claw-code's Rust layer patterns to fill gaps where the Python layer has only placeholders:

- **Hook lifecycle** (05_verification.py Part D): Based on `rust/crates/runtime/src/hooks.rs` (357 lines)
- **Sandbox patterns** (06_constraints.py Part E): Based on `rust/crates/runtime/src/sandbox.rs` (364 lines)
