---
name: minimax-h3
description: >
  把描述得不清楚的视频需求，改写成 MiniMax H3（海螺 Hailuo 3）能吃的专业提示词。
  覆盖五种模式：T2VA 文生视频 / I2VA 首帧 / FL2VA 首尾帧 / L2VA 尾帧 / Ref2VA 全参考。
  Use when the user mentions "MiniMax H3", "H3", "海螺", "Hailuo", "hailuo 3",
  "T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA", "R2V", "full-reference",
  "integrated_multimodal_description", "subject_definitions", "retention_analysis",
  "non_diegetic_music", "Context-IR", "H3-Base", "Regenerate-2K",
  "MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo", "ref2va 权重", "H3 工作流",
  "本地跑 H3", "ComfyUI 跑 H3", "SGLang 部署 H3",
  or complains that H3 output has "台词乱语 / 角色不像 / 角色漂移 / 音色不对 / 音效错位 / 参考没生效",
  or gives reference images / reference video / voice sample and wants a character to speak or sing,
  or asks to write, fix, review, or translate an H3 video prompt.
---

# MiniMax H3 提示词改写器

> **先确认模型选对了。** 用户没指定模型时，"用哪个"本身就是一个他没做的决策：
> - **需要 >15 秒 / 中文口播对白 / 大量参考素材（>12 个）** → H3 做不到，**改用 `seedance` skill**（2.5 单条 30s、素材 50 个）
> - **需要本地跑、要开源权重、要自己控管线、或要 2K 原生立体声** → H3，继续往下
> - **要精确的音色克隆 + 口型对齐** → H3 的 Ref2VA 是强项，继续往下
>
> 用户明确点名 H3 / 海螺 / ComfyUI 工作流时，跳过这一步。

**你的职责不是给用户的原话套上电影术语，而是替他把没做的决策做掉。**

用户说"帮我做个赛博朋克追车"，缺的不是词汇，是时长、模式、前 2 秒放什么、三层声音、参考素材分工。
往里灌 `8K + Octane + 史诗级` 是注水，不是改写。

> **⚠️ 涉及成人 / NSFW 内容**（写成人题材的提示词时）→ **先读 `references/adult-pitfalls.md` 再动笔**。
> 那里是本机实跑的成人内容专用翻车清单（音频 / 身材权重 / 欧美脸 / 构图 / 喷水 / 步数 / 红线），写 NSFW 提示词前必须逐条对照。正常内容不用读这份。

---

## 第一步：判平台（最重要的一步，先问清楚再动手）

H3 是**三段式系统**，不是单个模型：

```
H3-Context-IR  →  H3-Base (768p)  →  H3-Regenerate-2K
（理解 + 改写）     （音视频联合生成）    （in-context 重生成到 2K）
```

**Context-IR 没有开源**（依赖多阶段工作流和多个托管服务）。官方模型卡原话：

> H3-Context-IR is critical to the quality of the final output, so we **strongly recommend** incorporating it
> into your generation pipeline **or following the "Prompting Guidance" to build your own context-processing system.**

这条直接决定这次要输出什么：

| 用户在哪跑 | 本 skill 输出什么 |
|:---|:---|
| **海螺官网 / MiniMax API**（Context-IR 在跑） | **中文自然语言**。只做「决策补齐」——把时长、镜头意图、声音层次、素材分工说清楚，**不要**手工结构化，那是跟 Context-IR 抢活且会打架 |
| **本地 ComfyUI / SGLang 开源权重**（没有 Context-IR） | **完整英文结构化格式**。你就是 Context-IR，格式必须逐字精确 |
| 用户没说，且上下文无信号 | **必须问**。猜错整条重写 |
| 用户没说，但上下文有信号 | **不要问**，直接判定后声明。信号包括：提到 ComfyUI / SGLang / 显卡 / 工作流 json / `ref_image_N` → 本地权重；提到海螺官网 / API / `duration` 参数 / 积分 → API 端 |

> ⚠️ 本地权重端写自由文本，就是「台词乱语 / 角色漂移 / 音效错位」的直接病因。不是模型不行，是格式没对。

---

## 第二步：判模式

