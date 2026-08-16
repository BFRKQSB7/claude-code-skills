# llama.cpp 启动器脚本 — 模板与排错

> 加载条件: AI 模型启动器 / llama-server 启动脚本 / .bat 菜单 / 多模型切换脚本

**模板文件**: `<llama安装目录>\aaastart.bat`（纯 ASCII 英文，12GB VRAM，5 模型菜单）

---

## 脚本设计原则 ★

| # | 原则 | 说明 |
|:---:|------|------|
| 1 | **纯 ASCII 英文** | cmd.exe 按 ANSI/GBK 解析 .bat，UTF-8 中文 = 乱码/崩溃（见坑0） |
| 2 | **全局变量管理** | 端口、服务器 exe、模型目录统一用变量，改一处全生效 |
| 3 | **缺失模型 → 下载链接** | `:miss` 显示 HF + 国内镜像双链接，用户不用自己搜 |
| 4 | **每个模型独立 label** | 禁止多个模型 `goto` 到同一个 `:run`（翻译和 RP 不能共享采样器） |
| 5 | **`title` 窗口标题** | 选模型后 `title [%M%] %MODE%`，退出/返回菜单时恢复 `title LLM Launcher` |
| 6 | **分离绑定地址与显示地址** | `--host` 传给服务器（`0.0.0.0`），`SHOW_HOST` 给用户看（实际 IP）（见坑7） |

---

## 坑0: .bat 文件编码 → cmd.exe 解析崩溃 ★★★

**现象**: 中文注释/echo 全变乱码，每行报 `'XXX' 不是内部或外部命令`

**根因**: cmd.exe 按系统 ANSI 代码页（中文 Windows=GBK）解析 .bat 文件。UTF-8 多字节字符被拆成随机命令名。`chcp 65001` 只改控制台输出编码，不改进程启动时的文件解析编码——解析在 chcp 执行前完成。

**已验证失败的所有方案**（6 种）:
- `chcp 65001` 在 bat 文件内 → 马后炮
- UTF-8 无 BOM → 乱码
- UTF-8 + BOM → Git Bash 跨平台丢失
- GBK + chcp 65001 → 控制台乱码
- GBK (PowerShell `GetEncoding(936)`) → 依旧不行
- `-Encoding Default` via Git Bash PS → 映射不可靠

**唯一稳定解**: **纯 ASCII 英文**。中文注释全换英文，echo 全英文。经 6 次编码方案验证，仅此方案零故障。

**防御**: 
- .bat 文件只用 ASCII 字符（A-Z a-z 0-9 标点）
- 写完 `file script.bat` 验证不含 "UTF-8"
- Claude Code Write 工具默认 UTF-8 → 全 ASCII 内容不受影响

**追加发现 (2026-07-10) — 即使 "看起来像 ASCII" 也可能有坑**:
- 用 Python 检查：`all(ord(c) < 128 for c in text)` — 必须 100% ASCII
- 常见"伪 ASCII"字符：em dash `—` (U+2014)、箭头 `→` (U+2192)、弯引号
- 这些字符在 UTF-8 中占 2-3 字节，CP936 解析时会被当作双字节汉字，扰乱后续字符边界
- 替换表：`—`→`--`, `→`→`->`, `–`→`-`, `…`→`...`

### 坑0.5: LF 换行 vs CRLF — cmd.exe 解析失败 ★★★

**现象**: 脚本双击后大量 `'XXX' 不是内部或外部命令`，每个报错都是原命令的前几个字符被吃掉：
- `set "M=..."` → `'M'` 不是内部或外部命令
- `if exist "..."` → `'exist'` 不是内部或外部命令
- `if not ...` → `'f'` 不是内部或外部命令
- `echo.` → `'cho.'` 不是内部或外部命令
- `set "JINJA_OK=0"` → `'"JINJA_OK=0"'` 不是内部或外部命令

