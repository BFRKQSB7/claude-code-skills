#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai-model-recommender skill 验证脚本。

用法:
    python scripts/audit.py [skill_dir]

检查:
    1. SKILL.md token 预算 (默认上限 3800)
    2. 触发词 (frontmatter description) 完整性
    3. 核心工作流标记 (Phase 0-9、关键规则)
    4. 中文语义完整性 (无 �/????/锟，关键中文短语仍在)
    5. references 导航一致性 (SKILL.md 引用的文件存在)
    6. 报告 SKILL.md / 各 reference / 全量 runtime 的 token 规模

退出码: 0 = 全部通过, 1 = 有失败项。
"""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SKILL_NAME = "ai-model-recommender"
DEFAULT_DIR = os.path.expanduser("~/.claude/skills/ai-model-recommender")
TOKEN_BUDGET = 3800

# tiktoken 可选；没有时退化为字符数/4 的估计
try:
    import tiktoken
    _ENC = tiktoken.get_encoding("o200k_base")

    def _tok(text):
        return len(_ENC.encode(text))
except ImportError:
    def _tok(text):
        return max(1, len(text) // 4)

# frontmatter description 里必须保留的触发词（缺任一即破坏触发）
# 注意：必须是 description 中的字面子串（如 "choosing"，而非词根 "choose"）
TRIGGER_PHRASES = [
    "choosing", "comparing", "downloading", "llama.cpp", "Ollama",
    "model selection", "which model should I use", "model comparison",
    "uncensored", "abliterated", "translation models", "GGUF",
]

# 核心工作流标记
WORKFLOW_MARKERS = [
    "Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4",
    "Phase 5", "Phase 6", "Phase 7", "Phase 8", "Phase 9",
    "Core Rules", "VRAM", "Q4_K_M", "llama.cpp", "references/",
    "NEVER state a spec", "symmetrically",
]

# 关键中文短语（语义完整性）
CJK_PHRASES = [
    "你用什么工具调用模型", "主要翻译什么内容", "翻译哪些语言",
    "电脑配置是什么", "角色扮演", "世界书", "文本补全", "中文 RP",
]

CORRUPTION_PATTERNS = [
    (r"�", "替换符 �"),
    (r"锟", "锟"),
    (r"\?{4,}", "????"),
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    skill_md = os.path.join(skill_dir, "SKILL.md")
    refs_dir = os.path.join(skill_dir, "references")
    fails = []
    warns = []

    print(f"== ai-model-recommender audit: {skill_dir}")

    # --- 结构 ---
    if not os.path.exists(skill_md):
        print(f"[FAIL] SKILL.md 不存在: {skill_md}")
        sys.exit(1)
    if not os.path.isdir(refs_dir):
        print("[FAIL] references/ 目录不存在")
        sys.exit(1)

    main_text = read(skill_md)

    # --- 1. token 预算 ---
    main_tokens = _tok(main_text)
    flag = "OK " if main_tokens <= TOKEN_BUDGET else "FAIL"
    if main_tokens > TOKEN_BUDGET:
        fails.append(f"SKILL.md {main_tokens} tokens 超过预算 {TOKEN_BUDGET}")
    print(f"[{flag}] SKILL.md tokens: {main_tokens} (预算 {TOKEN_BUDGET})")

    # --- 2. 触发词 ---
    desc = ""
    m = re.search(r"^description:\s*\|\s*$(.*?)^---", main_text, re.M | re.S)
    if m:
        desc = m.group(1)
    missing_trig = [p for p in TRIGGER_PHRASES if p.lower() not in desc.lower()]
    if missing_trig:
        fails.append(f"description 缺失触发词: {missing_trig}")
        print(f"[FAIL] 缺失触发词: {missing_trig}")
    else:
        print("[OK ] 触发词完整")

    # --- 3. 工作流标记 ---
    missing_wf = [p for p in WORKFLOW_MARKERS if p not in main_text]
    if missing_wf:
        fails.append(f"SKILL.md 缺失工作流标记: {missing_wf}")
        print(f"[FAIL] 缺失工作流标记: {missing_wf}")
    else:
        print("[OK ] 工作流标记完整 (Phase 0-9 + 核心规则)")

    # --- 4. 中文完整性 (SKILL.md + 全部 references) ---
    all_refs = sorted(os.listdir(refs_dir))
    ref_paths = [os.path.join(refs_dir, r) for r in all_refs if r.endswith(".md")]
    all_text = main_text + "\n" + "\n".join(read(p) for p in ref_paths)

    corruption = []
    for pat, label in CORRUPTION_PATTERNS:
        for mm in re.finditer(pat, all_text):
            line = all_text[:mm.start()].count("\n") + 1
            corruption.append(f"{label} @ line {line}")
    if corruption:
        fails.append(f"中文/文本损坏: {corruption[:5]}")
        print(f"[FAIL] 文本损坏: {corruption[:5]}")
    else:
        print("[OK ] 无文本损坏标记")

    missing_cjk = [p for p in CJK_PHRASES if p not in all_text]
    if missing_cjk:
        fails.append(f"关键中文短语缺失: {missing_cjk}")
        print(f"[FAIL] 关键中文短语缺失: {missing_cjk}")
    else:
        print("[OK ] 关键中文短语完整")

    # --- 5. references 导航一致性 ---
    referenced = set(re.findall(r"references/([\w-]+\.md)", main_text))
    existing = set(all_refs)
    dangling = referenced - existing
    unreferenced = {r for r in existing if r != "INDEX.md"} - referenced
    if dangling:
        fails.append(f"SKILL.md 引用了不存在的 reference: {dangling}")
        print(f"[FAIL] 悬空引用: {dangling}")
    else:
        print("[OK ] 所有引用均存在")
    if unreferenced:
        warns.append(f"未被 SKILL.md 提及的 reference: {unreferenced}")
        print(f"[WARN] 未被主文件提及: {unreferenced}")

    # --- 6. token 规模报告 ---
    print("\n== token 规模 (o200k) ==")
    print(f"  SKILL.md:            {main_tokens:>6}")
    ref_tokens = {}
    for p in ref_paths:
        t = _tok(read(p))
        ref_tokens[os.path.basename(p)] = t
        print(f"  references/{os.path.basename(p):<28} {t:>6}")
    total = main_tokens + sum(ref_tokens.values())
    print(f"  全量 runtime:        {total:>6}")
    # 常见加载组合
    print(f"  SKILL.md + catalog:  {main_tokens + ref_tokens.get('model-catalog.md', 0):>6}  (Phase 2/4 种子)")
    print(f"  SKILL.md + catalog + deployment: {main_tokens + ref_tokens.get('model-catalog.md', 0) + ref_tokens.get('deployment-llamacpp.md', 0):>6}")

    # --- 汇总 ---
    print()
    if fails:
        print(f"== RESULT: FAIL ({len(fails)} 项) ==")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    if warns:
        print(f"== RESULT: PASS with {len(warns)} warning(s) ==")
        for w in warns:
            print("  -", w)
    else:
        print("== RESULT: PASS ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
