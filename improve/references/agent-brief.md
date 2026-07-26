# Agent Brief 模板

> 来源: Matt Pocock `triage` — AFK agent 的权威规格说明

## 原则

- **耐久性 > 精确度**: 不引文件路径/行号（会过时），描述接口/类型/行为契约
- **行为描述**: 描述 what（系统该做什么），不描述 how（怎么实现）
- **完整验收标准**: 每个标准独立可验证
- **明确范围边界**: 列出 out of scope

## 模板

```markdown
## Agent Brief

**Category:** bug / enhancement
**Summary:** 一句话

**Current behavior:**
现状（bug = 错误行为，enhancement = 新功能基础）

**Desired behavior:**
目标行为。覆盖边界情况和错误条件。

**Key interfaces:**
- `TypeName` — 要改什么，为什么
- `functionName()` 返回类型 — 当前 vs 目标
- Config shape — 新增配置项

**Acceptance criteria:**
- [ ] 具体、可验证的标准 1
- [ ] 具体、可验证的标准 2

**Out of scope:**
- 不在此 issue 范围内的相关事项
```
