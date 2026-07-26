# Debug / Diagnose

> 加载条件: 任务涉及 debug, diagnose, bug, 调试, 诊断, 循环, 复现

---

## ★ [2026-06-16] 无反馈循环就开修 → 瞎猜 (置信度: high, 命中: 1)

**Rule**: Bug 修复第一步 = 构建快速、确定性的 agent 可运行的 pass/fail 信号
**Wrong**: 看代码 → 凭经验猜根因 → 直接改 → 改完等用户反馈
**Right**: 10 种方法构建循环（详见 [diagnose-loop.md](diagnose-loop.md)）→ 复现 → 假设 → 插桩 → 修复 → 回归
**Why**: 没有循环 = 不知道是否修好了。2 秒确定性循环是调试超能力。30 秒 flaky 循环 ≈ 没有。
**来源**: Matt Pocock `diagnose` Phase 1
**泛化**: 任何调试任务第一步永远是构建反馈循环，不分语言/框架/领域

---

## ★★ [2026-06-16] 调试日志无标记 → 清理遗漏 (置信度: medium, 命中: 2)

**Rule**: 每条临时调试日志打唯一前缀标签 `[DEBUG-xxxx]`，修完 `grep` 前缀全删
**Wrong**: `console.log("here"); console.log("value:", x);` — 修完不知道哪些该删
**Right**: `console.log("[DEBUG-a4f2] Order state:", state);` — `grep -r "\[DEBUG-a4f2\]"` 一键查
**Why**: 无标签的调试日志混入生产日志，下次 debug 误判。标签 = 免清理焦虑。
**来源**: 2026-06-15 原始教训（#state）迁移至此 domain
**泛化**: 任何临时 instrumentation（断点/日志/注入）都标记 + 修完清理

---

## ★ [2026-06-16] 单假设锚定 → 忽略其他根因 (置信度: medium, 命中: 1)

**Rule**: 生成 3-5 个排序假设后再测试，不可只拿一个就扎进去
**Wrong**: 第一个 plausible 想法 → 立刻追 → 追错方向
**Right**: 3-5 个可证伪假设（"If X is cause, changing Y makes bug disappear"）→ 排序 → 给用户看 → 再测试
**Why**: 单假设 = 锚定效应。多种可能 root cause 被忽略。用户常有领域知识一秒重排序。
**来源**: Matt Pocock `diagnose` Phase 3
**泛化**: 任何故障排除。先列可能原因，排优先级，再动手。
