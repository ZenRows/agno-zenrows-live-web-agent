from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("source_url must be a valid HTTP or HTTPS URL")
    return value


def _keep_source_url_schema_plain(schema: dict[str, object]) -> None:
    properties = schema.get("properties")
    if isinstance(properties, dict):
        source_url = properties.get("source_url")
        if isinstance(source_url, dict):
            # remove metadata that the structured-output schema does not need
            source_url.pop("title", None)


class FetchedPage(BaseModel):
    # keep source_url as a plain string in the OpenAI output schema
    model_config = ConfigDict(json_schema_extra=_keep_source_url_schema_plain)

    source_url: str
    status_code: int
    title: str | None = None
    text: str
    fetched_at: datetime

    # validate the URL in Python without adding format: "uri" to the schema
    _source_url_is_http = field_validator("source_url")(_validate_http_url)


class MarketSnapshot(BaseModel):
    model_config = ConfigDict(json_schema_extra=_keep_source_url_schema_plain)

    product_name: str | None = None
    current_price: float | None = None
    currency: str | None = None
    availability: str | None = None
    source_url: str
    collected_at: datetime
    evidence: list[str] = Field(default_factory=list, max_length=5)

    _source_url_is_http = field_validator("source_url")(_validate_http_url)
