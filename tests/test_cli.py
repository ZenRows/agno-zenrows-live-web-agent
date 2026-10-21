import json
import sys

from live_web_agent import cli


def test_fetch_only_prints_tool_result_without_building_agents(monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)
    monkeypatch.setenv("ZENROWS_API_KEY", "secret")
    monkeypatch.setattr(
        sys, "argv", ["live-web-agent", "--url", "https://example.com", "--fetch-only"]
    )
    monkeypatch.setattr(cli, "fetch_direct", lambda url: {"status_code": 403})
    monkeypatch.setattr(
        cli,
        "fetch_with_zenrows",
        lambda url, api_key: {"source_url": url, "status_code": 200},
    )

    def fail_build(settings):
        raise AssertionError("agents must not be built with --fetch-only")

    monkeypatch.setattr(cli, "build_agents", fail_build)

    cli.main()

    output = capsys.readouterr().out
    tool_result = output.split("Zenrows tool result:\n", 1)[1]
    assert json.loads(tool_result) == {
        "source_url": "https://example.com",
        "status_code": 200,
    }
    assert "secret" not in output
