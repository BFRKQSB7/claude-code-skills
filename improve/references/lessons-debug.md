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

---

## ★ [2026-08-12] OCR 提取的 API key 误读 l/I → 无效 key 白调试 (置信度: high, 命中: 1)

**Rule**: 从截图 OCR 得到的关键**精确值**（API key、token、文件名、端口）不能直接信任——OCR 常把 `l` 读成 `I`、`0` 读成 `O`。用前必须从**权威源**二次核对：本地配置文件（auth.json/settings.json）、环境变量、或运行中的应用，程序化提取。一位字符错 = 无效 key = 白排查半天。
**Wrong**: 转换器接 opencode，OCR 截图得 `sk-I75Iv...`（大写 I），实际是 `sk-l75Iv...`（小写 l）→ 反复 401 "Invalid API key"，误判为 CORS/端点问题
**Right**: OCR 后读 `~/.local/share/opencode/auth.json` 程序化取精确 key（而非复制 OCR 输出）
**Why**: key 是精确值，一位错全错；OCR 在 l/1/I、0/O/8 上不可靠。关联 [[OCR 判不了文字重叠]]「OCR 值不可靠」。
**检测**: 关键值用 `python -c "json.load(...)['key']"` 从权威源读，或让用户粘贴确认，不直接用 OCR 输出。

---

## ★ [2026-08-12] style.display='' 回落 CSS display:none，验证看 offsetHeight 不看 style 字符串 (置信度: high, 命中: 1)

**Rule**: CSS 类自带 `display:none` 时，`el.style.display=''` 是想「恢复默认」，但会**回落到 CSS 的 none** → 元素仍隐藏。显式用 `'block'`/`'flex'`。验证可见性看 `offsetHeight>0`，别只看 `style.display` 字符串（'none' 与 '' 都可能假）。
**Wrong**: `$('riskNote').style.display = isOnline?'':'none'` → 在线时 style 显示 '' 但实际隐藏，免责声明一直没出现，多次检查 style 字符串都没发现。
**Right**: `style.display = isOnline?'block':'none'`；验证 `risk.offsetHeight > 0`。
**Why**: JS 设置 `''` 是删除内联覆盖，回落到样式表值；只查 style 属性查不到「实际是否渲染」。

## ★ [2026-08-12] 负面提示词注入审查/安全术语会抑制露骨内容 (置信度: high, 命中: 1)

**Rule**: 用 LLM 生成 NSFW 负面提示词时，小模型常把 censorship / explicit content / nsfw / moderation 写进负面 → 反向抑制露骨内容生成。指令显式禁止 + 输出后过滤这些词。
**Wrong**: 负面生成器只要求「列质量问题」→ Qwen3-4B 把 censorship/explicit content 写进负面。
**Right**: 系统提示加「严禁把审查/安全术语写进负面」+ 后置 `sanitizeNeg` 正则剔除（\b(censorship|explicit content|nsfw|moderation)\b）。

## ★ [2026-08-12] 4B 小模型扛不动复杂结构化输出格式（H3 三字段/六段）(置信度: high, 命中: 3)

**Rule**: 官方结构化格式（长字段名 + 占位符 + 严格纪律）对 4B 是天花板：Qwen3 漏指令回显+年龄漂移、Gemma 保留占位符(MM:/原文)、MiniCPM 整段回显系统提示词。提示词加强约束 + 后处理脚本能改善，但根除不了。复杂结构化任务 → 换大模型，别在 4B 上耗。
**Wrong**: 期望 4B 完美输出 H3 官方格式 → 三个模型各有各的问题。
**Right**: 加强约束（STRICT COMPLIANCE：填满占位符/只输出字段/不回显指令）+ 后处理（截断泄漏标记、填时间戳、规整对白占位）；SDXL 短输出 4B 够用。
**Why**: 长指令 + 模板占位符叠加，4B 注意力/指令遵循不足；后处理是止血不是根治。

## ★ [2026-08-12] 全量标签库角色名检索：垃圾条目+带后缀名+跨番剧歧义 (置信度: high, 命中: 1)

