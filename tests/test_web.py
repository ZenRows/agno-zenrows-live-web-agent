from live_web_agent.web import fetch_direct, fetch_with_zenrows, page_to_text


class FakeResponse:
    status_code = 200
    text = "<html><head><title>Widget</title></head><body><p>$19</p></body></html>"

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse()


def test_page_to_text_removes_script_content():
    title, text = page_to_text("<title>A</title><script>bad()</script><p>Good data</p>")
    assert title == "A"
    assert text == "A Good data"


def test_page_to_text_preserves_market_metadata():
    html = """
    <span itemprop="priceCurrency" content="USD">$52</span>
    <meta itemprop="availability" content="http://schema.org/InStock">
    """

    _, text = page_to_text(html)

    assert "priceCurrency: USD" in text
    assert "availability: http://schema.org/InStock" in text


def test_zenrows_request_uses_documented_parameters():
    session = FakeSession()
    result = fetch_with_zenrows("https://example.com", "secret", session=session)

    _, kwargs = session.calls[0]
    assert kwargs["params"] == {
        "url": "https://example.com",
        "apikey": "secret",
        "mode": "auto",
    }
    assert result["title"] == "Widget"


def test_direct_request_does_not_use_zenrows():
    session = FakeSession()
    fetch_direct("https://example.com", session=session)
    assert session.calls[0][0] == "https://example.com"
    assert "params" not in session.calls[0][1]
