# README 模板（语言自适应）

> 每次发布时检查 README 是否包含以下必需节。`[可选]` 标记的节按需保留。
> 安装章节按项目语言选择。

---

# {项目名} v{版本号}

> {一句话描述 — 做什么、给谁用}

![](https://img.shields.io/badge/version-{版本号}-blue)
![](https://img.shields.io/badge/license-{许可证}-green)

## 多语言版本

**默认（用户偏好 2026-08-10 更正）**：**文件切换版** —— 根目录 `README.md` 放默认语言（中文），翻译放 `docs/<lang-code>/README.md`，每个 README 顶部标题正下方放语言切换条。
**纯外语 README（无中文）不允许发布** —— 必须含中文版；存量纯外语 README 一律补中文。

```
README.md                    ← 中文（默认，GitHub 自动渲染）
docs/
  en/README.md               ← English 翻译
  (ja/ 等按需)
```

**语言切换条**（每个 README 顶部，标题正下方）：

```
**中文简体** | [**English**](./docs/en/README.md)
```

规则：当前语言 **加粗无链接**，其他语言 **[加粗链接](相对路径)**。用该语言的自称（`中文简体` 不写 Chinese，`English` 不写 英文）。

**发布门禁（★ 2026-08-10）**：
- [ ] 改 README 时**中英两版同步更新**（根 `README.md` + `docs/en/README.md`），不允许只改一版
- [ ] 新增语言 → 建 `docs/<lang>/README.md` 并更新所有已有 README 的切换条

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
