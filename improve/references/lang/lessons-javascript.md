# JavaScript / TypeScript Lessons

> 加载条件: .js, .ts, .tsx, .jsx, .mjs, .cjs, node, npm, package.json, react, vue, next, 用户说"JavaScript" "TypeScript" "JS" "TS"

---

## #async — 异步陷阱

### ★★ Promise 不 await 不 return → 静默丢失 (置信度: high, 命中: 2)

**Rule**: async 函数内每个 Promise 必须被 `await` / `return` / `Promise.all()` 之一消费
**Wrong**: `async function fn() { doAsync(); return "done"; }` — `doAsync()` 返回的 Promise 无人等待，错误被静默吞掉
**Right**: `await doAsync()` 或 `const p = doAsync(); ...; await p;` 或 `return doAsync()`（调用方 await）
**Why**: 无 await 的 Promise 继续执行但错误无人捕获 → `UnhandledPromiseRejectionWarning` → Node 15+ 进程退出。

### ★★ forEach + async → 并发非预期 (置信度: high, 命中: 2)

**Rule**: `Array.forEach(async () => ...)` 是 fire-and-forget，不等待任何回调完成
**Wrong**: `[1,2,3].forEach(async (id) => { await save(id); }); console.log("done")` — "done" 先于所有 save 打印
**Right**: `for (const id of [1,2,3]) { await save(id); }` 顺序执行 或 `await Promise.all(ids.map(save))` 并发
**Why**: `forEach` 忽略回调返回值（包括 Promise），不等待。`for-of` + `await` 正确处理。

### ★ Promise.all 短路 → 一个 reject 全部失败 (置信度: medium, 命中: 1)

**Rule**: 需部分容错用 `Promise.allSettled()`。需快速成功用 `Promise.any()`。只有全部必须成功才用 `Promise.all()`。
**Wrong**: `await Promise.all([a(), b(), c()])` — a 和 c 成功但 b 失败 → 全部抛异常，a/c 的结果丢弃
**Right**: 允许部分失败 → `Promise.allSettled()` → 检查 `.status` 分别处理

### ★ async 函数返回值是 Promise → 漏 await (置信度: medium, 命中: 1)

**Rule**: `async function` 总是返回 Promise。非 async 调用者得到的是 Promise 不是值。
**Wrong**: `const user = getUser(id); user.name` → `undefined` — user 是 `Promise<User>`，name 访问在 fulfilled 之前
**Right**: `const user = await getUser(id); user.name`

---

## #error — 错误处理陷阱

### ★★ 全局 Promise rejection 未处理 → 进程 crash (置信度: high, 命中: 2)

**Rule**: 所有 Promise 链必须 `.catch()` 或 try-catch await。Express/Koa 中间件 async 错误必须传 next。
**Wrong**: `app.get('/api', async (req, res) => { const data = await risky(); res.json(data); })` — rejection → 请求永远不响应 + 内存泄漏
**Right**: Express 5+: `app.get('/api', asyncHandler(async (req, res) => { ... }))` 或显式 `try/catch` + `next(err)`
**Why**: Express 4.x 不会自动捕获 async 中间件的 rejection。Express 5+ 已修复但仍推荐显式处理。

### ★ JSON.parse / 外部数据无 try-catch → 崩溃 (置信度: medium, 命中: 1)

**Rule**: 任何外部数据（API 响应、localStorage、URL params）的 `JSON.parse()` 必须包 try-catch。
**Why**: 损坏的 localStorage / 中间人篡改的响应 / 用户手动改 URL → 语法错误 → 整页白屏。

---

## #loop — 循环陷阱

### ★★ var 循环引用 → 闭包捕获最后值 (置信度: high, 命中: 2)

**Rule**: 循环创建闭包永远用 `let`（块作用域）。`var` 提升到函数作用域 — 所有闭包共享同一个变量。
**Wrong**: `for (var i = 0; i < 3; i++) { setTimeout(() => console.log(i), 100); }` → 打印 "3 3 3"
**Right**: `for (let i = 0; i < 3; i++) { ... }` → 每次迭代新绑定 → 打印 "0 1 2"
**Why**: `var` = 函数作用域，整个循环只有一个 `i`。`let` = 块作用域，每次迭代创建新绑定。

