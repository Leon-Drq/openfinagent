"""
finagent.runtime.registry
=========================

Provider registry + routing policy + the per-run cost guard.

Responsibilities
----------------
1. Build provider instances from a declarative ``config.yaml``.
2. Pick the right provider for a given ``capability_id`` according to
   the active :class:`RoutingPolicy`.
3. Track cumulative spend on the current run and abort if it crosses the
   declared budget.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable

from finagent.providers.base import CallResult, DataProvider


class RoutingPolicy(str, Enum):
    """How to break ties when multiple providers can serve a capability.

    * ``PREFER_FREE``     — exhaust free / low-priority providers first.
    * ``PREFER_QUALITY``  — try the highest-priority (paid) provider first.
    * ``EXPLICIT``        — caller must specify a provider name; never fall back.
    """

    PREFER_FREE = "prefer_free"
    PREFER_QUALITY = "prefer_quality"
    EXPLICIT = "explicit"


# ---------------------------------------------------------------------------
# Config records (parsed from YAML)
# ---------------------------------------------------------------------------


@dataclass
class ProviderConfig:
    name: str
    type: str
    priority: int = 5
    options: dict[str, Any] = field(default_factory=dict)
    budget_usd_per_run: float | None = None


# ---------------------------------------------------------------------------
# Budget exception
# ---------------------------------------------------------------------------


class BudgetExceeded(RuntimeError):
    """Raised when a workflow tries to spend more than the per-run cap."""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass
class _Slot:
    """One registered provider plus the priority/budget metadata."""

    provider: DataProvider
    priority: int
    budget_usd_per_run: float | None
    spent_usd: float = 0.0


class ProviderRegistry:
    """A pool of providers plus the routing logic that selects between them.

    The registry is created once per ``Runner.run()`` invocation; spend
    counters reset every run.
    """

    def __init__(
        self,
        slots: Iterable[_Slot] | None = None,
        *,
        policy: RoutingPolicy = RoutingPolicy.PREFER_FREE,
        global_budget_usd: float | None = None,
    ) -> None:
        self._slots: list[_Slot] = list(slots or [])
        self._policy = policy
        self._global_budget_usd = global_budget_usd
        self._global_spent_usd = 0.0
        self._setup_done = False
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #

    @classmethod
    def from_configs(
        cls,
        configs: list[ProviderConfig],
        *,
        policy: RoutingPolicy = RoutingPolicy.PREFER_FREE,
        global_budget_usd: float | None = None,
    ) -> ProviderRegistry:
        """Instantiate the registry from a parsed YAML provider list."""

        # Imported lazily to avoid a hard cycle at import time.
        from finagent.providers.builtin import BUILTIN_PROVIDERS

        slots: list[_Slot] = []
        for config in configs:
            provider_cls = BUILTIN_PROVIDERS.get(config.type)
            if provider_cls is None:
                # Custom user provider: dotted import path
                provider_cls = _import_dotted(config.type)
            instance = provider_cls(**config.options)
            # Override the user-facing name when the YAML overrides it.
            if config.name and config.name != getattr(instance, "name", None):
                instance.name = config.name
            slots.append(
                _Slot(
                    provider=instance,
                    priority=config.priority,
                    budget_usd_per_run=config.budget_usd_per_run,
                )
            )
        return cls(slots, policy=policy, global_budget_usd=global_budget_usd)

    def add(
        self,
        provider: DataProvider,
        *,
        priority: int = 5,
        budget_usd_per_run: float | None = None,
    ) -> None:
        """Register a provider directly (handy for tests and notebooks)."""

        self._slots.append(
            _Slot(
                provider=provider,
                priority=priority,
                budget_usd_per_run=budget_usd_per_run,
            )
        )

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def setup(self) -> None:
        if self._setup_done:
            return
        await asyncio.gather(*(slot.provider.setup() for slot in self._slots))
        self._setup_done = True

    async def teardown(self) -> None:
        await asyncio.gather(
            *(slot.provider.teardown() for slot in self._slots),
            return_exceptions=True,
        )
        self._setup_done = False

    # ------------------------------------------------------------------ #
    # Discovery / call
    # ------------------------------------------------------------------ #

    def candidates(self, capability_id: str) -> list[_Slot]:
        """Return slots that claim to serve ``capability_id``, in route order."""

        matching = [s for s in self._slots if s.provider.serves(capability_id)]
        if self._policy is RoutingPolicy.PREFER_QUALITY:
            matching.sort(key=lambda s: -s.priority)
        else:  # PREFER_FREE / EXPLICIT both walk in priority-ascending order
            matching.sort(key=lambda s: s.priority)
        return matching

    async def call(
        self,
        capability_id: str,
        /,
        provider: str | None = None,
        **params: Any,
    ) -> CallResult:
        """Execute ``capability_id`` on the first matching provider.

        If ``provider`` is given, only that provider is tried (matches
        ``RoutingPolicy.EXPLICIT`` semantics).
        """

        await self.setup()

        slots = self.candidates(capability_id)
        if provider is not None:
            slots = [s for s in slots if s.provider.name == provider]
            if not slots:
                raise LookupError(
                    f"No registered provider named {provider!r} serves "
                    f"{capability_id!r}."
                )

        if not slots:
            raise LookupError(
                f"No registered provider serves capability {capability_id!r}. "
                f"Configured providers: {[s.provider.name for s in self._slots]}"
            )

        last_error: Exception | None = None
        for slot in slots:
            try:
                result = await slot.provider.call(capability_id, **params)
            except KeyError as exc:
                # Provider doesn't actually have this capability; try next.
                last_error = exc
                continue
            await self._charge(slot, result)
            return result

        raise LookupError(
            f"All providers refused capability {capability_id!r}: {last_error!r}"
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    async def _charge(self, slot: _Slot, result: CallResult) -> None:
        """Update spend counters and enforce budgets."""

        async with self._lock:
            slot.spent_usd += result.cost_usd
            self._global_spent_usd += result.cost_usd

            if (
                slot.budget_usd_per_run is not None
                and slot.spent_usd > slot.budget_usd_per_run
            ):
                raise BudgetExceeded(
                    f"Provider {slot.provider.name!r} exceeded per-run "
                    f"budget of ${slot.budget_usd_per_run:.2f} "
                    f"(spent ${slot.spent_usd:.2f})."
                )
            if (
                self._global_budget_usd is not None
                and self._global_spent_usd > self._global_budget_usd
            ):
                raise BudgetExceeded(
                    f"Run exceeded global budget of "
                    f"${self._global_budget_usd:.2f} "
                    f"(spent ${self._global_spent_usd:.2f})."
                )

    @property
    def total_spent_usd(self) -> float:
        return self._global_spent_usd

    @property
    def providers(self) -> list[DataProvider]:
        return [slot.provider for slot in self._slots]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _import_dotted(path: str) -> type[DataProvider]:
    """Import a dotted ``module.ClassName`` path and return the class."""

    if ":" in path:
        module_name, class_name = path.split(":", 1)
    elif "." in path:
        module_name, class_name = path.rsplit(".", 1)
    else:
        raise ValueError(
            f"Custom provider type {path!r} must be 'pkg.module:Class' "
            f"or 'pkg.module.Class'."
        )

    import importlib

    module = importlib.import_module(module_name)
    klass = getattr(module, class_name)
    if not isinstance(klass, type) or not issubclass(klass, DataProvider):
        raise TypeError(
            f"{path!r} does not resolve to a DataProvider subclass."
        )
    return klass
