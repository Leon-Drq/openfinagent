"""
finagent.providers.builtin.sample
=================================

Deterministic, keyless sample data for first-run demos and tests.

The sample provider intentionally does not hit the network and does not
pretend to be live market data. It serves a narrow subset of the normal
provider protocol so `finagent demo NVDA` can produce a complete report
without API keys, credentials, or an LLM call.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Sequence

from finagent.providers.base import (
    Capability,
    CapabilityMeta,
    CallResult,
    DataProvider,
)


_TICKER_PARAM = {
    "ticker": {
        "type": "string",
        "description": "Sample ticker symbol: NVDA, AAPL, or MSFT.",
    }
}


_CATALOG: dict[str, Capability] = {
    "equity.quote": Capability(
        id="equity.quote",
        title="Sample equity quote",
        description="Deterministic quote snapshot for the demo workflow.",
        tags=frozenset({"sample", "equity", "quote"}),
        estimated_cost_usd=0.0,
    ),
    "equity.profile": Capability(
        id="equity.profile",
        title="Sample company profile",
        description="Deterministic company profile for the demo workflow.",
        tags=frozenset({"sample", "equity", "profile"}),
        estimated_cost_usd=0.0,
    ),
    "filings.recent": Capability(
        id="filings.recent",
        title="Sample SEC filings",
        description="Deterministic filing metadata for the demo workflow.",
        tags=frozenset({"sample", "filings", "sec"}),
        estimated_cost_usd=0.0,
    ),
}


_SAMPLE_DATA: dict[str, dict[str, Any]] = {
    "NVDA": {
        "profile": {
            "ticker": "NVDA",
            "name": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "country": "United States",
            "website": "https://www.nvidia.com",
            "employees": 29600,
            "summary": (
                "NVIDIA designs accelerated computing platforms spanning GPUs, "
                "networking, systems software, and AI infrastructure."
            ),
            "sample_as_of": "2026-04-29",
        },
        "quote": {
            "ticker": "NVDA",
            "price": 126.47,
            "currency": "USD",
            "day_high": 128.19,
            "day_low": 123.84,
            "volume": 318442000,
            "market_cap": 3110000000000,
            "previous_close": 124.91,
            "sample_as_of": "2026-04-29",
        },
        "filings": [
            {
                "form": "10-K",
                "filing_date": "2026-02-26",
                "report_date": "2026-01-26",
                "accession": "sample-nvda-10k",
                "url": "https://www.sec.gov/edgar/search/",
            },
            {
                "form": "10-Q",
                "filing_date": "2025-11-20",
                "report_date": "2025-10-27",
                "accession": "sample-nvda-10q",
                "url": "https://www.sec.gov/edgar/search/",
            },
            {
                "form": "8-K",
                "filing_date": "2025-08-28",
                "report_date": "2025-08-27",
                "accession": "sample-nvda-8k",
                "url": "https://www.sec.gov/edgar/search/",
            },
        ],
    },
    "AAPL": {
        "profile": {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "United States",
            "website": "https://www.apple.com",
            "employees": 164000,
            "summary": (
                "Apple designs consumer devices, software platforms, and services "
                "with a vertically integrated hardware and ecosystem strategy."
            ),
            "sample_as_of": "2026-04-29",
        },
        "quote": {
            "ticker": "AAPL",
            "price": 198.22,
            "currency": "USD",
            "day_high": 200.10,
            "day_low": 196.42,
            "volume": 57200000,
            "market_cap": 2970000000000,
            "previous_close": 197.55,
            "sample_as_of": "2026-04-29",
        },
        "filings": [
            {
                "form": "10-K",
                "filing_date": "2025-11-01",
                "report_date": "2025-09-27",
                "accession": "sample-aapl-10k",
                "url": "https://www.sec.gov/edgar/search/",
            },
            {
                "form": "10-Q",
                "filing_date": "2026-02-02",
                "report_date": "2025-12-27",
                "accession": "sample-aapl-10q",
                "url": "https://www.sec.gov/edgar/search/",
            },
        ],
    },
    "MSFT": {
        "profile": {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software - Infrastructure",
            "country": "United States",
            "website": "https://www.microsoft.com",
            "employees": 228000,
            "summary": (
                "Microsoft provides cloud infrastructure, productivity software, "
                "business applications, gaming, and AI platform services."
            ),
            "sample_as_of": "2026-04-29",
        },
        "quote": {
            "ticker": "MSFT",
            "price": 431.18,
            "currency": "USD",
            "day_high": 435.00,
            "day_low": 428.45,
            "volume": 22400000,
            "market_cap": 3200000000000,
            "previous_close": 430.02,
            "sample_as_of": "2026-04-29",
        },
        "filings": [
            {
                "form": "10-K",
                "filing_date": "2025-07-30",
                "report_date": "2025-06-30",
                "accession": "sample-msft-10k",
                "url": "https://www.sec.gov/edgar/search/",
            },
            {
                "form": "10-Q",
                "filing_date": "2026-01-28",
                "report_date": "2025-12-31",
                "accession": "sample-msft-10q",
                "url": "https://www.sec.gov/edgar/search/",
            },
        ],
    },
}


class SampleProvider(DataProvider):
    """Offline demo provider with deterministic sample data."""

    name = "sample"
    namespace = frozenset({"equity.*", "filings.*"})
    is_free = True
    requires_credentials = False

    async def discover(self, query: str) -> Sequence[Capability]:
        q = query.lower().strip()
        if not q:
            return list(_CATALOG.values())
        return [
            cap
            for cap in _CATALOG.values()
            if q in cap.id
            or q in cap.title.lower()
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
                "properties": _TICKER_PARAM,
                "required": ["ticker"],
            },
            output_schema={"type": "object"},
            examples=[{"ticker": "NVDA"}, {"ticker": "AAPL"}, {"ticker": "MSFT"}],
            rate_limit_per_minute=None,
            requires_auth=False,
        )

    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        if capability_id not in _CATALOG:
            raise KeyError(capability_id)

        ticker = str(params.get("ticker") or "NVDA").upper().strip()
        if ticker not in _SAMPLE_DATA:
            supported = ", ".join(sorted(_SAMPLE_DATA))
            raise ValueError(
                f"SampleProvider only includes {supported}; got {ticker!r}."
            )

        company = _SAMPLE_DATA[ticker]
        if capability_id == "equity.profile":
            data = company["profile"]
        elif capability_id == "equity.quote":
            data = company["quote"]
        else:
            forms = {str(f).upper() for f in params.get("forms") or []}
            limit = int(params.get("limit") or 10)
            filings = [
                filing
                for filing in company["filings"]
                if not forms or filing["form"] in forms
            ][:limit]
            data = {"ticker": ticker, "cik": "sample", "filings": filings}

        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data=deepcopy(data),
            cost_usd=0.0,
            latency_ms=0.0,
            cached=True,
        )
