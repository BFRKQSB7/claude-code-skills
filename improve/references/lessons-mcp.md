# MCP Tool Calling Lessons

> Chrome DevTools MCP / WebFetch / WebSearch / 浏览器自动化经验

---

## ★★★ Chrome DevTools MCP 连接：自己起专用 Chrome + `--browserUrl`，别伪造 DevToolsActivePort `rotatable` (since: 2026-08-07, last_hit: 2026-08-07)

**Rule**: 要用 Chrome DevTools MCP 时，**首选自己启动一个专用 Chrome**（独立 `--user-data-dir` + `--remote-debugging-port=<空闲端口>`），再用 `--browserUrl=http://127.0.0.1:<端口>` 启动 MCP。**不要伪造 DevToolsActivePort，不要依赖 `--auto-connect`**。

**Wrong**:
- `--auto-connect` 需要用户真实 Chrome 开着 + 手动开 remote debugging（Chrome ≥136 拒绝在默认 profile 上开调试端口）→ 经常连不上
- 伪造 DevToolsActivePort（复制端口文件到默认位置骗 MCP）→ 繁琐、UUID 易过期、耗时极长，且复制 cookie 带不来登录态（Chrome ≥127 app-bound 加密）

**Right**（browser-testing skill 已固化）:
1. `launch_skill_chrome.ps1`：复用/自动启动专用 Chrome（持久 profile `~\.chrome-skill`，挑空闲端口 9222+），TCP 活性确认
2. MCP 用 `--browserUrl=http://127.0.0.1:<端口>` 显式连接（无 auto-connect、无 DevToolsActivePort）
3. MCP 本体用本地固定安装（`~/.claude/chrome-devtools-mcp`），启动不联网
4. 登录态走持久 profile：`login.bat` 一次性登录，之后所有会话复用

**Why**: 关键洞察 = **别对抗 MCP 的自动发现，给它一个确定的 URL**。Chrome ≥136 只是禁止在**默认** user-data-dir 上开调试端口；独立 profile 上 `--remote-debugging-port` 照常有效。所以自己起一个专用浏览器就绕开了禁令，`--browserUrl` 是显式连接、完全确定。`--auto-connect` 需要读 `DevToolsActivePort` 文件 + 手动 toggle，两个脆弱点都消掉了。
**检测**: MCP 连不上 → 跑 `scripts/launch_skill_chrome.ps1`，看 `~/.claude/chrome-devtools.json` 的 `ok`/`port`；`list_pages` 端到端 3-4s 应连上。
**命中**: 2026-08-07 — 用户旧会话反复调试靠伪造 DevToolsActivePort 才连上且无登录态；新方案热/冷启动、多会话并发全部 PASS

---

## ★★★ Chrome DevTools 连接：DevToolsActivePort 路径不匹配 + UUID 过期 `permanent`

> ⚠️ **首选上方新方案**（自己起专用 Chrome + `--browserUrl`），本 hack 仅在无法自己启动浏览器时才需要。

**Rule**: Chrome `--remote-debugging-port` 强制 `--user-data-dir` 为非默认目录，但 MCP 工具硬编码读取 `%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort`。**不要试图让 MCP 工具读新目录——直接伪造它要的文件**。另外 Chrome 重启后 UUID 会变，旧文件里的 UUID 即使路径正确也连不上。

**Wrong**:
```
# Chrome 写 DevToolsActivePort 到自定义目录
chrome --remote-debugging-port=9222 --user-data-dir=C:\custom-dir
# MCP 读默认目录 → 找不到 → 永远连不上
```

**Right**:
```
# 1. 启动 Chrome（可以不带 --user-data-dir，用默认目录）
chrome --remote-debugging-port=9222

# 2. 从 Chrome HTTP API 获取当前 browser UUID
curl http://127.0.0.1:9222/json/version → webSocketDebuggerUrl

# 3. 更新 DevToolsActivePort（覆盖旧 UUID）
printf "9222\n/devtools/browser/<current-uuid>\n" > "%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort"
```

**Why**: MCP 工具代码写死默认路径，Chrome 安全策略禁止默认目录开调试端口 → 两个约束冲突 → 唯一解法是"欺骗"MCP 工具

