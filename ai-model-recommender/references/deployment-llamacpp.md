# Deployment Guidance (llama.cpp)

Read this at Phase 8 when the user has chosen a model and needs a working command / parameters. The summary in `SKILL.md` is the condensed version.

## Working Commands

```bash
# llama.cpp server (for LunaTranslator / API-based tools)
./llama-server \
  -m ~/models/[model-file].gguf \
  -ngl 999 \
  --flash-attn \
  -c 4096 \
  --port 8080

# Or CLI for quick test
./llama-cli \
  -m ~/models/[model-file].gguf \
  -ngl 999 \
  --flash-attn \
  -p "[translation prompt]"
```

## Key Parameters

- `-ngl 999`: Offload all layers to GPU. Lower if VRAM is tight.
- `--flash-attn`: Enable Flash Attention. **Always include on NVIDIA RTX 30/40/50 series and newer AMD.** Accelerates prompt processing by 10-30% (more benefit at longer contexts). Blackwell (RTX 50) and Ada Lovelace (RTX 40) see the largest gains. No VRAM cost — it's a pure compute optimization using fused kernels. Exclude only on very old GPUs (GTX 10 series or older) where it may not be supported.
- `-c`: Context length. Must fit: model_size + KV_cache + 1.5GB overhead < VRAM. 12B@32K KV cache is ~5GB → too much for 12GB cards. 12B practical limit is ~20K.
- `--temp`: 0.1-0.3 translation/code, 0.8-1.0 RP/creative, 0.7-0.9 general chat
- `--port`: Any free port for the server mode.

## Flash Attention Compatibility

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

## Sampling Parameters by Task Type

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