**Rule**: 用全量标签库做「中文输入→英文标签」检索喂给 LLM 时，三个坑让模型选错角色：①库里存在截断/拼错垃圾条目（「阿米」→amyi 是 amiya 的残次翻译，截断了完整角色名）②角色名带「(明日方舟)」后缀，用户输入短名「阿米娅」匹配不到完整 key ③跨番剧歧义（「博士」→ dottore(Genshin) 与 doctor(Arknights) 并存）。检索要**先精确匹配通用词（巨大→jumbo/乳房→breasts），再前缀展开带后缀的角色变体（阿米娅 (明日方舟)→amiya）**，保证正确标签必进参考块，让 LLM 按场景过滤噪音。
**Wrong**: 只做「输入子串→key」匹配 → 「阿米」→amyi 垃圾命中、「博士」→dottore，模型输出 myi/dottore 错误角色（精选库无角色噪音反而输出对）。
**Right**: 前两字索引 + 每位置取公共前缀≥2 的 key；精确 key 优先，再取前缀展开的角色变体；正确标签与噪音并存，LLM 结合上下文（阿米娅=明日方舟）选对。
**Why**: 检索无法知道用户意图（博士是哪个番剧），但保证正确候选在参考里，模型能结合同输入的其他角色上下文推断。实测 deepseek 全量库下 amiya_(arknights)/doctor_(arknights) 正确。

---

## ★★ [2026-08-08] 否定性主张（做不到/不支持/门槛高）未穷尽反例 → 被反例打脸 (置信度: high, 命中: 2)

**Rule**: 断言「做不到/不支持/不可行/门槛很高/上限只有 X」前，先穷尽枚举反例：官方途径之外有无社区衍生方案（插件/补丁/降级配置/魔改/替代服务）？有无真实用户不同条件下的实测？搜不到≠不存在。
**Wrong**: 断言某工具「8GB 显存跑不动」，只依据官方文档 + 官方量化文件大小 → 漏掉社区 4-bit 方案和大量低配实测，一个反例推翻结论并污染全部交付物返工。
**Right**: 穷举不全就降级表述：「截至 YYYY-MM 已知途径门槛高，可能有更轻/更省的方案未穷尽核实」；负面/边界陈述必须带来源或写成「截至 YYYY-MM 未找到 X」；检索渠道按对象提前想（中文 bilibili/知乎、英文 reddit/论坛、开源 repo、官方 issue）。
**Why**: 能力下限/上限/替代路径由「社区衍生方案+真实用户实测」决定，不在官方口径里；否定性主张是最贵的结论——一个反例当场打脸还污染所有下游产物。
**再次**: 2026-08-12 — lessons-mcp「curl 000 别断言已死」同样根因（负向断言未穷尽验证）。

---

## ★★ [2026-08-23] 文字遮罩漏整列且边缘残留 (置信度: high, 命中: 2)

**Rule**: 字形掩膜用稳健背景估计→颜色候选→连通域过滤→小幅膨胀，最后裁回 OCR 多边形；禁止腐蚀后裁字，也禁止因连通域偏大整块丢弃。
**Wrong**: OCR 边缘先腐蚀 + 自适应候选粘成大块后按面积删除 → 紧框粗体、相邻竖排、注音整列漏掉；膨胀后不裁剪又越界。
**Right**: 背景距离用抗邻字污染的分位数；颜色候选足够时不用自适应桥接；模型种子永不被面积过滤丢弃；膨胀后与原多边形相交。
**Why**: 完整性与边界约束必须分步保证：候选阶段保笔画，最终裁剪管越界；用同一腐蚀/面积阈值同时处理两者会两头失败。

---

## ★★ [2026-08-23] 竖排按原始字符计格 → 主文字被标点压小 (置信度: high, 命中: 2)

**Rule**: 竖排拟合前先把字符串规范化为视觉字形：移除排版空白，将 ASCII `...` 合并为一个省略号，再按实际字形格数计算字号。
**Wrong**: `... 嘘` 被当成 5 个等高格，狭长 OCR 框为塞下三个点和一个空格，把真正的汉字从原文估算 23px 压到 19px；继续调全局字号系数会让其他气泡过大。
**Right**: 竖排专用预处理 `"".join(text.split()).replace("...", "…")`，再映射竖排标点并拟合；用真实问题框断言最终字号等于原文字号上限。
**Why**: 字符串长度不等于视觉占位。标点、空白、组合序列必须先归一化，否则短译文也会因虚假长度缩小。

---

## ★★ [2026-08-23] 全图统一字号层级 → 独立小字区拖小正文 (置信度: high, 命中: 2)