模型文件存在但变量未设置 → `:miss` 显示的 File/Download 行为空。

**根因**: Claude Code Write 工具写入的文件默认使用 Unix LF (`\n`) 换行。Windows cmd.exe 解析器期望 CRLF (`\r\n`)，遇到 LF-only 时行边界识别错误，导致多行被合并/截断，命令前缀丢失。

**确诊**: **LF 字符数 = CRLF 字符数 × 0**（`raw.count(b'\r\n') == 0`）→ 100% 是此坑。

**诊断**:
```python
with open('script.bat', 'rb') as f:
    raw = f.read()
if raw.count(b'\r\n') == 0:
    print('LF-only — needs CRLF conversion')
```

**修复（PowerShell — Windows 原生工具链，最可靠）**:
```powershell
$bytes = [System.IO.File]::ReadAllBytes($file)
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
$text = $text -replace "`r`n", "`n"
$text = $text -replace "`n", "`r`n"
[System.IO.File]::WriteAllBytes($file, [System.Text.Encoding]::UTF8.GetBytes($text))
```

**注意**: Windows 10 1903+ **声称**支持 LF-only .bat，但实际表现因文件内容复杂度而异——简单单行脚本可能运行，含 `goto`/label/`^`跨行/`%%`转义的复杂脚本必定失败。**不要依赖部分兼容性，一律用 CRLF。**

**警告**: Git Bash 的 `sed -i` 会**自动剥离 CR** → LF-only 复发。修复 .bat 后避免用 sed 编辑，或用 PowerShell 重转 CRLF。

### 坑0.6: `chcp 65001` 不一定需要，反而可能有害 ★★

**现象**: 加了 `chcp 65001` 后，`pause` 命令乱码或卡死，`timeout` 不工作。

**根因**: 
- `chcp 65001` 切换控制台到 UTF-8 代码页，影响后续所有输出
- 如果脚本本身是全 ASCII（无中文），`chcp 65001` 完全多余
- 某些 Windows 版本的 `pause`/`timeout` 在 UTF-8 下行为异常

**原则**: 
- 全 ASCII 脚本 → **不加** `chcp 65001`
- 必须含中文 → 考虑换成英文，而不是靠 chcp

---

## 模板骨架

```bat
@echo off
setlocal enabledelayedexpansion
title LLM Launcher - 12GB VRAM - 5070Ti
cd /d "%~dp0"

REM ========== Global ==========
set "PORT=8080"
set "LLAMA_SERVER=llama-server.exe"
set "MODELS_DIR=models"
if not defined MODE set "MODE=Local" & set "HOST=127.0.0.1"

:menu
title LLM Launcher - 12GB VRAM - 5070Ti
cls
echo ==========================================
echo   LLM Launcher  ^|  12G VRAM  ^|  5070Ti
echo ==========================================
echo.
echo  [1] Model-Name          Category / Use
echo  [2] Another-Model        Category / Use
echo.
echo  [L] Toggle LAN / Local  [Current: %MODE%]
echo  [0] Exit
echo ==========================================

set "choice="
set /p "choice=Enter: "

if "%choice%"=="1"  goto model1
if "%choice%"=="2"  goto model2
if /i "%choice%"=="L" goto toggle_mode
if "%choice%"=="0"  exit /b
echo Invalid.
pause
goto menu

REM ========== LAN/Local toggle ==========
:toggle_mode
if "%MODE%"=="LAN" (set "MODE=Local" & set "HOST=127.0.0.1") else (set "MODE=LAN" & set "HOST=0.0.0.0")
if not defined MODE set "MODE=Local" & set "HOST=127.0.0.1"
goto menu

REM ======================================================================
REM  Model-Name
REM  XB - Q4_K_M - X.XGB - VRAM ~XGB
REM  Parameter notes
REM ======================================================================

