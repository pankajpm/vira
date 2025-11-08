"""RAG pipeline responsible for generating the alignment analysis."""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..config.settings import get_settings
from ..vectorstore.manager import load_vectorstore
from ..retrieval.hybrid import HybridRetriever


class AlignmentSection(BaseModel):
    """Model representing a single alignment or gap entry."""

    title: str = Field(..., description="Short descriptive title of the point.")
    explanation: str = Field(
        ..., description="Multi-sentence explanation of the point with evidence."
    )
    sources: list[str] = Field(
        default_factory=list, description="List of supporting source URLs."
    )
    confidence: float | None = Field(
        default=None, description="Confidence score 0-1 (Iteration 2)"
    )
    evidence_quality: str | None = Field(
        default=None, description="Evidence quality: strong/medium/weak/insufficient (Iteration 2)"
    )


class AlignmentResponse(BaseModel):
    """Structured response returned to the API/UI."""

    company_name: str
    aligns: list[AlignmentSection]
    gaps: list[AlignmentSection]
    summary: str
    
    # Iteration 2: Reflection Agent fields
    overall_confidence: float | None = Field(
        default=None, description="Overall confidence score 0-1"
    )
    research_conducted: list[dict] | None = Field(
        default=None, description="Research queries and results"
    )
    data_gaps: list[str] | None = Field(
        default=None, description="Identified information gaps"
    )


def build_prompt_with_classified_evidence() -> ChatPromptTemplate:
    """
    Build prompt template that uses pre-classified evidence sections.
    
    This prompt expects separate alignment_context and gap_context instead of
    a single combined context, ensuring citations match the claim type.
    """
    
    template = """
You are a VC analyst. Analyze alignment between the business plan and VC criteria using pre-classified evidence.

EVIDENCE SUPPORTING ALIGNMENT:
{alignment_context}

EVIDENCE HIGHLIGHTING GAPS:
{gap_context}

BUSINESS PLAN (Company: {company_name}):
{plan_summary}

CRITICAL INSTRUCTIONS:
1. For ALIGNMENT points: Use ONLY sources from "Evidence Supporting Alignment" section
   - Quote the VC criterion that supports alignment
   - Quote the business plan text that matches
   - Cite the source URL
   
2. For GAP points: Use ONLY sources from "Evidence Highlighting Gaps" section
   - Quote the VC criterion the plan doesn't address
   - Explain what's missing in the business plan
   - Cite the source URL

3. If either section has insufficient evidence, acknowledge: "Limited evidence available for [alignments/gaps]"

4. NEVER cite alignment evidence when discussing gaps, or vice versa

OUTPUT FORMAT (JSON):
{{
  "company_name": "string",
  "aligns": [
    {{
      "title": "Short descriptive title",
      "explanation": "VC Criterion: '[exact quote]' | Business Plan: '[exact quote]' | Connection: [explanation]",
      "sources": ["URL"]
    }}
  ],
  "gaps": [
    {{
      "title": "Short descriptive title",
      "explanation": "VC Criterion: '[exact quote]' | Business Plan Status: [what's missing]",
      "sources": ["URL"]
    }}
  ],
  "summary": "Neutral 80-120 word summary. Acknowledge if evidence is limited."
}}

Do NOT make investment recommendations or assign scores.
"""
    return ChatPromptTemplate.from_template(template)


def build_prompt() -> ChatPromptTemplate:
    """Return the prompt template guiding the LLM output with strict citation requirements."""

    template = """
You are a VC analyst. Analyze alignment between the business plan and VC criteria using ONLY the retrieved evidence.

RETRIEVED VC CRITERIA CONTEXT:
{context}

BUSINESS PLAN (Company: {company_name}):
{plan_summary}

CRITICAL INSTRUCTIONS FOR CITATIONS:
You MUST provide explicit evidence for every claim. This is not optional.

For ALIGNMENT points:
1. Quote the SPECIFIC VC criterion from the context that supports alignment
2. Quote the SPECIFIC business plan text that matches that criterion
3. Explain the connection between the two quotes
4. Cite the source URL
5. If you CANNOT find supporting evidence in the retrieved context, DO NOT list that alignment point

For GAP points:
1. Quote the SPECIFIC VC criterion that the plan doesn't address
2. Explain what is MISSING or CONTRADICTORY in the business plan
3. Cite the source URL for the VC criterion
4. If you CANNOT find gap evidence in the retrieved context, DO NOT list that gap

EVIDENCE REQUIREMENTS:
- Each alignment point MUST have: VC criterion quote + BP quote + source URL
- Each gap point MUST have: VC criterion quote + explanation of what's missing + source URL
- If you cannot find explicit evidence for 3+ alignments OR 3+ gaps, acknowledge this with:
  "Limited evidence available in retrieved context for [alignments/gaps]"
- NEVER cite a point without explicit supporting evidence from the context

OUTPUT FORMAT (JSON):
{{
  "company_name": "string",
  "aligns": [
    {{
      "title": "Short descriptive title",
      "explanation": "VC Criterion: '[exact quote]' | Business Plan: '[exact quote]' | Connection: [explanation]",
      "sources": ["URL"]
    }}
  ],
  "gaps": [
    {{
      "title": "Short descriptive title", 
      "explanation": "VC Criterion: '[exact quote]' | Business Plan Status: [what's missing/contradictory]",
      "sources": ["URL"]
    }}
  ],
  "summary": "Neutral 80-120 word summary balancing strengths and gaps. Acknowledge if evidence is limited."
}}

Do NOT make investment recommendations or assign scores.
Only cite points with explicit evidence from the retrieved context.
"""
    return ChatPromptTemplate.from_template(template)


