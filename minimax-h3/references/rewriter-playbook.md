# H3 改写器实战手册

SKILL.md 是路由和决策层，这里是落地细节。官方规范以 `official-base-en.md` / `official-ref-en.md` 为准，本文件不覆盖它们，只补「怎么替用户做决策」。

---

## 1. 从"烂需求"到"专业提示词"的五步

用户输入长这样：**"帮我做个赛博朋克追车，要炸裂"**

**❌ 注水式改写**（市面上 enhancer 的通病）：

> 8K 超高清，Octane 渲染，工业光魔级 VFX，电影级质感，史诗氛围，赛博朋克霓虹，
> 极致细节，大师构图，丁达尔效应，杜比视界 HDR……

加了 60 个词，**零个新信息**。模型不知道多长、几个镜头、谁在追谁、有没有声音、前 2 秒放什么。

**✅ 决策式改写**：

| 步骤 | 动作 | 本例 |
|:---|:---|:---|
| 1 | 判平台 | **问**：API 还是本地 ComfyUI？ |
| 2 | 判模式 | 无素材 → T2VA |
| 3 | 补决策 | 时长 8s（默认）；2 个镜头；风格 `Live-action, cinematic`；前 2 秒 = 车已经在飞，不要从静止起步；无台词 → 不用问台词 |
| 4 | 查拒绝 | "炸裂"不是概念。追车本身没钩子 → **提一个具体钩子**：追车中途撞碎全息广告牌，碎片在雨里悬停半秒 |
| 5 | 出稿 + 说明 | 提示词 + 「我替你做了哪些决策」 |

**关键**：第 4 步是分水岭。能拒绝的是改写器，不能拒绝的是扩写器。

### 第 5 步的产物长什么样

同一份决策，两个平台**输出形态完全不同**。

#### ✅ API 端成品（Context-IR 在跑 → 中文自然语言，不手工结构化）

> 这是**多数用户走的路径**。目标是把决策说清楚，让 Context-IR 有足够信息去结构化，而不是替它结构化。

```
8 秒，实拍电影感，赛博朋克暴雨夜城。

开场就在高速状态——一辆黑色改装车已经在积水路面上高速甩尾，不要从静止起步。
镜头低机位贴地跟车，小幅度快速推进，雨水和溅起的水幕不断扫过镜头前。
大约第 4 秒，车头撞穿一块悬空的全息广告牌，广告牌碎成大片蓝紫色光斑，
这些光斑在雨里短暂悬停约半秒才被气流冲散——这半秒是全片的记忆点，给足画面。
最后车冲出画面右侧，镜头留在原地，光斑余烬缓缓落下收尾。

声音：全程暴雨砸在车顶和路面的密集雨声、引擎高转轰鸣、轮胎在积水里打滑的摩擦声；
撞碎广告牌时一声清脆的电子碎裂音，随后是短暂的电流杂音。
不要配乐，只保留现场声。
```

**注意这条里有什么、没有什么：**

| 有 | 没有 |
|:---|:---|
| 时长、风格、前 2 秒状态 | `[Shot 1]` / `integrated_multimodal_description` 等字段名 |
| 一个具体的视觉钩子（碎片悬停半秒） | `Push In with small amplitude at slow speed` 这类官方运镜词 |
| 声音分层（环境 / 事件 / 明确不要配乐） | `8K / Octane / 工业光魔 / 电影级质感` 等注水词 |
| 关键时间点（第 4 秒） | 精确到毫秒的时间戳 |

> **手工结构化会和 Context-IR 打架**：你写半套 `[Shot N]`，Context-IR 再改写一遍，
> 容易出现镜头数翻倍或时间戳错位。API 端把决策讲清楚就够了。

#### ✅ 本地权重端成品

同一个需求在本地端要写成完整的三字段结构化格式（T2VA 无参考素材），
骨架见 SKILL.md「输出格式骨架」，完整范例见下面第 4 节（Ref2VA 版本，含参考素材的写法）。

---

## 2. 决策默认值全表

用户没说就按这个走，**不要为这些问问题**，出稿后一句话声明即可。

