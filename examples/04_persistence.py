#!/usr/bin/env python3
"""Layer 4: Persistence — Memory Across Sessions.

Based on claw-code's SessionStore, TranscriptStore, and HistoryLog.
Maps to Claude Code's session save/resume and CLAUDE.md hierarchy.

Source: https://github.com/instructkr/claw-code/blob/main/src/session_store.py
"""

from __future__ import annotations
import json
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from uuid import uuid4
from utils.display import console, print_header, print_step, print_result


# --- Session Store (from claw-code: src/session_store.py, full module) ---

@dataclass(frozen=True)
class StoredSession:
    """Immutable session snapshot for persistence."""
    session_id: str
    messages: tuple[str, ...]
    input_tokens: int
    output_tokens: int


def save_session(session: StoredSession, directory: Path) -> Path:
    """Save session as JSON. From claw-code: session_store.py save_session()."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{session.session_id}.json"
    path.write_text(json.dumps(asdict(session), indent=2))
    return path


def load_session(session_id: str, directory: Path) -> StoredSession:
    """Load session from JSON. From claw-code: session_store.py load_session()."""
    data = json.loads((directory / f"{session_id}.json").read_text())
    return StoredSession(
        session_id=data["session_id"],
        messages=tuple(data["messages"]),
        input_tokens=data["input_tokens"],
        output_tokens=data["output_tokens"],
    )


# --- Transcript Store (from claw-code: src/transcript.py, full module) ---

@dataclass
class TranscriptStore:
    """In-memory message store with compaction support."""
    entries: list[str] = field(default_factory=list)
    flushed: bool = False

    def append(self, entry: str) -> None:
        self.entries.append(entry)
        self.flushed = False

    def compact(self, keep_last: int = 10) -> int:
        """Keep only the most recent N entries. Returns count removed."""
        if len(self.entries) <= keep_last:
            return 0
        removed = len(self.entries) - keep_last
        self.entries[:] = self.entries[-keep_last:]
        return removed

    def replay(self) -> tuple[str, ...]:
        return tuple(self.entries)

    def flush(self) -> None:
        self.flushed = True


# --- History Log (from claw-code: src/history.py, full module) ---

@dataclass(frozen=True)
class HistoryEvent:
    title: str
    detail: str

@dataclass
class HistoryLog:
    """Append-only event log — the agent's audit trail."""
    events: list[HistoryEvent] = field(default_factory=list)

    def add(self, title: str, detail: str) -> None:
        self.events.append(HistoryEvent(title=title, detail=detail))

    def as_markdown(self) -> str:
        lines = ["# Session History", ""]
        lines.extend(f"- {e.title}: {e.detail}" for e in self.events)
        return "\n".join(lines)


if __name__ == "__main__":
    print_header("Layer 4: Persistence", layer="persistence")
    console.print("\n[dim]Based on claw-code's session store, transcript, and history[/dim]\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        session_dir = Path(tmpdir)

        # Step 1: Create and populate a session
        print_step(1, "Creating session with messages")
        session_id = uuid4().hex[:12]
        transcript = TranscriptStore()
        history = HistoryLog()

        for i in range(5):
            msg = f"Turn {i+1}: Working on the task..."
            transcript.append(msg)
            history.add("turn", f"Completed turn {i+1}")

        print_result("Session ID", session_id)
        print_result("Messages", str(len(transcript.entries)))
        print_result("History events", str(len(history.events)))

        # Step 2: Save session
        print_step(2, "Saving session to disk")
        stored = StoredSession(
            session_id=session_id,
            messages=transcript.replay(),
            input_tokens=150, output_tokens=300,
        )
        path = save_session(stored, session_dir)
        print_result("Saved to", str(path))

        # Step 3: Load session (the "/resume" pattern)
        print_step(3, "Loading session (resume pattern)")
        loaded = load_session(session_id, session_dir)
        print_result("Loaded ID", loaded.session_id)
        print_result("Messages", str(len(loaded.messages)))
        print_result("Tokens", f"in={loaded.input_tokens} out={loaded.output_tokens}")

        # Step 4: Demonstrate transcript compaction
        print_step(4, "Transcript compaction (keep_last=3)")
        t2 = TranscriptStore(entries=list(loaded.messages))
        removed = t2.compact(keep_last=3)
        print_result("Removed", f"{removed} old messages")
        print_result("Remaining", str(t2.replay()))

        # Step 5: Show history log
        print_step(5, "History audit trail")
        console.print(f"\n[dim]{history.as_markdown()}[/dim]")
