# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

from pathlib import Path

from sdk.journal.jsonl_journal import JSONLJournal, JournalConfig


def test_jsonl_journal_supports_context_manager(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.jsonl"
    with JSONLJournal(JournalConfig(path=str(journal_path))) as journal:
        journal.append_statement({"type": "AAR", "seq": 0, "version": "AAR-MCP-2.0"})

    lines = journal_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert '"seq":0' in lines[0]
