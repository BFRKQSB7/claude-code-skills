# Critical Lessons — Always Loaded

> ★★★ 系统性顽疾。Phase 1 无条件加载（~1KB），不依赖关键词路由。

## 轮换规则
- `permanent`: 复入 ≥2 次 → 永驻；`rotatable`: 首次入列，30 天未命中 → 降级回 domain；`dormant`: 降级后再次 ★★★ → 升 `permanent`
- **Phase 3 维护**: 扫所有教训 → ★★★ 且不在 critical → 加入（`rotatable`）→ 超 30 天降级 → 复入标 `permanent`

---

## ★★★ 变更后未全局 grep → 引用断裂 `rotatable` (since: 2026-06-21, last_hit: 2026-08-07)

**Rule**: 任何变更操作（删除/重命名/移动/重构）→ `grep -r "old-identifier"` 全项目文本文件 → 逐条更新 → 再宣称完成
**Why**: 人眼无法穷举所有引用点。一条引用断裂 = 安装脚本 404 / 用户看到旧版 README / GitHub 页面展示旧内容。

| # | 子模式 | 现象 | 命中 |
|---|--------|------|------|
| 1 | 迁移保留旧目录 | 两份数据源，内容分化 | 1 |
| 2 | 删除功能不删引用 | README/注释/脚本仍引已删功能 | 1 |
| 3 | 删除目录 cron 残留 | 定时任务静默失败 | 1 |
| 4 | 重命名文件引用未同步 | 安装脚本/下载链接引旧名 | 3 |
| 5 | 修复旧数据分多次 | 修了格式漏了数据，用户提醒才补 | 2 |
| 6 | 推错分支/默认分支不匹配 | GitHub 页面展示旧内容 | 1 |
| 7 | 衍生项目旧 repo issue 引用未替换 | setup.md issue 链接指向旧仓库 | 1 |

**防御**:
- 版本号变更后必跑 `grep -rn "旧版本号"` 全局扫描 → 零残留才能继续
- git push 后: 确认默认分支匹配 → 验证 GitHub README 版本号正确 → 宣称完成
- 高风险点: README 安装步骤、install-*.bat/sh、RELEASE Checksums、GitHub 默认分支

**再次**: 2026-06-21 — v1.1.3 发布，README 安装步骤仍引 v1.1.2（子模式 #4）；git push 到 master 但默认分支是 main（子模式 #6）

---

## ★★★ 发布流程手动重复 → 遗漏步骤 `rotatable` (since: 2026-06-21, last_hit: 2026-08-07)

**Rule**: >2 次的重复流程必须自动化或硬编码检查点，不能依赖人脑清单
**Wrong**: 发布依赖人脑记步骤 → 本次会话遗漏 2 次（文件名引用 + 分支错位）
**Right**: Phase 2 强制门禁 — 每一步有可机器验证的检查点
**核心**: 人脑不适合"每次 N 步清单"。清单的每一项必须能自动验证（grep / gh api / diff）。

**再次**: 2026-06-16 — 重命名 zip 但 4 处引用未更新；Checksums 漏 bat
**再次**: 2026-06-21 — git push 到 master 但默认分支是 main，未验证 GitHub 页面

---

## ★★★ 空值未检查直接访问 → 运行时崩溃 `rotatable` (since: 2026-07-03, last_hit: 2026-07-02)

**Rule**: 任何来自 I/O 边界（API/DB/文件/用户输入/环境变量）的值，使用前**必须**做空值检查。不假设"这里不可能为空"。
**Why**: Sonar 数据 — null pointer dereference 是继 dead code 之后全球第二常见的可靠性 bug（~1,500 issue/M LoC）。2025 年 6 月 Google Cloud 大宕机的根因 = null 值缺乏错误处理。
**Wrong**: `user.profile.address.city` 不检查链路 / `data.getValue()` 返回 null 不处理 / `interface{}` 类型断言不 comma-ok
**Right**: 类型系统强制 non-null（TS strictNullChecks / Rust Option<T> / Python mypy strict）+ 边界处 assertion fail fast
**泛化**: "不可能为空"是最危险的假设。需求变化/重构/上游变更 = impossible → possible。类型系统 > 注释 > 祈祷。
**检测**: I/O 边界处 grep `?.` `!.` `.unwrap()` — 确认每个都有合理的 null handling 策略

---

## ★★★ 死代码/空语句 → 逻辑静默跳过 `rotatable` (since: 2026-07-03, last_hit: 2026-07-02)

