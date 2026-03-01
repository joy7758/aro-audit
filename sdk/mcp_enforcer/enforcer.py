import os
from datetime import UTC, datetime
from typing import Any, Callable

from sdk.journal.jsonl_journal import JournalConfig, JSONLJournal

HIGH_RISK_TOOLS = {
    "write_file",
    "delete_resource",
    "transfer_funds",
}
DEFAULT_JOURNAL_PATH = "demo/out/journal.jsonl"


def enforce_and_execute(tool_name: str, tool_args: dict[str, Any], tool_callable: Callable[..., Any]) -> Any:
    """Write AAR evidence before executing high-risk tools."""

    if tool_name in HIGH_RISK_TOOLS:
        journal_path = os.getenv("ARO_JOURNAL_PATH", DEFAULT_JOURNAL_PATH)
        aar_statement = {
            "type": "AAR",
            "tool": tool_name,
            "args": tool_args,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

        try:
            with JSONLJournal(JournalConfig(path=journal_path)) as journal:
                journal.append_statement(aar_statement)
        except (OSError, TypeError, ValueError) as exc:
            raise RuntimeError(f"Failed to write AAR evidence, refusing execution: {exc}") from exc

    return tool_callable(**tool_args)
