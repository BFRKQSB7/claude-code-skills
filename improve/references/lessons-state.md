# State / API / Monitoring / CLI

> 加载条件: 任务涉及 api, monitoring, sampling, balance, cli, cross-platform, 余额, 采样, 轮询, 跨平台

---

## ★★ [2026-08-03] statusline 插件不显示 → 先查 statusLine 键是否被外部工具改写 (置信度: high, 命中: 1)

**场景**: balance-hud v2.1.0（声称"与 API 无关，任意 API 均正常显示"）在第三方 API（ccswitch 代理, `ANTHROPIC_BASE_URL=127.0.0.1:7897`）下 HUD 完全不显示
**根因**: `~/.claude/settings.json` 被代理切换工具 ccswitch 重写，`statusLine` 键被丢弃 → Claude Code 从不调用 HUD 进程。引擎本身对第三方 API payload 渲染完全正常（用模拟 stdin 验证）。装的就是真 v2.1.0（dist 与 release zip 逐字节一致），v2.1 的"API 无关"改的是渲染代码，与"没被调用"无关
**修复**: ① 写 `statusline.mjs` 包装器（设 COLUMNS 宽度 + 直连插件路径，不依赖 cache 结构）② statusLine 加回 `~/.claude/settings.json` ③ 同时写入 `~/.claude/settings.local.json`（优先级更高且 ccswitch 不碰此文件）→ 抗重写
**泛化**: 外部工具重写配置文件时丢未知键（只保自己的 env/model 模板）。配置类插件失效，第一诊断是"进程是否被调用"，不是改渲染代码。隔离方法：`node dist/index.js < test_payload.json` 直接喂模拟 stdin → 输出正常 = 没被调用（查 wiring）；输出空/报错 = 渲染 bug。statusLine 是顶层键，settings.local.json 优先级高于 settings.json
**关键词**: `statusLine` `settings.json` `settings.local.json` `ccswitch` `statusline` `HUD` `重写` `覆盖` `配置文件`

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
