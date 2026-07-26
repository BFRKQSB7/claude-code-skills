---
name: AI-install-and-fix
description: 本地 AI 工具安装排错指南。记录 Pinokio、Open WebUI、SearXNG、llama.cpp 等工具的安装坑和修复方法。当用户提到安装本地 AI 模型、配置 AI 工具遇到报错、Pinokio 安装失败、SearXNG 搜索无结果、联网搜索配置、AI 模型启动器、llama-server 启动脚本、.bat 菜单脚本、多模型切换等问题时使用。
---

# AI 工具安装排错索引

记录折腾本地 AI 模型和工具时遇到的坑及已验证的修复方法。

## 路由表

| 出问题的工具 | 看这里 |
|-------------|--------|
| llama.cpp 启动器 / .bat 脚本 / 多模型菜单 | [llama-cpp-launcher.md](llama-cpp-launcher.md) |
| SearXNG | [Pinokio/searxng.md](Pinokio/searxng.md) |
| Open WebUI | [Pinokio/open-webui.md](Pinokio/open-webui.md) |
| llama.cpp 推理参数 | [Pinokio/llama-cpp.md](Pinokio/llama-cpp.md) |

## 触发词映射

| 关键词 | 加载文件 |
|--------|---------|
| 启动脚本 / 启动器 / .bat / launcher / 多模型切换 / 菜单脚本 / 模板 / 乱码 / 运行不了 / 闪退 / CRLF / ASCII / DLL / cudart / companion | llama-cpp-launcher.md |
| SearXNG / 搜索引擎 / 搜索 | Pinokio/searxng.md |
| Open WebUI / WebUI / 前端 / 网页界面 | Pinokio/open-webui.md |
| llama.cpp / 推理 / 采样 / 参数 / GPU / context | Pinokio/llama-cpp.md |

## 目录结构

```
AI-install-and-fix/
├── SKILL.md                  # 本文件 — 索引
├── llama-cpp-launcher.md     # 启动脚本模板 + 编码坑 + 参数速查
└── Pinokio/
    ├── searxng.md            # SearXNG（隐私搜索引擎）
    ├── open-webui.md         # Open WebUI（AI 对话前端）
    └── llama-cpp.md          # llama.cpp（本地推理后端）
```
