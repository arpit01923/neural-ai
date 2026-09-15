from typing import Any

from langchain_community.llms import Ollama

from config import settings
from services.research_prompts import CONCLUSION_PROMPT, PLANNING_PROMPT, READING_PROMPT, REPORT_PROMPT
from services.tools.search_tool import fetch_page_text, search_web


llm = Ollama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_URL)


def _deduplicate_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique_by_content: dict[str, dict[str, Any]] = {}

    for source in sources:
        content = (source.get("content") or "").strip().lower()
        if not content:
            continue

        current_best = unique_by_content.get(content)
        if current_best is None or float(source.get("score", 0.0)) > float(current_best.get("score", 0.0)):
            unique_by_content[content] = source

    return list(unique_by_content.values())


def _build_sections(query: str, context: str) -> list[dict[str, str]]:
    report_prompt = REPORT_PROMPT.format(question=query, context=context)
    raw_report = llm.invoke(report_prompt).strip()

    sections: list[dict[str, str]] = []
    current_heading = "Overview"
    buffer: list[str] = []

    for line in raw_report.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if buffer:
                sections.append({"heading": current_heading, "content": "\n".join(buffer).strip()})
            current_heading = stripped.lstrip("# ").strip() or "Overview"
            buffer = []
        elif stripped:
            buffer.append(stripped)

    if buffer:
        sections.append({"heading": current_heading, "content": "\n".join(buffer).strip()})

    return sections or [
        {"heading": "Overview", "content": "The report has been generated from the collected sources."},
        {"heading": "Main Findings", "content": "The search results were summarized into a concise research overview."},
    ]


def build_research_report(query: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    unique_sources = _deduplicate_sources(sources)
    if not unique_sources:
        raise ValueError("No research sources could be collected for the requested question.")

    context_lines = []
    for source in unique_sources:
        source_content = source.get("content", "") or ""
        if source_content:
            context_lines.append(f"Title: {source.get('title', 'Untitled')}\nURL: {source.get('url', '')}\nContent: {source_content}")

    context = "\n\n".join(context_lines)

    summary_prompt = (
        "You are a research summarizer. Create a concise but informative summary based only on the provided source material. "
        "Keep it neutral and avoid inventing facts.\n\n"
        f"Question: {query}\n\nSources:\n{context}"
    )
    summary = llm.invoke(summary_prompt).strip()

    reading_prompt = READING_PROMPT.format(question=query, context=context)
    findings = llm.invoke(reading_prompt).strip()

    sections = _build_sections(query, context)

    conclusion_prompt = CONCLUSION_PROMPT.format(question=query, findings=findings)
    conclusion = llm.invoke(conclusion_prompt).strip()

    if conclusion:
        sections.append({"heading": "Conclusion", "content": conclusion})

    key_points = [
        line.strip().lstrip("-*• ")
        for line in findings.splitlines()
        if line.strip()
    ]

    if not key_points:
        key_points = [
            "The provided sources describe the topic from multiple perspectives.",
            "The search results were summarized into a concise research overview.",
        ]

    return {
        "title": query,
        "summary": summary or "No summary could be generated from the collected sources.",
        "key_points": key_points[:5],
        "sections": sections,
        "sources": unique_sources,
    }


def generate_research_report(query: str) -> dict[str, Any]:
    print(f"Generating research report for question: {query}")
    search_results = search_web(query, max_results=5)
    print(f"Search results for question '{query}': {len(search_results)}")
    if not search_results:
        raise ValueError("The search service returned no results for the requested question.")

    enriched_results: list[dict[str, Any]] = []
    for result in search_results:
        print(f"Fetching page text for URL: {result['url']}")
        page_text = fetch_page_text(result["url"])
        print(f"Fetched page text for URL '{result['url']}': {len(page_text) if page_text else 0} characters")
        enriched_results.append(
            {
                "title": result["title"],
                "url": result["url"],
                "content": page_text or result["content"],
                "score": result["score"],
            }
        )

    return build_research_report(query, enriched_results)
