"""Context manager for session state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vira.ui.database.models import BusinessPlan, Session


@dataclass
class SessionContext:
    """Container for session state."""

    session_id: str
    session: Session
    current_plan: BusinessPlan | None = None
    conversation_history: list[dict[str, Any]] = field(default_factory=list)
    debug_mode: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "company_name": self.session.company_name,
            "plan_version": self.current_plan.version if self.current_plan else None,
            "debug_mode": self.debug_mode,
            "message_count": len(self.conversation_history),
            "metadata": self.metadata,
        }


class ContextManager:
    """Manages session context and state."""

    def __init__(self):
        """Initialize context manager."""
        self._contexts: dict[str, SessionContext] = {}

    def create_context(
        self,
        session_id: str,
        session: Session,
        plan: BusinessPlan | None = None,
        debug_mode: bool = False,
    ) -> SessionContext:
        """Create a new session context.

        Args:
            session_id: Session ID
            session: Session object
            plan: Business plan (if available)
            debug_mode: Debug mode flag

        Returns:
            Created context
        """
        context = SessionContext(
            session_id=session_id,
            session=session,
            current_plan=plan,
            debug_mode=debug_mode,
        )
        self._contexts[session_id] = context
        return context

    def get_context(self, session_id: str) -> SessionContext | None:
        """Get context for a session.

        Args:
            session_id: Session ID

        Returns:
            Context or None if not found
        """
        return self._contexts.get(session_id)

    def update_plan(self, session_id: str, plan: BusinessPlan) -> None:
        """Update business plan in context.

        Args:
            session_id: Session ID
            plan: New business plan
        """
        if context := self._contexts.get(session_id):
            context.current_plan = plan

    def add_message(self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add message to conversation history.

        Args:
            session_id: Session ID
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        if context := self._contexts.get(session_id):
            context.conversation_history.append({
                "role": role,
                "content": content,
                "metadata": metadata or {},
            })

    def set_debug_mode(self, session_id: str, enabled: bool) -> None:
        """Toggle debug mode.

        Args:
            session_id: Session ID
            enabled: Enable or disable
        """
        if context := self._contexts.get(session_id):
            context.debug_mode = enabled

    def clear_context(self, session_id: str) -> None:
        """Clear context for a session.

        Args:
            session_id: Session ID
        """
        self._contexts.pop(session_id, None)

    def get_full_context(self, session_id: str) -> str:
        """Get formatted full context for LLM.

        Args:
            session_id: Session ID

        Returns:
            Formatted context string
        """
        context = self._contexts.get(session_id)
        if not context:
            return ""

        parts = []

        # Session info
        parts.append(f"Session: {context.session.company_name}")
        parts.append(f"Session ID: {context.session_id}")

        # Business plan
        if context.current_plan:
            parts.append(f"\nBusiness Plan (v{context.current_plan.version}):")
            parts.append(context.current_plan.content)

        # Conversation history
        if context.conversation_history:
            parts.append("\nConversation History:")
            for msg in context.conversation_history[-10:]:  # Last 10 messages
                parts.append(f"{msg['role']}: {msg['content'][:200]}")

        return "\n".join(parts)

