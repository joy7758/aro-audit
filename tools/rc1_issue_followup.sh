#!/usr/bin/env bash
set -euo pipefail

TITLE="RC1 Review Request: AAR-MCP-2.0 Verifiable Interaction Layer (Conformance Gate included)"
MARK="[ARO-RC1-FOLLOWUP]"
DISCUSS_1="https://github.com/joy7758/aro-audit/discussions/3"
DISCUSS_2="https://github.com/joy7758/aro-audit/discussions/4"

# 你要维护者执行的“最小验收命令”（务必只保留一条）
MIN_CMD="./tools/run_conformance.sh"

COMMENT="$(cat <<COMMENT
${MARK}
感谢维护！为避免在多个仓库分散讨论，我把所有 RC1 反馈统一收口到这里：
- ${DISCUSS_1}
- ${DISCUSS_2}

最小验收（1 条命令）：
\`\`\`bash
${MIN_CMD}
\`\`\`

如果你愿意进一步评审：
1) 看到 \`VERIFY_OK\` / \`VERIFY_FAIL(attack)\` 即代表 conformance gate 正常
2) 任何疑问/改动建议请直接贴到 Discussion（或提 PR，我这边会跟进）
COMMENT
)"

echo "【进度】1/5 预检查 gh"
command -v gh >/dev/null 2>&1 || { echo "❌ 未找到 gh"; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "❌ gh 未登录（先 gh auth login）"; exit 2; }

echo "【进度】2/5 确认最小验收脚本存在：${MIN_CMD}"
[[ -f "./tools/run_conformance.sh" ]] || { echo "❌ 找不到 ./tools/run_conformance.sh"; exit 2; }

echo "【进度】3/5 批量跟进评论（10 个目标）"
OK=0
SKIP=0
MISS=0

while IFS= read -r REPO; do
  [[ -z "$REPO" ]] && continue

  URL="$(gh issue list -R "$REPO" --limit 50 --json title,url,number \
    --jq ".[] | select(.title == \"$TITLE\") | .url" | head -n 1 || true)"

  if [[ -z "$URL" ]]; then
    echo "MISS: $REPO (未找到匹配标题的 Issue)"
    MISS=$((MISS+1))
    continue
  fi

  NUM="$(echo "$URL" | awk -F/ '{print $NF}')"

  # 检查是否已经发过跟进（含 MARK）
  HAS="$(gh issue view -R "$REPO" "$NUM" --comments --json comments \
    --jq ".comments[].body | select(contains(\"$MARK\"))" | head -n 1 || true)"

  if [[ -n "$HAS" ]]; then
    echo "SKIP: $REPO#$NUM (已跟进过)"
    SKIP=$((SKIP+1))
    continue
  fi

  gh issue comment -R "$REPO" "$NUM" --body "$COMMENT" >/dev/null
  echo "OK: $REPO#$NUM 已评论"
  OK=$((OK+1))
done < tools/rc1_outreach_targets.txt

echo "【结果】OK=$OK SKIP=$SKIP MISS=$MISS"
