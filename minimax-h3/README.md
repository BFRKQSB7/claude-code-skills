<div align="center">

# MiniMax H3 提示词改写器

**把描述不清的视频需求，改写成 MiniMax H3（海螺 Hailuo 3）能吃的专业提示词**

不是提示词库，是**决策补齐器**。

[![Skill](https://img.shields.io/badge/Type-Agent%20Skill-6E56CF)](SKILL.md)
[![Model](https://img.shields.io/badge/Model-MiniMax%20H3-0EA5E9)](https://github.com/MiniMax-AI/MiniMax-H3)
[![Modes](https://img.shields.io/badge/模式-T2VA%20|%20I2VA%20|%20FL2VA%20|%20L2VA%20|%20Ref2VA-22C55E)]()
[![License](https://img.shields.io/badge/License-MIT-64748B)](LICENSE)

</div>

---

## 这个 skill 解决什么问题

用户说"帮我做个赛博朋克追车，要炸裂"。

市面上的 prompt enhancer 会吐回来：

> 8K 超高清，Octane 渲染，工业光魔级 VFX，电影级质感，史诗氛围，赛博朋克霓虹，极致细节，大师构图……

加了 60 个词，**零个新信息**。模型仍然不知道多长、几个镜头、谁在追谁、有没有声音、前 2 秒放什么。

**用户缺的不是词汇，是决策。** 这个 skill 的职责是替他把决策做掉，而不是给他的原话套上电影术语。

## 核心设计

### 1. 先判平台——这一刀决定输出什么

H3 是三段式系统，不是单个模型：

```
H3-Context-IR  →  H3-Base (768p)  →  H3-Regenerate-2K
（理解 + 改写）      （音视频联合生成）    （in-context 重生成到 2K）
```

**Context-IR 没有开源。** 官方模型卡原话：

> H3-Context-IR is critical to the quality of the final output, so we **strongly recommend** incorporating it
> into your generation pipeline **or following the "Prompting Guidance" to build your own context-processing system.**

于是：

| 你在哪跑 | 该写什么 |
|:---|:---|
| **海螺官网 / MiniMax API**（Context-IR 在跑） | **中文自然语言**。只做决策补齐，手工结构化会和 Context-IR 打架 |
| **本地 ComfyUI / SGLang 开源权重**（没有 Context-IR） | **完整英文结构化格式**。你就是 Context-IR |

本地端写自由文本，就是「台词乱语 / 角色漂移 / 音效错位」的直接病因。不是模型不行，是格式没对。

### 2. 决策补齐，不是词汇堆砌

9 项默认值——时长、风格锚定、镜头数、**前 2 秒放什么**、三层声音、台词、素材分工、画幅。
能默认的一律默认，出稿后在「我替你做了哪些决策」里一次性声明。

### 3. 提问预算分两类

混在一个计数器里会让 Agent 反复纠结"还能不能再问一个"：

- **A 类 · 内容征集**（不计预算）——台词逐字原文、素材用途、平台。这些不是决策，是**无权代劳的输入**
- **B 类 · 决策问题**（≤1 个）——只有"选 A 和选 B 会做出两支完全不同的片子"才占用名额

### 4. 敢说不

纯改写器最大的问题是：**会忠实地把一个平庸想法翻译成措辞专业的平庸想法。**

7 类拒绝触发：概念无钩子 / 超 15s 上限 / 素材超官方限额 / 台词密度超时长 / 模式选错 / 超显存 / 合规风险。

## 覆盖能力

| 模式 | 场景 |
|:---|:---|
| **T2VA** | 纯文本生成 |
| **I2VA** | 首帧驱动 |
| **FL2VA** | 首尾帧插值 |
| **L2VA** | 尾帧收敛 |
| **Ref2VA** | 全参考——角色 / 画风 / 音色 / 动作迁移 |

还包括：官方硬上限速查、五模式对齐指令逐字模板、九条易错规则、10 条翻车对照表、本地端显存/帧数反查、素材分工话术、两端分离的质量自检。

## 安装

```bash
git clone https://github.com/ye4wzp/minimax-h3-prompt-skill ~/.claude/skills/minimax-h3
```

支持 [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) 规范的工具（Claude Code / Cursor 等）会在你提到 H3 / 海螺 / Ref2VA 时自动加载。

## 目录

```
SKILL.md                              路由 + 决策层
references/
  official-base-en.md                 官方指南原文（T2VA/I2VA/FL2VA/L2VA）
  official-ref-en.md                  官方指南原文（Ref2VA 六段格式）
  rewriter-playbook.md                决策默认值 / 五模式配方 / 两端完整范例 / 翻车表 / 显存反查
experiments/
  README.md                           为什么要有失败记录
  cases/case-template.md              case 模板
```

## ⚠️ 当前状态：case 库是空的

**这是这个 skill 现在最大的短板，说在前面。**

改写器每一步都在做决策，决策依据只能来自实测。现在这套是「官方文档 + 第三方实测 + 跨模型经验迁移」的合成品——
凡是标 🔬 的地方，就是它**还没有自己腿**的地方（台词容量表、前 2 秒法则、部分翻车条目、显存表）。

市面上几十个视频提示词仓库收集的都是**成功的**提示词，而决策需要的是**失败的**提示词。
这也是它们做不出好改写器的原因。欢迎提 PR 补 case——**特别是失败的**。

## 来源与许可

- `references/official-base-en.md`、`references/official-ref-en.md` 取自
  [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing/references) 官方仓库，
  **版权归 MiniMax 所有，适用 MiniMax H3 Community License，此处未做任何修改**，仅为技能自包含而附带
- 三段式架构与 Context-IR 说明引自 [HF MiniMaxAI/MiniMax-H3 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- 本地端显存/帧数实测数据来自 [kuronzzhan-droid/minimax-h3-prompt-skill](https://github.com/kuronzzhan-droid/minimax-h3-prompt-skill)（RTX 5090 32GB，非官方数值）
- 其余内容采用 [MIT](LICENSE)
