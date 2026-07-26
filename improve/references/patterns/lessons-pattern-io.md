# Pattern: I/O / Network / Database

> 跨语言通用。语言特定细节参见 `lang/lessons-<lang>.md`
> 加载条件: open, read, write, file, http, fetch, db, database, sql, api, request, response, stdin, stdout, socket, json, csv, 文件, 网络, 数据库, 读写

---

## 通用原则

### ★★★ 资源不关闭 → 句柄泄漏 (置信度: high, 命中: 3)

**Rule**: 文件/socket/DB连接/HTTP连接必须在所有代码路径（包括异常路径）关闭
**Right**: Python `with` / JS `try-finally` 或 `using` (ES2024) / Go `defer f.Close()` / Rust `Drop` trait (自动) / Bash `trap 'rm -f "$TMP"' EXIT`
**Why**: 进程级句柄上限（ulimit FD 1024-65535）。短请求没问题，长期运行必爆。

### ★★★ 外部输入未校验 → 注入/崩溃 (置信度: high, 命中: 3)

**Rule**: 所有外部数据（API响应/文件内容/URL参数/stdin/环境变量）在使用前校验
**Check**: JSON schema? 字段类型? 字符串长度? 特殊字符? SQL injection? Shell injection?
**Why**: 外部数据 = 不受信任。格式错误 = 崩溃；恶意数据 = 安全漏洞。校验是必需的防线。

### ★★ 大文件全量加载 → OOM (置信度: high, 命中: 2)

**Rule**: > 100MB 文件用 stream/chunk/iterator，不 `.read()` / `readFileSync` / `read_to_string()` 全量
**Right**: Python `for line in f:` / JS `createReadStream().pipe()` / Go `bufio.Scanner` / Rust `BufReader::lines()`
**Why**: 文件大小不可控。用户可能拖 2GB 文件到你的 CLI / API 可能返回巨大 payload。

### ★★★ 字符编码假设 → 乱码/命令损坏 (置信度: high, 命中: 3)

**Rule**: 读文本文件显式指定 encoding。不假设 UTF-8。Windows 上尤其注意（默认 GBK/CP1252）。
**Right**: `open(path, encoding='utf-8')` / `readFileSync(path, 'utf-8')`。读二进制不指定编码。

**子模式: Windows 批处理文件编码 → 命令损坏 (2026-07-05)**

| # | 子模式 | 现象 | 命中 |
|---|--------|------|------|
| 1 | Write 工具写入 UTF-8 → cmd.exe 按 GBK 解析 | 中文→乱码字节→含特殊字符→goto 标签截断/^ 换行断裂 | 2 |
| 2 | chcp 65001 修复 → 无效 | 解析在 chcp 执行前完成 → 马后炮 | 2 |
| 3 | GBK 转换 (PowerShell) → 依旧不行 | GBK 转换也不可靠，用户反馈仍报错 | 1 |

**Rule**: Windows cmd.exe 用系统 ANSI 编码（中文 Windows=GBK）**解析 .bat 文件**。`chcp 65001` 只改变**控制台输出**编码，不改变解析阶段编码——解析发生在 `chcp` 执行之前。
**Wrong**: 用 Write 工具 (默认 UTF-8) 直接写含中文的 .bat → cmd.exe 按 GBK 解 → 乱码字节命中 cmd 特殊字符 → 标签名断裂、命令被截断 / 尝试 `chcp 65001` 修复 → 无效 / 尝试 PowerShell GBK 转换 → 依旧不行
**Right**: ① **纯 ASCII 英文 .bat（唯一稳定解）**
**失败路径（已验证，按失败次数排序）**:
- `chcp 65001` 在 bat 文件内: 解析已完成 → 马后炮，无效（累计 3 次）
- UTF-8 无 BOM: cmd.exe 按 ANSI 解 → 乱码
- UTF-8 + BOM: Git Bash 跨平台写入时 BOM 丢失或 cmd 忽略
- GBK + chcp 65001: 控制台切 UTF-8 显示 GBK 字节 → 屏幕乱码
- GBK (PowerShell `GetEncoding(936)`): 用户反馈依旧不行（2026-07-08）
- `-Encoding Default` via Git Bash PS: Default 映射不可靠

**Why**: 编辑工具（Linux/macOS 原生 UTF-8）和 Windows cmd.exe（系统 ANSI）编码假设不一致。跨平台写入文本文件时，写入端的默认编码 ≠ 消费端的默认编码。

**防御**:
- .bat 文件用纯 ASCII 英文 — 已验证 6 种编码方案，仅纯 ASCII 零故障
- 如必须跨平台生成: Bash heredoc 写 CRLF
- 事后 `file script.bat` 验证不含 "UTF-8 BOM" 或 "UTF-8"

