# Open WebUI @ Pinokio 安装排错

Open WebUI 通过 Pinokio 安装，连接本地 llama.cpp 推理后端。

> 相关文件: [SearXNG](searxng.md) · [llama.cpp](llama-cpp.md)

---

## 坑1: HuggingFace 模型下载卡住

**现象**: 启动后 embedding 模型下载进度条不动

**根因**: 国内直连 huggingface.co 极慢或被阻断

**修复**: 在 `ENVIRONMENT` 文件添加 HF 镜像：
```
HF_ENDPOINT=https://hf-mirror.com
```
重启 Pinokio 生效。

---

## 坑2: 联网搜索后回答截断

**现象**: 模型生成到一半被 cancel
```
W srv stop: cancel task, id_task = 5198
```

**根因**: SearXNG 搜索结果 + 对话历史超出 llama.cpp context

**修复**:
1. 减 SearXNG 引擎 → 见 [SearXNG](searxng.md)
2. 增 context / 输出 token → 见 [llama.cpp](llama-cpp.md) 坑3
3. Open WebUI 管理后台 → 增大 API timeout

---

## 坑3: 第二轮对话搜索正常但不输出回答

**现象**: 第一轮联网搜索+回答正常，第二轮搜到结果但模型不生成任何文字

**根因**: 多轮 context 累积溢出。第一轮（提问 + 搜索结果 + 回答）+ 第二轮（提问 + 搜索结果）→ 超出 llama.cpp `-c` 限制 → 模型静默不输出

**修复**:
1. **扩大 context**: `-c 65536` → `-c 131072`（9B 模型 128K ≈ 3GB KV cache，12GB 显存够）
2. **增大输出**: `-n 8192` → `-n 16384`
3. **减少引擎**: SearXNG 3 引擎 → 2 引擎（去 360search）→ 见 [SearXNG](searxng.md)

**推荐 9B + 12GB 配置**:
```bat
-c 131072 -n 16384 -ngl 999
```
SearXNG `keep_only` 只留 2 个引擎。Results Count 默认 3 即可无需改。

---

## 坑4: exFAT 驱动器警告

**现象**: Pinokio 弹出 "exFAT drives often break permissions/metadata"

**根因**: exFAT 不支持 Unix 权限和符号链接

**修复**: Pinokio 目录放 NTFS 分区。

---

## 坑5: 模型无法获取网页正文（MCP 抓取）

**现象**: 模型 fetch URL 返回 `{"error": "The URL you provided is invalid..."}` — Open WebUI 内置 web loader 对非主流 TLD（如 `.blog`）校验过严

**根因**: Open WebUI 的 URL fetcher 有严格的 URL 格式校验，`.blog` 等非主流 TLD 被误判。

**修复**: 用 MCP Streamable HTTP 桥接脚本暴露 `mcp-server-fetch`：

```bash
pip install mcp-server-fetch
```

桥接用 FastMCP 的 `run_streamable_http_async()`（**不是** `mcpo`）：

```python
# 关键设置
mcp.settings.streamable_http_path = "/"   # 根路径
mcp.settings.stateless_http = True        # 无状态模式
mcp.settings.json_response = True         # JSON 响应
```

**Open WebUI 配置**:

Admin → External Tools → Add → `http://127.0.0.1:8000` / Type: MCP (Streamable HTTP) / Auth: None

**持久化**: 启动脚本中 35B/9B 模型各有 `+MCP` 变体选项，选之自动拉起桥接 → 见 [llama.cpp](llama-cpp.md)

### 绕过 Cloudflare / 反爬保护

`mcp-server-fetch` 默认用 `httpx` + `ModelContextProtocol` UA，Cloudflare 站点直接 403。

**修复**: 用 `curl_cffi` 替代 `httpx`，模拟 Chrome TLS 指纹：

```bash
pip install curl_cffi
```

```python
from curl_cffi.requests import AsyncSession

async with AsyncSession(impersonate="chrome131", timeout=30.0) as session:
    response = await session.get(url)
```

已验证可绕过: javdb.com (Cloudflare), Wikipedia, GitHub, Baidu

### 为什么不能用 mcpo

`mcpo` 是 OpenAPI REST 代理 — 它把 MCP 工具转成 `POST /fetch` 这种 REST 端点，不是 MCP Streamable HTTP 协议。Open WebUI 的 "MCP (Streamable HTTP)" 类型需要真正的 MCP 端点。

验证方法：
```bash
curl -s -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
# 正确返回: {"jsonrpc":"2.0","id":1,"result":{"tools":[...]}}
# mcpo 返回: {"detail":"Not Found"}  或 OpenAPI JSON
```

