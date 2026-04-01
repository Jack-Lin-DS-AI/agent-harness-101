#!/usr/bin/env python3
"""Layer 7: Full Integration — All 6 Layers Wired Together.

Demonstrates a complete task lifecycle using patterns from all 6 claw-code layers:
  1. Loop: Turn-based execution with bounded iterations
  2. Tools: Registry, filtering, and dispatch
  3. Context: Workspace scanning, system init, compaction
  4. Persistence: Session save/load/resume
  5. Verification: Cost hooks, safety hooks, parity audit
  6. Constraints: Permission engine gating tool access

Based on claw-code's PortRuntime.bootstrap_session() which ties everything together.
Source: https://github.com/instructkr/claw-code/blob/main/src/runtime.py
"""

from __future__ import annotations
import json
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from uuid import uuid4
from utils.display import console, print_header, print_step, print_result


# ============================================================
# Layer 6: Constraints — Permission engine (evaluated FIRST)
# ============================================================

@dataclass(frozen=True)
class ToolPermissionContext:
    deny_names: frozenset[str] = field(default_factory=frozenset)
    deny_prefixes: tuple[str, ...] = ()

    def blocks(self, tool_name: str) -> bool:
        lowered = tool_name.lower()
        return lowered in self.deny_names or any(lowered.startswith(p) for p in self.deny_prefixes)


@dataclass(frozen=True)
class PermissionDenial:
    tool_name: str
    reason: str


# ============================================================
# Layer 2: Tools — Registry and dispatch
# ============================================================

@dataclass(frozen=True)
class Tool:
    name: str
    description: str

TOOL_REGISTRY: dict[str, Tool] = {}

def register_tool(name: str, desc: str) -> None:
    TOOL_REGISTRY[name.lower()] = Tool(name, desc)

def get_filtered_tools(ctx: ToolPermissionContext | None = None) -> list[Tool]:
    tools = list(TOOL_REGISTRY.values())
    if ctx:
        tools = [t for t in tools if not ctx.blocks(t.name)]
    return tools

def execute_tool(name: str, input_data: dict) -> str:
    tool = TOOL_REGISTRY.get(name.lower())
    if not tool:
        return f"Error: Unknown tool '{name}'"
    return f"[{tool.name}] executed with {json.dumps(input_data)}"


# ============================================================
# Layer 5: Verification — Cost tracking and hooks
# ============================================================

@dataclass
class CostTracker:
    total_units: int = 0
    events: list[str] = field(default_factory=list)

    def record(self, label: str, units: int) -> None:
        self.total_units += units
        self.events.append(f"{label}:{units}")

def safety_check(tool_name: str, tool_input: dict) -> PermissionDenial | None:
    """Pre-execution safety hook."""
    if tool_name == "BashTool" and any(
        cmd in str(tool_input) for cmd in ["rm -rf", "dd if=", "mkfs"]
    ):
        return PermissionDenial(tool_name, "Destructive command blocked by safety hook")
    return None


# ============================================================
# Layer 3: Context — Workspace awareness
# ============================================================

@dataclass(frozen=True)
class WorkspaceContext:
    root: Path
    file_count: int
    has_git: bool

def build_context() -> WorkspaceContext:
    root = Path.cwd()
    return WorkspaceContext(
        root=root,
        file_count=sum(1 for _ in root.rglob("*.py")),
        has_git=(root / ".git").exists(),
    )


# ============================================================
# Layer 4: Persistence — Session store
# ============================================================

@dataclass(frozen=True)
class StoredSession:
    session_id: str
    messages: tuple[str, ...]
    input_tokens: int
    output_tokens: int

