# Migration / Refactor / Cleanup

> 加载条件: 任务涉及 migration, refactor, delete, paths, cron, naming, rename, 迁移, 重命名, 删除, 清理

---

## ★★★ 变更后未全局 grep → 引用断裂 (置信度: high, 命中: 9)

> **→ 常加载** `[lessons-critical.md](lessons-critical.md)` 含完整 Rule / 6 子模式 / 防御 / 再次记录

---

## ★ [2026-07-05] 衍生项目未替换旧仓库引用 → Issue 链接指向错误仓库 (置信度: high, 命中: 1)

**Rule**: 从上游 fork/adapt 的项目，必须全局替换旧 repo URL + issue references
**Wrong**: `commands/setup.md` 从 `jarrodwatts/claude-hud` 复制但 issue references 仍指向 `jarrodwatts/balance-hud`（#531, #547, #326, #521, #315）→ 用户点击 issue 链接跳转到旧仓库
**Right**: `grep -rn "旧owner/旧repo"` 全项目 → 逐条替换为新仓库 → 验证 issue 链接可达
**Why**: 这些链接是 setup 命令排错的核心参考。指向错误仓库 = 用户看到不相关的 issue history = 排错失败。
**泛化**: 任何 fork/adapt 项目：旧 URL、旧 owner/repo、旧 email、旧品牌名 — 全部 grep 替换。setup.md/README/CONTRIBUTING 是重灾区。
**检测**: `grep -rn "github.com/[old-owner]" --include="*.md" --include="*.json"`
