"""
finagent.config
===============

Tiny config loader: parse ``config.yaml`` (or its absence) into a list
of :class:`ProviderConfig` records, expanding ``${ENV_VAR}`` references
against the environment.

A missing config file is *not* an error — the loader falls back to a
sensible default that registers ``yfinance`` and ``sec_edgar`` (both
keyless).  This keeps the "5-minute first run" promise intact.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from finagent.runtime.registry import ProviderConfig, RoutingPolicy

_ENV_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


# Default config: free + keyless providers only.
_DEFAULT_CONFIG = {
    "providers": [
        {"name": "yfinance",  "type": "builtin.yfinance",  "priority": 1},
        {"name": "sec_edgar", "type": "builtin.sec_edgar", "priority": 1},
    ],
    "routing": {"policy": "prefer_free"},
}


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Read a config file (if present), expand env vars, and return a dict."""

    if path is not None:
        config_path = Path(path)
    else:
        # Walk up from CWD looking for config.yaml.
        config_path = _find_config()

    if config_path is None or not Path(config_path).exists():
        return _DEFAULT_CONFIG

    with Path(config_path).open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    return _expand_env(raw)


def parse_providers(config: dict[str, Any]) -> list[ProviderConfig]:
    """Build :class:`ProviderConfig` records from a parsed config dict."""

    out: list[ProviderConfig] = []
    for entry in config.get("providers") or []:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name") or entry.get("type") or "").strip()
        type_ = str(entry.get("type") or "").strip()
        if not name or not type_:
            raise ValueError(
                f"Provider entry must have both 'name' and 'type': {entry!r}"
            )
        # Anything not in the well-known keys is forwarded to the
        # provider constructor as kwargs.
        well_known = {"name", "type", "priority", "budget_usd_per_run"}
        options = {k: v for k, v in entry.items() if k not in well_known}
        out.append(
            ProviderConfig(
                name=name,
                type=type_,
                priority=int(entry.get("priority", 5)),
                options=options,
                budget_usd_per_run=_maybe_float(entry.get("budget_usd_per_run")),
            )
        )
    return out


def parse_policy(config: dict[str, Any]) -> RoutingPolicy:
    raw = (config.get("routing") or {}).get("policy") or "prefer_free"
    try:
        return RoutingPolicy(str(raw).lower())
    except ValueError as exc:
        raise ValueError(
            f"Unknown routing policy {raw!r}. "
            f"Valid: {[p.value for p in RoutingPolicy]}"
        ) from exc


def parse_global_budget(config: dict[str, Any]) -> float | None:
    return _maybe_float((config.get("budget") or {}).get("usd_per_run"))


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _find_config() -> Path | None:
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / "config.yaml"
        if candidate.exists():
            return candidate
        candidate = parent / "finagent.yaml"
        if candidate.exists():
            return candidate
    return None


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return _ENV_RE.sub(lambda m: os.environ.get(m.group(1), ""), value)
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    return value


def _maybe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