### ★ for-in 枚举原型链 → 意外属性 (置信度: medium, 命中: 1)

**Rule**: 遍历对象属性用 `for (const [k, v] of Object.entries(obj))` 或 `Object.keys()`。不直接用 `for-in`。
**Wrong**: `for (const k in obj) { ... }` — 遍历到 `toString` `hasOwnProperty` 等原型属性（库可能 pollute 了原型）
**Right**: `for (const k of Object.keys(obj))` 或加 `hasOwnProperty` guard
**Why**: `for-in` 遍历整条原型链。别人（或 polyfill）往 `Object.prototype` 加的属性也会被遍历到。

---

## #type — TypeScript 类型陷阱

### ★★ any 传染 → 类型检查静默失效 (置信度: high, 命中: 2)

**Rule**: tsconfig `strict: true` + `noImplicitAny: true`。禁止 `as any`（除非 FFI/边界）。
**Wrong**: `(data as any).name` → `name` 是 `any` → 下一行也用 `any` → 整条链无检查
**Right**: 写 type guard `function isUser(x: unknown): x is User { ... }` → `if (isUser(data)) { data.name }`
**Why**: `any` = 退出类型系统。一个人的 `as any` 传染整个调用栈。

### ★ 严格模式下 null/undefined 未处理 (置信度: medium, 命中: 1)

**Rule**: `strictNullChecks: true` 下，nullable 类型不能直接 `.` 访问。
**Right**: optional chaining `obj?.prop?.nested` + nullish coalescing `value ?? defaultValue`
**Why**: `?.` 和 `??` 是 TS/ES2020 最佳实践，比 `&&` 链更安全（`&&` 遇到 `0`/`""` 会短路）。

---

## #security — 安全陷阱

### ★★★ innerHTML / dangerouslySetInnerHTML → XSS (置信度: high, 命中: 3)

**Rule**: 不对不可信内容使用 `innerHTML` / `insertAdjacentHTML` / React `dangerouslySetInnerHTML`。用 `textContent` 或经过 DOMPurify 净化。
**Wrong**: `div.innerHTML = userComment` / `<div dangerouslySetInnerHTML={{__html: apiResponse}} />`
**Right**: `div.textContent = userComment` 或用 `DOMPurify.sanitize(richContent, {ALLOWED_TAGS: ['b','i']})`
**Why**: XSS (CWE-79) 在 CWE Top 25 中排名靠前。innerHTML 执行 `<script>` 和 `onerror`/`onload` 等事件处理器。

### ★★ eval() / new Function() / setTimeout(string) → 代码注入 (置信度: high, 命中: 2)

**Rule**: 永远不对用户输入使用 `eval()` `new Function()` 或字符串版 `setTimeout`/`setInterval`。
**Wrong**: `eval('(' + jsonpResponse + ')')` / `setTimeout("doThing(" + userInput + ")", 100)`
**Right**: `JSON.parse(response)` / `setTimeout(() => doThing(input), 100)`
**Why**: eval = 任意代码执行。即使用于"解析" JSONP 也是危险的。

### ★★ prototype pollution → 全局注入 (置信度: high, 命中: 2)

**Rule**: 避免不安全的深度合并/深拷贝（`for-in` + 赋值到 `__proto__`）。用 `Object.create(null)` 做纯字典。
**Wrong**: `function merge(a, b) { for (let k in b) { a[k] = b[k] } }` + `merge({}, JSON.parse(userData))`
→ `{"__proto__": {"isAdmin": true}}` → 所有对象继承 `isAdmin: true`
**Right**: `Object.freeze(Object.prototype)` / 用 lodash `_.merge` 或 structured clone / 校验 key 不含 `__proto__` / `constructor` / `prototype`
**Why**: 2018-2024 年大量 npm 包（lodash、jQuery、mongoose）被爆 prototype pollution CVEs。O(N²) 的 package 审查成本。
**检测**: `Object.prototype.isAdmin` → 检查是否被意外污染。

### ★★ SSR Hydration 不匹配 → 空白页面 (置信度: medium, 命中: 2)

