"""Allow ``python -m finagent ...`` to invoke the CLI."""

from finagent.cli import app

if __name__ == "__main__":
    app()
