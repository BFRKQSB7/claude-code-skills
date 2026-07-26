---
name: ai-model-recommender
description: |
  Recommend the best local LLM for a user's specific needs. Use this skill whenever the user asks about choosing, comparing, or downloading AI models — especially for local deployment with llama.cpp, Ollama, or similar tools. Also trigger when the user mentions model selection, "which model should I use", model comparison, uncensored / abliterated models, translation models, or wants to find GGUF quantized models for their hardware. Do NOT rely on surface-level knowledge — always follow the deep research methodology in this skill.
---

# AI Model Recommender

Recommend the best local LLM for a user's specific use case and hardware. Never recommend based on brand familiarity or a single search result. Every recommendation must survive adversarial verification.

## Core Anti-Patterns (learned from failure)

These are the mistakes this skill is designed to prevent:

1. **Recommending before understanding** — Don't name a model until Phase 4. You'll be wrong.
2. **Recommending then retracting then recommending another** — Kills user trust. Deep research first.
3. **Trusting official benchmarks blindly** — "WMT champion" means nothing if the model censors NSFW content.
4. **Ignoring content filtering** — A translation model that sanitizes adult content is useless for visual novel translation.
5. **Equating "uncensored" with "good uncensored"** — Abliteration technique quality varies dramatically.
6. **Recommending a model that doesn't fit the user's VRAM** — Always calculate: weights + KV cache + overhead.
7. **Assuming "more parameters = better" for every task** — A 7B translation-specialized model can beat a 32B general model.
8. **Fabricating model specifications without verification** — NEVER state a model's context length, parameter count, quantization size, or benchmark score from memory. You WILL get it wrong. Every number must come from a search result or official source. If you haven't searched for it, say "I need to verify this" — don't guess.
9. **Using self-contradictory logic to rank models** — "Model A is bad because it only has 8K context, so I recommend Model B which only has 2K instead." This is logically incoherent. Always cross-check: if a criterion eliminates one model, apply the SAME criterion to the model you're recommending. If your recommendation fails your own test, you have a contradiction.
10. **Failing to apply your own skill's rules** — Writing a skill doesn't mean you follow it. After every recommendation, explicitly audit yourself: "Did I do Phase 4's 4 rounds of search? Did I do Phase 5's content filtering audit? Did I verify every spec I cited?"
11. **Confusing "uncensored" with "good at RP"** — A model that never refuses NSFW can still write like a corporate email. RP requires dialogue training, character consistency, and narrative voice — things that only RP-specific finetunes provide. Always search for RP-specialized models FIRST, then check which ones are uncensored. Never recommend a general abliterated model for RP unless no RP model exists in that size class.

### Case Study: The TranslateGemma 4K Debacle

This conversation produced a textbook example of errors 8, 9, and 10:

**What happened:**
- Recommended TranslateGemma 12B as primary, dismissed Aya Expanse 8B as "limited by 8K context"
- Claimed TranslateGemma has "4K context" — a number that was NEVER searched for or verified
- When user challenged the logic ("8K is more than 4K, how is 8K worse?"), the contradiction was exposed

**What searching actually revealed:**
- TranslateGemma: trained on 2K sequences, but built on Gemma 3 architecture (128K native). Practical deployment can use 4K-8K+ via RoPE extrapolation. The "4K" number was fabricated.
- Aya Expanse 8B: 8K context confirmed. BUT has severe safety filtering (MLCommons "Poor" rating, 72.3% sexual content violation rate) — a potential dealbreaker for NSFW content that was never checked.

**Root cause:** Specs were stated from "memory" (actually hallucinated). No adversarial verification was performed. The skill's Phase 4 and Phase 5 were completely ignored by the very conversation that created them.

**What should have happened:**
1. Search for TranslateGemma's actual context length → discover 2K training / 128K architecture
2. Search for Aya Expanse's content filtering → discover severe censorship issues
3. Present BOTH models with VERIFIED specs, let the user decide based on accurate data
4. The comparison would be: "TranslateGemma: no censorship, 2K training context but flexible in practice" vs "Aya Expanse: 8K context, but heavy safety filtering may interfere with GalGame content"

### Case Study: RP ≠ "Uncensored General"