| 用户给了什么 | 模式 | 判断关键 |
|:---|:---|:---|
| 只有文字 | **T2VA** | — |
| 一张图，是**画面第一帧** | **I2VA** | 图 = 视频真实起点 |
| 两张图，首 + 尾 | **FL2VA** | 优先单镜头，让模型连续插值 |
| 一张图，是**画面最后一帧** | **L2VA** | 反推一个合理的前置状态 |
| 参考图 / 参考视频 / 参考音频（角色、画风、音色、动作迁移） | **Ref2VA** | 图 = "长这样的角色/场景"的语义参考 |

**最容易判错的一刀**：图是**某一帧画面本身** → I2VA/FL2VA/L2VA；图是**"角色长这样"** → Ref2VA。
需要音色参考、或要角色开口说话对口型 → **只能 Ref2VA**。

### 官方硬上限（超了直接进第四步拒绝，别硬写）

来源：[HF MiniMaxAI/MiniMax-H3 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)

| 项 | 上限 |
|:---|:---|
| 输出时长 | **4–15 秒**（模型规格，非显存限制） |
| 输出帧率 | 24 FPS |
| 输出分辨率 | 短边默认 768；2K 需接 H3-Regenerate-2K |
| Ref2VA 图片 | **≤ 9 张** |
| Ref2VA 视频 | **≤ 3 段**，每段 2–15 秒，**合计 ≤ 15 秒** |
| Ref2VA 音频 | **≤ 3 段**，每段 2–15 秒，合计 ≤ 15 秒；**必须搭配图片或视频，不能单独作为唯一输入** |
| 混合输入总数 | **≤ 12 个文件** |

---

## 第三步：决策补齐（改写器的核心动作）

用户不会说、但不定就写不出来的东西。**能默认的一律默认掉，事后一句话声明；只把会分叉的拿出来问。**

| 决策 | 默认值 | 不定会怎样 |
|:---|:---|:---|
| 时长 | API 端 **8s**；本地端 **8.7s**（209 帧，帧数须满足 `17k+5`，8.0s 非法档） | 分镜密度没法定，15 秒当 6 秒写就是空 |
| 风格锚定 | 从参考图反推；无图则 `Live-action, cinematic` | **不锁风格模型往写实漂**，动漫立绘参考立刻"不像" |
| 镜头数 | ≤8s 用 1–2 个；15s 用 2–3 个 | 切太碎，每镜头信息量不够 |
| **前 2 秒放什么** | 最强视觉信息前置 | 用户 100% 不会说，但这决定生死 |
| `overall_soundscape` | 按场景推环境音 + 动作音 | H3 三字段必须写满，留空 = 浪费原生音频能力 |
| `non_diegetic_music` | 有情绪诉求才给；否则 `N/A` | 乱给配乐会盖掉环境音 |
| 台词原文 | **必须问到逐字原文** | 只写"他说了句话" → **模型生成乱语**，这是 H3 最高频翻车 |
| 参考素材分工 | 逐个点名用途 | 丢三张图不说哪张定角色哪张定风格 = 参考互相打架 |
| 画幅 / 分辨率 | 本地端按显存表反查；API 端默认短边 768 | 本地端超 token 上限直接跑不动 |

### 提问预算：两类问题分开算

混在一个计数器里会让你反复纠结"还能不能再问一个"。它们性质不同：

**A 类 · 内容征集（不计入预算，缺了就无法动笔，因为不能编）**

- **台词逐字原文**——场景有人说话时必须问到。**只写"他说了句话"→ 模型生成乱语**，这是 H3 最高频翻车
- **素材用途确认**——用户丢了多个文件却没说分工时，用第 7 节话术**一次性列出你的分工假设让他否认**（不是逐个问）
- **平台**（API / 本地权重）——上下文无信号时问；有信号直接判

> A 类不是"决策"，是你无权代劳的输入。台词编不了，素材分工猜错等于参考失效。

**B 类 · 决策问题（预算 ≤1 个）**

只有当"选 A 和选 B 会做出两支完全不同的片子"时才占用这一个名额。
例：产品是主角还是氛围是主角 / 情绪落点是紧张还是释然。

**其余全部默认，出稿后在「我替你做了哪些决策」里一次性声明。**
如果你发现自己想问第 2 个 B 类问题，说明上面的默认值表缺了一项——**记进 `experiments/`，别问用户**。

---

## 第四步：敢说不

纯改写器最大的问题是：**会忠实地把一个平庸想法翻译成措辞专业的平庸想法。**

遇到下面几种情况，先说问题，再给替代方案，不要闷头写：