**Rule**: 代码变更后检查条件分支是否真的执行。PR review 必查: 每个 if/for/while 的 body 是否真的能命中。
**Why**: Sonar 数据 — 死代码/"do-nothing"是**全球 #1 最常被检测到的 bug**（~2,100 reliability issue/M LoC）。Apple 著名的 "goto fail" bug（一个多余分号跳过证书验证）就是这种类型 — 让数百万用户暴露于 MITM 攻击。
**Wrong**: `if (condition); doSomething();` — 分号终结 if / `while (cond); { ... }` — 空循环体 / 重构后遗留不可达代码
**Right**: 编译器/IDE warning 视为 error + PR review 检查每个条件体 + linter `no-empty` 规则
**检测**: ESLint `no-empty` / pylint `pointless-statement` / go vet `unreachable` / clippy `semicolon_if_nothing_returned`

---

## ★★★ 测试无断言 → 虚假安全感 `rotatable` (since: 2026-07-03, last_hit: 2026-07-02)

**Rule**: 每个测试必须有显式断言。测试通过 ≠ 代码正确 — 测试可能什么都没验证。
**Why**: Sonar 数据 — "测试无断言"是全球最常见的 **blocker 级别**可维护性 issue。测试只确认"代码没崩溃"，不验证"代码做对了"。虚假的覆盖率 = 比没有测试更危险。
**Wrong**: `test("login works", () => { login(); });` — 没验证返回值/状态/副作用 / `def test_process(): process()` — 没 assert
**Right**: 每个测试至少 1 个 explicit assert / expect: `expect(result).toBe(expected)` / `assert result == expected`
**检测**: `grep -L "assert\|expect" **/*.test.*` 找无断言测试 / ESLint `jest/expect-expect` / pytest `--assert=rewrite`

---

## ★★★ 含格式码字符串按 raw length 截断 → 显示错误 `rotatable` (since: 2026-07-05, last_hit: 2026-07-05)

**Rule**: 含 ANSI/HTML/Markdown 格式码的字符串，任何长度检查/截断必须在**剥离格式后的 visible text** 上操作。`rawString.length` 包含不可见的格式标记，会导致截断位置错误。
**Wrong**: `if (ansiLabel.length > 50) return ansiLabel.slice(0, 47) + '...'` — ANSI escape 占长度但不占宽度
**Right**: 剥离格式 → 按 visible width 判断 → 映射回 raw 索引 → 截断 + 补 closing format + `...`
**Why**: 非可见格式码（ANSI CSI `\x1b[...m`、HTML tags、Markdown links）在 `string.length` 中占位但在显示宽度中为 0。直接在 raw string 上截断 = 实际截断位置远早于预期 = 丢失关键显示信息。

| # | 子模式 | 现象 | 命中 |
|---|--------|------|------|
| 1 | ANSI label 长度限制 | 余额行消费信息被 `...` 替换 | 1 |

**防御**:
- 任何 `MAX_LENGTH` 截断: 先 strip ANSI/markup → 按 visible length 判断
- 如果保留格式截断: 需 visible-to-raw 索引映射（例如 token-based split）
- 短期: 上限设足够大（512+）容纳格式码；长期: 实现 visible-length-based truncation

**再次**: 2026-07-05 — balance-hud `sanitizeBalanceLabel()` MAX_BALANCE_LABEL_LENGTH=50, balance_label 含 ~70 chars ANSI 码 → 用户见 `...` 3 天未定位

---

## ★★★ MCP 工具触发 → 强制加载 lessons-mcp.md `permanent` (since: 2026-07-06, last_hit: 2026-07-06)

**Rule**: 任何 MCP 工具调用（`mcp__*` / `WebFetch` / `WebSearch`）前 → **必须先读** [lessons-mcp.md](lessons-mcp.md)。Chrome 连接失败一次 = 浪费 5-10 分钟 + 打断用户操作。
**Why**: Chrome DevTools MCP 连接需要 4 步手工操作（伪造 DevToolsActivePort），不读教训的代价是平均 6 次重试才能连上。WebFetch 拦截 / snapshot 溢出都有一条正确的绕过路径 → 不查 = 反复撞墙。
**防御**: Phase 1 检测到 MCP 工具关键词（`mcp__` `WebFetch` `WebSearch` `take_snapshot` `take_screenshot` `navigate_page` `evaluate_script` `new_page` `select_page` `click` `fill` `list_pages` `performance` `lighthouse` `upload_file` `browser` `chrome` `devtools` `huggingface` `搜索` `浏览器` `截图` `网页` `访问` `下载` `渲染`）→ 门禁加载 lessons-mcp.md

---

