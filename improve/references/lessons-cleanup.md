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

---

## ★★ [2026-08-08] 发布文件带本机个性化信息 → 用户名/绝对路径泄漏 (置信度: high, 命中: 1)

**Rule**: 任何发布到 GitHub / 公开分享的文件，发布前必须扫描并清除**本机个性化信息**：OS 用户名、含用户名的绝对路径（`C:\Users\<用户名>\`、`/Users/<用户名>/`、`/home/<用户名>/`）、本机代理端口、hostname、密钥 token。发布源只允许**通用占位符**（`~`、`%USERPROFILE%`、`<用户名>`、运行时 `Path.home()`）。
**Wrong**: html-guide README / Release 正文带 `C:\Users\NYRO\...`（泄漏本机用户名）；kakuyomu-scraper `OUT_DIR` 硬编码 `C:\Users\NYRO\Desktop\1`（功能 + 泄漏）；improve lessons、balance-hud README 同样带本机路径。用户点名「发布的文件不能带本机个性化信息」。
**Right**:
1. 发布前扫描：`grep -rIn "C:\\\\Users\\\\\|/Users/\|/home/\|<OS用户名>\|<本机端口>" --exclude-dir=.git .`
2. 路径一律用通用形式：`~` / `%USERPROFILE%` / `Path.home()`（运行时动态取当前用户，发布文件零泄漏）
3. 作者 / 版权字段用 GitHub 昵称而非 OS 用户名（OS 用户名泄漏本机账户名；若用笔名需确认是有意为之）
4. 历史 Release 正文同样要清（`gh release view` → `gh release edit`），不只仓库文件
**Why**: 公开仓库任何人可见。`C:\Users\<用户名>\` 直接暴露本机账户名，可被社工；硬编码路径还会让脚本在别人机器上失效。
**检测**: 发布后 `grep -rIn "<OS用户名>" .` 零残留 + `gh release view <新> --json body | grep "<OS用户名>"` 零残留
