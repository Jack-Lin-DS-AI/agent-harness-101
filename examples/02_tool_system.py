#!/usr/bin/env python3
"""Layer 2: Tool System — Letting the Agent Act.

Based on claw-code's tool registry, tool pool assembly, and execution dispatch.
Maps to Claude Code's 40 tools with 29K lines of definitions.

Source: https://github.com/instructkr/claw-code/blob/main/src/tools.py
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from functools import lru_cache
from utils.display import console, print_header, print_step, print_result


# --- Tool Definition (from claw-code: src/Tool.py) ---

@dataclass(frozen=True)
class ToolDefinition:
    """A tool is just a name + schema. Minimal unit of capability."""
    name: str
    description: str
    input_schema: dict = field(default_factory=dict)


# --- Tool Registry (from claw-code: src/tools.py) ---

# In claw-code, 184 tools are loaded from tools_snapshot.json.
# Here we define a teaching subset that mirrors the real tool names.
TOOL_REGISTRY: dict[str, ToolDefinition] = {}


def register_tool(name: str, description: str, schema: dict | None = None) -> ToolDefinition:
    """Register a tool in the global registry."""
    tool = ToolDefinition(name=name, description=description, input_schema=schema or {})
    TOOL_REGISTRY[name.lower()] = tool
    return tool


def get_tool(name: str) -> ToolDefinition | None:
    """Look up tool by name (case-insensitive). From claw-code: tools.py get_tool()."""
    return TOOL_REGISTRY.get(name.lower())


def find_tools(query: str, limit: int = 20) -> list[ToolDefinition]:
    """Search tools by keyword. From claw-code: tools.py find_tools()."""
    needle = query.lower()
    return [t for t in TOOL_REGISTRY.values()
            if needle in t.name.lower() or needle in t.description.lower()][:limit]


# --- Permission-Aware Filtering (from claw-code: src/tools.py + permissions.py) ---

@dataclass(frozen=True)
class PermissionContext:
    deny_names: frozenset[str] = field(default_factory=frozenset)
    deny_prefixes: tuple[str, ...] = ()

    def blocks(self, tool_name: str) -> bool:
        lowered = tool_name.lower()
        return lowered in self.deny_names or any(lowered.startswith(p) for p in self.deny_prefixes)


def get_tools_filtered(simple_mode: bool = False, permission_context: PermissionContext | None = None) -> list[ToolDefinition]:
    """Assemble the active tool pool. From claw-code: tool_pool.py assemble_tool_pool()."""
    tools = list(TOOL_REGISTRY.values())
    if simple_mode:
        tools = [t for t in tools if t.name in {'BashTool', 'FileReadTool', 'FileEditTool'}]
    if permission_context:
        tools = [t for t in tools if not permission_context.blocks(t.name)]
    return tools


# --- Execution Dispatch (from claw-code: src/execution_registry.py) ---

@dataclass
class ToolExecution:
    name: str
    handled: bool
    output: str


def execute_tool(name: str, tool_input: dict) -> ToolExecution:
    """Dispatch tool execution. From claw-code: tools.py execute_tool()."""
    tool = get_tool(name)
    if tool is None:
        return ToolExecution(name=name, handled=False, output=f"Unknown tool: {name}")
    # In real implementation: actually run the tool
    return ToolExecution(name=tool.name, handled=True,
                         output=f"Executed {tool.name} with input {json.dumps(tool_input)}")


if __name__ == "__main__":
    print_header("Layer 2: Tool System", layer="tools")
    console.print("\n[dim]Based on claw-code's tool registry + dispatch pattern[/dim]\n")

    # Step 1: Register tools (mirrors claw-code loading from snapshot JSON)
    print_step(1, "Registering tools (claw-code loads 184 from JSON snapshot)")
    register_tool("BashTool", "Execute shell commands", {"command": {"type": "string"}})
    register_tool("FileReadTool", "Read file contents", {"path": {"type": "string"}})
    register_tool("FileEditTool", "Edit files with diffs", {"path": {"type": "string"}, "diff": {"type": "string"}})
    register_tool("FileWriteTool", "Create new files", {"path": {"type": "string"}, "content": {"type": "string"}})
    register_tool("GlobTool", "Search for files by pattern", {"pattern": {"type": "string"}})
    register_tool("GrepTool", "Search file contents", {"pattern": {"type": "string"}})
    register_tool("mcp__github__create_pr", "Create a GitHub PR via MCP", {})
    print_result("Registered", f"{len(TOOL_REGISTRY)} tools")

    # Step 2: Search
    print_step(2, "Searching for 'file' tools")
    matches = find_tools("file")
    for t in matches:
        print_result("  Found", t.name)

    # Step 3: Filter by permissions
    print_step(3, "Filtering with permission context (deny bash, deny mcp__ prefix)")
    ctx = PermissionContext(deny_names=frozenset({"bashtool"}), deny_prefixes=("mcp__",))
    filtered = get_tools_filtered(permission_context=ctx)
    print_result("Available", f"{len(filtered)} tools (from {len(TOOL_REGISTRY)} registered)")
    for t in filtered:
        print_result("  Allowed", t.name)

    # Step 4: Execute
    print_step(4, "Executing FileReadTool")
    result = execute_tool("FileReadTool", {"path": "/tmp/test.py"})
    print_result("Result", result.output)

    # Step 5: Try blocked tool
    print_step(5, "Attempting blocked tool: BashTool")
    if ctx.blocks("BashTool"):
        print_result("Blocked", "BashTool denied by permission context", style="red")