This conversation exposed another category error:

**What happened:**
- User asked for the best uncensored model for role-playing (RP/角色扮演)
- Recommended Qwen3.6-12B Heretic — a general uncensored model — without checking if it was actually good at RP
- Assumed "uncensored = good for RP" because RP needs NSFW freedom

**What searching actually revealed:**
- Top RP models (MN-Violet-Lotus, RPMax, KrakenSakura-Maelstrom) are all based on Mistral Nemo 12B with dedicated RP training — but they're English-only, useless for Chinese RP
- For Chinese RP: Peach-2.0-9B-8k-Roleplay-Heretic (Yi-1.5 base, 100K+ conversation SFT+DPO, SillyTavern compatible) is the best option in the 12GB range
- Qwen3.6-12B Heretic: zero RP training data. Writes like an AI assistant, not a character. Good for general chat, bad for roleplay.
- No Qwen3-based Chinese RP finetune exists at the 12B level yet (too new)

**Root cause:** Confused two distinct requirements:
- "Uncensored" = won't refuse NSFW requests
- "Good at RP" = trained on dialogue, writes in character, understands persona cards

A model can be perfectly uncensored but terrible at RP (writes like a Wikipedia article).
A model can be great at RP but have a 4% refusal rate.

**The correct framework:**
1. First, find RP-specialized models (SFT/DPO on conversation data)
2. Then, check which ones are uncensored or have abliterated versions
3. Never recommend a general uncensored model for RP unless no RP model exists in the size class

---

## Phase 0: Clarify the User's Actual Needs

**This is the most important phase.** Most bad recommendations come from skipping it.

### Required Information Checklist

Before any searching, confirm ALL of the following. If the user hasn't provided something, ASK:

| Question | Why It Matters | Example |
|----------|---------------|---------|
| **What tool/software will call the model?** | Determines API format, prompt template, context window needs | LunaTranslator → needs OpenAI-compatible API |
| **What content will be translated/processed?** | Determines if censorship is a dealbreaker | GalGame/VN → NSFW filtering = dead |
| **What languages?** | Different models excel at different language pairs | Japanese→Chinese (use Sakura) vs English→Chinese (need different model) |
| **What existing models do they have?** | Avoid redundant recommendations, understand ecosystem | Already have Sakura for JP → don't need JP model |
| **Real-time or batch?** | Determines speed vs quality tradeoff | Game hook translation → speed matters; novel translation → quality matters more |
| **Hardware specs?** | Hard constraint on what can run | See Phase 1 |

### When the User is Vague

If the user says something like "推荐一个翻译模型" without context, DO NOT start searching. Ask:

- "你用什么工具调用模型？（LunaTranslator / Ollama / 自己写代码？）"
- "主要翻译什么内容？（游戏/小说/技术文档/日常对话？）"
- "翻译哪些语言？"
- "电脑配置是什么？"

Only proceed when you have answers to at least: **use case + content type + hardware**.

---

## Phase 1: Hardware Assessment

Get exact specs. Don't guess.

### How to Check

```bash
# Windows (PowerShell)
Get-CimInstance Win32_Processor | Select-Object Name
Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM
Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum

# Linux
nvidia-smi --query-gpu=name,memory.total --format=csv
lscpu | grep "Model name"
free -h
```

### VRAM Budget Calculator

```
Total VRAM needed = Model file size + KV Cache + 1.5 GB overhead

KV Cache (rough):
- 4K context  → ~1 GB for 7-8B models, ~2 GB for 12-14B
- 8K context  → ~2 GB for 7-8B, ~4 GB for 12-14B
- 32K context → ~8 GB for 7-8B, ~16 GB for 12-14B

Model file size (Q4_K_M):
- 7-8B  → ~4.5-5.5 GB
- 12-14B → ~7.5-9 GB
- 20B   → ~12 GB
- 27-35B → ~17-20 GB
```

**Hard rule**: If the model + KV cache > available VRAM, either reduce context, reduce quantization, or pick a smaller model. Never recommend a model that requires CPU offloading for real-time use cases.

---

## Phase 2: Classify the Use Case

Map the user's need to a model category. This determines the entire search strategy.

