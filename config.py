import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("research_agent")

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

SCRAPE_TIMEOUT = 10
MAX_SOURCES = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

RATE_LIMIT_DEFAULT = "10 per minute"
RATE_LIMIT_STORAGE_URI = "memory://"
