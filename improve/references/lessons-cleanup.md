# Migration / Refactor / Cleanup

> 加载条件: 任务涉及 migration, refactor, delete, paths, cron, naming, rename, 迁移, 重命名, 删除, 清理

---

## ★★★ 变更后未全局 grep → 引用断裂 (置信度: high, 命中: 10)

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

## ★★★ [2026-08-08] 发布文件带本机个性化信息 → 用户名/盘符路径/端口泄漏 (置信度: high, 命中: 3)

> **→ 常加载** `lessons-critical.md` 含完整 Rule / 检测模式（含盘符路径固定串扫）/ 多次命中记录

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
**Wrong**: 调试 OCR 留 `ocr_stderr.txt`+`ocr_stderr2.txt`；SDXL 验证截图留 `outputs/comfyui_*.png`；绘世启动器解压副本留 `项目/.launcher`（75M，真正运行的其实在 `<盘符>:\<软件目录>\`）→ 目录堆满重复与调试垃圾
**Right**: 会话收尾 `ls` 目录逐项分类：临时→删，缓存→留（自动再生），正式→留；大体积工具放正式位置（`<盘符>:\<软件目录>`），项目目录不留副本
**Why**: 临时产物对后续会话零价值，还干扰「哪是正式产出」的判断；多会话各留一份 → 目录膨胀（2026-08-10 清理项目目录，垃圾项占大头）
**检测**: 收尾 `ls` 目录按「正式/缓存/临时」分类，临时项零残留

---

## ★ [2026-08-11] Write 工具 Windows 字面路径 vs Bash /tmp → 误建盘符根目录 (置信度: high, 命中: 1)

**Rule**: Git Bash `/tmp` = `C:/Users/<user>/AppData/Local/Temp`（`pwd -W` / `cygpath -w` 可查），但 Write/Edit 工具用 Windows 字面路径。给 Bash 产物写文件前先 `pwd -W` 确认映射，写完 `ls` 核对落点。
**Wrong**: 克隆在 `/tmp/aps-clone`（=AppData\Local\Temp），Write 写到 `<盘符>:\tmp\aps-clone` → 两处副本 + 盘符根多出垃圾目录。
**Right**: 先 `pwd -W` 取真实 Windows 路径再 Write；或 Bash `cp` 落地。写错路径后 `rm -rf` 清掉误建目录。
**Why**: Bash 与 Write 工具路径语义不同（/tmp 映射 vs 字面盘符）。跨工具写文件是路径错位重灾区。

---

## ★ [2026-08-11] 发布仓库不留旧版备份文件，git 历史即备份 (命中: 1)

**泛化**: 发布仓库只放当前发布物；「旧版备份」由 git tag/历史承担，不留 index_old.html 式冗余文件（14MB 副本 + README/Release 残留引用 + 用户困惑哪个是正式版）。
**核心**: 删除已发布备份文件时必须连带 grep 清理 README/Release 正文里的当前态引用；历史变更日志条目属史实，保留。

---

## ★★ [2026-08-12] 发布 bump 版本号只改发布副本 → 本地源文件版本落后 (置信度: high, 命中: 1)

**Rule**: 发布工具 bump 版本号时，**本地源文件 + 发布副本双写同步**；commit 前 grep 两边都零残留旧版本号，并 diff 确认两文件一致。
**Wrong**: 只改发布克隆（index.html v2.6.0→v2.7.0）就 commit，本地源文件仍是 v2.6.0 → 用户提醒「本地的你也得改啊」
**Right**: 发布流程把「同步本地源文件版本号」列一步；`diff <(本地) <(发布副本)` 一致再 commit
**Why**: 本地源文件是日常运行版本 + 后续编辑基底。版本号落后 = 显示与发布不符，下次改版基于旧版继续 → 双源分化（lessons-critical 子模式 #1 迁移保留旧目录）。

---

## ★ [2026-08-12] 维护注释写入锚点名 → 脚本 count 断言失准 (置信度: high, 命中: 1)

**Rule**: 用「字符串锚点 + count==N 断言」定位/改文件时，锚点名可能同时出现在注释/文档里——若在注释里写了该锚点名作说明，`s.count(anchor)` 会 >1 断言失败。改用更精确锚点（带数据首元素特征，如 `const X = [["data",`）或按首次出现定位。
**Wrong**: 文件头部维护注释写了 `const FULL_TAGS = [` 作定位说明 → 脚本 `assert s.count('const FULL_TAGS = [')==1` 失败（实际 count=6，注释里出现 5 次）
**Right**: 锚点带数据特征 `const FULL_TAGS = [["newest",` 锁定真实声明，注释文本不受影响
**Why**: 人写的维护文档与脚本逻辑共用同一字符串常量时互相干扰；断言失败是表面，静默插错位置是更糟的隐性失败。

---

## ★ [2026-08-12] 发布前未自查工具界面版本号 → 覆盖发布返工 (置信度: high, 命中: 1)

**Rule**: 发布新工具前，自查**界面各处**版本号显示与当前版本一致——顶部标题 h1、页脚、`<title>` 都要带版本号，且与同族已发布工具（如超市 h1 带版本号）惯例对齐。漏一处 → 用户发现 → 覆盖发布（`gh release delete --cleanup-tag` + 重建）返工。
**Wrong**: 写实提示词生成器 v1.0.0 发布，`<title>`/footer 带版本号但**左上角 h1 标题漏了** → 用户提醒「左上角标题没带版本号」→ 覆盖发布一次
**Right**: 发布前 grep 界面可见的版本显示位置（h1 / title / footer）+ 对照同族工具惯例；版本号出现次数与期望一致
**Why**: 工具 UI 是用户第一眼看到的地方，版本号缺失 = 与发布不符 + 触发额外发布循环。

---

## ★ [2026-08-12] 用户说「把库放进来」默认全量嵌入 → 返工 (置信度: high, 命中: 1)

**Rule**: 用户要求「把某个数据源/库放进来 / 拿那个改一改」时，动手前先确认**范围（全量 vs 常用子集）和形式（原样嵌入 vs 转换适配）**，别默认全量嵌入。数据量级差异大（38KB vs 13MB），「导入」≠「全量嵌入」。
**Wrong**: 用户说「导入超市的库」→ 把 321,450 条（13MB）整个嵌入生成器 + 搜索框，用户纠正「不是这个意思，把常用的导进来，分类做适配」
**Right**: 先问/确认范围与适配方式（AskUserQuestion：全量嵌入 / 常用分类并入 / 转自然语言短语）；按确认实施
**Why**: 「库」「那个」是模糊指代；用户真实意图常是「提取常用、适配进现有结构」，全量嵌入会改变工具体积与定位。

---

## ★ [2026-08-12] 桌面 app 源码放运行时目录 → 两套配置分叉 (置信度: high, 命中: 1)

**Rule**: 桌面 app 源码目录与运行时数据目录分离——源码独立放一处，运行时数据（exe / llama-server.exe / models/ / 配置预设 json）统一在 exe 目录。源码别放运行时目录的 dev/ 子目录，否则 BASE 按 `__file__` 指到 dev/，出现「源码版读写 dev/ 的 llm_presets.json / llm_gui_config.json，exe 版读写根目录」的两套分叉。
**Wrong**: LLM GUI 源码 `<盘符>:\<软件目录>\dev\llm_gui.py` 嵌在 llama 运行时目录 → dev/ 与根目录各一套 presets/config，数据双源、改错份
**Right**: 源码迁独立目录（`~/<源码目录>/llm-launcher-gui`）；移走后把运行时目录残留（dev/ build/ dist/ __pycache__）**归档移走不删**（`_archived/`），已编译 exe 留在原处照常用
**Why**: 源码目录 ≠ exe 目录 → 同一 app 两套配置读写分叉，极难排查；清理残留「移走不删」保证可恢复
**泛化**: 源码内嵌运行时目录的项目：先分目录再归档残留；归档后 diff 两份配置确认无独有数据再安心
**检测**: 迁移后 `ls` 运行时目录只剩必需文件 + 一个 `_archived/`；两份 presets diff 无独有模型

---

## ★ [2026-08-13] Windows 大小写改名不落地 → git 跟踪名不变 (置信度: high, 命中: 1)

**Rule**: NTFS 大小写不敏感 + git `core.ignorecase=true` 时，文件名大小写改动（`skill.md`→`SKILL.md`）不能靠 Write/cp 覆盖——磁盘是同一物理文件，git 仍记为 `M <旧名>`，index 跟踪名不变，push 后远端还是小写。必须两步 `git mv` 经临时名强制：`git mv <旧> <临时名> && git mv <临时名> <大写名>`；改名后 `git status` 应显示 `R`（rename），`os.listdir` 确认存储名为大写。
**Wrong**: cp/Write 直接生成大写文件 → `git status` 显示 `M skill.md`，远端提交仍是 `skill.md` → 大小写敏感 glob 的 skill 加载器（Codex 匹配 `SKILL.md`）可能失败
**Right**: 两步 `git mv`；commit 后 `git ls-remote` / GitHub API contents 核验远端路径为大写
**Why**: git 在 Windows 用 index 跟踪名区分大小写，磁盘只有一个物理文件；不强制 rename 就沿用旧大小写。skill 文件名大小写对加载器是真实差异。

---

## ★ [2026-08-15] 发布借鉴他人产品的界面/图标 → 缺致谢声明 (置信度: high, 命中: 1)

**Rule**: 项目界面/图标复用其他产品元素（如 ChatGPT/DeepSeek）→ 发布前 README 必须加致谢声明（中英两版同步），别等用户提醒
**Wrong**: llama-chat-ui 布局/图标直接复用 ChatGPT+DeepSeek，README 只写「ChatGPT 风格」→ 用户更正「有些元素直接拿来用了」
**Right**: README 加「致谢/Acknowledgments」节：界面布局、交互与部分图标借鉴自 XXX 网页版（部分直接复用）；中英两版同步更新
**Why**: 直接复用他人产品元素不声明 = 误导原创 + 遗漏合规；低成本诚实声明防返工

---

## ★ [2026-08-15] 发布门禁代理端口正则误报 CORS 通用示例端口 (置信度: high, 命中: 1)

**Rule**: 发布门禁扫 `127.0.0.1:[0-9]+|localhost:[0-9]+` 命中时，先区分**本机代理端口**（如 `<代理端口>`，个性化泄漏）vs **通用示例端口**（前端开发默认 3000/5173/8080，教学占位），别一刀切当泄漏
**Wrong**: llm-launcher-gui 加 `--cors` 功能，示例 `http://localhost:3000,http://localhost:5173` 被门禁正则命中 → 差点当泄漏误删示例
**Right**: 通用前端开发端口按示例放行保留；只删对应用户代理配置的本机端口
**Why**: 泄漏的是本机个性化端口，示例端口删了反而让文档/工具失去教学价值
**检测**: 命中后核对端口是否对应用户代理配置（查记忆/代理工具）；3000/5173/8000/8080 默认当示例

---

## ★ [2026-08-17] 覆盖发布重打同 tag → 忘 force push tag (置信度: high, 命中: 1)

**Rule**: 覆盖发布（重打同 tag）时必须 `git push origin <tag> --force`，否则旧 tag 留在远端、release 仍指向旧 commit
**Wrong**: llm-launcher-gui v1.7.0 CORS 修正后本地 `git tag -d && git tag -a` 重打，push 时漏 `--force` → 远端 tag 还是旧指向
**Right**: 重打 tag 三步：`git tag -d vX` → `git tag -a vX` → `git push origin vX --force`（先删远端 release 再重建）
**Why**: 覆盖发布 = 让 release 页指向最新 commit；tag 不 force 推送则 release 资产与代码脱节

---

## ★ [2026-08-17] 验证 annotated tag 指向 → rev-parse 返回 tag 对象 hash 误判 (置信度: high, 命中: 1)

**Rule**: `git rev-parse <tag>` 对 annotated tag 返回 tag 对象自身 hash（≠ commit hash）；验证 tag 指向哪个提交用 `git show <tag>` 或 `git rev-parse <tag>^{}`，别拿它当 commit 判断
**Wrong**: llm-launcher-gui 审计 v1.7.0 tag 指向，`git rev-parse v1.7.0` 得 fb819a9 ≠ HEAD 5abea80 → 误以为 tag 挂错提交
**Right**: `git show v1.7.0` 显示 peeled 目标就是 5abea80（`Tagger` 行下方是 commit hash）；或 `git rev-parse v1.7.0^{}` 直接剥出 commit hash
**Why**: annotated tag 是独立对象，rev-parse 不带 `^{}` 给的是对象 hash；用 commit hash 比对 tag 会虚惊一场

---

## ★ [2026-08-21] 版本 grep 用 v 前缀排除 → README 徽章漏检假通过 (置信度: high, 命中: 1)

**Rule**: bump 版本号后全局 grep 旧版本时，**不要用 `vX.Y.Z` 形式做排除**——README 徽章（`![badge/version-v1.8.0-blue]`）自带 `v` 前缀，会被一起滤掉；只排除变更日志历史行（含 `（2026`），其余逐条人工确认
**Wrong**: `grep -rn "1\.8\.0" . | grep -v "v1\.8\.0"` → README 顶部徽章行被滤掉 → "零残留"门禁假通过，徽章留在 v1.8.0（本次 llm-launcher-gui v1.9.0 发布实测踩中）
**Right**: 门禁分两步——(1) grep 全部旧版本，仅排除含 `（2026`/`(2026` 的 changelog 历史行；(2) 单独 `grep -iE "badge|version" README*` 核对徽章/标题行
**Why**: 徽章用 img.shields.io `version-v1.8.0` 形式，`v` 前缀是徽章组成部分，用它做排除恰好命中徽章。版本号是发布一致性核心，漏一处用户可见 → 返工
**关联**: [[发布 bump 版本号本地源文件同步]] [[发布前未自查界面版本号]]