def save_session(session: StoredSession, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{session.session_id}.json"
    path.write_text(json.dumps(asdict(session), indent=2))
    return path

@dataclass
class HistoryLog:
    events: list[tuple[str, str]] = field(default_factory=list)
    def add(self, title: str, detail: str) -> None:
        self.events.append((title, detail))


# ============================================================
# Layer 1: Loop — The agent turn loop (ties everything together)
# ============================================================

@dataclass
class TurnResult:
    turn: int
    output: str
    stop_reason: str
    denials: list[PermissionDenial] = field(default_factory=list)

def run_full_harness(prompt: str, max_turns: int = 5) -> list[TurnResult]:
    """The full agent harness — all 6 layers in action.
    Mirrors claw-code's PortRuntime.bootstrap_session()."""

    print_header("Full Agent Harness", layer="loop")

    # --- Layer 6: Set up constraints ---
    print_step(1, "[Constraints] Creating permission context")
    permissions = ToolPermissionContext(
        deny_names=frozenset({"dangeroustool"}),
        deny_prefixes=("mcp__experimental_",),
    )

    # --- Layer 2: Register and filter tools ---
    print_step(2, "[Tools] Registering and filtering tools")
    register_tool("BashTool", "Execute shell commands")
    register_tool("FileReadTool", "Read file contents")
    register_tool("FileEditTool", "Edit files")
    register_tool("GrepTool", "Search file contents")
    register_tool("DangerousTool", "A blocked tool")
    register_tool("mcp__experimental_beta", "An experimental MCP tool")
    available = get_filtered_tools(permissions)
    print_result("Available tools", f"{len(available)}/{len(TOOL_REGISTRY)}")

    # --- Layer 3: Build context ---
    print_step(3, "[Context] Building workspace context")
    ctx = build_context()
    print_result("Workspace", f"{ctx.root} ({ctx.file_count} .py files)")

    # --- Layer 5: Initialize verification ---
    print_step(4, "[Verification] Initializing cost tracker")
    cost = CostTracker()

    # --- Layer 4: Initialize persistence ---
    session_id = uuid4().hex[:12]
    history = HistoryLog()
    messages: list[str] = []
    total_tokens = 0
    history.add("bootstrap", f"session={session_id} tools={len(available)} files={ctx.file_count}")

    # --- Layer 1: The turn loop ---
    print_step(5, "[Loop] Starting turn loop")
    results: list[TurnResult] = []

    # Simulate a task that uses tools across multiple turns
    task_plan = [
        ("FileReadTool", {"path": "main.py"}),
        ("GrepTool", {"pattern": "def process", "path": "."}),
        ("BashTool", {"command": "rm -rf /"}),  # Should be blocked by safety hook!
        ("FileEditTool", {"path": "main.py", "diff": "fix bug"}),
        None,  # No tool use = end_turn
    ]

    for turn in range(min(max_turns, len(task_plan))):
        console.print(f"\n  --- Turn {turn + 1} ---")
        action = task_plan[turn]
        denials: list[PermissionDenial] = []

        if action is None:
            results.append(TurnResult(turn + 1, "Task complete", "end_turn"))
            print_result("Stop", "end_turn", style="yellow")
            break

        tool_name, tool_input = action

        # Layer 6: Permission check
        if permissions.blocks(tool_name):
            denial = PermissionDenial(tool_name, "Blocked by permission context")
            denials.append(denial)
            print_result("Denied", f"{tool_name}: {denial.reason}", style="red")
            results.append(TurnResult(turn + 1, denial.reason, "permission_denied", denials))
            continue

        # Layer 5: Safety hook
        safety = safety_check(tool_name, tool_input)
        if safety:
            denials.append(safety)
            print_result("Blocked", f"{tool_name}: {safety.reason}", style="red")
            results.append(TurnResult(turn + 1, safety.reason, "hook_denied", denials))
            history.add("hook_denial", f"{tool_name}: {safety.reason}")
            continue

        # Layer 2: Execute tool
        output = execute_tool(tool_name, tool_input)
        print_result("Executed", output)

        # Layer 5: Record cost
        cost.record(tool_name, 10)
        total_tokens += 50
        messages.append(f"turn_{turn+1}: {output}")

        history.add("execution", f"{tool_name} -> {len(output)} chars")
        results.append(TurnResult(turn + 1, output, "completed"))

    # --- Layer 4: Persist session ---
    console.print()
    print_step(6, "[Persistence] Saving session")
    with tempfile.TemporaryDirectory() as tmpdir:
        stored = StoredSession(
            session_id=session_id, messages=tuple(messages),
            input_tokens=total_tokens, output_tokens=total_tokens // 2,
        )
        path = save_session(stored, Path(tmpdir))
        print_result("Saved", str(path))

    # --- Summary ---
    console.print()
    print_header("Session Summary", layer="loop")
    print_result("Turns", str(len(results)))
    print_result("Total cost", f"{cost.total_units} units")
    print_result("Denials", str(sum(len(r.denials) for r in results)))
    print_result("History", str(len(history.events)) + " events")

    for title, detail in history.events:
        print_result(f"  {title}", detail, style="dim")

    return results


if __name__ == "__main__":
    print_header("Layer 7: Full Integration", layer="loop")
    console.print("\n[dim]All 6 layers wired together — based on claw-code's PortRuntime[/dim]\n")
    run_full_harness("Fix the critical bug in main.py")
