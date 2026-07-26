# Pattern: Null / Undefined / Optional Handling

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: null, nil, None, undefined, optional, maybe, nullable, ?, unwrap, 空指针, 空值, 判空, 可选

---

## 通用原则

### ★★★ 未检查 null/None/nil 就访问 → 运行时崩溃 (置信度: high, 命中: 3)

**Rule**: 任何可能为空的返回值/参数，在使用前必须显式检查。不假设"这里不可能是空"。
**Why**: Sonar 数据 — null pointer dereference 是继 dead code 之后 **第二常见的 bug**（~1,500 可靠性 issue/M LoC）。2025 年 6 月 Google Cloud 大宕机的根因就是 null 值处理缺失。
**模式**: null 值可能来自 — 外部 API / 数据库查询 / 文件读取 / 用户输入 — 任何 I/O 边界都是 null 来源。

### ★★★ "不可能为空"的假设 → 生产事故 (置信度: high, 命中: 3)

**Rule**: 代码注释"this can never be null"是反模式。用类型系统强制 non-null，或用防御性检查。
**Why**: 需求变化/重构/上游变更会让"绝不可能"变"偶尔发生"。类型系统比注释可靠 100 倍。
**防御**: TypeScript `strictNullChecks` / Python `mypy strict` / Rust `Option<T>` 编译时强制 / Go `if err != nil` idiom

### ★★ 空值语义不明确 → 逻辑错误 (置信度: high, 命中: 2)

**Rule**: 区分"不存在"vs"存在但为空"vs"出错"。不把所有空白情况合并处理。
**Wrong**: `if not data:` 合并了 `None`, `[]`, `{}`, `0`, `False`, `""` — 六种不同语义
**Right**: 显式检查 `if data is None:` vs `if len(data) == 0:` vs `if not data.ok:`
**Why**: Python/JS 的 falsy 值语义太宽。`0` 和 `None` 和 `[]` 在业务上完全不同，合并处理 = 隐藏 bug。

### ★ 可选链滥用 → 吞掉真正的错误 (置信度: medium, 命中: 1)

**Rule**: `?.` / `Optional.map()` 只在"值为空是正常情况"时使用。如果空值代表 bug，应该 fail loud。
**Wrong**: `user?.profile?.address?.city` — 链上任一环节空 → 静默 undefined → 用户看到空白页面，没人知道
**Right**: 在边界处校验: `assert user.profile is not None, "profile not loaded"` → 后续代码安全访问
**Why**: 可选链是方便的，但过度使用 = 隐藏 bug。fail fast > fail silently。

---

## 语言差异

| 陷阱 | Python | JavaScript/TS | Go | Rust |
|------|--------|---------------|----|----|
| 空值类型 | `None` (singleton) | `null` + `undefined` (两种!) | `nil` | `None` (Option) |
| 编译时检查 | mypy strict 模式下 | `strictNullChecks: true` | 运行时检查（无编译保护） | **编译时强制** (Option<T>) |
| 安全访问 | `getattr(obj, 'x', default)` | `?.` (optional chaining) | 手动 `if x != nil` | `x.map()` / `?` |
| 常见陷阱 | `Optional[X]` = `X\|None` | `typeof null === 'object'` | nil interface ≠ nil concrete | `unwrap()` = panic |
| 零值语义 | `None` ≠ `0` ≠ `[]` | `null == undefined` (==) | nil = zero value | `None` ≠ `0` |
| falsy 陷阱 | `0`, `[]`, `""` 都是 falsy | `0`, `""`, `false`, `NaN` | 无 falsy 概念（bool 明确） | 无 falsy 概念 |

## Go 特殊陷阱: nil interface ≠ nil concrete value

```go
// ❌ 常见生产 bug
func getUser() *User { return nil }
var u interface{} = getUser()
if u == nil {
    // 不会执行! u != nil 因为 interface 持有 (*User, nil)
    // interface 有两部分: (type, value)
    // (nil, nil) → nil interface
    // (*User, nil) → non-nil interface ← BUG!
}
```

**Rule**: 返回 interface 的函数，nil 检查要检查底层 concrete value。或直接返回具体类型。

## JavaScript/TS 特殊陷阱: null vs undefined

```typescript
// ❌ 混乱的检查
if (x == null)   // 匹配 null 和 undefined (loose equality)
if (x === null)  // 只匹配 null
if (x == undefined) // 匹配 null 和 undefined
if (typeof x === 'undefined') // 只匹配 undefined（安全，x 可能未声明）

// ✅ 最佳实践
if (x == null)   // 故意同时检查 null 和 undefined（常见模式）
if (x != null)   // type guard: x is T (排除 null/undefined)
value ?? default // nullish coalescing: null/undefined → default（不短路 0/""）
value || default // false/0/""/null/undefined → default（太宽，有陷阱）
```
