import logging
from agent.search import search_web, SearchError
from agent.scraper import scrape_urls, format_context
from llm.client import debate_challenge, LLMError
from cache.db import get_cached, set_cached
from config import MAX_SOURCES

logger = logging.getLogger("research_agent.debater")


class DebateError(Exception):
    pass


def debate(topic: str, user_pov: str) -> dict:
    if not topic or not topic.strip():
        raise DebateError("Please enter a topic.")
    if not user_pov or not user_pov.strip():
        raise DebateError("Please share your position on this topic.")

    topic = topic.strip()
    user_pov = user_pov.strip()

    cache_key = f"{topic}|||{user_pov}"
    cached = get_cached(cache_key, "debate")
    if cached:
        logger.info(f"Cache hit for debate: {topic[:50]}")
        return cached

    try:
        search_results = search_web(topic, max_results=MAX_SOURCES)
    except SearchError as e:
        raise DebateError(str(e))

    urls = [r["url"] for r in search_results] if search_results else []
    scraped = scrape_urls(urls) if urls else []
    context = format_context(scraped)

    try:
        challenge = debate_challenge(topic, user_pov, context)
    except LLMError as e:
        raise DebateError(str(e))

    sources = []
    for i, item in enumerate(search_results, 1):
        sources.append({
            "id": i,
            "title": item["title"],
            "url": item["url"],
        })

    result = {
        "challenge": challenge,
        "sources": sources,
    }

    set_cached(cache_key, "debate", result)
    return result
