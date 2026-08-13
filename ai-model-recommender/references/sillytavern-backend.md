# SillyTavern Backend Selection

Read this at Phase 9, only when the user is a SillyTavern user choosing a backend. The backend choice affects sampler availability, performance, and deployment complexity. It is NOT just "pick one" — the architecture diagram matters.

## The Layered Architecture

```
SillyTavern（前端 UI）
    │
    ├── Text Completion API ──→ KoboldCPP ──→ 底层 llama.cpp 引擎
    ├── Text Completion API ──→ llama.cpp server (/completion 端点)
    ├── OpenAI Chat API    ──→ llama.cpp server (/v1/chat/completions)
    └── OpenAI Chat API    ──→ oobabooga ──→ 可内调 llama.cpp / ExLlama / Transformers
```

**Critical:** KoboldCPP and oobabooga are NOT alternatives to llama.cpp — they are WRAPPERS around it. The core inference engine is the same.

## Backend Comparison Table

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

## The Sampler Problem (Why This Matters)

SillyTavern connected via **OpenAI Chat Completion API** (llama.cpp server default) loses access to the three most important RP samplers:

| Sampler | What it does | Available via OpenAI API? | Available via Text Completion? |
|---------|-------------|:---:|:---:|
| **DRY** | Penalizes repeated phrase patterns | ❌ | ✅ |
| **XTC** | Randomly skips top-prob tokens, forces creativity | ❌ | ✅ |
| **Mirostat** | Adaptive perplexity targeting for stable long output | ❌ | ✅ |
| Temperature | Standard randomness | ✅ | ✅ |
| Top-P / Top-K | Standard truncation | ✅ | ✅ |

**Result:** llama.cpp server 引擎本身支持 DRY/XTC/Mirostat（通过 `/completion` 原生端点），但 SillyTavern 走 OpenAI API 路径时拿不到这些采样器。KoboldCPP 通过 Text Completion API 原生暴露全部采样器，SillyTavern 可以直接控制。

## Context Shifting: Promise vs Reality

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

## EXL2 vs GGUF: When EXL2 Matters

EXL2 (ExLlamaV2) is 1.5–3× faster than GGUF on modern NVIDIA GPUs with Flash Attention. But:

| Factor | EXL2 | GGUF |
|---|---|---|
| Speed (RTX 30/40/50) | 🟢 1.5–3× faster | 🟡 Baseline |
| Chinese RP model availability | 🔴 Near zero | 🟢 Everything |
| Hardware compatibility | NVIDIA-only | CPU + GPU + Apple Silicon |
| Quantization granularity | Precise (2.4, 3.0, 4.125 bpw...) | Fixed tiers (Q4_K_M, Q5_K_M...) |

**oobabooga's EXL2 advantage only matters if EXL2 models exist for the user's language.** For Chinese RP, the ecosystem is essentially GGUF-only. This eliminates oobabooga's primary value proposition.

## Decision Flowchart

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

## Typical User Profiles

| Profile | Recommended Backend | Why |
|---|---|---|
| **SillyTavern 中文 RP 入门** | llama.cpp server (current) | 够用，不折腾 |
| **SillyTavern RP 追求质量** | KoboldCPP | DRY/XTC/Mirostat 采样器，ST 原生控制 |
| **模型研究者/多格式折腾** | oobabooga | EXL2 + LoRA + 多后端 |
| **API 集成/自动化脚本** | llama.cpp server | MIT 许可，最轻量 |
| **12GB VRAM + GGUF 中文模型** | llama.cpp 或 KoboldCPP | oobabooga 核心优势用不上 |

## KoboldCPP Quick Deploy (if recommended)

```bash
# Download single exe: https://github.com/LostRuins/koboldcpp/releases
# Choose koboldcpp_nocuda.exe (CUDA) or koboldcpp_rocm.exe (AMD)

koboldcpp.exe ^
  --model "~/models/Peach-2.0-9B-8k-Roleplay-heretic-Q4_K_M.gguf" ^
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
