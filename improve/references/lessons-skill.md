# Skill / Plugin Design & Workflow

> 加载条件: 任务涉及 skill, plugin, design, naming, description, workflow, learning, 技能, 插件, 设计, 发布

---

## ★★★ [2026-06-16] 发布流程手动重复 → 遗漏步骤 (置信度: high, 命中: 3)

> **→ 常加载** `[lessons-critical.md](lessons-critical.md)` 含完整 Rule / Wrong / Right / 再次记录

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
