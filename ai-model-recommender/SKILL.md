---
name: ai-model-recommender
description: |
  Recommend the best local LLM for a user's specific needs. Use this skill whenever the user asks about choosing, comparing, or downloading AI models — especially for local deployment with llama.cpp, Ollama, or similar tools. Also trigger when the user mentions model selection, "which model should I use", model comparison, uncensored / abliterated models, translation models, or wants to find GGUF quantized models for their hardware. Do NOT rely on surface-level knowledge — always follow the deep research methodology in this skill.
---

# AI Model Recommender

Recommend the best local LLM for a user's specific use case and hardware. Never recommend based on brand familiarity or a single search result. Every recommendation must survive adversarial verification.

## Core Rules (learned from failure)

1. **Don't name a model until Phase 4.** Research first, recommend once — never retract-and-repick mid-conversation.
2. **Never trust official benchmarks blindly.** "WMT champion" means nothing if the model censors the user's content.
3. **Always check content filtering.** A translation model that sanitizes adult content is useless for VN/GalGame translation.
4. **Always fit VRAM.** weights + KV cache + 1.5GB overhead. A great model that doesn't fit is useless.
5. **More parameters ≠ better.** A 7B translation-specialized model can beat a 32B general model.
6. **NEVER state a spec from memory.** Context length, params, quant size, benchmark scores — every number must come from a search result. If you haven't searched, say "I need to verify this."
7. **Apply criteria symmetrically.** If a criterion eliminates Model A, apply the SAME criterion to your recommendation. If your pick fails your own test, you have a contradiction.
8. **"Uncensored" ≠ "good at RP" ≠ "good at translation".** Match training to task: RP needs dialogue finetunes, translation needs translation-specialized models, general abliterated models still write like assistants.
9. **Audit yourself after every recommendation.** Phase 0? Phase 4's 4 rounds? Phase 5 censorship check? Phase 6 abliteration tier? Verify every spec you cited? If you skipped any, you failed.

> The failure narratives behind these rules (TranslateGemma 4K debacle, RP ≠ uncensored general): `references/case-studies.md`.

## Workflow

### Phase 0 — Clarify Needs (most important phase)

Before searching, confirm **use case + content type + hardware** (plus: tool/software, languages, real-time vs batch, existing models). If the user is vague, DO NOT search yet — ASK:
- "你用什么工具调用模型？（LunaTranslator / Ollama / 自己写代码？）"
- "主要翻译什么内容？（游戏/小说/技术文档/日常对话？）"
- "翻译哪些语言？"
- "电脑配置是什么？"

Only proceed with at least: use case + content type + hardware.

### Phase 1 — Hardware Assessment

Get exact specs, don't guess. Windows: `Get-CimInstance Win32_VideoController | Select Name,AdapterRAM`; Linux: `nvidia-smi --query-gpu=name,memory.total --format=csv`.
**VRAM budget:** total = model_file + KV cache + 1.5GB overhead. Q4_K_M sizes: 7-8B ≈ 4.5-5.5GB, 12-14B ≈ 7.5-9GB, 20B ≈ 12GB, 27-35B ≈ 17-20GB. KV cache: 4K ctx ≈ 1-2GB (7-8B) / 2GB (12-14B); 8K ≈ 2GB / 4GB; 32K ≈ 8GB / 16GB.
**Hard rule:** if model + KV > VRAM, reduce context / quant / size. Never recommend CPU offloading for real-time use.

### Phase 2 — Classify the Use Case

| Use case | Category | What to search |
|---|---|---|
| Translation (language pair) | Translation-specialized | WMT/XCOMET, language coverage |
| General chat (uncensored) | Abliterated general | abliteration quality, HarmBench ASR |
| Code generation | Code-specialized | SWE-bench, HumanEval, LiveCodeBench |
| Creative writing / RP | RP-specialized finetune (NOT just uncensored) | dialogue quality, character consistency, SillyTavern compat |
| Multimodal (image understanding) | Vision-language | MMMU, OCR accuracy, mmproj availability |
| Long documents | Large context | native context length, KV efficiency |

A general model CAN do translation, but a translation-specialized model ALWAYS wins at the same size. Same logic applies to every specialized category.

### Phase 3 — Audit Existing Models

Check what the user already has (`ls ~/models/ ~/.ollama/models/ ~/.cache/lm-studio/`). If they already own a fit, say so — don't push downloads. Mention repurposable and redundant models explicitly.

### Phase 4 — Deep Research (core, minimum 4 rounds)

Never stop at one search; the first result is often wrong.

- **R1 Candidate discovery:** `best [category] [year] [use case]`, `[model] review real world [use case]`, reddit threads.
- **R2 Adversarial verification (most important):** `[model] problem limitation`, `[model] censorship filter NSFW`, `[model] bad review`. For uncensored: `[model] abliteration quality loss analysis`.
- **R3 Head-to-head:** `[A] vs [B] comparison [use case]`, real-world reddit.
- **R4 Deployment:** `[model] GGUF Q4_K_M download huggingface`, `llama.cpp compatibility`, `VRAM usage [quant] [ctx]`.