### 时长与镜头数

**官方硬参数**（[HF 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)）：`Output duration 4–15 seconds`、`Output frame rate 24 FPS`。
15s 是**模型规格上限**，不是显存限制——本地端跑不到 15s 是显存问题，见第 6 节。

| 时长 | 镜头数 | 适合 | 台词容量 🔬 |
|:---|:---|:---|:---|
| 4–6s | 1 | 单个动作 / 产品特写 / 一个瞬间 | ≤10 字 |
| **8s（默认）** | 1–2 | 一次完整表演 / 一问一答 | ≤25 字 |
| 10–12s | 2–3 | 小情节转折 | ≤40 字 |
| 15s（上限） | 2–4 | 完整起承转合 | ≤55 字 |

> 🔬 **台词容量是经验值，不是实测值。** 推导口径：中文约 4–5 字/秒、英文约 2.5 词/秒，
> 再按"片长越短，越需要留时间做视觉建立"打折——4–6s 只留约 4 成给台词，15s 可以给到约 8 成。
> 这个折扣曲线是拍的，**跑到边界情况时以实际截断为准并回写这张表**。
> 超了必须加时长或砍台词，硬塞会被 `<cutoff>` 截断。

> ⚠️ **8s 默认值分平台**：
> - **API 端**：`duration` 是请求参数，`8` 是官方示例用过的合法值（模型卡 i2va 示例即 `"duration": 8`），直接用
> - **本地权重端**：帧数受 `17k+5` 约束，**8.0s 不是合法档**。最近的合法档是 209 帧 ≈ **8.7s**。
>   本地端出稿时用 8.7s，不要写 8s（见第 6 节）

### 风格锚定（`[Shot 1]` 开头，Ref2VA 放 `[Shot 1]` 之前）

官方常用值：`Cinematic` / `live-action` / `2D-animated` / `3D CG` / `claymation` / `watercolor` / `vintage film`

- 有参考图 → **从图反推**，写进风格句并绑定来源：`matching the illustration style of <Picture 1>`
- 无参考图 → 默认 `Live-action, cinematic`
- **参考图是插画/立绘却不写 `2D-animated`，模型必往写实漂，角色立刻"不像"**

### 三层声音的默认策略

| 字段 | 默认动作 |
|:---|:---|
| 主描述字段内 | 事件音效随镜头写（开门声、玻璃碎、脚步落地）——**和画面同步的都在这里** |
| `overall_soundscape` | 按场景推 1–4 句：环境底噪 + 动作音 + 非语言人声。**永远不要留空**（除非用户明确要全片静音才写 `N/A`） |
| `non_diegetic_music` | **默认 `N/A`**。只有用户提了情绪诉求 / 是 MV、广告、预告片时才给。给的时候只写乐器 + 速度 + 力度变化，**禁止写"紧张""温暖"这类情绪词** |

### 前 2 秒（用户永远不会说）🔬

- 最强视觉信息前置，**禁止用"缓缓推进""镜头慢慢移动"开场**
- 静 → 动的突变比全程运动更抓人
- T2VA 里把主体和风格在第一句话内交代完

> 🔬 **来源与适用边界**：这三条是从 Seedance 实战经验迁移过来的，**在 H3 上未验证**。
> 而且"2 秒生死线"本质是**短视频信息流的分发规则**，不是模型规则——
> 片子如果不投信息流（比如做素材、做游戏过场、做产品页 loop），这条可以不遵守。
> 跑过 H3 之后回来把它坐实或删掉。

---

## 3. 五模式写法配方

### T2VA

结构：`[Shot 1] 风格 + 景别 + 主体 + 环境` → 运镜句 → 动作/台词 → `[Shot 2] At MM:SS.mmm, ...`

允许补用户没说的场景、动作、声音细节，只要不违背原意。

### I2VA

第一行对齐指令逐字照抄：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

`<Picture 1>` 是 0.00 秒的真实首帧。写法：**首帧锚定 → 动作起始 → 连续发展 → 结果/反应**。
角色身份、服装、配色、关键道具、空间关系全程保持一致。

### FL2VA

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