**Rule**: 字号统一只作用于视觉尺寸接近的区域；先用真实图列出每块源字号，独立区域相差超过约 10% 就保留各自层级。
**Wrong**: 24px 引用框与 27px 正文因 22% 聚类阈值被归为一组，取最小值后整页正文都变成 24px。
**Right**: 缩紧聚类阈值并用真实坐标回归，断言正文/引用分别保持 27px/24px；段内仍统一，跨样式区不互相拖小。
**Why**: “统一”不是全图取最小值；版块、引用、标题的原始字号本来不同，跨版块归一化会稳定制造小字。

---

## ★★ [2026-08-23] 用译文字体测原文宽度 → 横排长句字号被压小 (置信度: high, 命中: 2)

**Rule**: 跨语言回嵌时，横排源字号从 OCR 文字高度估算，译文再在原占地区域内换行拟合；竖排另走字形格/列布局。
**Wrong**: 拿中文替换字体测英文原句宽度，长句即使原图字高相同也会从 32px 缩到 9px。
**Right**: 横排用实际 OCR 文字高度校准源字号，合并段落按原边界框拟合；明显左对齐段落保留左对齐。
**Why**: 字符数和字串宽度受语言与字体度量影响，不能代表原图视觉字号；横排与竖排的约束维度也不同。
**再次**: 2026-08-23 — OCR 框高系数未用原图字形像素校准，正文/引用译文比原文各大 2–3px；实图测量后回归为 29/26px。

---

## ★ [2026-08-23] 单个关键词判代码 → 正常句子整句漏译 (置信度: high, 命中: 1)

**Rule**: 自然语言与代码共用的关键词不能单独作分类信号；必须匹配语法结构，并用用户原句跑入口级回归。
**Wrong**: 不区分大小写的 `UPDATE` 正则把 `Update on rate limits...` 当 SQL，句子未进翻译器；只修翻译结果检查完全无效。
**Right**: SQL 至少匹配 `UPDATE <table> SET` / `DELETE FROM` 等结构；回归同时断言真 SQL 保留、报错原句参与翻译。
**Why**: 漏译可能发生在翻译前过滤、模型输出或回嵌三层；不追完整数据流就会在错层修复。

---

## ★ [2026-08-23] 只对齐原字号 → 短译文在原文字块中大量留白 (置信度: high, 命中: 1)

**Rule**: 回嵌同时校验源字号和字块占用率；译文较短时在原框内 smart-scale，不得用全局字号统一拖小其他块。
**Wrong**: 横排/竖排都把原字号当最大值，7 行原文翻成 4 行后只占原块高度约 45%，上下留白各约四分之一。
**Right**: 横排在原矩形内重新换行，竖排重算字格/行/列；各块独立拟合，放大上限 35% 且永不越出原框。
**Why**: “字号相似”与“版面占用相似”是两个指标；跨语言字符密度不同，必须在边界约束下平衡。

---

## ★ [2026-08-23] 复核 OCR 高置信输出纯标点 → 覆盖可用主识别 (置信度: high, 命中: 1)

**Rule**: 二级 OCR 替换主结果前同时校验置信度与语义有效性；纯标点/空白输出只能拒绝，不能因分数更高而覆盖。
**Wrong**: MangaOCR 对艺术字以 0.84 置信度输出连续省略号，代码只看分数便替换了仍含日文信息的 PP-OCR 结果。
**Right**: 要求输出至少含目标文字、字母或数字，再满足置信度门槛；用真实低置信裁块验证，复核模型失败时保持主流程不阻塞。
**Why**: token 概率只表示模型对自身输出的确定度，不代表语义正确；级联模型必须为每次覆盖设置内容级门禁。

---

## ★ [2026-08-25] 艺术字识别失败就加模型 → 体积增加但问题仍在 (置信度: high, 命中: 1)

**Rule**: 新 OCR 接入前必须用同一真实疑难裁块 A/B；倾斜、变形、字号重叠导致多个专用 OCR 都失败时，改用用户框选的视觉语义 OCR。
**Wrong**: PP-OCR 拆成碎片便假设 MangaOCR/48px 能补全；实测两者仍只输出部分字或乱码。
**Right**: 记录各模型原始输出；本地模型无明确增益则不接入，视觉 OCR 携带图片与本地碎片重建，结果仍允许人工改。
**Why**: 艺术 Logo 同时破坏检测、几何归一化与字形分类；普通识别模型没有足够视觉语义完成缺字重建。