**Evaluate:** official benchmarks = potential; community reviews (Reddit/CSDN/Zhihu/HF discussions) = reality; independent forensics = gold. **Red flag:** high scores + zero user reviews = unproven — don't recommend as first choice.
**Context budget:** research incrementally — summarize each round to 2-3 lines and reuse across rounds; don't dump full benchmark tables or chat logs into context. Optional candidate seed: `references/model-catalog.md` (ALWAYS verify by search).

### Phase 5 — Content Filtering Audit

For translation models: search `[model] NSFW censor filter adult content translation` + HF discussions. Evidence of sanitization (e.g. "ass"→"food") = **DEALBREAKER** for adult use cases. Community abliterated version = usable but quality risk.
For uncensored models: refusal rate (HarmBench ASR >95% = truly uncensored), quality retention (KL div <0.01 excellent / <0.1 good / >0.3 damaged), technique (Heretic MPOA > Huihui > HauhauCS > random), benchmark impact (TruthfulQA/GSM8K/MMLU delta >5pt = concerning).

### Phase 6 — Abliteration Tier (only if user needs uncensored)

| Tier | Technique | KL div | Notes |
|---|---|---|---|
| 🥇 | **Heretic** | 0.0037 | Surgical, best quality retention (MPOA) |
| 🥇 | **Huihui** | 0.0074 | Minimal benchmark loss |
| 🥉 | **HauhauCS** | 0.0242 | 4× KL damage vs Heretic; plagiarized |
| ❌ | **AEON / Abliterix** | ~0.024 | Claims contradicted by data |

No technique is lossless; bigger models lose more (TruthfulQA 2pt@2B → 9.5pt@27B); "aggressive" is branding, not technical. Full analysis + user-facing explanation: `references/abliteration-technique.md`.

### Phase 7 — Final Recommendation

Present a ranked comparison table, then a single pick:

```markdown
| Model | Size | Fits VRAM? | Quality | Speed | Risk/Issue | Verdict |
|-------|------|:---:|:---:|:---:|------|:---:|
| Model A | X GB Q4_K_M | ✅/❌ | ⭐⭐⭐ | ⭐⭐⭐ | Issue | Best if... |

## Recommended: [Model] (Q4_K_M)
- [Specific reason tied to use case / hardware / quality]
**Tradeoffs you're accepting:** [honest limitations]
**Download:** huggingface.co/[author]/[repo] → [model]-Q4_K_M.gguf (~X GB)

## Alternative: [Model]
For if [specific scenario]...
```

**Key principles:** name a specific GGUF file + source (e.g. `bartowski/Qwen3-8B-GGUF → Qwen3-8B-Q4_K_M.gguf`); always state tradeoffs; always say what you ruled OUT and why; present both candidates if two are viable; never change the recommendation mid-conversation without explaining what new info changed your assessment.

### Phase 8 — Deployment (summary)

llama.cpp: `-m <model>.gguf -ngl 999 --flash-attn -c 4096 --port 8080`. `-ngl 999` = all layers to GPU. `--flash-attn` = always on RTX 30/40/50 & RDNA3, skip on GTX10/Metal. `-c` must satisfy model + KV + 1.5GB < VRAM. `--temp`: 0.1-0.3 translation/code, 0.8-1.0 RP, 0.7-0.9 chat. Samplers differ per task (RP: DRY on; translation/code: low temp, minimal samplers). Full commands, Flash Attention table, sampling table, DRY vs rep_pen, VRAM-aware context sizing: `references/deployment-llamacpp.md`.

### Phase 9 — SillyTavern Backend (companion, on demand)

Only for SillyTavern users choosing a backend. KoboldCPP/oobabooga are WRAPPERS around llama.cpp, not alternatives. ST via OpenAI API loses DRY/XTC/Mirostat (KoboldCPP via Text Completion exposes them). Context Shifting breaks with World Info/Author's Note. EXL2 is faster but Chinese RP is GGUF-only. Decision flowchart + comparison tables + deploy commands: `references/sillytavern-backend.md`.

## References

| File | Read when |
|---|---|
| `references/model-catalog.md` | Phase 2/4 — candidate seed tables (translation / uncensored / JP / RP), mid-2026. ALWAYS re-verify specs by search |
| `references/case-studies.md` | You're about to break a Core Rule, or want the lessons behind the rules |
| `references/abliteration-technique.md` | Phase 6 — full hierarchy, key facts, user-facing explanation |
| `references/deployment-llamacpp.md` | Phase 8 — full commands, tables, sampler guidance |
| `references/sillytavern-backend.md` | Phase 9 — SillyTavern backend choice |

## Reminders

- Trust is fragile: research first, recommend once. Hardware is the ultimate constraint. Use case determines everything.
- Content filtering can silently ruin results — always check before recommending translation models.
- Abliteration quality varies by an order of magnitude.
- If the user already has good models, tell them — don't push downloads.
- **Never state a spec from memory.** If you haven't searched, say "let me verify."
- Apply your own criteria symmetrically. Check before recommending.
- The skill is a checklist, not a suggestion. After every recommendation, audit yourself: Phase 0? 4 rounds? censorship? abliteration tier?
