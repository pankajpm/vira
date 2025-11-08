"""Chat history sidebar component."""

from __future__ import annotations

from typing import TYPE_CHECKING

import chainlit as cl

if TYPE_CHECKING:
    from vira.ui.database.session_manager import SessionManager


class ChatHistory:
    """Manages chat history sidebar display."""

    def __init__(self, session_manager: SessionManager):
        """Initialize chat history component.

        Args:
            session_manager: Database session manager
        """
        self.db = session_manager

    async def render_sidebar(self, current_session_id: str | None = None) -> None:
        """Render session history in sidebar.

        Args:
            current_session_id: Currently active session ID
        """
        sessions = self.db.list_sessions(limit=20)

        if not sessions:
            await cl.Message(
                content="📊 **Session History**\n\nNo previous sessions found.",
                author="History",
            ).send()
            return

        # Build session list with active indicator
        lines = ["## 📊 Session History\n"]
        for session in sessions:
            is_current = session.id == current_session_id
            indicator = "●" if is_current else "○"
            timestamp = session.created_at.strftime("%b %d, %I:%M %p")

            lines.append(f"{indicator} **{session.company_name}**")
            lines.append(f"  _ID: {session.id[:8]}..._")
            lines.append(f"  _Created: {timestamp}_")
            lines.append(f"  _Status: {session.status}_")
            lines.append("")

        lines.append("\n---\n")
        lines.append("**Commands:**")
        lines.append("- `/load <session_id>` - Load a session")
        lines.append("- `/sessions` - Refresh list")
        lines.append("- `/search <term>` - Search sessions")

        await cl.Message(
            content="\n".join(lines),
            author="History",
        ).send()

    async def load_session(self, session_id: str) -> bool:
        """Load a previous session into current chat.

        Args:
            session_id: Session ID to load

        Returns:
            True if loaded successfully
        """
        session = self.db.get_session(session_id)

        if not session:
            await cl.Message(
                content=f"⚠️ Session `{session_id}` not found.",
                author="VIRA",
            ).send()
            return False

        # Load messages
        messages = self.db.get_messages(session_id)

        await cl.Message(
            content=f"📂 Loading session for **{session.company_name}** ({len(messages)} messages)...",
            author="VIRA",
        ).send()

        # Display message history
        for msg in messages[-10:]:  # Last 10 messages
            await cl.Message(
                content=msg.content,
                author="User" if msg.role == "user" else "VIRA",
            ).send()

        # Load business plan
        plan = self.db.get_latest_plan(session_id)
        if plan:
            await cl.Message(
                content=f"📝 Business plan loaded (version {plan.version})",
                author="VIRA",
            ).send()

        return True

    async def search_sessions(self, search_term: str) -> None:
        """Search sessions by company name.

        Args:
            search_term: Term to search for
        """
        sessions = self.db.search_sessions(search_term)

        if not sessions:
            await cl.Message(
                content=f"🔍 No sessions found matching '{search_term}'",
                author="VIRA",
            ).send()
            return

        lines = [f"## 🔍 Search Results for '{search_term}'\n"]
        for session in sessions[:10]:  # Limit to 10
            timestamp = session.created_at.strftime("%b %d, %I:%M %p")
            lines.append(f"**{session.company_name}**")
            lines.append(f"  _ID: {session.id[:8]}..._")
            lines.append(f"  _Created: {timestamp}_")
            lines.append("")

        await cl.Message(
            content="\n".join(lines),
            author="VIRA",
        ).send()

