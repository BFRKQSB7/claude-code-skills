# Bash / Shell Lessons

> 加载条件: .sh, .bash, .zsh, bash, shell, 用户说"Bash" "Shell" "脚本"

---

## #error — 错误处理陷阱

### ★★ set -e 不相信管道 → pipefail 必须显式开启 (置信度: high, 命中: 2)

**Rule**: 脚本开头三行: `set -euo pipefail`。只用 `set -e` 是不够的。
**Wrong**: `set -e; cat missing.txt | grep "foo"` → cat 失败但管道只取最后一个命令 exit code → grep 成功 → 不退出
**Right**: `set -euo pipefail` — 管道任何命令失败都失败
**Why**: Bash 默认只有管道最后一个命令决定 `$?`。`pipefail` 让任何命令失败都传播。

### ★ glob 无匹配返回空 → 路径拼接静默失败 (置信度: high, 命中: 1)

**Rule**: 用 glob/命令替换获取路径时，必须验证结果非空再使用。配置文件（settings.json）中的 shell 命令避免动态 glob 查路径 — 用静态绝对路径。
**Wrong**: `dir=$(ls -1d plugins/cache/*/claude-hud/*/ 2>/dev/null); node "$dir/dist/index.js"` → glob 无匹配 → `$dir` = "" → `node "/dist/index.js"` → 静默失败，statusLine 消失
**Right**: `dir="plugins/marketplaces/claude-hud"; node "$HOME/.claude/$dir/dist/index.js"` 或用 guard: `[ -n "$dir" ] && node "$dir/dist/index.js" || echo "plugin not found" >&2`
**Why**: `ls` 在 glob 无匹配时输出空字符串（stderr 被 `/dev/null` 吃掉了 "No such file or directory"），变量被赋值但值为空。`set -u` 防不住——变量已定义。**配置文件中的命令没有交互机会，失败必须 loud & explicit。**
**再次**: 2026-07-02 — claude-hud statusLine 消失，缓存目录 `plugins/cache/*/claude-hud/` 无内容，glob 返回空

### ★ 变量未定义不报错 → 空字符串静默替换 (置信度: high, 命中: 1)

**Rule**: `set -u` 让引用未定义变量立即退出
**Wrong**: `rm -rf /$UNDEFINED_VAR/` → 扩展为 `rm -rf //` → 即 `rm -rf /`
**Right**: `set -u` → `$UNDEFINED_VAR` 立即报错退出
**Why**: Bash 默认 `${UNDEFINED}` = `""`。拼写错误 = 空字符串 = 灾难性副作用。

---

## #encoding — 编码陷阱

### ★★★ Write 工具写 .bat 用 UTF-8 → cmd.exe 解析崩溃 (置信度: high, 命中: 3)

