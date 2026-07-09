"""
finagent
========

Open-source workspace for financial agents.

Public API
----------
The objects re-exported here are the stable surface for library users.
Everything inside private submodules (``finagent.runtime._*``,
``finagent.providers.builtin.*``) is considered internal and may change
between minor versions.
"""

from __future__ import annotations

__version__ = "0.2.0"

from finagent.providers.base import (
    Capability,
    CapabilityMeta,
    CallResult,
    DataProvider,
)
from finagent.runtime.registry import ProviderRegistry, RoutingPolicy
from finagent.runtime.runner import Runner, RunResult

__all__ = [
    "__version__",
    "Capability",
    "CapabilityMeta",
    "CallResult",
    "DataProvider",
    "ProviderRegistry",
    "RoutingPolicy",
    "Runner",
    "RunResult",
]
