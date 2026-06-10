"""
finagent.cli
============

Typer-based CLI.  Three commands are wired up for v0.x:

    finagent run <workflow> [--input k=v ...]
    finagent providers list
    finagent version

Install ``openfinagent`` and the entry point ``finagent`` is on
``$PATH`` automatically.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from finagent import __version__
from finagent.config import (
    load_config,
    parse_global_budget,
    parse_policy,
    parse_providers,
)
from finagent.runtime.llm import LLMClient
from finagent.runtime.registry import ProviderRegistry
from finagent.runtime.runner import Runner

app = typer.Typer(
    name="finagent",
    help="Open-source workspace for financial agents.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()

_INIT_CONFIG = """# OpenFinAgent project config.
# The default live setup uses keyless public providers first.

routing:
  policy: prefer_free

budget:
  usd_per_run: 2.00

providers:
  - name: yfinance
    type: builtin.yfinance
    priority: 1

  - name: sec_edgar
    type: builtin.sec_edgar
    priority: 1

  # Optional: uncomment after setting QVERIS_API_KEY.
  # - name: qveris
  #   type: builtin.qveris
  #   priority: 2
  #   api_key: ${QVERIS_API_KEY}
  #   budget_usd_per_run: 5.00
"""

_INIT_ENV = """# Required for live agent steps.
OPENAI_API_KEY=

# Optional: OpenAI-compatible gateway endpoint.
# OPENAI_BASE_URL=https://gateway.ai.vercel.com/v1/openai

# Optional: SEC asks automated clients to identify themselves.
# SEC_USER_AGENT=openfinagent/0.1 your-email@example.com

# Optional: managed financial capability layer.
# QVERIS_API_KEY=
"""

_INIT_README = """# OpenFinAgent Starter

Run the offline demo first:

```bash
finagent demo NVDA
```

Then add `OPENAI_API_KEY` to `.env` and run the live workflow:

```bash
finagent run earnings-deep-dive --input ticker=NVDA
```

The live workflow uses `yfinance` and SEC EDGAR by default. Add QVeris or
private providers in `finagent.yaml` when you need broader coverage.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_dotenv() -> None:
    """Load a local ``.env`` file if present, without overriding real env."""

    try:
        from dotenv import load_dotenv  # type: ignore[import-untyped]
    except ImportError:
        return
    for candidate in (Path.cwd() / ".env", Path.cwd() / ".env.local"):
        if candidate.exists():
            load_dotenv(candidate, override=False)


def _build_registry(config_path: str | None) -> tuple[ProviderRegistry, dict]:
    config = load_config(config_path)
    provider_configs = parse_providers(config)
    policy = parse_policy(config)
    global_budget = parse_global_budget(config)
    registry = ProviderRegistry.from_configs(
        provider_configs,
        policy=policy,
        global_budget_usd=global_budget,
    )
    return registry, config