| Use Case | Model Category | What to Search For | Example Models |
|----------|---------------|-------------------|----------------|
| **Translation (specific language pairs)** | Translation-specialized | WMT benchmarks, XCOMET scores, language coverage | TranslateGemma, HY-MT1.5, Aya Expanse |
| **General chat (uncensored)** | Abliterated general model | Abliteration technique, HarmBench ASR, KL divergence | Qwen Heretic, Gemma Heretic |
| **Code generation** | Code-specialized | SWE-bench, HumanEval, LiveCodeBench | Qwen3.6-35B-A3B, DeepSeek Coder |
| **Creative writing / RP** | RP-specialized finetune (NOT just uncensored) | Dialogue quality, character consistency, Chinese fluency, SillyTavern compatibility | Peach-2.0, Tifa-7B, vanilla-cn-roleplay |
| **Multimodal (image understanding)** | Vision-language model | MMMU, OCR accuracy, mmproj availability | Qwen-VL, Gemma 4 |
| **Long document processing** | Large context model | Native context length, KV cache efficiency | Qwen3.6 (262K), Gemma (128K) |

**Critical distinction**: A general model CAN do translation, but a translation-specialized model will ALWAYS do it better at the same parameter count. Don't recommend a general model for translation unless no specialized model fits.

---

## Phase 3: Audit Existing Models

Check what the user already has. Look in common directories:

```bash
ls -lh E:/AI/llama/models/ ~/models/ ~/.ollama/models/ ~/.cache/lm-studio/
```

Then evaluate:
- **Does the user already have a model that fits their need?** → Don't recommend a download if they already own the solution.
- **Can existing models be repurposed?** → Their GPT-OSS-20B might do translation decently as a stopgap.
- **Are existing models redundant with what you'd recommend?** → Mention this explicitly.

---

## Phase 4: Deep Research (Multi-Round Search)

**This is the core of the skill.** Never stop at one search. The first result is often wrong or incomplete.

### Search Strategy (minimum 4 rounds)

**Round 1 — Candidate discovery:**
```
Search: "best [category] model [year] [use case] benchmark"
Search: "[specific model] review real world [use case]"
Search: "site:reddit.com [use case] model recommendation [hardware]"
```

**Round 2 — Adversarial verification (the most important round):**
```
Search: "[model] problem issue limitation [use case]"
Search: "[model] censorship filter NSFW content"
Search: "[model] actual user experience bad review"
```

If the model is uncensored/abliterated, add:
```
Search: "[model] abliteration quality loss benchmark analysis"
Search: "[technique creator] vs [other technique] comparison"
```

**Round 3 — Head-to-head comparison:**
```
Search: "[model A] vs [model B] translation comparison benchmark"
Search: "[model A] [model B] real world [use case] reddit"
```

**Round 4 — Deployment verification:**
```
Search: "[model] GGUF Q4_K_M download huggingface"
Search: "[model] llama.cpp compatibility issue"
Search: "[model] VRAM usage [quantization] [context length]"
```

### How to Evaluate Search Results

- **Official benchmarks** tell you what the model CAN do under ideal conditions.
- **Community reviews (Reddit, forums, CSDN, Zhihu)** tell you what it ACTUALLY does in the real world.
- **HuggingFace discussion tabs** reveal bugs, censorship issues, and deployment problems.
- **Independent forensic analyses** (like Abliterlitics) are gold — they're the only third-party verification available.

**Red flag**: If a model has high benchmark scores but ZERO user reviews, it's unproven. Don't recommend unproven models as first choices.

---

## Phase 5: Content Filtering Audit

**This is the phase that would have prevented the HY-MT1.5 disaster.**

### For Translation Models

Check if the model censors or sanitizes content:

```
Search: "[model] NSFW censor filter adult content translation"
Search: "[model] content filtering sanitize problem"
Search: "site:huggingface.co [model] discussion"
```

Look for specific evidence:
- ✅ "No filtering issues found" — but only trust this after thorough searching
- 🔴 Evidence of sanitization (e.g., "ass" → "food") — **DEALBREAKER** for adult content use cases
- 🟡 Community abliterated version exists — usable but carries quality risk

### For Uncensored Models

"Uncensored" doesn't just mean "no refusals." Evaluate:

