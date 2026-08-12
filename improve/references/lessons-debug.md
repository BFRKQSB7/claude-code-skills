# Debug / Diagnose

> 加载条件: 任务涉及 debug, diagnose, bug, 调试, 诊断, 循环, 复现, diff/compare/对比, 行尾/换行符/CRLF

---

## ★ [2026-06-16] 无反馈循环就开修 → 瞎猜 (置信度: high, 命中: 1)

**Rule**: Bug 修复第一步 = 构建快速、确定性的 agent 可运行的 pass/fail 信号
**Wrong**: 看代码 → 凭经验猜根因 → 直接改 → 改完等用户反馈
**Right**: 10 种方法构建循环（详见 [diagnose-loop.md](diagnose-loop.md)）→ 复现 → 假设 → 插桩 → 修复 → 回归
**Why**: 没有循环 = 不知道是否修好了。2 秒确定性循环是调试超能力。30 秒 flaky 循环 ≈ 没有。
**来源**: Matt Pocock `diagnose` Phase 1
**泛化**: 任何调试任务第一步永远是构建反馈循环，不分语言/框架/领域

---

## ★★ [2026-06-16] 调试日志无标记 → 清理遗漏 (置信度: medium, 命中: 2)

**Rule**: 每条临时调试日志打唯一前缀标签 `[DEBUG-xxxx]`，修完 `grep` 前缀全删
**Wrong**: `console.log("here"); console.log("value:", x);` — 修完不知道哪些该删
**Right**: `console.log("[DEBUG-a4f2] Order state:", state);` — `grep -r "\[DEBUG-a4f2\]"` 一键查
**Why**: 无标签的调试日志混入生产日志，下次 debug 误判。标签 = 免清理焦虑。
**来源**: 2026-06-15 原始教训（#state）迁移至此 domain
**泛化**: 任何临时 instrumentation（断点/日志/注入）都标记 + 修完清理

---

## ★ [2026-07-30] 工具服务正常但模型不调用 → 先查模型工具模式与 Provider 协议 (置信度: high, 命中: 1)

**场景**: MCP 服务成功初始化、catalog 能列出工具，但模型声称工具不可用，Computer Use 无法启动。
**根因**: 模型目录将目标模型标为 `code_mode_only`；Codex 将工具封装为 `additional_tools` 中的 custom `exec`，而 custom Provider／上游模型没有实际发出 `exec` custom tool call。传统工具模式模型在同一 Provider 下可直接调用 MCP。
**修复**: 先用 `codex debug models` 检查 `tool_mode`，再做单变量模型 A/B；要求真实 tool call 并检查工具结果。若兼容模型成功，切换模型或修复 Provider 的 custom-tool 协议，不清缓存、不盲改 feature flag。
**泛化**: “工具 catalog 存在”只证明宿主发现工具；模型能否调用取决于最终请求形态、模型能力声明和 Provider 对协议的完整实现。验证层级必须是：服务初始化 → 请求中声明工具 → 模型发出 call → 宿主调度 → 工具结果回传。

---

## ★ [2026-07-30] 配置 feature 名仍可写但已 removed → 修改无效 (置信度: high, 命中: 1)

**Rule**: 修改 feature flag 前先运行产品自带的 feature 列表或 schema 检查，确认状态不是 `removed`/`deprecated`。
**Wrong**: 看到 `js_repl = false` 就直接改成 `true`，把相关性当根因。
**Right**: 运行 `codex features list`；若该 flag 已 `removed`，转查当前实现采用的 MCP/模型工具路由。
**Why**: 兼容解析器可能继续接受旧键，但运行时不再读取它；配置 diff 看似正确，行为却完全不变。

---

## ★ [2026-06-16] 单假设锚定 → 忽略其他根因 (置信度: medium, 命中: 2)

**Rule**: 生成 3-5 个排序假设后再测试，不可只拿一个就扎进去
**Wrong**: 第一个 plausible 想法 → 立刻追 → 追错方向
**Right**: 3-5 个可证伪假设（"If X is cause, changing Y makes bug disappear"）→ 排序 → 给用户看 → 再测试
**Why**: 单假设 = 锚定效应。多种可能 root cause 被忽略。用户常有领域知识一秒重排序。
**来源**: Matt Pocock `diagnose` Phase 3
**泛化**: 任何故障排除。先列可能原因，排优先级，再动手。
**再次**: 2026-08-11 — 标签工具自动保存调试，先锚定 "DataCloneError 挂起" 理论，测试只部分成立；真正根因是跨测试残留状态（IndexedDB 里的旧句柄）。靠逐步插桩日志（每步 log）才定位。