**Rule**: SSR/SSG 框架（Next.js/Nuxt）: 服务端和客户端渲染结果必须一致。不一致 = hydration mismatch → 页面空白或布局错乱。
**Wrong**: 服务端渲染 `<div>{Date.now()}</div>` → 客户端 hydration 时值不同 → React 重新渲染整棵树
**Right**: `useEffect` 包裹浏览器专用代码（`window` `localStorage` `Date`）。动态值用 `suppressHydrationWarning`。
**Why**: React 18+ hydration 对 mismatch 零容忍。不符合 = 性能降级（整棵组件树客户端重渲染）≠ 优雅降级。

### ★ CORS 配置 fetch mode: 'no-cors' → 静默吞数据 (置信度: medium, 命中: 1)

**Rule**: `fetch(url, {mode: 'no-cors'})` 返回 "opaque response" — 无法读 body/headers/status。几乎永远不是你要的。
**Wrong**: `const res = await fetch(apiUrl, {mode: 'no-cors'}); const data = await res.json()` → `data` 为空
**Right**: 后端加 CORS header / 用 proxy / 不要 no-cors
**Why**: no-cors 允许请求发出但禁止 JS 读响应 = 静默返回空数据。最常见于新手 debug CORS 时的错误尝试。

---

## #io — 文件/网络陷阱

### ★ fs.readFile 不用 stream → 大文件 OOM (置信度: medium, 命中: 1)

**Rule**: >100MB 文件用 `fs.createReadStream()` + pipe，不 `fs.readFileSync()` / `fs.readFile()` 全量加载。
**Wrong**: `const buf = fs.readFileSync('2GB.dat')` → 2GB Buffer → OOM
**Right**: `fs.createReadStream('2GB.dat').pipe(transform).pipe(fs.createWriteStream('out.dat'))`

### ★ fetch 缺超时 → 永久挂起 (置信度: medium, 命中: 1)

**Rule**: `fetch()` 没有内置超时。用 `AbortController.signal` + `setTimeout` 模拟。
**Wrong**: `await fetch(url)` — 服务器不响应 → 永远不 resolve
**Right**: `const ctrl = new AbortController(); setTimeout(() => ctrl.abort(), 10000); await fetch(url, {signal: ctrl.signal});`
**Why**: fetch spec 故意不设默认超时。网络请求必须有 timeout，否则阻塞整个 async 流程。

---

## #string — 字符串处理陷阱

### ★ [2026-08-05] Edit old_string 含 \uXXXX 字面量 → 不匹配 (置信度: high, 命中: 1)

**Rule**: 编辑含 `\uXXXX` 转义**字面量**的 JS（编译产物里 `'│'` 就是字面 backslash+u2502，不是实际字符）时，Edit 参数按 JSON 解析会把 `│` 解码成实际字符 `│` → old_string 不匹配（工具自动尝试 `\uXXXX`↔字符两种形式仍失败）。
**Wrong**: `old_string: "return parts.join(' │ ');"` 想匹配文件里的 `return parts.join(' │ ');` → not found。
**Right**: old_string 写文件实际内容 `\\u2502`（JSON 层转义 → 匹配到字面 backslash-u-2502）；new_string 可用实际字符。
**Why**: 编译后 dist JS 常用 `\uXXXX` 表示特殊字符（如 `│`、分隔符）；Edit 参数走 JSON 序列化，`\u` 被当转义。遇到不匹配先看目标行是否含 `\u` 字面量。

### ★★★ 含 ANSI/标记的字符串长度检查 → 截断错误 (置信度: high, 命中: 1)

**Rule**: 含 ANSI 转义序列/HTML 标签/Markdown 标记的字符串，长度检查和截断必须在**剥离格式代码后的 visible text** 上执行，不能用 `string.length`
**Wrong**: `if (ansiLabel.length > 50) return ansiLabel.slice(0, 47) + '...'` — ANSI 码 ~70 字符但不占显示宽度，截断位置在格式码内 → 显示 "余额 ¥16.25 |..."
**Right**: 先 `stripAnsi(str)` 得 visible length → 判断是否需要截断 → 如需截断，按 visible 索引映射回原始字符串 → 追加 `...` 后补 ANSI reset
**Why**: `\x1b[94m` 占 7 个 `string.length` 但终端显示宽度为 0。富文本同理（`<b>bold</b>` 6 个 raw chars 但 visible 只有 4）。`MAX_LENGTH=50` 对 117-char ANSI 字符串在 `|` 处截断 → 用户只看到 `余额 ¥16 | ...` 缺失消费信息。
**Where**: 2026-07-05 balance-hud v2.0.0 `sanitizeBalanceLabel()` — `MAX_BALANCE_LABEL_LENGTH=50` 但 balance_label 含 ~70 chars ANSI 码 → 消费信息被 `...` 替换，用户 3 天未定位。
**Fix**: `MAX_BALANCE_LABEL_LENGTH` 50 → 512（临时）；根本修复应为 `stripAnsi()` 后按 visible length 截断。


