# RELEASE 模板（语言自适应）

> 每次发布时复制对应语言模板，替换 `{...}` 占位符。

---

## 通用流程

### 0. 发布前检查（★ 新增门禁，2026-07-26）

```bash
# 1. 查看现有 Release 格式
gh release list
gh release view <latest-tag> --json name,body

# 2. 提取模板：版本号风格？标题结构？正文模板？
# 3. 新 Release 严格套用现有格式
```

- [ ] `gh release list` 已查看现有版本号风格（semver / calver / 其他）
- [ ] 新 tag 命名与现有风格一致
- [ ] 新 title 与现有标题结构一致（`vX.Y.Z — <描述>`，**不含项目名前缀**——仓库名已标识）
- [ ] 正文模板与最新旧版对齐
- [ ] 正文**开门见山**：版本号只在 title 字段；正文直接以 `## 小节` 开头；不含版本号标题、不含项目名开场白（教训：html-guide 三个版本区间格式不一，2026-08-08 已统一标题 + 正文）
- [ ] **发布文件已扫描本机个性化信息**（OS 用户名 / 含用户名的绝对路径 / 本机代理端口 / token）→ 零残留；只允许 `~` / `%USERPROFILE%` / `Path.home()` 等通用形式（教训：html-guide / kakuyomu / balance-hud / improve 曾带 `C:\Users\<用户名>\` 泄漏，2026-08-08 清理）

### 1. 创建 Release

1. `gh release list` 确认现有格式 →
2. 填写 Tag `v{版本号}` (新建) / Target: `main` / Title: 与现有格式一致
3. 粘贴 Release Notes（用下方对应语言模板）
4. 上传构建产物（如有）
5. `gh release view <new>` 对比确认格式一致
6. 点击 **Publish release**

---

## Release Notes 模板

````
### v{版本号}

**{分类}**：{一句话描述}

**{分类}**：{一句话描述}

---
{安装章节 — 按语言选择}

Checksums:
- {文件名}: {大小}
````

**分类词**：`新增` `修复` `删除` `优化` `版本`。每条一行，分类加粗，冒号中文全角。

---

## 安装章节（按语言）

### Python

````
### 安装

```bash
pip install {包名}=={版本号}
# 或从 GitHub Release 下载 .whl
pip install {包名}-{版本号}-py3-none-any.whl
```
````

### JavaScript / TypeScript

````
### 安装

```bash
npm install {包名}@{版本号}
# 或: yarn add {包名}@{版本号}
```
````

### Rust

````
### 安装

```bash
cargo install {包名} --version {版本号}
```
````

### Go

````
### 安装

```bash
go install {模块路径}@{版本号}
```
````

### Claude Code Plugin

````
### 安装

#### Windows
1. 下载 `{项目名} v{版本号}.zip` 和 `install-{项目名}.bat`，放同一目录
2. 双击 `install-{项目名}.bat`

#### macOS / Linux
```bash
unzip "{项目名} v{版本号}.zip" -d ~/.claude/plugins/
```
````

## 发布后检查

- [ ] GitHub Release 页面显示正确版本号
- [ ] 安装命令一键可用（复制粘贴到终端即可运行）
- [ ] Checksums 与实际文件匹配
- [ ] Repo topics 已更新（`gh repo edit --add-topic`）