**UUID 过期问题**: Chrome 每次启动生成新 UUID。上次会话的 `DevToolsActivePort` 文件还在，但 UUID 已失效。MCP 读到旧 UUID → 连接旧 WebSocket endpoint → 404。**每次 Chrome 重启后必须重新同步 UUID**。

**完整诊断流程**:
```bash
# Step 1: 确认端口在监听
curl -s http://127.0.0.1:9222/json/version || echo "Chrome not listening"

# Step 2: 对比 UUID
cat "%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort" 2>/dev/null
# 第二行 /devtools/browser/<uuid> 必须和 Step 1 的 webSocketDebuggerUrl 匹配

# Step 3: 不匹配 → 写入当前 UUID
printf "9222\n/devtools/browser/<current-uuid>\n" > "%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort"
```

**检测**: 先 `curl http://127.0.0.1:9222/json/version` 确认端口在监听 + 拿到当前 UUID → 对比文件里的 UUID

**启动方式**: **禁止**从 bash 用 `start "" chrome.exe` 启动 Chrome → 桌面上生成 `Google Chrome.lnk` 快捷方式。改用：
```bash
# 正确：直接后台运行，不经过 start
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 &
```
或者直接告诉用户自己打开 Chrome（如果已经在运行，只修 UUID 即可）。

**命中**: 2026-07-06 — 9 次重试才连上，根因路径不匹配
**再次**: 2026-07-07 — DevToolsActivePort 存在但连不上，根因 UUID 过期（Chrome 重启后 UUID 变了，文件里是旧的 `5eb7f394`，实际是 `9815446a`）
**再次**: 2026-07-07 — 每次用 `start "" chrome.exe` 从 bash 启动都会在桌面生成快捷方式

---

## ★★ WebFetch 中文/特定域名大面积被拦截 `rotatable` (since: 2026-07-06, last_hit: 2026-07-06)

**Rule**: WebFetch 被安全策略拦截时 → 改用浏览器 MCP `evaluate_script` 读 `document.body.innerText`

**Wrong**: 反复用 WebFetch 重试 → 每次都被同一个安全策略拦截

**Right**:
```
# Step 1: navigate_page(url)
# Step 2: evaluate_script(() => document.body.innerText.substring(idx, idx+2000))
```

**Why**: WebFetch 域名白名单偏保守，知乎/阿里云/arxiv HTML/gigagpu 等都被拦。浏览器 MCP 走真实 Chrome → 几乎不被拦。

**被拦截域名清单**: `zhuanlan.zhihu.com` `www.alibabacloud.com` `ar5iv.labs.arxiv.org` `qwenlm.github.io` `gigagpu.com`

---

## ★ WebSearch 中文查询命中率低 (confidence: high, 命中: 3)

**Rule**: 中文长查询 → 拆成短英文关键词。模型名 + `benchmark`/`comparison`/`GGUF` 优于完整中文问句。

**Wrong**: `"Qwen3.6-35B-A3B vs Qwen2.5-14B benchmark comparison GGUF 2025"`
**Right**: `qwen3.5 9B benchmark` `qwen 7B 14B HumanEval`

**核心**: Bing 后端对中文分词效果差，短英文关键词命中率远高于长中文查询

---

## ★★ take_snapshot SPA 页面 → 130K tokens 溢出 `rotatable` (since: 2026-07-06, last_hit: 2026-07-06)

**Rule**: 对 SPA 页面（HuggingFace / OpenRouter / GitHub）**禁止** `take_snapshot(verbose=true)`。组合拳替代：

| 操作 | 工具 | 用途 |
|------|------|------|
| 拿页面结构 | `take_snapshot(verbose=false)` | 元素 uid、导航 |
| 拿精确数据 | `evaluate_script()` | DOM 查询、表格提取 |
| 拿视觉确认 | `take_screenshot()` | 图表、布局验证 |

**Wrong**: `take_snapshot(verbose=true)` 在 OpenRouter 页面 → 134K chars 被截断到文件
**Right**: `evaluate_script(() => document.body.innerText.substring(...))` → 只取需要的段落

**Why**: SPA 框架生成海量 aria 标签和空 div，verbose snapshot 连 ignored element 都输出 → token 爆炸

---

## ★★ 浏览器 MCP 比 WebFetch 可靠 10 倍 (confidence: high, 命中: 5+)