---

## #dom — DOM 运行时陷阱

### ★★ HTML/JS 模板依赖运行时 JS 的功能会静默失效 (置信度: high, 命中: 1)

**Rule**: 生成含运行时 JS 的 HTML 页面时，交互功能（高亮/目录/复制/Tab）**必须无头渲染验证**，不能只查源码里有没有类名。JS 一个静默报错 = 后续所有功能全部失效且无报错。
**Wrong**:
- 用 `element.innerText` 读代码内容 → `innerText` 依赖布局，`--dump-dom` 等未渲染场景返回空 → 高亮零输出
- 用 `querySelector("#" + a.hash.slice(1))` 反查中文 id 标题 → `a.hash` 对非 ASCII 返回 percent-encode（`#示例`→`#%E7%A4%BA%E4%BE%8B`）→ `querySelector` 抛 `SyntaxError` → 目录 JS 中断，**它后面的高亮/复制/Tab/过滤全部不执行**
- 校验脚本 `grep "tok-"` 匹配到的是 CSS/JS 里的类名定义，不是真实渲染的 span → 假阳性通过
**Right**:
- 读元素文本用 `textContent`（布局无关）；目录滚动高亮直接保存元素引用，不用 id 反查
- 校验：headless Chrome `--dump-dom` 渲染后 `grep 'class="tok-'` 数真实 span 数量
- `position:sticky` 在大页面会无规律失效（fixed 却正常）→ 用 scroll 监听转 `fixed` 兜底
**Why**: 一个 `querySelector` 的 SyntaxError 让整页语法高亮+复制+Tabs 全灭，4 轮评测用户连续两轮反馈"无语法高亮"才定位到根因——JS 静默失败没有错误提示，只能靠渲染验证兜底。
**Where**: 2026-08 html-guide skill 骨架 — `it.a.hash` 中文 id percent-encode 导致 buildToc 抛错，高亮/复制/Tab 全部未跑（评测迭代 2→3 修复）。
**Fix**: `textContent` 替代 `innerText`；目录存元素引用替代 querySelector 反查；SKILL.md 内置 headless 验证步骤。

---

## ★★ [2026-08-11] 展示/匹配共用展示层解析链，别自建更窄查询 (置信度: high, 命中: 2)

**Rule**: 界面要显示/匹配的值（本地化/中文/覆盖显示名）应从**实际渲染/解析该值的地方**取，别从原始数据集反查，别自建更窄的并行查询。所有查询入口必须共用同一解析函数，否则分叉。
**Wrong**: ① ★收藏 用 `fullMap.has(en)?fullMap[1]:en`，分类用 `CURATED_ZH[en] || fullMap[1] || en` → 只在 CURATED_ZH 的词（masterpiece）在收藏里中文消失。② v2.4.0 回填识别第一版只查 `fullMap` → "breast fondling"（收藏词、只在 CURATED_ZH）被识别成 raw。
**Right**: 统一多层解析链：CURATED_ZH > FULL_TAGS/fullMap > 收藏(favZh)；键做下划线↔空格归一化；构建一次 `matchMap` 供所有匹配入口复用。
**Why**: 展示层有覆盖/精选逻辑，原始数据查不到 = 分叉。同一词两种存法（`best_quality`/`best quality`）不归一也失配。**新增任何识别/匹配逻辑，先找已有解析函数复用，别自建更窄的查询**。
**Where**: 2026-08-11 Danbooru 标签超市 — ①收藏中文缺失 ②回填识别漏 CURATED_ZH 词。修复：favZhMap/favZh 统一解析 + matchMap。

---

## ★ [2026-08-11] File System Access API 不暴露真实路径：无 path/getParent，目录句柄只能 showDirectoryPicker 取 (置信度: high, 命中: 1)

