# README 模板（语言自适应）

> 每次发布时检查 README 是否包含以下必需节。`[可选]` 标记的节按需保留。
> 安装章节按项目语言选择。

---

# {项目名} v{版本号}

> {一句话描述 — 做什么、给谁用}

![](https://img.shields.io/badge/version-{版本号}-blue)
![](https://img.shields.io/badge/license-{许可证}-green)

## 多语言版本

> 参考 GPT-SoVITS 模式。目录结构：根目录放默认语言，翻译放 `docs/<lang-code>/README.md`

**English** | [**中文简体**](./docs/cn/README.md) | [**日本語**](./docs/ja/README.md)

> 规则：当前语言 **加粗无链接**，其他语言 **[加粗链接](path)**。用该语言的自称（한국어 不写 Korean）。相对路径。

## 功能

- **{功能名}** — {一句话说明}
- （3-6 条为宜）

## 快速安装

### {语言 — Python / Node.js / Rust / Go / Claude Code Plugin}

{选择对应安装模板 — 见下方}

## {核心功能说明}  [可选]

（展示主要输出或界面截图/示例）

| 元素 | 说明 |
|------|------|
| `{示例}` | {解释} |

## 配置  [可选]

```bash
# 常用配置示例
```

## 环境变量  [可选]

| 变量 | 平台 | 说明 |
|------|------|------|
| `{VAR_NAME}` | {平台} | {说明} |

## 文件结构

```
{项目名}/
├── {包管理文件}            # pyproject.toml / package.json / Cargo.toml / go.mod
├── src/
│   └── {主模块}
├── tests/
├── README.md
└── LICENSE
```

（不包含运行时文件：缓存、日志、虚拟环境、node_modules）

## 变更日志

### v{版本号}
- **{分类}**：{内容}
- （分类词同 RELEASE 模板：新增/修复/删除/优化/版本）

### v{旧版本号}
- ...

## 许可证

{许可证名}

---

## 安装模板（按语言）

### Python

```bash
pip install {包名}
# 或: pip install {包名}=={版本号}
# 开发安装: pip install -e .
```

### JavaScript / TypeScript

```bash
npm install {包名}
# 或: yarn add {包名}
```

### Rust

```bash
cargo install {包名}
```

### Go

```bash
go install {模块路径}@{版本号}
```

### Claude Code Plugin

#### Windows
1. 下载 `{项目名} v{版本号}.zip` 和 `install-{项目名}.bat`，放同一目录
2. 双击 `install-{项目名}.bat`，按提示输入配置

#### macOS / Linux
```bash
unzip "{项目名} v{版本号}.zip" -d ~/.claude/plugins/
```