:model1
set "M=Model Display Name"
set "F=%MODELS_DIR%\model-filename.gguf"
set "DL=https://hf-mirror.com/ORG/REPO/resolve/main/model-filename.gguf"
set "DL2=https://huggingface.co/ORG/REPO/resolve/main/model-filename.gguf"
if not exist "%F%" goto miss
taskkill /f /im %LLAMA_SERVER% >nul 2>&1
timeout /t 1 /nobreak >nul
title [%M%] %MODE%
echo.
echo [%M%] %MODE% ^| 8K ctx ^| temp 0.8
echo API: http://%HOST%:%PORT%/v1
echo ==========================================
%LLAMA_SERVER% ^
  -m "%F%" ^
  -ngl 999 ^
  --flash-attn on ^
  -c 8192 ^
  -n 512 ^
  --parallel 1 ^
  --temp 0.8 ^
  --top-p 0.95 ^
  --host %HOST% ^
  --port %PORT%
goto end

REM ======================================================================
REM  Error / End handlers
REM ======================================================================

:miss
title LLM Launcher - 12GB VRAM - 5070Ti
echo.
echo ==========================================
echo   Model not found: %M%
echo   File: %F%
echo.
echo   Download:
echo   [Mirror] %DL%
echo   [HF]     %DL2%
echo ==========================================
pause
goto menu

:end
set "EXIT_CODE=%ERRORLEVEL%"
title LLM Launcher - 12GB VRAM - 5070Ti
echo.
echo ==========================================
echo   Server exited with code: %EXIT_CODE%
if "%EXIT_CODE%"=="0" (
    echo   Status: Normal shutdown
) else if "%EXIT_CODE%"=="-1073740791" (
    echo   ERROR: Stack buffer overrun (0xC0000409^)
    echo   Known cause: Broken Gemma3 chat template
    echo   Fix: --chat-template-file "%~dp0gemma_chat_template.jinja"
) else if "%EXIT_CODE%"=="-1073741819" (
    echo   ERROR: Access violation (0xC0000005^)
    echo   Check: Corrupted model file? GPU OOM?
) else if "%EXIT_CODE%"=="-1073741515" (
    echo   ERROR: DLL not found (0xC0000135^)
    echo   Fix: Reinstall CUDA companion zip from llama.cpp release
) else if "%EXIT_CODE%"=="-1073741502" (
    echo   ERROR: DLL init failed (0xC0000142^)
    echo   Check: CUDA driver version compatible?
) else (
    echo   Status: Unknown error
)
echo ==========================================
pause
goto menu
```

**ERRORLEVEL 捕获必须在 `:end` 第一行** — `%ERRORLEVEL%` 在每个命令后刷新（包括 `echo`、`title`），必须立即 `set` 到变量中保存。

## llama.cpp 退出码速查

| 退出码 | 十六进制 | 含义 | 常见原因 | 修复 |
|--------|----------|------|----------|------|
| `0` | `0x0` | 正常退出 | 用户 Ctrl+C 或 `/exit` | — |
| `-1073740791` | `0xC0000409` | Stack buffer overrun | Gemma3 模型内置模板损坏 | `--chat-template-file`（坑2） |
| `-1073741819` | `0xC0000005` | Access violation | 模型文件损坏 / GPU OOM | 重下模型或降 ctx |
| `-1073741515` | `0xC0000135` | DLL not found | 缺 CUDA companion zip | 下载 DLLs zip 合并（坑6） |
| `-1073741502` | `0xC0000142` | DLL init failed | CUDA 驱动不兼容 | 更新显卡驱动 |

**注意**: `-1073740791` 只在 Gemma3 架构模型上出现（TranslateGemma 等）。非 Gemma 模型报此码 → 模型文件损坏。

1. 在 `:menu` 的 echo 区加一行 `echo  [N] Model-Name    Category`
2. 在 `:menu` 的 if 区加 `if "%choice%"=="N"  goto label_name`
3. 在 `:end` 之前加 `:label_name` block，按模板填:
   - `set "M=..."` — 显示名称
   - `set "F=%MODELS_DIR%\..."` — 文件路径（用全局变量 `%MODELS_DIR%`）
   - `set "DL=..."` — hf-mirror.com 国内镜像下载链接
   - `set "DL2=..."` — huggingface.co 原始下载链接
   - 模型专属采样参数（temp, top-p, ctx, n 等 — 翻译和 RP 不能共用）
4. 每个 block 必须独立：**禁止**把多个模型 `goto` 到同一个 `:run` label
5. 下载链接格式: `https://hf-mirror.com/<org>/<repo>/resolve/main/<filename>.gguf`
   - 国内镜像(优先): `DL` = hf-mirror.com
   - 原始站(备用): `DL2` = huggingface.co