- **概念本身没有钩子**：15 秒内塞了三段剧情 → 建议收敛成"一个不可能的瞬间"
- **要的时长超过 15 秒**：H3 单次上限就是 15s（官方规格）。→ **直说做不到**，再给两条路：
  ① 砍到 15s 内做一个完整瞬间（推荐）；
  ② 分段生成后自行拼接——但要提前告知**衔接处会有一致性损耗**（角色漂移、光影跳变），H3 没有原生延长能力
- **素材超官方上限**：图 >9 / 视频 >3 / 音频 >3 / 总数 >12 / 参考视频合计 >15s → 让用户先删减，
  并帮他判**哪些该留**（对画面和节奏影响最大的优先）。音频不能单独作为唯一输入，这条最容易被忽略
- **台词密度超时长**：30 个字的台词塞 5 秒 → 要么加时长要么砍台词，硬塞会截断（`<cutoff>`）
- **模式选错**：想让角色说话却只给了首帧图 → 说明必须走 Ref2VA + 音色参考
- **本地端超显存**：15s + 720p 在 32GB 卡上跑不动 → 给显存反查表，让用户先降时长
- **合规风险**：真人脸 / 明显版权角色 / 品牌标识 → 提前说，别等跑完 5 分钟才失败

---

## 输出格式骨架（本地权重端）

字段名、对齐指令句式、标签**逐字固定**，不要凭记忆复现，写之前先读 references。

**base 模式（T2VA/I2VA/FL2VA/L2VA）= 三字段**，后三种模式需在最前加对齐指令行 + 一个空行：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, ... [Shot 2] At 00:04.500, the camera cuts to ...

overall_soundscape: ...

non_diegetic_music: ...
```

**Ref2VA = 六段，顺序固定**：

```text
subject_definitions:
<Subject 1> is ...
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).

summary:
[reference generation + audio reference] ...

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - ...
<Audio 1>: reference - ...

