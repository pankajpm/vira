"""Chainlit-based multi-turn chat interface for VIRA."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import chainlit as cl
from chainlit.input_widget import Switch

from vira.config.settings import get_settings
from vira.rag.pipeline import AlignmentAnalyzer
from vira.ui.components import BusinessPlanEditor, ChatHistory, DebugPanel
from vira.ui.database.session_manager import SessionManager
from vira.ui.state import ContextManager
from vira.ui.utils import estimate_tokens, estimate_tokens_accurate, get_langsmith_trace_url, init_langsmith, calculate_cost

# Initialize components
settings = get_settings()
db = SessionManager(Path("./data/vira_sessions.db"))

# Initialize analyzer (Iteration 2 if enabled, else Iteration 1)
if settings.enable_reflection:
    try:
        from vira.agents.analyzer import ReflectiveAnalyzer
        analyzer = ReflectiveAnalyzer()
        print("🔬 Iteration 2 (Reflective Agent) enabled in Chainlit UI")
    except Exception as e:
        print(f"⚠️  Could not initialize Iteration 2: {e}")
        print("   Falling back to Iteration 1")
        analyzer = AlignmentAnalyzer()
else:
    analyzer = AlignmentAnalyzer()
    print("📝 Using Iteration 1 (Basic RAG)")

context_manager = ContextManager()

# Initialize LangSmith
langsmith_enabled = init_langsmith()

# Initialize UI components
chat_history = ChatHistory(db)
plan_editor = BusinessPlanEditor(db)
debug_panel = DebugPanel(db)


# ========== Formatting Utilities ==========


def format_alignment_response(result: Any) -> str:
    """Format alignment analysis result as markdown with two-column layout.

    Args:
        result: AlignmentResponse object

    Returns:
        Formatted markdown string with side-by-side layout
    """
    output = [f"# Analysis for {result.company_name}\n"]

    # Create side-by-side content using divs with inline styles
    output.append('<div style="display: flex; gap: 20px; margin-bottom: 20px;">')

    # Strengths column
    output.append('<div style="flex: 1; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f9f9f9;">')
    output.append('')
    output.append('### ✅ Alignment Strengths\n')
    for i, align in enumerate(result.aligns, 1):
        output.append(f'**{i}. {align.title}**\n')
        output.append(f'{align.explanation}\n')
        if align.sources:
            output.append('**Sources:**\n')
            for source in align.sources:
                # Extract a readable part of the URL (path after domain)
                url_display = source.replace('https://', '').replace('http://', '')
                output.append(f'- 🔗 [{url_display}]({source})\n')
        output.append('')
    output.append('</div>')

    # Gaps column
    output.append('<div style="flex: 1; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f9f9f9;">')
    output.append('')
    output.append('### ⚠️ Alignment Gaps\n')
    for i, gap in enumerate(result.gaps, 1):
        output.append(f'**{i}. {gap.title}**\n')
        output.append(f'{gap.explanation}\n')
        if gap.sources:
            output.append('**Sources:**\n')
            for source in gap.sources:
                # Extract a readable part of the URL (path after domain)
                url_display = source.replace('https://', '').replace('http://', '')
                output.append(f'- 🔗 [{url_display}]({source})\n')
        output.append('')
    output.append('</div>')

    output.append('</div>')
    output.append('')
    
    # Add Iteration 2 metadata if available
    if hasattr(result, 'overall_confidence') and result.overall_confidence is not None:
        output.append('---')
        output.append('')
        output.append('## 🔬 Iteration 2: Reflection Metadata\n')
        
        # Overall confidence
        confidence_pct = result.overall_confidence * 100
        confidence_emoji = "🟢" if confidence_pct >= 80 else "🟡" if confidence_pct >= 60 else "🔴"
        output.append(f'**Overall Confidence:** {confidence_emoji} **{confidence_pct:.0f}%**\n')
        
        # Research conducted
        if hasattr(result, 'research_conducted') and result.research_conducted:
            output.append(f'\n**Research Conducted:** {len(result.research_conducted)} searches\n')
            for i, research in enumerate(result.research_conducted[:3], 1):
                output.append(f'{i}. Query: _{research.get("query", "N/A")}_')
                if research.get('gap_addressed'):
                    output.append(f' → {research["gap_addressed"][:50]}...')
                output.append('')
        
        # Data gaps identified
        if hasattr(result, 'data_gaps') and result.data_gaps:
            output.append(f'\n**Information Gaps Identified:** {len(result.data_gaps)}\n')
            for gap in result.data_gaps[:3]:
                output.append(f'- {gap}')
            if len(result.data_gaps) > 3:
                output.append(f'- _...and {len(result.data_gaps) - 3} more_')
            output.append('')
    
    output.append('---')
    output.append('')

    # Add summary below
    output.append('### 📝 Summary\n')
    output.append(result.summary)

    return "\n".join(output)


# ========== Business Plan Management ==========


async def save_business_plan_and_confirm(session_id: str, content: str) -> bool:
    """Save business plan and send confirmation.

    Returns:
        True if saved successfully
    """
    return await plan_editor.save_plan(session_id, content, created_by="user")


# ========== Analysis Pipeline ==========


async def handle_analysis_request(session_id: str, debug_mode: bool):
    """Execute business plan analysis with optional debug info.

    Args:
        session_id: Current session ID
        debug_mode: Whether to show debug information
    """
    # Get current business plan
    plan = db.get_latest_plan(session_id)
    session = db.get_session(session_id)

    if not plan:
        await cl.Message(
            content="⚠️ No business plan found. Please paste your plan in the chat.",
            author="VIRA"
        ).send()
        return

    # Show analysis steps
    async with cl.Step(name="🔍 Analyzing alignment", type="run") as main_step:
        start_time = time.time()

        # Step 1: Retrieval
        async with cl.Step(name="📚 Retrieving VC criteria", parent_id=main_step.id) as retrieve_step:
            retrieval_start = time.time()

            # Generate query from plan
            query = plan.content[:1500]

            retrieval_time = (time.time() - retrieval_start) * 1000
            retrieve_step.output = f"Query prepared from business plan (first 1500 chars)"

        # Step 2: LLM Analysis
        async with cl.Step(name="🤖 Generating alignment analysis", parent_id=main_step.id) as llm_step:
            llm_start = time.time()

            # Run analysis (supports both Iteration 1 and 2)
            analysis_result = analyzer.analyze(
                company_name=session.company_name,
                plan_summary=plan.content,
                query=query
            )
            
            # Handle different return types
            if isinstance(analysis_result, tuple) and len(analysis_result) == 2:
                result, second_value = analysis_result
                # Check if it's Iteration 2 (returns metadata dict) or Iteration 1 (returns docs list)
                if isinstance(second_value, dict):
                    # Iteration 2: metadata dict
                    metadata = second_value
                    retrieved_docs = []  # No direct doc list in Iteration 2
                    llm_step.output = f"Generated {len(result.aligns)} alignments, {len(result.gaps)} gaps (Iteration 2: confidence {metadata.get('overall_confidence', 0):.2f})"
                else:
                    # Iteration 1: docs list
                    retrieved_docs = second_value
                    metadata = {}
                    llm_step.output = f"Generated {len(result.aligns)} alignments, {len(result.gaps)} gaps"
            else:
                # Fallback
                result = analysis_result
                retrieved_docs = []
                metadata = {}
                llm_step.output = f"Generated {len(result.aligns)} alignments, {len(result.gaps)} gaps"

            llm_time = (time.time() - llm_start) * 1000

        total_time = (time.time() - start_time) * 1000

        # Calculate token usage
        input_text = query + "\n".join([doc.page_content for doc in retrieved_docs[:10]])
        output_text = format_alignment_response(result)

        tokens_input = estimate_tokens_accurate(input_text)
        tokens_output = estimate_tokens_accurate(output_text)
        cost = calculate_cost(tokens_input, tokens_output)

        # Format response
        response_content = format_alignment_response(result)

        # Save to database
        message = db.add_message(
            session_id=session_id,
            role="assistant",
            content=response_content,
            metadata={
                "analysis_type": "full",
                "retrieved_docs": len(retrieved_docs),
                "latency_ms": total_time,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "cost": cost,
            }
        )

        # Save analysis metadata
        langsmith_url = get_langsmith_trace_url() if langsmith_enabled else None

        db.save_analysis(
            session_id=session_id,
            message_id=message.id,
            plan_version=plan.version,
            retrieved_docs=len(retrieved_docs),
            tokens_used={
                "input": tokens_input,
                "output": tokens_output,
                "cost": cost,
            },
            latency_ms={
                "retrieval": retrieval_time,
                "llm": llm_time,
                "total": total_time,
            },
            langsmith_trace_url=langsmith_url,
        )

        main_step.output = response_content

    # Send final response
    await cl.Message(content=response_content, author="VIRA").send()

    # Show debug panel if enabled
    if debug_mode:
        await debug_panel.render(
            message_id=message.id,
            latency_ms=total_time,
            retrieved_docs=retrieved_docs,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            langsmith_url=langsmith_url,
        )


# ========== Conversational Interactions ==========


async def handle_conversation(session_id: str, user_message: str, debug_mode: bool):
    """Handle general conversational messages (not analysis).

    Args:
        session_id: Current session ID
        user_message: User's message content
        debug_mode: Debug mode flag
    """
    # Check if user is providing their business plan
    plan = db.get_latest_plan(session_id)

    # Check if user wants to analyze after providing plan
    user_msg_lower = user_message.lower().strip()
    if user_msg_lower in ["yes", "sure", "ok", "okay", "y", "yeah", "yep"]:
        if plan:
            await handle_analysis_request(session_id, debug_mode)
            return
        else:
            response = "I don't have your business plan yet. Please paste it below."
            db.add_message(session_id, role="assistant", content=response)
            await cl.Message(content=response, author="VIRA").send()
            return

    # If no plan exists and message is long, assume it's the business plan
    if not plan and len(user_message) > 100:
        await plan_editor.save_plan(session_id, user_message, created_by="user")
        await cl.Message(
            content="✅ Business plan saved! Type **`yes`** or **`analyze`** to get alignment feedback.",
            author="VIRA"
        ).send()
        return

    # If plan exists and message is long, treat as plan update
    if plan and len(user_message) > 100:
        await plan_editor.save_plan(session_id, user_message, created_by="user")
        await cl.Message(
            content="✅ Business plan updated! Type **`yes`** or **`analyze`** to analyze the new version.",
            author="VIRA"
        ).send()
        return

    # Default response for short messages
    if not plan:
        response = "I'm ready to help! Please share your business plan by pasting it below."
    else:
        response = (
            f"I have your business plan saved. "
            f"Type `analyze` to get alignment feedback, or paste a new version to update it."
        )

    # Save conversation
    db.add_message(session_id, role="assistant", content=response)

    await cl.Message(content=response, author="VIRA").send()


async def handle_command(session_id: str, command: str, args: list[str]) -> bool:
    """Handle slash commands.

    Args:
        session_id: Current session ID
        command: Command name
        args: Command arguments

    Returns:
        True if command was handled
    """
    if command == "sessions":
        await chat_history.render_sidebar(session_id)
        return True

    elif command == "load" and args:
        target_session_id = args[0]
        success = await chat_history.load_session(target_session_id)
        if success:
            # Update current session
            cl.user_session.set("session_id", target_session_id)
        return True

    elif command == "search" and args:
        search_term = " ".join(args)
        await chat_history.search_sessions(search_term)
        return True

    elif command == "versions":
        await plan_editor.show_versions(session_id)
        return True

    elif command == "diff" and len(args) >= 2:
        try:
            v1, v2 = int(args[0]), int(args[1])
            await plan_editor.show_diff(session_id, v1, v2)
        except ValueError:
            await cl.Message(content="⚠️ Usage: `/diff <version1> <version2>`", author="VIRA").send()
        return True

    elif command == "rollback" and args:
        try:
            version = int(args[0])
            await plan_editor.rollback(session_id, version)
        except ValueError:
            await cl.Message(content="⚠️ Usage: `/rollback <version>`", author="VIRA").send()
        return True

    elif command == "editor":
        await plan_editor.render_editor(session_id)
        return True

    elif command == "help":
        await show_help()
        return True

    return False


async def show_help():
    """Show help message with available commands."""
    help_text = """
