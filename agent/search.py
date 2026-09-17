import logging
from ddgs import DDGS

logger = logging.getLogger("research_agent.search")


class SearchError(Exception):
    pass


def search_web(query: str, max_results: int = 5) -> list[dict]:
    if not query or not query.strip():
        return []

    try:
        results = list(DDGS().text(query, max_results=max_results))
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise SearchError("Web search service is currently unavailable. Please try again.")

    output = []
    for r in results:
        url = r.get("href", "")
        if not url or not url.startswith("http"):
            continue
        output.append({
            "title": r.get("title", "").strip(),
            "url": url,
            "display_url": url,
            "snippet": r.get("body", "").strip(),
        })
    return output
