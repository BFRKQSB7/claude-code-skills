# Python Lessons

> 加载条件: .py, python, pip, pyproject.toml, django, flask, fastapi, pytest, 用户说"Python"

---

## #async — 异步陷阱

### ★★ asyncio.create_task 忘 await → 静默丢失 (置信度: high, 命中: 2)

**Rule**: `asyncio.create_task()` 返回的 Task 必须被 await / gather / 存引用，否则 GC 回收静默取消
**Wrong**: `asyncio.create_task(worker())` 不存引用 — 事件循环下一轮 GC 回收 task，worker 永远不执行
**Right**: `task = asyncio.create_task(worker())` → `await task` 或 `tasks.append(task)` → `await asyncio.gather(*tasks)`
**Why**: CPython 引用计数 — Task 对象无引用 → 立即析构 → `__del__` 取消协程。无任何异常/警告。
**泛化**: 任何"fire and forget"异步操作都需要保持引用。JS 的 Promise 无此问题（GC 不取消已提交的 Promise）。

### ★ 混用 sync/async → 事件循环死锁 (置信度: high, 命中: 1)

**Rule**: async 函数内禁止调用 `asyncio.run()` 或同步阻塞方法；sync 函数内禁止调用 `loop.run_until_complete()`
**Wrong**: `def sync_fn(): asyncio.run(async_fn())` 被另一个 `asyncio.run()` 调用 → `RuntimeError: Event loop is already running`
**Right**: async 环境全程 async（入口 `asyncio.run(main())` 只调一次）；sync 环境用 `asyncio.run()` 做桥接
**Why**: Python asyncio 不允许嵌套事件循环（不同于 JS 的 microtask queue）。

### ★ 生成器 + async → 混淆 (置信度: medium, 命中: 1)

**Rule**: `async for` 配 `async def generator`；普通 `for` 配 `def generator`。不混用。
**Wrong**: `async def gen(): yield 1` → `for x in gen():` → `TypeError: 'async_generator' object is not iterable`
**Right**: `async for x in gen():` 或 把 generator 改成 `def gen(): yield 1`

---

## #error — 错误处理陷阱

### ★★ 裸 except: → 吞掉 KeyboardInterrupt + SystemExit (置信度: high, 命中: 2)

**Rule**: 永远不用 `except:` 裸捕获。最低限度 `except Exception:`。
**Wrong**: `try: ... except: pass` 吞掉 Ctrl+C — 程序杀不死
**Right**: `try: ... except Exception as e: logger.error(...)` 让 `BaseException` 子类（KeyboardInterrupt/SystemExit）正常传播
**Why**: Python 异常继承树: `BaseException` → `Exception` → 具体异常。`except:` 捕获包括系统信号的全部异常。

### ★ raise ... from ... 不链 → 根因丢失 (置信度: medium, 命中: 1)

**Rule**: 重抛异常必须用 `raise NewError(...) from original` 保留因果链
**Wrong**: `try: ... except ValueError as e: raise MyError(f"bad: {e}")` — 丢失 traceback 链
**Right**: `raise MyError("context") from e` — `__cause__` 链接两个 traceback
**Why**: 调试时需要看到原始异常在哪行抛出。`from` 保留完整异常链。

### ★ assert 语句用于业务逻辑 → 可被 PYTHONOPTIMIZE 禁用 (置信度: medium, 命中: 1)

**Rule**: `assert` 只用于调试/测试。业务校验用 `if ... raise ValueError(...)`
**Why**: `python -O` (O=PYTHONOPTIMIZE) 移除所有 assert 语句。生产环境可能启用。

---

## #loop — 循环陷阱

### ★★ 迭代中修改列表 → 跳过/死循环/IndexError (置信度: high, 命中: 2)

**Rule**: 不在 `for item in list:` 循环体内修改同一列表
**Wrong**: `for i, x in enumerate(lst): if bad(x): lst.pop(i)` → 索引偏移，漏检元素
**Right**: 迭代副本 `for x in list(lst):` 或列表推导 `lst = [x for x in lst if not bad(x)]` 或用 `filter()`
**Why**: Python for 循环依赖内部索引器。删除元素 → 后续元素前移 → 索引跳过相邻元素。

### ★ 默认参数可变 → 跨调用共享 (置信度: high, 命中: 1)

**Rule**: 默认参数值不用可变对象（`[]` `{}` `set()`）。用 `None` + 内部初始化。
**Wrong**: `def f(items=[]): items.append(1); return items` → 每次调用的 `items` 指向同一个 list
**Right**: `def f(items=None): items = items or []; items.append(1); return items`
**Why**: Python 只在函数定义时计算一次默认值。list/dict 是引用 — 所有调用共享同一对象。