| Criterion | How to Check |
|-----------|-------------|
| **Refusal rate** | HarmBench ASR (attack success rate). >95% = actually uncensored |
| **Quality retention** | KL divergence vs base model. <0.01 = excellent, <0.1 = good, >0.3 = damaged |
| **Technique** | Heretic MPOA > Huihui > HauhauCS > random abliteration |
| **Benchmark impact** | Check TruthfulQA, GSM8K, MMLU deltas. >5 point drop = concerning |
| **Plagiarism/ethics** | Check if the technique is properly attributed |

---

## Phase 6: Abliteration/Uncensored Evaluation

If the user needs uncensored models, you MUST understand the technique landscape.

### The Hierarchy (Qwen3.6-27B, 85 GPU-hour forensic analysis)

| Tier | Technique | KL Divergence | Capability Loss | Verdict |
|:---:|-----------|:---:|:---:|------|
| 🥇 | **Heretic** (p-e-w) | 0.0037 | 1.3pp avg | Surgical. Best quality retention. MPOA method. |
| 🥇 | **Huihui** | 0.0074 | 0.5pp avg | Most minimal benchmark loss. Full layer coverage. |
| 🥉 | **HauhauCS** | 0.0242 | 2.0pp avg | Effective but 4x more KL damage than Heretic. Plagiarized. |
| ❌ | **AEON** | 0.0238 | 2.0pp avg | Claims "enhanced capabilities" — data contradicts. |
| ❌ | **Abliterix** | 0.0222 | 4.6pp avg | Worst capability preservation. Likely BNB4 quantization artifact. |

### Key Facts About Abliteration

1. **No technique is truly "lossless."** All remove some capability alongside refusals. The question is HOW MUCH.
2. **Bigger models suffer more.** TruthfulQA loss scales from 2pt (2B) → 8pt (9B) → 9.5pt (27B).
3. **Architecture matters.** Hybrid Mamba2+Transformer models need architecture-aware ablation.
4. **Raw GSM8K scores are misleading on reasoning models.** Abliteration changes thinking efficiency, not ability. Check adjusted scores.
5. **"Aggressive" is a branding term, not a technical one.** It usually means "we modified more tensors" — which is NOT better.

### For the User: Explain Like This

When the user asks about their uncensored models, explain:
- Their technique tier and what it means
- Quantified quality loss vs alternatives
- Whether they could upgrade to a better-abliterated version of the same base model
- That "0 refusals" and "0 quality loss" are marketing, not engineering

---

## Phase 7: Final Recommendation

Present findings as a ranked comparison table, not a single model name.

### Required Format

```markdown
## Final Comparison

| Model | Size | Fits VRAM? | Quality | Speed | Risk/Issue | Verdict |
|-------|------|:---:|:---:|:---:|------|:---:|
| Model A | X GB Q4_K_M | ✅/❌ | ⭐⭐⭐ | ⭐⭐⭐ | Issue description | Best if... |
| Model B | Y GB Q4_K_M | ✅/❌ | ⭐⭐⭐⭐ | ⭐⭐ | Issue description | Best if... |

## Recommended: [Model Name] (Q4_K_M)

**Why this one:**
- [Specific reason 1 tied to user's use case]
- [Specific reason 2 tied to user's hardware]
- [Specific reason 3 tied to quality/performance]

**Tradeoffs you're accepting:**
- [Honest limitation 1]
- [Honest limitation 2]

**Download:**
[huggingface.co/author/repo-name](URL)
→ File: model-name-Q4_K_M.gguf (~X GB)

## Alternative: [Model Name]

For if [specific scenario]...
```

### Key Principles

- **Always name a specific GGUF file and download source.** "Qwen3-8B" is not enough — say "bartowski/Qwen3-8B-GGUF → Qwen3-8B-Q4_K_M.gguf"
- **Always state the tradeoffs.** No model is perfect.
- **Always mention what you ruled OUT and why.** Builds trust.
- **If there are two viable candidates, present both with clear differentiation.**
- **Never change your recommendation mid-conversation without explicitly acknowledging it and explaining why the new information changed your assessment.**

---

## Phase 8: Deployment Guidance

After the user chooses, provide a working command:

