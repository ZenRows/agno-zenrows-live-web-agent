from datetime import UTC, datetime
import json
from types import SimpleNamespace

import pytest

import live_web_agent.agents as agents_module
from live_web_agent.agents import build_agents
from live_web_agent.config import Settings
from live_web_agent.schemas import FetchedPage, MarketSnapshot
from live_web_agent.workflow import WorkflowAgentError, run_workflow


class FakeAgent:
    def __init__(self, content):
        self.content = content
        self.prompts = []

    def run(self, prompt):
        self.prompts.append(prompt)
        return SimpleNamespace(content=self.content)


def test_workflow_passes_fetch_result_to_processing_agent():
    now = datetime.now(UTC)
    page = FetchedPage(
        source_url="https://example.com/product",
        status_code=200,
        title="Widget",
        text="Widget costs $19 and is in stock.",
        fetched_at=now,
    )
    snapshot = MarketSnapshot(
        product_name="Widget",
        current_price=19,
        currency="USD",
        availability="in stock",
        source_url=page.source_url,
        collected_at=now,
        evidence=["Widget costs $19 and is in stock."],
    )
    fetch_agent = FakeAgent(page)
    processing_agent = FakeAgent(snapshot)

    result = run_workflow(str(page.source_url), fetch_agent, processing_agent)

    assert result == snapshot
    assert "Widget costs $19" in processing_agent.prompts[0]


def test_zenrows_tool_registration_has_safe_openai_schema(monkeypatch):
    secret = "zenrows-secret-that-must-not-leak"
    fetch_agent, _ = build_agents(
        Settings(
            zenrows_api_key=secret,
            openai_api_key="test-openai-key",
        )
    )

    tool = fetch_agent.tools[0]
    assert callable(tool)
    assert tool.__name__ == "fetch_with_zenrows"
    assert "Fetch a public page through Zenrows" in tool.__doc__

    from agno.tools.function import Function

    registered = Function.from_callable(tool, strict=True)
    assert registered.parameters == {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"],
        "additionalProperties": False,
    }

    serialized = json.dumps(registered.to_dict())
    assert secret not in serialized
    assert secret not in repr(tool)
    assert secret not in repr(registered)

    def fail_with_secret(*args, **kwargs):
        raise RuntimeError(f"request URL contained apikey={secret}")

    monkeypatch.setattr(agents_module, "fetch_with_zenrows", fail_with_secret)
    with pytest.raises(RuntimeError, match="^Zenrows request failed$") as error:
        tool("https://example.com")
    assert secret not in str(error.value)


def test_workflow_reports_provider_error_before_schema_validation():
    fetch_agent = FakeAgent("Provider rejected the tool schema")
    fetch_agent.run = lambda prompt: SimpleNamespace(
        content="Provider rejected the tool schema", status="ERROR"
    )

    with pytest.raises(
        WorkflowAgentError,
        match="Web data agent failed: Provider rejected the tool schema",
    ):
        run_workflow("https://example.com/product", fetch_agent, FakeAgent(None))
