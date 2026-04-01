#!/usr/bin/env python3
"""Layer 5: Verification — Trust but Verify.

Based on claw-code's CostTracker, costHook, and parity_audit patterns.
Hook lifecycle based on Rust hooks.rs (357 lines) since Python hooks/ is a placeholder.
Maps to Claude Code's PreToolUse/PostToolUse/Stop hook system.

Source: https://github.com/instructkr/claw-code/blob/main/src/costHook.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from utils.display import console, print_header, print_step, print_result


# --- Cost Tracker (from claw-code: src/cost_tracker.py, full module) ---

@dataclass
class CostTracker:
    """Accumulative cost tracking. Every tool execution is metered."""
    total_units: int = 0
    events: list[str] = field(default_factory=list)

    def record(self, label: str, units: int) -> None:
        self.total_units += units
        self.events.append(f"{label}:{units}")


# --- Cost Hook (from claw-code: src/costHook.py, full module) ---

def apply_cost_hook(tracker: CostTracker, label: str, units: int) -> CostTracker:
    """The simplest hook: intercept an action, record cost, pass through.
    Hooks WRAP behavior without changing it."""
    tracker.record(label, units)
    return tracker


# --- Hook Lifecycle [Teaching Implementation — based on Rust hooks.rs patterns] ---

@dataclass
class HookEvent:
    kind: str       # 'PreToolUse' | 'PostToolUse' | 'Stop'
    tool_name: str
    tool_input: dict = field(default_factory=dict)

@dataclass
class HookResult:
    allowed: bool
    message: str

# Hook registry: maps event kinds to lists of hook functions
HookRegistry = dict[str, list]


def create_hook_registry() -> HookRegistry:
    """Create a fresh hook registry with empty lists for each event kind."""
    return {"PreToolUse": [], "PostToolUse": [], "Stop": []}


def register_hook(registry: HookRegistry, kind: str, hook_fn) -> None:
    """Register a hook function for an event kind."""
    registry.setdefault(kind, []).append(hook_fn)


def run_hooks(registry: HookRegistry, event: HookEvent) -> HookResult:
    """Execute all hooks for an event. Any hook can veto (deny) the action.
    Exit codes: 0 = allow, 2 = deny. Mirrors Rust hooks.rs."""
    for hook_fn in registry.get(event.kind, []):
        result = hook_fn(event)
        if not result.allowed:
            return result  # First denial wins
    return HookResult(allowed=True, message="All hooks passed")


def execute_with_hooks(tool_name: str, tool_input: dict,
                       registry: HookRegistry, executor) -> dict:
    """Full hook lifecycle wrapping tool execution."""
    # Phase 1: PreToolUse — can veto
    pre = run_hooks(registry, HookEvent("PreToolUse", tool_name, tool_input))
    if not pre.allowed:
        return {"denied": True, "reason": pre.message}

    # Phase 2: Execute
    result = executor(tool_name, tool_input)

    # Phase 3: PostToolUse — audit only
    run_hooks(registry, HookEvent("PostToolUse", tool_name, tool_input))
    return {"denied": False, "result": result}


# --- Parity Audit Pattern (from claw-code: src/parity_audit.py) ---

def run_parity_check(implemented: set[str], expected: set[str]) -> dict:
    """Self-assessment: how complete is our implementation?
    From claw-code: parity_audit.py run_parity_audit()."""
    covered = implemented & expected
    missing = expected - implemented
    return {
        "coverage": f"{len(covered)}/{len(expected)}",
        "percentage": f"{len(covered)/len(expected)*100:.0f}%" if expected else "N/A",
        "missing": sorted(missing),
    }


if __name__ == "__main__":
    print_header("Layer 5: Verification", layer="verification")
    console.print("\n[dim]Based on claw-code's cost tracking + Rust hook patterns[/dim]\n")

    # Demo 1: Cost tracking
    print_step(1, "Cost tracking with hooks")
    tracker = CostTracker()
    apply_cost_hook(tracker, "FileReadTool", 10)
    apply_cost_hook(tracker, "BashTool", 25)
    apply_cost_hook(tracker, "FileEditTool", 15)
    print_result("Total cost", f"{tracker.total_units} units")
    print_result("Events", str(tracker.events))

    # Demo 2: Hook lifecycle
    print_step(2, "Hook lifecycle (PreToolUse / PostToolUse)")
    registry = create_hook_registry()

    # Register a safety hook that blocks dangerous commands
    def safety_hook(event: HookEvent) -> HookResult:
        if event.tool_name == "BashTool" and "rm -rf" in str(event.tool_input):
            return HookResult(False, "Blocked: destructive command detected")
        return HookResult(True, "OK")

    register_hook(registry, "PreToolUse", safety_hook)

    # Safe tool: passes
    result = execute_with_hooks("FileReadTool", {"path": "/tmp/test.py"}, registry,
                                lambda name, inp: f"Read {inp['path']}")
    print_result("FileReadTool", str(result))

    # Dangerous tool: blocked
    result = execute_with_hooks("BashTool", {"command": "rm -rf /"}, registry,
                                lambda name, inp: "should not run")
    print_result("BashTool rm -rf", str(result), style="red")

    # Demo 3: Parity audit
    print_step(3, "Parity audit (self-assessment)")
    implemented = {"runtime", "query_engine", "tools", "commands", "permissions", "session_store"}
    expected = {"runtime", "query_engine", "tools", "commands", "permissions", "session_store",
                "hooks", "review", "security", "sandbox", "mcp_client"}
    audit = run_parity_check(implemented, expected)
    print_result("Coverage", audit["coverage"])
    print_result("Percentage", audit["percentage"])
    print_result("Missing", str(audit["missing"]), style="yellow")
