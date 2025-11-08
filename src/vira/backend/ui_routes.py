"""UI-specific API routes for React frontend."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..config.settings import get_settings
from ..rag.pipeline import AlignmentAnalyzer
from ..ui.database.session_manager import SessionManager
from ..ui.utils.token_counter import calculate_cost, estimate_tokens_accurate

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize components
db = SessionManager("./data/vira_sessions.db")

# Initialize analyzer (Iteration 2 if enabled, else Iteration 1)
analyzer_v1 = AlignmentAnalyzer()
analyzer_v2 = None

if settings.enable_reflection:
    try:
        from ..agents.analyzer import ReflectiveAnalyzer
        analyzer_v2 = ReflectiveAnalyzer()
        logger.info("🔬 Iteration 2 (Reflective Agent) enabled in UI routes")
    except Exception as e:
        logger.warning(f"⚠️  Could not initialize Iteration 2: {e}. Using Iteration 1")

analyzer = analyzer_v2 if analyzer_v2 else analyzer_v1

router = APIRouter(prefix="/api", tags=["ui"])


def _format_analysis_message(result: Any, company_name: str, show_reflection_pending: bool = False) -> str:
    """Format analysis result into markdown message content."""
    response_content = f"**Iteration 1 (VC content only): Analysis for {company_name}**\n\n"
    response_content += "**✅ Alignment Strengths**\n\n"
    for i, align in enumerate(result.aligns, 1):
        explanation = align.explanation.replace("VC Criterion:", "**VC Criterion:**").replace("Business Plan:", "**Business Plan:**").replace("Connection:", "**Connection:**")
        response_content += f"**{i}. {align.title}**\n\n{explanation}\n\n"
        if align.sources and len(align.sources) > 0:
            response_content += "*Sources:*\n"
            for source in align.sources:
                response_content += f"- [{source}]({source})\n"
            response_content += "\n"
    
    response_content += "**⚠️ Alignment Gaps**\n\n"
    for i, gap in enumerate(result.gaps, 1):
        explanation = gap.explanation.replace("VC Criterion:", "**VC Criterion:**").replace("Business Plan:", "**Business Plan:**").replace("Connection:", "**Connection:**")
        response_content += f"**{i}. {gap.title}**\n\n{explanation}\n\n"
        if gap.sources and len(gap.sources) > 0:
            response_content += "*Sources:*\n"
            for source in gap.sources:
                response_content += f"- [{source}]({source})\n"
            response_content += "\n"
    
    # Always add Iteration 1 Summary
    response_content += "\n---\n\n"
    response_content += f"**Iteration 1 (VC content only): Summary**\n\n{result.summary}\n\n"
    
    # Add Overall Confidence if available (from Iteration 1 reflection)
    if hasattr(result, 'overall_confidence') and result.overall_confidence is not None:
        conf_pct = result.overall_confidence * 100
        conf_emoji = "🟢" if conf_pct >= 80 else "🟡" if conf_pct >= 60 else "🔴"
        response_content += f"**Overall Confidence:** {conf_emoji} **{conf_pct:.0f}%**\n\n"
    
    if show_reflection_pending:
        # Show Iteration 2 section title immediately (even while waiting)
        response_content += "---\n\n"
        response_content += "**Iteration 2 (Web Research): Reflection Metadata**\n\n"
        response_content += "🔄 *Reflection analysis in progress... This message will update shortly.*\n"
    # For Iteration 2, reflection metadata will be added after this (not here)
    return response_content


def _run_full_analysis_sync(session_id: str, message_id: str, company_name: str, plan_content: str, query: str):
    """Run full analysis (Iteration 1 + Iteration 2) in background thread."""
    import time
    print(f"🚀 [FULL_ANALYSIS] Starting full analysis for message {message_id}, company {company_name}")
    try:
        if not analyzer_v2:
            print(f"❌ [FULL_ANALYSIS] analyzer_v2 is None, cannot run full analysis")
            return
        
        # Step 1: Run Iteration 1 analysis
        print(f"🚀 [FULL_ANALYSIS] Running Iteration 1 analysis...")
        iteration1_start = time.time()
        initial_result, initial_docs = analyzer_v1.analyze(
            company_name=company_name,
            plan_summary=plan_content,
            query=query
        )
        iteration1_time = time.time() - iteration1_start
        print(f"⏱️ [FULL_ANALYSIS] Iteration 1 analysis took {iteration1_time:.2f}s")
        
        # Step 2: Update message with Iteration 1 results
        print(f"🚀 [FULL_ANALYSIS] Updating message with Iteration 1 results...")
        iteration1_content = _format_analysis_message(initial_result, company_name, show_reflection_pending=True)
        db.update_message(message_id, content=iteration1_content)
        print(f"✅ [FULL_ANALYSIS] Updated message with Iteration 1 results")
        
        # Step 3: Run Iteration 2 analysis (reflection + research)
        print(f"🚀 [FULL_ANALYSIS] Running Iteration 2 analysis (reflection + research)...")
        iteration2_start = time.time()
        final_result, metadata = analyzer_v2.analyze(
            company_name=company_name,
            plan_summary=plan_content,
            query=query
        )
        iteration2_time = time.time() - iteration2_start
        print(f"⏱️ [FULL_ANALYSIS] Iteration 2 analysis took {iteration2_time:.2f}s")
        
        # Step 4: Update message with final results
        print(f"🚀 [FULL_ANALYSIS] Updating message with final results...")
        final_content = _format_analysis_message(final_result, company_name, show_reflection_pending=False)
        
        # Add reflection metadata (below the Iteration 1 Summary)
        if final_result.overall_confidence is not None:
            final_content += "\n---\n\n"
            final_content += "**Iteration 2 (Web Research): Reflection Metadata**\n\n"
            final_content += "**Web Research:**\n\n"
            
            if final_result.research_conducted and len(final_result.research_conducted) > 0:
                has_sources = any(r.get('sources') and len(r['sources']) > 0 for r in final_result.research_conducted)
                if has_sources:
                    final_content += f"Conducted {len(final_result.research_conducted)} searches:\n\n"
                    for i, r in enumerate(final_result.research_conducted[:3], 1):
                        # Show category title first
                        category = r.get('gap_addressed', 'Research')
                        if category and len(category) > 100:
                            category = category[:100] + "..."
                        final_content += f"**{i}. {category}**\n\n"
                        final_content += f"Query: *{r.get('query', 'N/A')}*\n"
                        if r.get('sources'):
                            final_content += "Sources:\n"
                            for src in r['sources']:
                                domain = src.replace('https://', '').replace('http://', '').split('/')[0]
                                final_content += f"- [{domain}]({src})\n"
                        final_content += "\n"
                else:
                    final_content += f"ℹ️ *No external sources found.*\n\n"
            else:
                conf_pct = final_result.overall_confidence * 100
                final_content += f"✅ *Not needed.* Confidence ({conf_pct:.0f}%) above threshold.\n\n" if conf_pct >= 70 else f"ℹ️ *None conducted.*\n\n"
            
            if final_result.data_gaps:
                final_content += f"**Information Gaps:** {len(final_result.data_gaps)}\n\n"
                for gap in final_result.data_gaps[:3]:
                    final_content += f"- {gap}\n"
            # Note: Summary is already shown above as "Iteration 1: Summary", so we don't add it here
        
        db.update_message(message_id, content=final_content)
        print(f"✅ [FULL_ANALYSIS] Successfully updated message {message_id} with final analysis")
        logger.info(f"Updated message {message_id} with full analysis (Iteration 1 + Iteration 2)")
    except Exception as e:
        print(f"❌ [FULL_ANALYSIS] Full analysis failed: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Full analysis failed: {e}", exc_info=True)

async def _complete_reflection_async(session_id: str, initial_msg_id: str, company_name: str, plan_content: str, query: str):
    """Run reflection in a separate thread (fire-and-forget)."""
    print(f"🚀 [ASYNC] Scheduling background thread for message {initial_msg_id}")
    import threading
    thread = threading.Thread(target=_run_reflection_sync, args=(session_id, initial_msg_id, company_name, plan_content, query), daemon=True)
    thread.start()
    print(f"✅ [ASYNC] Background thread started for message {initial_msg_id}")

def _run_reflection_sync(session_id: str, initial_msg_id: str, company_name: str, plan_content: str, query: str):
    """Run full reflection/research and update the message (sync)."""
    print(f"🚀 [BACKGROUND] Thread started for message {initial_msg_id}, company {company_name}")
    try:
        if not analyzer_v2:
            print(f"❌ [BACKGROUND] analyzer_v2 is None, cannot run reflection")
            return
        print(f"🚀 [BACKGROUND] Calling analyzer_v2.analyze...")
        result, metadata = analyzer_v2.analyze(company_name=company_name, plan_summary=plan_content, query=query)
        print(f"🚀 [BACKGROUND] Analysis complete, formatting message...")
        content = _format_analysis_message(result, company_name, False)
        
        # Add reflection metadata
        if result.overall_confidence is not None:
            content += "\n---\n\n"
            content += "**Iteration 2 (Web Research): Reflection Metadata**\n\n"
            content += "**Web Research:**\n\n"
            
            if result.research_conducted and len(result.research_conducted) > 0:
                has_sources = any(r.get('sources') and len(r['sources']) > 0 for r in result.research_conducted)
                if has_sources:
                    content += f"Conducted {len(result.research_conducted)} searches:\n\n"
                    for i, r in enumerate(result.research_conducted[:3], 1):
                        # Show category title first
                        category = r.get('gap_addressed', 'Research')
                        if category and len(category) > 100:
                            category = category[:100] + "..."
                        content += f"**{i}. {category}**\n\n"
                        content += f"Query: *{r.get('query', 'N/A')}*\n"
                        if r.get('sources'):
                            content += "Sources:\n"
                            for src in r['sources']:
                                domain = src.replace('https://', '').replace('http://', '').split('/')[0]
                                content += f"- [{domain}]({src})\n"
                        content += "\n"
                else:
                    content += f"ℹ️ *No external sources found.*\n\n"
            else:
                conf_pct = result.overall_confidence * 100
                content += f"✅ *Not needed.* Confidence ({conf_pct:.0f}%) above threshold.\n\n" if conf_pct >= 70 else f"ℹ️ *None conducted.*\n\n"
            
            if result.data_gaps:
                content += f"**Information Gaps:** {len(result.data_gaps)}\n\n"
                for gap in result.data_gaps[:3]:
                    content += f"- {gap}\n"
            
            # Add summary as part of metadata
            content += f"\n**Summary:** {result.summary}\n"
        
        print(f"🚀 [BACKGROUND] Updating message {initial_msg_id}...")
        db.update_message(initial_msg_id, content=content)
        print(f"✅ [BACKGROUND] Successfully updated message {initial_msg_id} with reflection analysis")
        logger.info(f"Updated message {initial_msg_id} with reflection analysis")
    except Exception as e:
        print(f"❌ [BACKGROUND] Background reflection failed: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Background reflection failed: {e}", exc_info=True)

# ===== Request/Response Models =====

class CreateSessionRequest(BaseModel):
    company_name: str

class CreateMessageRequest(BaseModel):
    role: str
    content: str

class SavePlanRequest(BaseModel):
    content: str
    created_by: str = "user"

class RollbackRequest(BaseModel):
    version: int

# ===== Session Endpoints =====

@router.post("/sessions")
async def create_session(req: CreateSessionRequest):
    """Create a new chat session."""
    session = db.create_session(company_name=req.company_name)
    return session.to_dict()

@router.get("/sessions")
async def list_sessions(limit: int = 50):
    """List recent sessions."""
    sessions = db.list_sessions(limit=limit)
    return [s.to_dict() for s in sessions]

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session by ID."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()

@router.get("/sessions/search")
async def search_sessions(term: str):
    """Search sessions by company name."""
    sessions = db.search_sessions(term)
    return [s.to_dict() for s in sessions]

@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, req: dict):
    """Update session fields (status, company_name, etc)."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate status if provided
    if 'status' in req and req['status'] not in ['active', 'archived']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update allowed fields
    update_fields = {}
    if 'status' in req:
        update_fields['status'] = req['status']
    if 'company_name' in req:
        update_fields['company_name'] = req['company_name']
    
    updated = db.update_session(session_id, **update_fields)
    return updated.to_dict()

