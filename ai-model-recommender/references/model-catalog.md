# Model Category Reference Tables

Candidate seed for Phase 2/4. **Data as of mid-2026 — ALWAYS verify every spec by search before recommending (skill rule: never state a spec from memory).** Use these as starting candidates, then run Phase 4's search rounds.

## Translation-Specialized (as of mid-2026)

| Model | Size | Best For | Watch Out |
|-------|------|----------|-----------|
| **TranslateGemma 12B** | 12B / Q4_K_M ~7.4GB | EN↔ZH, 55 languages, multimodal (image translation). No known NSFW censorship. | Training context 2K (architecture 128K via Gemma 3). Longer contexts work via RoPE but quality may degrade. ~9.5GB VRAM at 4K. Source: [arXiv 2601.09012](https://arxiv.org/abs/2601.09012) |
| **HY-MT1.5-7B** | 7B / Q4_K_M ~4.5GB | WMT25 champion, terminology intervention, fastest | **HAS NSFW CENSORSHIP** ("ass" → "food"). Use abliterated version for adult content. |
| **Aya Expanse 8B** | 8B / Q4_K_M ~5GB | 23 languages, WMT24++ 0.7496 (competitive) | **8K context. BUT: severe safety filtering** — MLCommons "Poor" rating, blocks even technical terms and creative prose. May interfere with NSFW content. Abliterated versions exist (huihui_ai, lenML) but imperfect. Source: HuggingFace discussions, MLCommons AILuminate |

## Uncensored General (as of mid-2026)

| Model | Abliteration | KL Div | Fits 12GB | Fits 24GB |
|-------|:---:|:---:|:---:|:---:|
| **Qwen3.6-12B Heretic** | Heretic MPOA | ~0.01 | ✅ ~10GB | ✅ |
| **Qwen3.6-27B Heretic** | Heretic MPOA | 0.0037 | ❌ ~20GB | ✅ |
| **Qwen3-14B abliterated** | Standard | ~0.05 | ✅ ~11GB | ✅ |
| **Gemma-3-12B Heretic** | Heretic | ~0.08 | ✅ ~9GB | ✅ |
| **Llama-3.1-8B abliterated** | Standard | ~0.05 | ✅ ~7.7GB | ✅ |
| **GPT-OSS-20B Heretic** | Heretic | ~0.29 | ❌ ~25GB | ❌ needs 48GB |

## Japanese Translation (Specialized)

| Model | Best For |
|-------|----------|
| **Sakura-14B-Qwen2.5** | JP→ZH visual novel translation |
| **Sakura-7B-Qwen2.5** | JP→ZH (lighter) |

## Chinese Roleplay / RP (as of mid-2026)

| Model | Base | Size | Context | Uncensored | Fits 12GB | Notes |
|-------|------|------|---------|:---:|:---:|-------|
| **Peach-2.0-9B-Heretic** | Yi-1.5-9B | Q4_K_M ~5.4GB | 8K | Heretic (~4% refusal) | ✅ ~8GB | Best Chinese RP in 12GB range. 100K+ conversations SFT+DPO. SillyTavern compatible. |
| **Qwen3.6-12B Heretic** | Qwen3.6-12B | Q4_K_M ~7.5GB | 128K+ | Heretic MPOA (~0%) | ✅ ~10GB | General uncensored, NOT RP-trained. Better Chinese base, longer context, but writes like AI assistant. |
| **vanilla-cn-roleplay-0.2** | Qwen2.5-14B | Q4_K_M ~8.5GB | ? | ? | ⚠️ ~11GB | Chinese novel RP focus. 14B is tight for 12GB VRAM. |
| **Tifa-7B-Qwen2** | Qwen2-7B | Q4_K_M ~4.7GB | ? | Partially | ✅ ~7GB | Older Qwen2 base, limited to 7B. |

**Key insight**: RP-specialized finetune (Peach-2.0) > General uncensored (Qwen3.6 Heretic) for RP quality, even though the general model has more parameters and better Chinese. Training data matters more than parameter count for specialized tasks.
