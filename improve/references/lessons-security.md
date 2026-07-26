# Security / Vulnerability Prevention

> 加载条件: 任务涉及 security, auth, login, token, password, secret, encrypt, hash, sql, injection, XSS, CSRF, CORS, CSP, supply chain, dependency, deserialize, pickle, eval, exec, sanitize, validate, 安全, 认证, 加密, 注入, 序列化, 依赖

---

## ★★★ 外部输入未校验 → 注入攻击 (置信度: high, 命中: 3)

**Rule**: 所有外部数据（用户输入/API响应/URL参数/文件内容/环境变量）在使用前必须校验+净化。不信任任何外部输入。
**Wrong**: `f"SELECT * FROM users WHERE name = '{name}'"` / `eval(user_input)` / `os.system(f"ping {host}")` / `innerHTML = apiResponse`
**Right**: 参数化查询 / `shlex.quote()` / `DOMPurify.sanitize()` / JSON Schema 校验 / 白名单验证
**Why**: 注入攻击（SQL/命令/代码/XSS）在 OWASP Top 10 中持续位居前列。参数化查询和输入校验是唯一的防线。
**泛化**: 适用于任何"外部字符串进入执行上下文"的场景。永远用参数化/白名单，不靠转义/黑名单。

## ★★★ 敏感信息硬编码/泄露 → 凭证暴露 (置信度: high, 命中: 3)

**Rule**: 密钥/token/password/API key 永远不硬编码在源码中。用环境变量/secret manager/.env（不提交 git）。
**Wrong**: `const API_KEY = "sk-abc123"` 在源码中 → git push → 公开仓库 = 凭证泄露
**Right**: `const API_KEY = process.env.API_KEY` + `.env` 在 `.gitignore` + `.env.example` 模板提交
**Why**: GitHub 每天检测到数千次凭证泄露。一旦 push 到公开仓库，即使立即删除，凭证已被扫描 bot 获取。
**防御**: pre-commit hook 扫描密钥模式 / `.gitignore` 含 `.env` `*.pem` `credentials.*` / GitLab/GitHub secret detection

## ★★ 依赖链攻击 → 供应链污染 (置信度: high, 命中: 2)

**Rule**: 第三方依赖必须审查：固定版本（lockfile）、定期审计、最小权限、来源验证
**Wrong**: `npm install cool-package` 不审查 → typosquatting 恶意包 → 窃取环境变量
**Right**: 审查: 下载量？维护者历史？源码质量？权限请求？→ `npm audit` / `pip-audit` / `cargo-audit` → lockfile 提交
**Why**: 2024-2025 年供应链攻击激增（OWASP A03 新条目）。恶意 npm/PyPI 包通过相似命名、依赖混淆、维护者接管等方式渗透。
**泛化**: 成熟生态（npm/pip/cargo/go mod）的依赖安全 = 锁文件 + 定期审计 + 最小依赖原则

## ★★ 不安全的反序列化 → RCE (置信度: high, 命中: 2)

**Rule**: 永远不对不受信任的数据使用 `pickle.loads()` / `yaml.load()` (unsafe) / `eval()` / `new Function()`
**Wrong**: Python `pickle.loads(user_data)` — 可执行任意代码 / JS `eval(JSONP_response)` / `yaml.load(untrusted)`
**Right**: Python `json.loads()` / JS `JSON.parse()` / `yaml.safe_load()` / 用 serde (Rust) / encoding/json (Go)
**Why**: pickle/yaml.load/eval 可以执行任意代码。反序列化攻击在 CWE Top 25 中排名靠前。
**检测**: grep `pickle.loads` `yaml.load(` `eval(` `new Function(` `exec(` → 确认输入来源

## ★ 日志泄露敏感信息 → 合规风险 (置信度: medium, 命中: 1)

**Rule**: 日志/错误消息中不输出 password/token/SSN/信用卡号/PII。生产环境关闭 debug 日志。
**Wrong**: `log.info(f"User {email} logged in with password {pwd}")` / stack trace 返回给前端
**Right**: 生产日志级别 ≥ INFO、敏感字段脱敏 `***`、错误消息对用户泛化（内部日志保留详情）
**Why**: Sonar 数据：debug 功能和堆栈跟踪是 Java 最常见的生产安全漏洞。GDPR/CCPA 合规要求。
**检测**: grep `password` `token` `secret` `key` 在日志/print 语句中

## ★ CORS 配置过于宽松 → 跨域攻击 (置信度: medium, 命中: 1)

**Rule**: CORS `Access-Control-Allow-Origin: *` 且 `Allow-Credentials: true` = 安全漏洞。用白名单。
**Wrong**: `Access-Control-Allow-Origin: *` + `Access-Control-Allow-Credentials: true` — 任意域可带凭证请求
**Right**: 显式白名单 + 动态 Origin 校验。`*` 只在不需要 credentials 的公开 API 使用。
**Why**: 宽松 CORS + credentials = 任何网站的 JS 都能以登录用户身份调你的 API。

## ★ 弱加密/哈希 → 数据可逆推 (置信度: medium, 命中: 1)

**Rule**: 密码用 bcrypt/argon2（不 SHA/MD5）。传输用 TLS 1.3（不 HTTP/FTP/Telnet 明文）。
**Wrong**: `hashlib.md5(password)` 存密码 / `http://api.example.com` 明文传输
**Right**: `bcrypt.hash(password, salt_rounds=12)` / HTTPS + HSTS / 敏感数据静止加密 (AES-256-GCM)
**Why**: MD5/SHA-1 可在秒级碰撞。HTTP/FTP 明文可以被任何网络中间节点嗅探。Sonar 数据：Python 最常见的安全 bug 是使用明文协议。

---

## 语言差异

| 陷阱 | Python | JavaScript | Go | Rust |
|------|--------|------------|----|----|
| 不安全反序列化 | `pickle.loads()` | `eval()` / `new Function()` | `gob` 相对安全 | serde 编译时安全 |
| 命令注入 | `os.system()` / `subprocess(shell=True)` | `child_process.exec()` | `exec.Command()` 天然安全 | `std::process::Command` 天然安全 |
| 模板注入 | Jinja2 无 autoescape | EJS `<%-` (unescaped) | `html/template` 天然安全 | 编译时模板 |
| 依赖审计 | `pip-audit` / safety | `npm audit` / `yarn audit` | `govulncheck` | `cargo-audit` |
| SQL 注入 | 参数化 `?` `%s` | 参数化 `?` `$1` | `database/sql` 占位符 | sqlx 宏编译检查 |
| 密钥管理 | python-dotenv | dotenv | os.Getenv | dotenvy |
