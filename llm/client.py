import logging
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError
from config import OPENROUTER_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger("research_agent.llm")

client = None


class LLMError(Exception):
    pass


def _get_client():
    global client
    if client is None:
        if not OPENROUTER_API_KEY:
            raise LLMError("API key not configured. Set OPENROUTER_API_KEY in your .env file.")
        client = OpenAI(base_url=LLM_BASE_URL, api_key=OPENROUTER_API_KEY, timeout=60.0, max_retries=2)
    return client


def chat(messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> str:
    try:
        response = _get_client().chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        if not content:
            raise LLMError("LLM returned an empty response.")
        return content
    except APITimeoutError:
        logger.error("LLM request timed out")
        raise LLMError("The AI service timed out. Please try again.")
    except APIConnectionError:
        logger.error("Failed to connect to LLM API")
        raise LLMError("Could not connect to the AI service. Check your internet connection.")
    except APIError as e:
        logger.error(f"LLM API error: {e}")
        raise LLMError(f"AI service error: {e.message}")
    except LLMError:
        raise
    except Exception as e:
        logger.exception("Unexpected LLM error")
        raise LLMError("An unexpected error occurred with the AI service.")


def research_query(context: str, question: str) -> str:
    system = (
        "You are a research assistant. Given scraped web content below, provide a "
        "thorough, accurate answer to the user's question. Cite your sources by "
        "including the URL in brackets like [1], [2] etc. after each claim. "
        "If the sources disagree, note the disagreement. "
        "Always indicate your confidence level (high/medium/low) at the end."
    )
    user = f"## Web Content\n\n{context}\n\n## Question\n\n{question}"
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ], temperature=0.3)


def debate_challenge(topic: str, user_pov: str, context: str) -> str:
    system = (
        "You are a Socratic debate partner. Your role is to respectfully challenge "
        "the user's point of view on any topic. Use the provided web research as "
        "evidence. Structure your response as:\n"
        "1. Acknowledge what the user said\n"
        "2. Present counter-arguments with evidence from the sources\n"
        "3. Ask a thought-provoking question\n"
        "4. Rate the strength of the user's argument (1-10)\n\n"
        "Be respectful but intellectually rigorous. Cite sources with [1], [2] etc."
    )
    user = (
        f"## Topic: {topic}\n\n"
        f"## User's Position:\n{user_pov}\n\n"
        f"## Research Context:\n{context}"
    )
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ], temperature=0.5)
