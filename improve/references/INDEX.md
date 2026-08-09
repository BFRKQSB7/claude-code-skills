# Domain Index — 工程领域教训目录

> 按需浏览。路由匹配后直接读具体文件，不需要全读这个 index。
> 想了解某个 domain 有哪些教训 → 读对应行。

## 文件清单

| Domain | 文件 | 教训数 | 一句话 |
|--------|------|--------|--------|
| Process | [lessons-process.md](lessons-process.md) | 4 | 后台进程/锁/启动竞态/daemon hook async |
| Cleanup | [lessons-cleanup.md](lessons-cleanup.md) | 3 (7子模式) | 变更后全局 grep 防引用断裂 / 衍生项目旧仓库引用 / 发布文件禁带本机个性化信息 |
| State | [lessons-state.md](lessons-state.md) | 8 | API 采样/跨平台 CLI/实时性/statusLine 被重写/凭据回退/残留进程污染/模型 env 重映射 |
| Skill | [lessons-skill.md](lessons-skill.md) | 29 | 发布流程/教训审查/SKILL.md 架构/术语/命名/衍生项目文档/多语言 README/代理指令禁弹窗/断言验运行时/迭代基线优化/手动插件注册/独立仓库确认/运行目录与 diff 克隆分离/raw CDN 缓存验证/单文件 HTML GitHub Pages 托管 |
| Debug | [lessons-debug.md](lessons-debug.md) | 9 | 反馈循环优先/调试日志标记/多假设锚定/代理端口验活/行尾差异/实测当前行为/spawnSync 模拟 stdin |
| Security | [lessons-security.md](lessons-security.md) | 8 | 注入/凭证泄露/供应链/反序列化/CORS/加密 |
| **MCP** | **[lessons-mcp.md](lessons-mcp.md)** | **7** | **自起 Chrome+--browserUrl 连接/DevToolsActivePort hack 备选/WebFetch 拦截/WebSearch 技巧/截图溢出/浏览器 vs WebFetch** |

## 按需加载决策树

```
任务含 "daemon/lock/pid/启动/后台/守护/竞态" → lessons-process.md (4条，~50行)
任务含 "rename/delete/version/release/重命名/版本/发布/打包" → lessons-cleanup.md (2条+6子模式，~30行)
任务含 "api/monitoring/cli/cross-platform/windows/path/采样/跨平台" → lessons-state.md (8条，~95行)
任务含 "skill/plugin/design/naming/description/readme/i18n/multi-language/多语言/翻译/技能/反省/学习" → lessons-skill.md (28条)
任务含 "debug/diagnose/bug/fix/log/调试/诊断/复现/排查/diff/compare/对比/行尾/换行符/CRLF" → lessons-debug.md (9条，~100行)
任务含 "security/auth/token/password/encrypt/injection/安全/认证/加密" → lessons-security.md (8条，~80行)
任务含 "mcp/chrome/devtools/browser/webfetch/websearch/navigate/snapshot/screenshot/evaluate_script/click/fill/select_page/new_page/fetch/search/URL/huggingface/page/浏览器/搜索/截图/网页/访问/下载/渲染/表单" → lessons-mcp.md (7条，~110行) ⚠️
```

## 交叉索引

- Process + Cleanup 同时触发 → 两个都加载（发布 daemon 时常见）
- Debug + Security 同时触发 → 两个都加载（安全漏洞排查）
- 常加载 `lessons-critical.md` 独立于此路由（永久在上下文中）
