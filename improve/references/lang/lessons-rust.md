# Rust Lessons

> 加载条件: .rs, rust, cargo, Cargo.toml, 用户说"Rust"

---

## #error — 错误处理陷阱

### ★★ unwrap() 在生产代码 → panic 崩溃 (置信度: high, 命中: 2)

**Rule**: 生产代码禁用 `.unwrap()` `.expect()`。用 `?` 传播或 `match`/`unwrap_or_*` 处理。
**Wrong**: `let config = read_config().unwrap();` — 文件不存在 → panic → 整个服务 crash
**Right**: `let config = read_config().context("failed to read config")?;` + main 里 `anyhow::Result`
**Why**: Rust 的 panic = 不可恢复错误（默认 unwind 析构 + 可能 abort）。库代码 panic 让调用方无法 recover。

---

## #type — 所有权/生命周期陷阱

### ★★ 引用生命周期不够 → 编译错误 (置信度: high, 命中: 2)

**Rule**: 避免在 struct 中存裸引用。新手用 `String` 而非 `&str`，用 owned type 先让编译过再优化。
**Wrong**: `struct Config { path: &str }` → 到处补生命周期标注 → 传染整个代码库
**Right**: `struct Config { path: String }` 或 `PathBuf`。先 owned → 跑通 → profile → 必要时退回引用。
**Why**: 生命周期标注是 Rust 最陡峭的学习曲线。owned types 的运行时开销通常可忽略。

### ★ clone() 滥用 → 掩盖设计问题 (置信度: medium, 命中: 1)

**Rule**: `.clone()` 出现在 hot path → 重构为借用。冷启动/配置加载 → clone 没问题。
**Right**: profile 定位 hotspot → 按需引入 `Cow`/`Rc`/`Arc`/借用。不提前优化。

---

## #async — 异步陷阱

### ★ tokio::spawn 忘记 await/join → 静默取消 (置信度: medium, 命中: 1)

**Rule**: `tokio::spawn()` 返回 `JoinHandle`，必须 `.await`。drop JoinHandle = cancel task。
**Wrong**: `tokio::spawn(background_worker());` — 下一行 drop handle → task 立刻取消
**Right**: `let handle = tokio::spawn(...); ... ; handle.await??;`
