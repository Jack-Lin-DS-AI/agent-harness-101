## Tools

Tools are how the agent acts in the world. Without tools, an LLM can only produce text. With tools, it can read files, run commands, search codebases, and modify code.

### Loading Tool Definitions

claw-code loads 184 tool definitions from `tools_snapshot.json` via `load_tool_snapshot()`. Each definition includes a name, description, and parameter schema — everything the LLM needs to know how to call the tool.

This snapshot approach is intentional. Rather than dynamically discovering tools at runtime, claw-code ships a known set. This makes the system predictable and testable.

### Tool Filtering

Not every tool should be available in every session. claw-code filters tools through several mechanisms:

- **simple_mode** — Restricts the agent to only Bash, FileRead, and FileEdit. Useful for constrained environments or when you want minimal capabilities.
- **MCP toggle** — Enables or disables Model Context Protocol tools, which connect to external services.
- **Permission-based filtering** — Tools blocked by the constraint layer are removed before the LLM ever sees them.

### The ToolPool

`ToolPool` assembles the active tool set for each session via `assemble_tool_pool()`. It takes the full snapshot, applies all filters, and produces the final list of tools that will be sent to the model.

This is a key design pattern: the tool set is not static. It is assembled fresh based on the session's configuration, trust level, and user preferences.

### The ExecutionRegistry

`ExecutionRegistry` unifies two kinds of callable things — commands and tools — into a single dispatch surface. When the agent needs to execute something, it goes through the registry.

`execute_tool()` dispatches by name and returns a result indicating whether the tool was handled or unhandled. This clean separation means adding a new tool requires only registering it, not modifying the dispatch logic.

### Commands vs Tools

These are related but distinct concepts:

- **Commands** are user-facing. They are slash commands like `/help` or `/resume` that the user types directly.
- **Tools** are LLM-facing. They are capabilities the model can invoke during its reasoning, like reading a file or running a shell command.

Both go through the same registry, but they serve different audiences.

> **Teaching note:** The tool layer is where the agent's capabilities are defined. A model without tools is a chatbot. A model with well-filtered, well-dispatched tools is an agent. The filtering step is especially important — it is where the harness decides what the agent CAN do, before the model decides what it WILL do.

### The Universal Pattern

All agent frameworks need a way to register, filter, and dispatch tools. Whether it is LangChain's Tool class, OpenAI's function calling schema, or claw-code's ToolPool, the problem is the same: give the model a menu of actions, then execute what it picks.
