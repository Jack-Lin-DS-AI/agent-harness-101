## Conclusion

### The Six Layers

We have walked through the complete anatomy of an agent harness:

- **Loop** — The observe-decide-act-verify cycle that drives every turn
- **Tools** — Registration, filtering, and dispatch of the agent's capabilities
- **Context** — Working memory management: system prompts, prefetching, compaction
- **Persistence** — Saving and restoring state across sessions
- **Verification** — Cost tracking, hooks, and self-auditing for observability and safety
- **Constraints** — Permission enforcement and sandboxing as the foundation of trust

Each layer is simple in isolation. A cost tracker is 13 lines. A permission engine is 20 lines. A turn loop is a bounded for-loop. The power comes from their composition.

### The Full Integration

In claw-code, `bootstrap_session()` ties all six layers together. It:

- Scans the workspace and builds context (Context layer)
- Loads and filters the tool set (Tools layer)
- Applies permission constraints (Constraints layer)
- Sets up cost tracking and hooks (Verification layer)
- Restores a previous session if resuming (Persistence layer)
- Enters the turn loop (Loop layer)

This single function is the spine of the agent. Every layer plugs in, and the result is greater than the sum of its parts.

### The Harness is Not Boilerplate

The most important takeaway from this guide: the harness is not incidental code that wraps the "real" intelligence of the model. It is core engineering.

The model does not know how to manage its own context window. The model does not enforce its own permissions. The model does not track its own costs or audit its own behavior. The harness does all of this, and without it, the model is a brilliant but unreliable conversation partner.

> **Key insight:** When people say that ~40% of Claude Code's capability comes from the harness, they mean that prompt engineering, tool filtering, context management, persistence, safety hooks, and permission enforcement are not overhead. They are product.

### Going Further

This guide used claw-code's Python layer for clarity. The Rust layer offers production-grade patterns for the same concepts:

- `hooks.rs` (357 lines) — Full hook lifecycle with pre/post/stop phases
- `sandbox.rs` (364 lines) — OS-level isolation with namespaces and filesystem control
- The Rust modules show how these patterns scale to production requirements

Read the Python to understand the concepts. Read the Rust to see how they harden for deployment.

### The 40% That Makes the Difference

An LLM without a harness is a demo. An LLM with a well-engineered harness is a product. The six layers we covered are not unique to Claude Code or claw-code — they appear in every serious agent system. Now that you can see them, you will recognize them everywhere.

The agent harness is the 40% that makes the difference.