`S.SS` = 有效时长，**必须两位小数**。
**优先单镜头**（让模型连续插值），除非用户明确要多镜头。
正文不要把两张图各描述一遍，要写**连接它们的运动路径**：首帧状态 → 可观察的中间变化 → 差异逐步收窄 → 尾帧状态。

### L2VA

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

`<Picture 1>` 是最后一帧，**不属于 Shot 1**。要反推一个合理的前置状态，再让动作、物体状态、构图逐步落到这张图上。
写法：合理前置状态 → 明确动作与过渡路径 → 末镜头逐渐收敛 → 落帧。

### Ref2VA

六段顺序固定。逐段要点：

1. **`subject_definitions`** — 每个要单独追踪的参考内容一行。角色定义把可辨识特征**写全**（头部、眼睛、配色、服装细节、武器/道具），后面两段要复用这些词。音色参考固定句式：`<Audio 1> is the voice-timbre reference for <Subject 1> (S1).`——`(S1)` 在这里就绑定，后文不再另行分配
2. **`summary`** — 一段话，开头方括号任务类型，多个用 ` + ` 连接且不重复：
   `keyframe completion` / `reference generation` / `video editing` / `video continuation` / `audio reuse` / `audio reference`
   > 角色图 + 音色参考 = `[reference generation + audio reference]`
   > 有视频/音频**不自动**产生对应类型。参考视频只提供运镜/剪辑/节奏 → 仍属 `reference generation`
3. **`retention_analysis`** — 每标签一行，关系标记来自固定枚举。**新增的动作/背景/剧情不算保真损失**，不要因此降级成 `partially_preserved`
4. **`detailed_description`** — 风格开场句独立放 `[Shot 1]` 之前；生成类任务 350–500 英文词；`<Subject N>` 首次出场时把参考特征在画面语境里复述一遍
5. **`overall_soundscape`** — 只写环境音/动作音；复制了参考音频的环境层要在此声明
6. **`non_diegetic_music`** — 只写观众侧配乐；直接复用参考 BGM 在此声明

**`<Picture N>` 还是 `<Subject N>`？**

| 图的角色 | 用什么 |
|:---|:---|
| 首帧 / 关键帧 / 尾帧 / 分镜板 / 构图锚点 | 独立 `<Picture N>` 条目 |
| "角色/场景/画风长这样" | **不建独立条目**，在 `<Subject N>` 定义里引用它 |

> 角色参考几乎总是后者：`<Subject 1> is the knight from <Picture 1>, with ...`

---

## 4. 完整范例（Ref2VA，8 秒，角色图 + 音色参考）

需求原话：**"用这张乌鸦骑士立绘做个视频，雪夜城墙拔剑，说句狠话"**

补齐的决策：时长 8s（两镜头够用）｜风格 `2D-animated, dark-fantasy anime`（从立绘反推）｜台词**问到原文**"雪落之时，便是审判。"｜前 2 秒 = 已在拔剑不是站着｜`non_diegetic_music` 给（有情绪诉求）

