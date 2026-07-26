# Lessons Learned — Phase 1 路由表

> 统一路由。Phase 1 读此文件 → 匹配关键词/扩展名 → 确定要加载的教训文件清单。
> 单文件 ~70 行，不存教训内容，只有路由规则。

## 无条件常加载

| 文件 | 原因 |
|------|------|
| [lessons-critical.md](lessons-critical.md) | ★★★ 系统性顽疾，无条件加载 |

## 路由规则（按优先级匹配）

### Layer 1: 触发词精确匹配（任务描述中的关键词）

| 触发词 | 加载文件 |
|--------|---------|
| 发布 / release / 打包 / version bump | lessons-cleanup.md |
| daemon / lock / pid / 后台 / 守护 / 竞态 / SessionStart | lessons-process.md |
| API / CLI / 采样 / 跨平台 / monitoring | lessons-state.md |
| skill / plugin / 技能 / 反省 / 学习 / README / 多语言 | lessons-skill.md |
| debug / diagnose / 调试 / 诊断 / 复现 / 排查 | lessons-debug.md |
| security / auth / token / 安全 / 认证 / 加密 / SQL注入 | lessons-security.md |
| MCP / chrome / devtools / browser / WebFetch / WebSearch / 浏览器 / 搜索 / 截图 / 网页 | lessons-mcp.md |

### Layer 2: 文件扩展名检测（任务的输入/输出文件）

| 扩展名 | 加载文件 |
|--------|---------|
| `.py` `.pyx` `.pyi` | lang/lessons-python.md |
| `.js` `.ts` `.jsx` `.tsx` `.mjs` `.cjs` | lang/lessons-javascript.md |
| `.go` | lang/lessons-go.md |
| `.rs` | lang/lessons-rust.md |
| `.sh` `.bash` `.zsh` | lang/lessons-bash.md |
| **`.bat` `.cmd`** | **lang/lessons-bash.md** + patterns/lessons-pattern-io.md #encoding |

### Layer 3: 代码模式检测（编辑内容中的代码模式）

| 模式关键词 | 加载文件 |
|-----------|---------|
| async / await / Promise / goroutine / tokio / 并发 | patterns/lessons-pattern-async.md |
| for / while / loop / 循环 / 遍历 / 迭代 | patterns/lessons-pattern-loop.md |
| try / catch / error / unwrap / panic / 错误 / 异常 | patterns/lessons-pattern-error.md |
| open / read / write / fetch / http / 文件 / 编码 / encoding / UTF-8 / BOM / GBK / **乱码** | patterns/lessons-pattern-io.md |
| null / None / nil / undefined / 空值 / 空指针 | patterns/lessons-pattern-null.md |
| type / interface / any / enum / 类型 | patterns/lessons-pattern-type.md |
| test / assert / expect / 测试 / 用例 | patterns/lessons-pattern-test.md |
| profile / 性能 / 优化 / O(N) / alloc | patterns/lessons-pattern-perf.md |

### Layer 4: 组合触发（多条件同时命中 → 全部加载）

| 组合 | 加载 |
|------|------|
| `.bat` + encoding/乱码/UTF-8/BOM | lang/lessons-bash.md #encoding + patterns/lessons-pattern-io.md #encoding |
| `.go` + async/goroutine | lang/lessons-go.md #async + patterns/lessons-pattern-async.md |
| `.py` + try/except/错误处理 | lang/lessons-python.md #error + patterns/lessons-pattern-error.md |
| MCP + browser/chrome | lessons-mcp.md（★ 强制先读再调 MCP 工具）|
| 变更 + 删除/重命名/移动 | lessons-cleanup.md（grep 旧引用门禁）|
| 发布 + 任何语言 | lessons-cleanup.md + lessons-skill.md #发布 |

### Layer 5: 门禁自检（操作类型触发，不是关键词触发）

| 操作类型 | 加载文件 |
|---------|---------|
| 删除/重命名/移动文件 | lessons-cleanup.md |
| git push / 发布 | lessons-cleanup.md + lessons-skill.md #publish |
| MCP 工具调用（`mcp__*`） | lessons-mcp.md（★ 永久门禁，不查 = 反复撞墙）|
| 安全敏感操作（auth/crypto/凭证）| lessons-security.md |

## 使用方式

Phase 1 执行流程:
1. 无条件加载 `lessons-critical.md`
2. 扫描任务描述 → Layer 1 匹配 → 加载对应 domain 文件
3. 扫描输入文件扩展名 → Layer 2 匹配 → 加载对应 lang 文件
4. 扫描代码内容/编辑模式 → Layer 3 匹配 → 加载对应 pattern 文件
5. 检查操作类型 → Layer 4 组合 → Layer 5 门禁 → 追加加载
6. 输出避坑清单（2-6 个文件，~2-4K tokens）

## 命中选择逻辑

单层内的多个匹配项 → **全部加载**（不是选一个）。
但每层有上限：Domain ≤ 2, Language ≤ 2, Pattern ≤ 3，超出取优先级高的（按 INDEX.md 中的命中次数排序）。
最终清单 2-6 个文件。

## 维护

- 新增教训文件 → 在本表对应 Layer 加路由规则
- 教训文件重命名 → 同步更新本表所有引用
- 30 天未命中 → 路由保持，教训文件内部降级到 #dormant
- 新增触发词 → 加在对应 Layer，不要跨 Layer 重复
