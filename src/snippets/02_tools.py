# From claw-code: src/tools.py, lines ~14-86 + src/tool_pool.py + src/execution_registry.py
# Layer 2: Tool System — How the harness lets the agent act
# https://github.com/instructkr/claw-code

# --- Part A: Tool Definition (Tool.py) ---

@dataclass(frozen=True)
class ToolDefinition:
    name: str                                          # ← A tool is just a name + purpose
    purpose: str                                       # ← Compare: Claude Code has 29K lines of tool defs

# --- Part B: Tool Registry — Loading from Snapshot (tools.py) ---

SNAPSHOT_PATH = Path(__file__).parent / 'reference_data' / 'tools_snapshot.json'

@lru_cache(maxsize=1)                                  # ← Cache: load once, use forever
def load_tool_snapshot() -> tuple[PortingModule, ...]:
    raw_entries = json.loads(SNAPSHOT_PATH.read_text()) # ← 184 tool definitions from JSON
    return tuple(
        PortingModule(name=entry['name'], responsibility=entry['responsibility'],
                      source_hint=entry['source_hint'], status='mirrored')
        for entry in raw_entries
    )

PORTED_TOOLS = load_tool_snapshot()                    # ← Module-level constant: tools available at import

# --- Part C: Tool Filtering — Permission-Aware Selection (tools.py) ---

def get_tools(simple_mode=False, include_mcp=True, permission_context=None):
    tools = list(PORTED_TOOLS)
    if simple_mode:                                    # ← Simple mode: only Bash, FileRead, FileEdit
        tools = [m for m in tools if m.name in {'BashTool', 'FileReadTool', 'FileEditTool'}]
    if not include_mcp:                                # ← MCP toggle: exclude MCP tools
        tools = [m for m in tools if 'mcp' not in m.name.lower()]
    return filter_tools_by_permission_context(tuple(tools), permission_context)  # ← Permission gate

# --- Part D: Tool Pool Assembly (tool_pool.py) ---

@dataclass(frozen=True)
class ToolPool:
    tools: tuple[PortingModule, ...]                   # ← The active tool set for this session
    simple_mode: bool
    include_mcp: bool

def assemble_tool_pool(simple_mode=False, include_mcp=True, permission_context=None):
    return ToolPool(                                   # ← Single function assembles the filtered pool
        tools=get_tools(simple_mode=simple_mode, include_mcp=include_mcp,
                        permission_context=permission_context),
        simple_mode=simple_mode, include_mcp=include_mcp,
    )

# --- Part E: Execution Dispatch (execution_registry.py) ---

@dataclass(frozen=True)
class ExecutionRegistry:
    commands: tuple[MirroredCommand, ...]              # ← Unified registry: commands AND tools
    tools: tuple[MirroredTool, ...]

    def tool(self, name):                              # ← Look up tool by name (case-insensitive)
        lowered = name.lower()
        for tool in self.tools:
            if tool.name.lower() == lowered:
                return tool
        return None

def execute_tool(name, payload=''):
    module = get_tool(name)
    if module is None:
        return ToolExecution(name=name, handled=False, # ← Unknown tool: explicit failure
                             message=f'Unknown mirrored tool: {name}')
    return ToolExecution(name=module.name, handled=True,  # ← Known tool: dispatch and handle
                         message=f"Tool '{module.name}' handles payload {payload!r}.")