完整示例见 `<llama安装目录>\aaastart.bat`。

---

## 启动器配套文件

| 文件 | 路径 | 用途 | 关联模型 |
|------|------|------|----------|
| `aaastart.bat` | `<llama安装目录>\` | 多模型启动菜单脚本 | 全部 |
| `gemma_chat_template.jinja` | `<llama安装目录>\` | Gemma 3 自定义 Jinja 模板 | [1] TranslateGemma-12B |
| `llama-server.exe` | `<llama安装目录>\` | llama.cpp 推理服务器 | 全部 |
| `models\*.gguf` | `<llama安装目录>\models\` | 量化模型文件 | 各自对应 |

**注意**: `gemma_chat_template.jinja` 是 TranslateGemma-12B 的**必需**配套文件。缺少时模型启动即崩溃（0xC0000409）。模板内容见坑2。

---

## 采样参数速查

### 按任务类型

| 任务 | temp | top-p | top-k | min-p | DRY | 说明 |
|------|------|-------|-------|-------|-----|------|
| RP/角色扮演 | 0.8 | 0.95 | 60 | 0.05 | ✅ | DRY 替代传统 rep_pen |
| 通用聊天 | 0.8 | 0.95 | 60 | 0.05 | ✅ | 高温 + DRY |
| 翻译 | 0.1-0.3 | 0.8-0.9 | - | - | ❌ | 确定性任务，采样器越少越好 |
| 代码生成 | 0.1-0.2 | 0.9 | - | - | ❌ | 极低温 = 准确 |

### 参数含义

| 参数 | 作用 | 常用值 |
|------|------|--------|
| `--temp` | 随机度。高=创意，低=确定 | RP 0.8, 翻译 0.1-0.3 |
| `--top-p` | 核采样阈值。只从累积概率 top P% 的 token 中选 | 0.8-0.95 |
| `--top-k` | 只从概率最高的 K 个 token 中选 | RP 40-60, 翻译不用 |
| `--min-p` | token 概率低于此值直接丢弃，防乱码 | 0.05 |
| `--repeat-penalty` | 惩罚已出现过的 token | 1.0=禁用 (DRY 替代) |
| `--dry-multiplier` | DRY 惩罚强度 | RP 0.7-0.8 |
| `--dry-base` | DRY 基础值 | 1.75 |
| `--dry-allowed-length` | 允许重复的最长短语（token 数） | 2 |
| `--dry-penalty-last-n` | DRY 回溯范围，-1=全部 | -1 |

### DRY vs rep_pen

- `--repeat-penalty` 惩罚所有重复 token → RP 中"他说""她说"被误伤
- DRY (`--dry-*`) 只针对**短语级**重复 → 短词自由重复，长句防止复读
- 两者互斥：用 DRY 时设 `--repeat-penalty 1.0`（即禁用）

---

## Context 上限速查（12GB VRAM）

| 模型大小 | 安全 ctx | KV 估算 | 总显存 |
|----------|---------|--------|--------|
| 7-9B | 32K | ~1.5 GB | ~7 GB |
| 12B | 20K | ~3 GB | ~11 GB |
| 14B | 16-20K | ~3.5 GB | ~11.5 GB |

**公式**: `模型文件 + (ctx/1000 × 0.12~0.18)GB + 1.5GB < 12GB`

错误示范：12B 模型设 32K → KV 4.8GB → 7.5+4.8+1.5 = 13.8 > 12 → OOM。

---

## 坑1: --flash-attn 不写值 → 吃掉下一个参数 ★★★

**现象**: 
```
error while handling argument "--flash-attn": error: unknown value for --flash-attn: '-c'
```

**根因**: 新版 llama.cpp 的 `--flash-attn` **必须**带值（`on`/`off`/`auto`）。旧版允许裸写默认 `auto`，新版严格校验。不加值时，下一行的 `-c 4096` 被当作值传入，`-c` 不是有效值所以报错。

**修复**: 所有 `--flash-attn` 改为 `--flash-attn on`（或 `auto`）。

**影响范围**: 任何用了 `--flash-attn ^` 裸写的 bat 脚本，所有模型入口都受影响。

**注意**: 删除参数时如果留下空白行，cmd.exe 的 `^` 续行符会被打断 → `error: invalid argument:`。确保 `llama-server.exe ^` 到 `goto end` 之间没有空行。

---

## 坑2: Gemma 3 模型栈溢出崩溃 (0xC0000409) ★★★

**现象**:
- 服务器加载模型后立即退出，无任何错误信息
- `echo %ERRORLEVEL%` 显示 `-1073740791` (= `0xC0000409` = `STATUS_STACK_BUFFER_OVERRUN`)
- 日志最后一行: `W render_message_to_json: Neither string content nor typed content is supported by the template`

**根因**: TranslateGemma 等 Gemma 3 架构模型的 GGUF 内置聊天模板损坏。llama.cpp 在初始化时调用 `render_message_to_json` 尝试验证模板，模板解析触发栈缓冲区溢出（C 代码级崩溃，非配置问题）。

**影响范围**: 已知 TranslateGemma-12B (mradermacher GGUF, b9873)，其他 Gemma 3 衍生模型也可能触发。

**修复步骤**:
1. 移除 `--jinja` 参数（防止强制使用损坏的内置模板）
2. 创建 `gemma_chat_template.jinja`（位于 `<llama安装目录>\`，内容见下）
3. 在启动参数中添加 `--chat-template-file "%~dp0gemma_chat_template.jinja"`

**模板内容** (`<llama安装目录>\gemma_chat_template.jinja`):
```
{{ bos_token }}{% for message in messages %}{% if message['role'] == 'user' %}<start_of_turn>user
{{ message['content'] }}<end_of_turn>
{% elif message['role'] == 'assistant' %}<start_of_turn>model
{{ message['content'] }}<end_of_turn>
{% endif %}{% endfor %}{% if add_generation_prompt %}<start_of_turn>model
{% endif %}
```

**已验证**: llama.cpp v9873 + TranslateGemma-12B-Q4_K_M + RTX 5070 Ti，自定义模板后正常运行，54 tok/s。

**注意**: 模板文件中的 `{%` 和 `%}` 在 .bat 脚本中会被 cmd.exe 解析为变量。不要 inline 写入 bat，用 `--chat-template-file` 指向独立文件。

**自动修复**: `aaastart.bat` 的 `:tg12` 段已内置自检逻辑——每次启动前用 `findstr` 检查 jinja 文件是否存在且包含 `<start_of_turn>model`，缺失或损坏时自动重新生成。无需手动维护。

**在 .bat 中正确写入 jinja 的方法**(供参考):
```bat
> "%JINJA_FILE%" echo {{ bos_token }}{%% for message in messages %%}{%% if message['role'] == 'user' %%}^<start_of_turn^>user
>>"%JINJA_FILE%" echo {{ message['content'] }}^<end_of_turn^>
```
- `{%%` → 输出 `{%`
- `%%}` → 输出 `%}`
- `^<` → 输出 `<`
- `^>` → 输出 `>`

**扩展影响**: `--jinja` 参数本身也会导致多个模型（Peach、Qwen Heretic 等）推理时卡死（/v1/models 正常但 /v1/chat/completions 无限挂起）。**建议所有模型都不要使用 `--jinja`**，llama.cpp 默认会自动检测模板引擎。

---

## 坑3: --min-p 过高 → 标点符号丢失 ★★

**现象**: RP 模型回复没有逗号、句号、引号等标点符号，文字连成一片。

**根因**: min-p 过滤掉概率低于 `最高概率 × min-p` 的 token。标点符号（，。！？）的概率通常远低于内容词，`--min-p 0.05` 会将其过滤。中文标点的概率尤其低（词表占比小）。

**修复**: 将 `--min-p` 从 0.05 降到 0.02。对 RP/创意写作推荐 0.02-0.03。

**注意**: SillyTavern 的 "Sampler Select" 如果没选 "Default"，会用酒馆的采样器**覆盖**服务器参数，标点问题可能出在酒馆那边。先检查 ST 的 Min-P 设置。

---

## 坑4: 删除参数留空行 → ^ 续行符断裂 ★

**现象**: `error: invalid argument:`（冒号后无内容）

**根因**: 用 Edit 工具删除 `--jinja ^` 行时，内容删了但留下了空白行。cmd.exe 的 `^` 续行符只能转义紧随其后的换行符；中间有空行会打断续行，后续参数被当作新命令执行。

**修复**: 确保每个 `llama-server.exe ^` 到 `goto end` 之间没有空白行。批量替换后要肉眼检查。

---

## 坑5: 加载角色卡后 AI 重复无意义内容 ★★

**现象**: SillyTavern 加载角色卡后，模型不停重复同一个词/短语，或输出乱码。

**根因（三选一或多重）**:

1. **ST 采样器覆盖了 DRY**（最常见）: ST 的 Sampler Select ≠ Default 时，用酒馆采样参数替代服务器参数，但 ST 不会发送 DRY 参数。没了 DRY 反重复机制，模型必然复读。

2. **上下文溢出**: 角色卡（设定+示例+世界书）通常在 1-3K tokens，加上聊天记录很容易超出 8K 上限。溢出后 KV 缓存截断，模型丢失前面的关键信息开始胡言乱语。

3. **Temp 偏高**: 长上下文 + `--temp 0.8` 容易发散。

**修复**（按优先级）:
1. SillyTavern → 预设 → Sampler Select → **Default**（让服务器端 DRY 生效）
2. 加大 `-c`：8K → 12K（9B 模型 12GB 显存放得下，KV 增加约 1GB）
3. 降低 `--temp`：0.8 → 0.7
4. 在 ST 中检查 Context 用量指示器，确认是否接近上限

---

## 坑6: llama.cpp Release 页 CUDA 版本有两个 zip — 只下一个 → 缺 DLL ★★★

**现象**: 启动 llama-server.exe 时报 `找不到 cudart64_12.dll` 或 `找不到 cudart64_13.dll`。

**根因**: llama.cpp Release 页每个 CUDA 版本有**两个** zip 文件：
- 主程序：`llama-bXXXX-bin-win-cuda-12.4-x64.zip`
- DLLs（companion）：`cudart-llama-bin-win-cuda-12.4-x64.zip`

两个文件大小相同（~373 MB），很多人以为随便选一个就行。实际上主程序 zip 不含 CUDA 运行时 DLL，DLLs zip 不含可执行文件。**两个都要下载，解压后合并到同一目录。**

**正确做法**:
1. 下载主程序 zip → 解压
2. 下载 DLLs zip → 解压
3. 把两个解压出来的文件放到同一个文件夹
4. `llama-server.exe` 和 `cudart64_*.dll` 必须在同一目录

**文件名速查**（版本号会随 Release 更新）:
| CUDA 版本 | 主程序 | DLLs |
|-----------|--------|------|
| CUDA 12 | `llama-bXXXX-bin-win-cuda-12.4-x64.zip` | `cudart-llama-bin-win-cuda-12.4-x64.zip` |
| CUDA 13 | `llama-bXXXX-bin-win-cuda-13.3-x64.zip` | `cudart-llama-bin-win-cuda-13.3-x64.zip` |
| Vulkan | `llama-bXXXX-bin-win-vulkan-x64.zip` | 无（Vulkan 只需 1 个文件） |

**再次**: 2026-07-10 — 部署指南初版只写"下载一个 zip 文件，取出 llama-server.exe"，未提及 DLLs companion 文件。用户指出每个 CUDA 版本有两个文件。已修正部署指南 §1.2 为两文件下载 + 合并流程。

---
---

## 坑7: LAN 模式 API 显示 `0.0.0.0` → 用户不知道实际连接地址 ★★

**现象**: LAN 模式下脚本窗口显示 `API: http://0.0.0.0:8080/v1`，局域网其他设备上的用户不知道应该填什么 IP。