---

## ★ [2026-08-01] 网络失败先验代理端口存活，再判网络故障 (置信度: high, 命中: 1)

**场景**: `git clone` / `gh repo clone` 报 `Failed to connect to github.com port 443 via 127.0.0.1: Could not connect to server`
**根因**: `git config --global http.proxy` 指向已停止的本地代理端口 (<旧代理端口>)，实际 <存活端口> 存活且直连可通 (curl 200)
**修复**: `netstat -ano | grep LISTENING | grep 127.0.0.1:789x` 找存活端口 → `curl -x http://127.0.0.1:<port> https://api.github.com` 验活 → `git -c http.proxy=http://127.0.0.1:<port> clone ...`；同时测直连 `curl -s -o /dev/null -w "%{http_code}" https://api.github.com`
**Why**: Windows 本地代理/VPN 工具端口会变（重启后占新端口），全局 git 代理配置陈旧；gh CLI 走 `HTTPS_PROXY` env，git 走 `http.proxy` config，两套不共享
**泛化**: 任何"通过代理的网络操作失败"：第一步验证代理端口是否真活 + 试直连，再谈网络故障。测出存活端口后临时 `-c` 覆盖比改全局配置更安全。

---

## ★ [2026-08-06] 模拟 stdin-payload 子进程用 spawnSync({input})，不用 shell 管道 (置信度: high, 命中: 1)

**Rule**: 模拟"从 stdin 读 JSON payload"的 CLI 子进程（如 Claude Code statusline），用 `spawnSync(proc, [script], { input: payload })` 交付 payload，不要 `printf payload | node script`。
**Wrong**: `printf '{json}' | node dist/index.js` → `readStdin()` 判为无 stdin → 走"正在初始化..."分支输出误导信息，让人误以为渲染失败，白查 5-10 分钟。
**Right**: 参照 `scripts/hud_debug.mjs` 的 `simulateRender()` — `spawnSync(process.execPath, [dist/index.js], { input: payload, encoding: 'utf8', env, timeout })`。渲染前先确认 stdout 含真实 ANSI 码（`grep -c $'\x1b\[97m' raw`），不要先经 `cat -v` 再 grep（`\x1b` 会被转成 `^[` 永远匹配不到）。
**Why**: 子进程对 stdin 的 EOF/读取方式敏感；spawnSync `input` 由父进程直接写 fd，shell 管道经转发行为不同。误判输出会浪费验证时间。
**检测**: 模拟渲染输出 `正在初始化...`/`Initializing...` = 走错分支，改用 spawnSync input；`cat -v` 后 grep 原始 ANSI 码为 0 = 先别信，直接 grep raw 文件。

---

## ★★ [2026-08-01] 比较文件树"全部文件不同"/diff 差异行数巨大 → 先查行尾 (置信度: high, 命中: 2) (再次: 2026-08-09)

**场景**: (1) 比较 Windows 上 zip 解压的插件与 git clone 的同一项目，`diff -rq` 与逐文件 diff 均显示"所有文件都不同"；(2) 本地 skill 目录 vs 备份仓逐文件 diff 显示每文件 320-980 行差异，实则内容一致
**根因**: CRLF vs LF 行尾差异 — PowerShell `Expand-Archive` 保留 CRLF，git clone + `core.autocrlf` 产生 LF；`diff` 把每行都当不同。**diff 差异行数巨大（数百行级）本身就是换行符漂移的强信号**
**修复**: `cat -A file` / `file file` 查行尾 → `diff --strip-trailing-cr file1 file2` 先排除行尾，再判内容；内容级判断用 `git diff --stat` 或按行尾剥离后对比
**Why**: Windows 文件系统无行尾语义，同一源码不同落地方式（zip / clone / 备份仓同步 / 编辑器）可产生两种行尾；"全部不同"或"全文件数百行 diff"都可能是行尾漂移，误判"内容分叉"会白费排查
**泛化**: 比较两个文件树时，先排除行尾差异再看内容。差异行数巨大 → 优先怀疑行尾而非内容。

