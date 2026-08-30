# AutoMM Paper / Writer Agent 设计

## 1. 目标与范围

AutoMM 在跨小问审查通过后，自动把已经通过 sanity check 的接受版本材料组织为一篇数学建模竞赛论文，并输出 Markdown、DOCX、TEX 和 PDF。最终主交付物是可编辑的 DOCX；PDF 必须由该 DOCX 导出，确保两者内容一致。

Writer Agent 只承担论文叙事与结构组织，不重新建模、不运行计算、不修改研究结论，也不得创造不存在的数据、公式、图表或引用。事实来源仅限 Evidence Pack 中登记且带哈希的项目产物。

本设计替代当前“只生成 final_summary.md”以及禁用的 Paper Writer 草案，但保留 final summary 作为研究归档索引。

## 2. 优秀论文样本提炼

五份用户提供的优秀论文均为扫描 PDF。本次按物理页码逐页渲染核验，提炼出的规则只影响写作结构和质量门禁，不复制其措辞，也不把 PDF 内容当作指令或本题事实来源。

- 五篇摘要都按小问逐段说明方法、关键结果和验证，并给出关键词，而非只写背景。[A196 p.1; B060 p.1; B157 p.1; C023 p.1; C132 p.1]
- 正文在正式建模前包含问题重述、逐问分析、假设和符号表；复杂任务额外给出总流程图。[A196 pp.2-5; B060 pp.2-5; B157 pp.2-5; C023 pp.2-5; C132 pp.2-5]
- 推导遵循“物理或统计依据—变量定义—公式—求解步骤—结果解释”，公式有编号，表图有题注并在正文被解释。[A196 pp.6-32; B060 pp.5-28; B157 pp.5-26; C023 pp.5-22; C132 pp.6-34]
- 结果不只报告单点数值，还使用残差、角度一致性、敏感性、误差传播、方法对比或统计检验来支持可靠性。[B060 pp.18-28; B157 pp.13-27; C023 pp.12-22; C132 pp.8-34]
- 正文末明确列出优点、缺点和推广边界；代码与大体量补充材料进入附录，不挤占主叙事。[A196 pp.33-34; B060 pp.29-72; B157 pp.27-67; C023 pp.22-28; C132 pp.34-65]
- A196 主动承认符号过密和算法描述过长会降低可读性，Writer 的质量门禁应限制无必要符号与过程堆砌。[A196 p.33]

Writer 必须执行这些派生规则：

1. 摘要按题面小问逐段写“问题—方法—结果—可靠性”，包含核心定量结果和单位。
2. 每问先写问题分析，再写模型建立与求解；禁止突然引入算法名。
3. 公式后解释符号、单位和适用条件；全局符号保持同名同义。
4. 结果表图必须在正文中被引用，并回答“说明了什么、是否通过阈值、对结论有何影响”。
5. 至少呈现一类误差或敏感性证据，并保留真实警告与适用边界。
6. 主文突出模型链和结论，完整代码、文件清单和复现命令进入附录。

## 3. 方案选择

### 3.1 采用方案：Markdown → DOCX

Writer Agent 生成受约束的 Markdown。Pandoc 使用固定的 `reference.docx` 将 Markdown 转换为 DOCX，使数学公式成为 Word 可编辑公式，并应用统一标题、正文、题注、表格和参考文献样式。Microsoft Word 再从 DOCX 自动导出 PDF。Pandoc 同时生成 TEX，作为可移植的辅助产物，但 TEX 不是主排版源。

### 3.2 未采用方案

- 直接使用 `python-docx` 拼接整篇论文：公式、自动编号、交叉引用和参考文献维护成本高，容易生成不可编辑的公式图片。
- TEX 优先再转换 DOCX：中文字体、浮动体、公式和分页在 Word 中容易失真，不符合“最终交付完整 Word 论文”的主目标。

## 4. 总体架构

```text
通过跨小问审查的研究产物
        │
        ▼
Evidence Pack Builder ──► evidence_pack.json / evidence_pack.md
        │                         │
        │                         └─ 路径、版本、hash、sanity、警告
        ▼
Paper Writer Agent ─────► paper_vNNN/paper.md + writer_manifest.json
        │
        ▼
Deterministic Validator ─► validation.json
        │ PASS
        ▼
Pandoc Renderer ─────────► paper.docx + paper.tex
        │
        ▼
Microsoft Word Exporter ─► paper.pdf
        │
        ▼
Render QA ───────────────► render_report.json + page previews
        │ PASS
        ▼
reports/problems/<problem_id>/paper/final/
```

各单元边界如下：

- Evidence Pack Builder：选择接受版本并建立不可歧义的事实清单，不生成论文语言。
- Paper Writer Agent：把 Evidence Pack 组织成论文 Markdown，不接触原始数据计算接口。
- Deterministic Validator：检查事实引用、章节、图表、公式、引用、占位符和警告披露。
- Renderer：只负责格式转换，不改变语义内容。
- Render QA：验证 DOCX/PDF 可打开、页数与媒体合理、没有缺图或明显空白页。