# ===== Message Endpoints =====

@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Get all messages for a session."""
    messages = db.get_messages(session_id)
    return [m.to_dict() for m in messages]

@router.post("/sessions/{session_id}/messages")
async def create_message(session_id: str, req: CreateMessageRequest):
    """Add a new message to a session."""
    message = db.add_message(
        session_id=session_id,
        role=req.role,
        content=req.content
    )
    return message.to_dict()

# ===== Business Plan Endpoints =====

@router.post("/sessions/{session_id}/plan")
async def save_plan(session_id: str, req: SavePlanRequest):
    """Save a new version of the business plan."""
    plan = db.save_business_plan(
        session_id=session_id,
        content=req.content,
        created_by=req.created_by
    )
    return plan.to_dict()

@router.get("/sessions/{session_id}/plan")
async def get_latest_plan(session_id: str):
    """Get the latest business plan for a session."""
    plan = db.get_latest_plan(session_id)
    if not plan:
        return None
    return plan.to_dict()

@router.get("/sessions/{session_id}/plan/versions")
async def get_plan_versions(session_id: str):
    """Get all versions of the business plan."""
    versions = db.get_plan_versions(session_id)
    return [v.to_dict() for v in versions]

@router.get("/sessions/{session_id}/plan/versions/{version}")
async def get_plan_version(session_id: str, version: int):
    """Get a specific version of the business plan."""
    plan = db.get_plan_by_version(session_id, version)
    if not plan:
        raise HTTPException(status_code=404, detail="Version not found")
    return plan.to_dict()

@router.post("/sessions/{session_id}/plan/rollback")
async def rollback_plan(session_id: str, req: RollbackRequest):
    """Rollback to a specific version."""
    old_plan = db.get_plan_by_version(session_id, req.version)
    if not old_plan:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Create new version with old content
    new_plan = db.save_business_plan(
        session_id=session_id,
        content=old_plan.content,
        created_by="system"
    )
    return new_plan.to_dict()

# ===== Analysis Endpoints =====

@router.post("/sessions/{session_id}/analyze")
async def analyze_plan(session_id: str):
    """Analyze the business plan for a session.
    
    For Iteration 2, this returns immediately with a placeholder message and runs
    both Iteration 1 and Iteration 2 analysis in the background for instant response.
    """
    import time
    start_time = time.time()
    
    # Fast database lookups (should be < 10ms each)
    db_start = time.time()
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session_time = time.time() - db_start
    
    db_start = time.time()
    plan = db.get_latest_plan(session_id)
    if not plan:
        raise HTTPException(status_code=400, detail="No business plan found")
    plan_time = time.time() - db_start
    
    if session_time > 0.05 or plan_time > 0.05:
        print(f"⚠️ Slow DB lookups: session={session_time:.3f}s, plan={plan_time:.3f}s")
    
    # Run analysis
    query = plan.content[:1500]
    
    # Check which analyzer we're using
    if analyzer_v2:
        # Iteration 2: Return immediately, run full analysis in background
        print(f"⏱️ Returning immediately, running analysis in background for {session.company_name}")
        
        # Create placeholder message content (minimal string operations)
        placeholder_content = (
            f"**Iteration 1 (VC content only): Analysis for {session.company_name}**\n\n"
            "**✅ Alignment Strengths**\n\n"
            "*Analysis in progress...*\n\n"
            "**⚠️ Alignment Gaps**\n\n"
            "*Analysis in progress...*\n\n"
            "---\n\n"
            "**Iteration 1 (VC content only): Summary**\n\n"
            "*Analysis in progress...*\n\n"
            "---\n\n"
            "**Iteration 2 (Web Research): Reflection Metadata**\n\n"
            "🔄 *Reflection analysis in progress... This message will update shortly.*\n"
        )
        
        # Save placeholder message (fast DB operation)
        save_start = time.time()
        message = db.add_message(
            session_id=session_id,
            role="assistant",
            content=placeholder_content,
            metadata={
                "analysis_type": "placeholder",
                "retrieved_docs": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "cost": 0,
                "overall_confidence": None,
            }
        )
        save_time = time.time() - save_start
        if save_time > 0.1:
            print(f"⚠️ Message save took {save_time:.3f}s (slow!)")
        
        # Start background thread to run full analysis (non-blocking)
        import threading
        thread = threading.Thread(
            target=_run_full_analysis_sync,
            args=(session_id, message.id, session.company_name, plan.content, query),
            daemon=True
        )
        thread.start()
        
        # Return immediately with placeholder response
        total_time = time.time() - start_time
        print(f"⏱️ Total analyze_plan took {total_time:.3f}s (returning placeholder)")
        
        return {
            "company_name": session.company_name,
            "aligns": [],
            "gaps": [],
            "summary": "Analysis in progress...",
            "overall_confidence": None,
            "research_conducted": None,
            "data_gaps": None,
        }
    else:
        # Iteration 1: Returns (result, docs)
        result, retrieved_docs = analyzer.analyze(
            company_name=session.company_name,
            plan_summary=plan.content,
            query=query
        )
        retrieved_docs_count = len(retrieved_docs)
        metadata = {}
    
    # Calculate tokens and cost
    if analyzer_v2:
        # For Iteration 2, estimate based on result
        input_text = query + plan.content[:1000]
        retrieved_docs = []
    else:
        input_text = query + "\n".join([doc.page_content for doc in retrieved_docs[:10]])
    
    tokens_input = estimate_tokens_accurate(input_text)
    
    output_text = f"{result.summary}\n" + "\n".join([
        f"{a.title}: {a.explanation}" for a in result.aligns + result.gaps
    ])
    tokens_output = estimate_tokens_accurate(output_text)
    cost = calculate_cost(tokens_input, tokens_output)
    
    # Format response - use helper for initial results with pending indicator
    format_start = time.time()
    response_content = _format_analysis_message(result, result.company_name, show_reflection_pending=(analyzer_v2 is not None))
    print(f"⏱️ Message formatting took {time.time() - format_start:.2f}s")
    
    # For Iteration 2, this won't have reflection metadata yet
    # Add it only if this is the full analysis (not initial)
    if analyzer_v2 and result.overall_confidence is not None:
        response_content += "\n---\n\n"
        response_content += "**Iteration 2 (Web Research): Reflection Metadata**\n\n"
        
        # Web Research Section
        response_content += "**Web Research:**\n\n"
        if result.research_conducted and len(result.research_conducted) > 0:
            # Check if any research has sources
            has_sources = any(
                research.get('sources') and len(research['sources']) > 0 
                for research in result.research_conducted
            )
            
            if has_sources:
                response_content += f"Conducted {len(result.research_conducted)} searches to fill information gaps:\n\n"
                for i, research in enumerate(result.research_conducted[:3], 1):
                    # Show category title first
                    category = research.get('gap_addressed', 'Research')
                    if category and len(category) > 100:
                        category = category[:100] + "..."
                    response_content += f"**{i}. {category}**\n\n"
                    response_content += f"Query: *{research.get('query', 'N/A')}*\n"
                    # Display the source links
                    if research.get('sources') and len(research['sources']) > 0:
                        response_content += "Sources:\n"
                        for source in research['sources']:
                            # Extract domain for cleaner display
                            domain = source.replace('https://', '').replace('http://', '').split('/')[0]
                            response_content += f"- [{domain}]({source})\n"
                    response_content += "\n"
            else:
                response_content += f"ℹ️ *No external sources found.* Conducted {len(result.research_conducted)} searches but no relevant external information was available to supplement the VC knowledge base.\n\n"
        else:
            # No research conducted - explain why
            # We're already in a block where result.overall_confidence is not None
            confidence_pct = result.overall_confidence * 100
            if confidence_pct >= 70:
                response_content += f"✅ *Not needed.* Confidence score ({confidence_pct:.0f}%) is above threshold (70%). All necessary information found in VC knowledge base.\n\n"
            else:
                response_content += f"ℹ️ *None conducted.* While confidence is low ({confidence_pct:.0f}%), no information gaps were identified that could be addressed through web research.\n\n"
        
        if result.data_gaps:
            response_content += f"**Information Gaps Identified:** {len(result.data_gaps)}\n\n"
            for gap in result.data_gaps[:3]:
                response_content += f"- {gap}\n"
            if len(result.data_gaps) > 3:
                response_content += f"- *...and {len(result.data_gaps) - 3} more*\n"
            response_content += "\n"
        
        # Add summary as part of metadata
        response_content += f"**Summary:** {result.summary}\n"
        
        response_content += "---\n\n"
    # Note: Summary is already included in Iteration 2 metadata above, or in Iteration 1 via _format_analysis_message
    
    # Save message
    save_start = time.time()
    message = db.add_message(
        session_id=session_id,
        role="assistant",
        content=response_content,
        metadata={
            "analysis_type": "initial" if (analyzer_v2 and not hasattr(result, 'overall_confidence')) else "full",
            "retrieved_docs": retrieved_docs_count,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost": cost,
            "overall_confidence": result.overall_confidence if hasattr(result, 'overall_confidence') else None,
        }
    )
    print(f"⏱️ Message save took {time.time() - save_start:.2f}s")
    
    # For Iteration 2, trigger background reflection/research after returning initial results
    has_conf = hasattr(result, 'overall_confidence') and result.overall_confidence is not None
    if analyzer_v2 and not has_conf:
        # Start background thread directly (fire-and-forget)
        print(f"🚀 [ANALYZE] Scheduling background reflection for message {message.id}")
        import threading
        thread = threading.Thread(
            target=_run_reflection_sync,
            args=(session_id, message.id, session.company_name, plan.content, query),
            daemon=True
        )
        thread.start()
        print(f"✅ [ANALYZE] Background thread started for message {message.id}")
        logger.info(f"Scheduled background reflection for session {session_id}")
    
    # Save analysis metadata
    import time
    db.save_analysis(
        session_id=session_id,
        message_id=message.id,
        plan_version=plan.version,
        retrieved_docs=retrieved_docs_count,
        tokens_used={
            "input": tokens_input,
            "output": tokens_output,
            "cost": cost,
        },
        latency_ms={
            "retrieval": 0,  # TODO: Track actual timing
            "llm": 0,
            "total": 0,
        },
        langsmith_trace_url=None,
    )
    
    # Return structured response with Iteration 2 fields
    response_data = {
        "company_name": result.company_name,
        "aligns": [
            {
                "title": a.title,
                "explanation": a.explanation,
                "sources": a.sources,
                "confidence": getattr(a, 'confidence', None),
                "evidence_quality": getattr(a, 'evidence_quality', None),
            } for a in result.aligns
        ],
        "gaps": [
            {
                "title": g.title,
                "explanation": g.explanation,
                "sources": g.sources,
                "confidence": getattr(g, 'confidence', None),
                "evidence_quality": getattr(g, 'evidence_quality', None),
            } for g in result.gaps
        ],
        "summary": result.summary,
    }
    
    # Add Iteration 2 fields
    if hasattr(result, 'overall_confidence'):
        response_data["overall_confidence"] = result.overall_confidence
    if hasattr(result, 'research_conducted'):
        response_data["research_conducted"] = result.research_conducted
    if hasattr(result, 'data_gaps'):
        response_data["data_gaps"] = result.data_gaps
    
    total_time = time.time() - start_time
    print(f"⏱️ Total analyze_plan took {total_time:.2f}s (returning to client)")
    return response_data

@router.get("/analyses/{message_id}")
async def get_analysis(message_id: str):
    """Get analysis metadata for a message."""
    analysis = db.get_analysis(message_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis.to_dict()

# ===== WebSocket Endpoint =====

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now - extend later for real-time analysis progress
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

