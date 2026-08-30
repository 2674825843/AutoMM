---
name: paper-writing
description: 在跨小问审查通过后，仅依据 Evidence Pack 生成并校验数学建模竞赛论文 Markdown，随后派生 DOCX、TEX 和 PDF。
---

# Paper Writing

## 前置门禁

运行 `python scripts/build_paper.py evidence --problem-id <id>`。只有所有小问 locally completed、接受版本有效、L1–L4 与 L5 通过、无 stale、图表视觉复核通过、引用完整且跨问审查 passed 时才继续。

## 写作

运行 `python scripts/build_paper.py draft --problem-id <id>` 创建不可覆盖的 `paper_vNNN`。只读取 Evidence Pack 白名单文件；关键事实保留 `<!-- evidence:ID -->`，引用使用 `[@ID]`，图表使用 stable ID。按小问写“问题—方法—结果—可靠性”，保留全部 warning、局限和适用边界。

## 校验与渲染

运行 `python scripts/build_paper.py build --problem-id <id> --version paper_vNNN`。内容校验必须 PASS；Pandoc 生成 DOCX 和 TEX，Microsoft Word 从 DOCX 导出 PDF。失败时保留当前版本和日志，不覆盖旧版本，不把部分成功标成 completed。

## 禁止行为

不得运行模型或完整数据集；不得修改题面、数据、假设、公式、结果、图表/引用 registry 或受保护状态；不得读取 Evidence Pack 之外的事实文件；不得隐藏 warning 或虚构结果。
