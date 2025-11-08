"""Research agent for autonomous gap-filling via web search.

This module implements the research agent that:
- Generates optimized search queries from information gaps
- Executes web searches via Serper API
- Parses and filters search results
- Manages research budget (max 5 queries per analysis)
"""

from __future__ import annotations

from typing import Any

from ..config.settings import get_settings
from .state import InformationGap, ResearchResult


class WebSearchTool:
    """Web search integration using Serper API (Google Search)."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize web search tool.

        Args:
            api_key: Serper API key (optional, defaults to settings)
        """
        settings = get_settings()
        self.api_key = api_key or settings.serper_api_key
        if not self.api_key:
            raise ValueError("Serper API key not provided and not found in settings")

    def search(self, query: str, num_results: int = 5) -> list[dict[str, Any]]:
        """Execute web search query.

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            List of search results with 'title', 'snippet', 'link' keys
        """
        import requests
        
        url = "https://google.serper.dev/search"
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract organic results
            results = []
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Search API error: {e}")
            return []
        except Exception as e:
            print(f"   ⚠️  Unexpected error in search: {e}")
            return []


def generate_baseline_queries(company_name: str, plan_summary: str = "") -> list[str]:
    """Generate 3 core baseline research queries from business plan.
    
    These queries are always run to provide external validation:
    1. Market/Industry Validation
    2. Competitive Landscape
    3. VC Alignment/Investment Thesis
    
    Args:
        company_name: Company name
        plan_summary: Business plan text to extract industry/business model from
        
    Returns:
        List of exactly 3 search query strings
    """
    queries: list[str] = []
    
    # Extract industry and business model keywords from plan
    plan_lower = plan_summary.lower() if plan_summary else ""
    
    # Common industry keywords
    industry_keywords = []
    if any(kw in plan_lower for kw in ["ai", "artificial intelligence", "machine learning", "ml"]):
        industry_keywords.append("AI artificial intelligence")
    elif any(kw in plan_lower for kw in ["saas", "software as a service", "software"]):
        industry_keywords.append("SaaS software")
    elif any(kw in plan_lower for kw in ["healthcare", "health care", "medical"]):
        industry_keywords.append("healthcare medical")
    elif any(kw in plan_lower for kw in ["fintech", "financial technology", "finance", "banking"]):
        industry_keywords.append("fintech financial")
    elif any(kw in plan_lower for kw in ["e-commerce", "ecommerce", "retail"]):
        industry_keywords.append("e-commerce retail")
    elif any(kw in plan_lower for kw in ["marketplace", "platform"]):
        industry_keywords.append("marketplace platform")
    else:
        # Fallback: use first few words from plan or company name
        industry_keywords.append("industry")
    
    industry_term = industry_keywords[0] if industry_keywords else "industry"
    
    # Extract business model
    business_model = ""
    if any(kw in plan_lower for kw in ["b2b", "b to b", "business to business", "enterprise"]):
        business_model = "B2B enterprise"
    elif any(kw in plan_lower for kw in ["b2c", "b to c", "business to consumer", "consumer"]):
        business_model = "B2C consumer"
    elif "marketplace" in plan_lower:
        business_model = "marketplace"
    elif "platform" in plan_lower:
        business_model = "platform"
    
    # Query 1: Market/Industry Validation
    if industry_term != "industry":
        query1 = f"{company_name} {industry_term} market size growth"
    else:
        query1 = f"{company_name} industry market size"
    queries.append(query1)
    
    # Query 2: Competitive Landscape
    query2 = f"{company_name} competitors similar companies funding"
    queries.append(query2)
    
    # Query 3: VC Alignment/Investment Thesis
    if business_model and industry_term != "industry":
        query3 = f"{industry_term} {business_model} venture capital investment criteria"
    elif industry_term != "industry":
        query3 = f"{industry_term} venture capital investment criteria"
    else:
        query3 = f"{company_name} VC investment fit"
    queries.append(query3)
    
    return queries[:3]  # Ensure exactly 3 queries


def generate_research_queries(gaps: list[InformationGap], company_name: str = "") -> list[str]:
    """Generate optimized search queries from information gaps.

    Query templates by gap type:
    - team_info: "{founder name} LinkedIn experience", "{CTO name} background"
    - market_data: "{industry} market size TAM", "{sector} growth rate"
    - competitive: "{company name} competitors funding", "{space} similar companies"
    - vc_preferences: "{VC name} investment thesis", "{VC name} portfolio {sector}"

    Args:
        gaps: List of information gaps from reflection
        company_name: Company name to include in queries

    Returns:
        List of search query strings, prioritized by gap importance
    """
    queries: list[str] = []
    
    for gap in gaps:
        # Extract key terms from gap description
        description = gap.description.lower()
        
        if gap.category == "team_info":
            if "founder" in description or "ceo" in description:
                queries.append(f"{company_name} CEO founder background LinkedIn")
            if "team" in description or "experience" in description:
                queries.append(f"{company_name} founding team experience")
                
        elif gap.category == "market_data":
            if "market" in description or "tam" in description:
                queries.append(f"{company_name} target market size TAM")
            if "growth" in description:
                queries.append(f"{company_name} industry market growth rate")
                
        elif gap.category == "competitive_landscape":
            queries.append(f"{company_name} competitors funding")
            queries.append(f"{company_name} similar companies space")
            
        elif gap.category == "vc_preferences":
            # Extract VC name if mentioned
            if "a16z" in description or "andreessen" in description:
                queries.append("a16z investment thesis criteria")
                queries.append("a16z portfolio companies")
            else:
                queries.append("venture capital investment criteria")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    return unique_queries


