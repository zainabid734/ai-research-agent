# AI Research Agent

A deep research agent that scrapes the web in real-time, synthesizes evidence-based answers with citations, and challenges your point of view through Socratic debate.

## Features

- **Research Mode** — Enter any topic, get a thorough answer with clickable source citations
- **Debate Mode** — Toggle on to have the agent challenge your position with counter-arguments and evidence
- **Confidence Scoring** — Each answer includes a confidence level based on source agreement
- **SQLite Caching** — Repeated queries are served from cache to save API calls
- **Real-time Scraping** — Uses DuckDuckGo for search and BeautifulSoup for content extraction

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | NVIDIA Nemotron 3 Ultra via OpenRouter (free tier) |
| Web Scraping | BeautifulSoup + Requests |
| Search Engine | DuckDuckGo |
| Backend | Flask |
| Frontend | HTML/CSS/JS |
| Caching | SQLite |

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a free API key from [OpenRouter](https://openrouter.ai/keys)

3. Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

4. Run the app:
```bash
python app.py
```

5. Open `http://localhost:5000` in your browser.

## Usage

### Research Mode
1. Type any topic or question in the input field
2. Click **Research**
3. View the synthesized answer with clickable source citations

### Debate Mode
1. Click the **Debate** toggle
2. Enter a topic and your position
3. Click **Challenge Me**
4. The agent will present counter-arguments and rate your argument strength

## Project Structure

```
ai-research-agent/
├── app.py                 # Flask entry point
├── config.py              # Configuration
├── agent/
│   ├── search.py          # DuckDuckGo search
│   ├── scraper.py         # BeautifulSoup scraper
│   ├── researcher.py      # Research orchestration
│   └── debater.py         # Debate mode logic
├── llm/
│   └── client.py          # OpenRouter LLM client
├── cache/
│   └── db.py              # SQLite caching
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    └── index.html
```
