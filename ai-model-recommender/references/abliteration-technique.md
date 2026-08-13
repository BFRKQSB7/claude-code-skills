# Abliteration / Uncensored Evaluation

Read this when the user needs uncensored/abliterated models and you're at Phase 6. The tier summary in `SKILL.md` is the condensed version.

## The Hierarchy (Qwen3.6-27B, 85 GPU-hour forensic analysis)

| Tier | Technique | KL Divergence | Capability Loss | Verdict |
|:---:|-----------|:---:|:---:|------|
| 🥇 | **Heretic** (p-e-w) | 0.0037 | 1.3pp avg | Surgical. Best quality retention. MPOA method. |
| 🥇 | **Huihui** | 0.0074 | 0.5pp avg | Most minimal benchmark loss. Full layer coverage. |
| 🥉 | **HauhauCS** | 0.0242 | 2.0pp avg | Effective but 4x more KL damage than Heretic. Plagiarized. |
| ❌ | **AEON** | 0.0238 | 2.0pp avg | Claims "enhanced capabilities" — data contradicts. |
| ❌ | **Abliterix** | 0.0222 | 4.6pp avg | Worst capability preservation. Likely BNB4 quantization artifact. |

## Key Facts About Abliteration

1. **No technique is truly "lossless."** All remove some capability alongside refusals. The question is HOW MUCH.
2. **Bigger models suffer more.** TruthfulQA loss scales from 2pt (2B) → 8pt (9B) → 9.5pt (27B).
3. **Architecture matters.** Hybrid Mamba2+Transformer models need architecture-aware ablation.
4. **Raw GSM8K scores are misleading on reasoning models.** Abliteration changes thinking efficiency, not ability. Check adjusted scores.
5. **"Aggressive" is a branding term, not a technical one.** It usually means "we modified more tensors" — which is NOT better.

## For the User: Explain Like This

When the user asks about their uncensored models, explain:
- Their technique tier and what it means
- Quantified quality loss vs alternatives
- Whether they could upgrade to a better-abliterated version of the same base model
- That "0 refusals" and "0 quality loss" are marketing, not engineering
