# Pattern: Type System

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: type, interface, generic, trait, protocol, annotation, typedef, type hint, any, unknown, Optional, Union, enum, 类型, 泛型, 接口

---

## 通用原则

### ★★★ 类型宽度过大 → 误用 (置信度: high, 命中: 3)

**Rule**: 返回类型/参数类型越窄越好。不返回 `dict`/`object`/`any`/`interface{}`。
**Wrong**: `def process(data: dict) -> dict:` — 调用方对键值一无所知
**Right**: `def process(data: ProcessInput) -> ProcessOutput:` (TypedDict/dataclass/pydantic)
**Why**: 宽类型 = 无类型。`dict` 可以是任何结构。窄类型让编译器和 IDE 能帮你验证。

### ★★ any / interface{} 传染 → 整链无检查 (置信度: high, 命中: 2)

**Rule**: 一处 `any`/`as any`/`interface{}` → 调用方也失检查 → 传染到整个调用链。唯一例外是 FFI 边界。
**Right**: TypeScript `unknown` + type guard / Go generics / Python `TypeVar` / Rust `Box<dyn Trait>`
**Why**: `any` = 退出类型系统 = 人类自己保证正确性 = 迟早出错。

### ★ 可选值未缩窄 → NPE/NoneType error (置信度: medium, 命中: 1)

**Rule**: `Optional`/`null`/`undefined`/`nil` 返回后必须先缩窄（null check）才能访问属性
**Right**: Python `if x is not None:` / TS `x?.prop ?? default` / Go `if err != nil { return }` / Rust `match Option { Some(v) => ..., None => ... }`
**Why**: 大多数 runtime crash 是 null dereference。类型系统告诉你"可能为空" = 你必须处理。

### ★ enum/union 不完备匹配 → 漏分支 (置信度: medium, 命中: 1)

**Rule**: 新增 enum 成员/union variant 时，编译器/检查器应强制所有 match/switch 分支更新
**Right**: Rust `match` 编译强制穷举 / TS `switch` + `never` exhaustiveness check / Python `match` + mypy `--warn-unreachable`
**Why**: 漏掉一个新 variant = 运行时走到意外分支 = 逻辑错误或 crash

---

## 语言差异

| 陷阱 | Python | TypeScript | Go | Rust |
|------|--------|------------|----|----|
| 宽类型 | `dict` → 用 TypedDict/dataclass | `any` → 用 `unknown` | `interface{}` → 用 generics | `Box<dyn Any>` 极少用 |
| null safety | Optional 需显式 check | strictNullChecks | nil 接口非 nil | Option<T> 强制 |
| 泛型语法 | `TypeVar` / `[T]` (3.12) | `<T>` | `[T any]` (1.18+) | `<T>` |
| exhaustiveness | mypy `match` 检查 | `never` type trick | `default: panic` | 编译时保证 |
| 类型体操 | Protocol / overload | conditional types | 无 | associated types / GATs |
