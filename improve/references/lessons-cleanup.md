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

## ★ [2026-08-10] cp 多源+多目标 → 全部拷进最后一个目录，产生垃圾文件 (置信度: high, 命中: 1)

**Rule**: `cp f1 f2 f3 dest1 dest2` 中 cp 把最后一个目录参数当目标目录，所有源全拷进去；dest1 被忽略。同步多文件到多目标 → 分条 cp（`cp a X/Y.md && cp b c X/refs/`），别一条命令多源多目标。
**Wrong**: `cp a.md b.md c.md X/Y.md X/refs/` → a.md 被拷成 `X/refs/a.md`，X/Y.md 没更新 → 备份仓库污染（improve/references/SKILL.md 垃圾文件）
**Right**: 每条 cp 目标唯一；同步后 diff 逐文件核对 + `git status` 看新增文件位置
**Why**: cp 的目录/文件目标判定只看最后一个参数。多目标人脑假设"一一对应"，实际全进最后目录 → 静默错位。
**检测**: 同步后逐文件 `diff <(tr -d '\r' < src) <(tr -d '\r' < dst)`；`find dst -name "*.md"` 无意外新文件

---

## ★★ [2026-08-08] 发布文件带本机个性化信息 → 用户名/绝对路径泄漏 (置信度: high, 命中: 2)

