---
name: paper-writing
description: Use when AutoMM 已通过跨小问审查并需要生成、校验或重新渲染数学建模竞赛论文。
---

# Paper Writing

## 核心原则

论文是已验收研究的证据闭合表达，不是第二次建模。完成标准是同一版本的 Markdown、DOCX、TEX、PDF、校验报告与哈希链全部通过。

## 前置门禁

运行 `python scripts/build_paper.py evidence --problem-id <id>`。只有所有小问 locally completed、接受版本有效、L1–L4 与 L5 通过、无 stale、图表视觉复核通过、引用完整且跨问审查 passed 时才继续。

## 写作

运行 `python scripts/build_paper.py draft --problem-id <id>` 创建不可覆盖的 `paper_vNNN`。只读取 Evidence Pack 白名单文件；关键事实保留 `<!-- evidence:ID -->`，引用使用 `[@ID]`，图表使用 stable ID。按小问写“问题—方法—结果—可靠性”，保留全部 warning、局限和适用边界。

## 校验与渲染

运行 `python scripts/build_paper.py build --problem-id <id> --version paper_vNNN`。内容校验必须 PASS；Pandoc 生成 DOCX 和 TEX，Microsoft Word 从 DOCX 导出 PDF。失败时保留当前版本和日志，不覆盖旧版本，不把部分成功标成 completed。

## 禁止行为

不得运行模型或完整数据集；不得修改题面、数据、假设、公式、结果、图表/引用 registry 或受保护状态；不得读取 Evidence Pack 之外的事实文件；不得隐藏 warning 或虚构结果。

## 快速判断

| 状态 | 动作 |
|---|---|
| Evidence 门禁失败 | 返回对应研究阶段，不写论文 |
| 内容校验 NEEDS_REVISION | 创建下一 `paper_vNNN`，保留旧版本 |
| FAILED_RENDER | 保留 Markdown/DOCX/TEX，在同版本重试基础设施 |
| 内容与渲染 PASS | 发布 `paper/final/`，再进入 completed |

## 常见错误

- 直接读取原始数据补写数字：数字必须先进入已验收结果和 Evidence Pack。
- 删除 `PASS_WITH_WARNING` 以改善观感：必须在结果或局限章节原样披露。
- 用图片公式替代 Word 公式：DOCX 必须保留 OMML 可编辑公式。
- 覆盖旧论文：每次内容修订创建新版本；渲染重试才复用同一版本。
