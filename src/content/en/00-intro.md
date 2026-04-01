## What is Agent Harness Engineering?

When you use an AI coding agent like Claude Code, you might assume the magic is all in the model. It is not. Roughly 40% of what makes Claude Code effective comes from the **harness** — the surrounding engineering that turns a language model into a reliable agent.

This is **Agent Harness Engineering**: the discipline of building the scaffolding that makes an LLM useful in the real world.

## The Formula

> **Agent = Model + Harness**

This framing comes from Mitchell Hashimoto, who observed that the non-model code in Claude Code is not boilerplate — it is core to the product's capability. The model provides intelligence. The harness provides structure, memory, safety, and reliability.

## The 6-Layer Framework

Every agent harness can be understood through six layers, each solving a distinct problem:

- **Loop** — The observe-decide-act-verify cycle that drives the agent forward
- **Tools** — How the agent acts in the world: registration, filtering, dispatch
- **Context** — The agent's working memory: system prompts, prefetching, compaction
- **Persistence** — Remembering across sessions: saving and restoring state
- **Verification** — Observability and safety: cost tracking, hooks, self-auditing
- **Constraints** — What the agent cannot do: permissions, trust modes, sandboxing

These layers compose. Each one is simple on its own. Together, they produce a capable and trustworthy agent.

## How claw-code Helps Us Learn

**claw-code** is a Python and Rust reimplementation of Claude Code's core architecture. It exists to make these patterns visible and studiable.

The original Claude Code is a production TypeScript codebase — large, optimized, and sometimes hard to read for educational purposes. claw-code reimplements the same concepts in Python (for clarity) and Rust (for production-grade patterns), giving us a smaller codebase where every design decision is legible.

Throughout this guide, we will reference specific files and functions in claw-code. When you see a function name like `run_turn_loop()` or a file like `context.py`, that is real code you can read and modify.

## What You Will Learn

By the end of this guide, you will understand:

- Why the harness matters as much as the model
- How each layer works in isolation and in combination
- The universal patterns that appear in every agent framework
- How to read and extend claw-code to experiment with your own harness designs

Let us begin with the most fundamental layer: the loop.