**Rule**: 任何发布到 GitHub / 公开分享的文件，发布前必须扫描并清除**本机个性化信息**：OS 用户名、含用户名的绝对路径（`C:\Users\<用户名>\`、`/Users/<用户名>/`、`/home/<用户名>/`）、本机代理端口、hostname、密钥 token。发布源只允许**通用占位符**（`~`、`%USERPROFILE%`、`<用户名>`、运行时 `Path.home()`）。
**Wrong**: html-guide README / Release 正文带 `C:\Users\NYRO\...`（泄漏本机用户名）；kakuyomu-scraper `OUT_DIR` 硬编码 `C:\Users\NYRO\Desktop\1`（功能 + 泄漏）；improve lessons、balance-hud README 同样带本机路径。用户点名「发布的文件不能带本机个性化信息」。
**Right**:
1. 发布前扫描：`grep -rIn "C:\\\\Users\\\\\|/Users/\|/home/\|<OS用户名>\|<本机端口>" --exclude-dir=.git .`
2. 路径一律用通用形式：`~` / `%USERPROFILE%` / `Path.home()`（运行时动态取当前用户，发布文件零泄漏）
3. 作者 / 版权字段用 GitHub 昵称而非 OS 用户名（OS 用户名泄漏本机账户名；若用笔名需确认是有意为之）
4. 历史 Release 正文同样要清（`gh release view` → `gh release edit`），不只仓库文件
**Why**: 公开仓库任何人可见。`C:\Users\<用户名>\` 直接暴露本机账户名，可被社工；硬编码路径还会让脚本在别人机器上失效。
**检测**: 发布后 `grep -rIn "<OS用户名>" .` 零残留 + `gh release view <新> --json body | grep "<OS用户名>"` 零残留

**再次**: 2026-08-10 — html-guide 技能介绍页（公开 GitHub Pages）安装示例写死本机代理端口 `127.0.0.1:7896`，用户提醒后 v2.2.4 清为 `127.0.0.1:&lt;代理端口&gt;` 占位并重发布。教训：**代理端口也属于本机个性化信息**，且会跟着 Pages 一直公开；发公开页前 `grep -n "127.0.0.1:[0-9]" index.html` 也要零残留。
**再次**: 2026-08-10 — llm-sight 发布前扫描抓到 **commands/*.md 与 scripts/setup.py** 里都写了本机代理端口 `127.0.0.1:7896`，清为 `127.0.0.1:<端口>` 占位。教训：**帮助文本/示例参数里的代理端口同样泄漏**；发布前 `grep -rInE "127\.0\.0\.1:[0-9]+"` 要覆盖 .py/.md/.json 全类型，且 **`.venv/` 用 `--exclude-dir` 排除后仍要扫 skill 脚本本体**。

---

## ★ [2026-08-10] git archive --format=tar 条目无前缀 → 解到子目录 staging 为空 → 空/残缺 zip (置信度: high, 命中: 1)

**Rule**: `git archive --format=tar HEAD | tar -x -C <dir>` 的条目是顶层相对路径（无 `llm-sight/` 前缀）。若期望它们落在 `<dir>/llm-sight/`，会解到 `<dir>/` 根下——staging 子目录为空 → zip 只剩目录条目（v1 空 22B），v2 只剩手动拷进去的 models（丢全部 skill 文件）。
**Wrong**: 假设 tar 自带前缀，解到 `STAGE_ROOT`，从 `STAGE_ROOT/llm-sight` 走 os.walk → 空
**Right**: `mkdir -p $STAGE_ROOT/llm-sight && git archive | tar -x -C $STAGE_ROOT/llm-sight`，zip 条目再统一加 `llm-sight/` 前缀
**Why**: git archive 的 tar 不含目录前缀（要前缀得用 `--prefix`）。staging 路径假设错 = 静默产出空/残缺 zip，只有列 zip 内容才暴露（`unzip -l` 抽查 SKILL.md / models 都在）。
**检测**: 打包后 `unzip -l zip` 数文件数 + 抽查关键文件；两份 zip（v1/v2）都要看

---

## ★★ [2026-08-10] 删 skill 只删主目录 → 斜杠命令里还在 (置信度: high, 命中: 2)

**Rule**: 删除 skill 要「删干净」——除 `~/.claude/skills/<name>`，还要扫 `~/.agents/skills/`、`~/.cc-switch/skills/` 等**本机加载目录**，副本全删；再清 `settings.local.json` 的 `skillOverrides` 残留条目。**云端/发布仓库默认不删**（见下条）。真实 skill 名可能与用户叫法不同（ai-fix → `AI-install-and-fix`），搜目录名别搜口语名。
**Wrong**: 只删 `~/.claude/skills/pinokio` → 斜杠命令还在：`.agents` / `.cc-switch` / `claude-code-skills` 各有一份拷贝继续被加载。
**Right**: `find ~/.claude ~/.agents ~/.cc-switch -maxdepth 3 -type d -iname "<skill名>"` → 全删（**不含云端克隆**）→ 删 `skillOverrides` 条目 → 重启会话验证 `/` 里消失。
**Why**: skill 会被多个加载目录复制加载，主目录删 ≠ 删干净；override 残留条目指向尸体，纯噪音。叫法差异会让搜索失败（搜「ai-fix」找不到 `AI-install-and-fix`）。
**检测**: 删除后 find 本机加载目录（.claude/.agents/.cc-switch）零命中 + `grep "<skill名>" settings*.json` 零残留。

**再次**: 2026-08-10 — 同会话连删 `AI-install-and-fix`、`gepeto`、`pinokio` 三个 skill，每个都有 `.agents`+`.cc-switch`（+聚合仓库）副本，只删主目录必然复发。

---

## ★ [2026-08-10] 删 skill 连云端一起删 → 越界 (置信度: high, 命中: 1)

**Rule**: 删除 skill 默认**只删本机加载目录**（`~/.claude/skills`、`~/.agents/skills`、`~/.cc-switch/skills`）；云端/发布仓库（GitHub skill 仓库、`~/claude-code-skills` 克隆）默认保留。只有用户明说「连云端一起删 / push 删除」才 commit+push 删除。
**Wrong**: 用户说「pinokio 从本机删掉」→ 我把删除 commit+push 到云端 `claude-code-skills` → 用户纠正「云端 skill 除特殊说明默认不删除」。
**Right**: 删本机加载目录即可；git 状态出现未授权删除时 `git checkout -- <path>` 恢复；已 push 则开 restore 提交还回（禁 force-push）。
**Why**: 云端仓库是 skill 的备份/发布源，本机删除 ≠ 授权云端删除。删除影响所有克隆与协作者，默认保守，按用户明示的范围执行。
**检测**: push 前 `git status` / `git diff --cached --stat` 只含授权改动，无 skill 文件删除。

---

## ★★ [2026-08-10] 会话临时文件用完不删 → 项目目录堆垃圾 (置信度: high, 命中: 2)

**Rule**: 会话工作产生的**一次性临时产物**（调试日志、验证截图、临时下载/解压副本、可再下载的工具）用完后当场删；项目/工作目录只留正式产出与发布克隆。
**Wrong**: 调试 OCR 留 `ocr_stderr.txt`+`ocr_stderr2.txt`；SDXL 验证截图留 `outputs/comfyui_*.png`；绘世启动器解压副本留 `项目/.launcher`（75M，真正运行的其实在 `E:\AI\ai-image\`）→ 目录堆满重复与调试垃圾
**Right**: 会话收尾 `ls` 目录逐项分类：临时→删，缓存→留（自动再生），正式→留；大体积工具放正式位置（E:\AI\ai-image），项目目录不留副本
**Why**: 临时产物对后续会话零价值，还干扰「哪是正式产出」的判断；多会话各留一份 → 目录膨胀（2026-08-10 清理项目目录，垃圾项占大头）
**检测**: 收尾 `ls` 目录按「正式/缓存/临时」分类，临时项零残留