**根因**: `0.0.0.0` 是**绑定地址**（告诉 llama-server 监听所有网卡），不是**可连接地址**。其他设备不能用 `0.0.0.0` 发起连接——必须用服务器的实际局域网 IP（如 `<局域网IP>`）。

**修复**（分离 HOST 和 SHOW_HOST）:
1. 初始化时用 `ipconfig` 自动检测本机 LAN IP：
```bat
set "LAN_IP="
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr /v "127.0.0"') do (
    if not defined LAN_IP (
        set "T=%%a"
        set "LAN_IP=!T: =!"
    )
)
if not defined LAN_IP set "LAN_IP=0.0.0.0"
```
2. 新增 `SHOW_HOST` 变量：`HOST` 传给 llama-server（绑定地址），`SHOW_HOST` 给用户看（实际 IP）
3. `:toggle_mode` 切换时同步更新 `SHOW_HOST`
4. 所有 `echo API: http://%HOST%:%PORT%/v1` 改为 `echo API: http://%SHOW_HOST%:%PORT%/v1`

**设计原则**: **永远把"绑定地址"和"显示地址"分开**——`--host` 参数和用户看到的 API 地址是两个不同概念。

**防御**: 启动脚本中任何对外显示的地址，必须是用户可以直接复制粘贴使用的实际 IP，不能是 `0.0.0.0`。

