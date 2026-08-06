# Skill / Plugin Design & Workflow

> 加载条件: 任务涉及 skill, plugin, design, naming, description, workflow, learning, 技能, 插件, 设计, 发布

---

## ★ [2026-08-05] 手动解压插件未注册 → /plugin 斜杠命令全部不可用 (置信度: high, 命中: 1)

**Rule**: 手动解压到 `~/.claude/plugins/<name>/` 的插件，只配置 `statusLine` 只能显示 HUD，**斜杠命令（`/plugin:<cmd>`）不会出现**——命令只有把插件注册进插件系统才生效。`installed_plugins.json` 为空 = 幽灵安装。
**Wrong**: `statusLine.command` 直接指向 `node ~/.claude/plugins/balance-hud/dist/index.js`，HUD 正常但 `/balance-hud:configure` 等"用不了"。
**Right**: 注册本地插件（路径**必须正斜杠**，反斜杠会被 CLI 当 marketplace 名解析 → 报 `Marketplace "...not found"`）:
```
/plugin marketplace add C:/Users/NYRO/.claude/plugins/balance-hud
/plugin install balance-hud
```
然后完全重启 Claude Code。安装会复制到 `~/.claude/plugins/cache/` 并从副本注册命令；**不**动 `statusLine`。之后**不要**再跑 `/balance-hud:setup`（会重写 statusLine.command）。判断已注册：`installed_plugins.json` 含该插件条目。
**Why**: `/plugin install <目录路径>` 不接受路径——参数被当 marketplace 名解析。本地插件必须先以 marketplace 形式 `add` 再 `install`。

---

## ★ [2026-08-01] 修改 improve skill 后未同步 GitHub 备份 → 备份过期 (置信度: high, 命中: 1)

**Rule**: 任何修改 improve skill 文件（SKILL.md / lessons / INDEX / 删文件）后，Phase 3 反省时把改动同步到 GitHub 备份 repo `BFRKQSB7/claude-code-skills` 的 `improve/` 并 push
**Why**: 备份 repo 是 `~/.claude/skills/` 的 self-use 备份。不同步则多会话后备份严重过期（本会话发现备份仍含已删除的 `agent-brief.md` / `handoff.md` / `references/lessons-learned.md`）
**Right**: 同步流程（备份 clone 在 `C:/Users/NYRO/claude-code-skills`，已设本地代理 7896）:
```bash
cd C:/Users/NYRO/claude-code-skills && git pull
rsync -a --delete "C:/Users/NYRO/.claude/skills/improve/" improve/
git add -A && git commit -m "sync: improve <改动摘要>" && git push
```
**检测**: 修改后 `git -C C:/Users/NYRO/claude-code-skills status --short improve/` 无输出 = 已同步
**泛化**: 任何"自修改型"skill（会更新自身教训文件）都要内置备份步骤，否则知识库与备份分叉。

---

## ★★★ [2026-06-16] 发布流程手动重复 → 遗漏步骤 (置信度: high, 命中: 3)

> **→ 常加载** `[lessons-critical.md](lessons-critical.md)` 含完整 Rule / Wrong / Right / 再次记录

---

## ★★ [2026-07-26] 发布前未检查现有 Release 格式 → 版本号/标题不一致 (置信度: high, 命中: 1)

**Rule**: 创建新 Release 前必须 `gh release list` 查看现有格式（版本号风格、标题结构、正文模板），严格对齐后再创建
**Wrong**: 直接 `gh release create v2026.07.26 --title "LAN IP..."` — 日期格式版本号 vs 已有 v1.0.0 semver，标题不含 "ACGN Translation Guide" 前缀 → 用户指出格式不统一
**Right**: 
1. `gh release list` → 看到 `v1.0.0 — ACGN Translation Guide 首次发布`
2. 提取模板：版本号 `v<MAJOR>.<MINOR>.<PATCH>`，标题 `vX.Y.Z — ACGN Translation Guide <描述>`，正文 `# vX.Y.Z — <描述>` + 中文分段
3. 严格套用 → `v1.1.0 — ACGN Translation Guide LAN IP 自动检测 & API 显示统一`
**Why**: 追加内容不匹配现有格式 = 看起来像两个不相关项目。Release 页面是用户对项目的"第一眼版本履历"——格式跳跃 = 信任度下降。操作前不读现状 = 闭眼写代码。
**防御**: Phase 2 发布流程增加门禁步骤：
- [ ] `gh release list` 检查现有 Release 格式（版本号、标题、正文模板）
- [ ] 新 Release 的 tag/title/body 是否严格套用现有模板？
- [ ] 创建后 `gh release view <new>` 与最新旧版对比确认格式一致

