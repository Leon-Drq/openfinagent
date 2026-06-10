"""
finagent.providers.builtin.sec_edgar
====================================

A keyless :class:`DataProvider` backed by the SEC EDGAR public API.

EDGAR requires only a polite ``User-Agent`` header (per the SEC's fair-use
policy) and is rate-limited to ~10 req/sec.  We send a contact string of
the form ``openfinagent/<version> <contact>``.  Set ``SEC_USER_AGENT``
in the environment to your own contact email if you publish heavy
workflows; the default is a generic one.

Capabilities served
-------------------

* ``filings.recent`` — list the most recent filings for a ticker (10-K,
  10-Q, 8-K by default).  Returns metadata with direct EDGAR URLs.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Sequence

import httpx

from finagent.providers.base import (
    Capability,
    CapabilityMeta,
    CallResult,
    DataProvider,
)

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"

_DEFAULT_USER_AGENT = (
    "openfinagent/0.1 (https://github.com/Leon-Drq/openfinagent)"
)


_CATALOG: dict[str, Capability] = {
    "filings.recent": Capability(
        id="filings.recent",
        title="Recent SEC filings",
        description="Most recent EDGAR filings for a US-listed company.",
        tags=frozenset({"filings", "sec", "edgar", "us"}),
        estimated_cost_usd=0.0,
    ),
}


class SecEdgarProvider(DataProvider):
    """Read-only adapter for SEC EDGAR (filings index)."""

    name = "sec_edgar"
    namespace = frozenset({"filings.*"})
    is_free = True
    requires_credentials = False

    def __init__(self, user_agent: str | None = None) -> None:
        self._user_agent = (
            user_agent or os.environ.get("SEC_USER_AGENT") or _DEFAULT_USER_AGENT
        )
        self._client: httpx.AsyncClient | None = None
        self._ticker_index: dict[str, int] | None = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def setup(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=15.0,
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json",
            },
        )

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
            if q in cap.id or q in cap.title.lower() or q in cap.description.lower()
        ]

    async def inspect(self, capability_id: str) -> CapabilityMeta:
        if capability_id not in _CATALOG:
            raise KeyError(capability_id)
        return CapabilityMeta(
            capability=_CATALOG[capability_id],
            input_schema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "forms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filing forms to keep (e.g. 10-K, 10-Q, 8-K).",
                    },
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["ticker"],
            },
            output_schema={"type": "object"},
            examples=[
                {"ticker": "NVDA", "forms": ["10-K", "10-Q"], "limit": 5},
            ],
            rate_limit_per_minute=600,  # SEC fair use is ~10 req/sec
            requires_auth=False,
        )

    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        if capability_id != "filings.recent":
            raise KeyError(capability_id)

        ticker = str(params.get("ticker", "")).upper().strip()
        if not ticker:
            raise ValueError("filings.recent requires a 'ticker' parameter")
        forms = {f.upper() for f in params.get("forms") or ["10-K", "10-Q", "8-K"]}
        limit = int(params.get("limit") or 10)

        started = self._now_ms()
        cik = await self._lookup_cik(ticker)
        filings = await self._recent_filings(cik, forms=forms, limit=limit)
        latency = self._now_ms() - started

        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data={"ticker": ticker, "cik": cik, "filings": filings},
            cost_usd=0.0,
            latency_ms=latency,
            cached=False,
        )

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            await self.setup()
        assert self._client is not None
        return self._client

    async def _lookup_cik(self, ticker: str) -> int:
        async with self._lock:
            if self._ticker_index is None:
                client = await self._get_client()
                response = await client.get(_TICKERS_URL)
                response.raise_for_status()
                payload = response.json()
                # The endpoint returns ``{"0": {"cik_str": ..., "ticker": ...}, ...}``.
                self._ticker_index = {
                    str(item["ticker"]).upper(): int(item["cik_str"])
                    for item in payload.values()
                    if isinstance(item, dict) and "ticker" in item
                }
        cik = self._ticker_index.get(ticker)
        if cik is None:
            raise ValueError(f"Unknown ticker on EDGAR: {ticker}")
        return cik

    async def _recent_filings(
        self, cik: int, *, forms: set[str], limit: int
    ) -> list[dict[str, Any]]:
        client = await self._get_client()
        response = await client.get(_SUBMISSIONS_URL.format(cik=cik))
        response.raise_for_status()
        body = response.json()
        recent = body.get("filings", {}).get("recent", {}) or {}

        accession_numbers = recent.get("accessionNumber", [])
        primary_documents = recent.get("primaryDocument", [])
        forms_list = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])

        out: list[dict[str, Any]] = []
        for i, form in enumerate(forms_list):
            if forms and form not in forms:
                continue
            accession = accession_numbers[i] if i < len(accession_numbers) else ""
            primary = primary_documents[i] if i < len(primary_documents) else ""
            accession_clean = accession.replace("-", "")
            url = (
                f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                f"{accession_clean}/{primary}"
                if accession_clean and primary
                else None
            )
            out.append(
                {
                    "form": form,
                    "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                    "report_date": report_dates[i] if i < len(report_dates) else None,
                    "accession": accession,
                    "url": url,
                }
            )
            if len(out) >= limit:
                break
        return out