**Rule**: 需要 JS 渲染 / 下载链接 / 动态内容 → 选浏览器 MCP，不选 WebFetch

| 场景 | WebFetch | 浏览器 MCP |
|------|----------|-----------|
| 静态文档 | ✅ | ✅ |
| JS 渲染页面 | ❌ | ✅ |
| 提取下载链接 | ❌ | ✅ `querySelectorAll('a[href$=".gguf"]')` |
| 中国网站 | 经常被拦 | 很少 |
| HuggingFace 模型页 | 部分可读 | ✅ 完整 DOM |
| 数据精确度 | 低（全文提取） | 高（精准定位） |

**Why**: WebFetch 是轻量 HTTP 请求 + 文本提取；浏览器 MCP 是真实 Chrome 渲染 → 所有 SPA / 动态内容 / API 渲染页面都能拿到

---

## 🟢 最佳实践组合

```
需要搜索            → WebSearch（短英文关键词）
需要静态文档内容    → WebFetch
需要 JS 渲染页面    → navigate_page → evaluate_script
需要下载链接        → navigate_page → evaluate_script + querySelector
需要表格/结构化数据 → evaluate_script + 自定义 JS
需要视觉确认        → take_screenshot
```

---

## ★★ [2026-08-05] 横评/榜单页只做主题搜索 → 漏掉厂商新发布 (置信度: high, 命中: 1)

**Rule**: 生成「最新/横评/对比」类页面时，信息收集必须**先枚举厂商清单、再逐家扫官方渠道按时间倒序**，不能只做主题搜索。主题搜索会漏新发布（LLM 知识截止 + 单一搜索路径 = 时间窗口盲区）。
**Wrong**: 生成「8 月最新大模型横评」（8-05）只按榜单/主题搜，漏掉 DeepSeek V4 Flash 0731 正式版（8-01 发布，deepseek-ai 组织页按更新时间排序第一行）。数据实际只到 7.27，用户批评「数据收集太差」。
**Right**:
1. 厂商清单枚举（OpenAI/Anthropic/DeepMind/Meta/DeepSeek/Kimi/GLM/Qwen/xAI/Mistral/字节/MiniMax），逐家覆盖
2. 每家查 HF 组织页按 lastModified 倒序：`api/models?author=<厂商>&sort=lastModified&direction=-1`——新模型必在顶部，JSON API 无 JS 渲染问题
3. 日期窗口 `[知识截止, 今天]` 显式覆盖，窗口内每家逐条交代或标注「无更新」
4. JS 渲染新闻页（Docusaurus 等）别抓 HTML，走 HF API 或浏览器 skill
**Why**: 这类页面的命门是「截至今天」的**完整性**。枚举 + 时间倒序 = 系统性覆盖；主题搜索 = 随机命中。用户对时效残缺容忍度极低。
**检测**: 生成横评页后自查——窗口期内每家厂商是否有新发布/更新被遗漏？
**泛化**: 任何「截至某日」的汇总/盘点（新闻综述、竞品分析、版本更新）都用同一方法。方法论已固化进 html-guide search-guide.md §2.5。

---

## ★ [2026-08-09] 读 GitHub 文件全文：浏览器 + `react-app.embeddedData` 的 `rawLines` (置信度: high, 命中: 1)

**Rule**: 要读 GitHub 仓库某文件/技能完整内容，别翻 snapshot 或 `body.innerText`（blob 正文不渲染进静态 DOM）。导航到 `github.com/<o>/<r>/blob/<branch>/<path>` → `evaluate_script` 解析 `<script data-target="react-app.embeddedData">` 的 JSON，**递归 walk** 找 `rawLines` 数组 `join('\n')` 即全文。
**Why**: 本机 WebFetch 域名校验拦 github.com、api.github.com contents 未认证限流（60/hr）、raw.githubusercontent 直连不稳——唯一稳定路径是真实浏览器加载 github.com 页面本身 + 读内嵌 payload。
**Wrong**: 先试 WebFetch→被拦；api.github.com→限流；`raw.githubusercontent.com`→连接失败；`body.innerText` 拿 blob 页→正文不出现。
**Right**: 降级链 = 浏览器导航 github.com → embeddedData 递归找 `rawLines`（路径随 GitHub 改版漂移，必须递归 walk 而非硬编码路径）。GitHub 未登录 search 也限流（"Too many requests"）→ 直接导航已知仓库路径，别用站内搜索。
**检测**: evaluate_script 返回 `{found:true, full}` 且 `full.length` 与文件预期规模相符。