**Rule**: Claude Code Write 工具创建的 .bat 文件默认 UTF-8 编码（可能带 BOM），cmd.exe 无法正确解析。必须在 bash 中 `cat > file << 'EOF'` 写 .bat 文件，确保 pure ASCII + CRLF。
**现象**: cmd 报 `'65001' 不是内部或外部命令`、`'e' 不是内部或外部命令`（echo. 被截断）、`'Detect' 不是内部或外部命令`（注释被当命令）、`'閫氱敤' 不是内部或外部命令`（中文乱码字节被当命令名）
**Wrong**: Write 工具直接写 .bat → UTF-8 BOM + 多字节字符 → cmd.exe 把 BOM 当命令名 / chcp 65001 命令名被 BOM 污染 / 每行首字符解析错位
**Right**: 纯 ASCII 英文 — 已验证 6 种编码方案（UTF-8/BOM/GBK+chcp/GBK-chcp/GBK-PS/Default），仅纯 ASCII 零故障。
**Wrong（已验证失败）**:
- `chcp 65001` 在 bat 文件内: 解析在 chcp 执行前完成 → 马后炮，无效
- UTF-8 无 BOM: cmd.exe 按 ANSI 解 → 乱码字节含特殊字符 → goto 标签/^ 换行断裂
- UTF-8 + BOM: Git Bash 跨平台写入时 BOM 丢失或 cmd 忽略
- GBK + chcp 65001: 控制台切 UTF-8 显示 GBK 字节 → 屏幕乱码
- GBK (PowerShell 转换, 无 chcp): 用户反馈依旧不行 → GBK 转换也不可靠，纯 ASCII 是唯一稳定解
- `-Encoding Default` via Git Bash PS: Default 映射不可靠
**Why**: cmd.exe 按系统默认代码页（GBK/CP437）逐字节解析批处理文件。UTF-8 BOM (`EF BB BF`) 被读作命令名的一部分 → 第一行 `@echo off` 永久不执行。`chcp 65001` 只改变**控制台输出**编码，不改变**文件解析阶段**编码 — 解析发生在 chcp 执行之前。
**防御**: .bat/.cmd 文件 → 纯 ASCII 英文。写完 `file script.bat` 验证不含 "UTF-8"。
**再次**: 2026-07-07 — 首次用 Write 创建 switch-search.bat → cmd 报 15+ 条"不是内部或外部命令"；用 bash heredoc 重写 → 正常。
**再次**: 2026-07-08 — aaastart.bat 中文注释乱码。Claude 尝试用 `chcp 65001` 修复（已记录的失败路径），用户指出"没用"→ 确认 chcp 无法解决解析阶段编码问题。根因: Phase 1 未加载 lessons-bash.md → 重复踩坑。
**再次**: 2026-07-10 — launcher_template.bat 用户运行不了。Claude 加 `chcp 65001` 后仍失败。根因分析发现：① Write 工具写入 LF 换行，cmd.exe 解析 LF-only 文件可能失败 ② 文件含 `—` (U+2014) `→` (U+2192) 等"伪 ASCII"字符，UTF-8 3 字节在 CP936 下被当双字节汉字解析 → 字符边界错位。

### ★★★ Write 工具写 .bat → LF 换行 → cmd.exe 解析失败 (置信度: high, 命中: 2)

**Rule**: Write 工具创建的文件默认 Unix LF (`\n`) 换行。Windows 批处理文件必须 CRLF (`\r\n`)。写完 .bat 后必须验证 `raw.count(b'\r\n') > 0`。
**现象**: 用户双击 .bat → 大量 `'XXX' 不是内部或外部命令` 错误。关键诊断信号：原命令前缀被吃掉：
- `set "M=..."` → 报 `'M'` 不是内部或外部命令（`set "` 被吃掉）
- `if exist "..."` → 报 `'exist'` 不是内部或外部命令（`if ` 被吃掉）
- `echo.` → 报 `'cho.'` 不是内部或外部命令（`e` 被吃掉）
- `set "VAR=value"` → 报 `'"VAR=value"'` 不是内部或外部命令（`set ` 被吃掉）

