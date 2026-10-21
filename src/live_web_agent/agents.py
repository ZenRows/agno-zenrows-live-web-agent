from __future__ import annotations

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from .config import Settings
from .schemas import FetchedPage, MarketSnapshot
from .web import fetch_with_zenrows


def build_agents(settings: Settings) -> tuple[Agent, Agent]:
    # both agents use the model selected in the application settings
    model = OpenAIChat(
        id=settings.openai_model,
        api_key=settings.openai_api_key,
    )

    # capture the API key here so the model supplies only the URL
    def fetch_with_zenrows_tool(url: str) -> dict[str, object]:
        """Fetch a public page through Zenrows and return compact page text."""
        try:
            return fetch_with_zenrows(
                url,
                api_key=settings.zenrows_api_key,
            )
        except Exception:
            # request exceptions can include the complete query string
            # keep Zenrows credentials out of logs and model tool results
            raise RuntimeError("Zenrows request failed") from None

    # expose a stable public tool name to Agno
    fetch_with_zenrows_tool.__name__ = "fetch_with_zenrows"

    # require the first agent to fetch the supplied page through Zenrows
    fetch_agent = Agent(
        name="Web data agent",
        model=model,
        tools=[fetch_with_zenrows_tool],
        output_schema=FetchedPage,
        instructions=[
            "Always call fetch_with_zenrows for the supplied URL.",
            "Return only the fetched page data. Do not invent missing content.",
        ],
    )
    # give the second agent no tools because it only processes fetched data
    processing_agent = Agent(
        name="Market intelligence agent",
        model=model,
        output_schema=MarketSnapshot,
        instructions=[
            "Extract only values supported by the supplied page data.",
            "Use null for missing fields and quote short evidence snippets.",
        ],
    )
    return fetch_agent, processing_agent
