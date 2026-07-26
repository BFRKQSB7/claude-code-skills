# Lessons Index — 三轴路由

> 纯路由表。正文在 `references/` 按需加载。想看某轴有哪些教训 → 读对应 `INDEX.md`。

## 路由逻辑

```
触发 → 检测 Language（扩展名）→ 检测 Pattern（代码关键词）→ 匹配 Domain（任务关键词）
     → 交集加载 2-4 个文件（每文件 ~30-80 行，总 ~2K tokens）
     → 不确定时读对应 INDEX.md 浏览目录
```

## 元规则

- **合并**: 同根因合并 + `(再次: date)` + 升优先级
- **休眠**: 30天未命中 → 移入文件底部 Dormant 区
- **格式**: Rule/Wrong/Right/Why（再犯坑）；泛化/核心（设计决策）
- **归类**: 语言特定 → `lang/` | 模式通用 → `patterns/` | 工程领域 → `references/lessons-*.md`

---

## 轴 1 — Domain（工程领域）

> 匹配任务关键词 → 加载 1-2 个 domain 文件。INDEX: [references/INDEX.md](references/INDEX.md)

| 关键词 | 文件 |
|--------|------|
| daemon, lock, pid, startup, session, hook, 后台, 守护, 进程, 启动, 竞态, 超时, 并发, 单例 | [lessons-process.md](references/lessons-process.md) |
| migration, refactor, delete, rename, version, bump, release, install, package, zip, 迁移, 删除, 重命名, 版本, 发布, 打包, 引用, 残留, 清理 | [lessons-cleanup.md](references/lessons-cleanup.md) |
| api, monitoring, sampling, balance, cli, cross-platform, windows, path, env, 余额, 采样, 轮询, 跨平台, 环境变量, 初始化 | [lessons-state.md](references/lessons-state.md) |
| skill, plugin, design, naming, description, workflow, learning, readme, i18n, multi-language, 多语言, 翻译, 技能, 插件, 反省, 教训, 学习, 审查, 模板 | [lessons-skill.md](references/lessons-skill.md) |
| debug, diagnose, bug, fix, log, trace, verify, 调试, 诊断, 复现, 日志, 追踪, 验证, 排查 | [lessons-debug.md](references/lessons-debug.md) |
| security, auth, login, token, password, encrypt, hash, injection, XSS, CSRF, CORS, deserialize, pickle, eval, 安全, 认证, 加密, 注入, 反序列化, 依赖 | [lessons-security.md](references/lessons-security.md) |
| **MCP, mcp__, chrome, devtools, browser, WebFetch, WebSearch, navigate, snapshot, screenshot, evaluate_script, click, fill, hover, select_page, press_key, type_text, upload_file, list_pages, new_page, performance, lighthouse, console, network, fetch, search, URL, link, http, huggingface, page, 浏览器, 搜索, 截图, 网页, 打开, 访问, 页面, 下载, 表单, 登录, 渲染** | **[lessons-mcp.md](references/lessons-mcp.md)** ⚠️ |

---

## 轴 2 — Language（编程语言）

> 扫描项目扩展名 → 加载对应语言文件。INDEX: [references/lang/INDEX.md](references/lang/INDEX.md)

| 触发条件 | 文件 |
|----------|------|
| `.py` `python` `pip` `pyproject.toml` `django` `flask` `fastapi` `pytest` | [lang/lessons-python.md](references/lang/lessons-python.md) |
| `.js` `.ts` `.tsx` `.jsx` `.mjs` `.cjs` `node` `npm` `react` `vue` `next` | [lang/lessons-javascript.md](references/lang/lessons-javascript.md) |
| `.sh` `.bash` `.zsh` `bash` `shell` `脚本` | [lang/lessons-bash.md](references/lang/lessons-bash.md) |
| `.rs` `rust` `cargo` `Cargo.toml` | [lang/lessons-rust.md](references/lang/lessons-rust.md) |
| `.go` `golang` `go` `go.mod` | [lang/lessons-go.md](references/lang/lessons-go.md) |

---

## 轴 3 — Pattern（代码模式）

> 检测代码关键词 → 加载对应模式文件。INDEX: [references/patterns/INDEX.md](references/patterns/INDEX.md)

| 关键词 | 文件 |
|--------|------|
| `async` `await` `promise` `future` `goroutine` `tokio` `spawn` `thread` `concurrent` `异步` `并发` `协程` | [patterns/lessons-pattern-async.md](references/patterns/lessons-pattern-async.md) |
| `loop` `for` `while` `map` `filter` `reduce` `generator` `range` `forEach` `循环` `迭代` `遍历` | [patterns/lessons-pattern-loop.md](references/patterns/lessons-pattern-loop.md) |
| `try` `catch` `except` `error` `panic` `unwrap` `result` `throw` `raise` `err` `错误` `异常` `捕获` | [patterns/lessons-pattern-error.md](references/patterns/lessons-pattern-error.md) |
| `open` `read` `write` `file` `http` `fetch` `db` `sql` `api` `json` `csv` `socket` `文件` `网络` `数据库` `读写` | [patterns/lessons-pattern-io.md](references/patterns/lessons-pattern-io.md) |
| `type` `interface` `generic` `trait` `annotation` `type hint` `any` `Optional` `enum` `类型` `泛型` `接口` | [patterns/lessons-pattern-type.md](references/patterns/lessons-pattern-type.md) |
| `test` `mock` `stub` `fixture` `assert` `spec` `coverage` `jest` `pytest` `vitest` `测试` `模拟` `断言` | [patterns/lessons-pattern-test.md](references/patterns/lessons-pattern-test.md) |
| `cache` `perf` `optimize` `benchmark` `profile` `memory` `leak` `OOM` `性能` `缓存` `优化` `内存` | [patterns/lessons-pattern-perf.md](references/patterns/lessons-pattern-perf.md) |
| `null` `nil` `None` `undefined` `optional` `nullable` `??` `?.` `空指针` `空值` `判空` `可选` | [patterns/lessons-pattern-null.md](references/patterns/lessons-pattern-null.md) |

---

## 常加载

- **[lessons-critical.md](references/lessons-critical.md)** — ★★★ 系统性顽疾，Phase 1 无条件加载（~80 行）
- **检测到变更操作** → 必加载 [lessons-cleanup.md](references/lessons-cleanup.md)
- **检测到安全关键词** → 必加载 [lessons-security.md](references/lessons-security.md)