此时 `:miss` 显示的 File/Download 行必然为空（变量 `set` 命令从未执行）。
**诊断**:
```python
with open('script.bat', 'rb') as f:
    raw = f.read()
if raw.count(b'\r\n') == 0:
    print('LF-only — 需要转换为 CRLF')
```
**修复**: PowerShell（Windows 原生工具链，最可靠）:
```powershell
$bytes = [System.IO.File]::ReadAllBytes($file)
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
$text = $text -replace "`r`n", "`n"
$text = $text -replace "`n", "`r`n"
[System.IO.File]::WriteAllBytes($file, [System.Text.Encoding]::UTF8.GetBytes($text))
```
**Why**: cmd.exe 按字节流解析 .bat。LF-only 时行边界识别错乱 → 多行合并/截断 → 命令前缀随机丢失 → 变量从未赋值 → 模型文件存在但检测失败。
**注意**: Windows 10 1903+ **声称**部分支持 LF-only，但含 `goto`/label/`^`续行/`%%`转义的复杂脚本必定失败。不要依赖部分兼容性。
**警告**: Git Bash `sed -i` 会自动剥离 CR → 修复后复发。避免用 sed 编辑 .bat；如必须，事后用 PowerShell 重转 CRLF。
**再次**: 2026-07-25 — aaastart.bat 用户报告 LF-only 启动失败（0 CRLF, 339 LF）。此前文档称"能正常运行"是错误的。sed 修复代码后复发 LF → 二次 CRLF 转换解决。

### ★★ "看起来像 ASCII" 的 Unicode 字符 → CP936 解析错位 (置信度: high, 命中: 1)

**Rule**: .bat 文件不只不能有中文——任何 U+0080 以上的字符都是炸弹。包括 em dash `—` (U+2014)、箭头 `→` (U+2192)、弯引号等"看起来像 ASCII 标点"的字符。
**现象**: 脚本静态分析通过、无中文、无 BOM → 但 cmd.exe 解析时行首/关键字符错位 → 随机命令失败
**常见炸弹字符替换表**:
| 字符 | Unicode | 替换 |
|------|---------|------|
| `—` (em dash) | U+2014 | `--` |
| `→` (arrow) | U+2192 | `->` |
| `–` (en dash) | U+2013 | `-` |
| `…` (省略号) | U+2026 | `...` |
| `"` `"` (弯引号) | U+201C/D | `"` |
**诊断**: `all(ord(c) < 128 for c in text)` 必须 True。非 ASCII → 逐字符定位并替换。
**Why**: CP936 (GBK) 是多字节编码。UTF-8 的 `—` = 3 字节 `E2 80 94`，CP936 把 `E2 80` 当双字节汉字、`94` 当下一字符 → 字符边界错位 → 后续所有字节移位 → `"` 和 `%` 边界丢失 → 语法崩溃。
**防御**: 写完 .bat 后执行 `all(ord(c) < 128 for c in open('file.bat', encoding='utf-8').read())` 验证零非 ASCII。

### ★ `chcp 65001` 全 ASCII 脚本不需要 — 反而可能有害 (置信度: medium, 命中: 1)

**Rule**: 若 .bat 已是纯 ASCII → 不加 `chcp 65001`。该命令在某些 Windows 上导致 `pause`/`timeout` 异常。
**Why**: UTF-8 代码页 (65001) 在旧版 Windows 上有已知 bug — `pause` 提示文本显示为乱码或卡死等待按键。

---

## #io — 特殊字符陷阱

### ★★ 变量扩展不加引号 → 分词 + glob (置信度: high, 命中: 2)

**Rule**: `"$var"` 永远双引号包起来。`$var` 不引 = 被 IFS 分词 → 每个词做 glob 扩展。
**Wrong**: `for f in $FILES; do ...` — 文件名含空格 → 被拆成多个"文件"
**Right**: `while IFS= read -r f; do ...; done < <(find . -name "*.txt")` 或用 `"$@"` 遍历参数
**Why**: 引号不是建议，是语法要求。不引 = shell 先按 IFS 切分，再对每个词做 glob。

### ★ 文件名特殊字符 → rm 误删 (置信度: medium, 命中: 1)

**Rule**: 文件名含空格/换行/`-` 开头 → `--` 结束选项 + 引号
**Wrong**: `rm $file` — `$file="-rf"` → `rm -rf` 递归删除
**Right**: `rm -- "$file"` — `--` 表示选项结束，后面全是文件名

### ★ [ condition ] 中变量没引 → 语法错误 (置信度: medium, 命中: 1)

**Rule**: `[ "$var" = "value" ]` 变量永远引起来。空变量不引 → `[ = "value" ]` 语法错误
**Right**: 用 `[[ ]]`（bash 内置，不分裂变量）替代 `[ ]`（POSIX test）

---

## #loop — 循环陷阱

## #llm — llama.cpp 启动脚本

### ★★ 采样参数"一刀切" → RP/翻译/代码用同一套采样器 (置信度: high, 命中: 2)

