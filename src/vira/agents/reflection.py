"""Reflection agent for meta-assessment of alignment analysis quality.

This module implements the reflection agent that:
- Assesses confidence in each alignment/gap claim
- Grades evidence quality (strong/medium/weak/insufficient)
- Identifies information gaps
- Triggers research when confidence is below threshold
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from ..rag.pipeline import AlignmentResponse
from .state import InformationGap, ReflectionResult


def assess_claim_confidence(
    claim_text: str, evidence_text: str, llm: ChatOpenAI
) -> tuple[float, str]:
    """Assess confidence in a single alignment or gap claim.

    Args:
        claim_text: The alignment or gap claim
        evidence_text: Supporting evidence from retrieved documents
        llm: Language model for assessment

    Returns:
        Tuple of (confidence_score, reasoning)
        confidence_score: 0.0-1.0, where:
            - 0.8-1.0: Strong (explicit statement with multiple sources)
            - 0.6-0.8: Medium (clear inference from source)
            - 0.4-0.6: Weak (single ambiguous reference)
            - 0.0-0.4: Insufficient (no clear evidence)
    """
    prompt = f"""You are assessing the confidence/evidence quality of an alignment or gap claim.

CLAIM:
{claim_text}

EVIDENCE:
{evidence_text}

Assess the evidence quality and assign a confidence score:

**0.9-1.0 (Strong ✓✓✓)**: Explicit statement with multiple clear sources
- Direct quotes from 2+ sources explicitly supporting the claim
- No ambiguity, very clear connection

**0.7-0.85 (Medium-Strong ✓✓)**: Clear evidence from reliable source
- Direct quote from 1 source or multiple indirect signals
- Clear inference with minimal ambiguity

**0.5-0.65 (Weak ✓)**: Limited or indirect evidence
- Single vague reference or weak inference
- Some supporting signals but incomplete

**0.0-0.45 (Insufficient ?)**: No clear evidence
- Claim lacks supporting evidence in retrieved content
- Speculative or unsupported assertion

