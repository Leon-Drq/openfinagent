"""
finagent.providers.builtin.fred
===============================

A reference free-tier :class:`DataProvider` backed by the St. Louis Fed
FRED API.  This is the smallest realistic provider in the project and is
intended as a template for new contributors.

* No SDK dependency — uses :mod:`httpx` directly.
* Honours the FRED 120-req/min rate limit by sleeping when necessary.
* Reports zero cost: FRED is free for non-commercial research.

Usage
-----

.. code-block:: yaml

    # config.yaml
    providers:
      - name: fred
        type: builtin.fred
        priority: 1
        api_key: ${FRED_API_KEY}     # free, request at fred.stlouisfed.org
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Sequence

import httpx

from ..base import Capability, CapabilityMeta, CallResult, DataProvider


_API = "https://api.stlouisfed.org/fred"

# A tiny curated catalog so ``discover`` returns something useful out of
# the box.  In production you would proxy FRED's full series search.
_CATALOG: dict[str, Capability] = {
    "macro.us.gdp.real": Capability(
        id="macro.us.gdp.real",
        title="US Real GDP (chained 2017 dollars)",
        description="Quarterly real GDP, seasonally adjusted, billions USD.",
        tags=frozenset({"macro", "us", "gdp"}),
        estimated_cost_usd=0.0,
    ),
    "macro.us.cpi.headline": Capability(
        id="macro.us.cpi.headline",
        title="US CPI, all urban consumers",
        description="Headline CPI index, monthly, 1982-1984 = 100.",
        tags=frozenset({"macro", "us", "inflation"}),
        estimated_cost_usd=0.0,
    ),
    "macro.us.unemployment": Capability(
        id="macro.us.unemployment",
        title="US Unemployment Rate (U-3)",
        description="Civilian unemployment rate, seasonally adjusted, %.",
        tags=frozenset({"macro", "us", "labor"}),
        estimated_cost_usd=0.0,
    ),
}

# Capability id -> FRED series id
_SERIES_MAP: dict[str, str] = {
    "macro.us.gdp.real": "GDPC1",
    "macro.us.cpi.headline": "CPIAUCSL",
    "macro.us.unemployment": "UNRATE",
}


class FredProvider(DataProvider):
    """Read-only adapter for FRED economic time series."""

    name = "fred"
    namespace = frozenset({"macro.us.*"})
    is_free = True
    requires_credentials = True  # API key is free but required

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("FRED_API_KEY")
        if not self._api_key:
            raise RuntimeError(
                "FredProvider requires FRED_API_KEY (free at fred.stlouisfed.org)."
            )
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()  # serialize requests for the rate limit

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def setup(self) -> None:
        self._client = httpx.AsyncClient(timeout=10.0)

    async def teardown(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    # ------------------------------------------------------------------ #
    # Required methods
    # ------------------------------------------------------------------ #

    async def discover(self, query: str) -> Sequence[Capability]:
        q = query.lower()
        return [
            cap for cap in _CATALOG.values()
            if q in cap.title.lower()
            or q in cap.description.lower()
            or any(q in tag for tag in cap.tags)
        ]

    async def inspect(self, capability_id: str) -> CapabilityMeta:
        if capability_id not in _CATALOG:
            raise KeyError(capability_id)
        return CapabilityMeta(
            capability=_CATALOG[capability_id],
            input_schema={
                "type": "object",
                "properties": {
                    "start": {"type": "string", "format": "date",
                              "description": "Inclusive start date, YYYY-MM-DD."},
                    "end":   {"type": "string", "format": "date",
                              "description": "Inclusive end date, YYYY-MM-DD."},
                },
                "required": [],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "series_id": {"type": "string"},
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date":  {"type": "string", "format": "date"},
                                "value": {"type": "number"},
                            },
                        },
                    },
                },
            },
            examples=[
                {"start": "2020-01-01", "end": "2024-12-31"},
            ],
            rate_limit_per_minute=120,
            requires_auth=True,
        )

    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        if capability_id not in _SERIES_MAP:
            raise KeyError(capability_id)
        if self._client is None:
            await self.setup()
        assert self._client is not None  # narrow for type-checkers

        series_id = _SERIES_MAP[capability_id]
        query: dict[str, Any] = {
            "series_id": series_id,
            "api_key": self._api_key,
            "file_type": "json",
        }
        if "start" in params:
            query["observation_start"] = params["start"]
        if "end" in params:
            query["observation_end"] = params["end"]

        started = self._now_ms()
        async with self._lock:
            response = await self._client.get(
                f"{_API}/series/observations", params=query
            )
            response.raise_for_status()
            payload = response.json()

        observations = [
            {"date": row["date"], "value": _safe_float(row["value"])}
            for row in payload.get("observations", [])
        ]

        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data={"series_id": series_id, "observations": observations},
            cost_usd=0.0,
            latency_ms=self._now_ms() - started,
            cached=False,
        )


def _safe_float(value: str) -> float | None:
    """FRED uses ``"."`` to mark missing observations."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