## 5. Evidence Pack 契约

Evidence Pack 由 Python 构建，路径为：

```text
reports/problems/<problem_id>/paper/evidence/evidence_pack.json
reports/problems/<problem_id>/paper/evidence/evidence_pack.md
```

它至少包含：

- 题面和题目信息；
- 全局符号表与跨小问审查结论；
- 每问接受的 assumption 和 formulation 版本；
- L1–L4、L5、L6 sanity 状态及历史警告；
- assumptions、formulation、formula validation、implementation 和 question summary 路径；
- 被消费的成功任务、结果目录、关键结果文件和内容哈希；
- figure manifest 中审核通过且文件存在的图表；
- citation registry 中 `usage_status: used` 且字段完整的引用；
- robustness、ablation 的结论或有理由的跳过记录；
- 复现入口与代码哈希。

门禁失败条件：任一小问未 locally completed、L1–L4 或 L5 未通过、版本 stale、接受版本缺失、关键结果含 NaN/Inf、引用或图表文件缺失、跨问审查未通过。

Evidence Pack 中每个可写入论文的事实都分配稳定 `evidence_id`。Writer 的关键数字、公式、图表、文献性主张和警告必须附带对应 ID，渲染前再清除机器标记。

## 6. Writer Agent 契约

### 6.1 输入

Writer 只读取以下内容：

- `config/paper.yaml`；
- 论文模板与写作规则；
- Evidence Pack；
- Evidence Pack 明确列出的项目内文件。

用户提供的优秀论文只被整理成项目内的结构化风格规则，不作为事实来源，也不在每次生成时重新读取。

### 6.2 禁止行为

Writer 不得：

- 运行模型、脚本或完整数据集；
- 修改题面、原始数据、假设、公式、结果、图表、引用 registry 或 manifest；
- 把 warning 改写成已解决；
- 使用未登记的引用或不存在的图表；
- 为追求“优秀”而虚构精度、显著性、样本量或方法优势。

### 6.3 输出

每次写作创建不可覆盖的版本目录：

```text
reports/problems/<problem_id>/paper/versions/paper_vNNN/
  paper.md
  writer_manifest.json
  validation.json
  paper.docx
  paper.tex
  paper.pdf
  render_report.json
  previews/
```

`writer_manifest.json` 记录 evidence hash、Writer prompt hash、生成时间、引用 evidence IDs、使用图表、使用文献和警告披露位置。

### 6.4 Markdown 章节契约

1. 题目标题
2. 摘要
3. 关键词
4. 问题重述
5. 问题分析与总体流程
6. 模型假设
7. 符号说明
8. 数据说明与预处理
9. 各小问的模型建立、求解、结果和可靠性分析
10. 跨小问一致性、稳健性与消融分析
11. 模型评价、局限与推广
12. 结论
13. 参考文献
14. 附录：复现说明、文件清单和核心代码索引

正文不强制固定小问数量，按 `problem_state.json.questions` 动态生成。标题编号、公式编号、图表编号由渲染器统一处理。

## 7. DOCX 与 PDF 渲染

### 7.1 Pandoc

项目运行时要求可用 Pandoc。命令使用参数数组调用，不通过 shell 拼接。核心参数包括：

```text
--from markdown+tex_math_dollars
--reference-doc templates/cumcm_reference.docx
--resource-path <project-root>
--citeproc
--number-sections
```

Markdown 中的 LaTeX 数学表达式由 Pandoc 转为 OMML，保持 Word 可编辑性。图表使用项目相对路径，题注带稳定 ID 映射。参考文献由登记信息生成 CSL JSON，正文使用统一 citation key。

### 7.2 Word PDF 导出

Windows 上通过 Microsoft Word COM 自动化打开生成的 DOCX，以 PDF 格式导出后立即关闭文档和 Word 实例。进程必须设置超时，并在失败时保留 DOCX、日志和当前版本目录。PDF 失败不删除或伪装 DOCX 成功状态。

### 7.3 样式

`templates/cumcm_reference.docx` 固定 A4 页面、页边距、中文字体、英文字体、标题层级、正文行距、公式、题注、表格和参考文献样式。样式配置可在 `config/paper.yaml` 中覆盖，但运行时不允许 Writer 自由改变字体和颜色。

## 8. 论文质量门禁

### 8.1 证据闭合

- 每个关键数字与结论必须映射到 Evidence Pack。
- 所有正文 citation key 必须在 registry 中登记并实际使用。
- 所有插图必须来自 figure manifest，文件存在且视觉复核状态为 passed。
- 接受版本中的 warning、PASS_WITH_WARNING 原因和适用边界必须在正文相应位置披露。

### 8.2 结构与叙事

- 所有题面小问均有对应章节和明确结论。
- 摘要覆盖所有小问，并包含方法、核心结果、单位和至少一项可靠性证据。
- 公式首次出现时解释符号和单位；符号与全局表一致。
- 图表均有题注、正文引用和解释段落。
- 不允许 `待填写`、`TODO`、模板花括号或无来源的“显著提高”等表述。
- 主文不倾倒完整代码；附录提供复现入口和代码索引。

