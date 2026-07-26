# Go Lessons

> 加载条件: .go, golang, go, go.mod, 用户说"Go" "Golang"

---

## #async — 并发陷阱

### ★★ goroutine 泄漏 → 内存无限增长 (置信度: high, 命中: 2)

**Rule**: 每条 goroutine 必须有退出路径。用 `context.Context` 传 cancellation，用 `sync.WaitGroup` 等完成。
**Wrong**: `go func() { for { select { case <-ch: work() } } }()` — 没人 close(ch) → goroutine 永不退出
**Right**: `go func() { for { select { case <-ctx.Done(): return; case <-ch: work() } } }()` → 调用方 `cancel()`
**Why**: 泄漏的 goroutine 类似内存泄漏 — GC 无法回收运行中的 goroutine。长期运行的服务逐步耗尽。

### ★★ channel 未关闭 → goroutine 永久阻塞 (置信度: high, 命中: 2)

**Rule**: `for range ch` 在没有 `close(ch)` 时永不退出。range channel 必须对应明确的 close。
**Wrong**: `go func() { for msg := range ch { process(msg) } }()` — 无人 close(ch) → goroutine 永远阻塞在 range
**Right**: 用 context: `select { case <-ctx.Done(): return; case msg, ok := <-ch: if !ok { return }; process(msg) }`
**Why**: `range ch` 等价于不断从 ch 读直到 close。不 close = 永远读 = goroutine 泄漏。

---

## #error — 错误处理陷阱

### ★★ 忽略 error 返回值 → 静默数据损坏 (置信度: high, 命中: 2)

**Rule**: 永远不 `_` 吞 error。最低限度 `if err != nil { log.Println(err) }`。
**Wrong**: `data, _ := ioutil.ReadAll(resp.Body)` — 网络错误 → data 截断 → 静默处理半截数据
**Right**: `data, err := io.ReadAll(...); if err != nil { return fmt.Errorf("read: %w", err) }`
**Why**: Go 没有异常。error = 唯一的错误信号。忽略 error = 假装错误没发生。

---

## #loop — 循环陷阱

### ★★ range 循环取地址 → 全指向最后元素 (置信度: high, 命中: 1)

**Rule**: `for _, item := range slice { ... &item ... }` 中的 `&item` 在全部迭代中是同一地址
**Wrong**:
```go
var ptrs []*Item
for _, item := range items {
    ptrs = append(ptrs, &item) // BUG: 全部指向最后一个 item
}
```
**Right**:
```go
for i := range items {
    ptrs = append(ptrs, &items[i]) // 或赋值给本地变量
}
```
**Why**: Go range 复用同一个迭代变量。`&item` 每次都是同一块内存，内容被覆盖。

---

## #null — 空值陷阱

### ★★★ nil interface ≠ nil concrete value → 空指针 (置信度: high, 命中: 3)

**Rule**: 返回 interface 的函数，nil 检查要检查底层 concrete value。interface 有两部分: `(type, value)`。
**Wrong**:
```go
func getUser() *User { return nil }
var u interface{} = getUser()
if u == nil { ... } // 不执行! u = (*User, nil) ≠ nil
```
**Right**: 不返回 `interface{}`，返回具体类型。或检查时用 reflect: `v.IsNil()`。
**Why**: `(nil, nil)` 才是 nil interface。`(*User, nil)` 是 non-nil interface，有 type 信息。这是 Go 面试第一题也是生产第一坑。

### ★★ type assertion 缺 ok → panic (置信度: high, 命中: 2)

**Rule**: 永远用 comma-ok 模式: `val, ok := x.(Type)`。不用单返回值断言。
**Wrong**: `user := data.(User)` — data 是 `*Admin` 或 nil → panic
**Right**: `user, ok := data.(User); if !ok { return fmt.Errorf("unexpected type: %T", data) }`
**Why**: 单返回值断言失败 = panic，无恢复机会。comma-ok 允许容错处理。

---

## #lifecycle — defer 陷阱

### ★★ defer 在循环中 → 资源堆积 (置信度: high, 命中: 2)

**Rule**: 不在 for 循环中 defer 资源释放。用匿名函数包裹或手动关闭。
**Wrong**:
```go
for _, f := range files {
    file, _ := os.Open(f)
    defer file.Close() // 全部文件堆积到函数返回才关
}
```
**Right**: 提取为独立函数 `func processOne(f string) { ... defer close() }` 或匿名函数包裹
**Why**: defer 在函数返回时执行，不是块退出时。循环中的 defer 全部堆积 = FD 耗尽。

### ★★ time.After 在 select 循环中 → 内存泄漏 (置信度: high, 命中: 2)

**Rule**: `for { select { case <-time.After(d): ... } }` 每次循环创建新 timer，GC 要等 timer 触发才回收
**Wrong**: `for { select { case <-time.After(5*time.Second): work() } }` — timer 泄漏
**Right**: `t := time.NewTimer(5*time.Second); for { select { case <-t.C: work(); t.Reset(5*time.Second) } }`
**Why**: `time.After` 创建的 timer 在触发前不会被 GC。循环中不断创建 → 内存持续增长。

### ★ sync.WaitGroup Add 在 goroutine 内部 → 竞态 (置信度: medium, 命中: 1)

**Rule**: `wg.Add(1)` 必须在 goroutine 外部调用，不能在 goroutine 内部。
**Wrong**: `go func() { wg.Add(1); defer wg.Done(); work() }()` — Add 可能在 Wait 之后执行
**Right**: `wg.Add(1); go func() { defer wg.Done(); work() }()`
**Why**: WaitGroup 计数必须 ≥ 启动的 goroutine 数。Add 在 goroutine 内 = Wait 可能先于 Add 返回。

---

## #context — Context 陷阱

### ★★ context.Background() 断链 → goroutine 无法取消 (置信度: high, 命中: 2)

**Rule**: 下游函数永远从上游 context 派生（`context.WithTimeout`/`WithCancel`）。不新建 `context.Background()`。
**Wrong**: 中间件创建 `ctx := context.Background()` → 上游超时/取消传播断裂 → goroutine 泄漏
**Right**: `ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second); defer cancel()`
**Why**: context 链 = goroutine 的生命线。断链 = goroutine 失控 = 最常见的生产内存泄漏。

### ★ context 值类型断言缺 ok → panic (置信度: medium, 命中: 1)

**Rule**: `ctx.Value(key).(string)` → 用 comma-ok: `val, ok := ctx.Value(key).(string)`
**Why**: context.Value 返回 `interface{}`。没有 comma-ok 的类型断言 = 潜在 panic。
