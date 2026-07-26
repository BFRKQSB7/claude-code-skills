# Pattern: Performance / Memory

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: cache, memo, lazy, perf, optimize, benchmark, profile, memory, leak, slow, OOM, gc, 性能, 缓存, 优化, 内存

---

## 通用原则

### ★★★ 不 profile 就优化 → 牺牲可读性换零收益 (置信度: high, 命中: 3)

**Rule**: 优化前必 profile。不猜哪里慢。不优化非瓶颈代码（Amdahl's law）。
**Right**: `perf`/`pprof`/`py-spy`/Chrome DevTools → 找到 >5% CPU 的 hotspot → 优化 → 再次 profile 验证
**Why**: 人脑对性能瓶颈的直觉准确率 ~20%。90% 时间花在 10% 代码上。profile 告诉你哪 10%。

### ★★ 过早缓存 → 失效/内存双难题 (置信度: high, 命中: 2)

**Rule**: 缓存只在测量后加。有 TTL。有容量上限。有命中率监控。
**Wrong**: "这里可能慢，加个 cache" → 无 TTL → 内存无限增长 + 数据过期
**Right**: 先测 latency。慢 → 确认数据新鲜度要求 → 设计 TTL + max size → LRU/LFU eviction → 加命中率 metric
**Why**: 两个最难的问题：cache invalidation 和 naming。不同时解决过期和内存 = 定时炸弹。

### ★★ 循环里分配对象 → GC 压力 (置信度: medium, 命中: 2)

**Rule**: hot loop 内避免分配新对象（new/malloc/literal）。复用 buffer / object pool / stack allocation。
**Why**: 每秒百万次 alloc → GC 运行频繁 → CPU 被 GC 吃掉 50%+。Go escape analysis / Rust 栈分配 / Python 尽量用 generator。
**检测**: profile 看 allocation rate。不是每个 loop 都 hot — 先 profile。

### ★ 字符串拼接用 + → O(N²) (置信度: medium, 命中: 1)

**Rule**: 循环拼接字符串用 `join`/`StringBuilder`/`Vec<String>`。避免 `s += chunk` 在循环中。
**Why**: 大多语言字符串不可变。`+=` 每次创建新字符串复制全部内容 → O(N²)。`join` 一次分配 → O(N)。
**Right**: Python `''.join(chunks)` / JS `Array.push + join` / Go `strings.Builder` / Rust `String::push_str`

---

## 语言差异

| 陷阱 | Python | JavaScript | Go | Rust |
|------|--------|------------|----|----|
| Profiler | py-spy / cProfile | Chrome DevTools / clinic | pprof | perf / flamegraph |
| GC 模型 | 引用计数 + generational | mark-sweep (V8) | 并发 mark-sweep | 无 GC (ownership) |
| 内存分析 | tracemalloc / memray | heap snapshot | pprof --alloc_objects | valgrind / dhat |
| 字符串拼接 | `''.join()` | `arr.join('')` | `strings.Builder` | `String::push_str` |
| 对象池 | `queue.Queue` | object pool 手动 | `sync.Pool` | `object-pool` crate |
| 逃逸分析 | N/A | N/A | 编译器自动 (在堆/栈) | 显式 `Box` = 堆 |