---

## #io — 文件/网络陷阱

### ★ 文件未用 context manager → 句柄泄漏 (置信度: high, 命中: 1)

**Rule**: 文件操作始终用 `with open(...) as f:`。网络/DB 连接同理。
**Wrong**: `f = open('data.txt'); data = f.read()` — 异常时 f 不关闭，长期运行句柄耗尽
**Right**: `with open('data.txt') as f: data = f.read()`
**Why**: CPython 引用计数在大多数情况会立即 GC 关闭文件，但 PyPy/Jython 和异常路径不可靠。

### ★ subprocess 缺 timeout → 永久挂起 (置信度: medium, 命中: 1)

**Rule**: 任何 `subprocess.run()` 设 `timeout=` 参数
**Wrong**: `subprocess.run(['ffmpeg', ...])` — 进程卡死时程序永久阻塞
**Right**: `subprocess.run(['ffmpeg', ...], timeout=300)` — 超时抛 `TimeoutExpired`

---

## #security — 安全陷阱

### ★★★ pickle.loads() 不可信数据 → RCE (置信度: high, 命中: 3)

**Rule**: 不对不受信任数据使用 `pickle.loads()`。用 `json.loads()` 或 `yaml.safe_load()`。
**Wrong**: `pickle.loads(user_cookie)` — 攻击者可执行任意 Python 代码
**Right**: `json.loads(data)` 或 protocol buffers / msgpack 等安全序列化格式
**Why**: pickle 可以序列化任意 Python 对象包括函数/类。反序列化恶意 pickle = 远程代码执行（RCE）。

### ★★ eval() / exec() 不可信输入 → 代码注入 (置信度: high, 命中: 2)

**Rule**: 永远不对用户输入使用 `eval()` `exec()` `compile()`。用 `ast.literal_eval()`（仅字面量）或 JSON。
**Wrong**: `eval(user_expression)` / `exec(f"x = {user_input}")`
**Right**: `ast.literal_eval(safe_str)` 仅解析字面量 / `json.loads()` / 写专用 DSL parser
**Why**: eval/exec 在调用者的命名空间中执行任意代码。没有安全的 eval。

### ★★ 明文协议 (HTTP/FTP/Telnet) → 数据泄露 (置信度: high, 命中: 2)

**Rule**: 生产环境只用 HTTPS/TLS。不通过 HTTP/FTP 明文传敏感数据。
**Wrong**: `requests.get('http://api.internal.com/v1/users')` 明文传输
**Right**: HTTPS + 证书校验 + `requests.get('https://...', verify=True)`
**Why**: Sonar 数据: 明文协议是 Python 最常被检测到的安全缺陷。HTTP/FTP 无加密 = 网络嗅探即可获取数据。

### ★ subprocess shell=True → 命令注入 (置信度: medium, 命中: 1)

**Rule**: `subprocess` 默认不用 `shell=True`。必须用时用 `shlex.quote()` 转义所有参数。
**Wrong**: `subprocess.run(f'grep {user_input} /var/log/app.log', shell=True)` — 注入
**Right**: `subprocess.run(['grep', user_input, '/var/log/app.log'])` — 列表形式天然防注入
**Why**: `shell=True` 把字符串传给 /bin/sh 解析，shell 元字符（`;` `|` `$()`）= 命令注入。

---

## #type — 类型陷阱

### ★ Optional 语义误解 → None 检查遗漏 (置信度: medium, 命中: 1)

**Rule**: `Optional[X]` = `X | None`。mypy strict 模式下访问 Optional 必须先缩窄。
**Wrong**: `def get(key: str) -> Optional[str]: ...` → `result = get("k"); print(result.upper())` — mypy 报错
**Right**: `if result is not None: print(result.upper())` 或 `assert result is not None`

### ★ Any 传染 → 类型检查失效 (置信度: medium, 命中: 1)

**Rule**: 函数返回值漏标 → `Any` → 调用方也变 `Any` → 整条链失去类型检查
**Right**: `mypy --disallow-untyped-defs` 强制标注所有函数。返回类型至少标 `-> None`。

---

## #package — 打包陷阱

### ★★ [2026-08-12] PyInstaller onefile: `__file__` 指向 _MEIPASS 临时目录 (置信度: high, 命中: 1)

