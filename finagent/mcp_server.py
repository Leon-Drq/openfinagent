"""
finagent.mcp_server
===================

Expose the configured :class:`ProviderRegistry` as an MCP server over
stdio, so that Claude Code, Cursor, Codex, Continue and any other MCP
client can drive a finagent installation as if it were a native tool.

We deliberately do **not** register each capability as an individual MCP
tool.  The capability surface is too large (10k+ when QVeris is enabled)
and would blow past every client's tool-list ceiling.  Instead we expose
three meta-tools that mirror the provider protocol — ``discover``,
``inspect``, ``call`` — and let the LLM walk the catalog dynamically.
This is the same pattern QVeris itself uses.

Run with:

    finagent mcp serve

Add to a Claude Code or Cursor config:

    {
      "mcpServers": {
        "finagent": { "command": "finagent", "args": ["mcp", "serve"] }
      }
    }
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from finagent.providers.base import Capability, CapabilityMeta
from finagent.runtime.registry import ProviderRegistry


# ---------------------------------------------------------------------------
# JSON encoders for our value objects
# ---------------------------------------------------------------------------


def _capability_to_dict(c: Capability) -> dict[str, Any]:
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "tags": sorted(c.tags),
        "estimated_cost_usd": c.estimated_cost_usd,
    }


def _meta_to_dict(m: CapabilityMeta) -> dict[str, Any]:
    return {
        "capability": _capability_to_dict(m.capability),
        "input_schema": dict(m.input_schema),
        "output_schema": dict(m.output_schema),
        "examples": [dict(e) for e in m.examples],
        "rate_limit_per_minute": m.rate_limit_per_minute,
        "requires_auth": m.requires_auth,
    }


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


async def tool_discover(
    registry: ProviderRegistry,
    query: str,
    provider: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Run ``discover`` across every (or one) provider and merge results."""

    await registry.setup()
    results: list[dict[str, Any]] = []
    for slot in registry._slots:  # noqa: SLF001 — internal access on purpose
        if provider is not None and slot.provider.name != provider:
            continue
        try:
            caps = await slot.provider.discover(query)
        except Exception as exc:  # noqa: BLE001
            results.append(
                {"provider": slot.provider.name, "error": repr(exc)}
            )
            continue
        for cap in caps:
            entry = _capability_to_dict(cap)
            entry["provider"] = slot.provider.name
            results.append(entry)
            if len(results) >= limit:
                return results
    return results


async def tool_inspect(
    registry: ProviderRegistry,
    capability_id: str,
    provider: str | None = None,
) -> dict[str, Any]:
    """Return the schema for ``capability_id`` from the first matching provider."""

    await registry.setup()
    for slot in registry.candidates(capability_id):
        if provider is not None and slot.provider.name != provider:
            continue
        try:
            meta = await slot.provider.inspect(capability_id)
        except KeyError:
            continue
        out = _meta_to_dict(meta)
        out["provider"] = slot.provider.name
        return out
    raise LookupError(f"No provider serves capability {capability_id!r}.")


async def tool_call(
    registry: ProviderRegistry,
    capability_id: str,
    params: dict[str, Any] | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    """Execute a capability and return the wrapped result as plain JSON."""

    result = await registry.call(
        capability_id, provider=provider, **(params or {})
    )
    payload = asdict(result)
    # ``data`` may not be JSON-serialisable (datetimes, dataclasses, …);
    # the registry-level call already returns plain dict/list payloads
    # for builtin providers, but we coerce defensively here too.
    try:
        json.dumps(payload["data"])
    except (TypeError, ValueError):
        payload["data"] = json.loads(json.dumps(payload["data"], default=str))
    return payload


# ---------------------------------------------------------------------------
# Server entry point
# ---------------------------------------------------------------------------


async def serve(registry: ProviderRegistry) -> None:
    """Start the MCP stdio server backed by ``registry``.

    Imported lazily because the ``mcp`` package is an optional install
    extra (``openfinagent[mcp]``).
    """

    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "MCP support requires the 'mcp' package. Install with:\n"
            "    pip install 'openfinagent[mcp]'"
        ) from exc

    server = Server("finagent")

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return [
            Tool(
                name="discover",
                description=(
                    "Search for financial capabilities by free-text query. "
                    "Returns up to `limit` candidates across all configured "
                    "providers. Use this first when you don't know which "
                    "capability id to call."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "provider": {
                            "type": "string",
                            "description": "Optional: restrict to one provider name.",
                        },
                        "limit": {"type": "integer", "default": 20},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="inspect",
                description=(
                    "Return the JSON schema for a capability id, including "
                    "input parameters, output shape, and rate limits. "
                    "Call this before `call` so you know what to pass."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string"},
                        "provider": {"type": "string"},
                    },
                    "required": ["capability_id"],
                },
            ),
            Tool(
                name="call",
                description=(
                    "Execute a capability with the given parameters. The "
                    "runtime applies the configured routing policy and "
                    "budget caps. Returns provider, latency, cost, and the "
                    "data payload."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string"},
                        "params": {"type": "object"},
                        "provider": {"type": "string"},
                    },
                    "required": ["capability_id"],
                },
            ),
        ]

    @server.call_tool()
    async def _call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[TextContent]:
        if name == "discover":
            payload = await tool_discover(
                registry,
                query=arguments["query"],
                provider=arguments.get("provider"),
                limit=int(arguments.get("limit", 20)),
            )
        elif name == "inspect":
            payload = await tool_inspect(
                registry,
                capability_id=arguments["capability_id"],
                provider=arguments.get("provider"),
            )
        elif name == "call":
            payload = await tool_call(
                registry,
                capability_id=arguments["capability_id"],
                params=arguments.get("params"),
                provider=arguments.get("provider"),
            )
        else:
            raise ValueError(f"Unknown tool {name!r}.")

        return [TextContent(type="text", text=json.dumps(payload, indent=2))]

    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
        finally:
            await registry.teardown()
