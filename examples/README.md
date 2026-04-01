# Runnable Python Examples

These examples demonstrate Agent Harness Engineering patterns extracted from
[instructkr/claw-code](https://github.com/instructkr/claw-code), a clean-room
Python/Rust reimplementation of Claude Code's architecture.

## Quick Start

```bash
pip install -r requirements.txt
python 01_agent_loop.py
```

Each example is self-contained and runnable independently. The examples use simulated
model responses by default. To use real API calls, set `ANTHROPIC_API_KEY`.

## Examples

| File | Layer | What It Demonstrates | claw-code Source |
|------|-------|---------------------|-----------------|
| `01_agent_loop.py` | Loop | Turn-based execution, budget checking, streaming | `runtime.py`, `query_engine.py` |
| `02_tool_system.py` | Tools | Registry, filtering, permission-gated dispatch | `tools.py`, `tool_pool.py`, `execution_registry.py` |
| `03_context_manager.py` | Context | Workspace scanning, system init, compaction | `context.py`, `system_init.py`, `prefetch.py` |
| `04_persistence.py` | Persistence | Session save/load, transcript compaction, history | `session_store.py`, `transcript.py`, `history.py` |
| `05_verification.py` | Verification | Cost tracking, safety hooks, parity audit | `costHook.py`, `cost_tracker.py`, `parity_audit.py` |
| `06_constraints.py` | Constraints | Permission engine, trust modes, sandbox | `permissions.py`, `models.py`, `setup.py` |
| `07_full_harness.py` | Integration | All 6 layers wired together | `runtime.py` (bootstrap_session) |

## Attribution

Core logic patterns are derived from claw-code's actual implementation. All code is
used for educational purposes under fair use principles. See the project root README
for the full disclaimer.