Respond with ONLY a JSON object:
{{
  "score": <float 0-1>,
  "reasoning": "<2-3 sentence explanation>"
}}
"""
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse JSON response
        import json
        if content.startswith("```"):
            # Remove code fence if present
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content)
        score = float(result["score"])
        reasoning = result["reasoning"]
        
        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))
        
        return score, reasoning
        
    except Exception as e:
        # Fallback: return medium confidence if parsing fails
        return 0.6, f"Error assessing confidence: {str(e)}"


def identify_information_gaps(
    explanation: AlignmentResponse, reflection_confidence: dict[str, float]
) -> list[InformationGap]:
    """Identify gaps in information based on low-confidence claims.

    Args:
        explanation: The alignment analysis
        reflection_confidence: Per-claim confidence scores

    Returns:
        List of prioritized information gaps
    """
    gaps: list[InformationGap] = []
    
    # Low confidence threshold for triggering gap identification
    LOW_CONFIDENCE_THRESHOLD = 0.65
    
    # Analyze alignment claims
    for i, align in enumerate(explanation.aligns):
        claim_id = f"align_{i}"
        confidence = reflection_confidence.get(claim_id, 0.7)
        
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            # Try to categorize the gap based on claim title/explanation
            category = _categorize_gap(align.title, align.explanation)
            
            gap = InformationGap(
                category=category,
                description=f"Insufficient evidence for alignment claim: {align.title}",
                priority=1 if confidence < 0.5 else 2,
                claim_id=claim_id,
            )
            gaps.append(gap)
    
    # Analyze gap claims
    for i, gap_claim in enumerate(explanation.gaps):
        claim_id = f"gap_{i}"
        confidence = reflection_confidence.get(claim_id, 0.7)
        
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            category = _categorize_gap(gap_claim.title, gap_claim.explanation)
            
            gap = InformationGap(
                category=category,
                description=f"Insufficient evidence for gap claim: {gap_claim.title}",
                priority=1 if confidence < 0.5 else 2,
                claim_id=claim_id,
            )
            gaps.append(gap)
    
    # Sort by priority
    gaps.sort(key=lambda g: g.priority)
    
    return gaps


def _categorize_gap(title: str, explanation: str) -> str:
    """Categorize an information gap based on claim text.
    
    Returns:
        One of: team_info, market_data, competitive_landscape, vc_preferences
    """
    text = (title + " " + explanation).lower()
    
    # Simple keyword-based categorization
    if any(word in text for word in ["team", "founder", "ceo", "cto", "experience", "background"]):
        return "team_info"
    elif any(word in text for word in ["market", "tam", "growth", "size", "opportunity"]):
        return "market_data"
    elif any(word in text for word in ["competitor", "competitive", "landscape", "similar", "alternative"]):
        return "competitive_landscape"
    elif any(word in text for word in ["vc", "investment", "thesis", "portfolio", "preference", "focus"]):
        return "vc_preferences"
    else:
        # Default to market data
        return "market_data"


def reflect_on_explanation(
    explanation: AlignmentResponse, retrieved_docs: list, llm: ChatOpenAI
) -> ReflectionResult:
    """Perform meta-assessment of alignment explanation quality.

    This is the main reflection function that:
    1. Assesses confidence for each alignment/gap claim
    2. Calculates overall confidence
    3. Identifies information gaps
    4. Returns structured reflection results

    Args:
        explanation: Initial alignment analysis from Iteration 1 pipeline
        retrieved_docs: Documents used to generate the explanation
        llm: Language model for reflection

    Returns:
        ReflectionResult with confidence scores and identified gaps
    """
    # Build evidence context from retrieved documents
    evidence_context = _build_evidence_context(retrieved_docs)
    
    per_claim_confidence: dict[str, float] = {}
    confidence_reasonings: list[str] = []
    
    # Assess each alignment claim
    for i, align in enumerate(explanation.aligns):
        claim_id = f"align_{i}"
        claim_text = f"{align.title}: {align.explanation}"
        
        score, reasoning = assess_claim_confidence(claim_text, evidence_context, llm)
        per_claim_confidence[claim_id] = score
        confidence_reasonings.append(f"{claim_id}: {reasoning}")
    
    # Assess each gap claim
    for i, gap in enumerate(explanation.gaps):
        claim_id = f"gap_{i}"
        claim_text = f"{gap.title}: {gap.explanation}"
        
        score, reasoning = assess_claim_confidence(claim_text, evidence_context, llm)
        per_claim_confidence[claim_id] = score
        confidence_reasonings.append(f"{claim_id}: {reasoning}")
    
    # Calculate overall confidence (weighted average)
    if per_claim_confidence:
        overall_confidence = sum(per_claim_confidence.values()) / len(per_claim_confidence)
    else:
        overall_confidence = 0.7  # Default if no claims
    
    # Identify information gaps for low-confidence claims
    information_gaps = identify_information_gaps(explanation, per_claim_confidence)
    
    # Build reasoning summary
    reasoning = f"""Reflection Summary:
- Total claims assessed: {len(per_claim_confidence)}
- Overall confidence: {overall_confidence:.2f}
- Information gaps identified: {len(information_gaps)}

Confidence breakdown:
{chr(10).join(confidence_reasonings[:5])}  # Show first 5
"""
    
    return ReflectionResult(
        overall_confidence=overall_confidence,
        per_claim_confidence=per_claim_confidence,
        information_gaps=information_gaps,
        reasoning=reasoning,
    )


def _build_evidence_context(retrieved_docs: list) -> str:
    """Build evidence context string from retrieved documents.
    
    Args:
        retrieved_docs: List of Document objects or similar
        
    Returns:
        Formatted evidence string
    """
    if not retrieved_docs:
        return "No evidence available."
    
    evidence_parts = []
    for i, doc in enumerate(retrieved_docs[:10]):  # Limit to first 10 docs
        if hasattr(doc, 'page_content'):
            content = doc.page_content[:400]  # Truncate long content
        else:
            content = str(doc)[:400]
        
        source = ""
        if hasattr(doc, 'metadata') and doc.metadata:
            source = doc.metadata.get('url', doc.metadata.get('source', ''))
        
        evidence_parts.append(f"[Doc {i+1}] {content}\nSource: {source}\n")
    
    return "\n".join(evidence_parts)


__all__ = [
    "assess_claim_confidence",
    "identify_information_gaps",
    "reflect_on_explanation",
]