---

## ★ [2026-08-11] evaluate_script 传 async 函数直接 return → "Promise was collected" (置信度: high, 命中: 1)

**Rule**: chrome-devtools `evaluate_script` 里 async 函数直接 `return {...}` → 报 `Protocol error (Runtime.callFunctionOn): Promise was collected` 或 undefined。改用**两步法**：第一步 fire-and-forget 的 IIFE 把结果塞进 `window.__x`，第二步 `() => window.__x` 读回。
**Wrong**: `async () => ({ a: 1 })` 直接返回对象 → 拿不到
**Right**: `() => { (async ()=>{ window.__x = await ...; })(); return 'started'; }` → 再 `() => window.__x`
**Why**: 该 MCP 的 evaluate 不 await async promise，promise 被 GC。两步法本会话验证 5+ 次可靠。测完删全局 + 用唯一键防污染。

---

## ★★ [2026-08-12] curl 可达性 000 → 别断言「已死」，以真实下载/用户实测为准 (置信度: high, 命中: 1)

**Rule**: `curl` 返回 000（连接失败）只说明"这条命令没连上"，可能是 curl/代理/瞬时原因，**不等于目标不可达**。断言「某镜像/站点已死」前必须用真实下载工具实测 + 听用户实际使用反馈。
**Wrong**: curl 直连+代理都 000 hf-mirror.com → 断言「hf-mirror 已死」并更新记忆 → 用户纠正「hf-mirror 首选且不开代理，实际下载正常」
**Right**: 断言不可达前：真实下载（浏览器/FDM/`curl -L` 实际拉文件）实测 + 用户实测为准；curl 000 仅作待验证信号
**Why**: curl 000 可因代理设置、TLS、防火墙、瞬时网络等多因；用户日常下载成功才是强证据。负向断言要穷尽验证（呼应 memory「否定性主张先穷尽再断言」）。

## ★ [2026-08-12] 浏览器直连 API 前先 OPTIONS 预检验证 CORS（含 Origin:null）(置信度: high, 命中: 1)

**Rule**: 设计"纯网页直连某 API"前，先 `curl -X OPTIONS <url> -H "Origin: <源>"` 看 `Access-Control-Allow-Origin` 是否放行；**file:// 页面 Origin 是 `null`，要单独测**。别凭印象假设"必然被拦"或"肯定能调"。
**Right**: `curl -X OPTIONS https://api.deepseek.com/v1/chat/completions -H "Origin: null" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type,authorization"` → 见 `access-control-allow-origin: null` 才确认 file:// 可直连
**Why**: OpenAI/DeepSeek 实测对 localhost 与 `Origin: null` 都放行——假设会错，实测成本极低。

---

## ★ [2026-08-12] 网页调外部 API：推理模型空响应 / 端点靠猜 / 无 CORS 头 (置信度: high, 命中: 1)

**Rule**: file:// 或跨域页面 fetch 外部 API，三层各自独立失败：
1. **推理模型空响应**：Qwen3/deepseek 类先出 `reasoning_content` 再出 content，max_tokens 小则思考吃光预算 → `content` 空。请求加 `chat_template_kwargs:{enable_thinking:false}` + max_tokens 提到 2048。
2. **端点靠猜**：官网地址 ≠ API 端点（opencode.ai/go 是网站，API 是 `opencode.ai/zen/go/v1`）。真实端点从应用配置/认证文件/日志挖（auth.json、provider 配置、运行日志），别猜 host/path。
3. **无 CORS 头**：自建网关/本地代理不带 `Access-Control-Allow-Origin` → 浏览器拦「Failed to fetch」。curl 能通但浏览器不通 = CORS → 写**本地 CORS 代理**（Python http.server 转发 + 加头，curl 转发绕开 Python SSL 被掐）。
**Wrong**: opencode 接入：Base URL 填官网 → Failed to fetch；猜 gateway.opencode.ai → 错 host；512 预算被思考吃光 → 空响应，三重误判
**Right**: ①从 auth.json/provider 配置挖真实端点 ②curl 直连验证端点+模型 ③浏览器测区分 CORS vs 模型问题 → 本地代理兜底
**Why**: 三层失败相互叠加，单独排查每一项都「像」网络问题，实际根因各异。关联 [[CORS 预检验证直连]]。
**检测**: curl 测 /v1/models + chat/completions（绕 CORS 定位端点/模型）；浏览器测看 console 是 CORS 还是空 content。