## ★★★ 提交身份错配 → 贡献归属陌生人 `permanent` (since: 2026-08-05, last_hit: 2026-08-09)

**Rule**: 任何 git commit 前，必须确认提交身份正确 — commit 前 `git config user.email`、commit 后 `git log -1 --format='%an <%ae>'` 复核。发布流程 Phase 2 已加「提交身份」门禁。
**Why**: git 提交邮箱会被 GitHub 关联到对应账号。身份错配 = 整个仓库的贡献被归属给陌生人（不是协作者，只是贡献显示错人），且协作者列表不会提示 — 只能靠 `git filter-branch --env-filter` 重写历史 + `git push --force` 修正，属于破坏性操作。
**Wrong**: 全局 git user.email 缺失/从旧项目复制 config；提交后才发现贡献者列表出现陌生人头像
**Right**: commit 前 `git config user.email` 校验 = `226671264+BFRKQSB7@users.noreply.github.com`；push 后 `gh api repos/<owner>/<repo>/contributors` 确认无陌生账号
**检测**: `git log --all --format='%an <%ae>' | sort -u` 扫一遍所有提交身份，确认每个邮箱都归属本人账号
**防御**: 校验必须是**断言**（打印后逐字比对，`printf` 出来不等于通过）。`git config user.email` 可能被**仓库级 `--local` 配置覆盖**——先 `git config --local --get user.email`，再 `git config user.email`，两个都须等于 `226671264+BFRKQSB7@users.noreply.github.com`。备份/同步仓库的提交同样受此门禁约束。
**再次**: 2026-08-05×2 / 08-09 — 误用 `nyro@`、少 `226671264+` 前缀；已 5 仓 `filter-branch` 重写归一。凡 commit 必双查断言（`--local` + 全局），别用 `-c user.email` 简写。

---

## ★★★ 发布文件带本机个性化信息 → 用户名/盘符路径/端口泄漏 `rotatable` (since: 2026-08-15, last_hit: 2026-08-15)

**Rule**: 本机个性化信息**不进发布文件，也不进程序/网页的 UI 文案**：OS 用户名、绝对路径（`C:\Users\<用户名>\`、`/Users/<用户名>/`、**盘符路径 `E:\...`**）、本机代理端口、hostname、token、个人使用习惯（偏好端口/专属工具名/启动命令）。发布源只允许通用占位符（`~`、`%USERPROFILE%`、`<用户名>`、`Path.home()`）。
**Why**: 公开仓库任何人可见；用户名泄漏可被社工；硬编码路径使脚本在他机失效。
**检测**（发布门禁必跑，覆盖 .py/.md/.json/.spec/.jinja，排除 .git/build/dist）:
- 盘符/绝对路径：`grep -rInF ':\' --include='*.py' --include='*.md' .` —— 正则 `[A-Za-z]:\\` 结尾反斜杠报 **"Trailing backslash"**，改用**固定串 `grep -F ':\'`**；`<盘符>:\<软件目录>\` 这种无用户名盘符路径**也算泄漏**
- **正斜杠盘符/家目录实布局**（固定串 `:\` 抓不到）：`grep -rInE "D:/|C:/|~/Desktop" .` —— `D:/<python目录>/python.exe`、`~/Desktop/<工作目录>/` 均泄漏；**程序通用默认输出目录**（`Path.home()`/`~/Desktop/<应用输出目录>`，env 可覆盖、无用户名、非本机实路径）不算泄漏，勿误报
- 用户名：`grep -rIn "<OS用户名>" .` 零残留
- 代理端口：`grep -rInE "127\.0\.0\.1:[0-9]+|localhost:[0-9]+" .` 零残留
- **个人使用端口/LAN IP**（URL 正则漏网，`400[01]` 常裸写）：`grep -rInE "(^|[^0-9])400[01]([^0-9]|$)" .` + `grep -rInE "192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\." .`
- Release 正文同样扫（`gh release view <tag> --json body`），历史 release 也要清
**Wrong**: html-guide/kakuyomu `C:\Users\...`；llm-sight 帮助文本代理端口；LLM GUI tooltip 写「翻译 `<端口>`/转换 `<端口>`」使用习惯；llm-launcher-gui 维护清单 `<盘符>:\<软件目录>\LLMGUI.exe` 盘符路径（2026-08-15 门禁固定串扫抓到，泛化为「运行时目录」）
**再次**: 2026-08-08 html-guide/kakuyomu / 2026-08-10 llm-sight / 2026-08-12 LLM GUI tooltip / 2026-08-15 llm-launcher-gui 盘符路径
