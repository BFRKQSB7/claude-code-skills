#!/usr/bin/env bash
# 检测项目主要编程语言
# 用法: source scripts/detect-lang.sh [目录]
# 输出: python|javascript|rust|go|bash|unknown

detect_lang() {
  local dir="${1:-.}"
  local -A counts=()
  local total=0

  # 统计各语言源文件数
  for ext in py js ts tsx jsx mjs cjs rs go sh bash zsh; do
    local count
    count=$(find "$dir" -maxdepth 3 -name "*.$ext" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/__pycache__/*" -not -path "*/target/*" -not -path "*/vendor/*" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
      counts[$ext]=$count
      total=$((total + count))
    fi
  done

  if [ "$total" -eq 0 ]; then
    echo "unknown"
    return
  fi

  # 聚合到语言
  local -A lang_counts=()
  for ext in "${!counts[@]}"; do
    case "$ext" in
      py) lang_counts[python]=$((lang_counts[python] + counts[$ext])) ;;
      js|ts|tsx|jsx|mjs|cjs) lang_counts[javascript]=$((lang_counts[javascript] + counts[$ext])) ;;
      rs) lang_counts[rust]=$((lang_counts[rust] + counts[$ext])) ;;
      go) lang_counts[go]=$((lang_counts[go] + counts[$ext])) ;;
      sh|bash|zsh) lang_counts[bash]=$((lang_counts[bash] + counts[$ext])) ;;
    esac
  done

  # 找数量最多的语言
  local max_lang="" max_count=0
  for lang in "${!lang_counts[@]}"; do
    if [ "${lang_counts[$lang]}" -gt "$max_count" ]; then
      max_count=${lang_counts[$lang]}
      max_lang=$lang
    fi
  done

  echo "$max_lang"
  return
}

# 如果有参数，直接运行
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  detect_lang "$@"
fi