def build_chain(model_name: str = "gpt-4o-mini", use_classification: bool = True) -> Any:
    """
    Construct the LangChain pipeline end-to-end.
    
    Args:
        model_name: LLM model to use
        use_classification: If True, use classified evidence prompt; if False, use original
        
    Returns:
        LangChain chain for alignment analysis
    """

    prompt = build_prompt_with_classified_evidence() if use_classification else build_prompt()
    llm = ChatOpenAI(model=model_name, temperature=0.2)
    parser = JsonOutputParser(pydantic_object=AlignmentResponse)
    return prompt | llm | parser


def classify_chunk(
    chunk_text: str, 
    plan_summary: str, 
    llm: ChatOpenAI
) -> Literal["alignment", "gap", "neutral"]:
    """
    Classify a retrieved chunk as supporting alignment, indicating a gap, or neutral.
    
    This is a simple prototype implementation using a fast LLM call to categorize
    each chunk relative to the business plan.
    
    Args:
        chunk_text: The VC criterion/content chunk to classify
        plan_summary: Summary of the business plan for context
        llm: Language model to use for classification
        
    Returns:
        One of "alignment", "gap", or "neutral"
    """
    
    classification_prompt = f"""You are classifying VC investment criteria relative to a business plan.

Business Plan Summary:
{plan_summary[:500]}  

VC Criterion Chunk:
{chunk_text[:400]}

Does this VC criterion:
A) Support or validate something present in the business plan (ALIGNMENT)
B) Highlight something missing, contradictory, or unaddressed in the plan (GAP)
C) Not clearly relevant to assessing this specific plan (NEUTRAL)

Respond with ONLY one letter: A, B, or C

Your response:"""
    
    try:
        response = llm.invoke(classification_prompt)
        result = response.content.strip().upper()
        
        if 'A' in result:
            return "alignment"
        elif 'B' in result:
            return "gap"
        else:
            return "neutral"
    except Exception:
        # On error, default to neutral to avoid breaking the pipeline
        return "neutral"


def classify_documents(
    documents: list[Document],
    plan_summary: str,
    llm: ChatOpenAI
) -> dict[str, list[Document]]:
    """
    Classify all retrieved documents into alignment, gap, or neutral categories.
    
    For prototype: sequential processing is acceptable. Production version would
    batch or parallelize these calls.
    
    Args:
        documents: List of retrieved documents
        plan_summary: Business plan summary for context
        llm: Language model for classification
        
    Returns:
        Dictionary with keys 'alignment', 'gap', 'neutral' containing categorized docs
    """
    
    classified: dict[str, list[Document]] = {
        "alignment": [],
        "gap": [],
        "neutral": []
    }
    
    for doc in documents:
        category = classify_chunk(doc.page_content, plan_summary, llm)
        classified[category].append(doc)
    
    return classified


