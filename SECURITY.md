# Security Policy

We take security seriously. OpenFinAgent is a research tool that may be
configured with credentials for paid data vendors and cloud LLM providers, so
responsible disclosure matters.

## Supported versions

While the project is in `v0.x` we only patch the latest released minor version.
Once we hit `v1.0`, we will ship security fixes for the latest two minor lines.

| Version | Supported          |
|---------|--------------------|
| `0.1.x` | yes (current line) |
| older   | no                 |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive reports.

Email the maintainers privately at `security@<your-domain>` (replace with the
real address before publishing). If you prefer GitHub's private channel, use
the **"Report a vulnerability"** button under the repository's *Security* tab.

When reporting, include as much of the following as you can:

- A clear description of the issue and the impact you observed.
- A minimal reproduction (a workflow YAML, provider config, or input that
  triggers the problem) — please redact any real credentials.
- The version (`finagent --version`) and Python version you are running.
- Any logs, stack traces, or audit entries that help us understand the issue.

We will acknowledge your report within **3 business days** and aim to ship a
fix or mitigation within **14 days** for high-severity issues. We will credit
reporters in the release notes unless you ask us not to.

## Scope

In scope:

- The `finagent` Python package and CLI.
- The bundled built-in providers under `finagent/providers/builtin/`.
- The MCP server (`finagent mcp serve`).
- The example workflows shipped in this repository.

Out of scope:

- Vulnerabilities in third-party data vendors, LLM APIs, or the QVeris service
  itself — please report those directly to the upstream vendor.
- Issues that require a malicious local user with write access to your config
  files, environment variables, or `audit.jsonl`.
- Findings that depend on a fork or a custom provider you wrote yourself.

## Operational hardening

A few defaults you should know about:

- The runtime never proxies your credentials. API keys for QVeris, paid data
  vendors, and LLM providers are read from your environment and used only by
  the provider that needs them.
- Every provider call and LLM call is logged to `audit.jsonl` (input args,
  output size, latency, cost). Treat that file like a log file: do not commit
  it to a public repo without reviewing it.
- `v0.1` ships read-only providers only. No bundled capability touches order
  entry, fund movement, or account mutation.

If you operate OpenFinAgent inside an organization, we recommend running
the runtime with the minimum credentials each provider needs, and capping
spend with `budget_usd_per_run` per provider plus a global daily budget.
