"""
Tests that don't hit the network.  Verify the runtime plumbing:

* Provider registry routing
* Budget enforcement
* Template expansion in the workflow runner
* End-to-end fetch + report (no LLM, no network)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import pytest
from typer.testing import CliRunner

from finagent import (
    Capability,
    CapabilityMeta,
    CallResult,
    DataProvider,
    ProviderRegistry,
    RoutingPolicy,
    Runner,
)
from finagent.cli import app
from finagent.runtime.registry import BudgetExceeded


# ---------------------------------------------------------------------------
# Fixtures: a fake provider that records calls
# ---------------------------------------------------------------------------


class FakeProvider(DataProvider):
    name = "fake"
    namespace = frozenset({"fake.*"})
    is_free = True
    requires_credentials = False

    def __init__(self, *, cost_per_call: float = 0.0) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._cost = cost_per_call

    async def discover(self, query: str) -> Sequence[Capability]:
        return [Capability(id="fake.echo", title="echo")]

    async def inspect(self, capability_id: str) -> CapabilityMeta:
        return CapabilityMeta(
            capability=Capability(id=capability_id, title=capability_id),
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        self.calls.append((capability_id, params))
        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data={"ok": True, **params},
            cost_usd=self._cost,
            latency_ms=1.0,
            cached=False,
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_registry_routes_to_matching_provider() -> None:
    registry = ProviderRegistry(policy=RoutingPolicy.PREFER_FREE)
    fake = FakeProvider()
    registry.add(fake, priority=1)

    result = await registry.call("fake.echo", value=42)

    assert result.data == {"ok": True, "value": 42}
    assert fake.calls == [("fake.echo", {"value": 42})]


@pytest.mark.asyncio
async def test_registry_raises_when_no_provider_serves_capability() -> None:
    registry = ProviderRegistry()
    registry.add(FakeProvider(), priority=1)

    with pytest.raises(LookupError):
        await registry.call("missing.thing")


@pytest.mark.asyncio
async def test_registry_enforces_per_provider_budget() -> None:
    registry = ProviderRegistry()
    registry.add(FakeProvider(cost_per_call=0.4), priority=1, budget_usd_per_run=0.5)

    # First call: $0.40, fine.
    await registry.call("fake.echo")
    # Second call would push us to $0.80 > $0.50.
    with pytest.raises(BudgetExceeded):
        await registry.call("fake.echo")


@pytest.mark.asyncio
async def test_runner_executes_fetch_and_report(tmp_path: Path) -> None:
    workflow_path = tmp_path / "wf.yaml"
    workflow_path.write_text(
        """
name: smoke
inputs:
  ticker: { type: string, required: true }
steps:
  - id: echo
    type: fetch
    capability: fake.echo
    params:
      ticker: ${ticker}
  - id: report
    type: report
    path: ${tmp}/out-${ticker}.md
    template: |
      ticker=${ticker}
      echoed=${echo.ticker}
""",
        encoding="utf-8",
    )

    registry = ProviderRegistry()
    registry.add(FakeProvider(), priority=1)

    runner = Runner(registry, audit_path=tmp_path / "audit.jsonl")
    result = await runner.run(
        workflow_path,
        inputs={"ticker": "NVDA", "tmp": str(tmp_path)},
    )

    assert result.report_path == tmp_path / "out-NVDA.md"
    body = result.report_path.read_text(encoding="utf-8")
    assert "ticker=NVDA" in body
    assert "echoed=NVDA" in body

    # Audit log should contain at least one call line and a run_end.
    audit_lines = (tmp_path / "audit.jsonl").read_text().splitlines()
    kinds = [line for line in audit_lines if "call" in line or "run_end" in line]
    assert len(kinds) >= 2

    await registry.teardown()


def test_demo_cli_generates_report(tmp_path: Path) -> None:
    runner = CliRunner()
    report_dir = tmp_path / "reports"
    audit_path = tmp_path / "audit.jsonl"

    result = runner.invoke(
        app,
        [
            "demo",
            "NVDA",
            "--output-dir",
            str(report_dir),
            "--audit",
            str(audit_path),
        ],
    )

    assert result.exit_code == 0, result.output
    # The exact date depends on the runner clock; keep the assertion robust.
    reports = list(report_dir.glob("NVDA-*-demo.md"))
    assert len(reports) == 1
    body = reports[0].read_text(encoding="utf-8")
    assert "Demo Research Brief" in body
    assert "SampleProvider" in body
    assert audit_path.exists()
    assert "provider" in audit_path.read_text(encoding="utf-8")


def test_init_cli_scaffolds_project(tmp_path: Path) -> None:
    runner = CliRunner()
    target = tmp_path / "starter"

    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code == 0, result.output
    assert (target / "finagent.yaml").exists()
    assert (target / ".env.example").exists()
    assert (target / "workflows" / "earnings-deep-dive.yaml").exists()
    assert (target / "workflows" / "demo-earnings-deep-dive.yaml").exists()