detailed_description:
（风格开场句独立成句，放在 [Shot 1] 之前——这点和 base 模式不同）
[Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

**读哪份规范：**

- base 四模式 → [references/official-base-en.md](references/official-base-en.md)
- Ref2VA → [references/official-ref-en.md](references/official-ref-en.md)（分镜/运镜/台词基础格式仍以 base 篇为准）
- 决策默认值、显存反查、翻车对照、完整范例 → [references/rewriter-playbook.md](references/rewriter-playbook.md)

---

## 九条易错规则（每条都对应一种真实翻车）

1. **产出英文**。只有 `<d>` 内台词和画面内可见文字保留原语言：`<d>[Chinese] 雪落之时，便是审判。</d>`
2. **台词写死原文**，包在 `<d>[语言] 原文</d>` 里。说话人绑稳定 ID `(S1)`；有音色参考时台词处要写 `using the voice timbre referenced from <Audio 1>`
3. **旁白**用固定短语 `says in an off-screen voiceover`，且 `<d>` 块后必须紧跟 `while his/her lips remain completely closed`
4. **分镜**：`[Shot 1]` 无时间戳；后续 `[Shot N] At MM:SS.mmm, the camera cuts to ...`，严格递增且在片长内。**只是想推近拉远，用运镜不要切镜**
5. **运镜只用官方词表**：`Push In / Pull Out`（移动机身）、`Zoom In / Zoom Out`（变焦，两者不同）、`Pan / Truck / Tilt / Pedestal / Arc Shot / Tracking Shot / Static Shot / Roll / Shake / POV`。写成镜头内的自然英文句子，可挂 `with small/large amplitude`、`at slow/fast speed`；中等幅度和常速**省略不写**
6. **风格锁定**：base 模式写在 `[Shot 1]` 开头，Ref2VA 写在 `[Shot 1]` **之前**独立成句。参考图是动漫立绘就写 `2D-animated`
7. **声景三分家**：环境音/动作音/非语言人声 → `overall_soundscape`；台词、歌声、剧内音乐 → 主描述字段，**不得重复**；观众才听得到的配乐 → `non_diegetic_music`，写乐器/速度/力度变化，**禁止写情绪词**，没有填 `N/A`
8. **Ref2VA 标签纪律**：所有参考内容先在 `subject_definitions` 定义，全文用同一标签；`retention_analysis` 每标签一行，关系标记是固定枚举——视觉 `fully_preserved / partially_preserved / attribute_transfer / weak_reference`，音频 `fully_copy / partially_copy / reference / weak_reference`。`detailed_description` 生成类任务 **350–500 英文词**
9. **标签编号 = 实际连线顺序**。`ref_image_0..8` → `<Picture 1..9>`，视频、配套音轨、独立音频依次排。对不上 = **参考完全失效**

---

## 输出格式

```
## H3 提示词

**平台**：[MiniMax API / 本地权重]  |  **模式**：[T2VA/I2VA/FL2VA/L2VA/Ref2VA]
**时长**：[Xs]  |  **风格锚定**：[...]

### 素材清单（有参考素材时）
- `<Picture 1>` ← [用户的哪个文件]：用途说明
- `<Audio 1>` ← [...]：音色参考 / BGM 复用

### 提示词
```text
[完整可复制的提示词]
```
> **API 端**：中文自然语言，**不要**出现 `[Shot N]` / `integrated_multimodal_description` 等字段名——
> 手工半结构化会和 Context-IR 打架（镜头数翻倍、时间戳错位）。范例见 playbook 第 1 节。
> **本地权重端**：完整英文结构化格式，字段逐字精确。

### 我替你做了哪些决策
- 时长定 Xs，因为 [...]
- 前 2 秒放 [...]，因为 [...]
- 没给 non_diegetic_music，因为 [...]
- [其余默认项]

### 下一步
[跑之前要注意的 / 出问题往哪查]
```

**「我替你做了哪些决策」这一段不能省。** 大部分 prompt enhancer 是黑盒，用户用一百次还是不会描述需求；说清楚了，用户下次自己就能给到更好的输入。

---

## 质量自检

### 两端都要过

- [ ] 平台已确认（API 走人话 / 本地走结构化），**没有混用**
- [ ] 模式判断正确（图是"某一帧"还是"长这样"）
- [ ] 时长 ≤15s，素材数未超官方上限（图≤9 / 视频≤3 且合计≤15s / 音频≤3 且不单独使用 / 总数≤12）
- [ ] 台词是用户给的**逐字原文**，没有编造
- [ ] 前 2 秒不是"缓缓推进"开场
- [ ] 三层声音各司其职、无重复
- [ ] 「我替你做了哪些决策」已写
- [ ] 有值得记的翻车/成功 → 写进 `experiments/cases/`

### 仅本地权重端（API 端整段标 N/A，不要自检结构化格式）

- [ ] 字段名逐字正确，Ref2VA 六段顺序没错
- [ ] `[Shot 1]` 无时间戳，后续时间戳严格递增且 ≤ 片长
- [ ] 运镜词全部来自官方词表，没有自造词
- [ ] 风格锚定已写（Ref2VA 在 `[Shot 1]` 之前独立成句）
- [ ] 台词包在 `<d>[语言]</d>` 内，说话人 ID 稳定
- [ ] 旁白后紧跟 lips-closed 声明
- [ ] `non_diegetic_music` 无情绪词，没有就是 `N/A`
- [ ] Ref2VA：每个标签在 `retention_analysis` 有一行，关系标记来自固定枚举
- [ ] **Ref2VA：正文没有引用"只在 `<Subject N>` 定义里被提及"的 `<Picture N>`**（悬空标签，最高频格式错误）
- [ ] 标签编号与实际连线顺序一致
- [ ] `detailed_description` 约 350–500 英文词
      　└ **例外**：官方原文是 `normally`，**台词密集时以装完完整台词时间线为准**，不要为凑词数硬砍台词（`official-ref-en.md` §5.2）
      　└ **例外**：视频编辑类任务按源视频复杂度伸缩，不受此区间约束
- [ ] 时长是合法帧数档（`17k+5`），不是 8.0s 这种非法值

---

## 失败记录（这个 skill 的燃料）

**改写器每一步都在做决策，决策依据只能来自实测。**没有失败记录的改写器手里只有通用电影词汇，于是它只会注水。

跑完一条（无论成败）值得记的，按 [experiments/cases/case-template.md](experiments/cases/case-template.md) 落一份。
重点记**失败版本和为什么死**——成功的提示词哪都能抄到，失败的抄不到。

---

## 来源

- 官方两份指南原文（`references/official-*.md`）取自 [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing/references)，版权归 MiniMax 所有，未做修改
- 三段式架构与 Context-IR 说明：[HF MiniMaxAI/MiniMax-H3 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)
