# Pattern Index — 跨语言代码模式教训目录

> 按需浏览。路由自动匹配代码关键词，不需要手动读这个 index。
> 不确定某个模式覆盖什么时读这里。

## 文件清单

| Pattern | 文件 | 教训数 | 覆盖 |
|---------|------|--------|------|
| Async | [lessons-pattern-async.md](lessons-pattern-async.md) | 5 | 超时/竞态/限流/顺序假设/IndexedDB promise永不settle + 5语言差异表 |
| Loop | [lessons-pattern-loop.md](lessons-pattern-loop.md) | 5 | 修改迭代对象/闭包/进度/O(N²)/querySelector 只改第一个 |
| Error | [lessons-pattern-error.md](lessons-pattern-error.md) | 5 | 吞错误/无上下文/异常链断裂/类型太粗/辅助校验全量回退 + 5语言差异表 |
| I/O | [lessons-pattern-io.md](lessons-pattern-io.md) | 6 | 资源泄漏/外部输入校验/大文件OOM/编码假设 + 5语言差异表 |
| Type | [lessons-pattern-type.md](lessons-pattern-type.md) | 4 | 宽类型/any传染/null缩窄/enum穷举 |
| Test | [lessons-pattern-test.md](lessons-pattern-test.md) | 4 | 水平切片/flaky/只测happy path/测试名无场景 + 5语言差异表 |
| Perf | [lessons-pattern-perf.md](lessons-pattern-perf.md) | 4 | 不profile就优化/过早缓存/循环alloc/字符串拼接O(N²) + 4语言差异表 |
| Null | [lessons-pattern-null.md](lessons-pattern-null.md) | 4 | 空值崩溃/不可能为空假设/falsy合并/可选链滥用 + 4语言差异表 + Go nil interface专题 + JS null vs undefined专题 |

## 语言差异速查

| 陷阱 | Python | JavaScript | Go | Rust | Bash |
|------|--------|------------|----|----|----|
| 空值类型 | `None` | `null` + `undefined` | `nil` | `Option<T>` | `""` / unset |
| 忘 await | coroutine 静默丢失 | UnhandledPromiseRejection | goroutine 泄漏 | 编译错误 | N/A |
| 空捕获 | `except:` 吞 BaseException | `catch {}` | `_ = err` | `unwrap()` panic | `\|\| true` |
| 异常链 | `raise X from e` | `{cause: e}` (ES2022) | `%w` fmt verb | `anyhow::Context` | `$?` |
| 自动关闭 | `with` | `using` (ES2024) | `defer` | `Drop` (RAII) | `trap EXIT` |
| 大文件默认 | for line 流式 | 需 stream API | bufio.Scanner | BufReader | pipe |
| SQL 注入 | 参数化查询 | 参数化查询 | database/sql 占位符 | sqlx 宏 | `--arg` |
| 默认超时 | 无 | 无 (需 AbortController) | 无 | 需显式设 | `timeout` 命令 |
| Profiler | py-spy / cProfile | Chrome DevTools | pprof | perf / flamegraph | `time` |

## 交叉加载决策

```
async + 任何语言 → lessons-pattern-async.md + lang/lessons-<lang>.md #async
error + 任何语言 → lessons-pattern-error.md + lang/lessons-<lang>.md #error
null + .go         → lessons-pattern-null.md (Go nil interface 专题) + lessons-go.md #null
security + .py     → lessons-security.md + lessons-python.md #security
```
