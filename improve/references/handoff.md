# Session Handoff Pattern

> 来源: Matt Pocock `handoff` skill

## 何时用

长任务跨会话、需要换 agent 继续、或用户说 "总结一下给下次继续"

## 格式

```markdown
# Handoff: <任务简述>

## 当前状态
- 完成了什么
- 卡在哪里
- 下一步是什么

## 关键上下文
- 相关文件路径
- 已排除的方案
- 已确认的前提

## Suggested Skills
- /skill-name — 为什么需要

## 参考
- PRD: path/to/prd.md
- Issue: #42
- ADR: docs/adr/0001-xxx.md
```

## 规则

- 不重复已存在 artifact 中的内容（PRD/ADR/Issue/commit），只引用路径
- 脱敏：删除 API key、密码、PII
- 存到 OS 临时目录，不放工作区
