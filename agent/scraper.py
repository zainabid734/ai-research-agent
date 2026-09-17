import logging
import requests
from bs4 import BeautifulSoup
from config import USER_AGENT, SCRAPE_TIMEOUT

logger = logging.getLogger("research_agent.scraper")


class ScraperError(Exception):
    pass


def scrape_url(url: str) -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=SCRAPE_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout scraping {url}")
        return ""
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error scraping {url}")
        return ""
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP {e.response.status_code} scraping {url}")
        return ""
    except requests.RequestException as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ""

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return ""

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:200])


def scrape_urls(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        try:
            content = scrape_url(url)
            if content:
                results.append({"url": url, "content": content[:3000]})
        except Exception as e:
            logger.warning(f"Error scraping {url}: {e}")
    return results


def format_context(scraped: list[dict]) -> str:
    parts = []
    for i, item in enumerate(scraped, 1):
        parts.append(f"### Source [{i}] — {item['url']}\n{item['content']}\n")
    return "\n---\n".join(parts) if parts else "No web content available."
