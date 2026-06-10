"""
examples/quickstart.py
======================

The smallest possible end-to-end run, in pure Python (no CLI).

Prereqs:

    pip install openfinagent
    export OPENAI_API_KEY=sk-...

Run:

    python examples/quickstart.py NVDA
"""

from __future__ import annotations

import asyncio
import sys

from finagent import ProviderRegistry, Runner
from finagent.providers.builtin import SecEdgarProvider, YFinanceProvider
from finagent.runtime.llm import LLMClient


async def main(ticker: str) -> None:
    # 1. Build a registry directly (no config.yaml needed).
    registry = ProviderRegistry()
    registry.add(YFinanceProvider(), priority=1)
    registry.add(SecEdgarProvider(), priority=1)

    # 2. Build the LLM client (reads OPENAI_API_KEY from the environment).
    llm = LLMClient(default_model="gpt-4o-mini")

    # 3. Run the bundled workflow.
    runner = Runner(registry, llm=llm, audit_path="audit.jsonl")
    result = await runner.run(
        "workflows/earnings-deep-dive.yaml",
        inputs={"ticker": ticker},
    )

    print(f"\n✓ done in {result.elapsed_seconds:.1f}s, "
          f"spent ${result.total_cost_usd:.4f}")
    if result.report_path:
        print(f"  report: {result.report_path}")

    await registry.teardown()


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    asyncio.run(main(ticker))
