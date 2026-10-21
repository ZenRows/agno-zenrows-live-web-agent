# Build a Live Web Data Agent With Agno and Zenrows

Two Agno agents that retrieve current web data through [Zenrows Fetch](https://www.zenrows.com/products/fetch) and turn it into a validated market snapshot. The web data agent handles live web access through a typed Zenrows tool, and the processing agent extracts only values supported by the fetched page.

Companion code for the Zenrows article [Build a Live Web Data Agent With Agno and Zenrows](https://www.zenrows.com/blog/live-web-data-agent-agno-zenrows).

## Features

- Registers Zenrows Fetch as a typed Python function tool in Agno
- Keeps the Zenrows API key out of the tool schema: the model only supplies `url`
- Uses `mode=auto` so Fetch selects the access configuration for each target
- Runs a deterministic two-agent handoff, validated with Pydantic at each step
- Compares a direct request with the response returned through Zenrows
- `--fetch-only` prints the Zenrows tool result without running the agents
- Includes tests that run offline and spend no API credits

## Prerequisites

- Python 3.11, 3.12 or 3.13
- A Zenrows API key: [create a free account](https://app.zenrows.com/register)
- An OpenAI API key

Use only public pages you are authorized to access.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ZenRows/agno-zenrows-live-web-agent.git
cd agno-zenrows-live-web-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

```bash
# macOS and Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` installs this project in editable mode with its development tools (`pytest`, `ruff`), which also puts the `live-web-agent` command on your path.

## Configuration

Copy the example environment file and replace the placeholder values:

```bash
cp .env.example .env
```

```text
ZENROWS_API_KEY=replace_with_your_zenrows_api_key
OPENAI_API_KEY=replace_with_your_openai_api_key
OPENAI_MODEL=gpt-5-mini
TARGET_URL=https://www.scrapingcourse.com/cloudflare-challenge
```

- `ZENROWS_API_KEY`: from your [Zenrows dashboard](https://app.zenrows.com/register).
- `OPENAI_API_KEY`: from the OpenAI platform. Not needed for `--fetch-only`.
- `OPENAI_MODEL`: optional, defaults to `gpt-5-mini`.
- `TARGET_URL`: the page the CLI uses when you do not pass `--url`.

## Project structure

```text
agno-zenrows-live-web-agent/
├── src/live_web_agent/
│   ├── __init__.py
│   ├── agents.py      # the two Agno agents and the Zenrows tool wrapper
│   ├── cli.py         # live-web-agent command
│   ├── config.py      # settings loaded from the environment
│   ├── schemas.py     # FetchedPage and MarketSnapshot models
│   ├── web.py         # Zenrows Fetch request, direct request, page cleanup
│   └── workflow.py    # runs both agents and validates each handoff
├── tests/             # offline tests, no API calls
├── .env.example
├── .gitignore
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

## How it works

```text
URL
  ↓
Web data agent calls fetch_with_zenrows (Zenrows Fetch, mode=auto)
  ↓
Workflow validates the result as FetchedPage
  ↓
Market intelligence agent (no tools) extracts the product fields
  ↓
Workflow validates the result as MarketSnapshot
```

1. The CLI optionally sends a direct HTTP request so the access difference is visible.
2. The web data agent calls `fetch_with_zenrows()`, which sends the URL to Zenrows Fetch with `mode=auto`.
3. The tool removes scripts and styles, keeps Schema.org currency and availability values, and limits the page text before returning it to the agent.
4. The workflow passes the validated `FetchedPage` to the market intelligence agent as JSON.
5. The second agent returns a `MarketSnapshot` with evidence quoted from the page.

## Running the project

Check the Zenrows tool on the configured target, without running the agents:

```bash
live-web-agent --fetch-only
```

Run both agents on a product page:

```bash
live-web-agent --url "https://www.scrapingcourse.com/ecommerce/product/chaz-kangeroo-hoodie/"
```

Skip the direct-request comparison:

```bash
live-web-agent --skip-direct
```

Run the tests and the linter:

```bash
pytest -q
ruff check .
```

## Output

`live-web-agent --fetch-only` on the Cloudflare challenge page prints the direct response and the Zenrows tool result:

```text
Direct request comparison:
{
  "source_url": "https://www.scrapingcourse.com/cloudflare-challenge",
  "status_code": 403,
  "title": "Just a moment...",
  "text_preview": "Just a moment..."
}

Zenrows tool result:
{
  "source_url": "https://www.scrapingcourse.com/cloudflare-challenge",
  "status_code": 200,
  "title": "Cloudflare Challenge - ScrapingCourse.com",
  "text": "Cloudflare Challenge - ScrapingCourse.com Scraping Course Cloudflare Challenge You bypassed the Cloudflare challenge! :D",
  "fetched_at": "2026-10-21T08:11:16.464568+00:00"
}
```

A full run prints the direct comparison, then `Two-agent result:` followed by the validated `MarketSnapshot` JSON: `product_name`, `current_price`, `currency`, `availability`, `source_url`, `collected_at` and up to five `evidence` snippets. Fields the page does not support are `null`.

## Technologies

- Python
- Agno
- Zenrows Fetch
- OpenAI
- Pydantic
- Requests
- Beautiful Soup
- pytest and Ruff

## Related article

This repository accompanies the Zenrows article:

**Build a Live Web Data Agent With Agno and Zenrows**

https://www.zenrows.com/blog/live-web-data-agent-agno-zenrows