```bash
# llama.cpp server (for LunaTranslator / API-based tools)
./llama-server \
  -m E:/AI/llama/models/[model-file].gguf \
  -ngl 999 \
  --flash-attn \
  -c 4096 \
  --port 8080

# Or CLI for quick test
./llama-cli \
  -m E:/AI/llama/models/[model-file].gguf \
  -ngl 999 \
  --flash-attn \
  -p "[translation prompt]"
```

### Key Parameters

- `-ngl 999`: Offload all layers to GPU. Lower if VRAM is tight.
- `--flash-attn`: Enable Flash Attention. **Always include on NVIDIA RTX 30/40/50 series and newer AMD.** Accelerates prompt processing by 10-30% (more benefit at longer contexts). Blackwell (RTX 50) and Ada Lovelace (RTX 40) see the largest gains. No VRAM cost — it's a pure compute optimization using fused kernels. Exclude only on very old GPUs (GTX 10 series or older) where it may not be supported.
- `-c`: Context length. Must fit: model_size + KV_cache + 1.5GB overhead < VRAM. 12B@32K KV cache is ~5GB → too much for 12GB cards. 12B practical limit is ~20K.
- `--temp`: 0.1-0.3 translation/code, 0.8-1.0 RP/creative, 0.7-0.9 general chat
- `--port`: Any free port for the server mode.

### Flash Attention Compatibility

| GPU Architecture | Example GPUs | `--flash-attn` | Benefit |
|---|---|---|---|
| **Blackwell** (RTX 50) | RTX 5070 Ti, 5090 | ✅ Full support | 10-30% prompt speedup |
| **Ada Lovelace** (RTX 40) | RTX 4090, 4070 | ✅ Full support | 10-30% prompt speedup |
| **Ampere** (RTX 30) | RTX 3090, 3060 | ✅ Full support | 10-25% prompt speedup |
| **Turing** (RTX 20 / GTX 16) | RTX 2080 Ti, GTX 1660 | ✅ Supported | 5-15% prompt speedup |
| **Pascal** (GTX 10) | GTX 1080 Ti | ⚠️ May not work | Skip if error |
| **AMD RDNA3** | RX 7900 XTX | ✅ Supported (ROCm) | Similar gains |
| **Apple Silicon** | M1/M2/M3/M4 | ❌ Not applicable | Metal uses different attention path |

**Rule of thumb:** Any GPU made in 2018 or later should include `--flash-attn`. The longer the context, the bigger the benefit — at 32K context, prompt processing can be the dominant latency source, and Flash Attention cuts it significantly.

### Sampling Parameters by Task Type

**Critical: Do NOT use the same sampler chain for all models.** Each task type needs different sampling:

| Task | temp | top-p | top-k | min-p | DRY | Rationale |
|------|------|-------|-------|-------|-----|-----------|
| **RP / Creative** | 0.8 | 0.95 | 60 | 0.05 | ✅ multiplier 0.7-0.8, base 1.75, allowed 2 | DRY replaces traditional rep_pen; min-p prevents gibberish |
| **General Chat** | 0.8 | 0.95 | 60 | 0.05 | ✅ multiplier 0.7 | Newer architectures (Qwen3.6+) handle high temp well |
| **Translation** | 0.1-0.3 | 0.8-0.9 | — | — | ❌ | Deterministic task; fewer samplers = better |
| **Code** | 0.1-0.2 | 0.9 | — | — | ❌ | Lower temp = more accurate code |

**Why DRY over traditional rep_pen:**
- `--repeat-penalty` penalizes ALL repeated tokens indiscriminately
- `--dry-multiplier` + `--dry-base` targets only phrase-level repetition
- Set `--dry-allowed-length 2` so short common words can repeat freely
- When using DRY, set `--repeat-penalty 1.0` (disabled) — they conflict

**VRAM-aware context sizing:**
- 7-9B models: KV cache ~1-2GB at 8K, can push to 32K
- 12-14B models: KV cache ~2-3GB at 8K, limit to 16-20K on 12GB cards
- Rule: model_GB + (ctx/1000 × 0.15)GB + 1.5GB < total VRAM

---

## Phase 9: SillyTavern Backend Selection

