## Context

Context is the agent's working memory. It determines what the model knows when it makes decisions. Managing context well is the difference between an agent that understands your project and one that flails.

### Workspace Scanning

`PortContext` in `context.py` performs workspace scanning at startup. It examines the source root, counts files, checks for archive availability, and builds a picture of the environment. This happens before the first turn — the agent orients itself before it acts.

### The System Prompt

`build_system_init_message()` assembles the system prompt that frames the entire conversation. It weaves together:

- The current trust mode (what the agent is allowed to do)
- The count and names of available tools
- Startup steps and environment details
- Project-specific context gathered from scanning

This is not a static string. It is dynamically constructed based on the session configuration, making each session's system prompt unique to its context.

### The Prefetch Pattern

Waiting for the LLM to ask for information is slow. claw-code uses prefetching to load data before the model requests it:

- `start_mdm_raw_read()` — Begins loading markdown documentation in the background
- `start_project_scan()` — Starts scanning the project structure immediately

These run concurrently with other startup tasks. By the time the model needs project context, it is already available. This pattern shaves seconds off every session.

> **Teaching note:** Prefetching is a classic systems engineering technique applied to the agent domain. The harness predicts what the model will need and fetches it eagerly. This is pure harness intelligence — the model does not know or care that the data was prefetched.

### Message Compaction

As conversations grow, they eventually exceed what the context window can hold. claw-code handles this with `compact_messages_if_needed()`.

Compaction is triggered when messages exceed `compact_after_turns` (default: 12). When triggered, it keeps only the most recent N messages and discards older ones. This is a simple but effective strategy — recent context is almost always more relevant than old context.

### Budget Control

`QueryEngineConfig.max_budget_tokens` (default: 2000) sets a hard limit on token spending. When the budget is exhausted, the turn ends with a stop reason of `max_budget_reached`. This prevents runaway sessions from consuming unbounded resources.

### Claude Code's Approach

Claude Code uses a more sophisticated 4-tier compaction strategy that triggers at around 167K tokens. It progressively summarizes older messages rather than dropping them. claw-code's simpler keep-last-N approach trades fidelity for clarity — perfect for learning the concept.

### The Universal Pattern

Every long-running agent must manage its context window. The window is finite. Conversations are not. Some form of compaction, summarization, or sliding window is mandatory. The specific strategy varies, but the problem is universal.
