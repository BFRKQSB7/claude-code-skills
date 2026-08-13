# 大项目上下文预算

> 处理大仓库/长文档时防止 token 爆仓。默认**不整读**。2026-08-13 固化。

## 流程（按序）

1. **目录扫描** — `find . -maxdepth 2 -type d` 先摸结构，不读内容
2. **排除无关目录** — `node_modules` `.git` `build` `dist` `target` `vendor` `__pycache__` `cache` `生成目录`（如 321K 标签库的 `out/`）
3. **token 审计** — 大文件先 `wc -l`/按体积排序，标出哪些值得读、哪些只需 grep
4. **source map** — 关键符号用 `grep -rn` 定位到文件+行，只读命中区域
5. **分阶段增量读取** — 先读入口/主流程 → 按需读依赖，不一次全读
6. **摘要复用** — 已读部分输出一句话摘要记录，后续步骤引摘要不再重读

## 硬规则

- 单次读入候选文件总 token 预算 ≤ ~20K；超了先缩小范围
- 大文件（>10K 行）默认 `Read` 带 `offset/limit`，不整读
- 生成/衍生内容不进上下文：`generated/` `*.min.js` 图片文本化产物
- 子 agent 逐条大列表任务：**小分片 ≤300 条 + 紧凑 TSV + 禁联网（unknown）+ 失败片重跑**（32K 输出硬上限，见 lessons-skill「子 agent 32K 上限」）

## 相关教训

- [[lessons-skill.md]] 子 agent 32K 上限 / 级联复审橡皮图章 / 批量过滤省 token
- 会话级省 token：`.claudeignore` 排除大文件 + 合并请求摊薄共享上下文
