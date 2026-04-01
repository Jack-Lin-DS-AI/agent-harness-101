#!/usr/bin/env python3
"""Layer 6: Constraints — The Foundation of Trust.

Based on claw-code's ToolPermissionContext — the entire permission engine in 20 lines.
Maps to Claude Code's 6-layer permission engine with deny/ask/allow evaluation.

Source: https://github.com/instructkr/claw-code/blob/main/src/permissions.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
import platform
from utils.display import console, print_header, print_step, print_result


# --- Permission Engine (from claw-code: src/permissions.py, full module) ---

@dataclass(frozen=True)
class ToolPermissionContext:
    """The entire permission engine. Two mechanisms: deny_names + deny_prefixes."""
    deny_names: frozenset[str] = field(default_factory=frozenset)
    deny_prefixes: tuple[str, ...] = ()

    @classmethod
    def from_iterables(cls, deny_names: list[str] | None = None,
                       deny_prefixes: list[str] | None = None) -> 'ToolPermissionContext':
        return cls(
            deny_names=frozenset(n.lower() for n in (deny_names or [])),
            deny_prefixes=tuple(p.lower() for p in (deny_prefixes or [])),
        )

    def blocks(self, tool_name: str) -> bool:
        """The entire permission check — two simple rules."""
        lowered = tool_name.lower()
        return (lowered in self.deny_names
                or any(lowered.startswith(p) for p in self.deny_prefixes))


# --- Permission Denial Tracking (from claw-code: src/models.py + runtime.py) ---

@dataclass(frozen=True)
class PermissionDenial:
    tool_name: str
    reason: str


def check_tool_permission(ctx: ToolPermissionContext, tool_name: str) -> PermissionDenial | None:
    """Check if a tool is blocked and return denial with reason if so."""
    if not ctx.blocks(tool_name):
        return None
    lowered = tool_name.lower()
    if lowered in ctx.deny_names:
        reason = f"Tool '{tool_name}' is in the deny list"
    else:
        matching_prefix = next(p for p in ctx.deny_prefixes if lowered.startswith(p))
        reason = f"Tool '{tool_name}' matches deny prefix '{matching_prefix}'"
    return PermissionDenial(tool_name=tool_name, reason=reason)


# --- Trust Modes (from claw-code: src/setup.py) ---

def apply_trust_mode(trusted: bool) -> dict:
    """Binary trust gate. From claw-code: setup.py run_setup(trusted=...)."""
    if trusted:
        return {"mode": "trusted", "bash": True, "file_write": True, "network": True}
    return {"mode": "restricted", "bash": False, "file_write": False, "network": False}


# --- Sandbox Pattern [Teaching Implementation — based on Rust sandbox.rs] ---

@dataclass
class SandboxConfig:
    enabled: bool = True
    network_allowed: bool = False
    filesystem_mode: str = "workspace_only"  # 'off' | 'workspace_only' | 'allowlist'

@dataclass
class SandboxStatus:
    supported: bool
    active: bool
    reason: str

def resolve_sandbox(config: SandboxConfig) -> SandboxStatus:
    """Detect OS capabilities and resolve sandbox status.
    Based on claw-code Rust: sandbox.rs resolve_sandbox_status()."""
    is_linux = platform.system() == "Linux"
    if not config.enabled:
        return SandboxStatus(is_linux, False, "Disabled by configuration")
    if not is_linux:
        return SandboxStatus(False, False, f"Not supported on {platform.system()}")
    return SandboxStatus(True, True, "Linux namespace isolation active")


if __name__ == "__main__":
    print_header("Layer 6: Constraints", layer="constraints")
    console.print("\n[dim]Based on claw-code's ToolPermissionContext (20 lines!)[/dim]\n")

    # Demo 1: Permission engine
    print_step(1, "Creating permission context")
    ctx = ToolPermissionContext.from_iterables(
        deny_names=["BashTool", "NotebookEditTool"],
        deny_prefixes=["mcp__", "dangerous_"],
    )
    print_result("Deny names", str(ctx.deny_names))
    print_result("Deny prefixes", str(ctx.deny_prefixes))

    # Demo 2: Check various tools
    print_step(2, "Checking tool permissions")
    test_tools = ["FileReadTool", "BashTool", "mcp__github__create_pr",
                  "GrepTool", "dangerous_delete", "NotebookEditTool"]
    for tool in test_tools:
        denial = check_tool_permission(ctx, tool)
        if denial:
            print_result(f"  {tool}", f"DENIED — {denial.reason}", style="red")
        else:
            print_result(f"  {tool}", "ALLOWED", style="green")

    # Demo 3: Trust modes
    print_step(3, "Trust mode comparison")
    for trusted in [True, False]:
        caps = apply_trust_mode(trusted)
        print_result(f"  trusted={trusted}", str(caps))

    # Demo 4: Sandbox resolution
    print_step(4, "Sandbox status")
    sandbox = resolve_sandbox(SandboxConfig(enabled=True))
    print_result("Supported", str(sandbox.supported))
    print_result("Active", str(sandbox.active))
    print_result("Reason", sandbox.reason)
