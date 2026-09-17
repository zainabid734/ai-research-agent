import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from agent.researcher import research, ResearchError
from agent.debater import debate, DebateError
from llm.client import LLMError
from config import RATE_LIMIT_DEFAULT, RATE_LIMIT_STORAGE_URI, OPENROUTER_API_KEY

logger = logging.getLogger("research_agent")

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[RATE_LIMIT_DEFAULT],
    storage_uri=RATE_LIMIT_STORAGE_URI,
)


@app.route("/")
def index():
    api_configured = bool(OPENROUTER_API_KEY)
    return render_template("index.html", api_configured=api_configured)


@app.route("/api/research", methods=["POST"])
@limiter.limit("8 per minute")
def api_research():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "API key not configured. Please set OPENROUTER_API_KEY in your .env file."}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body."}), 400

    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "Please enter a topic to research."}), 400

    if len(topic) > 500:
        return jsonify({"error": "Topic is too long. Maximum 500 characters."}), 400

    try:
        result = research(topic)
        return jsonify(result)
    except ResearchError as e:
        return jsonify({"error": str(e)}), 422
    except LLMError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        logger.exception("Unexpected error in research endpoint")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


@app.route("/api/debate", methods=["POST"])
@limiter.limit("8 per minute")
def api_debate():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "API key not configured. Please set OPENROUTER_API_KEY in your .env file."}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body."}), 400

    topic = (data.get("topic") or "").strip()
    user_pov = (data.get("pov") or "").strip()

    if not topic:
        return jsonify({"error": "Please enter a topic."}), 400
    if not user_pov:
        return jsonify({"error": "Please share your position."}), 400

    if len(topic) > 500:
        return jsonify({"error": "Topic is too long. Maximum 500 characters."}), 400
    if len(user_pov) > 2000:
        return jsonify({"error": "Position is too long. Maximum 2000 characters."}), 400

    try:
        result = debate(topic, user_pov)
        return jsonify(result)
    except DebateError as e:
        return jsonify({"error": str(e)}), 422
    except LLMError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        logger.exception("Unexpected error in debate endpoint")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Please wait a moment before trying again."}), 429


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — app will start but research will not work.")
    app.run(debug=True, port=5000)