## 📖 Available Commands

### 🔍 Analysis
- **`analyze`** - Run alignment analysis
- **`yes`** / **`ok`** - Confirm analysis

### 📝 Plan Management  
- **`/versions`** - View version history
- **`/diff <v1> <v2>`** - Compare versions (e.g., `/diff 1 2`)
- **`/rollback <v>`** - Revert to version (e.g., `/rollback 2`)
- **`/editor`** - View plan details

### 📊 Session Management
- **`/sessions`** - View all sessions
- **`/load <id>`** - Load session (e.g., `/load abc123`)
- **`/search <term>`** - Search sessions (e.g., `/search TaskFlow`)

### 💡 Tips
- Paste your business plan to save it automatically
- Toggle **Developer Mode** in settings (⚙️) for metrics
- Long messages (>100 chars) update your plan
"""
    await cl.Message(content=help_text, author="VIRA").send()


# ========== Chainlit Lifecycle Hooks ==========


@cl.on_chat_start
async def start():
    """Initialize chat session on start."""

    # Create settings with debug mode toggle only
    settings_obj = await cl.ChatSettings([
        Switch(id="debug_mode", label="🔧 Developer Mode", initial=False),
    ]).send()

    # Ask for company name OR business plan
    res = await cl.AskUserMessage(
        content=(
            "👋 Hi! I'm VIRA, your VC alignment assistant.\n\n"
            "**Please share:**\n"
            "- Your company name, OR\n"
            "- Paste your full business plan (I'll extract the company name)"
        ),
        timeout=300,
    ).send()

    user_input = res["output"].strip() if res else ""

    # Determine if this is just a name or a full business plan
    if len(user_input) > 150:  # Long input = likely full business plan
        # Extract company name from first line or first few words
        first_line = user_input.split('\n')[0].strip()
        # Try to extract company name (look for common patterns)
        if ':' in first_line:
            company_name = first_line.split(':')[1].strip()
        else:
            # Take first 1-3 words as company name
            words = first_line.split()
            company_name = ' '.join(words[:min(3, len(words))])

        if not company_name or len(company_name) < 2:
            company_name = "Your Company"

        # Create session
        session = db.create_session(company_name=company_name)
        session_id = session.id

        # Save the business plan
        plan = db.save_business_plan(
            session_id=session_id,
            content=user_input,
            created_by="user"
        )

        # Create context
        context_manager.create_context(session_id, session, plan, debug_mode=settings_obj["debug_mode"])

        # Confirm and offer analysis
        await cl.Message(
            content=(
                f"✅ Got it! Business plan saved for **{company_name}**.\n\n"
                f"Type **`yes`** or **`analyze`** to get alignment feedback."
            ),
            author="VIRA",
        ).send()
    else:
        # Short input = just company name
        company_name = user_input if user_input else "Untitled Company"

        # Create session
        session = db.create_session(company_name=company_name)
        session_id = session.id

        # Create context
        context_manager.create_context(session_id, session, None, debug_mode=settings_obj["debug_mode"])

        # Ask for business plan
        await cl.Message(
            content=(
                f"Thanks! I'll help you understand how **{company_name}** aligns with a16z's investment criteria.\n\n"
                f"**Please paste your business plan below:**"
            ),
            author="VIRA",
        ).send()

    # Store in session state
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("analyzer", analyzer)
    cl.user_session.set("debug_mode", settings_obj["debug_mode"])

    # Note: Session history can be viewed with /sessions command


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages."""

    session_id = cl.user_session.get("session_id")
    debug_mode = cl.user_session.get("debug_mode", False)

    if not session_id:
        await cl.Message(content="⚠️ Session not initialized. Please refresh.", author="VIRA").send()
        return

    # Handle file uploads
    if message.elements:
        for element in message.elements:
            if hasattr(element, 'path'):
                await plan_editor.upload_file(session_id, element.path)
                return

    # Save user message
    db.add_message(session_id, role="user", content=message.content)

    # Check for commands
    content = message.content.strip()

    # Check for slash commands
    if content.startswith('/'):
        parts = content[1:].split()
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        if await handle_command(session_id, command, args):
            return

    # Check for analyze command (without slash)
    content_lower = content.lower()
    if content_lower in ["analyze", "analyse"]:
        await handle_analysis_request(session_id, debug_mode)
    else:
        # Handle as regular conversation (might be business plan or follow-up)
        await handle_conversation(session_id, message.content, debug_mode)


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings changes."""

    debug_mode = settings.get("debug_mode", False)
    session_id = cl.user_session.get("session_id")

    cl.user_session.set("debug_mode", debug_mode)

    if session_id:
        context_manager.set_debug_mode(session_id, debug_mode)


if __name__ == "__main__":
    # This file is meant to be run with: chainlit run chainlit_app.py
    pass
