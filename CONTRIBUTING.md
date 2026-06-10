# Contributing

Thanks for considering a contribution. This project is in active early
development; the fastest way to help is to land one of the issues
labelled `good first issue` or to ship a new built-in provider or
workflow.

## Development setup

```bash
git clone https://github.com/Leon-Drq/openfinagent
cd openfinagent

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"

cp .env.example .env  # add OPENAI_API_KEY for end-to-end runs
pytest -q             # offline smoke tests
```

The default tests do not hit the network. To run a real workflow:

```bash
finagent run earnings-deep-dive --input ticker=NVDA
```

## What we welcome (in priority order)

1. **New built-in providers.** Anything keyless and well-documented:
   ECB SDW, BoE Statistics, Stooq, CoinGecko, Binance public, EDGAR
   facts, Bank of Japan, etc. Use
   [`finagent/providers/builtin/yfinance_provider.py`](./finagent/providers/builtin/yfinance_provider.py)
   as a template.
2. **New workflows under `workflows/`.** Each YAML should run end-to-end
   on the bundled providers and produce a useful Markdown artifact.
3. **Tests.** Especially golden-file tests for workflows that don't need
   the network.
4. **Documentation under `docs/`.** Provider-specific guides, design
   notes, advanced examples.
5. **Bug fixes and small cleanups.**

## Coding conventions

- Python 3.10+, `from __future__ import annotations` at the top of every
  module.
- All I/O is `async`. Never call `requests` or block in a provider.
- Format with `ruff format`, lint with `ruff check`. CI enforces both.
- New public symbols ship with a docstring.
- Providers must implement `discover`, `inspect`, `call` and set the
  four class attributes (`name`, `namespace`, `is_free`,
  `requires_credentials`) — see
  [`finagent/providers/base.py`](./finagent/providers/base.py).

## Pull requests

- Branch from `main`. Keep PRs under ~400 lines of diff when possible.
- Reference the issue you're closing in the PR description.
- Add a one-line entry to the **Unreleased** section of `CHANGELOG.md`.
- The CI must be green before review.

## Reporting bugs

Open an issue with:

- the exact command or Python snippet you ran,
- the full traceback,
- your Python version and OS,
- whether you were using `yfinance`, `sec_edgar`, `fred`, `qveris`, or
  a custom provider.

## Security

Please do **not** open public issues for security problems. Email the
maintainers (see `SECURITY.md` once it lands) or open a private GitHub
security advisory.

## Licensing

By contributing you agree that your contribution is licensed under the
project's [Apache 2.0](./LICENSE) license. We do not require a CLA.
