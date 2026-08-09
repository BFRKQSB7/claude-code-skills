---
name: improve
description: >
  Code development workflow with active learning and self-improvement.
  Reads past mistakes before work, searches GitHub/web for mature solutions
  (don't reinvent), auto-detects language + code patterns for targeted
  reflection, auto-reflects after. Covers 100+ production-proven bug patterns
  (null safety, async leaks, security vulns, Go/goroutine pitfalls, Python
  pickle RCE, JS prototype pollution). Use when writing code, implementing
  features, fixing bugs, developing plugins/skills, publishing releases,
  or user mentions "写代码" "实现" "开发" "编程" "code" "implement"
  "develop" "fix" "build" "plugin" "skill" "发布" "打包" "improve"
  "best practice" "反省" "安全" "security" "null" "空指针" ".bat"
  ".cmd" "批处理" "batch file" "UTF-8" "encoding" "编码" "乱码"
  "launcher" "启动器" "启动脚本" "llama-server" "cmd.exe"
  "部署指南" "教程" "小白" "教学" "CUDA" "nvidia-smi"
  "crlf" "lf" "line ending" "换行" "伪ASCII".
user-invocable: true
---

# Improve — 主动学习 + 避坑 + 反省

## 内容规范（强制 — 所有写入本 skill 的内容按此格式）

> 目标：精简有效省 token。每条 ≤8 行；一次写入，只更新日期/命中/优先级。

**再犯的坑 → Rule**：`## ★★ [YYYY-MM-DD] 标题 (置信度, 命中: N)` 下挂 `**Rule**` `**Wrong**` `**Right**` `**Why**`（各 ≤1 行）
**设计决策 → 泛化**：`## ★ [YYYY-MM-DD] 标题 (命中: N)` 下挂 `**泛化**`（≤1 行）`**核心**`（一句话）
**调试 → Hypothesis**：`**Hypothesis**: If <X> 是根因, 则改 <Y> bug 消失` + `**Test**` + `**Result**: confirmed|ruled out`

**通用约定**：
- 标题=现象非空话；字段 ≤1 行；Caveman 禁填充词；命中 1/2/≥3 → ★/★★/★★★，★★★ 归 critical 常加载
- 分类词固定：`新增 修复 删除 优化 版本`（RELEASE/README 变更日志用）
- 路由：语言→`lang/`，模式→`patterns/`，领域→`references/lessons-*.md`；改教训 → 同步 INDEX.md 教训数
- 同根因合并 `(再次: YYYY-MM-DD)` + 升优先级；30 天未命中 → Dormant；引用一层深

## 三不原则
1. **不重复发明** — Phase 0 先搜现成方案，能搬就搬
2. **不跳步骤** — Phase 0→1→2→3 缺一不可
3. **不犯旧错** — 开工前按三轴加载教训：Domain × Language × Pattern

## 沟通模式
**默认 Caveman**：砍冠词/填充词/客套话，只留技术实质；代码和报错精确原文。
**例外（完整输出）**：Plan 阶段 / 用户提问后 / 安全警告 / 首次解释复杂概念。
> 来源: Matt Pocock `caveman` skill，省 ~75% token

## Workflow
`Phase 0 搜现成方案` → 有: 整合(跳 Phase 2) / 无: `Phase 1 三轴加载` → `Phase 2 执行` → `Phase 3 反省归档`

## Subcommands
| 输入 | 行为 |
|------|------|
| `/improve` | 询问：学习？创建？更新？发布？反省？ |
| `/improve learn <topic\|url>` | 搜 GitHub/web 最佳实践并吸收 |
| `/improve create <name>` | 创建项目骨架（语言检测 → 模板） |
| `/improve update` | 同步版本号 + grep 旧版本零残留 |
| `/improve publish` | 语言自适应发布（检测包管理器 → 打包 → GitHub） |
| `/improve reflect` | 手动反省 → 三轴归档 |

## Phase 0: 先找现成方案
搜 `anthropics/skills`(P0) → awesome-lists(P1) → 厂商 skills(P2) → 高星 repo(P3)。找到 → 提取 Gotchas/架构/工作流 → 整合。不确定 → 抛弃型原型验证。
详见: [checklist.md](references/checklist.md) [prototype.md](references/prototype.md)

## Phase 1: 三轴加载教训（渐进式，按需）
1. **常加载**: [lessons-critical.md](references/lessons-critical.md)（★★★ 无条件）
2. **路由**: [lessons-learned.md](lessons-learned.md) → 匹配关键词 → 文件清单
3. **按需加载**（2-4 个，总 ~2K tokens）:
   - Domain 轴: `references/lessons-<domain>.md`
   - Language 轴: `lang/lessons-<lang>.md`
   - Pattern 轴: `patterns/lessons-pattern-<pat>.md`
4. **浏览层**（不确定才读）: 对应 `INDEX.md`
5. **门禁**: 变更操作→[lessons-cleanup.md](references/lessons-cleanup.md) | 安全操作→[lessons-security.md](references/lessons-security.md)
6. 输出避坑清单；★★★ 防御措施 → Phase 2 强制门禁

## Phase 2: 执行
**发布（语言自适应）**: 检测包管理器 → 版本号同步 → **门禁** grep 旧版本零残留 → 打包 → RELEASE+README 模板 → git push → **门禁** 验证默认分支 + GitHub 版本号
**代码生成**: 垂直切片（test1→impl1→test2→impl2），禁水平切片
详见: [commands.md](references/commands.md)

## Phase 3: 反省归档
提炼（场景→现象→根因→修复→泛化）→ 按语言/模式/领域归档 → 合并同根因升优先级 / 30 天休眠 → **同步对应 INDEX.md 教训数**
**Critical 维护**: ★★★ → critical 常加载 → 30 天未命中降级 → 复入标记 `permanent`

## Review Checklist
- [ ] Phase 0: 搜过现成方案？有就搬
- [ ] Phase 1: 三轴已检测 + 避坑清单已出
- [ ] SKILL.md ≤ 100 行，引用一层深，新内容符合前置「内容规范」
- [ ] 发布: 语言自适应 + grep 零残留 + 提交身份断言（`226671264+BFRKQSB7@users.noreply.github.com`）
- [ ] Phase 3: 新教训按规范归档 + INDEX 教训数已更新
- [ ] 改过 skill → 已同步 `BFRKQSB7/claude-code-skills` 的 `improve/` 并 push