**Rule**: llama.cpp server 启动脚本中，每个模型必须有独立的启动 block，不能共享 `:run` 子程序。采样参数是模型的"个性"，不是"配置"。
**Wrong**: 所有模型 `goto run` 到一个共享 label → RP 模型和翻译模型被迫共用 temp/top-p/top-k → 翻译不需要 DRY 也被加上了，RP 该用 DRY 却没得用
**Right**: 每模型独立 label（`:peach` `:q36` `:tg12` 等），各自硬编码采样参数。共享的只是 taskkill + 错误处理。
**参数分类原则**:

| 任务类型 | temp | top-p | top-k | min-p | DRY | 理由 |
|----------|------|-------|-------|-------|-----|------|
| RP/创作 | 0.8 | 0.95 | 60 | 0.05 | ✅ 0.7-0.8 | DRY 替代传统 rep_pen，min-p 防乱码 |
| 通用聊天 | 0.8 | 0.95 | 60 | 0.05 | ✅ 0.7 | 新架构(Qwen3.6+)高温表现好 |
| 翻译 | 0.1-0.3 | 0.8-0.9 | - | - | ❌ | 确定性任务，采样器越少越好 |
| 代码 | 0.1-0.2 | 0.9 | - | - | ❌ | 同上，低温 = 准确 |

**VRAM 约束**: 12B 模型 32K ctx 的 KV cache ~5GB → 模型 7.5GB + 5GB + 1GB = 13.5GB > 12GB → 必须降到 20K。**ctx 不是越大越好，是显存放得下才行。**
**Why**: 第一次用统一 `:run` 重构了 bat → 所有模型共享同一条 `llama-server` 命令 → Peach 的 RP 场景被迫用 rep_pen（效果差）→ 用户要求"每个模型参数独立微调"→ 改回独立 block 后，每个模型参数差异清晰、互不影响
**防御**: 写完 bat 后逐模型检查：它的参数是否匹配它的任务类型？翻译模型有没有被加 DRY？RP 模型有没有 min-p？
**再次**: 2026-07-08 — 第一版重构用 `:run` 统一启动 → 用户指出"希望每个模型参数微调，不是统一管理" → 回滚为独立 label，每个模型按任务类型配采样器

### ★★ ERRORLEVEL 被 echo/title 覆盖 → 退出码丢失 (置信度: high, 命中: 2)

**Rule**: .bat 文件中 `%ERRORLEVEL%` 在每个命令后立即刷新（含 `echo`、`title`、`if`、`set`）。`:end` 标签内**第一行必须是 `set "EXIT_CODE=%ERRORLEVEL%"`**，否则退出码被后续 echo/title 覆盖为 0。
**Wrong**:
```bat
:end
title LLM Launcher
echo Server exited with code: %ERRORLEVEL%   REM <- 永远是 0！
```
**Right**:
```bat
:end
set "EXIT_CODE=%ERRORLEVEL%"   REM <- 必须第一行捕获
title LLM Launcher
echo Server exited with code: %EXIT_CODE%
```
**Why**: `%ERRORLEVEL%` 是动态变量，读取时取最后一个命令的退出码。`title` 命令成功后刷新 ERRORLEVEL=0 → 丢掉真实退出码。
**已知退出码**: 见 [llama-cpp-launcher.md](../../../AI-install-and-fix/llama-cpp-launcher.md#llamacpp-退出码速查)
**再次**: 2026-07-25 — aaastart.bat `:end` 添加退出码翻译时发现此坑

### ★ 管道中的循环在 subshell → 变量修改丢失 (置信度: medium, 命中: 1)

**Rule**: `while read; do ... done < <(cmd)`（process substitution）或 `shopt -s lastpipe`
**Wrong**: `cat file | while read line; do count=$((count+1)); done; echo $count` → 打印 0
**Right**: `while read line; do count=$((count+1)); done < file; echo $count`
**Why**: 管道右侧在 subshell 运行。subshell 内变量修改不影响父 shell。
