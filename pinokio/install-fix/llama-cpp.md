# llama.cpp 本地推理排错

llama-server 通过启动脚本运行，被 Open WebUI 作为外部 API 调用。

**启动脚本菜单**: Local / Local+MCP / LAN（无 LAN+MCP——MCP 是 Open WebUI 层面的功能，直连 API 不走工具层）。MCP 网页抓取桥接 → 见 [Open WebUI](open-webui.md) 坑5。

> 相关文件: [SearXNG](searxng.md) · [Open WebUI](open-webui.md)

---

## 坑1: 端口被占用

**现象**: `bind: address already in use` 或无法绑定端口

**根因**: Steam（steamwebhelper.exe）常驻 8080，其他服务也可能抢占常用端口。已记录的冲突：
- 端口 8080 → Steam / 其他 llama 实例
- 端口 8000 → NeatReader / 其他桌面软件

**修复**:
```bash
netstat -ano | grep <端口>        # 找占用 PID
taskkill /F /PID <PID>            # 杀掉
```
或改 `--port` 参数换端口。

---

## 坑2: GPU 卸载不足导致推理极慢

**现象**: 模型加载成功但生成 <1 t/s

**根因**: `-ngl` 太低，大部分层跑在 CPU/RAM。RTX 5070 Ti 12GB VRAM。

**修复**: 按模型大小调 `-ngl`：
```bat
# Qwen3.6-35B-A3B (MoE, IQ4_XS, ~19GB):
-ngl 22    # 22/40 layers GPU, 其余 RAM

# Qwen3.5-9B (Dense, Q4_K_M, ~5.3GB):
-ngl 999   # 全部 GPU

# Qwen2.5-Coder-14B (Q4_K_M, ~8.4GB):
-ngl 999   # 全部 GPU
```
`-ngl 999` = 全上 GPU。N = 只卸载 N 层，其余在 RAM。

---

## 坑3: Context 不够 → 生成截断 / 第二轮不输出

**现象 A — 生成截断**: 回答一半被 cancel
```
W srv stop: cancel task, id_task = 5198
I slot release: stop processing: n_tokens = 7527, truncated = 0
```

**现象 B — 第二轮静默**: 第一轮搜索+回答正常，第二轮搜到结果但模型不生成任何文字

**根因**: 多轮对话 context 累积 + 搜索结果 → 超出 `-c` 限制。现象 A = 刚刚溢出仍尝试输出；现象 B = 严重溢出模型直接放弃

**修复**（组合拳）:
1. `-c 65536` → `-c 131072`（9B 模型 128K ≈ 3GB KV cache，12GB 显卡够）
2. `-n 8192` → `-n 16384`（输出也翻倍）
3. 减 SearXNG 引擎到 2 个（去 360search）→ 见 [SearXNG](searxng.md)

**推荐 9B + 12GB 配置**:
```bat
-c 131072 -n 16384 -ngl 999
```

---

## 坑4: --parallel 并发限制

**现象**: Open WebUI 同时发多个请求时排队/超时

**根因**: `--parallel 1` 只允许 1 个并发请求

**修复**: 如果 VRAM 够，可调高：
```bat
--parallel 2      # 允许 2 并发
```
注意：并发翻倍 → VRAM 占用翻倍。

---

## 坑5: 采样参数一刀切 → RP 重复/翻译漂移

**现象**: 
- RP/角色扮演: 回复重复、同义反复、句式单调
- 翻译: 输出不稳定、同一句翻两次结果不同

**根因**: 所有模型共用同一套采样参数（rep_pen + top-k），不区分任务类型。

**修复**: 按任务类型配不同采样器链：

| 任务 | temp | top-p | top-k | min-p | DRY |
|------|------|-------|-------|-------|-----|
| RP/创作 | 0.8 | 0.95 | 60 | 0.05 | ✅ |
| 通用聊天 | 0.8 | 0.95 | 60 | 0.05 | ✅ |
| 翻译 | 0.1-0.3 | 0.8-0.9 | - | - | ❌ |
| 代码 | 0.1-0.2 | 0.9 | - | - | ❌ |

**DRY 替代传统 rep_pen 的原理**:
- `--repeat-penalty` 惩罚所有重复 token，不管位置/频率 → RP 对话中"他说""她说"被误伤
- `--dry-multiplier 0.7-0.8` + `--dry-base 1.75` + `--dry-allowed-length 2` → 只针对短语级重复，短词自由重复
- DRY 和 rep_pen 互斥 — 用 DRY 时设 `--repeat-penalty 1.0`

RP/聊天推荐 DRY 参数:
```bat
--temp 0.8 --top-p 0.95 --top-k 60 --min-p 0.05 ^
--dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 2 --dry-penalty-last-n -1
```

翻译/代码不需要 DRY — 确定性任务采样器越少越好。

---

## 坑6: 大模型长上下文 → KV Cache 爆显存（静默）

**现象**: 12B 模型设 `-c 32768`，加载成功，但跑几轮后 OOM 崩溃或系统卡死。没有明显错误提示。

**根因**: 只看模型文件大小（7.5GB），没算 KV Cache。**KV Cache 随 ctx 线性增长，模型越大增长越快。**

**12GB 显存下各模型安全 ctx 上限**:

| 模型大小 | 安全 ctx | KV Cache 估算 | 总显存估算 |
|----------|---------|--------------|-----------|
| 7-9B | 32K | ~1.5 GB | ~7 GB |
| 12B | **20K** | ~3 GB | ~11 GB |
| 14B | **20K** | ~3.5 GB | ~11.5 GB |

**公式**: `模型文件 + (ctx/1000 × 0.12~0.18)GB + 1.5GB < 12GB`
12B 模型在 0.15 GB/K-token → 32K = 4.8GB KV → 7.5+4.8+1.5 = 13.8 > 12 ❌

**修复**: 12B/14B 模型 ctx 从 32K 降到 16-20K。对 RP/翻译场景感知不到差异。

---

## 坑7: SillyTavern 连接 llama-server 配置

**现象**: SillyTavern 连不上本地 llama-server

**修复**:
1. llama-server 启动后用 OpenAI 兼容 API：
   ```
   API Type:       Chat Completion
   API:            OpenAI (或 Custom)
   API Key:        sk-test（随便填）
   API URL:        http://127.0.0.1:8080/v1
   ```
2. 不需要代理、不需要 Ollama。llama-server 自带 `/v1/chat/completions` 端点
3. 端口必须一致（bat 里 `--port` 和 SillyTavern 填的端口）

**推荐 SillyTavern 采样参数**（Peach-2.0-9B RP）:
```
Temperature: 0.8 | Top-P: 0.95 | Top-K: 60 | Min-P: 0.05
DRY: multiplier 0.8, base 1.75, allowed length 2
Repetition Penalty: 1.0 (disabled — DRY handles it)
```
