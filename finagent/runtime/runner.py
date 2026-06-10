"""
finagent.runtime.runner
=======================

Workflow runner — the heart of the v0.x prototype.

A workflow is a YAML file with three sections:

.. code-block:: yaml

    name: earnings-deep-dive
    inputs:
      ticker: { type: string, required: true }
    steps:
      - id: profile
        type: fetch
        capability: equity.profile
        params: { ticker: ${ticker} }

      - id: filings
        type: fetch
        capability: filings.recent
        params: { ticker: ${ticker}, forms: ["10-K", "10-Q"], limit: 4 }

      - id: thesis
        type: agent
        role: analyst
        prompt: |
          You are a sell-side equity analyst...
          Profile: ${profile}
          Filings: ${filings}
        output: thesis_md

      - id: report
        type: report
        path: reports/${ticker}-${run_date}.md
        template: |
          # ${ticker}
          ${thesis_md}

The runner walks ``steps`` sequentially, accumulating results into a
context dict that can be referenced via ``${name}`` in later steps.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from finagent.runtime.audit import AuditLog
from finagent.runtime.llm import LLMClient
from finagent.runtime.registry import ProviderRegistry


# ---------------------------------------------------------------------------
# Result objects
# ---------------------------------------------------------------------------


@dataclass
class StepResult:
    step_id: str
    kind: str
    output: Any
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    notes: str = ""


@dataclass
class RunResult:
    workflow: str
    run_id: str
    started_at: float
    finished_at: float
    inputs: dict[str, Any]
    steps: list[StepResult] = field(default_factory=list)
    report_path: Path | None = None
    total_cost_usd: float = 0.0

    @property
    def elapsed_seconds(self) -> float:
        return self.finished_at - self.started_at


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


# Matches ${name} or ${name.path.like.this}; we resolve dotted lookups
# against the running context so prompts can pull nested fields.
_TEMPLATE_RE = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_.\-]*)\}")


class Runner:
    """Execute a single workflow against a configured provider registry."""

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        llm: LLMClient | None = None,
        audit_path: str | Path = "audit.jsonl",
        on_event: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._registry = registry
        self._llm = llm
        self._audit_path = Path(audit_path)
        self._on_event = on_event or (lambda _kind, _payload: None)

    # ------------------------------------------------------------------ #
    # Public entry points
    # ------------------------------------------------------------------ #

    async def run(
        self,
        workflow_path: str | Path,
        inputs: dict[str, Any] | None = None,
    ) -> RunResult:
        workflow = _load_workflow(Path(workflow_path))
        return await self.run_workflow(workflow, inputs or {})

    async def run_workflow(
        self,
        workflow: dict[str, Any],
        inputs: dict[str, Any],
    ) -> RunResult:
        run_id = uuid.uuid4().hex[:12]
        started = time.time()
        run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        context: dict[str, Any] = {
            **(workflow.get("defaults") or {}),
            **inputs,
            "run_id": run_id,
            "run_date": run_date,
        }

        # Fill in defaults for any inputs the workflow declares but the
        # caller didn't pass.
        for key, spec in (workflow.get("inputs") or {}).items():
            if key not in context and isinstance(spec, dict) and "default" in spec:
                context[key] = spec["default"]
            if isinstance(spec, dict) and spec.get("required") and key not in context:
                raise ValueError(f"Workflow input {key!r} is required.")

        result = RunResult(
            workflow=workflow.get("name", "anonymous"),
            run_id=run_id,
            started_at=started,
            finished_at=started,
            inputs=dict(inputs),
        )

        await self._registry.setup()
        with AuditLog(self._audit_path, run_id) as audit:
            audit.write(
                "run_start",
                workflow=result.workflow,
                inputs=inputs,
            )
            self._on_event("run_start", {"workflow": result.workflow, "run_id": run_id})

            try:
                for step in workflow.get("steps") or []:
                    step_result = await self._execute_step(step, context, audit)
                    result.steps.append(step_result)
                    result.total_cost_usd += step_result.cost_usd
                    if step_result.kind == "report" and isinstance(
                        step_result.output, (str, Path)
                    ):
                        result.report_path = Path(step_result.output)
            except Exception as exc:
                audit.write("error", message=str(exc), type=type(exc).__name__)
                self._on_event("error", {"message": str(exc)})
                raise
            finally:
                result.finished_at = time.time()
                audit.write(
                    "run_end",
                    elapsed_seconds=result.elapsed_seconds,
                    total_cost_usd=result.total_cost_usd,
                )
                self._on_event(
                    "run_end",
                    {
                        "elapsed_seconds": result.elapsed_seconds,
                        "total_cost_usd": result.total_cost_usd,
                    },
                )

        return result

    # ------------------------------------------------------------------ #
    # Step dispatch
    # ------------------------------------------------------------------ #

    async def _execute_step(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
        audit: AuditLog,
    ) -> StepResult:
        step_id = str(step.get("id") or step.get("type") or "step")
        kind = str(step.get("type") or "").lower()

        self._on_event("step_start", {"id": step_id, "type": kind})

        if kind == "fetch":
            result = await self._step_fetch(step, context, audit)
        elif kind == "agent":
            result = await self._step_agent(step, context, audit)
        elif kind == "report":
            result = await self._step_report(step, context, audit)
        else:
            raise ValueError(f"Unknown step type {kind!r} on step {step_id!r}.")

        if "output" in step and isinstance(step["output"], str):
            context[step["output"]] = result.output
        else:
            context[step_id] = result.output

        self._on_event(
            "step_end",
            {
                "id": step_id,
                "type": kind,
                "cost_usd": result.cost_usd,
                "latency_ms": result.latency_ms,
            },
        )
        return result

    # ------------------------------------------------------------------ #
    # Step implementations
    # ------------------------------------------------------------------ #

    async def _step_fetch(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
        audit: AuditLog,
    ) -> StepResult:
        capability_id = str(step["capability"])
        params = _expand(step.get("params") or {}, context)
        provider = step.get("provider")

        call = await self._registry.call(capability_id, provider=provider, **params)

        audit.write(
            "call",
            step=step.get("id"),
            capability=capability_id,
            provider=call.provider,
            params=params,
            cost_usd=call.cost_usd,
            latency_ms=call.latency_ms,
            cached=call.cached,
        )

        return StepResult(
            step_id=str(step.get("id") or capability_id),
            kind="fetch",
            output=call.data,
            cost_usd=call.cost_usd,
            latency_ms=call.latency_ms,
            notes=f"{capability_id} via {call.provider}",
        )

    async def _step_agent(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
        audit: AuditLog,
    ) -> StepResult:
        if self._llm is None:
            raise RuntimeError(
                "Agent step requires an LLM client. Pass llm=LLMClient() to Runner()."
            )

        role = str(step.get("role") or "analyst")
        system = _expand(
            step.get("system")
            or _DEFAULT_AGENT_SYSTEM.get(role, _DEFAULT_AGENT_SYSTEM["analyst"]),
            context,
        )
        user_prompt = _expand(str(step.get("prompt", "")), context)

        started = time.perf_counter()
        response = await self._llm.complete(
            system=system,
            user=user_prompt,
            model=step.get("model"),
            max_tokens=int(step.get("max_tokens") or 1500),
            temperature=float(step.get("temperature") or 0.2),
        )
        latency_ms = (time.perf_counter() - started) * 1000

        audit.write(
            "llm",
            step=step.get("id"),
            role=role,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            cost_usd=response.cost_usd,
        )

        return StepResult(
            step_id=str(step.get("id") or role),
            kind="agent",
            output=response.text,
            cost_usd=response.cost_usd,
            latency_ms=latency_ms,
            notes=f"{role} via {response.model}",
        )

    async def _step_report(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
        audit: AuditLog,
    ) -> StepResult:
        path = Path(_expand(str(step["path"]), context))
        path.parent.mkdir(parents=True, exist_ok=True)
        body = _expand(str(step.get("template", "")), context)
        path.write_text(body, encoding="utf-8")

        audit.write("report", step=step.get("id"), path=str(path), bytes=len(body))

        return StepResult(
            step_id=str(step.get("id") or "report"),
            kind="report",
            output=path,
            notes=f"wrote {len(body)} bytes",
        )


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


_DEFAULT_AGENT_SYSTEM = {
    "analyst": (
        "You are a senior sell-side equity analyst. Be specific, cite numbers, "
        "use bullet points, and flag what is uncertain. Markdown only."
    ),
    "quant": (
        "You are a buy-side quant researcher. Compute concrete deltas, ratios, "
        "and z-scores. State assumptions explicitly. Markdown only."
    ),
    "risk": (
        "You are a risk officer. Identify downside scenarios, regulatory and "
        "litigation exposure. Be terse and concrete. Markdown only."
    ),
    "macro": (
        "You are a macro strategist. Frame company news against rates, FX, "
        "and sector rotation. Markdown only."
    ),
    "writer": (
        "You are a research editor. Compile inputs into a tight, well-organised "
        "investment memo. Preserve numbers verbatim. Markdown only."
    ),
}


# ---------------------------------------------------------------------------
# Templating helpers
# ---------------------------------------------------------------------------


def _expand(value: Any, context: dict[str, Any]) -> Any:
    """Recursively expand ``${var}`` references inside strings.

    Non-string scalars and lists/dicts are walked but otherwise untouched.
    Dotted paths like ``${profile.sector}`` walk into nested dicts.
    """

    if isinstance(value, str):
        return _expand_str(value, context)
    if isinstance(value, list):
        return [_expand(v, context) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v, context) for k, v in value.items()}
    return value


def _expand_str(text: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        path = match.group(1)
        try:
            value = _resolve(path, context)
        except KeyError:
            return match.group(0)  # leave unresolved placeholders intact
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, default=str, indent=2)
        return str(value)

    return _TEMPLATE_RE.sub(replace, text)


def _resolve(path: str, context: dict[str, Any]) -> Any:
    parts = path.split(".")
    cursor: Any = context
    for part in parts:
        if isinstance(cursor, dict) and part in cursor:
            cursor = cursor[part]
        else:
            raise KeyError(path)
    return cursor


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


def _load_workflow(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Workflow not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Workflow {path} must be a mapping at the top level.")
    return data
