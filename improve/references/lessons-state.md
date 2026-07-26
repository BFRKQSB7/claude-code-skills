# State / API / Monitoring / CLI

> 加载条件: 任务涉及 api, monitoring, sampling, balance, cli, cross-platform, 余额, 采样, 轮询, 跨平台

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
