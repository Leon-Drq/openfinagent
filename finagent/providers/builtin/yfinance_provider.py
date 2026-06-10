"""
finagent.providers.builtin.yfinance_provider
============================================

A real, keyless :class:`DataProvider` backed by the ``yfinance`` package.
This is the lowest-friction provider in the project — anyone can install
``openfinagent`` and immediately fetch quotes, fundamentals, and
analyst estimates without registering anywhere.

Capabilities served
-------------------

* ``equity.quote``                  — last price, day range, volume
* ``equity.profile``                — sector, industry, summary
* ``equity.fundamentals.income``    — last 4 annual income statements
* ``equity.fundamentals.balance``   — last 4 annual balance sheets
* ``equity.fundamentals.cashflow``  — last 4 annual cash-flow statements
* ``equity.analyst.targets``        — analyst price targets snapshot
* ``equity.news``                   — recent headline links

The ``yfinance`` package scrapes Yahoo Finance and may break without
notice; it is **not** appropriate for production trading.  Use the
QVeris provider for anything that touches money.
"""

from __future__ import annotations

import asyncio
from typing import Any, Sequence

from finagent.providers.base import (
    Capability,
    CapabilityMeta,
    CallResult,
    DataProvider,
)

# Lazy import: only blow up if a user actually constructs the provider.
try:
    import yfinance as _yf  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - import-time fallback
    _yf = None


_TICKER_PARAM = {
    "ticker": {
        "type": "string",
        "description": "Ticker symbol (e.g. NVDA, AAPL, BRK-B).",
    }
}


_CATALOG: dict[str, Capability] = {
    "equity.quote": Capability(
        id="equity.quote",
        title="Equity quote",
        description="Last price, day range, and volume for a US-listed equity.",
        tags=frozenset({"equity", "quote", "us"}),
        estimated_cost_usd=0.0,
    ),
    "equity.profile": Capability(
        id="equity.profile",
        title="Equity company profile",
        description="Sector, industry, and a short business summary.",
        tags=frozenset({"equity", "profile"}),
        estimated_cost_usd=0.0,
    ),
    "equity.fundamentals.income": Capability(
        id="equity.fundamentals.income",
        title="Income statements (annual)",
        description="Last four annual income statements as a list of rows.",
        tags=frozenset({"equity", "fundamentals", "income"}),
        estimated_cost_usd=0.0,
    ),
    "equity.fundamentals.balance": Capability(
        id="equity.fundamentals.balance",
        title="Balance sheets (annual)",
        description="Last four annual balance sheets as a list of rows.",
        tags=frozenset({"equity", "fundamentals", "balance"}),
        estimated_cost_usd=0.0,
    ),
    "equity.fundamentals.cashflow": Capability(
        id="equity.fundamentals.cashflow",
        title="Cash-flow statements (annual)",
        description="Last four annual cash-flow statements.",
        tags=frozenset({"equity", "fundamentals", "cashflow"}),
        estimated_cost_usd=0.0,
    ),
    "equity.analyst.targets": Capability(
        id="equity.analyst.targets",
        title="Analyst price targets",
        description="Sell-side mean / median / high / low price targets.",
        tags=frozenset({"equity", "analyst", "consensus"}),
        estimated_cost_usd=0.0,
    ),
    "equity.news": Capability(
        id="equity.news",
        title="Recent news headlines",
        description="Most recent news headlines for a ticker (titles + links).",
        tags=frozenset({"equity", "news"}),
        estimated_cost_usd=0.0,
    ),
}