**再次**: 2026-07-26 — acgn-translation-guide v1.1.0 首次用 `v2026.07.26` 日期 tag，用户指出与 v1.0.0 格式不一致 → 删旧 tag 重建

---

## ★ [2026-06-21] gh release create --notes 含特殊字符 → bash 吃掉 (置信度: high, 命中: 1)

**Rule**: `gh release create --notes "...inline..."` 中的反引号、`&`、`/dev/null` 等被 bash 解释 → Release body 截断/空白
**Wrong**: `gh release create v1.1.3 --notes "移除 bash -c 和 /dev/null，改用 async: true"` → backticks 触发命令替换，`&` 触发后台，Release body 乱七八糟
**Right**: `echo "..." > /tmp/notes.md` → `gh release create --notes-file /tmp/notes.md` 或用 `gh release edit --notes-file` 修复
**Why**: `--notes` 参数值是 shell 字符串，所有 shell 元字符（`` ` `` `$` `&` `(` `)` `|`）都会被解释。`--notes-file` 从文件读入，不走 shell 解释。
**再次**: 2026-06-21 — balance-hud v1.1.3 Release 首次创建时 body 被吃，用 `gh release edit --notes-file` 修复

---

## ★ [2026-06-16] 发布流程缺 repo 元数据 → 可发现性差 (置信度: medium, 命中: 1)

**Rule**: GitHub Release 发布后必须检查 repo topics + description + website
**Wrong**: Release 上传完毕即宣称完成 → repo 无 `claude` `claude-code` 等 topic → 搜索不可见
**Right**: `gh repo edit --add-topic "claude" --add-topic "claude-code" ...` 作为发布最后一步
**Why**: Topics 是 GitHub 搜索的主要索引。无 topic = 目标用户找不到。description 也影响搜索引擎摘要。

---

## ★ [2026-06-16] 模板推出后旧数据未回溯 → 格式腐烂 (置信度: medium, 命中: 1)

**Rule**: 引入统一模板/格式规范后，必须回溯修复所有存量数据
**Wrong**: 创建了 release-template.md 和 readme-template.md，但 v1.0.0 Release Notes 仍含 `你的仓库地址` 占位符，v1.1.0 格式混乱
**Right**: 模板创建后 → `gh release list` 遍历全部 Release → 逐个按模板重写 → 全部统一
**Why**: 模板只约束新建 = 存量腐烂继续扩散。用户看到的 Release 页面新旧格式混杂，信任度下降。

---

## ★ [2026-06-16] 技能指令名与官方冲突 → 补全困难 (置信度: medium, 命中: 1)

**泛化**: 命名前检查官方命令空间。`/plugin-dev` 与官方 plugin 管理命令前缀重叠 → 改名 `/improve`
**核心**: Tab 补全体验 = 命名空间设计。选独特的动词做前缀（improve / refine / craft）。

---

## ★ [2026-06-16] 技能默认进发布流程 → 用户无控制权 (置信度: medium, 命中: 1)

**泛化**: 裸触发指令应先询问而非默认执行。操作越危险（发布/删除/覆盖），越需要确认。
**核心**: 裸指令 = 菜单，子命令 = 执行。

---

## ★ [2026-06-16] 每次从零造轮子 → 忽略社区成熟方案 (置信度: medium, 命中: 1)

**Rule**: 做新功能前先搜 GitHub/web 有无现成方案
**Wrong**: 想都不想就直接写代码 → 踩的坑社区早踩过、早修好
**Right**: Phase 0 — 搜索 awesome-lists、官方 skills、高星 repo → 理解 → 适配 → 整合
**Why**: Claude Code 生态已成熟，1044+ skills、11989+ plugins 存在。别人踩过的坑、固化的工作流，直接搬来用比从零写更快且更稳。
**泛化**: 任何成熟生态（npm/pip/cargo/marketplace）都适用。先搜后写，先搬后改。

---

## ★ [2026-06-16] 教训平铺无优先级 → 慢性顽疾被淹没 (置信度: medium, 命中: 1)

**Rule**: 教训需要编码优先级，重复犯的必须升级
**Wrong**: 10 条教训平铺，第 9 条犯了 2 次但和第 1 条（犯 1 次）权重一样
**Right**: ★★★ 系统：1 次=★, 2 次=★★+Rule化, ≥3 次=★★★+Phase 1 高亮警告
**泛化**: 任何知识库都需要新鲜度/频率加权。30 天未命中 → 休眠，命中 → 恢复+升级。

---

## ★ [2026-06-16] SKILL.md 超 100 行未拆分 → 上下文膨胀 (置信度: high, 命中: 1)

**Rule**: SKILL.md ≤ 100 行。超出 → 拆到 `references/`。引用一层深。
**Wrong**: 162 行单文件塞满工作流+清单+命令参考+格式指南 → agent 每次加载全部内容
**Right**: 79 行核心工作流 + `references/` 按需加载
**Why**: Progressive disclosure 是 AI 技能的标准架构。SKILL.md 只写 agent 每次必读的内容。
**来源**: Matt Pocock `write-a-skill` 6-item checklist
**泛化**: 适用于任何 AI agent 技能的文档设计。类似 Web 开发的 code splitting。

---

## ★ [2026-06-16] Description 写给人看 → agent 路由失败 (置信度: medium, 命中: 1)

**Rule**: `description` 字段写给模型路由器，不写给人。必须含 "Use when [specific triggers]"
**Wrong**: `description: Helps with plugin development.` — agent 无法判断何时加载
**Right**: `description: Plugin/skill dev workflow... Use when working with plugins, hooks, skills...`
**Why**: description 是 agent 选择加载哪个 skill 的**唯一信号**。模糊 = 永远不会被触发。
**泛化**: 所有 AI agent skill/plugin 的 description 都是路由信号，不是人类摘要。

---

## ★ [2026-06-16] 学习外部技能只研究不整合 → 知识蒸发 (置信度: medium, 命中: 1)

**Rule**: `/improve learn` 的输出必须是文件变更，不能只是对话中的文字
**Wrong**: 研究了外部技能体系，在对话里总结要点，下次对话上下文清空就没了
**Right**: 提取 → 创建/更新文件 + 归档教训 + 输出报告
**泛化**: 任何"学习"行为的结果必须持久化到文件系统。对话是 volatile，文件是 durable。

---

## ★ [2026-06-16] 技能平铺无组织结构 → 查找困难 (置信度: medium, 命中: 1)

**Rule**: 技能用 bucket 分桶组织，每桶有 README 列出所有技能
**Wrong**: 20+ skills 平铺在一个目录 → 不知道哪个是日常用、哪个是实验、哪个已废弃
**Right**: `engineering/` `productivity/` `misc/` `personal/` `in-progress/` `deprecated/` 各一个 README
**Why**: 分桶 = 隐式文档。用户看到 `deprecated/` 就知道不要用，看到 `in-progress/` 就知道不稳定。
**来源**: Matt Pocock `CLAUDE.md` bucket system
**泛化**: 任何超过 10 个文件的目录都需要组织结构。文件夹名 = 元数据，README = 索引。

---

## ★ [2026-06-16] 术语不统一 → agent 和用户各说各话 (置信度: medium, 命中: 1)

**Rule**: 每个 skill 定义 3-5 个核心术语 + 标记废弃词
**Wrong**: 同一个概念在 skill 里叫 "插件"、README 里叫 "plugin"、代码里叫 "addon"
**Right**: `CONTEXT.md` 定义 "Issue tracker" = 托管 issue 的工具；明确标记 "backlog" 为废弃词 → 所有 skill 统一
**来源**: Matt Pocock `CONTEXT.md` controlled vocabulary
**泛化**: 文档和代码的一致性从术语开始。术语不统一 = agent 理解漂移 = 输出质量下降。

---

## ★ [2026-06-16] AI 代码生成水平切片 → 垃圾测试 (置信度: high, 命中: 1)

**Rule**: 代码生成必须垂直切片（test1→impl1→test2→impl2），禁止水平切片
**Wrong**: RED 阶段写完全部 5 个测试 → GREEN 阶段写完全部 5 个实现
**Right**: 逐对推进 — 一个 test → 一个 impl → 验证 → 下一个 test
**Why**: 批量写的测试基于**想象**行为而非**实际**行为。重构时假阳/假阴。你跑过头灯——在理解实现前就锁死了测试结构。
**来源**: Matt Pocock `tdd`
**泛化**: 适用任何 AI agent 代码生成。垂直 = 每个 cycle 学习。水平 = 猜测 × N。

---

## ★★ [2026-06-16] 教训不定期审查 → 重复犯错未被发现 (置信度: high, 命中: 2)

**Rule**: 每 3-5 次 `/improve reflect` 后做一次跨 domain 审查 — 扫描所有 ★★/★★★ 条目，找同根因可合并项
**Wrong**: 四条 cleanup 教训同根（变更未 grep）但分散在独立条目中 → 看起来像四个独立问题 → 每个都"只犯了一次" → 不升级 → 继续犯
**Right**: 审查时做"根因聚类"：把所有教训按根因分组 → 同根合并 + 累加命中次数 → 升级优先级
**Why**: 分散的教训掩盖真正的重复频率。四条各命中 1 次 = 同根因命中 4 次 = ★★★ 系统性问题。
**泛化**: 适用于 bug tracker、postmortem、OKR 回顾 — 聚类比计数重要。
**再次**: 2026-06-16 — 用户指出"上述问题不应该重复出现"，审查发现 cleanup 四条同根、发布遗漏实际命中 ≥2

---

## ★★ [2026-07-05] 修改→发布循环未批量化 → Release 反复重建 (置信度: high, 命中: 2)

**Rule**: 发布前批量完成**所有**文本/元数据修改（README、LICENSE、NOTICE、描述），最后一次打包上传。禁止"commit→push→release→发现问题→修改→再来一遍"的循环
**Wrong**: 本次会话重复 3 次完整 release 流程（改 README 属→tag→zip→upload，改安装脚本→tag→zip→upload...）→ 每次 5 步，浪费 15+ 次操作
**Right**: `git log --oneline HEAD...v2.0.0` 检查未发布 commits → 逐条 review → 确认所有修改完成 → **一次** tag + zip + upload
**Why**: GitHub Release 不是 CI/CD pipeline。每次改 zip 内容需要删旧 asset + 重新上传 + 更新 release notes → 3 步每步可能网络失败。批量发版 = 减少失败点。
**防御**: 发布前 checklist 增加"所有文本修改已完成？"条目。未完成 → 不进入打包阶段。

## ★★ [2026-08-06] 发布 skill 用错来源副本 → 把旧版当新版发布 (置信度: high, 命中: 2)

**Rule**: 发布 skill 前，先 `diff -rq <实际加载的 skill 目录> <发布仓库>` 核对两者是否分叉，**以当前加载的目录为准**，不要默认拿桌面/历史副本当发布源。
**Wrong**: `~/.claude/skills/html-guide`（加载源，含全部新改动）与桌面 `html-guide-skill` 仓库（v1.0 旧副本）各自独立。若直接基于旧副本改发布，会把旧版内容推上去，用户的"新改动"丢失。
**Right**: 发布前 diff 两份 → 明确以加载目录为源 → 把过时副本删掉或标记 deprecated，避免双源长期分叉。
**Why**: skill 安装目录与发布仓库很容易分叉（本会话桌面副本停留在 v1.0，加载目录已是 v2.0）。用错源 = 线上 SKILL.md/README 落后于实际功能。
**检测**: 发布前 `diff -rq` 源目录与 repo，有差异先确认改动方向再发布。

---

## ★ [2026-08-06] 插件发布 zip 用 `git archive` 构建 → 免手动打包错误 (置信度: high, 命中: 1)

**Rule**: 发布 Claude Code 插件/skill 的 zip 用 `git archive --format=zip --prefix=balance-hud/ -o out.zip HEAD`，禁止手动挑文件打包。
**Wrong**: 手动 zip（拖文件/`zip -r` 挑目录）→ 可能混入运行时残留（`balance_usage.json`/`session_state.json`/`config-cache/`/`.bak`）或漏文件，每次发布结构不一致。
**Right**: `git archive` 只含 git 跟踪文件，天然排除运行时垃圾与 `.git`。打包后两道门禁：① `diff <(git ls-files | sort) <(unzip -l zip | 文件清单 | sort)` 零差异（注意过滤目录条目与 header 行）② grep zip 内 `balance_usage|session_state|config-cache|.bak` 零命中。
**Why**: v2.2.1 手动 zip 236 文件，v2.2.2 用 git archive 237 文件——结构由 git 保证可复现，发布只关注"内容对不对"而非"漏没漏"。
**检测**: 发布 zip 后 `unzip -l` 对照 `git ls-files` 与运行时文件黑名单。


---

## ★ [2026-07-05] 衍生项目 README 描述沿用上游 → 与实现不符 (置信度: medium, 命中: 1)

**Rule**: 从上游 fork/adapt 的项目，**所有**用户可见文本（README、help、错误消息）必须 review 是否与当前实现一致
**Wrong**: README 写"方式二：使用安装脚本"但 `/balance-hud:setup` 是 Claude Code 斜杠命令，不是独立 `.sh`/`.bat` 文件 → 用户指出"2.0 并没有安装脚本"
**Right**: 每个用户可见描述对照实际功能验证。斜杠命令 → 称为"交互式设置命令"而非"安装脚本"。setup.md 步骤 → 称为"设置向导"而非"脚本"
**Why**: 衍生项目最容易被忽视的不是代码，而是文档。代码会报错 → 文档不会。术语不准确 = 用户找不到功能 = 以为缺失。
**检测**: grep README/commands 中的"脚本""script""CLI""二进制"等词 → 逐条验证是否确实存在

---

## ★ [2026-06-16] Agent Brief 写文件路径和行号 → 过时无效 (置信度: medium, 命中: 1)

**Rule**: Agent Brief 描述接口/类型/行为契约，不写文件路径/行号
**Wrong**: "Open src/types/skill.ts, add a schedule field on line 42"
**Right**: "The `SkillConfig` type should accept an optional `schedule` field of type `CronExpression`"
**Why**: issue 可能等数天才被 agent 拾取。文件路径/行号随时过时。接口/类型名变更慢得多。
**来源**: Matt Pocock `triage` Agent Brief template
**泛化**: 任何"给未来 agent 的指令"都用耐久性描述。行为契约 > 实现细节。

---

## ★ [2026-07-07] README 多语言切换 — 零依赖纯 Markdown 方案 (置信度: high, 命中: 1)

**来源**: GPT-SoVITS 仓库（RVC-Boss/GPT-SoVITS）— `docs/cn/README.md` 语言切换条
**泛化**: 任意多语言开源项目的 README 设计。零 JS、零 CI、纯 Markdown 相对路径。

**目录结构**:
```
README.md              ← 默认语言（GitHub 自动渲染）
docs/
  cn/README.md         ← 翻译版本
  ja/README.md
  ko/README.md
