# Case Studies

Read this when you are about to break a Core Rule, or when you need the full lessons behind the skill's anti-patterns. The Core Rules in `SKILL.md` are the condensed version of these two failures.

## Case Study: The TranslateGemma 4K Debacle

A textbook example of fabricating specs, self-contradictory ranking, and skipping the skill's own phases.

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

## Case Study: RP ≠ "Uncensored General"

Exposes the category error of confusing "uncensored" with "good at RP".

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
