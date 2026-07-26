# Skill Review Checklist

> 来源: Matt Pocock `write-a-skill` 审查清单，适配后用于 `/improve` 工作流

## 强制闸门

### Skill 质量
- [ ] **Description 含触发器**: `"Use when [specific triggers]"` — 第一句功能，第二句触发词
- [ ] **SKILL.md ≤ 100 行**: 超出则拆分到 `references/`，链接一层深
- [ ] **无时间敏感信息**: 日期、版本号、价格等动态数据放外部文件
- [ ] **术语一致 + 受控词汇表**: 每个 skill 定义 3-5 个核心术语；明确标记废弃词
- [ ] **有具体示例**: 每个工作流至少一个 "Good vs Bad" 或代码示例
- [ ] **引用一层深**: 不链式引用（A→B→C），只 A→B

### 三轴路由（Phase 1）
- [ ] **Critical 常加载**: `lessons-critical.md` 已读（5条 ★★★，~80行）
- [ ] **路由表**: `lessons-learned.md` 路由已匹配 → 文件清单已确定（纯路由 ~65行，不是全读）
- [ ] **Language 已检测**: 扫描了项目文件扩展名？对应 `lang/` 文件已加载？
- [ ] **Pattern 已检测**: 从任务/代码中识别了模式关键词？对应 `patterns/` 文件已加载？（含 null / security）
- [ ] **Domain 已匹配**: 任务关键词匹配了 domain 文件？
- [ ] **Security 自检**: 涉及认证/加密/输入/反序列化/依赖？→ `lessons-security.md` 已加载
- [ ] **浏览层**: 不确定某轴内容时才读 `INDEX.md`（~25行），不是盲目全读

### 发布（Phase 2）
- [ ] **包管理器已检测**: 确认了 `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / `.claude-plugin/`？
- [ ] **门禁通过**: grep 旧版本号零残留 + git push 后 GitHub 页面版本号正确
- [ ] **模板统一**: RELEASE 和 README 用对应语言模板

### 反省归档（Phase 3）
- [ ] **三轴归档**: 新教训按语言/模式/领域正确归类？
- [ ] **优先级维护**: 命中次数已更新？★★★ 已入 critical？rotatable 超 30 天已降级？

## Description 反例

```yaml
# ❌ 模糊 — agent 无法判断何时加载
description: Helps with code development.

# ✅ 精确 — agent 能根据触发词路由
description: >
  Code development workflow with active learning. Use when writing
  code, implementing features, fixing bugs, or user mentions
  "写代码" "开发" "编程" "plugin" "skill" "发布".
```

## 何时加脚本

- 操作是**确定性的**（验证、格式化、检查）
- 同一代码会被**反复生成**（省 token）
- 错误处理需要**显式控制**

## 何时拆分文件

- SKILL.md 超 100 行 → 拆内容到 `references/`
- 新语言 → `references/lang/lessons-<lang>.md` + 更新 `lang/INDEX.md`
- 新模式 → `references/patterns/lessons-pattern-<pat>.md` + 更新 `patterns/INDEX.md`
- 不同领域 → `references/lessons-<domain>.md` + 更新 `references/INDEX.md`
- 高级功能很少使用 → 独立文件按需加载
- 路由表保持纯索引：`lessons-learned.md` 只含路由条件，不含教训摘要
- 每个子目录有 `INDEX.md`：1行描述 + 教训数 + 交叉索引
