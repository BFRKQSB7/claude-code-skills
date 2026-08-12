# Domain Index — 工程领域教训目录

> 按需浏览。路由匹配后直接读具体文件，不需要全读这个 index。
> 想了解某个 domain 有哪些教训 → 读对应行。

## 文件清单

| Domain | 文件 | 教训数 | 一句话 |
|--------|------|--------|--------|
| Process | [lessons-process.md](lessons-process.md) | 4 | 后台进程/锁/启动竞态/daemon hook async |
| Cleanup | [lessons-cleanup.md](lessons-cleanup.md) | 15 | 变更后全局 grep 防引用断裂 / 衍生项目旧仓库引用 / 发布文件禁带本机个性化信息 / 删 skill 要删干净（多加载目录副本 + override 残留）/ 删 skill 云端默认不删 / 会话临时产物用完即删 / Write工具路径vs Bash /tmp / 发布仓库不留旧版备份文件 / 发布 bump 版本号本地源文件要同步 / 维护注释锚点名干扰脚本count断言 / 发布前自查界面版本号 / 「把库放进来」先确认范围与适配方式 / 源码放运行时目录→两套配置分叉 |
| State | [lessons-state.md](lessons-state.md) | 9 | API 采样/跨平台 CLI/实时性/statusLine 被重写/凭据回退/残留进程污染/模型 env 重映射/IndexedDB恢复句柄校验 |
| Skill | [lessons-skill.md](lessons-skill.md) | 35 | 发布流程/教训审查/SKILL.md 架构/术语/命名/衍生项目文档/多语言 README/纯外语 README 必补中文（文件切换版）/代理指令禁弹窗/断言验运行时/迭代基线优化/手动插件注册/独立仓库确认/运行目录与 diff 克隆分离/raw CDN 缓存验证/单文件 HTML GitHub Pages 托管/外部 skill 合并映射表/README 内容用户视角 |
| Debug | [lessons-debug.md](lessons-debug.md) | 13 | 反馈循环优先/调试日志标记/多假设锚定/代理端口验活/行尾差异/实测当前行为/spawnSync 模拟 stdin/页面测试残留状态/cmd LF行尾误解析/OCR数值不验证不写程序/OCR关键值二次核对权威源 |
| **GPU** | **[lessons-gpu.md](lessons-gpu.md)** | **4** | **Blackwell 上 paddle cu126 不可用走 onnxruntime+DirectML / 硬件探测独立于加速包（删模块可重装）/ ctypes D3D12 坑用 D3D11 / ORT-DML 同名互斥可卸载切换** |
| Security | [lessons-security.md](lessons-security.md) | 8 | 注入/凭证泄露/供应链/反序列化/CORS/加密 |
| **MCP** | **[lessons-mcp.md](lessons-mcp.md)** | **12** | **自起 Chrome+--browserUrl 连接/DevToolsActivePort hack 备选/WebFetch 拦截/WebSearch 技巧/截图溢出/浏览器 vs WebFetch/读 GitHub 文件全文(embeddedData.rawLines)/evaluate_script 异步两步法/curl 000 假阴性别断言已死/CORS 预检验证直连/推理模型空响应+端点挖掘+CORS代理** |

## 按需加载决策树

```
任务含 "daemon/lock/pid/启动/后台/守护/竞态" → lessons-process.md (4条，~50行)
任务含 "rename/delete/version/release/重命名/版本/发布/打包" → lessons-cleanup.md (15条，~180行)
任务含 "api/monitoring/cli/cross-platform/windows/path/采样/跨平台" → lessons-state.md (8条，~95行)
任务含 "skill/plugin/design/naming/description/readme/i18n/multi-language/多语言/翻译/技能/反省/学习" → lessons-skill.md (35条)
任务含 "debug/diagnose/bug/fix/log/调试/诊断/复现/排查/diff/compare/对比/行尾/换行符/CRLF" → lessons-debug.md (13条，~130行)
任务含 "gpu/显卡/cuda/directml/onnx/paddle/推理/模型部署/ocr/blackwell/rtx" → lessons-gpu.md (4条，~40行)
任务含 "security/auth/token/password/encrypt/injection/安全/认证/加密" → lessons-security.md (8条，~80行)
任务含 "mcp/chrome/devtools/browser/webfetch/websearch/navigate/snapshot/screenshot/evaluate_script/click/fill/select_page/new_page/fetch/search/URL/huggingface/page/浏览器/搜索/截图/网页/访问/下载/渲染/表单" → lessons-mcp.md (12条，~160行) ⚠️
```

## 交叉索引

- Process + Cleanup 同时触发 → 两个都加载（发布 daemon 时常见）
- Debug + Security 同时触发 → 两个都加载（安全漏洞排查）
- 常加载 `lessons-critical.md` 独立于此路由（永久在上下文中）
