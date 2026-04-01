## Persistence

Persistence lets the agent remember across sessions. Without it, every conversation starts from zero. With it, the agent can resume work, recall decisions, and maintain continuity.

### Stored Sessions

`StoredSession` in `session_store.py` is the core data structure. It holds:

- A `session_id` to uniquely identify the conversation
- The full list of messages exchanged
- Token counts for tracking usage

Sessions are saved as JSON files to the `.port_sessions/` directory. This is deliberately simple — no database, no complex serialization. Just JSON on disk.

### The Resume Pattern

`from_saved_session()` in `query_engine.py` implements the "/resume" pattern. When a user wants to continue a previous session, this function:

- Loads the stored session from disk
- Rebuilds the `TranscriptStore` with the saved messages
- Restores usage counters so budget tracking continues accurately

This means the agent picks up exactly where it left off. The model sees the full prior conversation and can continue reasoning without losing thread.

### TranscriptStore

`TranscriptStore` is the mutable message list that the agent works with during a session. It provides three key operations:

- `compact(keep_last=10)` — Trim the message list to the most recent entries
- `replay()` — Iterate over all stored messages, useful for rebuilding state
- `flush()` — Clear the store, typically after saving to disk

The transcript is the live working set. It grows during a session and gets compacted or saved when needed.

### HistoryLog

`HistoryLog` is a separate concern from the transcript. It is an append-only event log where each entry is a title-and-detail pair. Think of it as the agent's audit trail.

While the transcript stores the raw messages (what was said), the history log stores events (what happened). A transcript entry might be "read file X," while the history entry might be "File read: X, 200 lines, 3.2ms."

> **Teaching note:** claw-code deliberately separates transcripts from history. Transcripts are for the model — they feed back into the conversation. History is for the operator — it provides observability into what the agent did and why. Mixing these concerns would compromise both.

### The Universal Pattern

Stateful agents need to save and restore conversation state. Whether it is a database, a file on disk, or an in-memory cache, the problem is the same: serialize the conversation, store it somewhere durable, and reconstruct it when needed. The resume pattern is how agents achieve continuity across sessions.
