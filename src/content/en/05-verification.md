## Verification

Verification ensures the agent does not go off the rails. It covers cost tracking, behavioral hooks, and self-auditing — the mechanisms that make an agent observable and safe.

### Cost Tracking

`CostTracker` is just 13 lines of code. It accumulates `total_units` and maintains an event log. Every time the agent spends tokens, the tracker records it.

`apply_cost_hook()` is even simpler at 8 lines. It is the canonical hook pattern: intercept an event, record it, then pass it through unchanged. The hook does not modify behavior. It observes it.

> **Teaching note:** Hooks WRAP behavior without changing it. This is a critical design principle. A cost hook that altered the token count would be a bug. A cost hook that records the token count is observability. The distinction matters.

### The Hook Lifecycle

The Python `hooks/` directory in claw-code is a placeholder — it sketches the pattern but does not implement the full lifecycle. For that, look at the Rust `hooks.rs` (357 lines), which shows the complete picture:

- **PreToolUse** — Runs before a tool executes. Can veto the execution entirely.
- **PostToolUse** — Runs after a tool executes. Used for auditing and logging.
- **Stop** — Runs when the session ends. Used for cleanup and final reporting.

### Hook Exit Codes

The Rust implementation uses a simple protocol for hook results:

- **0** — Allow. The operation proceeds normally.
- **2** — Deny. The operation is blocked.
- **Other** — Warn. The operation proceeds but a warning is logged.

This three-state model (allow, deny, warn) is expressive enough to handle most safety and policy requirements without introducing complexity.

### Self-Auditing

`run_parity_audit()` (138 lines) is one of the most interesting functions in claw-code. The harness audits itself against the original Claude Code codebase, tracking:

- Coverage of root files
- Coverage of directories
- Coverage of commands
- Coverage of tools

This is the harness checking its own completeness. It answers the question: "How much of the original system have we reimplemented?" This kind of self-awareness is rare in software but invaluable for a project that aims to faithfully reproduce another system's behavior.

### The Universal Pattern

Production agents need observability and safety gates. You need to know what the agent is doing (cost tracking, event logs), you need to be able to intervene (pre-execution hooks that can veto), and you need to audit after the fact (post-execution hooks, history logs). The specific mechanisms vary, but every serious agent deployment has some version of these three capabilities.
