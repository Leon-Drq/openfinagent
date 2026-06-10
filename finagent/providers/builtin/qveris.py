"""
finagent.providers.builtin.qveris
=================================

The recommended production :class:`DataProvider` — a thin adapter over
the QVeris capability routing network.  In one call it brings 10,000+
verified financial capabilities (market data, fundamentals, filings,
alternative data, …) under the same protocol as a free or BYO provider.

Why a single provider for 10k+ capabilities?
--------------------------------------------
QVeris itself does the second-level routing: when we ask it to
``equity.fundamentals.income_statement``, QVeris picks the upstream
vendor that can serve it best, normalises the response, and reports the
true cost back to us.  From the agent's point of view it's still one
``DataProvider`` — which keeps the routing layer simple.

Usage
-----

.. code-block:: yaml

    # config.yaml
    providers:
      - name: qveris
        type: builtin.qveris
        priority: 2                 # fall back to QVeris when free tiers don't cover it
        api_key: ${QVERIS_API_KEY}
        budget_usd_per_run: 5.00    # hard cap, runtime aborts if exceeded
"""

from __future__ import annotations

import os
from typing import Any, Sequence

import httpx

from ..base import Capability, CapabilityMeta, CallResult, DataProvider


_DEFAULT_BASE_URL = "https://api.qveris.ai/v1"


class QverisProvider(DataProvider):
    """Adapter for the QVeris capability network.

    The wire protocol used here is illustrative — the real one is the
    MCP transport.  We keep this REST shim so the provider works in
    environments without an MCP client (CI, edge runtimes, …).
    """

    name = "qveris"
    # We claim everything: QVeris's whole point is broad coverage.
    namespace = frozenset({"*"})
    is_free = False
    requires_credentials = True

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = _DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("QVERIS_API_KEY")
        if not self._api_key:
            raise RuntimeError(
                "QverisProvider requires QVERIS_API_KEY. "
                "Get one at https://qveris.ai or run `finagent auth login`."
            )
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def setup(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "User-Agent": "openfinagent/0.1",
            },
        )

    async def teardown(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    # ------------------------------------------------------------------ #
    # Override `serves` — QVeris claims everything, so the router only
    # falls through to it after cheaper providers say no.
    # ------------------------------------------------------------------ #

    def serves(self, capability_id: str) -> bool:  # noqa: D401 — short
        return True

    # ------------------------------------------------------------------ #
    # Required methods
    # ------------------------------------------------------------------ #

    async def discover(self, query: str) -> Sequence[Capability]:
        client = await self._get_client()
        response = await client.post("/discover", json={"query": query, "limit": 20})
        response.raise_for_status()
        items = response.json().get("results", [])
        return [
            Capability(
                id=item["id"],
                title=item["title"],
                description=item.get("description", ""),
                tags=frozenset(item.get("tags", [])),
                estimated_cost_usd=item.get("estimated_cost_usd"),
            )
            for item in items
        ]

    async def inspect(self, capability_id: str) -> CapabilityMeta:
        client = await self._get_client()
        response = await client.get(f"/capabilities/{capability_id}")
        if response.status_code == 404:
            raise KeyError(capability_id)
        response.raise_for_status()
        body = response.json()

        return CapabilityMeta(
            capability=Capability(
                id=body["id"],
                title=body["title"],
                description=body.get("description", ""),
                tags=frozenset(body.get("tags", [])),
                estimated_cost_usd=body.get("estimated_cost_usd"),
            ),
            input_schema=body["input_schema"],
            output_schema=body["output_schema"],
            examples=body.get("examples", []),
            rate_limit_per_minute=body.get("rate_limit_per_minute"),
            requires_auth=True,
        )

    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        client = await self._get_client()
        started = self._now_ms()
        response = await client.post(
            f"/capabilities/{capability_id}/invoke",
            json={"params": params},
        )
        response.raise_for_status()
        body = response.json()

        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data=body["data"],
            # QVeris reports the *actual* upstream cost in the response —
            # never the agent's guess.  This is the audit-log source of truth.
            cost_usd=float(body.get("cost_usd", 0.0)),
            latency_ms=self._now_ms() - started,
            cached=bool(body.get("cached", False)),
            trace_id=body.get("trace_id") or CallResult.__dataclass_fields__["trace_id"].default_factory(),  # type: ignore[arg-type]
        )

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            await self.setup()
        assert self._client is not None
        return self._client
