"""SQLAlchemy models for session persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Session(Base):
    """Chat session model."""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    company_name = Column(String, nullable=False)
    status = Column(String, default="active")  # active, archived
    metadata_ = Column("metadata", JSON, default=dict)  # Additional session data

    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    business_plans = relationship("BusinessPlan", back_populates="session", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "company_name": self.company_name,
            "status": self.status,
            "metadata": self.metadata_,
        }


class Message(Base):
    """Chat message model."""

    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata_ = Column("metadata", JSON, default=dict)  # Tool calls, traces, etc.

    # Relationships
    session = relationship("Session", back_populates="messages")
    analyses = relationship("Analysis", back_populates="message")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata_,
        }


class BusinessPlan(Base):
    """Versioned business plan storage."""

    __tablename__ = "business_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String, default="user")  # system or user
    diff_summary = Column(Text)  # What changed

    # Relationships
    session = relationship("Session", back_populates="business_plans")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "version": self.version,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "diff_summary": self.diff_summary,
        }


class Analysis(Base):
    """Analysis run tracking."""

    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    plan_version = Column(Integer, nullable=False)
    retrieved_docs = Column(Integer)
    tokens_used = Column(JSON)  # {input: int, output: int, cost: float}
    latency_ms = Column(JSON)  # {retrieval: float, llm: float, total: float}
    langsmith_trace_url = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("Session", back_populates="analyses")
    message = relationship("Message", back_populates="analyses")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "plan_version": self.plan_version,
            "retrieved_docs": self.retrieved_docs,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "langsmith_trace_url": self.langsmith_trace_url,
            "created_at": self.created_at.isoformat(),
        }


def create_tables(db_url: str = "sqlite:///./data/vira_sessions.db") -> None:
    """Create all tables in the database."""
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    # Create tables when run directly
    create_tables()
    print("✅ Database tables created successfully")