def _parse_kv_list(raw: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise typer.BadParameter(
                f"--input expects key=value, got {item!r}"
            )
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _bundled_workflows_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "workflows"


def _write_text_file(path: Path, body: str, *, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return True


def _copy_file(source: Path, dest: Path, *, force: bool) -> bool:
    if dest.exists() and not force:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    return True


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def version() -> None:
    """Print the openfinagent version."""

    console.print(f"openfinagent [bold]{__version__}[/bold]")


@app.command(name="init")
def init_cmd(
    path: str = typer.Argument(".", help="Directory to create or update."),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing starter files.",
    ),
) -> None:
    """Create a starter OpenFinAgent project."""

    target = Path(path).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []

    files = [
        (target / "finagent.yaml", _INIT_CONFIG),
        (target / ".env.example", _INIT_ENV),
        (target / "README.md", _INIT_README),
    ]
    for file_path, body in files:
        if _write_text_file(file_path, body, force=force):
            created.append(str(file_path.relative_to(target)))
        else:
            skipped.append(str(file_path.relative_to(target)))

    workflow_source = _resolve_workflow_path("earnings-deep-dive")
    workflow_dest = target / "workflows" / "earnings-deep-dive.yaml"
    if _copy_file(workflow_source, workflow_dest, force=force):
        created.append(str(workflow_dest.relative_to(target)))
    else:
        skipped.append(str(workflow_dest.relative_to(target)))

    demo_source = _resolve_workflow_path("demo-earnings-deep-dive")
    demo_dest = target / "workflows" / "demo-earnings-deep-dive.yaml"
    if _copy_file(demo_source, demo_dest, force=force):
        created.append(str(demo_dest.relative_to(target)))
    else:
        skipped.append(str(demo_dest.relative_to(target)))

    console.print(
        Panel.fit(
            Text.from_markup(
                f"[bold]Initialized[/bold] {target}\n"
                f"created = {created or []}\n"
                f"skipped = {skipped or []}\n\n"
                "Next:\n"
                f"  cd {target}\n"
                "  finagent demo NVDA\n"
                "  cp .env.example .env"
            ),
            border_style="cyan",
        )
    )


@app.command(name="demo")
def demo_cmd(
    ticker: str = typer.Argument("NVDA", help="Sample ticker: NVDA, AAPL, or MSFT."),
    output_dir: str = typer.Option(
        "reports",
        "--output-dir",
        "-o",
        help="Directory where the demo report will be written.",
    ),
    audit: str = typer.Option(
        "audit.jsonl",
        "--audit",
        help="Audit log destination.",
    ),
) -> None:
    """Run the offline demo workflow with deterministic sample data."""

    from finagent.providers.builtin import SampleProvider

    workflow_path = _resolve_workflow_path("demo-earnings-deep-dive")
    registry = ProviderRegistry()
    registry.add(SampleProvider(), priority=0)

    normalized_ticker = ticker.upper().strip()

    def on_event(kind: str, payload: dict) -> None:
        if kind == "step_start":
            console.print(
                f"[dim]→[/dim] [bold]{payload['type']:<6}[/bold] {payload['id']}…"
            )
        elif kind == "step_end":
            latency = payload.get("latency_ms") or 0.0
            console.print(
                f"[green]✓[/green] {payload['id']:<24} "
                f"[dim]{latency / 1000:.2f}s · $0.0000[/dim]"
            )

    runner = Runner(registry, audit_path=audit, on_event=on_event)

    console.print(
        Panel.fit(
            Text.from_markup(
                f"[bold]Running offline demo[/bold] {workflow_path.name}\n"
                f"ticker = {normalized_ticker}\n"
                "provider = sample\n"
                "network = off"
            ),
            border_style="cyan",
        )
    )

    try:
        result = asyncio.run(
            runner.run(
                workflow_path,
                inputs={"ticker": normalized_ticker, "output_dir": output_dir},
            )
        )
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]✗ demo failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    finally:
        asyncio.run(registry.teardown())

    console.print(
        Panel.fit(
            Text.from_markup(
                f"[bold green]done[/bold green] · "
                f"{result.elapsed_seconds:.1f}s · $0.0000\n"
                f"[bold]report:[/bold] {result.report_path}\n"
                f"[bold]audit:[/bold] {audit}"
            ),
            border_style="green",
        )
    )