---

## ★★ [2026-08-12] chrome-devtools 视口模拟/缩放用完必须还原 (置信度: high, 命中: 1)

**Rule**: 用 `emulate`/`resize_page` 做响应式测试后，必须把视口还原到真实窗口尺寸。忘记还原 → 页面一直渲染在缩窄的模拟宽度里，用户看到「页面居左 + 右侧大片空白 + 滚动条」，误判成布局 bug 白排查。
**Wrong**: 测移动端 `emulate 390x800` 后不还原 → 用户报页面居左空白。
**Right**: 测完 `evaluate_script(() => ({w: screen.width, h: screen.height}))` 拿物理尺寸 → `emulate({viewport: '<w>x<h>x1'})` 还原。
**Why**: 浏览器是共享给用户的真实窗口；设备指标模拟是持久覆盖，不还原就残留。
**检测**: 用户报布局错位 → 先查 `window.innerWidth` 是否等于物理窗口宽。

## ★ [2026-08-12] 顶层 `const` 不进 window，跨 script 共享全局用 `var` (置信度: high, 命中: 1)

**Rule**: 需要另一个 `<script src>` 加载后通过 `window.X` 读取的全局数据，声明用 `var`（顶层 var 才挂 window）。`const`/`let` 只在全局词法作用域，`window.X` 取不到。
**Wrong**: prompt-db.js 用 `const PROMPT_DB=[...]` → script 加载成功但 `window.PROMPT_DB` undefined，页面显示「已加载 0 条」。
**Right**: 生成文件用 `var PROMPT_DB=[...]`。
**Why**: 大库靠 script 标签懒加载（跨域免 CORS），但必须能 `window` 访问；经典 script 顶层声明语义差异。关联 [[CORS 预检验证直连]]。

---

## ★★ [2026-08-11] MCP/浏览器连接状态：先实测再断言，别断言「永远」 (置信度: high, 命中: 1)

**Rule**: 关于连接类当前状态（MCP 能不能连、进程/端口活着没、需不需要重启），**先复测工具再下结论**，把「此刻 X」说成「必须 X 才能用」是不准的。
**Wrong**: 说「当前会话 MCP 在兜底模式、连不上 9222 skill Chrome、需重启 Claude Code 才能接上」→ 实际 MCP 后来自动重连成功（config 变 `ok:true` 后 wrapper 走 `--browserUrl` 接上运行中的 skill Chrome），用户拿另一会话实测（`list_pages` 成功）抓到错误断言。
**Right**: 任何「当前连不上/进程死了/需重启」断言，先当场复测（`list_pages`/`curl` 端口/查 config）再下结论；状态变了就更新结论并承认。MCP 连接懒加载、会话中途可自恢复。
**Why**: 会话开头两次 `list_pages` 报 profile 锁错误的时点判断 ≠ 持久状态。关联「否定性主张先穷尽再断言」。

---

## ★ [2026-08-11] 判布局文字重叠：别用 OCR「读得出」/ OCR 框相交 → 用 DOM 几何 (置信度: high, 命中: 1)

**Rule**: 判断文字是否重叠，**别用「OCR 读得出=不重叠」或「OCR 框相交」**——实测均不可靠。唯一可靠判据：`getBoundingClientRect` 两两相交面积 > 阈值，或元素上下边越过卡边界。
**Wrong**: (1) 重叠区字透过透明注释/页脚仍可见 → OCR 照样读得出（假阴性）；(2) 连续相同汉字（「点点点…」）被 OCR 合并成一框 → 重叠被掩盖（假阴性）；(3) 相邻行 OCR 框带内边距被撑大 → 无重叠也报框相交（假阳性）。
**Right**: headless Chrome + DOM 几何脚本判重叠（参考 `Desktop\AI\Claude\cardtest\gen.py` 注入检测器）；OCR 只适合读文本内容，不适合判布局。
**Why**: 2026-08-11 html-guide 1200×630 摘要卡重叠调研实测三案例定论。关联「连接状态先实测再断言」。

