#!/usr/bin/env bash
set -euo pipefail

echo "【进度】1/4 预检查 gh + git 状态"
command -v gh >/dev/null 2>&1 || { echo "❌ 未找到 gh"; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "❌ gh 未登录（先 gh auth login）"; exit 2; }

TITLE="RC1 Review Request: AAR-MCP-2.0 Verifiable Interaction Layer (Conformance Gate included)"

echo "【进度】2/4 生成外联日志 docs/rc1/outreach_log.md（抓取 Issue 链接）"
mkdir -p docs/rc1
OUT="docs/rc1/outreach_log.md"

{
  echo "# RC1 外联日志（自动生成）"
  echo
  echo "- 标题匹配：\`$TITLE\`"
  echo "- 目标清单：\`tools/rc1_outreach_targets.txt\`"
  echo "- 外联文案：\`tools/rc1_outreach_post.md\`"
  echo
  echo "## 已创建 Issue 列表"
  echo
  echo "| 目标仓库 | Issue 链接 | 状态 | 下一步动作 |"
  echo "|---|---|---|---|"
} > "$OUT"

OK=0
MISS=0

while IFS= read -r REPO; do
  [[ -z "$REPO" ]] && continue

  # 取最近 30 条，匹配标题，拿 URL
  URL="$(gh issue list -R "$REPO" --limit 30 --json title,url,number,createdAt \
    --jq ".[] | select(.title == \"$TITLE\") | .url" | head -n 1 || true)"

  if [[ -n "$URL" ]]; then
    OK=$((OK+1))
    echo "| \`$REPO\` | $URL | 已发出 | 24h 内无回复就去 Discussion #3/#4 贴一次“提醒+简化验收” |" >> "$OUT"
  else
    MISS=$((MISS+1))
    echo "| \`$REPO\` | *(未检索到，可能列表没命中或权限限制)* | 待核对 | 手动打开仓库 Issues 搜索同标题 |" >> "$OUT"
  fi
done < tools/rc1_outreach_targets.txt

{
  echo
  echo "## 汇总"
  echo
  echo "- 自动检索到链接：$OK"
  echo "- 未命中：$MISS"
  echo
  echo "## 回流漏斗（你只要盯这个）"
  echo
  echo "1) **所有反馈统一引导到 Discussions #3/#4**（不要在 10 个仓库里分散讨论）"
  echo "2) 对方要代码改动：让他提 PR，并使用你的 PR 模板"
  echo "3) 对方只评论不动手：让他按 Issue 模板给“最小复现/验收命令/反例”"
} >> "$OUT"

echo "【进度】3/4 git 提交（把外联脚本变成可复用资产）"
git add tools/rc1_outreach_run.sh tools/rc1_outreach_targets.txt tools/rc1_outreach_post.md "$OUT"

git commit -m "chore(rc1): add outreach automation + log (issue links, feedback funnel)" || {
  echo "⚠️ 没有新变更可提交（可能你已提交过）"
}

echo "【进度】4/4 推送到远程 main"
git push origin main

echo "✅ 完成：外联资产已固化并推送"
echo "产物：$OUT"
