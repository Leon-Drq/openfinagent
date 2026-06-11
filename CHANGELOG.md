# Changelog

All notable changes to OpenFinAgent are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/) and the
project adheres to [Semantic Versioning](https://semver.org/) once it
reaches v1.0.

## [Unreleased]

### Added

- `finagent demo` runs a no-network, no-LLM first-run workflow using the
  built-in deterministic `sample` provider.
- `finagent init` scaffolds a starter workspace with config, env template,
  and live/offline workflows.
- `finagent doctor` diagnoses Python version, package import, bundled
  workflows, dependencies, provider config, optional credentials, offline demo
  viability, and optional live endpoint reachability.
- `workflows/demo-earnings-deep-dive.yaml` for offline onboarding.
- GitHub Actions publishing workflow for TestPyPI / PyPI Trusted Publishing.
- Release guide at `docs/release.md`.

### Changed

- Wheel build configuration now includes bundled workflows and starter
  config templates so packaged installs can resolve built-in workflows.
- README quickstarts now lead with the offline demo before live LLM setup.
- CI now runs `finagent doctor --no-network` and the offline demo as CLI smoke
  checks.

## [0.1.0] — 2026-04-29

Initial public preview. The minimum viable end-to-end path is shipped:
clone the repo, set `OPENAI_API_KEY`, run `finagent run earnings-deep-dive
--input ticker=NVDA`, and a Markdown memo lands in `reports/`.

### Added

- `DataProvider` async protocol — `discover` / `inspect` / `call` plus
  optional `stream`, with first-class `CallResult` for cost and latency.
- Built-in providers:
  - `yfinance` (keyless) — quote, profile, history, dividends, earnings,
    holders, recommendations.
  - `sec_edgar` (keyless, custom User-Agent) — recent filings index by
    ticker.
  - `fred` (free key) — three macro series as a reference template.
  - `qveris` — REST adapter scaffold.
- `ProviderRegistry` with `PREFER_FREE` / `PREFER_QUALITY` / `EXPLICIT`
  routing policies, per-provider and global per-run budget caps, and an
  audit-friendly `_charge` accounting loop.
- YAML workflow DSL with three step kinds: `fetch`, `agent`, `report`.
  `${name}` / `${name.path}` templating.
- `Runner` — orchestrates a workflow end to end, emits per-step events,
  writes a JSONL `audit.jsonl`, and returns a `RunResult` with elapsed
  time, total spend, and the report path.
- `LLMClient` — thin OpenAI-compatible wrapper, works with real OpenAI,
  Vercel AI Gateway, Azure OpenAI, and local llama.cpp.
- `finagent` CLI (`run`, `providers`, `version`, `mcp serve`) backed by
  Typer + Rich.
- MCP server over stdio exposing three meta-tools (`discover`,
  `inspect`, `call`) for Claude Code / Cursor / Codex.
- Bundled workflow `workflows/earnings-deep-dive.yaml` and
  `examples/quickstart.py`.
- Apache 2.0 license, GitHub Actions CI matrix on Python 3.10–3.12,
  ruff lint, four offline smoke tests.

[Unreleased]: https://github.com/Leon-Drq/openfinagent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Leon-Drq/openfinagent/releases/tag/v0.1.0