**This is a companion phase for SillyTavern users.** The backend choice affects sampler availability, performance, and deployment complexity. It is NOT just "pick one" — the architecture diagram matters.

### The Layered Architecture

```
SillyTavern（前端 UI）
    │
    ├── Text Completion API ──→ KoboldCPP ──→ 底层 llama.cpp 引擎
    ├── Text Completion API ──→ llama.cpp server (/completion 端点)
    ├── OpenAI Chat API    ──→ llama.cpp server (/v1/chat/completions)
    └── OpenAI Chat API    ──→ oobabooga ──→ 可内调 llama.cpp / ExLlama / Transformers
```

**Critical:** KoboldCPP and oobabooga are NOT alternatives to llama.cpp — they are WRAPPERS around it. The core inference engine is the same.

### Backend Comparison Table

| Dimension | llama.cpp server | KoboldCPP | oobabooga |
|---|---|---|---|
| **Inference engine** | llama.cpp (native) | llama.cpp (bundled) | llama.cpp / ExLlamaV2 / Transformers |
| **Reason to exist** | Minimal inference API | RP-optimized wrapper | Multi-format experiment platform |
| **GGUF support** | ✅ Native | ✅ Native | ✅ Via llama.cpp backend |
| **EXL2 speed (1.5–3×)** | ❌ | ❌ | ✅ Only if model has EXL2 version |
| **DRY / XTC / Mirostat in ST** | ❌ (OpenAI API strips them) | ✅ Full via Text Completion | ⚠️ Partial |
| **Context Shifting** | ❌ No | ✅ Yes, but see caveats below | ❌ No |
| **Resource overhead** | ~100 MB RAM | ~150 MB RAM | ~500 MB – 1 GB RAM |
| **Install complexity** | Single exe | Single exe | Python + ~35 deps |
| **License** | MIT | AGPLv3 | AGPLv3 |
| **Best for** | Bare-metal serving; API integration | SillyTavern RP; creative writing | Multi-format research; LoRA training |

### The Sampler Problem (Why This Matters)

SillyTavern connected via **OpenAI Chat Completion API** (llama.cpp server default) loses access to the three most important RP samplers:

| Sampler | What it does | Available via OpenAI API? | Available via Text Completion? |
|---------|-------------|:---:|:---:|
| **DRY** | Penalizes repeated phrase patterns | ❌ | ✅ |
| **XTC** | Randomly skips top-prob tokens, forces creativity | ❌ | ✅ |
| **Mirostat** | Adaptive perplexity targeting for stable long output | ❌ | ✅ |
| Temperature | Standard randomness | ✅ | ✅ |
| Top-P / Top-K | Standard truncation | ✅ | ✅ |

**Result:** llama.cpp server 引擎本身支持 DRY/XTC/Mirostat（通过 `/completion` 原生端点），但 SillyTavern 走 OpenAI API 路径时拿不到这些采样器。KoboldCPP 通过 Text Completion API 原生暴露全部采样器，SillyTavern 可以直接控制。

### Context Shifting: Promise vs Reality

Context Shifting is KoboldCPP's headline feature — it shifts the KV cache in-place when old messages are truncated, avoiding full reprocessing (~22s → ~0.8s when it works).

**BUT it has fundamental incompatibilities with SillyTavern features:**

| SillyTavern Feature | Breaks Context Shifting? | Why |
|---|---|---|
| World Info / 世界书 (keyword-triggered) | 🔴 YES | Dynamic mid-context insertion → prefix no longer matches |
| Author's Note (changing content) | 🔴 YES | Any text change → cache miss |
| Example Messages (Gradual Push-Out, default) | 🔴 YES | Example dialogue block shifts position → mismatch |
| Summarize extension | 🔴 YES | Injects summary → prefix changes |
| Vector Storage / Smart Context | 🔴 YES | Dynamic content injection |
| Example Messages (Always include) | 🟢 FIXED | Stable position → shift succeeds |
| Pure linear chat, no World Info | 🟢 Works | Only new tokens appended, old ones truncated from front |

**Fix for Example Messages:** Set to "Always include" in User Settings. This alone fixes shifting for many users. But World Info activation will still break it every time.