class YFinanceProvider(DataProvider):
    """Free, keyless adapter over the ``yfinance`` Python package."""

    name = "yfinance"
    namespace = frozenset({"equity.*"})
    is_free = True
    requires_credentials = False

    def __init__(self) -> None:
        if _yf is None:
            raise RuntimeError(
                "YFinanceProvider requires the 'yfinance' package. "
                "Install it with: pip install yfinance"
            )

    # ------------------------------------------------------------------ #
    # Required methods
    # ------------------------------------------------------------------ #

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
            examples=[{"ticker": "NVDA"}, {"ticker": "AAPL"}],
            rate_limit_per_minute=60,
            requires_auth=False,
        )

    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        if capability_id not in _CATALOG:
            raise KeyError(capability_id)
        ticker = params.get("ticker")
        if not ticker:
            raise ValueError(f"{capability_id} requires a 'ticker' parameter")

        started = self._now_ms()
        # yfinance is sync and uses requests under the hood — push to a
        # worker thread so we don't block the event loop.
        data = await asyncio.to_thread(self._fetch, capability_id, str(ticker).upper())
        latency = self._now_ms() - started

        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data=data,
            cost_usd=0.0,
            latency_ms=latency,
            cached=False,
        )

    # ------------------------------------------------------------------ #
    # Internal: actually call yfinance
    # ------------------------------------------------------------------ #

    def _fetch(self, capability_id: str, ticker: str) -> dict[str, Any]:
        t = _yf.Ticker(ticker)

        if capability_id == "equity.quote":
            info = _safe_info(t)
            return {
                "ticker": ticker,
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "currency": info.get("currency"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "previous_close": info.get("previousClose"),
            }

        if capability_id == "equity.profile":
            info = _safe_info(t)
            return {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "website": info.get("website"),
                "summary": info.get("longBusinessSummary"),
                "employees": info.get("fullTimeEmployees"),
            }

        if capability_id == "equity.fundamentals.income":
            return {"ticker": ticker, "rows": _df_to_rows(t.income_stmt)}

        if capability_id == "equity.fundamentals.balance":
            return {"ticker": ticker, "rows": _df_to_rows(t.balance_sheet)}

        if capability_id == "equity.fundamentals.cashflow":
            return {"ticker": ticker, "rows": _df_to_rows(t.cashflow)}

        if capability_id == "equity.analyst.targets":
            try:
                targets = t.analyst_price_targets  # type: ignore[attr-defined]
            except Exception:
                targets = None
            return {"ticker": ticker, "targets": targets or {}}

        if capability_id == "equity.news":
            news_raw = list(getattr(t, "news", []) or [])[:10]
            return {
                "ticker": ticker,
                "items": [
                    {
                        "title": item.get("title"),
                        "publisher": item.get("publisher"),
                        "link": item.get("link"),
                        "published_at": item.get("providerPublishTime"),
                    }
                    for item in news_raw
                    if isinstance(item, dict)
                ],
            }

        raise KeyError(capability_id)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _safe_info(ticker_obj: Any) -> dict[str, Any]:
    """``Ticker.info`` occasionally raises; fall back to an empty dict."""

    try:
        info = ticker_obj.info or {}
    except Exception:  # pragma: no cover - defensive
        info = {}
    return dict(info) if isinstance(info, dict) else {}


def _df_to_rows(df: Any) -> list[dict[str, Any]]:
    """Convert a yfinance pandas DataFrame to a JSON-friendly list of rows.

    Each row keys by metric name and contains period -> value mappings.
    Returns an empty list if the DataFrame is missing or empty.
    """

    if df is None:
        return []
    try:
        if df.empty:
            return []
    except Exception:
        return []

    rows: list[dict[str, Any]] = []
    columns = [str(c) for c in df.columns]
    for metric, series in df.iterrows():
        row: dict[str, Any] = {"metric": str(metric)}
        for col, value in zip(columns, series.tolist()):
            row[col] = _coerce_number(value)
        rows.append(row)
    return rows


def _coerce_number(value: Any) -> Any:
    """Make values JSON-serialisable; turn NaN into ``None``."""

    try:
        # Most yfinance numbers come back as numpy float64; cast and detect NaN.
        f = float(value)
        if f != f:  # NaN check without importing math
            return None
        return f
    except (TypeError, ValueError):
        return value if value is not None else None