---

## ★ [2026-08-01] 实现"加功能"前先实测当前行为 → 缺口常在边界 (置信度: high, 命中: 1)

**场景**: 用户请求"升级 X 让功能在 Y 场景下可用"，假设当前完全不支持
**现象**: 实测发现主路径已支持（沙箱模拟 stdin + 无余额快照 → HUD 正常渲染、余额行自动隐藏），真正缺口在边界：daemon 无 key 分支不清残留快照、杀旧进程
**根因**: 凭代码阅读假设"不支持"，未先构建最小环境验证当前行为
**修复**: 复制 repo 到沙箱 → 构造最简输入实测当前行为 → 确认主路径已满足 → 只修边界缺口（本会话：no-keys 分支 acquireLock + 清快照）
**Why**: "加功能"≠"主路径缺功能"。已实现 90% 时，修边界缺口比重写主路径风险低得多
**泛化**: 任何"让 X 在 Y 下可用"的请求，第一步是实测 Y 场景当前行为，输出"已满足 + 真正缺口"清单，再动手。

---

## ★ [2026-08-11] 页面测试残留状态跨 evaluate 调用 → 假失败 (置信度: high, 命中: 1)

**Rule**: 同一页面多次 `evaluate_script` 时，localStorage / IndexedDB / 全局变量**跨调用持久**。测试前必须显式重置目标状态，失败先怀疑残留污染。
**Wrong**: 前次测试把 mock 句柄存进 IndexedDB + localStorage 设 autoSaveOn → 下次运行时 favHandle 是空对象（truthy 无方法）→ 跳过选文件、方法不被调用、开关行为反转，全被误判成真 bug，白调试多轮。
**Right**: 测试前置状态（清 localStorage 相关键 + IndexedDB + 相关全局变量），测完还原；现象"方法没被调 / 开关反转 / 写入为空" → 先查残留。
**Why**: 浏览器页面状态比想象持久得多。调试时先隔离"干净环境"再谈代码逻辑。

---

## ★ [2026-08-11] LF 行尾 .bat + UTF-8 多字节字符 → cmd 误解析执行碎片 (置信度: high, 命中: 1)

**Rule**: Windows `.bat`/`.cmd` 用 CRLF 行尾 + 纯 ASCII。LF 行尾文件里出现 UTF-8 多字节字符（em-dash `—` 等）→ cmd 批处理解析器把字符后的换行认错，把某字母碎片当命令执行，报 `'m' 不是内部或外部命令` 之类假错（stderr，功能不受影响）。
**Wrong**: login.bat 是 LF 行尾、注释含 em-dash `—` → 双击快捷方式跑登录时 stderr 报两次 `'m' 不是内部或外部命令`
**Right**: 写/改 .bat 后查行尾与字符集：LF + 非 ASCII → 转 CRLF + 多字节换 ASCII（`—`→`--`）。PowerShell `.ps1` 无此问题（不走 cmd 批处理解析器）。
**检测**: `python` 数 `\r\n`/`\n`；复现 `subprocess.run(['cmd','/c',bat], capture_output=True)` 看 stderr。A/B：LF+ASCII 无错 / LF+em-dash 报错 / CRLF+em-dash 无错。

---

## ★ [2026-08-12] OCR/截图来源数值 → 不验证就写进程序当「常见值」 (置信度: high, 命中: 1)

**Rule**: 程序/文档里的数值与事实声明（尤其「常见/标准/推荐」类）必须验证来源；OCR、截图、凭印象的数值不验证就写 = 错误断言。
**Wrong**: 用户截图 batch-size「768/384」，我 OCR 后写进 tooltip「常见值 384 / 768」→ 用户连纠两次「截图数值不是常见值」「常见值说明没验证」
**Right**: 写进程序前验证（官方文档/实测/社区确认）；不确定就写中性描述（「留空=用默认，一般无需手动设置」）
**Why**: OCR 是概率输出、截图数值无上下文；未验证的「常见值」是错误事实，会误导用户。
