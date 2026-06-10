<!--
Thanks for sending a PR! A few notes before you submit:

- Keep PRs focused. One concept per PR is much easier to review than a mega-PR.
- Run the dev loop locally: `pip install -e ".[dev]" && pytest && ruff check .`.
- If you changed user-facing behavior, update README, CHANGELOG, or the relevant
  page in `docs/`.
-->

## What does this PR do?

<!-- One or two sentences. Link the issue it closes if any. -->

Closes #

## How was it tested?

<!--
- New unit tests? List them.
- Manual repro? Paste the command and the relevant output.
- For provider PRs, please include a real (redacted) sample call.
-->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] New data provider
- [ ] New workflow / example
- [ ] Documentation only
- [ ] Refactor (no user-visible change)
- [ ] Breaking change (please describe migration below)

## Checklist

- [ ] I have read [`CONTRIBUTING.md`](../CONTRIBUTING.md).
- [ ] `pytest` passes locally.
- [ ] `ruff check .` is clean (or I explained the noqa).
- [ ] I updated `CHANGELOG.md` under the unreleased section if this is user-visible.
- [ ] I did not commit any real API keys, audit logs, or `reports/` artifacts.
