# 诊断反馈循环

> 来源: Matt Pocock `diagnose` Phase 1 — "有了正确的循环，bug 就修了 90%"

## 10 种构建方法（按优先级排序）

1. **Failing test** — 在能触及 bug 的缝（seam）写失败测试
2. **Curl / HTTP script** — 对运行中的 dev server 发请求
3. **CLI invocation** — 用 fixture 输入 + diff stdout 对已知正确快照
4. **Headless browser script** — Playwright/Puppeteer 驱动 UI，断言 DOM/console/network
5. **Replay captured trace** — 把真实请求/payload/event log 存盘，隔离重放
6. **Throwaway harness** — 最小子系统（一个 service + mock deps），单函数调用触发 bug 路径
7. **Property / fuzz loop** — 1000 随机输入找 failure mode
8. **Bisection harness** — `git bisect run` 自动化二分
9. **Differential loop** — 同输入跑旧版本 vs 新版本，diff 输出
10. **HITL bash script** — 最后手段。结构化人类点击流程，捕获输出

## 迭代循环本身

有了循环后三问：
- 能更快？（cache setup, skip init, narrow scope）
- 信号更清晰？（assert 特定症状，不是"没崩"）
- 更确定性？（固定时间、seed RNG、隔离文件系统、冻结网络）

**2 秒确定性循环 = 调试超能力。30 秒 flaky 循环 ≈ 没有循环。**

## 非确定性 bug

目标不是干净复现 → 是**提高复现率**。Loop 100×, parallelize, add stress, narrow timing, inject sleeps。
50% flaky → 可调试。1% → 不行。

## 构建不了循环时

停止。列出尝试过的。要求用户提供: (a) 能复现的环境访问 (b) 捕获的 artifact (HAR/log dump/core dump) (c) 临时生产 instrumentation 权限。
