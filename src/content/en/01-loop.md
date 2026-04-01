## The Agent Loop

Every agent is, at its core, a loop: observe the world, decide what to do, act, then verify the result. This cycle repeats until the task is done or a limit is reached.

### The Simplest Form

The agent loop is a `while(true)` with four phases:

- **Observe** — Gather the current state (user message, tool results, context)
- **Decide** — Send everything to the LLM, get back a response
- **Act** — Execute any tool calls the LLM requested
- **Verify** — Check if the task is complete or if another turn is needed

### How claw-code Implements It

In claw-code, the loop lives in `runtime.py` inside `PortRuntime.run_turn_loop()`. It is a bounded for-loop with a default of `max_turns=3`. Each iteration calls the query engine, processes tool calls, and checks whether to continue.

This is a deliberate design choice. Claude Code uses an unbounded `while(true)` — it runs until the model says stop. claw-code caps the turns, making it safer for experimentation and testing.

### A Single Turn

The real work of one turn happens in `QueryEnginePort.submit_message()`. This function handles the full lifecycle:

- Format the prompt with the current message history
- Check the token budget before calling the LLM
- Track the messages in the transcript store
- Compact the conversation if it has grown too long
- Return a `TurnResult` with the model's response and a `stop_reason`

The stop reason tells the loop what happened: did the model finish, did we hit a budget limit, or did the model request a tool call that needs execution?

### Streaming Variant

`stream_submit_message()` is the streaming counterpart. Instead of returning a single result, it uses Python generators to yield events as they arrive:

- `message_start` — the model began responding
- `command_match` — a slash command was detected
- `tool_match` — the model wants to use a tool
- `permission_denial` — a tool was blocked by the constraint layer
- `message_delta` — a chunk of text arrived
- `message_stop` — the model finished

This event-driven design lets the UI update in real time while the loop continues processing.

### Pre-LLM Intelligence

Before the model even runs, `route_prompt()` adds a layer of intelligence. It scores tools by token overlap with the user's message, helping the system prioritize which tools to include in the prompt. This is harness logic — not model logic — improving efficiency before a single token is generated.

> **Teaching note:** The loop is the heartbeat of the agent. Everything else — tools, context, persistence — exists to serve this cycle. If you understand the loop, you understand the skeleton on which the entire harness hangs.

### The Universal Pattern

Every agent framework has this observe-act loop. LangChain calls it an AgentExecutor. AutoGPT has its action cycle. The names differ but the structure is identical. Once you recognize the pattern, you can read any agent framework and immediately find its core.
