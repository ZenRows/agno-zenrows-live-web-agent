from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

ZENROWS_ENDPOINT = "https://api.zenrows.com/v1/"


def page_to_text(html: str, limit: int = 12_000) -> tuple[str | None, str]:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    text = " ".join(soup.get_text(" ", strip=True).split())
    metadata: list[str] = []
    for element in soup.select("[itemprop][content]"):
        itemprop = element.get("itemprop")
        content = element.get("content")
        if itemprop in {"priceCurrency", "availability"} and content:
            value = f"{itemprop}: {content}"
            if value not in metadata:
                metadata.append(value)
    if metadata:
        text = f"{text} Structured metadata: {'; '.join(metadata)}"
    return title, text[:limit]


def fetch_with_zenrows(
    url: str,
    api_key: str,
    *,
    session: Any = requests,
) -> dict[str, object]:
    """Fetch a public page through Zenrows and return compact page text."""
    response = session.get(
        ZENROWS_ENDPOINT,
        params={
            "url": url,
            "apikey": api_key,
            "mode": "auto",
        },
        timeout=60,
    )
    response.raise_for_status()
    title, text = page_to_text(response.text)
    return {
        "source_url": url,
        "status_code": response.status_code,
        "title": title,
        "text": text,
        "fetched_at": datetime.now(UTC).isoformat(),
    }


def fetch_direct(url: str, *, session: Any = requests) -> dict[str, object]:
    """Fetch the same page without Zenrows for a transparent comparison."""
    response = session.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; tutorial-validator/1.0)"},
        timeout=30,
    )
    title, text = page_to_text(response.text, limit=500)
    return {
        "source_url": url,
        "status_code": response.status_code,
        "title": title,
        "text_preview": text,
    }
