# 命令参考

## 语言检测

```bash
# 扫描当前目录，按优先级输出主要语言
# 优先级: 最近修改的源代码文件 > 数量最多的扩展名 > 用户指定
detect_lang() {
  local exts=("py" "js" "ts" "tsx" "jsx" "rs" "go" "sh")
  local lang=""
  for ext in "${exts[@]}"; do
    count=$(find . -maxdepth 3 -name "*.$ext" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
      case "$ext" in
        py) lang="python";;
        js|ts|tsx|jsx|mjs|cjs) lang="javascript";;
        rs) lang="rust";;
        go) lang="go";;
        sh|bash|zsh) lang="bash";;
      esac
      echo "$lang ($count .$ext files)"
      return
    fi
  done
  echo "unknown"
}
```

## 发布命令（语言自适应）

> ⚠️ **提交身份检查（★ 2026-08-05 教训，balance-hud / kakuyomu-scraper / claude-code-skills 踩坑）**:
> commit 前先确认身份 `git config user.email` = `226671264+BFRKQSB7@users.noreply.github.com`（本人账号，勿用 `nyro@...` 等）。
> commit 后复核 `git log -1 --format='%an <%ae>'`。提交邮箱会被 GitHub 关联到账号 → 错配 = 整个仓库贡献归属陌生人，
> 只能 `git filter-branch --env-filter` 重写历史 + `git push --force` 修正。

### Python 项目
```bash
# 版本号同步（pyproject.toml）
sed -i "s/version = \"[0-9.]*\"/version = \"$NEW_VER\"/" pyproject.toml

# 全局 grep 旧版本号 → 零残留
grep -rn "$OLD_VER" . --include="*.py" --include="*.toml" --include="*.md" --include="*.cfg" --include="*.ini"

# 打包
python -m build
# 或: pip install --editable .

# GitHub Release
gh release create "v$NEW_VER" dist/* --title "v$NEW_VER" --notes-file /tmp/release_notes.md

# PyPI (可选)
twine upload dist/*
```

### JS/TS 项目
```bash
# 版本号同步（package.json）
npm version "$NEW_VER" --no-git-tag-version

# 全局 grep 旧版本号 → 零残留
grep -rn "$OLD_VER" . --include="*.json" --include="*.js" --include="*.ts" --include="*.md"

# 打包
npm pack
# 或: npm publish (if public)

# GitHub Release
gh release create "v$NEW_VER" *.tgz --title "v$NEW_VER" --notes-file /tmp/release_notes.md
```

### Rust 项目
```bash
# 版本号同步（Cargo.toml）
sed -i "s/^version = \"[0-9.]*\"/version = \"$NEW_VER\"/" Cargo.toml

# 全局 grep 旧版本号 → 零残留
grep -rn "$OLD_VER" . --include="*.toml" --include="*.rs" --include="*.md"

# 构建 + 发布
cargo build --release
gh release create "v$NEW_VER" --title "v$NEW_VER" --notes-file /tmp/release_notes.md
# 或: cargo publish
```

### Go 项目
```bash
# Go 版本号在 git tag，不在源码
# 全局 grep 旧版本号 → 零残留（README/文档中可能硬编码）
grep -rn "$OLD_VER" . --include="*.go" --include="*.md" --include="go.mod"

gh release create "v$NEW_VER" --title "v$NEW_VER" --notes-file /tmp/release_notes.md
```

### Claude Code Plugin（保留现有）
```bash
# 打包（命名规范: "项目名 v版本号.zip"）
powershell Compress-Archive -Path '<name>-plugin' -DestinationPath '<项目名> v<版本号>.zip' -Force

# !! 版本号变更后强制全局 grep（防引用断裂 — ★★★ 已命中 9 次）
grep -rn "$OLD_VER" . --include="*.md" --include="*.json" --include="*.mjs" --include="*.js" --include="*.bat" --include="*.sh" --include="*.yml" --include="*.yaml"

# 检查旧路径引用
grep -r "old-name/" ~/.claude/plugins/<name>/

# 检查 cron 残留
cat ~/.claude/scheduled_tasks.json

# !! Git push 后验证（防分支错位 — ★★★ 子模式 #6）
gh api repos/<owner>/<repo> --jq '.default_branch'
gh api repos/<owner>/<repo>/contents/README.md --jq '.content' | base64 -d | head -5
```

## 模板

发布时使用统一模板:
- **RELEASE**: [release-template.md](release-template.md) — 语言自适应 GitHub Release 流程
- **README**: [readme-template.md](readme-template.md) — 语言自适应 README 节顺序

## 创建项目骨架

```bash
# 插件
mkdir -p ~/.claude/plugins/<name>/{.claude-plugin,hooks,scripts}

# Python
mkdir -p <name>/{src/<name>,tests} && touch <name>/pyproject.toml <name>/README.md

# JS/TS
mkdir -p <name>/src && cd <name> && npm init -y

# Rust
cargo new <name>

# Go
mkdir <name> && cd <name> && go mod init <module-path>
```
