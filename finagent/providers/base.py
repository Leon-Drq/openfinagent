"""
finagent.providers.base
=======================

The `DataProvider` protocol — a single, minimal interface that every data
source must implement, whether it's a free public API, the QVeris managed
network, or a private feed running inside an institutional VPC.

Design goals
------------
1. **One verb set, three calls.**  All providers expose the same
   ``discover`` -> ``inspect`` -> ``call`` lifecycle.  This is intentionally
   the same vocabulary used by the QVeris MCP, so an LLM agent can drive
   any provider with the same tool definitions.
2. **Async first.**  Every method is ``async``; data fetching is almost
   always I/O-bound and we want to fan out cleanly inside an agent step.
3. **Honest cost reporting.**  Every ``call`` returns a ``CallResult`` that
   carries cost, latency, and a cache flag — the runtime uses these to
   enforce the per-run budget and to write the audit log.
4. **Zero hard dependencies.**  This file imports only from the standard
   library so that vendoring it into a slim runtime (Lambda, Edge, …) is
   painless.

Reference implementations live in ``providers/builtin/``:

    * ``fred.py``    — a free-tier example (FRED economic series).
    * ``qveris.py``  — the recommended production provider.

To bring your own data source, subclass :class:`DataProvider`, implement
the three abstract methods, and register the class in ``config.yaml``.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Mapping, Sequence


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Capability:
    """A single addressable thing a provider can do.

    A capability id is a dot-namespaced string, e.g.
    ``equity.fundamentals.income_statement`` or ``macro.us.cpi.headline``.
    The same logical capability may be served by multiple providers; the
    runtime picks one according to the routing policy.
    """

    id: str
    title: str
    description: str = ""
    tags: frozenset[str] = field(default_factory=frozenset)
    # Estimated USD cost for a single call. ``None`` means free.
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class CapabilityMeta:
    """The full schema of a capability, returned by :meth:`DataProvider.inspect`.

    This is what the agent reads before deciding *how* to call the
    capability — analogous to an OpenAPI operation object.
    """

    capability: Capability
    input_schema: Mapping[str, Any]   # JSON schema for parameters
    output_schema: Mapping[str, Any]  # JSON schema for the return payload
    examples: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    rate_limit_per_minute: int | None = None
    requires_auth: bool = False


@dataclass
class CallResult:
    """Wraps the payload returned by :meth:`DataProvider.call`.

    The runtime never returns raw provider responses to user code; it always
    wraps them so that cost and provenance metadata travel together.
    """

    capability_id: str
    provider: str
    data: Any
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    cached: bool = False
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


class DataProvider(abc.ABC):
    """Abstract base class for every data provider.

    Subclasses must set the four class attributes below and implement the
    three async methods.  Anything else (auth, transport, retries, …) is
    an implementation detail of the concrete provider.

    Attributes
    ----------
    name:
        Stable, machine-readable identifier (``"fred"``, ``"qveris"``,
        ``"my_bloomberg"``).  Used in config files and audit logs.
    namespace:
        The capability prefix this provider claims to serve.  Wildcards are
        allowed: ``{"macro.*", "equity.quote"}``.
    is_free:
        Hint for the routing policy.  A provider that is *technically* free
        but rate-limited can still set this to ``True``.
    requires_credentials:
        If ``True``, the runtime will refuse to start until the relevant
        secret is present in the environment.
    """

    name: str
    namespace: frozenset[str]
    is_free: bool = False
    requires_credentials: bool = False

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def setup(self) -> None:  # noqa: D401 — short hook
        """Optional async setup hook (open clients, warm caches, …)."""

    async def teardown(self) -> None:  # noqa: D401 — short hook
        """Optional async teardown hook."""

    # ------------------------------------------------------------------ #
    # The three required methods
    # ------------------------------------------------------------------ #

    @abc.abstractmethod
    async def discover(self, query: str) -> Sequence[Capability]:
        """Return capabilities matching a free-text query.

        Implementations should rank by relevance.  Returning an empty list
        is fine and signals to the router to try another provider.
        """

    @abc.abstractmethod
    async def inspect(self, capability_id: str) -> CapabilityMeta:
        """Return the full schema for a given capability.

        Raises
        ------
        KeyError
            If the capability is not served by this provider.
        """

    @abc.abstractmethod
    async def call(self, capability_id: str, /, **params: Any) -> CallResult:
        """Execute a capability with the given parameters.

        Implementations are encouraged to use :meth:`_timed` to ensure the
        ``latency_ms`` field is populated consistently.
        """

    # ------------------------------------------------------------------ #
    # Optional streaming
    # ------------------------------------------------------------------ #

    async def stream(
        self, capability_id: str, /, **params: Any
    ) -> AsyncIterator[CallResult]:
        """Optional streaming variant of :meth:`call`.

        Default implementation emits a single result.  Override in
        providers that expose real-time feeds (level-2 quotes, news ticks,
        on-chain events, …).
        """

        yield await self.call(capability_id, **params)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def serves(self, capability_id: str) -> bool:
        """Quick check: does this provider claim to serve ``capability_id``?

        Used by the router before paying the cost of a real ``inspect``.
        """

        for pattern in self.namespace:
            if pattern == capability_id:
                return True
            if pattern.endswith(".*") and capability_id.startswith(pattern[:-1]):
                return True
        return False

    @staticmethod
    def _now_ms() -> float:
        return time.perf_counter() * 1000.0
