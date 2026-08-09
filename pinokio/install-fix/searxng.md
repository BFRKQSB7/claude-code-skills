# SearXNG @ Pinokio 安装排错

SearXNG 通过 Pinokio 脚本 `cocktailpeanut/searxng.pinokio` 安装。

> 相关文件: [Open WebUI](open-webui.md) · [llama.cpp](llama-cpp.md)

---

## 引擎切换脚本

项目根目录提供 `switch-search.bat`，一键切换国内/国外搜索引擎：

```
双击 switch-search.bat → 选 1(国内) 或 2(国外) → 重启 SearXNG
```

两套配置文件：
- `settings-cn.yml` — 国内引擎 (sogou + 360search + bing)，无需代理
- `settings-intl.yml` — 国外引擎 (Google 为主 + Bing + DuckDuckGo + Startpage)，需代理
- `settings.yml` — 当前生效的配置（脚本自动覆盖）

**代理要求**: 国外配置需开 **TUN 模式代理**（非系统代理），因为 Python httpx 不自动读 Windows 系统代理设置。如果用系统代理需在 `start.js` 显式传 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量。

---

## 坑1: CUDA/VS Build Tools 依赖卡死

**现象**: 安装到 10/14 时卡在 "Installing CUDA and cuDNN libraries"，conda SSL 报错 `SSLEOFError` / `ASN1: NOT_ENOUGH_DATA`

**根因**: `install.js` 中 `requires: { bundle: "ai" }` 触发 Pinokio 自动安装 CUDA + VS Build Tools。conda Python SSL 模块无法加载 Windows 证书存储，所有 conda 网络操作失败。

**修复**: 编辑 `install.js`，删除 `requires` 块：
```js
// 改前
module.exports = {
  requires: { bundle: "ai" },
  run: [...]
}
// 改后
module.exports = {
  run: [...]
}
```
然后用系统 Python（非 conda）创建 venv 安装依赖：
```bash
D:/python/python.exe -m venv env
env/Scripts/pip install -r app/requirements.txt -r app/requirements-server.txt
env/Scripts/pip install -e app/. --no-build-isolation
```

---

## 坑2: 国外搜索引擎全部超时

**现象**: 搜索返回 0 结果，日志 `ERROR:searx.engines.duckduckgo: HTTP requests timeout`
```
Results: 0, Unresponsive: [['duckduckgo', 'timeout'], ['google cse', 'timeout'], ['startpage', 'timeout'], ['wikidata', 'timeout'], ['wikipedia', 'timeout']]
```

**根因**: 国内网络无法直连 Google、DuckDuckGo、Wikipedia 等搜索引擎。

**修复**: 用 `keep_only` 只保留国内引擎（sogou、360search、bing）：
```yaml
# settings.yml
use_default_settings:
  engines:
    keep_only:
      - sogou
      - 360search
      - bing

engines:
  - name: sogou
    disabled: false
  - name: 360search
    disabled: false
  - name: bing
    disabled: false
```
注意：`disabled: false` 必须显式写，默认均为 `disabled: true`。

---

## 坑3: shortcut: 360 被 YAML 解析为 int

**现象**: `/preferences` 页面 500，日志 `jinja2.exceptions.UndefinedError: 'int object' has no attribute 'replace'`

**根因**: YAML 中 `shortcut: 360` 被解析为整数，Jinja2 模板调用 `.replace()` 崩溃。整个偏好页和默认引擎选择链断裂 → 搜索返回 0 条。

**修复**: 引号包裹：
```yaml
  - name: 360search
    shortcut: "360"   # 必须引号，否则 YAML 当成 int
```

---

## 坑4: Pinokio start.js 启动失败

**现象**: 点 Start 后报错 `'..' 不是内部或外部命令，也不是可运行的程序`

**根因**: Pinokio 在 Windows 上用 cmd.exe 执行命令，cmd 不认识 `/` 作为路径分隔符，把 `../env/Scripts/python.exe` 当成命令 `..`。

**修复**: `start.js` 用反斜杠 + 显式 Python 路径 + 硬编码 URL：
```js
// start.js
module.exports = {
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        env: {
          SEARXNG_SETTINGS_PATH: "{{path.resolve(cwd, 'settings.yml')}}",
          // ...其他 env
        },
        path: "app",
        message: [
          "..\\env\\Scripts\\python.exe ..\\start_searxng.py"  // cmd.exe 必须反斜杠
        ],
        on: [{ event: "/http:\\/\\/127.0.0.1:8081/", done: true }]
      }
    },
    {
      method: "local.set",
      params: { url: "http://127.0.0.1:8081" }  // 硬编码，不用 {{input.event[1]}}
    }
  ]
}
```

---

## 坑5: venv_python 版本不匹配

**现象**: Pinokio 启动时找不到模块 `ModuleNotFoundError: No module named 'werkzeug'`

**根因**: `start.js` / `install.js` 中 `venv_python: "3.11"` 与实际 venv 的 Python 3.14 不匹配。Pinokio 可能尝试用 conda Python 3.11 重建环境，但 conda Python SSL 已坏。

**修复**: 统一改为实际 Python 版本：
```js
venv_python: "3.14"  // install.js / start.js / start_debug.js / update.js 都要改
```

---

## 坑6: `venv` 参数导致 conda 干扰

**现象**: 即使 venv 里有 werkzeug，Pinokio 启动仍报 `ModuleNotFoundError`

**根因**: Pinokio 的 `venv: "env"` 参数在 cmd.exe 中先执行 `conda_hook & conda activate base`，conda base 的 Python 覆盖了 venv 的 PATH。

**修复**: 删除 `venv` 和 `venv_python` 参数，直接用 venv 的绝对路径：
```js
message: ["..\\env\\Scripts\\python.exe ..\\start_searxng.py"]
```

---

## 坑7: `use_default_settings: false` 缺必填项

**现象**: 搜索返回 500，日志 `KeyError: 'default_doi_resolver'`

**根因**: `use_default_settings: false` 关闭了所有默认设置，缺少 `default_doi_resolver` 等必要字段。

**修复**: 用 `keep_only` 过滤引擎，而非关闭全部默认设置。
