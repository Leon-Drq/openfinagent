# Release Guide

This project publishes the Python package from GitHub Actions using PyPI
Trusted Publishing. Do not store PyPI API tokens in the repository.

## One-Time PyPI Setup

Create projects named `openfinagent` on PyPI and TestPyPI, then configure
Trusted Publishing for this repository:

- Owner / repository: `Leon-Drq/openfinagent`
- Workflow file: `.github/workflows/publish.yml`
- PyPI environment: `pypi`
- TestPyPI environment: `testpypi`

The GitHub workflow uses OIDC (`id-token: write`) and publishes only from the
named environments.

Use these exact claims when configuring the TestPyPI publisher:

```text
Repository owner: Leon-Drq
Repository name: openfinagent
Workflow filename: publish.yml
Environment name: testpypi
```

Use these exact claims when configuring the PyPI publisher:

```text
Repository owner: Leon-Drq
Repository name: openfinagent
Workflow filename: publish.yml
Environment name: pypi
```

If the workflow fails with `invalid-publisher`, the matching Trusted Publisher
or Pending Publisher has not been configured on PyPI/TestPyPI yet.

## Local Preflight

Use Python 3.12 for release checks:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,release]"

ruff check .
pytest
npx tsc --noEmit
npm run build
```

Build and inspect the package:

```bash
rm -rf dist build *.egg-info
python -m build
twine check dist/*
```

Verify the wheel in a clean environment:

```bash
python -m venv /tmp/openfinagent-release-check
/tmp/openfinagent-release-check/bin/python -m pip install --upgrade pip
/tmp/openfinagent-release-check/bin/python -m pip install dist/openfinagent-*.whl

/tmp/openfinagent-release-check/bin/finagent version
/tmp/openfinagent-release-check/bin/finagent doctor --no-network
/tmp/openfinagent-release-check/bin/finagent demo NVDA --output-dir /tmp/openfinagent-demo
```

## Version Bump

Before a release, update the version in both files:

- `pyproject.toml`
- `finagent/__init__.py`

Then move the relevant `CHANGELOG.md` entries from `Unreleased` into a dated
release section.

## TestPyPI

Run the `Publish Python package` GitHub workflow manually and select
`testpypi`.

Then verify install:

```bash
python -m venv /tmp/openfinagent-testpypi
/tmp/openfinagent-testpypi/bin/python -m pip install --upgrade pip
/tmp/openfinagent-testpypi/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  openfinagent
/tmp/openfinagent-testpypi/bin/finagent demo NVDA
```

## PyPI

Create and publish a GitHub Release, for example `v0.2.0`. The release event
triggers `.github/workflows/publish.yml` and publishes to PyPI.

After the workflow completes:

```bash
python -m venv /tmp/openfinagent-pypi
/tmp/openfinagent-pypi/bin/python -m pip install --upgrade pip
/tmp/openfinagent-pypi/bin/python -m pip install openfinagent
/tmp/openfinagent-pypi/bin/finagent doctor --no-network
/tmp/openfinagent-pypi/bin/finagent demo NVDA
```

## Post-Release

Update README quickstarts from editable install to:

```bash
pip install openfinagent
finagent demo NVDA
```

Confirm the homepage and GitHub README both point at the published path.