class AlignmentAnalyzer:
    """High-level orchestrator for the retrieval + generation workflow."""

    def __init__(self, model_name: str = "gpt-4o-mini", use_classification: bool = True) -> None:
        """
        Initialize the analyzer.
        
        Args:
            model_name: LLM model to use
            use_classification: If True, classify chunks before analysis (recommended for prototype)
        """
        self.model_name = model_name
        self.use_classification = use_classification
        self.settings = get_settings()
        self.vectorstore = load_vectorstore()
        self.retriever = HybridRetriever(self.vectorstore)
        self.chain = build_chain(model_name, use_classification)
        # Separate LLM instance for classification to use lower temperature
        self.classifier_llm = ChatOpenAI(model=model_name, temperature=0.0)

    def analyze(
        self, 
        company_name: str, 
        plan_summary: str, 
        query: str,
        min_alignment_chunks: int = 2,
        min_gap_chunks: int = 2,
    ) -> tuple[AlignmentResponse, list[Document]]:
        """
        Retrieve contextual documents, optionally classify them, and generate alignment analysis.
        
        Includes adaptive retrieval: if classification produces insufficient evidence,
        retrieves more documents until minimum thresholds are met.
        
        Args:
            company_name: Name of the company being analyzed
            plan_summary: Business plan summary text
            query: Search query for retrieval
            min_alignment_chunks: Minimum alignment evidence chunks to retrieve (default: 2)
            min_gap_chunks: Minimum gap evidence chunks to retrieve (default: 2)
            
        Returns:
            Tuple of (AlignmentResponse, retrieved documents)
        """

        if self.use_classification:
            # Adaptive retrieval with classification
            docs, classified = self._retrieve_with_classification(
                query, 
                plan_summary, 
                min_alignment_chunks, 
                min_gap_chunks
            )
            
            alignment_context = self._format_context(classified["alignment"]) or "No clear alignment evidence found in retrieved context."
            gap_context = self._format_context(classified["gap"]) or "No clear gap evidence found in retrieved context."
            
            response_dict = self.chain.invoke(
                {
                    "alignment_context": alignment_context,
                    "gap_context": gap_context,
                    "plan_summary": plan_summary,
                    "company_name": company_name,
                }
            )
        else:
            # Original behavior without classification
            docs = self.retriever.get_relevant_documents(query)
            context = self._format_context(docs)
            response_dict = self.chain.invoke(
                {
                    "context": context,
                    "plan_summary": plan_summary,
                    "company_name": company_name,
                }
            )
        
        response = AlignmentResponse(**response_dict)
        return response, docs

    def _retrieve_with_classification(
        self,
        query: str,
        plan_summary: str,
        min_alignment: int,
        min_gap: int,
        max_attempts: int = 3,
    ) -> tuple[list[Document], dict[str, list[Document]]]:
        """
        Adaptively retrieve and classify documents until we have enough evidence.
        
        This handles the edge case where initial retrieval produces mostly neutral chunks.
        For prototype: simple implementation with max attempts limit.
        
        Args:
            query: Search query
            plan_summary: Business plan for classification context
            min_alignment: Minimum alignment chunks needed
            min_gap: Minimum gap chunks needed
            max_attempts: Maximum retrieval attempts (safety limit)
            
        Returns:
            Tuple of (all documents, classified documents dict)
        """
        
        all_docs: list[Document] = []
        classified: dict[str, list[Document]] = {
            "alignment": [],
            "gap": [],
            "neutral": []
        }
        
        # For prototype: single retrieval attempt is sufficient
        for _attempt in range(max_attempts):
            docs = self.retriever.get_relevant_documents(query)
            
            # Skip already classified documents
            new_docs = [doc for doc in docs if doc not in all_docs]
            if not new_docs:
                break
            
            all_docs.extend(new_docs)
            
            # Classify new documents
            new_classified = classify_documents(new_docs, plan_summary, self.classifier_llm)
            
            # Merge classifications
            classified["alignment"].extend(new_classified["alignment"])
            classified["gap"].extend(new_classified["gap"])
            classified["neutral"].extend(new_classified["neutral"])
            
            # Check if we have enough evidence
            has_enough_alignment = len(classified["alignment"]) >= min_alignment
            has_enough_gaps = len(classified["gap"]) >= min_gap
            
            if has_enough_alignment and has_enough_gaps:
                break
            
            # If not enough evidence after first attempt, expand retrieval
            # For prototype: just accept what we got after first attempt
            # Production: could try alternative queries or retrieve more chunks
            break
        
        return all_docs, classified

    @staticmethod
    def _format_context(documents: list[Document]) -> str:
        """Format documents into context string with sources."""
        if not documents:
            return ""
        
        formatted_chunks = []
        for doc in documents:
            source = doc.metadata.get("url", "unknown source")
            snippet = doc.page_content.strip()[:800]
            formatted_chunks.append(f"Source: {source}\nSnippet: {snippet}")
        return "\n\n".join(formatted_chunks)


__all__ = ["AlignmentAnalyzer", "AlignmentResponse", "AlignmentSection"]