```text
subject_definitions:
<Subject 1> is the crow knight from <Picture 1>, rendered in a 2D-animated dark-fantasy anime illustration style with crisp cel shading and a deep black-and-blue palette; he is an anthropomorphic raven warrior with a black-feathered avian head, a sharp dark beak, glowing cyan eyes, layered black-and-dark-blue feather armor edged with gold filigree, a glowing blue gem on his chest, a long dark-blue scarf, black gauntlets, clawed taloned feet, and an ornate dark sword wreathed in purple energy.
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).

summary:
[reference generation + audio reference] The target video shows <Subject 1> standing on a snow-covered castle rampart at night, slowly drawing his purple-energy sword and pointing it directly at the camera while delivering one Chinese line using the voice timbre of <Audio 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - the crow knight's black-feathered avian head, sharp dark beak, glowing cyan eyes, layered black-and-dark-blue feather armor with gold filigree, glowing blue chest gem, dark-blue scarf, black gauntlets, clawed talons, and purple-energy sword are all retained; only his pose, the snowy night rampart setting, and the lighting are newly staged.
<Audio 1>: reference - the target dialogue follows <Audio 1>'s voice timbre and delivery without copying the original signal.

detailed_description:
The target video is in a 2D-animated, dark-fantasy anime style with crisp cel shading, a deep black-and-blue palette, cold moonlit rim light, and drifting snow particles.
[Shot 1] A medium-wide shot frames <Subject 1>, the crow knight, standing in left profile on the snow-covered stone walkway of a castle rampart at night. Crenellated battlements line the right edge of the frame, a dark valley and steadily falling snow fill the background, and pale blue moonlight rims his silhouette. His black-feathered avian head with its sharp dark beak and glowing cyan eyes faces along the wall, his long dark-blue scarf and the layered feathers of his armor streaming in the night wind, the gold filigree edging and the glowing blue gem on his chest catching faint light. Snowflakes settle on his pauldrons as his black gauntleted right hand crosses his body and closes around the hilt of the sword at his hip. He begins to draw the weapon slowly and deliberately; inch by inch the dark blade clears its sheath, and purple energy ignites along its edge, wisps of violet light curling off the metal and casting a purple glow across his feathers and the snow at his taloned feet. The camera pushes in with small amplitude at slow speed toward him while loose black feathers lift from his cloak and drift with the snow.
[Shot 2] At 00:04.000, the camera cuts to a frontal medium close-up of <Subject 1> on the same rampart, snow falling between him and the lens. In one smooth continuous motion he completes the draw, sweeps the blade forward, and points its glowing purple tip directly at the camera; the tip hovers in the lower foreground with violet energy flickering along the edge, while his cyan eyes stare unblinking into the lens above the blade. The camera holds a static shot. <Subject 1> (S1), speaking in a low, calm, cold voice using the voice timbre referenced from <Audio 1>, says with slow, deliberate delivery as his beak articulates each word: <d>[Chinese] 雪落之时，便是审判。</d> After the line, he holds the pose completely still, the purple energy pulsing once along the blade, his scarf and feathers swaying in the wind as snow keeps falling through the final frame.

overall_soundscape: A cold night wind blows steadily across the ramparts, carrying the soft hiss of falling snow and the rustle of feathers and fabric. A long metallic scrape rings out as the blade is drawn, joined by a low hum and faint crackling from the purple energy, followed by the quiet creak of armor as the knight extends his arm.

non_diegetic_music: Sustained low strings at a slow tempo with sparse deep drum hits, holding a quiet level during the draw, marked by a single accented drum strike as the blade points at the camera, then decaying to a soft sustained tone under the spoken line.
```

**三个值得抄的手法：**

1. **画风锁定写进 `subject_definitions`，正文只用 `<Subject 1>`**。
   `<Subject 1> is the crow knight from <Picture 1>, rendered in a 2D-animated dark-fantasy anime illustration style...`
   —— 一句话同时绑定了来源和画风，且**正文全程不出现 `<Picture 1>`**。
   > ⚠️ **这是最容易写错的一处**：`<Picture 1>` 只用来定义角色/画风时，按官方 `official-ref-en.md` §2.2 **不得建独立条目**；
   > 既然没有独立条目，它在 `retention_analysis` 里也就没有对应行，**正文再引用它就是悬空标签**。
   > 官方完整示例的 `detailed_description` 从不引用这类 Picture，全程只用 `<Subject N>`——照着做。
   > 只有真正当帧锚点用的 Picture（首帧/关键帧/尾帧/分镜板）才既有独立条目、又有 retention 行、正文才能引用。
2. 台词镜头切到正面中近景并让镜头**静止**——口型和台词是画面焦点时别加运镜
3. 台词后写 `holds the pose` 填满收尾时长——**不写模型会自由发挥**

---

## 5. 翻车对照表