def parse_search_results(
    query: str, raw_results: list[dict[str, Any]], gap_description: str = ""
) -> ResearchResult:
    """Parse and filter search results into structured format.

    Args:
        query: The search query used
        raw_results: Raw search results from Serper API
        gap_description: Description of the gap being addressed

    Returns:
        Parsed ResearchResult with relevant snippets and sources
    """
    snippets: list[str] = []
    sources: list[str] = []
    
    for result in raw_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        
        if snippet:
            # Format: [Title] Snippet
            formatted = f"[{title}] {snippet}"
            snippets.append(formatted)
            sources.append(link)
    
    return ResearchResult(
        query=query,
        snippets=snippets,
        sources=sources,
        gap_addressed=gap_description
    )


def conduct_research(
    gaps: list[InformationGap], 
    company_name: str = "", 
    max_queries: int = 5,
    baseline_mode: bool = False,
    plan_summary: str = ""
) -> list[ResearchResult]:
    """Conduct research to fill information gaps or run baseline research.

    This is the main research orchestration function that:
    1. Generates search queries (from gaps or baseline)
    2. Executes searches within budget
    3. Parses and structures results
    4. Returns research findings

    Args:
        gaps: Information gaps from reflection agent (ignored if baseline_mode=True)
        company_name: Company name for query generation
        max_queries: Maximum number of search queries to execute
        baseline_mode: If True, run baseline research (3 queries) instead of gap-driven
        plan_summary: Business plan text for baseline query generation

    Returns:
        List of research results
    """
    # Baseline research: always run 3 core queries
    if baseline_mode:
        queries = generate_baseline_queries(company_name, plan_summary)
        print(f"   🔍 Generated {len(queries)} baseline research queries")
    else:
        # Gap-driven research
        if not gaps:
            print("   ℹ️  No gaps to research")
            return []
        
        # Generate queries from gaps
        queries = generate_research_queries(gaps, company_name)
        
        # Limit to budget
        queries = queries[:max_queries]
        
        if not queries:
            print("   ⚠️  No queries generated from gaps")
            return []
        
        print(f"   🔍 Generated {len(queries)} gap-driven research queries")
    
    # Initialize search tool
    try:
        search_tool = WebSearchTool()
    except ValueError as e:
        print(f"   ⚠️  Cannot initialize search: {e}")
        return []
    
    # Execute searches in parallel for better performance
    results: list[ResearchResult] = []
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def search_and_parse(query_info: tuple[int, str]) -> tuple[int, ResearchResult | None]:
        """Execute a single search query and parse results."""
        i, query = query_info
        print(f"   🔎 Query {i}/{len(queries)}: {query}")
        
        try:
            raw_results = search_tool.search(query, num_results=3)
            
            if raw_results:
                # Find the gap this query addresses (only for gap-driven research)
                gap_description = ""
                if not baseline_mode and gaps:
                    for gap in gaps:
                        if any(keyword in query.lower() for keyword in gap.category.split("_")):
                            gap_description = gap.description
                            break
                else:
                    # For baseline queries, use query type as description
                    if "market" in query.lower() or "industry" in query.lower():
                        gap_description = "Market/Industry Validation"
                    elif "competitor" in query.lower() or "similar" in query.lower():
                        gap_description = "Competitive Landscape Analysis"
                    elif ("VC" in query or "venture capital" in query.lower() or 
                          "investment" in query.lower()):
                        gap_description = "VC Alignment & Investment Thesis"
                
                parsed = parse_search_results(query, raw_results, gap_description)
                print(f"      ✓ Found {len(raw_results)} results")
                return (i, parsed)
            else:
                print("      ⚠️  No results")
                return (i, None)
                
        except Exception as e:
            print(f"      ⚠️  Error: {e}")
            return (i, None)
    
    # Run searches in parallel (max 3 concurrent)
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all queries
        query_info = [(i, query) for i, query in enumerate(queries, 1)]
        futures = {executor.submit(search_and_parse, qi): qi for qi in query_info}
        
        # Collect results as they complete
        for future in as_completed(futures):
            idx, parsed = future.result()
            if parsed:
                results.append(parsed)
    
    print(f"   📚 Research complete: {len(results)} result sets")
    return results


__all__ = [
    "WebSearchTool",
    "generate_baseline_queries",
    "generate_research_queries",
    "parse_search_results",
    "conduct_research",
]

