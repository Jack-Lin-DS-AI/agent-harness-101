# From claw-code: src/session_store.py + src/transcript.py + src/history.py + src/query_engine.py
# Layer 4: Persistence — Memory across sessions
# https://github.com/instructkr/claw-code

# --- Part A: Session Store (session_store.py, full file — 35 lines) ---

@dataclass(frozen=True)
class StoredSession:
    session_id: str                                    # ← Unique session identifier
    messages: tuple[str, ...]                          # ← Immutable message history
    input_tokens: int                                  # ← Usage tracking persisted with session
    output_tokens: int

DEFAULT_SESSION_DIR = Path('.port_sessions')            # ← Sessions saved to local directory

def save_session(session, directory=None):
    target_dir = directory or DEFAULT_SESSION_DIR
    target_dir.mkdir(parents=True, exist_ok=True)      # ← Auto-create storage directory
    path = target_dir / f'{session.session_id}.json'
    path.write_text(json.dumps(asdict(session), indent=2))  # ← JSON serialization
    return path

def load_session(session_id, directory=None):
    target_dir = directory or DEFAULT_SESSION_DIR
    data = json.loads((target_dir / f'{session_id}.json').read_text())
    return StoredSession(                              # ← Reconstruct immutable dataclass
        session_id=data['session_id'],
        messages=tuple(data['messages']),
        input_tokens=data['input_tokens'],
        output_tokens=data['output_tokens'],
    )

# --- Part B: Session Recovery (query_engine.py, lines ~49-59) ---

@classmethod
def from_saved_session(cls, session_id):               # ← The "/resume" pattern
    stored = load_session(session_id)                  # ← Load persisted state
    transcript = TranscriptStore(entries=list(stored.messages), flushed=True)
    return cls(
        manifest=build_port_manifest(),
        session_id=stored.session_id,                  # ← Restore original session ID
        mutable_messages=list(stored.messages),        # ← Restore message history
        total_usage=UsageSummary(stored.input_tokens, stored.output_tokens),  # ← Restore counters
        transcript_store=transcript,                   # ← Rebuild transcript from stored messages
    )

# --- Part C: Transcript Store (transcript.py, full file — 23 lines) ---

@dataclass
class TranscriptStore:
    entries: list[str] = field(default_factory=list)   # ← Mutable message list
    flushed: bool = False

    def append(self, entry):                           # ← Add new message
        self.entries.append(entry)
        self.flushed = False                           # ← Mark as dirty

    def compact(self, keep_last=10):                   # ← Compaction: keep only recent N
        if len(self.entries) > keep_last:
            self.entries[:] = self.entries[-keep_last:]

    def replay(self):                                  # ← Read back all messages
        return tuple(self.entries)

    def flush(self):                                   # ← Mark as persisted
        self.flushed = True

# --- Part D: History Log (history.py, full file — 22 lines) ---

@dataclass(frozen=True)
class HistoryEvent:
    title: str                                         # ← Event category (e.g., 'routing', 'execution')
    detail: str                                        # ← Human-readable detail

@dataclass
class HistoryLog:
    events: list[HistoryEvent] = field(default_factory=list)

    def add(self, title, detail):                      # ← Append-only audit trail
        self.events.append(HistoryEvent(title=title, detail=detail))

    def as_markdown(self):                             # ← Render for inspection
        lines = ['# Session History', '']
        lines.extend(f'- {e.title}: {e.detail}' for e in self.events)
        return '\n'.join(lines)