> 🔬 **本表来源**：官方规则反推 + 第三方仓库（[kuronzzhan-droid](https://github.com/kuronzzhan-droid/minimax-h3-prompt-skill)）的 ComfyUI 实测，
> **本地 case 库尚无一条独立验证**。前 4 行（台词/音色/画风/身份）在第三方实测中有明确对应，可信度较高；
> 其余为从官方规范反推的推论。命中或证伪任何一条，都往 `experiments/cases/` 落一份，回来把 🔬 摘掉。

| 症状 | 病根 | 修法 |
|:---|:---|:---|
| 台词乱语 / 听不清 | 没写台词原文，或没用 `<d>[语言]</d>` | 逐字写进 `<d>[Chinese] ...</d>` |
| 声音不像参考音色 | `<Audio N>` 没绑 `(S1)`，或台词处没引用 timbre | 定义处 `for <Subject 1> (S1)`，台词处 `using the voice timbre referenced from <Audio 1>` |
| 角色不像 / 画风漂移 | 没写风格锚定 | `[Shot 1]` 前/开头声明 `2D-animated` 等 |
| 角色身份被打散 | 同角色喂了多张裁剪特写 | **单张全身参考图 > 多张局部图**；要给第二张就给头部特写，不超过两张 |
| 参考完全没生效 | 标签编号 ≠ 实际连线顺序 | 按连线顺序重排 `<Picture N>` / `<Video N>` / `<Audio N>` |
| 音效堆在台词上 | 声景写进了主描述字段，或反之 | 环境音归 `overall_soundscape`，事件音效随镜头写，不重复 |
| 旁白角色嘴在动 | 漏了 lips-closed 声明 | `<d>` 块后紧跟 `while his lips remain completely closed` |
| 结尾突然乱动 | 最后一个动作后没写收尾状态 | 补 `holds the pose` / `the camera holds through the final frame` |
| 镜头切得莫名其妙 | 只是想推近却用了 cut | 距离/轻微角度变化改用运镜，`cut` 要带来**新信息**（主体/空间/状态/视点/时间） |
| 本地端直接跑不动 | 超 token 上限 | 见第 6 节，先降时长再降画幅 |

---

## 6. 本地权重端的时长 / 画幅约束

> ⚠️ **来源与局限**：下表来自第三方在 **RTX 5090 32GB** 上的实测（[kuronzzhan-droid/minimax-h3-prompt-skill](https://github.com/kuronzzhan-droid/minimax-h3-prompt-skill)），**不是官方数值**。换卡、换量化、换 attention 实现都会变。首次在新环境用之前自己压一遍，把真实结果写进 `experiments/cases/`。

估算式：`token ≈ 时间潜帧 × (宽/16) × (高/16)`，上限约 61k。帧数需满足 `17k + 5`（124 / 141 / … / 362）。

| 时长 | 该卡上最高可用画幅 |
|:---|:---|
| 5.2s（124 帧） | 864×480 或 640×640 |
| 8.7s（209 帧） | 640×352 |
| 15.1s（362 帧） | 512×288 |

**一致性配方（同来源实测）**：单张全身参考图 + 风格锁定 + 提示词里把角色特征写全写死。`ref_image_size` 的 `max` 档身份还原更强但每步都带全量参考 token，慢数倍且挤显存——短片可用，长片先降时长。

**给用户的建议顺序**：先降时长 → 再降画幅 → 最后才考虑降参考档位。用户要 720p 15 秒又要角色像，在 32GB 卡上是不可能三角，**直说**。

---

## 7. 素材分工话术

用户丢了一堆文件却不说用途时，别猜，用这套句式逐个点名后再确认：

```
我按这样分工，不对你说：
- 图1 → 角色外貌（写进 <Subject 1>，不作首帧）
- 图2 → 首帧构图（独立 <Picture 1> 条目，0.00 秒）
- 视频1 → 只借运镜和剪辑节奏，画面内容不复用（<Video 1>，weak_reference）
- 音频1 → 主角音色参考，不复制原信号（<Audio 1>，reference）
```

三条判断规则：

1. **人/物/场景/画风/动作**被复用为可见内容 → 一律 `<Subject N>`，哪怕它来自视频
2. `<Video N>` 只用于**整片级关系**：剪辑源、续写起点、整体时序结构
3. 参考视频**自带声音不自动**产生 `<Audio N>`；只有真的复用或参考了那条音轨才建
