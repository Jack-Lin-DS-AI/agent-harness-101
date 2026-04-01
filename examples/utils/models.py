"""Pydantic models for Agent-Harness-101 examples.
Based on claw-code's src/models.py data structures."""

from __future__ import annotations
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A conversation message (maps to claw-code's ConversationMessage)."""
    role: str = Field(description="'user', 'assistant', or 'tool'")
    content: str = Field(description="Message text content")
    tool_use_id: str | None = None


class ToolCall(BaseModel):
    """A tool invocation request from the model."""
    id: str
    name: str
    input: dict = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Result of executing a tool."""
    tool_use_id: str
    content: str
    is_error: bool = False


class SessionState(BaseModel):
    """Persisted session state (maps to claw-code's StoredSession)."""
    session_id: str
    messages: list[Message] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0


class PermissionContext(BaseModel):
    """Permission configuration (maps to claw-code's ToolPermissionContext)."""
    deny_names: set[str] = Field(default_factory=set)
    deny_prefixes: list[str] = Field(default_factory=list)

    def blocks(self, tool_name: str) -> bool:
        lowered = tool_name.lower()
        return (lowered in {n.lower() for n in self.deny_names}
                or any(lowered.startswith(p.lower()) for p in self.deny_prefixes))
