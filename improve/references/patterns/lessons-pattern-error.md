# Pattern: Error Handling

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: try, catch, except, error, panic, unwrap, result, throw, raise, reject, rescue, err, 错误, 异常, 捕获

---

## 通用原则

### ★★★ 吞错误 → 静默数据损坏 (置信度: high, 命中: 3)

**Rule**: 绝不吞掉错误（空 catch block / `_ = err` / `except: pass` / `.unwrap()` 在生产代码）
**Why**: 错误是唯一检测失败的手段。吞掉错误 = 让下游处理损坏的数据 = 最终失败时日志已无根因。
**最低**: 如果不处理，至少 `log.error("context", err)` + 传播。不能连日志都不打。

### ★★★ 错误信息不含上下文 → 无法定位 (置信度: high, 命中: 3)

**Rule**: 错误消息必须含"什么操作"+"什么输入"+"什么结果"。不抛裸 `"failed"`。
**Wrong**: `raise ValueError("invalid")` — 100 个地方抛同样的消息，不知道是哪个
**Right**: `raise ValueError(f"config parse: key={key} value={value}: expected int, got {type(v).__name__}")`
**Why**: 带上下文的错误消息 = 减少 debug 时间 90%。操作名、输入值、期望 vs 实际。

### ★★ 异常链断裂 → 根因丢失 (置信度: high, 命中: 2)

**Rule**: 捕获后重抛必须保留原始异常（`from`/`cause`/`%w`/wrapping）
**Right**: Python `raise X from e` / JS `throw new Error("ctx", {cause: e})` / Go `fmt.Errorf("ctx: %w", err)` / Rust `anyhow::Context`
**Why**: 调试时需要看到最初在哪行出错。异常链 = 调用栈的垂直版本。

### ★ 错误类型太粗 → 恢复策略受限 (置信度: medium, 命中: 1)

**Rule**: 用具体异常类型，不全部 `Exception`/`Error`。让调用方能按类型决定重试/跳过/abort。
**Right**: 定义 `RetryableError` vs `FatalError`，或 `ValueError` vs `IOError` vs `TimeoutError` 分别处理。

### ★★ [2026-08-22] 术语保护失败 → 整行回退或内部标记泄漏 (置信度: high, 命中: 2)

**Rule**: LLM 术语保护只用无语义占位符；后处理必须清除所有内部标记，标记丢失时保留主结果。
**Wrong**: 漏占位符就回退整行原文；改用携带原词的 HTML 标签又被模型翻译并泄漏到译图。
**Right**: 无语义占位符 + 宽容恢复 + 最终残留清洗；保护失败只降级该术语，不覆盖整行译文。
**Why**: 模型会改写任何可见结构；辅助机制不能比主结果更脆弱，也不能进入用户可见输出。

---

## 语言差异

| 陷阱 | Python | JavaScript | Go | Rust | Bash |
|------|--------|------------|----|----|----|
| 空捕获 | `except:` 吞 BaseException | `catch {}` 吞所有 | `_ = err` | `unwrap()` 生产 = panic | `|| true` |
| 异常链 | `raise X from e` | `{cause: e}` (ES2022) | `%w` fmt verb | `anyhow::Context` | `$?` |
| 编译检查错误 | mypy strict | TypeScript strict | 必须处理 error | 必须 match Result | 无 |
| 全局 handler | `sys.excepthook` | `window.onerror` + `unhandledrejection` | panic handler | `std::panic::set_hook` | `trap` |
| 断言生产禁用 | `-O` flag | N/A（console.assert） | N/A | release profile 跳过 debug_assert | N/A |
