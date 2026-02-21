#!/usr/bin/env bash
set -euo pipefail

echo "【进度】A-1/3 生成扩散目标清单 + 外联文案（RC1 Review 入口）"

mkdir -p tools

# 1) 目标仓库清单（你随时可编辑增删）
cat > tools/rc1_outreach_targets.txt <<'TARGETS'
modelcontextprotocol/servers
modelcontextprotocol/python-sdk
modelcontextprotocol/typescript-sdk
langchain-ai/langchain
langchain-ai/langgraph
microsoft/autogen
openai/openai-agents-python
anthropics/claude-code
crewAIInc/crewAI
pydantic/pydantic-ai
TARGETS

# 2) 外联文案模板（统一口径：可验证交互层 + conformance gate + review入口）
cat > tools/rc1_outreach_post.md <<'POST'
### Proposal: Integrate AAR-MCP-2.0 RC1 (Verifiable Agent Interaction Layer)

I’m publishing **AAR-MCP-2.0 Core Spec (RC1)**: a verifiable interaction layer for MCP/agent tool calls.
It provides **tamper-evident journals + checkpoint signatures + conformance vectors**, and exports an **audit bundle** reviewers can independently verify.

**Why this matters**
- Observability logs are not evidence. We need **non-repudiable action receipts** for high-risk tools (write config, transfer funds, etc.).
- This RC1 focuses on **fail-closed enforcement** and **format-stable verification**, not vendor lock-in.

**RC1 entry (spec bundle + sha256 + conformance gate)**
- Repo: joy7758/aro-audit
- RC1 Review入口已在 README 顶部（含 spec bundle + sha256）
- Conformance Gate: boundary vectors (base OK / attestations-only OK / predicate-tamper FAIL)

**Review workflow**
- Please review via GitHub Discussions:
  - Review Thread #3: https://github.com/joy7758/aro-audit/discussions/3
  - Review Thread #4: https://github.com/joy7758/aro-audit/discussions/4
- Or open an issue using our RC1 review template.

**Ask**
- I’d like feedback on:
  1) Record types + digest boundary definition
  2) Checkpoint semantics (range, merkle root, signature)
  3) Tool-level dependency policy (soft/strict/hard-gate)
  4) Conformance vectors coverage (what’s missing)

If your project exposes MCP tools, I can provide a minimal wrapper and a 30s demo bundle to validate integration.
POST

echo "【进度】A-2/3 预检查 gh 登录状态"
if ! command -v gh >/dev/null 2>&1; then
  echo "❌ 未找到 gh。请先安装：brew install gh"
  exit 2
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "❌ gh 未登录。请先执行：gh auth login"
  exit 2
fi

echo "【进度】A-3/3 批量创建 Issue（无权限则降级为打印可复制内容）"
TITLE="RC1 Review Request: AAR-MCP-2.0 Verifiable Interaction Layer (Conformance Gate included)"
BODY_FILE="tools/rc1_outreach_post.md"

OK=0
FAIL=0

while IFS= read -r REPO; do
  [[ -z "$REPO" ]] && continue
  echo "----"
  echo "目标：$REPO"

  # 先探测是否有创建 issue 权限
  if gh api "repos/$REPO" >/dev/null 2>&1; then
    # 尝试创建 issue（如果没有权限会失败）
    if gh issue create -R "$REPO" -t "$TITLE" -F "$BODY_FILE" >/dev/null 2>&1; then
      echo "✅ 已创建 Issue：$REPO"
      OK=$((OK+1))
    else
      echo "⚠️ 无权限/被限制，已输出可复制内容（你手动贴也行）：$REPO"
      echo "TITLE: $TITLE"
      echo "----- BODY BEGIN -----"
      cat "$BODY_FILE"
      echo "----- BODY END -----"
      FAIL=$((FAIL+1))
    fi
  else
    echo "⚠️ 无法访问仓库信息（可能拼写/网络/权限）。已输出可复制内容：$REPO"
    echo "TITLE: $TITLE"
    echo "----- BODY BEGIN -----"
    cat "$BODY_FILE"
    echo "----- BODY END -----"
    FAIL=$((FAIL+1))
  fi
done < tools/rc1_outreach_targets.txt

echo "==== 汇总 ===="
echo "已自动创建：$OK"
echo "需手动发布：$FAIL"
echo "目标清单：tools/rc1_outreach_targets.txt"
echo "外联文案：tools/rc1_outreach_post.md"
