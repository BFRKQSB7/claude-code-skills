# Critical Lessons — Always Loaded

> ★★★ 系统性顽疾。Phase 1 无条件加载（~1KB），不依赖关键词路由。

## 轮换规则

| 状态 | 含义 | 行为 |
|------|------|------|
| `permanent` | 复入列表（≥2 次） | **永驻**，不轮换 |
| `rotatable` | 首次入列 | 30 天未命中 → 降级回 domain 文件 |
| `dormant` | 已降级 | 只在 domain 文件，再次命中 ★★★ → 升级 `permanent` |

**Phase 3 维护**: 扫描所有教训 → ★★★ 且不在 critical → 加入（`rotatable`）→ 检查 rotatable 条目最后命中日期 → 超 30 天降级 → 降级后复入的标记 `permanent`

---

## ★★★ 变更后未全局 grep → 引用断裂 `rotatable` (since: 2026-06-21, last_hit: 2026-06-21)

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

## ★★★ 发布流程手动重复 → 遗漏步骤 `rotatable` (since: 2026-06-21, last_hit: 2026-06-21)

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