**Bottom line:** If the user uses World Info or Author's Note (most RP users do), Context Shifting delivers zero benefit. Don't recommend KoboldCPP FOR Context Shifting; recommend it for the sampler advantage.

### EXL2 vs GGUF: When EXL2 Matters

EXL2 (ExLlamaV2) is 1.5–3× faster than GGUF on modern NVIDIA GPUs with Flash Attention. But:

| Factor | EXL2 | GGUF |
|---|---|---|
| Speed (RTX 30/40/50) | 🟢 1.5–3× faster | 🟡 Baseline |
| Chinese RP model availability | 🔴 Near zero | 🟢 Everything |
| Hardware compatibility | NVIDIA-only | CPU + GPU + Apple Silicon |
| Quantization granularity | Precise (2.4, 3.0, 4.125 bpw...) | Fixed tiers (Q4_K_M, Q5_K_M...) |

**oobabooga's EXL2 advantage only matters if EXL2 models exist for the user's language.** For Chinese RP, the ecosystem is essentially GGUF-only. This eliminates oobabooga's primary value proposition.

### Decision Flowchart

```
User wants SillyTavern backend?
│
├── Uses World Info / Author's Note? ──→ Context Shifting irrelevant
│   ├── Wants DRY/XTC/Mirostat in ST UI? ──→ KoboldCPP
│   └── Fine with basic samplers? ──→ llama.cpp server (simplest)
│
├── Needs EXL2 speed? ──→ Check: do their models have EXL2 versions?
│   ├── Yes ──→ oobabooga (but most Chinese RP = GGUF only)
│   └── No ──→ KoboldCPP or llama.cpp
│
├── Needs LoRA training? ──→ oobabooga
├── Needs MIT license (commercial embedding)? ──→ llama.cpp server
└── Just wants to RP? ──→ KoboldCPP (best ST integration) or llama.cpp (simplest)
```

### Typical User Profiles

| Profile | Recommended Backend | Why |
|---|---|---|
| **SillyTavern 中文 RP 入门** | llama.cpp server (current) | 够用，不折腾 |
| **SillyTavern RP 追求质量** | KoboldCPP | DRY/XTC/Mirostat 采样器，ST 原生控制 |
| **模型研究者/多格式折腾** | oobabooga | EXL2 + LoRA + 多后端 |
| **API 集成/自动化脚本** | llama.cpp server | MIT 许可，最轻量 |
| **12GB VRAM + GGUF 中文模型** | llama.cpp 或 KoboldCPP | oobabooga 核心优势用不上 |

### KoboldCPP Quick Deploy (if recommended)

```bash
# Download single exe: https://github.com/LostRuins/koboldcpp/releases
# Choose koboldcpp_nocuda.exe (CUDA) or koboldcpp_rocm.exe (AMD)

koboldcpp.exe ^
  --model "E:\AI\llama\models\Peach-2.0-9B-8k-Roleplay-heretic-Q4_K_M.gguf" ^
  --gpulayers 999 ^
  --contextsize 8192 ^
  --port 5001 ^
  --host 127.0.0.1 ^
  --flashattention ^
  --usecontextshift

# SillyTavern connection:
# API: 文本补全 (Text Completion) → KoboldCpp
# URL: http://127.0.0.1:5001
# → ST sampler panel now shows DRY, XTC, Mirostat controls
```

---

## Model Category Reference Table

### Translation-Specialized (as of mid-2026)

