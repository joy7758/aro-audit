# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

from pathlib import Path

from sdk.journal.jsonl_journal import JournalConfig, JSONLJournal


def test_jsonl_journal_supports_context_manager(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.jsonl"
    with JSONLJournal(JournalConfig(path=str(journal_path))) as journal:
        journal.append_statement({"type": "AAR", "seq": 0, "version": "AAR-MCP-2.0"})

    lines = journal_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert '"seq":0' in lines[0]


def test_jsonl_journal_append_statement_with_lineno(tmp_path: Path) -> None:
    journal_path = tmp_path / "journal.jsonl"
    with JSONLJournal(JournalConfig(path=str(journal_path))) as journal:
        line_no_1, line_1 = journal.append_statement_with_lineno(
            {"type": "AAR", "seq": 0, "version": "AAR-MCP-2.0"}
        )
        line_no_2, _ = journal.append_statement_with_lineno(
            {"type": "AAR", "seq": 1, "version": "AAR-MCP-2.0"}
        )

    assert line_no_1 == 1
    assert line_no_2 == 2
    assert '"seq":0' in line_1