**Rule**: 浏览器拿不到文件/文件夹的绝对路径（含盘符）——`File`/`FileSystemFileHandle`/`FileSystemDirectoryHandle` 原型均无 `path`，`getParent()` 未实现。要实现「重选从上次位置开始」，唯一方案是存**目录句柄** + `showDirectoryPicker({startIn: lastDirHandle})`；路径展示只能给 `dirHandle.name + ' / ' + fileName`。
**Wrong**: 假设能 `favHandle.getParent()` 或 `file.path` 拿到带盘符路径 → Chrome 实测 `File.prototype` 无 path、两个 handle 原型均无 getParent。
**Right**: 自动保存改目录句柄模式：`showDirectoryPicker` 选文件夹 → 文件固定 `dtag_fav.json`（`getFileHandle(name,{create:true})`）→ 存 dirHandle，重选时 `startIn: dirHandle`；路径显示「文件夹名 / 文件名」。盘符只能用户手动填。
**Why**: File System Access API 安全模型故意隐藏绝对路径，parent 访问在 Chrome 未实现。用户要求「显示完整路径含盘符」时先测原型再定方案，别假设 API 提供。
**Where**: 2026-08-11 标签超市 v2.5.0 自动保存增强。实测：`FileSystemFileHandle.prototype` = [createWritable,getFile,move]，目录 handle 无 getParent。

---

## #html — HTML 单页陷阱

### ★★ [2026-08-14] Write/Edit 内容里的 `\x00` 转义落盘为真实 NUL 字节 → 文件变 binary (置信度: high, 命中: 1)

**Rule**: 用 Write/Edit 写源码时，内容里任何 `\x00`/` ` 反斜杠转义会被工具按 JSON 语义解码成真实控制字节写进文件 → 文件被 Grep 识别为 binary、Edit/Grep 全部失效、node/python 解析报 "cannot contain null bytes"。
**Wrong**: 用 NUL 做 markdown code-block 占位符（`'\x00' + i + '\x00'`）→ 写完文件里 3 个真实 NUL，后续 python 脚本也被污染。
**Right**: 占位符/分隔符一律用纯 ASCII token（如 `@@MD0@@`），正则 `/^@@MD\d+@@$/` 匹配；不要用任何控制字符。
**Why**: 工具参数走 JSON 序列化，`\x00` 是合法转义 → 落盘即真实 NUL。教训同 [2026-08-05] Edit old_string 含 `\uXXXX`（同类：反斜杠转义在工具层的解析）。

### ★ [2026-08-14] input[type=number] 的 step 校验从 min 起步 → 默认值可能 invalid (置信度: high, 命中: 1)

**Rule**: number input 合法值 = `min + k*step`（k≥0）。设 `min=-1` + `step=16` + `value=1024` → (1024-(-1)) 不整除 16 → `validity.valid=false`，a11y 显示 `invalid="true"`。想让用户任意手动输入：`step="any"`。
**Wrong**: min="-1"（允许 -1 表示"不限"）配默认值 → 默认值被判 invalid。
**Right**: `step="any"` 保留任意输入（含负值），或调整 min 使默认值对齐 step。
**Where**: 2026-08-14 llama-chat-ui 参数面板 max_tokens/repeat_last_n。

### ★★ [2026-08-14] OpenAI 兼容 baseUrl 拼接：用户填 /v1 后缀 + 代码再拼 /v1/chat/completions → 404 (置信度: high, 命中: 1)

**Rule**: 任何 OpenAI 兼容前端，baseUrl 语义要兼容「服务根」或「已带 /v1 后缀」两种填法。请求路径必须经规范化函数：`apiRoot = baseUrl.replace(/\/v1$/i, '')`，再拼 `/v1/chat/completions`、`/health`。
**Wrong**: `fetch(baseUrl + '/v1/chat/completions')` + 用户填 `http://host:<端口>/v1` → `/v1/v1/chat/completions` → 404 "File Not Found"，assistant 回复空。
**Right**: 统一 apiRoot() strip 尾部 `/v1`（health 同样走 apiRoot），用户填不带 /v1 也不出错。
**Where**: 2026-08-14 llama-chat-ui 真机联调（Qwen3.5 @<端口>），用户 baseUrl 填了 `/v1` 后缀。
