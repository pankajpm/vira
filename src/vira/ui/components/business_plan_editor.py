"""Business plan editor component with versioning."""

from __future__ import annotations

from typing import TYPE_CHECKING

import chainlit as cl

if TYPE_CHECKING:
    from vira.ui.database.session_manager import SessionManager


class BusinessPlanEditor:
    """Manages business plan editing and versioning."""

    def __init__(self, session_manager: SessionManager):
        """Initialize business plan editor.

        Args:
            session_manager: Database session manager
        """
        self.db = session_manager

    async def render_editor(self, session_id: str) -> None:
        """Render business plan editor interface.

        Args:
            session_id: Current session ID
        """
        plan = self.db.get_latest_plan(session_id)

        if not plan:
            await cl.Message(
                content=(
                    "## 📝 Business Plan Editor\n\n"
                    "No business plan found. Paste your plan in the chat to get started.\n\n"
                    "**Commands:**\n"
                    "- `/edit` - Edit current plan\n"
                    "- `/versions` - View version history\n"
                    "- `/upload` - Upload file (coming soon)"
                ),
                author="Editor",
            ).send()
            return

        content_preview = plan.content[:500] + ("..." if len(plan.content) > 500 else "")

        await cl.Message(
            content=(
                f"## 📝 Business Plan (v{plan.version})\n\n"
                f"**Created:** {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"**By:** {plan.created_by}\n"
                f"**Length:** {len(plan.content)} characters\n\n"
                f"### Preview:\n{content_preview}\n\n"
                f"**Commands:**\n"
                f"- `/edit` - Edit this plan\n"
                f"- `/versions` - View all versions\n"
                f"- `/rollback <version>` - Revert to version\n"
                f"- `/diff <v1> <v2>` - Compare versions"
            ),
            author="Editor",
        ).send()

    async def save_plan(self, session_id: str, content: str, created_by: str = "user") -> bool:
        """Save a new version of the business plan.

        Args:
            session_id: Current session ID
            content: Plan content
            created_by: Who created this version

        Returns:
            True if saved successfully
        """
        try:
            plan = self.db.save_business_plan(
                session_id=session_id,
                content=content,
                created_by=created_by
            )
            return True
        except Exception as e:
            await cl.Message(
                content=f"⚠️ Error saving plan: {str(e)}",
                author="VIRA",
            ).send()
            return False

    async def show_versions(self, session_id: str) -> None:
        """Display version history with diffs.

        Args:
            session_id: Current session ID
        """
        versions = self.db.get_plan_versions(session_id)

        if not versions:
            await cl.Message(
                content="No plan versions found.",
                author="Editor",
            ).send()
            return

        lines = ["## 📜 Business Plan Version History\n"]

        for v in versions[:10]:  # Show last 10
            lines.append(f"### Version {v.version}")
            lines.append(f"- **Created:** {v.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **By:** {v.created_by}")

            if v.diff_summary:
                lines.append(f"- **Changes:** {v.diff_summary}")

            # Content preview
            preview = v.content[:200].replace("\n", " ")
            lines.append(f"- **Preview:** _{preview}..._")
            lines.append("")

        lines.append("\n**Commands:**")
        lines.append("- `/diff <v1> <v2>` - Compare two versions")
        lines.append("- `/rollback <version>` - Restore a version")

        await cl.Message(
            content="\n".join(lines),
            author="Editor",
        ).send()

    async def show_diff(self, session_id: str, v1: int, v2: int) -> None:
        """Show diff between two versions.

        Args:
            session_id: Current session ID
            v1: First version number
            v2: Second version number
        """
        plan1 = self.db.get_plan_by_version(session_id, v1)
        plan2 = self.db.get_plan_by_version(session_id, v2)

        if not plan1 or not plan2:
            await cl.Message(
                content=f"⚠️ Could not find version {v1} or {v2}",
                author="Editor",
            ).send()
            return

        # Use difflib to generate diff
        import difflib

        diff = list(difflib.unified_diff(
            plan1.content.splitlines(keepends=True),
            plan2.content.splitlines(keepends=True),
            fromfile=f"Version {v1}",
            tofile=f"Version {v2}",
            lineterm=""
        ))

        if not diff:
            await cl.Message(
                content=f"No differences between version {v1} and {v2}",
                author="Editor",
            ).send()
            return

        # Show first 50 lines of diff
        diff_text = "".join(diff[:50])
        if len(diff) > 50:
            diff_text += f"\n\n... ({len(diff) - 50} more lines)"

        await cl.Message(
            content=f"## 🔄 Diff: v{v1} → v{v2}\n\n```diff\n{diff_text}\n```",
            author="Editor",
        ).send()

    async def rollback(self, session_id: str, version: int) -> bool:
        """Rollback to a specific version.

        Args:
            session_id: Current session ID
            version: Version number to rollback to

        Returns:
            True if successful
        """
        plan = self.db.get_plan_by_version(session_id, version)

        if not plan:
            await cl.Message(
                content=f"⚠️ Version {version} not found",
                author="Editor",
            ).send()
            return False

        # Create new version with old content
        new_plan = self.db.save_business_plan(
            session_id=session_id,
            content=plan.content,
            created_by="system"
        )

        await cl.Message(
            content=(
                f"✅ Rolled back to version {version}\n"
                f"Created new version {new_plan.version} with content from v{version}"
            ),
            author="Editor",
        ).send()

        return True

    async def upload_file(self, session_id: str, file_path: str) -> bool:
        """Handle file upload for business plan.

        Args:
            session_id: Current session ID
            file_path: Path to uploaded file

        Returns:
            True if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            await self.save_plan(session_id, content, created_by="file_upload")
            return True
        except Exception as e:
            await cl.Message(
                content=f"⚠️ Error reading file: {str(e)}",
                author="Editor",
            ).send()
            return False