| Model | Size | Best For | Watch Out |
|-------|------|----------|-----------|
| **TranslateGemma 12B** | 12B / Q4_K_M ~7.4GB | EN↔ZH, 55 languages, multimodal (image translation). No known NSFW censorship. | Training context 2K (architecture 128K via Gemma 3). Longer contexts work via RoPE but quality may degrade. ~9.5GB VRAM at 4K. Source: [arXiv 2601.09012](https://arxiv.org/abs/2601.09012) |
| **HY-MT1.5-7B** | 7B / Q4_K_M ~4.5GB | WMT25 champion, terminology intervention, fastest | **HAS NSFW CENSORSHIP** ("ass" → "food"). Use abliterated version for adult content. |
| **Aya Expanse 8B** | 8B / Q4_K_M ~5GB | 23 languages, WMT24++ 0.7496 (competitive) | **8K context. BUT: severe safety filtering** — MLCommons "Poor" rating, blocks even technical terms and creative prose. May interfere with NSFW content. Abliterated versions exist (huihui_ai, lenML) but imperfect. Source: HuggingFace discussions, MLCommons AILuminate |

### Uncensored General (as of mid-2026)

| Model | Abliteration | KL Div | Fits 12GB | Fits 24GB |
|-------|:---:|:---:|:---:|:---:|
| **Qwen3.6-12B Heretic** | Heretic MPOA | ~0.01 | ✅ ~10GB | ✅ |
| **Qwen3.6-27B Heretic** | Heretic MPOA | 0.0037 | ❌ ~20GB | ✅ |
| **Qwen3-14B abliterated** | Standard | ~0.05 | ✅ ~11GB | ✅ |
| **Gemma-3-12B Heretic** | Heretic | ~0.08 | ✅ ~9GB | ✅ |
| **Llama-3.1-8B abliterated** | Standard | ~0.05 | ✅ ~7.7GB | ✅ |
| **GPT-OSS-20B Heretic** | Heretic | ~0.29 | ❌ ~25GB | ❌ needs 48GB |

### Japanese Translation (Specialized)

| Model | Best For | Already Owned By User? |
|-------|----------|------------------------|
| **Sakura-14B-Qwen2.5** | JP→ZH visual novel translation | ✅ |
| **Sakura-7B-Qwen2.5** | JP→ZH (lighter) | ✅ |

### Chinese Roleplay / RP (as of mid-2026)

| Model | Base | Size | Context | Uncensored | Fits 12GB | Notes |
|-------|------|------|---------|:---:|:---:|-------|
| **Peach-2.0-9B-Heretic** | Yi-1.5-9B | Q4_K_M ~5.4GB | 8K | Heretic (~4% refusal) | ✅ ~8GB | Best Chinese RP in 12GB range. 100K+ conversations SFT+DPO. SillyTavern compatible. |
| **Qwen3.6-12B Heretic** | Qwen3.6-12B | Q4_K_M ~7.5GB | 128K+ | Heretic MPOA (~0%) | ✅ ~10GB | General uncensored, NOT RP-trained. Better Chinese base, longer context, but writes like AI assistant. |
| **vanilla-cn-roleplay-0.2** | Qwen2.5-14B | Q4_K_M ~8.5GB | ? | ? | ⚠️ ~11GB | Chinese novel RP focus. 14B is tight for 12GB VRAM. |
| **Tifa-7B-Qwen2** | Qwen2-7B | Q4_K_M ~4.7GB | ? | Partially | ✅ ~7GB | Older Qwen2 base, limited to 7B. |

**Key insight**: RP-specialized finetune (Peach-2.0) > General uncensored (Qwen3.6 Heretic) for RP quality, even though the general model has more parameters and better Chinese. Training data matters more than parameter count for specialized tasks.

---

## Reminders

- **The user's trust is fragile.** Each retracted recommendation costs credibility. Research first, recommend later.
- **Hardware is the ultimate constraint.** A great model that doesn't fit is useless. Check VRAM math first.
- **Use case determines everything.** A model perfect for legal document translation might be terrible for GalGame dialogue.
- **Content filtering can silently ruin results.** Always check for censorship before recommending a translation model.
- **Abliteration quality varies by an order of magnitude.** Heretic and Huihui are in a different tier from everything else.
- **Official benchmarks ≠ real-world performance.** Cross-reference with community reviews, forum discussions, and independent analyses.
- **If the user already has good models, tell them.** Don't push downloads they don't need.
- **NEVER state a spec from memory.** Context length, parameter count, file size, benchmark scores — every number must come from a search result. "I think it's 4K" is how you lose all credibility. If you haven't searched, say "let me verify."
- **Apply your own criteria symmetrically.** If you eliminate Model A for having "only X context," Model B must have more than X. Check before recommending.
- **The skill is a checklist, not a suggestion.** After every recommendation, audit yourself: Phase 0? Phase 4 (4 rounds)? Phase 5 (censorship check)? Phase 6 (abliteration tier)? If you skipped any, you failed.
