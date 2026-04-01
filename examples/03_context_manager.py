#!/usr/bin/env python3
"""Layer 3: Context Manager — Managing the Agent's Working Memory.

Based on claw-code's PortContext, system init, prefetch, and compaction patterns.
Maps to Claude Code's 4-tier compaction at 167K tokens and static/dynamic prompt split.

Source: https://github.com/instructkr/claw-code/blob/main/src/context.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from utils.display import console, print_header, print_step, print_result


# --- Workspace Context (from claw-code: src/context.py) ---

@dataclass(frozen=True)
class WorkspaceContext:
    """What the agent 'sees' about its environment. Built at startup."""
    source_root: Path
    python_file_count: int
    test_file_count: int
    has_git: bool

    def render(self) -> str:
        return (f"Source: {self.source_root} ({self.python_file_count} .py files, "
                f"{self.test_file_count} tests, git={'yes' if self.has_git else 'no'})")


def build_workspace_context(root: Path | None = None) -> WorkspaceContext:
    """Build context by scanning the workspace. From claw-code: context.py build_port_context()."""
    root = root or Path.cwd()
    return WorkspaceContext(
        source_root=root,
        python_file_count=sum(1 for _ in root.rglob("*.py")),
        test_file_count=sum(1 for _ in (root / "tests").rglob("*.py")) if (root / "tests").exists() else 0,
        has_git=(root / ".git").exists(),
    )


# --- System Init Message (from claw-code: src/system_init.py) ---

def build_system_init_message(context: WorkspaceContext, tool_count: int, trusted: bool = True) -> str:
    """Assemble the system prompt. From claw-code: system_init.py."""
    return "\n".join([
        "# System Init",
        f"Trusted mode: {trusted}",
        f"Workspace: {context.source_root}",
        f"Python files: {context.python_file_count}",
        f"Available tools: {tool_count}",
        "",
        "Startup steps:",
        "- Prefetch workspace data",
        "- Build workspace context",
        "- Load tool registry",
        "- Apply trust-gated init",
    ])


# --- Prefetch (from claw-code: src/prefetch.py) ---

@dataclass(frozen=True)
class PrefetchResult:
    name: str
    detail: str

def run_prefetch(root: Path) -> list[PrefetchResult]:
    """Proactive context loading. From claw-code: prefetch.py."""
    return [
        PrefetchResult("project_scan", f"Scanned {root}"),
        PrefetchResult("git_status", "Checked working tree status"),
        PrefetchResult("instruction_files", "Loaded CLAUDE.md + .claude/settings.json"),
    ]


# --- Message Compaction (from claw-code: src/query_engine.py) ---

@dataclass
class ConversationManager:
    """Manages conversation messages with compaction.
    From claw-code: QueryEnginePort message handling."""
    messages: list[dict] = field(default_factory=list)
    compact_after: int = 12
    max_budget_tokens: int = 4096
    total_tokens: int = 0

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.total_tokens += len(content.split()) * 4  # rough estimate
        self._compact_if_needed()

    def _compact_if_needed(self) -> None:
        """From claw-code: query_engine.py compact_messages_if_needed().
        Keep only the most recent N messages."""
        if len(self.messages) > self.compact_after:
            removed = len(self.messages) - self.compact_after
            self.messages[:] = self.messages[-self.compact_after:]
            print_result("Compacted", f"Removed {removed} old messages, kept {self.compact_after}")

    def budget_remaining(self) -> int:
        return max(0, self.max_budget_tokens - self.total_tokens)

    def should_stop(self) -> bool:
        return self.total_tokens >= self.max_budget_tokens


if __name__ == "__main__":
    print_header("Layer 3: Context Manager", layer="context")
    console.print("\n[dim]Based on claw-code's context, prefetch, and compaction patterns[/dim]\n")

    # Step 1: Build workspace context
    print_step(1, "Building workspace context")
    ctx = build_workspace_context()
    print_result("Context", ctx.render())

    # Step 2: Run prefetch
    print_step(2, "Running proactive prefetch")
    for pf in run_prefetch(Path.cwd()):
        print_result(f"  {pf.name}", pf.detail)

    # Step 3: Build system init
    print_step(3, "Building system init message")
    init_msg = build_system_init_message(ctx, tool_count=7, trusted=True)
    console.print(f"\n[dim]{init_msg}[/dim]\n")

    # Step 4: Demonstrate compaction
    print_step(4, "Demonstrating message compaction (compact_after=5)")
    mgr = ConversationManager(compact_after=5, max_budget_tokens=200)
    for i in range(8):
        mgr.add_message("user", f"Message {i+1}: {'x ' * 10}")
        print_result(f"  Msg {i+1}", f"{len(mgr.messages)} messages, {mgr.total_tokens} tokens, budget_left={mgr.budget_remaining()}")

    # Step 5: Budget check
    print_step(5, "Budget status")
    print_result("Should stop", str(mgr.should_stop()), style="yellow" if mgr.should_stop() else "green")
