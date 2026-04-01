# From claw-code: src/costHook.py + src/cost_tracker.py + src/parity_audit.py, lines ~73-138
# + Teaching implementation based on Rust hooks.rs patterns
# Layer 5: Verification — Trust but verify
# https://github.com/instructkr/claw-code

# --- Part A: Cost Hook Pattern (costHook.py, full file — 8 lines) ---

def apply_cost_hook(tracker, label, units):            # ← The simplest hook: intercept, record, pass through
    tracker.record(label, units)                       # ← Side effect: accumulate cost
    return tracker                                     # ← Return tracker unchanged — hooks WRAP, don't BLOCK

# --- Part B: Cost Tracker (cost_tracker.py, full file — 13 lines) ---

@dataclass
class CostTracker:
    total_units: int = 0                               # ← Accumulative counter
    events: list[str] = field(default_factory=list)    # ← Audit log of all cost events

    def record(self, label, units):                    # ← Called by hooks on every tool execution
        self.total_units += units
        self.events.append(f'{label}:{units}')         # ← Enables budget-based stop conditions

# --- Part C: Parity Audit — Self-Assessment (parity_audit.py, lines ~121-138) ---

def run_parity_audit():
    """The harness audits ITSELF against the original codebase."""
    current_entries = {path.name for path in CURRENT_ROOT.iterdir()}
    root_hits = [t for t in ARCHIVE_ROOT_FILES.values()     # ← Check: which root files are ported?
                 if t in current_entries]
    dir_hits = [t for t in ARCHIVE_DIR_MAPPINGS.values()    # ← Check: which directories are ported?
                if t in current_entries]
    missing_roots = tuple(t for t in ARCHIVE_ROOT_FILES.values()
                          if t not in current_entries)       # ← Track what's MISSING
    current_python_files = sum(1 for p in CURRENT_ROOT.rglob('*.py'))
    reference = _reference_surface()                         # ← Load the archived baseline
    return ParityAuditResult(
        root_file_coverage=(len(root_hits), len(ARCHIVE_ROOT_FILES)),    # ← e.g., 18/18
        directory_coverage=(len(dir_hits), len(ARCHIVE_DIR_MAPPINGS)),   # ← e.g., 30/35
        total_file_ratio=(current_python_files, int(reference['total_ts_like_files'])),
        command_entry_ratio=(_snapshot_count(COMMAND_SNAPSHOT_PATH), 207),
        tool_entry_ratio=(_snapshot_count(TOOL_SNAPSHOT_PATH), 184),     # ← Meta-verification!
        missing_root_targets=missing_roots,
    )

# --- Part D: Hook Lifecycle [Teaching Implementation — based on Rust hooks.rs patterns] ---
# claw-code's Python hooks/ is a placeholder. This teaching implementation
# is derived from the Rust hooks.rs (357 lines) to show the universal pattern.

@dataclass
class HookEvent:
    kind: str          # 'PreToolUse' | 'PostToolUse' | 'Stop'
    tool_name: str
    tool_input: dict

@dataclass
class HookResult:
    allowed: bool      # ← False = veto the tool execution
    message: str       # ← Reason for denial or audit note

def run_hook(event: HookEvent, hook_commands: list[str]) -> HookResult:
    """Execute hook commands and aggregate results.
    Exit codes: 0 = allow, 2 = deny, other = warn.
    This mirrors Claude Code's PreToolUse/PostToolUse lifecycle."""
    for cmd in hook_commands:
        # In real implementation: subprocess.run(cmd, input=json(event), ...)
        exit_code = 0  # simulate
        if exit_code == 2:                             # ← Exit code 2 = DENY
            return HookResult(allowed=False, message=f'Hook denied: {cmd}')
    return HookResult(allowed=True, message='All hooks passed')

def execute_with_hooks(tool_name, tool_input, hooks, executor):
    """The full hook lifecycle wrapping tool execution."""
    pre = run_hook(HookEvent('PreToolUse', tool_name, tool_input), hooks)  # ← Pre-execution gate
    if not pre.allowed:
        return {'denied': True, 'reason': pre.message}   # ← Tool never executes if denied

    result = executor(tool_name, tool_input)              # ← Actual tool execution

    post = run_hook(HookEvent('PostToolUse', tool_name, tool_input), hooks)  # ← Post-execution audit
    return {'denied': False, 'result': result, 'audit': post.message}
