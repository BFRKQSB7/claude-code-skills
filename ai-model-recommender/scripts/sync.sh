#!/usr/bin/env bash
# 同步/安装 ai-model-recommender skill 到目标目录（默认同步其余两处运行副本）
# 用法: ./scripts/sync.sh                 # 同步到 .agents/skills 与 .cc-switch/skills
#   例: ./scripts/sync.sh ~/.claude/skills/ai-model-recommender  # 指定单目标
# 只复制运行必需文件（白名单）；docs/examples/tests/showcase 等非运行内容一律不进 runtime。
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ $# -gt 0 ]; then
  TARGETS=("$1")
else
  TARGETS=(
    "$HOME/.agents/skills/ai-model-recommender"
    "$HOME/.cc-switch/skills/ai-model-recommender"
  )
fi

# 运行必需文件白名单。新增运行文件须在此登记，否则不会被安装。
RUNTIME=("SKILL.md" "references" "scripts")

for TARGET in "${TARGETS[@]}"; do
  echo "==> 同步到 $TARGET"
  mkdir -p "$TARGET"
  for item in "${RUNTIME[@]}"; do
    if [ ! -e "$SRC/$item" ]; then
      echo "WARN: $SRC/$item 不存在，跳过" >&2
      continue
    fi
    # 镜像式复制：先清目标同名项，避免陈旧文件/构建产物残留
    rm -rf "$TARGET/$item"
    cp -R "$SRC/$item" "$TARGET/$item"
  done
  find "$TARGET" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

  # 验证：目标目录不得包含白名单外的顶层内容
  EXTRA="$(find "$TARGET" -mindepth 1 -maxdepth 1 | xargs -n1 basename | grep -vxE "$(IFS='|'; echo "${RUNTIME[*]}")" || true)"
  if [ -n "$EXTRA" ]; then
    echo "NOTE: 目标存在白名单外内容（不会被删除）: $EXTRA" >&2
  fi
done

echo ""
echo "同步完成。当前运行目录文件："
find "$SRC" -type f | sort
