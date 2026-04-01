# From claw-code: src/context.py + src/system_init.py + src/prefetch.py + src/setup.py
# Layer 3: Context — Managing the agent's working memory
# https://github.com/instructkr/claw-code

# --- Part A: Workspace Context (context.py, lines ~7-47) ---

@dataclass(frozen=True)
class PortContext:
    source_root: Path                                  # ← What the agent "sees" about its environment
    tests_root: Path
    archive_root: Path
    python_file_count: int                             # ← Dynamic: counted at startup
    test_file_count: int
    archive_available: bool                            # ← Can we compare against the original?

def build_port_context(base=None):
    root = base or Path(__file__).resolve().parent.parent
    return PortContext(
        source_root=root / 'src',
        tests_root=root / 'tests',
        archive_root=root / 'archive' / 'claw_code_ts_snapshot' / 'src',
        python_file_count=sum(1 for p in (root / 'src').rglob('*.py')),  # ← Count at build time
        test_file_count=sum(1 for p in (root / 'tests').rglob('*.py')),
        archive_available=(root / 'archive' / 'claw_code_ts_snapshot' / 'src').exists(),
    )

# --- Part B: System Init Message (system_init.py) ---

def build_system_init_message(trusted=True):           # ← Assembles the system prompt
    setup = run_setup(trusted=trusted)
    commands = get_commands()                           # ← Load all available commands
    tools = get_tools()                                # ← Load all available tools
    lines = [
        '# System Init',
        f'Trusted: {setup.trusted}',                   # ← Trust mode affects capabilities
        f'Built-in command names: {len(built_in_command_names())}',
        f'Loaded command entries: {len(commands)}',     # ← Tell the model what tools exist
        f'Loaded tool entries: {len(tools)}',
        'Startup steps:',
        *(f'- {step}' for step in setup.setup.startup_steps()),
    ]
    return '\n'.join(lines)

# --- Part C: Proactive Prefetch (prefetch.py) ---

def start_mdm_raw_read():                             # ← Load workspace data BEFORE the LLM asks
    return PrefetchResult('mdm_raw_read', True, 'Simulated MDM raw-read prefetch')

def start_project_scan(root):                          # ← Scan project structure proactively
    return PrefetchResult('project_scan', True, f'Scanned project root {root}')

# --- Part D: Message Compaction (query_engine.py, lines ~129-132) ---

def compact_messages_if_needed(self):                  # ← Triggered when messages exceed threshold
    if len(self.mutable_messages) > self.config.compact_after_turns:  # ← Default: 12 turns
        self.mutable_messages[:] = self.mutable_messages[-self.config.compact_after_turns:]
    self.transcript_store.compact(self.config.compact_after_turns)  # ← Keep only recent N messages

# --- Part E: Budget Control (query_engine.py) ---

@dataclass(frozen=True)
class QueryEngineConfig:
    max_turns: int = 8                                 # ← Hard turn limit
    max_budget_tokens: int = 2000                      # ← Hard token budget
    compact_after_turns: int = 12                      # ← Compaction trigger threshold

# The budget check in submit_message():
# if projected_usage.input + projected_usage.output > max_budget_tokens:
#     stop_reason = 'max_budget_reached'               # ← Prevents runaway costs
