from __future__ import annotations

import argparse
import json
import os

from dotenv import load_dotenv

from .agents import build_agents
from .config import Settings
from .web import fetch_direct, fetch_with_zenrows
from .workflow import run_workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Agno and Zenrows workflow"
    )
    # use TARGET_URL unless the reader passes --url
    parser.add_argument("--url", default=os.getenv("TARGET_URL"))
    parser.add_argument("--skip-direct", action="store_true")
    parser.add_argument("--fetch-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    # load the local environment before reading TARGET_URL or API keys
    load_dotenv()
    args = parse_args()
    if not args.url:
        raise SystemExit("Pass --url or set TARGET_URL")

    # print the direct response unless --skip-direct is present
    if not args.skip_direct:
        print("Direct request comparison:")
        print(
            json.dumps(
                fetch_direct(args.url),
                indent=2,
                ensure_ascii=False,
            )
        )

    # print the Zenrows tool result without running the agents
    if args.fetch_only:
        api_key = os.getenv("ZENROWS_API_KEY")
        if not api_key:
            raise SystemExit("Set ZENROWS_API_KEY to run --fetch-only")
        print("\nZenrows tool result:")
        page = fetch_with_zenrows(args.url, api_key=api_key)
        print(json.dumps(page, indent=2, ensure_ascii=False))
        return

    settings = Settings.from_env()
    fetch_agent, processing_agent = build_agents(settings)
    result = run_workflow(args.url, fetch_agent, processing_agent)
    print("\nTwo-agent result:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
