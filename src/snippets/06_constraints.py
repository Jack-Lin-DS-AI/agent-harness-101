# From claw-code: src/permissions.py (full) + src/tools.py (filter) + src/models.py (denial)
# + Teaching implementation based on Rust sandbox.rs patterns
# Layer 6: Constraints — The foundation of trust
# https://github.com/instructkr/claw-code

# --- Part A: Permission Engine (permissions.py, full file — 20 lines) ---

@dataclass(frozen=True)
class ToolPermissionContext:
    deny_names: frozenset[str] = field(default_factory=frozenset)  # ← Exact-match blocklist
    deny_prefixes: tuple[str, ...] = ()                            # ← Prefix-match blocklist

    @classmethod
    def from_iterables(cls, deny_names=None, deny_prefixes=None):
        return cls(
            deny_names=frozenset(name.lower() for name in (deny_names or [])),
            deny_prefixes=tuple(prefix.lower() for prefix in (deny_prefixes or [])),
        )

    def blocks(self, tool_name):                       # ← The ENTIRE permission check
        lowered = tool_name.lower()
        return (lowered in self.deny_names             # ← Check 1: exact name match
                or any(lowered.startswith(p)           # ← Check 2: prefix match (e.g., "mcp__")
                       for p in self.deny_prefixes))

# --- Part B: Permission-Gated Tool Filtering (tools.py, lines ~56-72) ---

def filter_tools_by_permission_context(tools, permission_context=None):
    if permission_context is None:                     # ← No context = no restrictions
        return tools
    return tuple(m for m in tools                      # ← Denied tools NEVER reach the LLM
                 if not permission_context.blocks(m.name))

# --- Part C: Permission Denial Tracking (models.py + runtime.py) ---

@dataclass(frozen=True)
class PermissionDenial:
    tool_name: str                                     # ← WHICH tool was denied
    reason: str                                        # ← WHY it was denied

def _infer_permission_denials(self, matches):          # ← From runtime.py
    denials = []
    for match in matches:
        if match.kind == 'tool' and 'bash' in match.name.lower():
            denials.append(PermissionDenial(           # ← Bash is gated by default
                tool_name=match.name,
                reason='destructive shell execution remains gated'))
    return denials
    # Denials tracked per-session, reported in TurnResult
    # The LLM sees: "tool X was denied because Y"     # ← Transparency: model knows why

# --- Part D: Trust Modes (setup.py) ---

def run_setup(cwd=None, trusted=True):                 # ← Binary trust gate at startup
    # trusted=True  → full capabilities enabled
    # trusted=False → restricted mode (deferred init skipped)
    deferred = run_deferred_init(trusted=trusted)      # ← Trust-gated initialization
    return SetupReport(setup=build_workspace_setup(),
                       trusted=trusted, deferred_init=deferred,
                       prefetches=tuple(prefetches), cwd=root)

# --- Part E: Sandbox Patterns [Teaching Implementation — based on Rust sandbox.rs] ---
# claw-code's Rust sandbox.rs (364 lines) implements OS-level process isolation.
# This teaching implementation shows the pattern.

@dataclass
class SandboxConfig:
    enabled: bool = True
    network_allowed: bool = False                      # ← Network access control
    filesystem_mode: str = 'workspace_only'            # ← 'off' | 'workspace_only' | 'allowlist'
    allowed_paths: list[str] = field(default_factory=list)

@dataclass
class SandboxStatus:
    supported: bool                                    # ← Can the OS sandbox processes?
    active: bool                                       # ← Is sandboxing currently on?
    reason: str                                        # ← Why not, if inactive

def resolve_sandbox_status(config):
    """Detect OS capabilities and resolve actual sandbox status."""
    import platform
    is_linux = platform.system() == 'Linux'
    if not config.enabled:
        return SandboxStatus(is_linux, False, 'Disabled by config')
    if not is_linux:
        return SandboxStatus(False, False, f'Not supported on {platform.system()}')
    return SandboxStatus(True, True, 'Linux namespace isolation active')  # ← Graceful degradation
