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

---

## ★ [2026-08-11] IndexedDB put 不可克隆值 → onsuccess 内同步异常 → Promise 永不 settle (置信度: high, 命中: 1)

**Rule**: `put()` 含函数/不可结构化克隆的对象进 IndexedDB → `put` 在 onsuccess 回调里同步抛 `DataCloneError`，但 Promise executor 已返回 → `res/rej` 永不调用 → `await` **永久挂起**，try/catch 也抓不到（promise 不 reject）。持久化/副作用操作别阻塞主流程：fire-and-forget `.catch(()=>{})`。
**Wrong**: `await favDbSet(handle)` 依赖它 settle → 挂死。真实 `FileSystemFileHandle` 可结构化克隆（官方用法），但测试 mock（普通函数方法）不可克隆 → 假挂起。
**Right**: `favDbSet(handle).catch(()=>{})` 尽力而为，不 await；await 前确认 promise 必 settle。
**Why**: JS 事件处理器（onsuccess）里的同步异常不会 reject 外层 promise，异常变未捕获、promise 静默悬空。

## ★★ [2026-08-22] 先暴露可操作状态、后持久化 → 后续操作并发覆盖临时文件 (置信度: high, 命中: 1)

**Rule**: 异步任务进入“等待审核/可继续”等用户可操作状态时，状态发布、持久化与后续状态转换必须共享同一同步边界；同一记录的原子写临时文件也必须串行化。
**现象**: 前端刚轮询到可操作状态便提交下一步，首次 `job.tmp → job.json` 尚未完成；第二次持久化同时打开同一个 `job.tmp`，Windows 报 `PermissionError`，其他平台可能静默覆盖新状态。
**根因**: 任务状态先对其他线程可见，落盘在后；“临时文件再 rename”只保证单次写原子性，不保证多个写入者互斥。
**修复**: 每个持久化存储增加专用 mutex/单写者队列；状态转换先验证旧状态，并在同一同步协议内落盘和调度后续任务。测试必须覆盖“观察到可操作状态后立即提交”。
**泛化**: 适用于任务队列、审批流、断点续跑、文件式元数据和任何 read-modify-write 状态机。

## ★★ [2026-08-24] 只设置取消标志、不取消排队 Future → 重启后任务重复执行 (置信度: high, 命中: 1)

**Rule**: 支持“取消后立即重启”的任务队列必须区分排队与运行中任务：排队任务先调用调度器的 `Future.cancel()`，运行中任务才使用协作式取消标志；只有确认旧执行体不会再启动后，才能发布“已取消、可重启”状态。
**现象**: 排队任务被标记为已取消，用户立即重启；旧 Future 随后仍从队列启动，而取消标志已被重启流程清除，导致同一任务执行两次、同时写同一结果文件。
**修复**: 保存每个任务的 Future/handle；排队取消成功后再清理并允许重启，运行中则等安全边界确认退出。测试要占满 worker，覆盖“取消排队任务 → 立即重启 → 实际执行次数为 1”。
**泛化**: 适用于线程池、进程池、async task 队列以及任何把“取消标志”与可重试状态分开管理的系统。

## ★★ [2026-08-25] ThreadPoolExecutor 上下文退出等待运行中任务 → 取消界面仍卡死 (置信度: high, 命中: 1)

**Rule**: 不能协作取消的原生推理或网络调用若需快速中断，不要放在 `with ThreadPoolExecutor(...)` 中；上下文退出等价于等待式 shutdown，异常/取消路径仍会等运行中 Future 完成。
**修复**: 显式管理线程池，在轮询 Future 时检查取消，在退出时使用 `shutdown(wait=False, cancel_futures=True)`；仅可分离无写入副作用的工作，输出合成等写操作仍须等待安全边界。
**泛化**: 适用于 Python 包装的 ONNX/CUDA 推理、阻塞 SDK 和不支持 Abort 的 HTTP 客户端。