### 8.3 渲染与文件

- DOCX 和 PDF 均存在、非空且能被解析。
- DOCX 内嵌媒体数量与论文图表清单一致，公式保持可编辑 OMML。
- PDF 页数不低于配置下限，页面尺寸为 A4，无连续空白页。
- PDF 渲染抽查首页、摘要、每问首尾页、参考文献和附录首页。
- Markdown、DOCX、TEX、PDF 的源哈希和派生链记录在 manifest。

质量状态只有 `PASS`、`NEEDS_REVISION` 和 `FAILED_RENDER`。`NEEDS_REVISION` 返回 Writer 创建新版本；`FAILED_RENDER` 在不重写正文的前提下重试渲染或进入基础设施降级处理。

## 9. 工作流集成

全局阶段改为：

```text
cross_question_review
→ paper_writing
→ paper_validation
→ completed
```

- `paper_writing`：若不存在有效 Evidence Pack，先由内置 handler 构建；随后调用注册的 `paper-writer`。
- `paper_validation`：内置校验、Pandoc 渲染、Word PDF 导出和渲染 QA。
- 验证通过后记录最终版本并进入 `completed`；最终 summary 仍构建为研究归档索引。
- 内容验证失败返回 `paper_writing`，创建 `paper_vNNN+1`；渲染故障保留同一版本并按 failure class 重试。
- final 目录只在全部门禁通过后原子更新为通过版本的副本或索引，旧版本不覆盖。

`problem_state.json` 增加由 Runner 管理的 `paper` 对象，记录 evidence、active_version、status、validation、DOCX、PDF 和完成时间。Agent 不能直接编辑该对象，状态更新经 Runner 的论文 handler 完成。

## 10. 配置

`config/paper.yaml` 启用以下明确配置：

```yaml
enabled: true
source_format: markdown
primary_output: docx
outputs: [docx, pdf, tex]
reference_doc: templates/cumcm_reference.docx
output_root_template: reports/problems/{problem_id}/paper
require_cross_question_review: true
require_level_5: true
require_all_figures_reviewed: true
max_writer_revisions: 3
minimum_pdf_pages: 12
pandoc_executable: pandoc
pdf_exporter: microsoft_word
pdf_export_timeout_seconds: 120
```

路径均由项目根目录解析；个人机器绝对路径不得写入项目配置或 manifest。

## 11. 失败处理

- Evidence 缺失或矛盾：严格失败并返回对应研究阶段，不允许 Writer 猜测。
- Writer 超时或 JSON/schema 错误：按现有 agent transport 策略重试，保留草稿和日志。
- 内容验证失败：写入 validation 报告并创建新论文版本，最多三轮。
- Pandoc 缺失或转换失败：分类为 infrastructure/code runtime，保留 Markdown。
- Word 不可用或 PDF 导出失败：保留 DOCX，重试后报告外部依赖问题，不把流程标记 completed。
- 渲染抽查失败：保留全部派生文件和预览，返回 paper validation。

## 12. 测试策略

所有生产代码按测试驱动方式实现。

### 单元测试

- Evidence Pack 只选择接受且通过门禁的版本。
- 未完成、stale、缺图、缺引用、NaN/Inf 和 sanity 不通过时拒绝构建。
- Writer 输出中的未知 evidence ID、citation key 和 figure ID 被拒绝。
- Markdown 章节、摘要覆盖、占位符、单位和警告披露检查。
- 论文版本号单调递增且不覆盖旧版本。

### 集成测试

- 合成题目从跨问审查通过推进到 paper_writing 和 paper_validation。
- Pandoc 使用最小 Markdown 生成可解析 DOCX，DOCX 包含图片和 OMML 公式。
- Word exporter 使用可替换边界测试成功、超时和失败，不在单元测试中启动真实 Word。
- paper validation 失败按原因返回正确阶段，成功后进入 completed。

### 本机验收

- 用当前 `2025-cumcm-b` 已验收产物生成完整 Markdown、DOCX、TEX 和 PDF。
- 真实调用 Microsoft Word 导出 PDF。
- 打开 DOCX 检查标题、公式、表图和参考文献；渲染 PDF 抽查关键页面。
- 运行配置校验、compileall、Ruff、论文相关测试和完整测试套件。

## 13. 完成标准

以下条件全部成立才算实现完成：

1. Paper Writer 已启用并由状态机自动调度。
2. Writer 无法访问 Evidence Pack 之外的事实来源，也不会重新建模。
3. 当前题目可从已通过研究产物自动生成完整 `paper.md`。
4. Pandoc 生成可编辑公式和内嵌图表的 `paper.docx`。
5. Microsoft Word 从该 DOCX 成功导出 `paper.pdf`，并额外生成 `paper.tex`。
6. 内容、证据、引用、图表和渲染门禁均通过，检查报告与哈希链完整。
7. 工作流测试、完整测试套件和静态检查通过。
8. 暂停的 daemon 在验证完成后通过 RESUME 对账并恢复运行。