---

## 其他常见坑

| # | 坑 | 修复 |
|---|-----|------|
| LAN 模式显示 0.0.0.0 | 用户不知道实际连接地址 | 分离 HOST/SHOW_HOST，自动检测 LAN IP |
| --flash-attn 无值 | 报 `unknown value: '-c'` | 改成 `--flash-attn on` |
| --flash-attn 无值 | 报 `unknown value: '-c'` | 改成 `--flash-attn on` |
| Gemma3 模型崩溃 | 退出码 -1073740791 | 自定义 `--chat-template-file`（见坑2） |
| 标点符号丢失 | RP 模型回复无标点 | `--min-p` 降到 0.02（见坑3） |
| 删参数留空行 | `error: invalid argument:` | 去掉 ^ 续行块中的空白行（见坑4） |
| 端口占用 | Steam 占 8080 | `netstat -ano \| grep PORT` → `taskkill /F /PID X` |
| GPU 卸载不足 | 推理 <1 t/s | `-ngl 999`（全 GPU），大模型按需减 |
| 并发排队 | `--parallel 1` | 12GB 最多 `--parallel 2`，再高 OOM |
| SillyTavern 连接 | 连不上 | API Type=Chat Completion, URL=`http://127.0.0.1:8080/v1`, Key 随便填 |
| 多轮对话静默 | context 溢出 | 减小搜索结果/缩短 ctx/开新对话 |
