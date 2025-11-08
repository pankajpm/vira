"""Session manager for database operations."""

from __future__ import annotations

import difflib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, desc, select
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import sessionmaker

from .models import Analysis, Base, BusinessPlan, Message, Session


class SessionManager:
    """Manages database operations for chat sessions."""

    def __init__(self, db_path: str | Path = "./data/vira_sessions.db"):
        """Initialize session manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create engine and session factory
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_db(self) -> DBSession:
        """Get database session."""
        return self.SessionLocal()

    # ========== Session Operations ==========

    def create_session(self, company_name: str, metadata: dict[str, Any] | None = None) -> Session:
        """Create a new chat session.

        Args:
            company_name: Name of the company
            metadata: Optional metadata dictionary

        Returns:
            Created session object
        """
        with self._get_db() as db:
            session = Session(company_name=company_name, metadata_=metadata or {})
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    def get_session(self, session_id: str) -> Session | None:
        """Get session by ID.

        Args:
            session_id: Session UUID

        Returns:
            Session object or None if not found
        """
        with self._get_db() as db:
            stmt = select(Session).where(Session.id == session_id)
            return db.execute(stmt).scalar_one_or_none()

    def list_sessions(self, limit: int = 50, status: str = "active") -> list[Session]:
        """List recent sessions.

        Args:
            limit: Maximum number of sessions to return
            status: Filter by status (active, archived)

        Returns:
            List of session objects
        """
        with self._get_db() as db:
            stmt = select(Session).where(Session.status == status).order_by(desc(Session.updated_at)).limit(limit)
            return list(db.execute(stmt).scalars().all())

    def update_session(self, session_id: str, **kwargs: Any) -> Session:
        """Update session fields.

        Args:
            session_id: Session UUID
            **kwargs: Fields to update

        Returns:
            Updated session object
        """
        with self._get_db() as db:
            session = db.execute(select(Session).where(Session.id == session_id)).scalar_one()
            for key, value in kwargs.items():
                if key == "metadata":
                    key = "metadata_"
                setattr(session, key, value)
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(session)
            return session

    def archive_session(self, session_id: str) -> None:
        """Archive a session.

        Args:
            session_id: Session UUID
        """
        self.update_session(session_id, status="archived")

    def search_sessions(self, search_term: str, limit: int = 50) -> list[Session]:
        """Search sessions by company name.

        Args:
            search_term: Term to search for in company name
            limit: Maximum number of results

        Returns:
            List of matching sessions
        """
        with self._get_db() as db:
            stmt = (
                select(Session)
                .where(Session.company_name.contains(search_term))
                .order_by(desc(Session.updated_at))
                .limit(limit)
            )
            return list(db.execute(stmt).scalars().all())

    # ========== Message Operations ==========

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """Add a message to a session.

        Args:
            session_id: Session UUID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata

        Returns:
            Created message object
        """
        with self._get_db() as db:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                metadata_=metadata or {},
            )
            db.add(message)

            # Update session timestamp
            session = db.execute(select(Session).where(Session.id == session_id)).scalar_one()
            session.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(message)
            return message

    def update_message(self, message_id: str, content: str | None = None, metadata: dict[str, Any] | None = None) -> Message | None:
        """Update a message's content or metadata.

        Args:
            message_id: Message UUID
            content: New content (optional)
            metadata: New metadata (optional)

        Returns:
            Updated message object or None if not found
        """
        with self._get_db() as db:
            message = db.execute(select(Message).where(Message.id == message_id)).scalar_one_or_none()
            if not message:
                return None
            
            if content is not None:
                message.content = content
            if metadata is not None:
                message.metadata_ = metadata
            
            db.commit()
            db.refresh(message)
            return message

    def get_messages(self, session_id: str, limit: int | None = None) -> list[Message]:
        """Get messages for a session.

        Args:
            session_id: Session UUID
            limit: Optional limit on number of messages

        Returns:
            List of message objects ordered by creation time
        """
        with self._get_db() as db:
            stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
            if limit:
                stmt = stmt.limit(limit)
            return list(db.execute(stmt).scalars().all())

    def get_conversation_history(self, session_id: str) -> list[dict[str, str]]:
        """Get conversation history formatted for LLM context.

        Args:
            session_id: Session UUID

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        messages = self.get_messages(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    # ========== Business Plan Operations ==========

    def save_business_plan(
        self,
        session_id: str,
        content: str,
        created_by: str = "user",
    ) -> BusinessPlan:
        """Save a new version of the business plan.

        Args:
            session_id: Session UUID
            content: Business plan content
            created_by: Who created this version (user/system)

        Returns:
            Created business plan object
        """
        with self._get_db() as db:
            # Get latest version number
            stmt = (
                select(BusinessPlan)
                .where(BusinessPlan.session_id == session_id)
                .order_by(desc(BusinessPlan.version))
                .limit(1)
            )
            latest = db.execute(stmt).scalar_one_or_none()
            next_version = (latest.version + 1) if latest else 1

            # Generate diff summary
            diff_summary = None
            if latest:
                diff_summary = self._generate_diff_summary(latest.content, content)

            # Create new version
            plan = BusinessPlan(
                session_id=session_id,
                version=next_version,
                content=content,
                created_by=created_by,
                diff_summary=diff_summary,
            )
            db.add(plan)

            # Update session timestamp
            session = db.execute(select(Session).where(Session.id == session_id)).scalar_one()
            session.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(plan)
            return plan

    def get_latest_plan(self, session_id: str) -> BusinessPlan | None:
        """Get the latest version of the business plan.

        Args:
            session_id: Session UUID

        Returns:
            Latest business plan or None
        """
        with self._get_db() as db:
            stmt = (
                select(BusinessPlan)
                .where(BusinessPlan.session_id == session_id)
                .order_by(desc(BusinessPlan.version))
                .limit(1)
            )
            return db.execute(stmt).scalar_one_or_none()

    def get_plan_versions(self, session_id: str) -> list[BusinessPlan]:
        """Get all versions of the business plan.

        Args:
            session_id: Session UUID

        Returns:
            List of business plan versions
        """
        with self._get_db() as db:
            stmt = select(BusinessPlan).where(BusinessPlan.session_id == session_id).order_by(desc(BusinessPlan.version))
            return list(db.execute(stmt).scalars().all())

    def get_plan_by_version(self, session_id: str, version: int) -> BusinessPlan | None:
        """Get a specific version of business plan.

        Args:
            session_id: Session UUID
            version: Version number

        Returns:
            Business plan object or None if not found
        """
        with self._get_db() as db:
            stmt = select(BusinessPlan).where(
                BusinessPlan.session_id == session_id,
                BusinessPlan.version == version
            )
            return db.execute(stmt).scalar_one_or_none()

    def _generate_diff_summary(self, old_content: str, new_content: str) -> str:
        """Generate a summary of changes between two versions.

        Args:
            old_content: Previous content
            new_content: New content

        Returns:
            Summary string
        """
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm="", n=0))

        if not diff:
            return "No changes"

        added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

        return f"+{added} lines, -{removed} lines"

    # ========== Analysis Operations ==========

    def save_analysis(
        self,
        session_id: str,
        message_id: str,
        plan_version: int,
        retrieved_docs: int | None = None,
        tokens_used: dict[str, Any] | None = None,
        latency_ms: dict[str, float] | None = None,
        langsmith_trace_url: str | None = None,
    ) -> Analysis:
        """Save analysis metadata.

        Args:
            session_id: Session UUID
            message_id: Associated message ID
            plan_version: Business plan version used
            retrieved_docs: Number of documents retrieved
            tokens_used: Token usage dict
            latency_ms: Latency breakdown dict
            langsmith_trace_url: LangSmith trace URL

        Returns:
            Created analysis object
        """
        with self._get_db() as db:
            analysis = Analysis(
                session_id=session_id,
                message_id=message_id,
                plan_version=plan_version,
                retrieved_docs=retrieved_docs,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                langsmith_trace_url=langsmith_trace_url,
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis

    def get_analysis(self, message_id: str) -> Analysis | None:
        """Get analysis for a message.

        Args:
            message_id: Message UUID

        Returns:
            Analysis object or None
        """
        with self._get_db() as db:
            stmt = select(Analysis).where(Analysis.message_id == message_id)
            return db.execute(stmt).scalar_one_or_none()

    def get_session_analyses(self, session_id: str) -> list[Analysis]:
        """Get all analyses for a session.

        Args:
            session_id: Session UUID

        Returns:
            List of analysis objects
        """
        with self._get_db() as db:
            stmt = select(Analysis).where(Analysis.session_id == session_id).order_by(desc(Analysis.created_at))
            return list(db.execute(stmt).scalars().all())

    # ========== Utility Methods ==========

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        """Get a summary of session statistics.

        Args:
            session_id: Session UUID

        Returns:
            Dictionary with summary statistics
        """
        with self._get_db() as db:
            session = db.execute(select(Session).where(Session.id == session_id)).scalar_one()
            messages = self.get_messages(session_id)
            plans = self.get_plan_versions(session_id)
            analyses = self.get_session_analyses(session_id)

            return {
                "session_id": session_id,
                "company_name": session.company_name,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "status": session.status,
                "message_count": len(messages),
                "plan_versions": len(plans),
                "analysis_count": len(analyses),
                "last_plan_version": plans[0].version if plans else 0,
            }

