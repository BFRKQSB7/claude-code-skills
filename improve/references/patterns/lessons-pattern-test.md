# Pattern: Testing

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: test, mock, stub, fixture, assert, spec, coverage, unit, integration, e2e, jest, pytest, vitest, 测试, 模拟, 断言

---

## 通用原则

### ★★★ 水平切片写测试 → 假阳假阴 (置信度: high, 命中: 3)

**Rule**: 垂直切片: test1 → impl1 → verify → test2 → impl2 → verify。禁止: 全部 test → 全部 impl。
**Why**: 批量写的测试基于**想象**的 API 行为而非**实际**行为。重构时假阳（不该过还过）+ 假阴（该过不过）。
**来源**: Matt Pocock `tdd` skill
**泛化**: 任何 AI agent 代码生成都适用。垂直 = 每次 cycle 学习实现细节。水平 = 猜测 × N。

### ★★ 测试依赖外部状态 → flaky (置信度: high, 命中: 2)

**Rule**: 单元测试不接触网络/文件系统/数据库/当前时间。用 mock/stub/fake。
**Right**: Python `unittest.mock` / JS `jest.mock()` / Go `interface` + fake impl / Rust `#[cfg(test)]` + mockall
**Why**: Flaky test = 失去信任 = 没人看测试结果。外部依赖的测试放 integration/e2e，单元测试保持纯函数。

### ★★ 只测 happy path → 边界未覆盖 (置信度: high, 命中: 2)

**Rule**: 每个函数至少测试: 正常输入 / 空输入 / 极大输入 / 错误输入。用 property-based test 发现边界。
**Right**: Python `hypothesis` / JS `fast-check` / Go `testing/quick` / Rust `proptest`
**Why**: 边界条件占 bug 的 80%。正常输入谁都会测，空/null/极大/格式错才是 bug 来源。

### ★ 测试名不含场景 → 失败时靠猜 (置信度: medium, 命中: 1)

**Rule**: 测试名 = `test_<what>_<scenario>_<expected>` (Python) / `it('should <expect> when <scenario>')` (JS)
**Wrong**: `test_lock()` → 失败时不知道测什么锁、什么场景、期望什么
**Right**: `test_acquireLock_whenOldPidAlive_killsAndTakesOver()` — 不读代码就知道失败含义

---

## 语言差异

| 陷阱 | Python | JavaScript | Go | Rust |
|------|--------|------------|----|----|
| Mock 方式 | unittest.mock / pytest-mock | jest.mock() | interface + fake | mockall / trait mock |
| Fixture | pytest fixture | beforeEach / setup | TestMain / t.Cleanup | #[test] 函数内 |
| 参数化测试 | `@pytest.mark.parametrize` | `it.each` / `test.each` | table-driven `[]struct{}` | `#[test_case]` 宏 |
| Mock 文件系统 | pyfakefs / tmp_path | memfs | `testing/fstest` | tempdir |
| Property test | hypothesis | fast-check | testing/quick | proptest |
| 断言库 | assert 内置 | expect() | 仅 if err | assert! / assert_eq! |
