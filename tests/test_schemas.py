from datetime import UTC, datetime
import json

import pytest
from pydantic import ValidationError

from live_web_agent.schemas import FetchedPage, MarketSnapshot


@pytest.mark.parametrize("schema", [FetchedPage, MarketSnapshot])
def test_source_url_schema_is_an_unconstrained_string(schema):
    generated = schema.model_json_schema()

    assert generated["properties"]["source_url"] == {"type": "string"}
    assert '"format": "uri"' not in json.dumps(generated)


@pytest.mark.parametrize("url", ["http://example.com/page", "https://example.com/page"])
@pytest.mark.parametrize("schema", [FetchedPage, MarketSnapshot])
def test_source_url_accepts_http_and_https(schema, url):
    values = {
        "source_url": url,
        "collected_at": datetime.now(UTC),
    }
    if schema is FetchedPage:
        values.update(status_code=200, text="page", fetched_at=datetime.now(UTC))

    assert schema.model_validate(values).source_url == url


@pytest.mark.parametrize("url", ["not a url", "ftp://example.com", "https:///missing-host"])
@pytest.mark.parametrize("schema", [FetchedPage, MarketSnapshot])
def test_source_url_rejects_invalid_urls(schema, url):
    values = {
        "source_url": url,
        "collected_at": datetime.now(UTC),
    }
    if schema is FetchedPage:
        values.update(status_code=200, text="page", fetched_at=datetime.now(UTC))

    with pytest.raises(ValidationError, match="valid HTTP or HTTPS URL"):
        schema.model_validate(values)
