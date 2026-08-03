# State / API / Monitoring / CLI

> 加载条件: 任务涉及 api, monitoring, sampling, balance, cli, cross-platform, 余额, 采样, 轮询, 跨平台

---

## ★★ [2026-08-03] 残留后台进程跨会话污染状态 → 跨提供商残留余额 (置信度: high, 命中: 1)

**场景**: 用户 DeepSeek 会话用完后关窗口,切到第三方中转开新会话,HUD 底部仍显示 DeepSeek 官方余额
**根因**: SessionStart 钩子启动的余额轮询 daemon 在 Windows 上**不随 Claude Code 关闭而死**(async 钩子子进程脱离)。残留 daemon 继续用旧 DeepSeek key 每 15s 轮询并写 `balance_usage.json`,快照永远新鲜 → 新会话 HUD 读它 → 显示旧提供商余额。PID 抢占锁只在"新 daemon 启动"时杀旧 daemon;新会话钩子没触发(切换时插件注册被 cc-switch 改)就没人杀
**修复**: 三层:① 后台 daemon 加**父进程存活检测**(`process.ppid` 死则自终止,~一个轮询周期内退出)② HUD 读余额快照前验证**当前环境是否真是该提供商**(`isDeepSeekEnv`: baseUrl 含 deepseek 或显式 DEEPSEEK_API_KEY,否则忽略快照)③ 余额 API fetch 加 8s 超时防悬空请求累积
**泛化**: 外部工具切换只影响新进程,残留后台进程固化旧 env 会继续旧行为 → 先杀进程再改逻辑。后台进程必须绑定父进程生命周期(孤儿自终止),不能依赖"下次启动的锁"。状态文件被不可控进程持续写入时,读取方必须验证当前环境而不是信任文件
**关键词**: `残留进程` `孤儿进程` `父进程存活` `process.ppid` `跨提供商` `余额` `状态污染` `生命周期`

---
## ★ [2026-08-03] 中转下模型显示角色名而非真实模型 → env 重映射解析 (置信度: high, 命中: 1)

**场景**: 第三方中转(OpenCode Go, OpenAI 格式)下,HUD 模型只显示角色 `claude-sonnet-4-6`,用户要显示真实模型 `deepseek-v4-flash`
**根因**: 中转把 Claude 角色重映射成别的模型,但 statusline 的 stdin 只有角色 id(display_name 为空或=角色)。真实模型名在 env: `ANTHROPIC_DEFAULT_<ROLE>_MODEL_NAME`
**修复**: `getModelName` 优先解析 env 重映射 — 模型 id 是 `claude-(opus|sonnet|haiku|fable)-` 时,查 `ANTHROPIC_DEFAULT_<ROLE>_MODEL_NAME`(回退 `_MODEL`),显示真实模型;官方 API 无该 env → 不受影响走 display_name
**泛化**: 第三方中转/代理的"显示名"常与真实模型分离,真实信息藏在 env/配置重映射里。显示层读取 stdin 不够,要结合 env 解析。Claude Code 的 `ANTHROPIC_DEFAULT_<ROLE>_MODEL(_NAME)` 就是角色→真实模型权威映射
**关键词**: `模型角色` `真实模型` `ANTHROPIC_DEFAULT_SONNET_MODEL_NAME` `env 重映射` `中转` `getModelName`

---

## ★★ [2026-08-03] statusline 插件不显示 → 先查 statusLine 键是否被外部工具改写 (置信度: high, 命中: 1)

**场景**: balance-hud v2.1.0（声称"与 API 无关，任意 API 均正常显示"）在第三方 API（ccswitch 代理, `ANTHROPIC_BASE_URL=127.0.0.1:7897`）下 HUD 完全不显示
**根因**: `~/.claude/settings.json` 被代理切换工具 ccswitch 重写，`statusLine` 键被丢弃 → Claude Code 从不调用 HUD 进程。引擎本身对第三方 API payload 渲染完全正常（用模拟 stdin 验证）。装的就是真 v2.1.0（dist 与 release zip 逐字节一致），v2.1 的"API 无关"改的是渲染代码，与"没被调用"无关
**修复**: ① 写 `statusline.mjs` 包装器（设 COLUMNS 宽度 + 直连插件路径，不依赖 cache 结构）② statusLine 加回 `~/.claude/settings.json` ③ 根治：常驻看门狗（`fix_statusline.mjs --watch`，fs.watch 秒级 + 2s 轮询兜底）监控 settings.json，statusLine 被外部工具清掉时自动补回（保留其余键，先备份）。注册 Windows 启动项确保看门狗随登录常驻
**泛化**: 外部工具重写配置文件时丢未知键（只保自己的 env/model 模板）。配置类插件失效，第一诊断是"进程是否被调用"，不是改渲染代码。隔离方法：`node dist/index.js < test_payload.json` 直接喂模拟 stdin → 输出正常 = 没被调用（查 wiring）；输出空/报错 = 渲染 bug。**注意：`statusLine` 放 `settings.local.json` 不生效**（实测该版本不认，subagent 给的训练数据答案有误）→ 只能放 `settings.json`，被外部工具反复清掉就用常驻看门狗守卫，不能只修一次
**关键词**: `statusLine` `settings.json` `ccswitch` `看门狗` `fs.watch` `重写` `覆盖` `启动项` `常驻`

