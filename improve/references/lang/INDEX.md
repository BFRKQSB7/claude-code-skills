# Language Index — 语言特定教训目录

> 按需浏览。路由自动检测扩展名，不需要手动读这个 index。
> 不确定语言覆盖范围时读这里。

## 文件清单

| 语言 | 文件 | 教训数 | 重点领域 |
|------|------|--------|----------|
| Python | [lessons-python.md](lessons-python.md) | 20 | async create_task / 裸except / 可变默认参数 / 迭代改列表 / with资源 / pickle RCE / eval注入 / 明文协议 / PyInstaller sys.frozen / tooltip Toplevel不消失 / CTkLabel不随grid拉伸用tk.Label / PyInstaller onefile 二进制grep不到源码串 |
| JavaScript/TS | [lessons-javascript.md](lessons-javascript.md) | 27 | Promise不await / forEach+async / var闭包 / any传染 / fetch缺超时 / innerHTML XSS / prototype pollution / SSR hydration / ANSI字符串长度 / DOM运行时JS静默失效(textContent/中文id/sticky兜底) / \uXXXX字面量Edit匹配 / 展示值取展示层(收藏中文) / File System Access API无path/getParent / Write写入\x00→NUL变binary / number input step从min起步invalid / OpenAI兼容baseUrl /v1后缀重复拼接404 / localStorage控件类型迁移 / 局部重绘保留表单草稿 |
| Go | [lessons-go.md](lessons-go.md) | 11 | goroutine泄漏 / channel未关闭 / defer在循环 / nil interface / time.After泄漏 / context断链 / WaitGroup竞态 / range取地址 |
| Rust | [lessons-rust.md](lessons-rust.md) | 4 | unwrap生产panic / 生命周期传染 / clone滥用 / tokio drop handle |
| Bash | [lessons-bash.md](lessons-bash.md) | 17 | pipefail未开 / glob无匹配 / 变量不引号 / subshell变量丢失 / set -u / UTF-8 BOM → cmd崩溃 / LF换行 / 引号分词 / Windows zip反斜杠 / curl -m截断大下载 / curl中文乱码 / ls||输出源不明 |

## 语言检测优先级

1. 扫描项目文件扩展名（`detect-lang.sh`）
2. 用户明确提及的语言
3. 任务上下文推断（如 "写个 React 组件" → JS/TS）

## 交叉加载

Language × Pattern 取交集：同 Pattern 在不同语言有不同陷阱。
例: `async` + `.go` → 加载 `lessons-go.md` #async 分组 + `lessons-pattern-async.md` 通用原则