@app.command(name="run")
def run_cmd(
    workflow: str = typer.Argument(
        ..., help="Workflow YAML path or short name from ./workflows/."
    ),
    input_pairs: list[str] = typer.Option(
        [],
        "--input",
        "-i",
        help="Workflow input as key=value (repeat for multiple).",
    ),
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to config.yaml. Default: auto-detect."
    ),
    audit: str = typer.Option(
        "audit.jsonl", "--audit", help="Audit log destination."
    ),
    no_llm: bool = typer.Option(
        False, "--no-llm", help="Skip agent steps (useful for fetch-only smoke tests)."
    ),
) -> None:
    """Run a workflow end-to-end."""

    _load_dotenv()

    workflow_path = _resolve_workflow_path(workflow)
    inputs = _parse_kv_list(input_pairs)

    registry, _config = _build_registry(config)
    llm: LLMClient | None = None
    if not no_llm:
        try:
            llm = LLMClient()
        except RuntimeError as exc:
            console.print(
                f"[yellow]warning:[/yellow] {exc}\n"
                "[dim]Continuing with --no-llm semantics. "
                "Agent steps will fail.[/dim]"
            )

    def on_event(kind: str, payload: dict) -> None:
        if kind == "step_start":
            console.print(
                f"[dim]→[/dim] [bold]{payload['type']:<6}[/bold] {payload['id']}…"
            )
        elif kind == "step_end":
            cost = payload.get("cost_usd") or 0.0
            latency = payload.get("latency_ms") or 0.0
            console.print(
                f"[green]✓[/green] {payload['id']:<24} "
                f"[dim]{latency / 1000:.2f}s · ${cost:.4f}[/dim]"
            )

    runner = Runner(registry, llm=llm, audit_path=audit, on_event=on_event)

    console.print(
        Panel.fit(
            Text.from_markup(
                f"[bold]Running[/bold] {workflow_path.name}\n"
                f"inputs = {inputs or '{}'}\n"
                f"providers = {[p.name for p in registry.providers]}"
            ),
            border_style="cyan",
        )
    )

    try:
        result = asyncio.run(runner.run(workflow_path, inputs))
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]✗ run failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    finally:
        asyncio.run(registry.teardown())

    console.print(
        Panel.fit(
            Text.from_markup(
                f"[bold green]done[/bold green] · "
                f"{result.elapsed_seconds:.1f}s · "
                f"${result.total_cost_usd:.4f}\n"
                + (
                    f"[bold]report:[/bold] {result.report_path}"
                    if result.report_path
                    else ""
                )
            ),
            border_style="green",
        )
    )


mcp_app = typer.Typer(
    name="mcp", help="Run finagent as an MCP server.", no_args_is_help=True
)
app.add_typer(mcp_app)


@mcp_app.command("serve")
def mcp_serve(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to config.yaml."
    ),
) -> None:
    """Speak the Model Context Protocol over stdio.

    Add to a Claude Code, Cursor, or Codex config:

        {"mcpServers": {"finagent": {"command": "finagent", "args": ["mcp", "serve"]}}}
    """

    _load_dotenv()
    try:
        from finagent.mcp_server import serve
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]✗ MCP server unavailable:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    registry, _ = _build_registry(config)
    try:
        asyncio.run(serve(registry))
    except KeyboardInterrupt:
        pass


@app.command(name="providers")
def providers_cmd(
    config: str | None = typer.Option(
        None, "--config", "-c", help="Path to config.yaml."
    ),
) -> None:
    """List configured providers."""

    _load_dotenv()
    try:
        registry, _ = _build_registry(config)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]✗ failed to load providers:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Configured providers", title_style="bold")
    table.add_column("name", style="cyan")
    table.add_column("namespace")
    table.add_column("free?")
    table.add_column("auth?")

    for provider in registry.providers:
        table.add_row(
            provider.name,
            ", ".join(sorted(provider.namespace)),
            "yes" if provider.is_free else "no",
            "required" if provider.requires_credentials else "no",
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Workflow path resolution
# ---------------------------------------------------------------------------


def _resolve_workflow_path(name: str) -> Path:
    """Accept a path, a bare name (looked up under ./workflows), or a builtin."""

    explicit = Path(name)
    if explicit.suffix in {".yaml", ".yml"} and explicit.exists():
        return explicit

    cwd_workflow_dir = Path.cwd() / "workflows"
    for stem in (name, name.replace(":", "/"), name.replace(".", "/")):
        for suffix in (".yaml", ".yml"):
            candidate = cwd_workflow_dir / f"{stem}{suffix}"
            if candidate.exists():
                return candidate

    # Fall back to the workflows shipped with the package (for `finagent run earnings-deep-dive`).
    bundled = _bundled_workflows_dir() / f"{name}.yaml"
    if bundled.exists():
        return bundled

    raise typer.BadParameter(
        f"Workflow {name!r} not found. Looked in {cwd_workflow_dir} and "
        f"the bundled workflows. Pass a full path or create "
        f"workflows/{name}.yaml."
    )


if __name__ == "__main__":  # pragma: no cover
    app()
