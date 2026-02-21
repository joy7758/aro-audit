from datetime import datetime
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
        aar_statement = {
            "type": "AAR",
            "tool": tool_name,
            "args": tool_args,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        try:
            journal = JSONLJournal(JournalConfig(path="demo/out/journal.jsonl"))
            journal.append_statement(aar_statement)
            journal.close()
        except Exception as e:
            raise RuntimeError(f"AAR 写入失败，拒绝执行: {e}")

    # 执行真实工具
    return tool_callable(**tool_args)
