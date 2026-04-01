## Constraints

Constraints define what the agent CANNOT do. This is the foundation of trust. An agent without constraints is a liability. An agent with well-defined constraints is a tool you can rely on.

### The Permission Engine

`ToolPermissionContext` is just 20 lines of Python. That is the entire permission engine. It has two fields:

- `deny_names` — A set of tool names that are exactly blocked
- `deny_prefixes` — A set of prefixes; any tool whose name starts with a prefix is blocked

The `blocks()` method checks both: is the name in the deny set, or does it start with a deny prefix? If either is true, the tool is blocked.

> **Teaching note:** The brevity IS the teaching point. Twenty lines of Python encode a complete permission model. You do not need a complex RBAC system or a policy engine to build effective constraints. A deny list and a prefix matcher handle the vast majority of real-world cases.

### Filtering at the Source

`filter_tools_by_permission_context()` applies the permission check to the entire tool set. Denied tools are removed before they ever reach the LLM. The model cannot call what it cannot see.

This is a critical design decision. Rather than letting the model attempt a blocked tool and handling the error, claw-code removes the tool from the prompt entirely. The model never knows the tool exists, so it cannot try to work around the restriction.

### Denial Tracking

When a tool is denied, the system creates a `PermissionDenial` record with the tool name and the reason. These denials are included in the `TurnResult` so the LLM knows WHY a capability is unavailable.

This feedback loop matters. Without it, the model might repeatedly attempt to use a capability it cannot access. With denial tracking, the model can adapt its strategy.

### Trust Modes

Trust is binary in claw-code:

- **trusted=True** — Full capabilities are available. All tools load. Deferred initialization runs.
- **trusted=False** — Restricted mode. Some tools are filtered. Deferred init steps are skipped.

This two-tier model maps to real-world scenarios: a trusted session might be a developer on their own machine, while an untrusted session might be a CI pipeline or a shared environment.

### OS-Level Isolation

The Rust layer goes further. `sandbox.rs` (364 lines) adds operating system-level isolation:

- **Linux namespaces** — The agent runs in its own process namespace
- **Filesystem modes** — Read-only, read-write, or no access per path
- **Network control** — The agent's network access can be restricted or blocked entirely

This defense-in-depth approach means that even if the permission layer has a bug, the OS sandbox provides a second barrier.

### The Universal Pattern

Every safe agent needs a constraint layer between the model and its actions. The model proposes. The harness disposes. Whether implemented as a 20-line deny list or a full operating system sandbox, the principle is the same: define what the agent cannot do, and enforce it before the action happens.
