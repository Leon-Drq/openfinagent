# Data Providers — Design Overview

> *One protocol. Any combination. No vendor lock-in.*

This document explains **why** OpenFinAgent puts every data source —
free, paid, public, private — behind a single `DataProvider` protocol,
and **how** the runtime routes between them at agent-call time.

If you are looking for the API reference, see
[`providers/base.py`](../../providers/base.py). If you want to ship a
new provider in 50 lines, jump to [Writing your own](#writing-your-own).

---

## Table of contents

1. [The problem we are solving](#the-problem-we-are-solving)
2. [The three-tier supply model](#the-three-tier-supply-model)
3. [The protocol in one screen](#the-protocol-in-one-screen)
4. [Routing policy](#routing-policy)
5. [Cost guard and audit log](#cost-guard-and-audit-log)
6. [Configuration recipes](#configuration-recipes)
7. [Writing your own provider](#writing-your-own)
8. [FAQ](#faq)

---

## The problem we are solving

A useful financial AI agent has to read a lot of data. In practice this
data is scattered across:

* **Free public APIs** — FRED, SEC EDGAR, BLS, IMF, yfinance, CoinGecko.
  Cheap and ubiquitous, but each has its own SDK, auth scheme, rate
  limit, and idiosyncratic schema.
* **Premium aggregators** — QVeris, Refinitiv, FactSet, S&P, Bloomberg.
  Broad coverage, normalised schemas, real SLAs — but priced per call
  and locked behind enterprise procurement.
* **Internal feeds** — the proprietary research database your team has
  spent five years building, the CSV exports your PM emails on Friday,
  the on-prem Bloomberg terminal feed your compliance team will not let
  leave the building.

Most existing financial agent projects pick *one* tier and bolt the
others on as second-class citizens. That is the wrong abstraction. From
the agent's point of view, **a data source is a thing that answers
questions** — its commercial model and network location are implementation
details. So we hide all three behind one interface.

---

## The three-tier supply model

| Tier | Examples | Typical user | Cost shape |
|------|----------|--------------|------------|
| **1. Free & Public** | FRED · yfinance · SEC EDGAR · CoinGecko · Alpha Vantage free | Students, individual researchers, prototype phase | $0 (rate-limited) |
| **2. QVeris** *(recommended)* | One adapter, 10,000+ verified capabilities | Production users who want breadth without 30 vendor contracts | Pay per call; runtime enforces budget |
| **3. Bring Your Own (BYO)** | Bloomberg · Refinitiv · FactSet · S&P · internal SQL · proprietary CSVs | Institutions, compliance-sensitive workflows, data already paid for | Whatever your contract says; runtime never proxies your credentials |

A few non-obvious consequences of this model:

* **Tier 1 lets us be honest about onboarding.** A new user can install
  the package, run a workflow, and see a real answer in five minutes —
  no credit card, no signup. That is what makes the project adoptable.
* **Tier 2 is *recommended but never required*.** Calling QVeris the
  "default" tier would set the wrong expectation — the runtime works
  with any subset of providers, including only Tier 1 or only Tier 3.
* **Tier 3 is not an afterthought.** Many institutional users will *only*
  ship a project that lets them keep proprietary data inside their VPC.
  We treat the BYO path as a first-class citizen with its own templates
  and tests.

---

## The protocol in one screen

```python
class DataProvider(abc.ABC):
    name: str                        # "fred", "qveris", "my_bloomberg"
    namespace: frozenset[str]        # {"macro.us.*", "equity.quote"}
    is_free: bool = False
    requires_credentials: bool = False

    async def discover(self, query: str) -> Sequence[Capability]: ...
    async def inspect(self, capability_id: str) -> CapabilityMeta: ...
    async def call(self, capability_id: str, /, **params) -> CallResult: ...
```

Three verbs, deliberately mirroring the QVeris MCP vocabulary so an LLM
can drive a free provider with the same tool definitions it uses for the
paid one.

* **`discover`** — natural-language search returning a ranked list of
  capabilities the provider can serve. Cheap, often cached.
* **`inspect`** — return the full input/output JSON schema for one
  capability so the agent knows how to call it. Also cheap.
* **`call`** — actually execute the capability and return a `CallResult`
  carrying the data, the **true** USD cost, latency, and a trace id.

That is the entire surface area. Streaming, batching, and retries are
optional and live in the base class as default implementations.

---

## Routing policy

The runtime ships with three policies; pick one in `config.yaml` or
override per-workflow.

| Policy | Behaviour | When to use |
|--------|-----------|-------------|
| `prefer_free` *(default)* | Try Tier 1 providers first; fall through to Tier 2/3 only when free providers cannot serve the capability. | Cost-sensitive research, education, demos. |
| `prefer_quality` | Try the highest-priority provider for each capability, regardless of price, within the per-run budget. | Production research where freshness and accuracy beat cost. |
| `explicit` | The workflow YAML names the provider for each step; the router only enforces budgets. | Reproducible institutional pipelines, regulated environments. |

Routing is **per-capability**, not per-provider. A single workflow step
can read GDP from FRED, fundamentals from QVeris, and a proprietary
factor score from your internal feed — without the agent caring.

```text
agent.call("equity.fundamentals.income_statement", ticker="NVDA")
        │
        ▼
   router scans providers in priority order:
     0. my_bloomberg  -> serves? no  (namespace mismatch)
     1. fred          -> serves? no
     2. qveris        -> serves? yes -> dispatch
        │
        ▼
   QverisProvider.call(...) -> CallResult(cost=$0.012, latency=420ms)
        │
        ▼
   audit log + budget tracker + DuckDB cache
```

---

## Cost guard and audit log

Every `CallResult` carries:

```python
CallResult(
    capability_id="equity.fundamentals.income_statement",
    provider="qveris",
    data={...},
    cost_usd=0.012,
    latency_ms=423.7,
    cached=False,
    trace_id="b2c81e…",
)
```

The runtime aggregates these into:

* **A per-run budget cap.** When the cumulative `cost_usd` of a workflow
  exceeds `budget_usd_per_run`, the run is aborted with a clear error
  *before* the next call goes out. No surprise invoices.
* **A JSONL audit log** (`./logs/audit-<run_id>.jsonl`) that records
  every Discover → Inspect → Call cycle, including parameters, costs,
  and provider attribution. Suitable for SOC 2 / regulator review.
* **A DuckDB cache** keyed on `(provider, capability_id, params)`.
  Identical calls within the configured TTL are served from local
  storage at zero cost — critical when an agent re-asks the same
  question in different reasoning steps.

---

## Configuration recipes

### Free-only (zero-cost research)

```yaml
providers:
  - name: fred
    type: builtin.fred
    priority: 1
    api_key: ${FRED_API_KEY}
  - name: yfinance
    type: builtin.yfinance
    priority: 1

routing:
  policy: prefer_free
```

### QVeris-default (one-key onboarding)

```yaml
providers:
  - name: qveris
    type: builtin.qveris
    priority: 1
    api_key: ${QVERIS_API_KEY}
    budget_usd_per_run: 5.00

routing:
  policy: prefer_quality
```

### Mixed (the realistic team setup)

```yaml
providers:
  - name: my_bloomberg
    type: custom
    module: ./providers/bloomberg_proxy.py
    priority: 0                   # always first when it can serve
  - name: fred
    type: builtin.fred
    priority: 1
    api_key: ${FRED_API_KEY}
  - name: qveris
    type: builtin.qveris
    priority: 2                   # fallback for everything else
    api_key: ${QVERIS_API_KEY}
    budget_usd_per_run: 5.00

routing:
  policy: prefer_free
```

Read top-down: paid internal data wins when it can serve the call, then
free public data, and QVeris catches whatever the first two cannot.

---

## Writing your own

The contract is small enough to fit in your head. Minimum viable
provider:

```python
from finagent.providers import (
    Capability, CapabilityMeta, CallResult, DataProvider,
)

class MyInternalProvider(DataProvider):
    name = "my_internal"
    namespace = frozenset({"internal.*"})
    is_free = True

    async def discover(self, query):
        return [Capability(id="internal.research.note", title="Research notes")]

    async def inspect(self, capability_id):
        return CapabilityMeta(
            capability=Capability(id=capability_id, title="Research notes"),
            input_schema={"type": "object", "properties": {"ticker": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"text": {"type": "string"}}},
        )

    async def call(self, capability_id, /, **params):
        # ... talk to your internal database ...
        return CallResult(
            capability_id=capability_id,
            provider=self.name,
            data={"text": "Latest note on " + params["ticker"]},
            cost_usd=0.0,
        )
```

Save the file as `providers/my_internal.py`, register it in
`config.yaml` with `type: custom`, and the runtime will pick it up on
the next start. Reference implementations:

* [`providers/builtin/fred.py`](../../providers/builtin/fred.py) — a
  real free-tier provider in 200 lines.
* [`providers/builtin/qveris.py`](../../providers/builtin/qveris.py) —
  the recommended production provider; useful as a template if you are
  wrapping another commercial vendor.

A more complete walkthrough (auth flows, rate limiting, streaming,
testing with the golden-dataset harness) lives in
[`writing-a-provider.md`](./writing-a-provider.md) *(coming soon)*.

---

## FAQ

**Why not just standardise on the QVeris MCP and skip the protocol?**
Because not every user wants — or is allowed — to send data through a
managed network. The protocol is the *generalisation* of the MCP
contract; QVeris is one (excellent) implementation of it.

**Does using free providers degrade the agents' answers?**
Sometimes. Free coverage is patchy, especially outside US macro and
filings. The runtime surfaces this honestly: when the router cannot
find a provider for a capability, the agent sees an explicit
"capability unavailable" rather than a silent fallback. Upgrading one
slot in the config is the canonical fix.

**Can I run providers on different machines?**
Yes. Custom providers can be thin RPC clients over your own services —
the protocol is transport-agnostic. A common institutional pattern is
to run a BYO provider as a sidecar inside the VPC and let the agent
runtime live anywhere.

**How do I migrate from QVeris-only to a mixed setup later?**
Edit `config.yaml`, add the new provider, restart. Workflows do not
need to change because they reference *capability ids*, not providers.
This is the whole point of the abstraction.

---

*Last updated: project bootstrap. Contributions welcome — this document
is the canonical source of truth for the data layer's design.*
