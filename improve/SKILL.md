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

# Improve — 主动学习 + 避坑 + 反省（多语言通用）

## 三不原则

1. **不重复发明** — 先找现成方案（Phase 0），能搬就搬
2. **不跳步骤** — Phase 0→1→2→3 缺一不可
3. **不犯旧错** — 开工前按三轴加载教训：Domain × Language × Pattern

## 沟通模式

**默认 Caveman**：砍冠词/填充词/客套话，只留技术实质。代码块和错误信息精确原文。
**例外（完整输出）**：Plan 阶段 / 用户提问后回答 / 安全警告 / 首次解释复杂概念。
> 来源: Matt Pocock `caveman` skill，省 ~75% token

## Workflow State Machine

```
Phase 0: 搜现成方案 ──→ 有 → 理解→适配→整合 → 跳过 Phase 2
     │                    └─ 无 → Phase 1
     ↓
Phase 1: 三轴加载教训
         ├─ 轴1 Domain: 匹配任务关键词 → 加载 domain 文件
         ├─ 轴2 Language: 检测文件扩展名 → 加载 lang/lessons-<lang>.md
         └─ 轴3 Pattern: 检测代码模式 → 加载 patterns/lessons-pattern-<pat>.md
         → 输出避坑清单（交集，2-4 个文件 ~2K tokens）
     ↓
Phase 2: 执行（子命令见下）
     ↓
Phase 3: 反省 → 提炼教训 → 按三轴归档 → 合并/新增/休眠 → 更新优先级
```

## Subcommands

| 输入 | 行为 |
|------|------|
| `/improve` | 询问：学习？创建？更新？发布？反省？ |
| `/improve learn <topic\|url>` | 搜索 GitHub/web 最佳实践并吸收 |
| `/improve create <name>` | 创建项目骨架（检测语言 → 对应模板） |
| `/improve update` | 同步版本号 + 全局 grep 旧版本零残留 |
| `/improve publish` | 语言自适应发布（检测包管理器 → README → 打包 → GitHub） |
| `/improve reflect` | 手动反省 → 按三轴归类归档 |

## Phase 0: 先找现成方案

搜索: `anthropics/skills` (P0) → awesome-lists (P1) → 厂商 skills (P2) → 高星 repo (P3)
找到 → 提取 Gotchas/架构/工作流 → 整合。不确定时建抛弃型原型验证。

详见: [references/checklist.md](references/checklist.md) [references/prototype.md](references/prototype.md)

## Phase 1: 三轴加载教训（渐进式，按需读取）

1. **常加载**: [lessons-critical.md](references/lessons-critical.md)（★★★ 无条件，~80行）
2. **路由**: 读 [lessons-learned.md](lessons-learned.md)（纯路由表 ~70行）→ 匹配关键词 → 确定文件清单
3. **按需加载**（2-4个，每文件 ~30-80行，总 ~2K tokens）:
   - 轴1 Domain: 匹配任务关键词 → 加载 `lessons-<domain>.md`
   - 轴2 Language: 扫描扩展名 → 加载 `lang/lessons-<lang>.md`
   - 轴3 Pattern: 检测代码模式 → 加载 `patterns/lessons-pattern-<pat>.md`
4. **浏览层**（仅不确定内容时读，~25行/个）:
   [references/INDEX.md](references/INDEX.md) / [lang/INDEX.md](references/lang/INDEX.md) / [patterns/INDEX.md](references/patterns/INDEX.md)
5. **门禁自检**: 变更操作→[lessons-cleanup.md](references/lessons-cleanup.md) | 安全操作→[lessons-security.md](references/lessons-security.md)
6. 输出避坑清单。★★★ 防御措施 → Phase 2 强制门禁

## Phase 2: 执行

**发布（语言自适应）**: 检测项目类型 → `package.json`=npm / `pyproject.toml`=pip / `Cargo.toml`=cargo / `go.mod`=go / `.claude-plugin/`=zip
→ 版本号同步 → **门禁**: 全局 grep 旧版本号零残留 → 打包 → RELEASE+README 模板 → git push → **门禁**: 验证默认分支 + GitHub 版本号

**代码生成**: 垂直切片（test1→impl1→test2→impl2），禁止水平切片

详见: [references/commands.md](references/commands.md) [references/release-template.md](references/release-template.md)

## Phase 3: 反省（三轴归档）

提炼（场景→现象→根因→修复→泛化）→ 归档:
- 语言特有 → `lang/lessons-<lang>.md` 对应 Pattern 分组
- 跨语言通用 → `patterns/lessons-pattern-<pat>.md`
- 工程领域 → `references/lessons-<domain>.md`
- 合并同根因升优先级 / 30天未命中休眠
- **新增/删除/重命名教训后** → 更新对应 `INDEX.md` 的"教训数"和"重点领域"

**Critical 维护**: ★★★→critical → rotatable 30天未命中降级 → 复入标记 permanent
详见: [references/format-guide.md](references/format-guide.md)

## Review Checklist

- [ ] Phase 0: 搜过现成方案？有就搬
- [ ] Phase 1: 三轴已检测（Language + Pattern + Domain）+ 避坑清单已出
- [ ] SKILL.md ≤ 100 行，引用一层深，术语一致
- [ ] 发布: 包管理器已检测 → 语言自适应策略 → grep 旧版本号零残留
- [ ] Phase 3: 新教训按三轴归档 + 优先级已更新
