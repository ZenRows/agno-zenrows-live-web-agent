from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from .schemas import FetchedPage, MarketSnapshot


class WorkflowAgentError(RuntimeError):
    """Raised when an Agno agent or its model provider fails."""


def _run_agent(agent: Any, prompt: str, role: str) -> Any:
    try:
        response = agent.run(prompt)
    except Exception as exc:
        # include the failed agent's role in the application error
        raise WorkflowAgentError(f"{role} failed: {exc}") from exc

    status = getattr(response, "status", None)
    status_value = getattr(status, "value", status)
    # catch provider errors returned as Agno responses
    if isinstance(status_value, str) and status_value.upper() == "ERROR":
        detail = getattr(response, "content", None) or "unknown provider error"
        raise WorkflowAgentError(f"{role} failed: {detail}")
    return response


def _content(
    response: Any,
    schema: type[FetchedPage] | type[MarketSnapshot],
) -> Any:
    value = response.content
    if isinstance(value, schema):
        return value
    try:
        # parse JSON strings before handling dictionary-like values
        if isinstance(value, str):
            return schema.model_validate_json(value)
        return schema.model_validate(value)
    except ValidationError as exc:
        raise WorkflowAgentError(
            f"Agent returned invalid {schema.__name__} data: {value!r}"
        ) from exc


def run_workflow(
    url: str,
    fetch_agent: Any,
    processing_agent: Any,
) -> MarketSnapshot:
    fetch_response = _run_agent(
        fetch_agent,
        f"Fetch this public product page through Zenrows: {url}",
        "Web data agent",
    )
    # validate the fetch result before sending it to the processing agent
    page = _content(fetch_response, FetchedPage)
    # pass the validated page as JSON instead of raw HTML
    processing_response = _run_agent(
        processing_agent,
        "Extract a market snapshot from this fetched page data:\n"
        + json.dumps(page.model_dump(mode="json"), ensure_ascii=False),
        "Market intelligence agent",
    )
    return _content(processing_response, MarketSnapshot)
