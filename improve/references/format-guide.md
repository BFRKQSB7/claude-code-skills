# 教训格式指南

## 三种格式

### 设计决策/架构 → 泛化格式

```markdown
## ★ [YYYY-MM-DD] 一句话标题 (置信度: high/medium/low, 命中: N)
**泛化**: 可迁移到其他项目的通用原则
**核心**: 一句话记住
```

### "会再犯"的坑 → Rule 格式

```markdown
## ★★ [YYYY-MM-DD] 一句话标题 (置信度: high, 命中: 2)
**Rule**: 做什么/不做什么
**Wrong**: 错误做法
**Right**: 正确做法
**Why**: 根因
**泛化**: 可迁移
```

### 调试/诊断 → 可证伪假设格式

```markdown
**Hypothesis**: If <X> is the cause, then <changing Y> makes the bug disappear.
**Test**: <具体测试方法>
**Result**: <confirmed / ruled out>
**Why**: <如果是根因，解释为什么>
```
> 来源: Matt Pocock `diagnose` skill — 每个假设必须可证伪；不可证伪 = vibe，丢弃。

## 优先级规则

| 命中次数 | 优先级 | 行为 |
|----------|--------|------|
| 1 | ★ | 正常记录 |
| 2 | ★★ | Rule 化（Wrong/Right/Why） |
| ≥3 | ★★★ | Phase 1 高亮警告 |

## INDEX.md 规范

每个子目录（`references/` `lang/` `patterns/`）维护一个 `INDEX.md`（~25行）:
- 1行概述 + 教训数
- 交叉加载决策树
- 不确定内容时读，知道要什么直接读具体文件

## 维护规则

- 同根因 → 合并 + 追加 `(再次: YYYY-MM-DD)` + 升优先级
- 相似模式 → 交叉引用 `[[related]]`
- 30 天未命中 → 移至 `# Dormant` 区（不删）
- 新增/删除/重命名教训 → 更新对应 `INDEX.md` 的教训数
