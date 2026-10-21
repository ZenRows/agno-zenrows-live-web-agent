import pytest

from live_web_agent.config import Settings


def test_settings_reports_all_missing_keys(monkeypatch):
    monkeypatch.delenv("ZENROWS_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ZENROWS_API_KEY, OPENAI_API_KEY"):
        Settings.from_env()