**Rule**: PyInstaller 打包后 `__file__` = 运行时解压临时目录 `_MEIPASS`，不是 exe 所在目录。资源定位必须用 `os.path.dirname(sys.executable)`（frozen 时）。
**Wrong**: `BASE = os.path.dirname(os.path.abspath(__file__))` → onefile 运行时 BASE 指向 `%TEMP%\_MEIxxx`，找不到旁边的 llama-server.exe / models/
**Right**: `if getattr(sys, 'frozen', False): BASE = os.path.dirname(sys.executable) else: BASE = os.path.dirname(os.path.abspath(__file__))`
**Why**: PyInstaller onefile 启动时把程序解压到临时目录运行，`__file__` 指向那里；exe 自身路径才是 `sys.executable`。必须带 `import sys`。

### ★ [2026-08-17] PyInstaller onefile 二进制 grep 找不到源码字符串 → 误判改动未进包 (置信度: high, 命中: 1)

**Rule**: 打包后**不要用 binary grep 验证改动是否进 exe**。源码被编译+压缩进 PYZ archive，中文/emoji 等 UTF-8 源码串在二进制里无原文；能 grep 到 ASCII 依赖名（`customtkinter`）是 import 元数据仍明文，会造成「依赖能找、源码找不到」的错觉。验证链条 = 确认构建发生在改动之后 + `md5sum dist/` 与部署目录文件比对（同源即等价）+ 运行时冒烟测试断言真实行为（stub 掉 modal dialog 后测逻辑）。
**Wrong**: `grep -c "新提示文案" LLMGUI.exe` = 0 → 误判 fix 没打进包，浪费时间去翻构建缓存/重打包（连旧源码串也 grep 不到，ASCII 依赖却能找到 16 次）
**Right**: ① 重跑一次 `pyinstaller LLMGUI.spec`（构建必在改动后）② `md5sum dist/LLMGUI.exe` vs 部署目录 exe 比对一致 ③ 冒烟测试 stub `messagebox.showwarning` 断言 fired once、无 showerror
**Why**: PyInstaller 把 .py 编译+ZlibArchive 压缩进 PYZ，二进制里是压缩流非明文；UTF-8 中文串压缩后无原文可 grep。

---

## #gui — GUI 陷阱

### ★★ [2026-08-12] 悬浮提示挂独立 Toplevel → 移走后不消失 (置信度: high, 命中: 1)

**Rule**: tkinter/customtkinter 用独立 `Toplevel` 做 tooltip 时，鼠标移进 tooltip 窗口后原控件收不到 `<Leave>` → tooltip 残留。必须**在 tooltip 窗口本身也绑 `<Leave>`+`<Motion>`**（指针移出即 destroy），控件侧再绑 `<Motion>` 兜底。
**Wrong**: 只在控件绑 `<Enter>`/`<Leave>`；tooltip 是独立窗口，鼠标悬上去时事件发给 tooltip 而非原控件，`<Leave>` 不触发，移走也不消失
**Right**: tooltip 窗口 `bind('<Leave>', hide)` + `bind('<Motion>', 指针移出边界→hide)`；控件也 `bind('<Motion>', 移出控件边界→hide)` 双保险
**Why**: 独立 Toplevel 是另一窗口，鼠标在其上时 `<Motion>`/`<Leave>` 事件路由到 tooltip，原控件收不到。

### ★ [2026-08-15] CTkLabel 不随 grid sticky 拉伸 + 带内边距 → 精确宽度提示文本用 tk.Label (置信度: high, 命中: 1)

**Rule**: customtkinter 的 CTkLabel 不随 grid `sticky='ew'` / pack `fill='x' expand=True` 拉伸（内部 canvas 卡在文本自然宽），且自带 ~31px 内边距；CTk 控件尺寸是**逻辑值 × DPI 缩放**（逻辑 900 → 物理 1350）。需要"吃满剩余宽度/精确到文本宽"的次要提示文本（文件名、路径）改用普通 `tk.Label`（零内边距、正确随 sticky 拉伸、`winfo_width` 准确），背景对齐 CTk 深色主题色（`gray17`=`#2b2b2b`）。
**Wrong**: CTkLabel + grid `sticky='ew'` + weight 列放自动匹配到的文件名 → 控件宽卡文本宽，长文件名截断；`winfo_reqwidth`（含内边距）> `winfo_width` 仍未拉伸。排障时按 900 逻辑宽估算放不下，实际要按 1.5x 物理宽（`winfo_width`）判断。
**Right**: `tk.Label(frame, text='', fg=..., bg='#2b2b2b', anchor='w')` + grid `sticky='ew'`（列 weight=1）→ 零内边距、正确吃满剩余宽度、ToolTip 悬浮命中区域准确
**Why**: CTkLabel 内部是 CTkFrame+canvas，canvas 尺寸固定为文本，grid/pack 拉伸对自定义 widget 不生效；内边距来自 CTk 主题（非可配置）。DPI 缩放让逻辑/物理尺寸分离，宽度预算判断必须用物理值。
