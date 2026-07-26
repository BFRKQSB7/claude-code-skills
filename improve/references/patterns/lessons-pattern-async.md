# Pattern: Async / Concurrency

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: async, await, coroutine, promise, future, thread, concurrent, parallel, goroutine, tokio, spawn, non-blocking, 异步, 并发, 协程

---

## 通用原则

### ★★★ 并发操作缺超时 → 资源泄漏 (置信度: high, 命中: 3)

**Rule**: 任何 I/O 并发操作（网络请求/文件读取/锁获取/channel 接收）必须有 timeout。没有 timeout 的并发 = 定时炸弹。
**Why**: 网络断开/远端卡死/锁持有者 crash → 永不响应 → goroutine/thread/Promise 累积 → OOM。
**防御**: PR review 检查点 — 每个 await 路径追溯到最外层，确认有 `timeout`/`AbortController`/`with_timeout`。

### ★★ 共享状态无同步 → 数据竞争 (置信度: high, 命中: 2)

**Rule**: 多线程/多协程共享可变数据必须有同步原语（mutex/channel/atomic）。不假设"这个操作太快不可能交错"。
**Why**: 数据竞争 = undefined behavior。不只是"结果可能不对"，而是编译器和 CPU 可以任意重排代码。正确性不能依赖"感觉上不会发生"。
**检测**: Go `-race`、Python `threading` + `-X faulthandler`、JS 单线程无数据竞争但有不 await 的逻辑竞争。

### ★★ 并发数量无上限 → 资源耗尽 (置信度: high, 命中: 2)

**Rule**: 动态生成 goroutine/thread/Promise 必须有上限（semaphore/worker pool/限流器）
**Wrong**: `for _, url := range urls { go fetch(url) }` — 10000 个 URL = 10000 goroutine = FD 耗尽
**Right**: semaphore channel / worker pool / `Promise.all` chunked / `asyncio.Semaphore`

### ★ 顺序假设 → 逻辑竞争 (置信度: medium, 命中: 1)

**Rule**: 不假设并发操作的完成顺序，除非显式同步
**Wrong**: 启动 task A + task B，假设 A 先完成 → B 用到 A 的副作用但未 await A
**Right**: 有依赖 → 串行或显式 `await A; await B`。无依赖 → 各自独立处理结果

---

## 语言差异

| 陷阱 | Python | JavaScript | Rust | Go | Bash |
|------|--------|------------|------|----|----|
| 忘 await | coroutine 静默丢失 | UnhandledPromiseRejection | 编译错误 `must use future` | goroutine 泄漏 | N/A |
| 嵌套事件循环 | RuntimeError | 不支持 | N/A | N/A | N/A |
| GC 取消 task | `create_task` 不存引用 | Promise 不取消 | drop Future = 取消 | goroutine 不被 GC 取消 | N/A |
| 默认超时 | 无 | 无（需 AbortController） | 无 | 无 | `timeout` 命令可用 |
| 数据竞争检测 | 需 `threading` 或 mypy | 单线程无真数据竞争 | 编译时保证 | `-race` flag | N/A |
