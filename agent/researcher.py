import logging
from agent.search import search_web, SearchError
from agent.scraper import scrape_urls, format_context
from llm.client import research_query, LLMError
from cache.db import get_cached, set_cached
from config import MAX_SOURCES

logger = logging.getLogger("research_agent.researcher")


class ResearchError(Exception):
    pass


def research(topic: str) -> dict:
    if not topic or not topic.strip():
        raise ResearchError("Please enter a topic to research.")

    topic = topic.strip()

    cached = get_cached(topic, "research")
    if cached:
        logger.info(f"Cache hit for research: {topic[:50]}")
        return cached

    try:
        search_results = search_web(topic, max_results=MAX_SOURCES)
    except SearchError as e:
        raise ResearchError(str(e))

    if not search_results:
        return {
            "answer": "I couldn't find any relevant sources for this topic. Try rephrasing your question or using different keywords.",
            "sources": [],
            "confidence": "low",
        }

    urls = [r["url"] for r in search_results]
    scraped = scrape_urls(urls)
    context = format_context(scraped)

    try:
        answer = research_query(context, topic)
    except LLMError as e:
        raise ResearchError(str(e))

    sources = []
    for i, item in enumerate(search_results, 1):
        sources.append({
            "id": i,
            "title": item["title"],
            "url": item["url"],
            "snippet": item["snippet"],
        })

    confidence = _extract_confidence(answer)

    result = {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
    }

    set_cached(topic, "research", result)
    return result


def _extract_confidence(answer: str) -> str:
    lower = answer.lower()
    if "confidence: high" in lower or "high confidence" in lower:
        return "high"
    elif "confidence: medium" in lower or "medium confidence" in lower:
        return "medium"
    return "low"