**注意**: `Accept` 头必须同时包含 `application/json` 和 `text/event-stream`，缺一返回 406。

---

## 坑6: MCP 已添加但模型仍用内置工具

**现象**: 桥接正常、External Tools 已添加 MCP，但模型始终调用内置 `fetch_url`（报 URL invalid）而非 MCP 的 `fetch`

**根因**: 之前用 `mcpo` 时 Open WebUI 在数据库写入了 `"path": "openapi.json"` + `"spec_type": "url"`，换成 MCP Streamable HTTP 后这两个字段没清掉 → Open WebUI 仍尝试 OpenAPI 发现而非 MCP 协议

**修复**: 直接改 Open WebUI 数据库：

```bash
# 查当前配置
python -c "
import sqlite3, json
db = 'open_webui/data/webui.db'
conn = sqlite3.connect(db)
row = conn.execute(\"SELECT value FROM config WHERE key='tool_server.connections'\").fetchone()
print(row[0])
conn.close()
"
```

把 `"path": "openapi.json"` → `"path": ""`，`"spec_type": "url"` → `"spec_type": ""`。改完重启 Open WebUI。

**预防**: 如果用 `mcpo` 切到真正的 MCP 端点，直接在 Open WebUI 管理界面删掉旧工具重建，别复用同一条记录。

---

## 坑7: 模型仍优先选内置 web loader 而非 MCP fetch

**现象**: MCP fetch 工具可用，但模型在搜索后仍尝试调用内置 `fetch_url` 抓页面，不经过 MCP

**根因**: `utils/tools.py` 第 590 行把 `search_web` 和 `fetch_url` 绑在一起注册，web_search 启用时两个工具都会暴露给模型。模型看到 `fetch_url`（内置）和 `1_fetch`（MCP）两个选项，有时选错。

**修复**: 从内置工具列表中移除 `fetch_url`，只留 `search_web`：

```python
# open_webui/utils/tools.py 第 590 行
# 改前:
builtin_functions.extend([search_web, fetch_url])
# 改后:
builtin_functions.extend([search_web])  # fetch_url removed — use MCP fetch instead
```

**配合**: `web.search.bypass_web_loader = true`，搜完不自动抓页面。改完重启 Open WebUI。

**注意**: 更新 Open WebUI 后此修改会被覆盖，需重新改。

---

## 坑8: MCP fetch 报 TLS/SSL 错误但网站存在

**现象**: `fetch` 返回 `curl: (35) TLS connect error: error:00000000:invalid library (0):OPENSSL_internal:invalid library (0)`

**根因**: DNS 被 sinkhole 到 `198.18.0.0/15`（RFC 2544 测试网段）。域名不存在或被运营商/防火墙拦截，DNS 返回 bogon IP。

**诊断**:
```bash
nslookup <域名>
# 如果返回 198.18.x.x → DNS sinkhole，不是 TLS 问题
```

**不是 bridge 的问题**——bridge 用 `curl_cffi` 模拟 Chrome TLS 指纹，正常站点都能过。模型自己编的 URL 404 或 DNS 污染才是常见原因。

**对策**: 让模型先 `search_web` 搜到真实 URL，再 `1_fetch` 抓。避免直接猜 URL。

---

## 坑9: 模型抓完网页后不输出回答

**现象**: 模型调用 `1_fetch` 成功拿到网页内容，但之后不生成任何文字回答（输出为空）

**根因**: 
1. **小模型（9B/35B-MoE 3B 活跃）推理能力弱**——拿到大量抓取内容后不知道"该总结了"，反复 fetch 直到 context 爆满
2. **默认 max_length=5000 太大**——单次抓取占 ~2000 tokens，多轮累积撑爆 128K context
3. **35B MoE 实际只活跃 3B 参数**——知识存储大但推理能力 ≈ 3B 模型

**修复**:
1. **降低默认 max_length**: bridge 默认 `5000` → `2000`，减少每次抓取的 context 占用
2. **系统提示词加约束**: "每次对话最多抓取 3 个页面，之后必须基于已获取的内容总结回答，不要反复尝试"
3. **换 9B Dense 模型**（全量 9B 参数参与推理，判断力比 35B MoE 的 3B 活跃强）

**注意**: 此问题在 9B Dense 和 35B MoE 上都会出现，是本地小模型的固有局限。大模型（GPT-4/Claude）的推理能力才能很好地处理"搜索→抓取→总结"的完整链路。
