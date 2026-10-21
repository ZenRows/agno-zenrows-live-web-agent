from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    zenrows_api_key: str
    openai_api_key: str
    openai_model: str = "gpt-5-mini"

    @classmethod
    def from_env(cls) -> "Settings":
        # stop before creating either agent when a credential is missing
        missing = [
            name
            for name in ("ZENROWS_API_KEY", "OPENAI_API_KEY")
            if not os.getenv(name)
        ]
        if missing:
            names = ", ".join(missing)
            raise RuntimeError(f"Missing required environment variables: {names}")
        # use gpt-5-mini unless OPENAI_MODEL overrides it
        return cls(
            zenrows_api_key=os.environ["ZENROWS_API_KEY"],
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        )
