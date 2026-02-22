# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

import json
from pathlib import Path

from sdk.mcp_enforcer.enforcer import enforce_and_execute


def test_enforce_and_execute_uses_env_journal_path(monkeypatch, tmp_path: Path) -> None:
    journal_path = tmp_path / "custom_journal.jsonl"
    monkeypatch.setenv("ARO_JOURNAL_PATH", str(journal_path))

    called = {"ok": False}

    def tool_callable(**kwargs):
        called["ok"] = True
        return kwargs["value"] + 1

    result = enforce_and_execute("write_file", {"value": 1}, tool_callable)

    assert result == 2
    assert called["ok"] is True

    lines = journal_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["type"] == "AAR"
    assert entry["tool"] == "write_file"