```

**语言切换条**（每个 README 顶部，标题正下方）:
```markdown
**English** | [**中文简体**](./docs/cn/README.md) | [**日本語**](./docs/ja/README.md)
```

**五条规则**:
1. 当前语言 → **加粗** + 去掉链接（既是标识也是导航状态）
2. 其他语言 → **[加粗链接](相对路径)**
3. 语言名用该语言自称 — `한국어` 不写 `Korean`，`中文简体` 不写 `Chinese Simplified`
4. 默认语言放仓库根目录 — GitHub 自动展示，SEO 最佳
5. 全部用相对路径 — fork/branch/tag 都不会断

**Wrong**: 用 JS 检测浏览器语言跳转、用 `<select>` 下拉框、用 CI 生成不同语言页面 → 增加构建复杂度，GitHub README 不可用
**Right**: 一行 Markdown 语言条，每个翻译版本改一个词（哪个加粗去链接），其他完全一样
**Why**: GitHub README 是静态 Markdown，不支持 JS。任何需要构建/JS 的方案在 GitHub 上不可用。纯 Markdown 相对路径 = 所有 Git 平台通用（GitHub/GitLab/Gitee）。

---

## ★★ [2026-07-10] 部署指南面向技术人员 → 小白完全看不懂 (置信度: high, 命中: 1)

**Rule**: 部署/安装指南的目标读者是**不知道这个工具是什么的人**，而不是已经会的人。每个步骤必须回答四个问题：是什么？为什么？怎么做？在哪里点？
**Wrong**: "从 llama.cpp Releases 下载最新版 llama-server.exe（Windows）。推荐下载文件名含 cuda 的版本。" → 小白不知道 llama.cpp 是什么、Releases 页面几十个文件该点哪个、cuda 版本和自己的电脑什么关系、解压后一堆文件该取哪个
**Right**: 分四步——
1. **前置检查**（为什么需要这一步）：先教用户用 `nvidia-smi` 查 CUDA 版本，解释这个数字和下载文件的关系
2. **打开页面**（在哪里）：给完整 URL + "点击最新的那个版本"
3. **选对文件**（选哪个）：用表格列出"你的显卡 → 找这个名字的文件"，另列表"不要选的文件"
4. **解压取用**（取哪个文件）：明确说"解压后只需要 llama-server.exe 这一个文件"
**四个问题模板**:
- **是什么**: 一句话解释这个工具/概念
- **为什么**: 为什么需要做这一步？不做的后果？
- **怎么做**: 分步指令，每步一句话，不跳步骤
- **在哪里点**: 用 `→` 箭头描述 UI 路径（如 `右键点击 zip 文件 → "全部解压缩"`）
**小白提示 (callout)**: 每节能用 `> 📝 **小白提示**：` 的地方都要加，用"你只需要……""不要慌"等降低焦虑的话术
**Why**: 技术人员写文档默认读者和自己水平相当 → 跳过大量"显而易见"的步骤 → 真正的目标读者（刚入门的用户）每一步都会卡住。部署指南的受众不是模型作者，是想要用模型翻译轻小说的普通 ACGN 爱好者。
**防御**: 写完部署指南后问自己：一个只会双击 exe 安装软件的人，能独立完成前 3 步吗？
**再次**: 2026-07-10 — 用户指出 llama.cpp 下载表里写了 CUDA 11 版本但实际 Release 页只有 CUDA 12 + CUDA 13，50 系显卡是 13.x。教训：**写下载指南前必须打开 Release 页面核对实际文件名**，不能凭记忆编造。Release 页面的文件清单会随版本更新变化，不要假设"CUDA 11 肯定还在"。
**再次**: 2026-07-10 — 用户指出每个 CUDA 版本有**两个** zip 文件（主程序 + `cudart-llama-...` DLLs），不是"选一个就行"。只下载主程序 → 缺 `cudart64_*.dll` → 启动失败。教训：**核对 Release 页面时必须看清每个条目的完整描述**，标注"companion file"或同类文件不是可选的，是必下载。
**再次**: 2026-07-10 — 用户指出部署指南结构问题：① 命令行墙（§4 一大坨 CLI 参数）放在模型下载之前，小白还没下载模型就被吓退；② 400+ 行源码放在正文 §6，小白以为必须读完才能用。修正：插入 §2"快速上手"用三步搞定；CLI 参数移到 §5 并标注"进阶可选"；源码移到附录A。教训：**简单路径必须排在最前面**，进阶内容往后放+标注可选。小白看到第一步是"双击 bat 文件→搞定"才不会跑。
**再次**: 2026-07-10 — 用户指出三个小白必知规则：① 不能改模型文件名（脚本精确匹配）② 不需要下载全部模型（菜单多≠都要下）③ 模型不在菜单里→改脚本或问 AI。教训：**部署指南必须预判小白会犯的错**，这些对技术人员"显而易见"的规则对小白来说完全是新知。Rule 补充：提供可直接下载的脚本文件比让用户复制粘贴 400 行代码友好得多。


---

## #agent-指令 — 给桌面环境代理写指令

### ★★ 指令让代理"打开浏览器验证" → 桌面弹窗轰炸 (置信度: high, 命中: 1)

**Rule**: 运行在用户真实桌面会话里的代理/子代理，指令**禁止**写"打开浏览器/预览验证"——`webbrowser.open`/`os.startfile`/`start`/预览服务都会在用户屏幕上弹窗。
**Wrong**: SKILL.md Step 5 写"用浏览器打开该文件检查……" → 12 个评测子代理各自弹浏览器空白页，用户两次被骚扰（"怎么一直给我打开浏览器空白页"）。
**Right**: 桌面环境的视觉验证一律走 **headless**（`chrome --headless=new --dump-dom` / `--screenshot`），或让用户自行打开文件。指令里显式写"禁止打开任何浏览器窗口"。
**Why**: 后台代理会照字面执行指令。用户桌面是共享可视资源，"验证"这个无害意图会被放大成持续弹窗。
**Fix**: 改指令措辞 + SKILL.md 内置"严禁自动弹浏览器"硬规则。

### ★★ 评测断言只 grep 源码类名 → 假阳性，坏功能连过 2 轮 (置信度: high, 命中: 1)

**Rule**: 评测/校验断言若检查"源码里含某类名"，而功能是**运行时 JS** 生成的，断言会假阳性——CSS/JS 定义里就有该类名字符串。
**Wrong**: 断言 `"tok-" in 源码` 通过，但代码高亮是 JS 运行时渲染的；实际 12 个代码块 0 高亮，断言仍全过 → 用户连续两轮反馈"无语法高亮"才暴露。
**Right**: 运行时功能（高亮/目录/复制/Tab）必须用 headless 渲染后验证真实 DOM（`grep 'class="tok-'` 数渲染后的 span），不能只查源码。
**Why**: 人眼看不到"断言查错了对象"。假阳性的校验比没有校验更危险——它给你虚假安全感，让坏功能在评测里畅通无阻。

## #eval-循环 — 评测迭代成本

### ★ 基线价值确立后仍每轮全跑 12 代理 → 浪费 (置信度: medium, 命中: 1)

**Rule**: 迭代评测时，一旦基线（without_skill）的价值已确立，后续迭代只跑 with_skill 即可，省一半耗时与 token。
**Wrong**: 迭代 1-3 每轮都 12 代理（6 带 skill + 6 基线），每轮 ~10 分钟；迭代 4 改为只跑 6 个 with_skill 才省时。
**Right**: 首次对比用完整基线；后续迭代只验 with_skill，基线对比隔几轮抽查一次即可。

## #html-guide — 单文件页面生成

### ★ [2026-08-05] 已交付页追加组件只加标记 → 组件静默无样式 (置信度: high, 命中: 1)

**Rule**: 往已生成的单文件页面追加新组件（骨架新加的 `.barchart` / `.donut` 等）时，**必须把骨架最新的 `<style>`（必要时 `<script>`）同步进页面**——页面的内联 CSS 是生成时从旧骨架复制的快照，不会自动带上后来新增的组件样式。
**Wrong**: LLM 横评页加了 `.barchart` 标记（`--v` 内联样式），但页面 `<style>` 仍是旧快照，缺 `.bc-track` / `.bc-fill` 规则 → 用户打开网页看不到柱状条，只剩一串模型名和数字。
**Right**: 追加组件后先 `grep "组件类名" 页面.html`——标记和 CSS 两处都要有；CSS 缺失就把当前骨架的 `<style>` 整体替换进页面（正文 class 不变，`<script>` 一致则不动）。交付前无头渲染验证计算宽度（`getBoundingClientRect().width` 与 `--v` 成比例）。
**Why**: 单文件页面的样式是嵌入快照，与 skill 骨架独立演进。追加组件时人眼盯标记、漏看样式表是否含对应 CSS → 组件静默失效，纯文本浏览根本看不出来。
**检测**: 组件类名（如 `.bc-track` / `.donut`）在页面里应同时出现在标记与 CSS 两处。

---

### ★★ [2026-08-05] skill 发布仓库 README 独立维护 → 改 skill 不同步 README (置信度: high, 命中: 2)

**Rule**: skill 发布仓库的 `README.md` **只在 repo 里维护**（不在 `~/.claude/skills/<skill>/` 加载目录里）。发布流程「copy 加载目录 → repo」**不会带 README**——每次改 skill 后要单独检查/同步 README，否则 README 停在旧描述。
**Wrong**: v2.0.4 把代理端口解耦到 user-config.md，只改了 search-guide.md / SKILL.md；README 目录结构注释仍写 `curl -x 127.0.0.1:7896`。用户看到 GitHub README 还有 7896 才暴露。
**Right**:
1. 发布 skill 时，克隆仓库后先 `grep -rn "旧端口/旧功能名" README.md` 检查 README 是否需同步
2. README 最容易过期的三处：**功能表 / 目录结构 / 安装说明**
3. 判断 README 是否在加载目录：`ls ~/.claude/skills/<skill>/README.md` 不存在 = 仓库独有
**Why**: 发布源（加载目录）与仓库内容分叉，README 只在仓库侧、且发布流程不覆盖它 → 单点过期。
**检测**: 发布后 `grep "旧值" README.md` → 0 残留；README 不在加载目录 = 记得单独看 repo 侧。