**再次**: 2026-07-05 — 越狱版模型启动器.bat，7 次编码尝试（UTF-8/UTF-8 BOM/GBK+chcp/GBK-chcp/Default）均失败，最终纯 ASCII 解决
**再次**: 2026-07-08 — aaastart.bat 中文注释乱码。Claude 用 Write+Edit 加 `chcp 65001` → 无效（已记录失败路径 #2）。根因: Phase 1 未加载 lessons-bash.md → 重复踩坑。`chcp 65001` 是 bat 编码问题最诱人的错误答案 — 控制台输出 ≠ 文件解析。

---

### ★★★ 跨文件批量替换 → CRLF/LF 静默失败 (置信度: high, 命中: 2)

**现象**: Python 脚本用多行字符串对文件做 `.replace()`，打印"OK"但实际未替换任何内容。后续验证才发现文件未变更。

**根因**: Git `core.autocrlf=true`（Windows 默认）在 checkout 时自动将 LF→CRLF。Python 从文件读取的字符串包含 `\r\n`，但替换模式字符串只含 `\n`。`str.replace(old, new)` 按字节精确匹配 → CRLF vs LF 不匹配 → 静默返回原文本。`.replace()` 不报错，`print('OK')` 不验证 count → 整个替换悄悄跳过。

**诊断**:
```python
# 替换前必检
if old_string not in text:
    print(f'WARNING: pattern not found (CRLF mismatch?)')
    print(f'File has CRLF: {chr(13)+chr(10) in text}')
```

**Right**:
```python
# 读取时检测换行符
nl = '\r\n' if '\r\n' in text else '\n'
# 在 f-string 中使用 nl 变量构建多行模式
old = f'line1{nl}line2{nl}line3'
# 替换后验证 count
c = text.count(old)
print(f'Replaced: {c} occurrences')
text = text.replace(old, new)
```

**防御**:
- 多行 `.replace()` 前必须验证 `old_string in text`
- 用 f-string + `nl` 变量替代硬编码 `\n`
- 替换后打印 count，不假设成功
- 单行替换（不含换行符）不受影响，可以正常使用

**再次**: 2026-07-26 — launcher_template.bat 全局 init 和 toggle_mode 多行替换，Python 脚本在 CRLF 文件上用 LF 模式 → `print('OK')` 不验证 count → 2 处静默失败，第二轮才手动修复

### ★★ Python f-string 生成 .bat 代码 → % 转义混乱 (置信度: medium, 命中: 1)

**现象**: Python f-string 生成的 .bat 文件中，`for %%a in (...)` 变成 `for %%%%a in (...)`（百分号数量翻倍），cmd.exe 解析失败。

**根因**: Python f-string 中 `%%` 被解释为转义的 `%`。生成批处理代码时，目标文件需要 `%%`，但 f-string 中写 `%%%%` 才产生 `%%`。嵌套多层时极易算错。

**Right**:
```python
# 方案1：常规字符串 + .format() / .replace()（避免 f-string % 转义）
template = 'for /f "tokens=2 delims=:" {}a in (...)'.format('%')  # -> %%a

# 方案2：f-string 中用变量存储百分号
P = '%'
line = f'for /f "tokens=2 delims=:" {P}{P}a in (...)'  # -> %%a

# 方案3（最安全）：正则后处理
text = text.replace('PERCENTPERCENT', '%%')
```

**Why**: f-string 的 `%%` 转义和 bat 的 `%%` 转义语义冲突。在 f-string 中生成 bat 代码时，必须在脑中模拟两层转义 → 极易出错。

**再次**: 2026-07-26 — launcher_template.bat LAN IP 检测的 for 循环，f-string 中 `%%%%a` 预期输出 `%%a`，实际写入 `%%%%a` → 文件需二次修复

---

## 语言差异

| 陷阱 | Python | JavaScript | Go | Rust | Bash |
|------|--------|------------|----|----|----|
| 自动关闭 | `with` (context manager) | `using` (ES2024) | `defer` | `Drop` (RAII) | `trap EXIT` |
| 大文件默认 | for line 流式 | 需 stream API | bufio.Scanner | BufReader | pipe |
| 编码默认 | 平台相关 (PEP 686 后 UTF-8) | UTF-8 | UTF-8 | UTF-8 | 平台相关 |
| SQL 注入 | 参数化查询 | 参数化查询 | database/sql 占位符 | sqlx 宏 | `--arg` |
| HTTP 默认超时 | 无 (requests 有) | 无 (fetch) | 无 (http.Client 可配) | 需显式设 | `timeout` 命令 |
