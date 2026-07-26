# RELEASE 模板（语言自适应）

> 每次发布时复制对应语言模板，替换 `{...}` 占位符。

---

## 通用流程

1. 进入 GitHub 仓库 → **Releases** → **Create a new release**
2. 填写 Tag `v{版本号}` (新建) / Target: `main` / Title: `{项目名} v{版本号}`
3. 粘贴 Release Notes（用下方对应语言模板）
4. 上传构建产物（如有）
5. 点击 **Publish release**

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