---
## ★★ [2026-08-03] ANTHROPIC_AUTH_TOKEN 被当 DeepSeek 余额 key → 代理会话直连官网余额接口 (置信度: high, 命中: 1)

**场景**: 第三方 API（ccswitch 代理）会话，balance-hud 的 auto_refresh daemon 每 15s 直连 `api.deepseek.com/user/balance`，用户疑惑"第三方 API 为什么调官网余额查询"
**根因**: `getKeys()` = `DEEPSEEK_API_KEY || ANTHROPIC_AUTH_TOKEN`，只看变量非空，不判断 baseUrl 是否真 DeepSeek。代理 token（`PROXY_MANAGED`）被当 DeepSeek key 发到官网。且已运行的 daemon 固化旧 env（切代理前是直连 DeepSeek 的真 key），切换后残留进程继续拿旧 key 直连官网
**修复**: ① 杀掉残留 daemon（PID 抢占锁只在下次 SessionStart 触发，当前进程不受影响）② `getKeys()` 改为：`DEEPSEEK_API_KEY` 显式优先；`ANTHROPIC_AUTH_TOKEN` 仅当 `ANTHROPIC_BASE_URL` 含 `deepseek` 才当 key ③ 写空快照清掉残留余额行
**泛化**: 凭据回退要验证目标服务身份（baseUrl/环境），不能只看变量非空。外部工具切配置只影响新进程，残留后台进程固化旧 env 会继续旧行为 → 先杀进程再改逻辑。诊断"谁在调某 API"：grep 代码里的 fetch/axios URL + 查残留进程 startTime
**关键词**: `DEEPSEEK_API_KEY` `ANTHROPIC_AUTH_TOKEN` `ANTHROPIC_BASE_URL` `余额` `直连` `凭据回退` `代理` `残留进程` `getKeys`

---
## ★★ [2026-06-16] 初始化时异常采样 → 基准线错误 (置信度: high, 命中: 2)

**Rule**: 传感器/API 首次采样可能异常，不要第一点就固化
**Wrong**: API 瞬时返回低值(8.78) → 设为 initial → 后续恢复(39+) → consumed 永远 0%
**Right**: 取 N≥2 次采样 → 波动 <50% → 再锁定为 initial
**Why**: 网络抖动、服务端瞬时错误都会污染首次采样
**泛化**: 适用于余额、温度、延迟、计数器等任何累积量监控的基准线设定

---
## ★ [2026-06-15] CLI 输出跨平台不一致 → 假阴性 (置信度: medium, 命中: 1)

**泛化**: 跨平台脚本的进程检测要精确到字段级，不靠模糊 grep。`awk '{print $2}' | grep -x "$pid"` 而非 `grep -q node`
**核心**: 验证到列，不验证到行。

---

## ★ [2026-06-16] 假设 API 实时更新 → UI 误显零消耗 (置信度: medium, 命中: 1)

**场景**: balance-hud 显示消耗为 0%，daemon 正常轮询，但 API 连续 30 分钟返回相同余额
**根因**: DeepSeek 余额 API 约 5 分钟延迟结算，非实时。daemon 代码无 bug
**修复**: 删除进度条（延迟期间进度条无意义），保留余额数字+消耗+百分比+时间+低余额警告
**泛化**: 依赖外部 API 实时性前先验证更新频率。`curl` 间隔 1-5 分钟调 3 次确认延迟量级 → 再设计 UI。进度条/实时指标只在 API 更新频率 ≤ 轮询频率时有效
**关联**: [[diagnose-loop]] — 方法 3 (CLI invocation) 成功定位根因

---

## ★ [2026-06-16] Windows winget 安装 CLI → Git Bash 找不到 (置信度: medium, 命中: 1)

**场景**: `winget install --id GitHub.cli` 成功，但 Git Bash 里 `gh: command not found`
**根因**: winget 安装到 `C:\Program Files\GitHub CLI\`，该路径不在 Git Bash 的 PATH 中（Git Bash 用 `~/.bashrc`，不继承 Windows 系统 PATH 的所有条目）
**修复**: `echo 'export PATH="$PATH:/c/Program Files/GitHub CLI"' >> ~/.bashrc`
**泛化**: Windows 开发环境三套 PATH 体系（CMD/PowerShell/Git Bash），winget/scoop/choco 安装的 CLI 工具不一定三者都覆盖。安装后先 `which <cmd>` 验证，失败就加 bashrc。
**关键词**: `winget` `scoop` `choco` `Git Bash` `PATH` `command not found`
