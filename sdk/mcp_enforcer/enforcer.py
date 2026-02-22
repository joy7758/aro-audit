import os

from datetime import UTC, datetime
from sdk.journal.jsonl_journal import JSONLJournal, JournalConfig

HIGH_RISK_TOOLS = {
    "write_file",
    "delete_resource",
    "transfer_funds",
}


def enforce_and_execute(tool_name: str, tool_args: dict, tool_callable):
    """
    强制写 AAR 证据：
    1. 高风险工具必须先写入 AAR
    2. 写入失败则拒绝执行
    """

    if tool_name in HIGH_RISK_TOOLS:
        journal_path = os.getenv("ARO_JOURNAL_PATH", "demo/out/journal.jsonl")
        aar_statement = {
            "type": "AAR",
            "tool": tool_name,
            "args": tool_args,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

        try:
            with JSONLJournal(JournalConfig(path=journal_path)) as journal:
                journal.append_statement(aar_statement)
        except Exception as e:
            raise RuntimeError(f"AAR 写入失败，拒绝执行: {e}")

    # 执行真实工具
    return tool_callable(**tool_args)
