"""
finagent.runtime.audit
======================

JSONL audit log: one line per Discover / Inspect / Call / LLM event.

The audit log is the single source of truth for:

* Cost attribution per run, per provider, per capability.
* Reproducibility — given the same inputs and provider responses, you
  can replay a workflow deterministically.
* Compliance — institutional users need to prove what data was used
  to produce a given report.

Format
------

Each line is a self-contained JSON object with at least:

    { "ts": ..., "run_id": ..., "kind": "...", ... }

The ``kind`` field is one of: ``run_start``, ``run_end``, ``call``,
``llm``, ``error``.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class AuditLog:
    """Append-only JSONL writer with ``run_id`` tagging."""

    def __init__(self, path: str | os.PathLike[str], run_id: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._run_id = run_id
        self._handle = self._path.open("a", encoding="utf-8")

    def write(self, kind: str, **fields: Any) -> None:
        record = {
            "ts": time.time(),
            "run_id": self._run_id,
            "kind": kind,
            **fields,
        }
        self._handle.write(json.dumps(record, default=str) + "\n")
        self._handle.flush()

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.close()

    def __enter__(self) -> AuditLog:
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()
