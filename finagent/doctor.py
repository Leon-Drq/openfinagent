"""
finagent.doctor
===============

Environment diagnostics for the first-run path.

`finagent doctor` is intentionally conservative: it distinguishes between
blocking failures (the package cannot run) and warnings (live data or LLM
features are not configured yet). The offline demo should pass even when
network and credentials are unavailable.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import httpx
import yaml

from finagent import __version__
from finagent.config import (
    load_config,
    parse_global_budget,
    parse_policy,
    parse_providers,
)
from finagent.providers.builtin import SampleProvider
from finagent.runtime.registry import ProviderRegistry

DoctorStatus = Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class DoctorCheck:
    """One diagnostic result."""

    name: str
    status: DoctorStatus
    detail: str
    fix: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


async def run_doctor(
    *,
    config_path: str | None = None,
    network: bool = True,
    timeout_seconds: float = 5.0,
) -> list[DoctorCheck]:
    """Run all diagnostics and return structured results."""

    checks: list[DoctorCheck] = []
    checks.extend(_check_python())
    checks.extend(_check_package())
    checks.extend(_check_workflows())
    checks.extend(_check_optional_dependencies())
    checks.extend(_check_environment())
    checks.extend(_check_config(config_path))
    checks.extend(await _check_sample_provider())
    if network:
        checks.extend(await _check_network(timeout_seconds))
    else:
        checks.append(
            DoctorCheck(
                "network",
                "warn",
                "Skipped network checks.",
                "Run `finagent doctor --network` when you want live provider checks.",
            )
        )
    return checks


def has_failures(checks: list[DoctorCheck]) -> bool:
    """Return True when any diagnostic is blocking."""

    return any(check.status == "fail" for check in checks)


def _check_python() -> list[DoctorCheck]:
    version = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info >= (3, 10):
        return [DoctorCheck("python", "pass", f"Python {version}")]
    return [
        DoctorCheck(
            "python",
            "fail",
            f"Python {version}; OpenFinAgent requires Python 3.10+.",
            "Install Python 3.10, 3.11, or 3.12 and recreate your virtualenv.",
        )
    ]


def _check_package() -> list[DoctorCheck]:
    try:
        import finagent  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return [
            DoctorCheck(
                "package",
                "fail",
                f"Cannot import finagent: {exc}",
                "Install with `pip install -e .` from the repository root.",
            )
        ]
    return [
        DoctorCheck(
            "package",
            "pass",
            f"openfinagent {getattr(finagent, '__version__', __version__)}",
        )
    ]


def _check_workflows() -> list[DoctorCheck]:
    root = Path(__file__).resolve().parent.parent / "workflows"
    required = ["demo-earnings-deep-dive.yaml", "earnings-deep-dive.yaml"]
    missing = [name for name in required if not (root / name).exists()]
    if missing:
        return [
            DoctorCheck(
                "workflows",
                "fail",
                f"Missing bundled workflows: {', '.join(missing)}",
                "Reinstall the package or run from a complete source checkout.",
            )
        ]

    invalid: list[str] = []
    for name in required:
        try:
            with (root / name).open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            if not isinstance(data, dict) or not data.get("steps"):
                invalid.append(name)
        except Exception:  # noqa: BLE001
            invalid.append(name)

    if invalid:
        return [
            DoctorCheck(
                "workflows",
                "fail",
                f"Invalid bundled workflow YAML: {', '.join(invalid)}",
                "Reinstall the package or restore the workflows directory.",
            )
        ]

    return [
        DoctorCheck(
            "workflows",
            "pass",
            "Bundled demo and live workflows are present and parseable.",
        )
    ]


def _check_optional_dependencies() -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    required_modules = ["httpx", "openai", "rich", "typer", "yaml", "yfinance"]
    missing_required = [
        module for module in required_modules if importlib.util.find_spec(module) is None
    ]
    if missing_required:
        checks.append(
            DoctorCheck(
                "dependencies",
                "fail",
                f"Missing required modules: {', '.join(missing_required)}",
                "Run `pip install -e .` or reinstall `openfinagent`.",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "dependencies",
                "pass",
                "Required Python dependencies are importable.",
            )
        )

    if importlib.util.find_spec("mcp") is None:
        checks.append(
            DoctorCheck(
                "mcp extra",
                "warn",
                "MCP SDK is not installed.",
                'Install `openfinagent[mcp]` or use `pip install -e ".[mcp]"` from source.',
            )
        )
    else:
        checks.append(DoctorCheck("mcp extra", "pass", "MCP SDK is installed."))
    return checks


def _check_environment() -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    if os.environ.get("OPENAI_API_KEY"):
        base_url = os.environ.get("OPENAI_BASE_URL")
        detail = "OPENAI_API_KEY is set."
        if base_url:
            detail += f" OPENAI_BASE_URL={base_url}"
        checks.append(DoctorCheck("openai env", "pass", detail))
    else:
        checks.append(
            DoctorCheck(
                "openai env",
                "warn",
                "OPENAI_API_KEY is not set; offline demo works, live agent steps will not.",
                "Set OPENAI_API_KEY in `.env` before running live workflows.",
            )
        )

    if os.environ.get("QVERIS_API_KEY"):
        checks.append(DoctorCheck("qveris env", "pass", "QVERIS_API_KEY is set."))
    else:
        checks.append(
            DoctorCheck(
                "qveris env",
                "warn",
                "QVERIS_API_KEY is not set; QVeris provider will stay disabled.",
                "Set QVERIS_API_KEY when you want managed financial coverage.",
            )
        )

    if os.environ.get("SEC_USER_AGENT"):
        checks.append(DoctorCheck("sec user agent", "pass", "SEC_USER_AGENT is set."))
    else:
        checks.append(
            DoctorCheck(
                "sec user agent",
                "warn",
                "SEC_USER_AGENT is not set; default project user-agent will be used.",
                "Set SEC_USER_AGENT to identify your app/email for heavier EDGAR use.",
            )
        )
    return checks


def _check_config(config_path: str | None) -> list[DoctorCheck]:
    try:
        config = load_config(config_path)
        providers = parse_providers(config)
        policy = parse_policy(config)
        budget = parse_global_budget(config)
        registry = ProviderRegistry.from_configs(
            providers,
            policy=policy,
            global_budget_usd=budget,
        )
    except Exception as exc:  # noqa: BLE001
        return [
            DoctorCheck(
                "config",
                "fail",
                f"Cannot load provider config: {exc}",
                "Check `finagent.yaml` / `config.yaml` and provider credentials.",
            )
        ]

    names = [provider.name for provider in registry.providers]
    detail = f"Loaded providers: {', '.join(names) or 'none'}; policy={policy.value}"
    if budget is not None:
        detail += f"; budget=${budget:.2f}"
    return [DoctorCheck("config", "pass", detail)]


async def _check_sample_provider() -> list[DoctorCheck]:
    provider = SampleProvider()
    try:
        result = await provider.call("equity.quote", ticker="NVDA")
    except Exception as exc:  # noqa: BLE001
        return [
            DoctorCheck(
                "offline demo",
                "fail",
                f"SampleProvider failed: {exc}",
                "Reinstall the package or restore `finagent/providers/builtin/sample.py`.",
            )
        ]

    price = _get(result.data, "price")
    return [
        DoctorCheck(
            "offline demo",
            "pass",
            f"SampleProvider returned NVDA quote snapshot at {price}.",
        )
    ]


async def _check_network(timeout_seconds: float) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    timeout = httpx.Timeout(timeout_seconds)
    user_agent = os.environ.get("SEC_USER_AGENT") or (
        "openfinagent/0.1 (https://github.com/Leon-Drq/openfinagent; "
        "set SEC_USER_AGENT for production use)"
    )
    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        checks.append(
            await _probe_url(
                client,
                "sec edgar",
                "https://www.sec.gov/files/company_tickers.json",
                "SEC EDGAR company ticker index is reachable.",
                "Cannot reach SEC EDGAR; live filings workflows may fail.",
                "Set SEC_USER_AGENT to an app name plus contact email, then retry.",
            )
        )
        checks.append(
            await _probe_url(
                client,
                "yahoo finance",
                "https://query1.finance.yahoo.com/v8/finance/chart/NVDA?range=1d&interval=1d",
                "Yahoo Finance chart endpoint is reachable.",
                "Cannot reach Yahoo Finance; yfinance-backed live workflows may fail.",
                "Check your network or run live workflows from an unrestricted connection.",
            )
        )
        checks.append(
            await _probe_url(
                client,
                "pypi",
                "https://pypi.org/pypi/openfinagent/json",
                "PyPI package name is reachable.",
                "Cannot reach PyPI; package install checks may fail on this network.",
                "Check your network or package index configuration.",
                warn_on_404=True,
            )
        )
    return checks


async def _probe_url(
    client: httpx.AsyncClient,
    name: str,
    url: str,
    success_detail: str,
    failure_detail: str,
    failure_fix: str = "",
    *,
    warn_on_404: bool = False,
) -> DoctorCheck:
    try:
        response = await client.get(url)
        if response.status_code == 404 and warn_on_404:
            return DoctorCheck(
                name,
                "warn",
                "Endpoint reachable, but openfinagent is not published on PyPI yet.",
                "Publish the package from a GitHub Release when v0.2 is ready.",
            )
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return DoctorCheck(name, "warn", f"{failure_detail} ({exc})", failure_fix)
    return DoctorCheck(name, "pass", success_detail)


def _get(mapping: Any, key: str) -> Any:
    if isinstance(mapping, dict):
        return mapping.get(key)
    return None
