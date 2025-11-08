"""Debug panel component for developer mode."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import chainlit as cl

if TYPE_CHECKING:
    from vira.ui.database.session_manager import SessionManager


class DebugPanel:
    """Displays debug information for developers."""

    def __init__(self, session_manager: SessionManager):
        """Initialize debug panel.

        Args:
            session_manager: Database session manager
        """
        self.db = session_manager

    async def render(
        self,
        message_id: str,
        latency_ms: float,
        retrieved_docs: list[Any],
        tokens_input: int = 0,
        tokens_output: int = 0,
        langsmith_url: str | None = None,
    ) -> None:
        """Render debug panel with performance metrics.

        Args:
            message_id: Associated message ID
            latency_ms: Total latency in milliseconds
            retrieved_docs: List of retrieved documents
            tokens_input: Input token count
            tokens_output: Output token count
            langsmith_url: LangSmith trace URL
        """
        analysis = self.db.get_analysis(message_id)

        if not analysis:
            await cl.Message(
                content="⚠️ Debug info not available",
                author="Debug",
            ).send()
            return

        # Calculate costs (GPT-4o-mini pricing)
        input_cost = tokens_input * 0.00015 / 1000  # $0.15 per 1M tokens
        output_cost = tokens_output * 0.00060 / 1000  # $0.60 per 1M tokens
        total_cost = input_cost + output_cost

        # Build debug content
        lines = ["## 🔍 Debug Information\n"]

        # Performance metrics
        lines.append("### ⚡ Performance")
        lines.append(f"- **Retrieval:** {analysis.latency_ms.get('retrieval', 0):.0f}ms")
        lines.append(f"- **LLM Generation:** {analysis.latency_ms.get('llm', 0):.0f}ms")
        lines.append(f"- **Total:** {latency_ms:.0f}ms")
        lines.append("")

        # Token usage
        lines.append("### 🔢 Token Usage")
        lines.append(f"- **Input Tokens:** {tokens_input:,}")
        lines.append(f"- **Output Tokens:** {tokens_output:,}")
        lines.append(f"- **Total Tokens:** {tokens_input + tokens_output:,}")
        lines.append(f"- **Estimated Cost:** ${total_cost:.4f}")
        lines.append("")

        # Retrieved documents
        lines.append(f"### 📚 Retrieved Documents ({len(retrieved_docs)} docs)")
        for i, doc in enumerate(retrieved_docs[:5], 1):  # Show first 5
            url = doc.metadata.get("url", "unknown")
            score = doc.metadata.get("score", "N/A")
            content_preview = doc.page_content[:100].replace("\n", " ")

            lines.append(f"\n**{i}. Source Document**")
            lines.append(f"- **URL:** [{url}]({url})")
            lines.append(f"- **Relevance Score:** {score}")
            lines.append(f"- **Preview:** _{content_preview}..._")

        if len(retrieved_docs) > 5:
            lines.append(f"\n_... and {len(retrieved_docs) - 5} more documents_")

        lines.append("\n")

        # LangSmith trace
        lines.append("### 🔗 Tracing")
        if langsmith_url:
            lines.append(f"- **LangSmith Trace:** [View Full Trace]({langsmith_url})")
        else:
            lines.append("- **LangSmith:** _Not configured_")
            lines.append("- Set `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT` env vars to enable")

        lines.append("\n")

        # Session info
        lines.append("### 📊 Session Info")
        lines.append(f"- **Message ID:** `{message_id[:16]}...`")
        lines.append(f"- **Plan Version:** {analysis.plan_version}")
        lines.append(f"- **Timestamp:** {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        await cl.Message(
            content="\n".join(lines),
            author="Debug",
        ).send()

    async def render_retrieval_details(self, docs: list[Any]) -> None:
        """Show detailed retrieval information.

        Args:
            docs: Retrieved documents
        """
        if not docs:
            await cl.Message(
                content="No documents retrieved",
                author="Debug",
            ).send()
            return

        lines = [f"## 📚 Retrieval Details ({len(docs)} documents)\n"]

        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            lines.append(f"### Document {i}")
            lines.append(f"**URL:** [{metadata.get('url', 'N/A')}]({metadata.get('url', '#')})")
            lines.append(f"**Score:** {metadata.get('score', 'N/A')}")
            lines.append(f"**Source:** {metadata.get('source', 'N/A')}")
            lines.append(f"**Chunk:** {metadata.get('chunk_id', 'N/A')}")
            lines.append(f"\n**Content:**\n```\n{doc.page_content[:300]}\n```\n")

        await cl.Message(
            content="\n".join(lines),
            author="Debug",
        ).send()

    def format_retrieved_docs(self, docs: list[Any]) -> str:
        """Format retrieved documents for display.

        Args:
            docs: List of documents

        Returns:
            Formatted string
        """
        output = []
        for i, doc in enumerate(docs[:5], 1):
            url = doc.metadata.get("url", "unknown")
            content_preview = doc.page_content[:150].replace("\n", " ")
            output.append(f"{i}. [{url}]({url})")
            output.append(f"   _{content_preview}_...")
            output.append("")
        return "\n".join(output)

