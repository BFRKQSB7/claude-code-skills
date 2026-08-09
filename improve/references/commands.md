# 命令参考

## 语言检测

```bash
# 用脚本（比内联更健壮，过滤 node_modules/.git/cache）:
# 用法: source scripts/detect-lang.sh [目录] → python|javascript|rust|go|bash|unknown
source scripts/detect-lang.sh
detect_lang .
```

## 发布命令（语言自适应）

> ⚠️ **提交身份检查（★ 2026-08-05 教训，balance-hud / kakuyomu-scraper / claude-code-skills 踩坑）**:
> commit 前先确认身份 `git config user.email` = `226671264+BFRKQSB7@users.noreply.github.com`（本人账号，勿用 `nyro@...` 等）。
> commit 后复核 `git log -1 --format='%an <%ae>'`。提交邮箱会被 GitHub 关联到账号 → 错配 = 整个仓库贡献归属陌生人，
> 只能 `git filter-branch --env-filter` 重写历史 + `git push --force` 修正。

> ⚠️ **本地克隆纪律（用户登记 2026-08-10）**: 为对比/改版本而克隆的仓库，**先 `git pull` 拉最新**，改完/对比完**删除克隆**（`rm -rf <克隆目录>`），不留多余文件。误留 = 后续误用旧副本 + 磁盘垃圾。

> ⚠️ **发布偏好（用户登记 2026-08-09，发布必做）**:
> 1. **About 必填** — 建仓后 `gh repo edit <owner>/<repo> --description "<描述>"` 必须执行，空 About 不允许发布。
> 2. **双语言 README（文件切换版，★ 2026-08-10 更正）** — 根 `README.md` 放中文（默认），英文在 `docs/en/README.md`，标题下放语言切换条。**发布/改 README 时中英两版必须同步更新**，不允许只改一版。

## 版本号更新准则（x.y.z，不自由发挥）

> 用户登记 2026-08-10。发布前按此定版本号，禁止随手编。**覆盖发布仅限两类**：小更新+距上次不久、删已发布文件的个性化信息；其余一律新 tag。

| 更新类型 | 版本动作 |
|---|---|
| 小补丁 / 修 bug | z+1 |
| 新增功能（非破坏） | y+1 |
| 架构更新 / 大量新功能 / 与上一版差异大 | x+1 |
| 删除已发布文件的个性化信息 | **覆盖更新**（重打同 tag + 替换 release assets），发布页**不额外说明** |
| 小更新 + 距上次发布不久 | **覆盖发布**（重打同 tag + 替换 assets） |
| 小更新 + 距上次发布久 | z+1，新 release |
| 大更新（默认） | 按 x/y/z 规则定新版本号，新 release |
| 多项更新混合 | 按**最大的一档**算（如 修 bug + 新功能 → y+1） |
| 超多项 / 难以归类 | 模型自己评估选最贴切一档，发布说明里写明判断依据 |

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
