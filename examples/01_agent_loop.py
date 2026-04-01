#!/usr/bin/env python3
"""Layer 1: The Agent Loop — Observe, Decide, Act, Verify, Update.

Based on claw-code's PortRuntime.run_turn_loop() and QueryEnginePort.submit_message().
Maps to Claude Code's queryLoop() — a single while(true) that drives everything.

Source: https://github.com/instructkr/claw-code/blob/main/src/runtime.py
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from utils.display import console, print_header, print_step, print_result


# --- Core data structures (from claw-code: src/query_engine.py) ---

@dataclass
class TurnResult:
    """Result of a single agent turn."""
    prompt: str
    output: str
    stop_reason: str  # 'completed' | 'max_turns_reached' | 'max_budget_reached' | 'end_turn'
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class AgentConfig:
    """Configuration for the agent loop (from claw-code: QueryEngineConfig)."""
    max_turns: int = 8
    max_budget_tokens: int = 4096
    compact_after_turns: int = 12


# --- The Agent Loop (from claw-code: runtime.py + query_engine.py) ---

def run_agent_loop(prompt: str, config: AgentConfig | None = None) -> list[TurnResult]:
    """The core agent loop — iterates until done or budget exhausted.

    This mirrors claw-code's PortRuntime.run_turn_loop():
    - Bounded by max_turns (claw-code default: 3, Claude Code: while(true))
    - Each turn checks budget before proceeding
    - Stops early on end_turn, error, or budget
    """
    config = config or AgentConfig()
    results: list[TurnResult] = []
    total_tokens = 0
    messages: list[dict] = []

    print_header("Agent Loop", layer="loop")
    console.print(f"\n  Prompt: [bold]{prompt}[/bold]")
    console.print(f"  Config: max_turns={config.max_turns}, budget={config.max_budget_tokens} tokens\n")

    for turn in range(config.max_turns):
        print_step(turn + 1, f"Turn {turn + 1}/{config.max_turns}")

        # --- Budget check (from claw-code: query_engine.py submit_message) ---
        if total_tokens > config.max_budget_tokens:
            print_result("Stop", "max_budget_reached", style="yellow")
            results.append(TurnResult(
                prompt=prompt, output="Budget exhausted",
                stop_reason="max_budget_reached",
            ))
            break

        # --- Submit to model ---
        messages.append({"role": "user", "content": prompt if turn == 0 else f"{prompt} [turn {turn + 1}]"})

        # Simulate model response (replace with anthropic.Anthropic().messages.create() for real usage)
        response_text = f"[Simulated response for turn {turn + 1}]"
        has_tool_use = turn < 2  # Simulate: first 2 turns use tools, then stop

        input_toks = len(prompt.split()) * 4
        output_toks = len(response_text.split()) * 4
        total_tokens += input_toks + output_toks
        print_result("Tokens", f"+{input_toks}in +{output_toks}out (total: {total_tokens})")

        # --- Determine stop reason (from claw-code: query_engine.py) ---
        if has_tool_use:
            stop_reason = "completed"
            print_result("Action", "Tool use detected, continuing loop")
        else:
            stop_reason = "end_turn"
            print_result("Stop", "end_turn — model finished", style="yellow")

        results.append(TurnResult(
            prompt=prompt, output=response_text,
            stop_reason=stop_reason,
            input_tokens=input_toks, output_tokens=output_toks,
        ))

        if stop_reason != "completed":
            break

    console.print(f"\n  Loop completed: {len(results)} turns, {total_tokens} total tokens")
    return results


# --- Streaming variant (from claw-code: query_engine.py stream_submit_message) ---

def stream_events(prompt: str):
    """Generator that yields streaming events, mirroring claw-code's pattern."""
    yield {"type": "message_start", "prompt": prompt}
    yield {"type": "tool_match", "tools": ["BashTool", "FileReadTool"]}
    yield {"type": "message_delta", "text": "Reading file contents..."}
    yield {"type": "message_stop", "stop_reason": "end_turn"}


if __name__ == "__main__":
    print_header("Layer 1: The Agent Loop", layer="loop")
    console.print("\n[dim]Based on claw-code's PortRuntime.run_turn_loop()[/dim]\n")

    # Demo 1: Basic agent loop
    results = run_agent_loop("Fix the bug in main.py")

    # Demo 2: Streaming events
    console.print("\n")
    print_header("Streaming Events", layer="loop")
    for event in stream_events("Fix the bug in main.py"):
        print_result(event["type"], str(event))
