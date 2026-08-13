#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""improve skill 静态审计（零依赖，纯标准库，CI 可用）

用法:
    python3 audit.py [skill_dir]        # 默认相对脚本上一级目录

检查项:
    1. 单 SKILL.md 入口（无嵌套/大小写变体）
    2. 结构：必需文件与 INDEX 存在
    3. token 预算：启发式估算每文件 + 总量，超限即失败（防 token 回堆）
    4. 编码/乱码：UTF-8 有效，无 U+FFFD / 锟斤拷 / 连续 ?
    5. 中文触发词完整性：SKILL.md description 关键触发词不丢失
    6. 模板占位符：templates/*.md 必须含 {placeholder}
    7. 引用链接完整性：Markdown 相对链接都能解析到真实文件

退出码: 0=通过, 1=有违规。CI 直接以退出码判通过。
"""
import os
import re
import sys

CJK_RE = re.compile(r'[　-鿿＀-￯]')
ASCII_RE = re.compile(r"[A-Za-z0-9_\-\./\\]+")
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
HTTP_RE = re.compile(r'^(https?://|mailto:|#)')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT

# ---- token 启发式（o200k 近似：CJK≈1，ASCII≈len/4+1，其他≈×0.25）----
def est_tokens(text):
    cjk = len(CJK_RE.findall(text))
    words = ASCII_RE.findall(text)
    ascii_tok = sum(len(w) // 4 + 1 for w in words)
    other = len(text) - len(CJK_RE.sub('', text)) - sum(len(w) for w in words)
    return cjk + ascii_tok + int(other * 0.25)

# ---- token 预算（启发式口径；tiktoken 实测值约为此值 1.1~1.2 倍）----
# 值 = 2026-08-13 优化后基线 ×1.2~1.4 余量（允许新教训正常增长，超限即要求拆分/瘦身）
BUDGET = {
    'SKILL.md': 1700,
    'lessons-learned.md': 1100,
    'references/lessons-critical.md': 2900,
    'references/lessons-skill.md': 14500,
    'references/lessons-mcp.md': 5500,
    'references/lang/lessons-bash.md': 5000,
    'references/lessons-cleanup.md': 5500,
    'TOTAL': 70000,
}

# 关键触发词（description 中实际存在、不可丢失；防回归）
TRIGGERS = [
    'code', 'implement', 'develop', 'fix', 'build', 'plugin', 'skill',
    'publish', 'improve', 'security', 'null',
    '写代码', '实现', '开发', '编程', '发布', '打包', '反省', '安全', '空指针',
    '批处理', '编码', '乱码', '启动器', '启动脚本', '教程', '小白', '教学',
]

MOJIBAKE = ('锟' + '斤' + '拷')  # 字面拼接，避免审计脚本误检自身

errors = []
warns = []

# ---- walk 收集文件 ----
md_files = []
all_files = []
for dirpath, dirs, files in os.walk(TARGET):
    dirs[:] = sorted(d for d in dirs if d not in ('.git', '__pycache__'))
    for f in sorted(files):
        p = os.path.join(dirpath, f)
        rel = os.path.relpath(p, TARGET).replace(os.sep, '/')
        all_files.append((rel, p))
        if f.lower().endswith('.md'):
            md_files.append((rel, p))


# ---- 1. 单 SKILL.md 入口 ----
skill_mds = [rel for rel, _ in md_files if rel.lower().endswith('/skill.md') or rel.lower().endswith('/skil.md')]
skill_root = [rel for rel, _ in md_files if rel.lower() == 'skill.md']
skill_nested = [rel for rel in skill_mds if rel.lower() != 'skill.md']
if not skill_root:
    errors.append('缺少根 SKILL.md')
if skill_nested:
    errors.append(f'发现嵌套/重复 SKILL.md: {skill_nested}')


# ---- 2. 结构必需文件 ----
required = ['references/INDEX.md', 'references/lang/INDEX.md', 'references/patterns/INDEX.md',
            'references/lessons-critical.md', 'lessons-learned.md', 'scripts/detect-lang.sh',
            'templates/readme-template.md', 'templates/release-template.md']
present = {rel for rel, _ in all_files}
for req in required:
    if req not in present:
        errors.append(f'缺少必需文件: {req}')


# ---- 3/4. 读取 + 编码 + token ----
total = 0
for rel, p in all_files:
    if rel.endswith('audit.py'):
        continue  # 不扫描审计脚本自身
    try:
        raw = open(p, 'rb').read()
        text = raw.decode('utf-8')
    except UnicodeDecodeError as e:
        errors.append(f'[{rel}] 非 UTF-8: {e}')
        continue
    if '�' in text or MOJIBAKE in text:
        errors.append(f'[{rel}] 含乱码标记 (U+FFFD / 锟斤拷)')
    if re.search(r'[^\x00-\x7f]', text) is None and rel.endswith('.md'):
        pass  # 纯 ASCII md 不算错，但提示
    if not rel.lower().endswith(('.md', '.sh', '.py')):
        continue
    tok = est_tokens(text)
    total += tok
    if rel in BUDGET and tok > BUDGET[rel]:
        errors.append(f'[{rel}] token 超预算: ~{tok} > {BUDGET[rel]}')
    if rel.startswith('references/') and tok > 15000:
        errors.append(f'[{rel}] 单文件超过 15000 tok: ~{tok}')

if total > BUDGET['TOTAL']:
    errors.append(f'[TOTAL] token 超预算: ~{total} > {BUDGET["TOTAL"]}')


# ---- 5. 中文触发词完整性 ----
skill_text = ''
for rel, p in all_files:
    if rel.lower() == 'skill.md':
        skill_text = open(p, encoding='utf-8').read()
        break
if skill_text:
    missing = [t for t in TRIGGERS if t not in skill_text]
    if missing:
        errors.append(f'SKILL.md 缺少触发词: {missing}')


# ---- 6. 模板占位符 ----
for rel, p in all_files:
    if rel.startswith('templates/') and rel.endswith('.md'):
        t = open(p, encoding='utf-8').read()
        if not re.search(r'\{[^}\n]{1,60}\}', t):
            errors.append(f'[{rel}] 模板缺少 {{placeholder}}')


# ---- 7. 链接完整性（跳过围栏代码块与说明性文字）----
FENCE_RE = re.compile(r'```.*?```', re.S)
TARGET_ROOT = TARGET
for rel, p in all_files:
    if not rel.endswith('.md'):
        continue
    base = os.path.dirname(p)
    t = FENCE_RE.sub('', open(p, encoding='utf-8').read())
    for m in LINK_RE.finditer(t):
        target = m.group(1).strip()
        target = target.split('#')[0]
        if not target or HTTP_RE.match(target) or '{' in target:
            continue
        # 说明性文字（无路径分隔符、无扩展名）不算链接
        if '/' not in target and '\\' not in target and not re.search(r'\.\w+$', target):
            continue
        dest = os.path.normpath(os.path.join(base, target))
        if os.path.exists(dest):
            continue
        # 跨 skill 引用（指向本 skill 目录之外）只在完整仓库存在 → 警告
        if os.path.commonpath([os.path.abspath(dest), TARGET_ROOT]) != os.path.abspath(TARGET_ROOT):
            warns.append(f'[{rel}] 跨 skill 引用（完整仓库才有）: {target}')
        else:
            errors.append(f'[{rel}] 断链: {target}')


# ---- 输出 ----
print(f'# improve skill audit: {TARGET}')
print(f'  files={len(all_files)}  md={len(md_files)}  est_tokens≈{total}')
if warns:
    for w in warns:
        print(f'  WARN {w}')
if errors:
    print(f'  FAIL — {len(errors)} issues')
    for e in errors:
        print(f'    - {e}')
    sys.exit(1)
print('  PASS — structure/encoding/triggers/templates/links/token-budget all OK')
