from sdk.mcp_enforcer.enforcer import enforce_and_execute
from demo_tool import write_file

result = enforce_and_execute(
    tool_name="write_file",
    tool_args={"path": "test_output.txt", "content": "hello AAR"},
    tool_callable=write_file
)

print("执行结果:", result)
