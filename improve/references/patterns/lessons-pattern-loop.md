# Pattern: Loop / Iteration

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: loop, iterate, for, while, map, filter, reduce, generator, yield, range, forEach, 循环, 迭代, 遍历

---

## 通用原则

### ★★★ 迭代中修改被迭代对象 → 未定义行为 (置信度: high, 命中: 3)

**Rule**: 不在循环体内修改正在迭代的集合（增/删/重排）。需要修改 → 迭代副本或分批处理。
**Why**: 几乎所有语言的迭代器在底层修改集合时行为不可预测：跳过元素、重复元素、IndexError、ConcurrentModificationException。
**Right**: 通用模式 — `for item in list(collection):` (Python) / `[...arr].forEach()` (JS) / `for i := len(slice)-1; i >=0; i--` 倒序删除

### ★★ 循环变量闭包捕获 → 延迟绑定 (置信度: high, 命中: 2)

**Rule**: 循环创建闭包/goroutine → 显式传参或本地副本。不依赖循环变量在闭包执行时的值。
**Why**: 多数语言是"引用捕获"不是"值捕获"。闭包执行时循环变量已前进到最终值。
**Right**: `for x in xs: task(x=x)` (Python, copy by keyword) / `for (let x of xs) { ... }` (JS, let = per-iteration binding) / `x := x; go func() { use(x) }()` (Go, shadow copy)

### ★ 大循环无进度信号 → 不知道卡在哪 (置信度: medium, 命中: 1)

**Rule**: N > 1000 的循环，每 10% 或每 1000 条打印进度/日志
**Right**: `if i % 1000 == 0: print(f"{i}/{N}")` / progress bar library / structured logging

### ★ O(N²) 嵌套循环 → 性能陷阱 (置信度: medium, 命中: 1)

**Rule**: 对列表每个元素遍历另一列表 → O(N²)。常见反模式：`for x in xs: if x in ys:`。
**Right**: 将内层查找转为 `set`/`Map` O(1) → O(N)。或用 `itertools.product`/`cross-join` 明确表达意图。

---

## 语言差异

| 陷阱 | Python | JavaScript | Go | Rust |
|------|--------|------------|----|----|
| 迭代中删元素 | 索引偏移漏检 | `splice` 有同问题 | index 倒退法 | `Vec::retain` |
| 循环闭包 | lambda 捕获引用 | `let` = 每次新绑 | goroutine 截图 | move closure |
| for-in 遍历原型 | N/A | 需 `hasOwnProperty` | N/A | N/A |
| range 取地址 | N/A | N/A | 复用同一变量 | N/A |
| 无穷迭代器 | `itertools.count()` | generator 可以 | `for {}` channel | `std::iter::repeat` |
