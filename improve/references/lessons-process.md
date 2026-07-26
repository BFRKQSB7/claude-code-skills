# Process / Daemon / Lock

> 加载条件: 任务涉及 daemon, lock, pid, startup, session, 后台进程, 守护, 会话

---

## ★★ [2026-06-15] 多入口启动 → 竞态双实例 (置信度: high, 命中: 2)

**Rule**: 任何后台进程只保留一个启动路径；若必须保留多个，确保双方都 async（不阻塞 hook）
**Wrong**: `settings.json SessionStart` + `plugin hooks.json` 双重启动，且 settings.json 侧无 async → 阻塞超时
**Right**: 两个都 async（settings.json `"async": true`，hooks.json `&`），preemptive lock 处理抢锁
**Why**: 插件 hooks.json 是分发单元不可删；框架可能同时加载两者 → 必须双方 non-blocking
**再次**: 2026-06-16 — hooks.json 清空后未自动加载，改回 settings.json `$HOME` 绝对路径；同月发现双方实际同时活跃，settings.json 缺 async 导致 hook 超时报错
**关联**: [[pid-preemptive-lock]] [[hook-daemon-async]]

---

## ★★ [2026-06-16] Hook 跑 daemon 缺 async → 阻塞超时 (置信度: high, 命中: 2)

**Rule**: SessionStart hook 启动 daemon/长期进程必须标记 `"async": true`；禁止用 shell `&` 后台化（跨平台不可靠）
**Wrong**: `"command": "node daemon.mjs"` — daemon 永不退出 → hook 等到超时
**Wrong**: `"command": "bash -c 'node daemon.mjs &'"` — Unix shell 语法，Windows 上 `bash` 不在 PATH + `/dev/null` 不存在
**Right**: `"command": "node daemon.mjs", "async": true` — 平台无关，Claude Code 框架原生支持
**Why**: Claude Code hook runner 等待命令 exit code。daemon `setInterval` + `process.stdin.resume()` 永不退出 → 超时。`bash -c '... &'` 依赖 Unix shell，Win 不可用
**泛化**: 任何 hook（SessionStart/PostToolUse/Notification）跑长期进程都必须 async。不要用 shell 语法做后台化——用框架的 `async` 字段
**再次**: 2026-06-21 — balance-hud hooks.json 用 `bash -c "... </dev/null >/dev/null 2>&1 &"` 在 Windows 上无法启动，改为 `"async": true` + 直接 `node` 命令修复

---

## ★ [2026-06-15] 手动删锁文件 → 绕过单例保护 (置信度: high, 命中: 1)

**Rule**: 不要替锁机制做判断
**Wrong**: `rm -f .pid` 然后启动 → 旧实例还在，新实例又写锁
**Right**: 直接启动，让 `acquireLock()` 自己检测旧 PID 是否存活
**关联**: [[pid-preemptive-lock]]

---

## ★★ [2026-06-16] PID 防御锁 → 新会话永抢不到锁 (置信度: high, 命中: 2)

**Rule**: 后台守护进程用抢占式锁，不用防御式锁
**Wrong**: `acquireLock()` 发现旧 PID → `process.exit(0)` 静默退出 → `resetSessionState()` 跳过了
**Right**: 发现旧 PID → `process.kill(oldPid)` 杀掉旧进程 → 接管 → 照常 resetSessionState
**Why**: `&` 分离的进程不随父进程退出（被 init 接管），防御锁 = 旧实例永久占有
**泛化**: 适用于 SessionStart daemon、定时轮询器、watchdog 等跨会话后台任务
**关联**: [[multi-entry-startup]] [[manual-pid-delete]]
