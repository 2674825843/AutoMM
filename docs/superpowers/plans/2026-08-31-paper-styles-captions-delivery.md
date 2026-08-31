# 写作 Agent 原生 Word Styles、规范题注与交付包 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. 用户已授权实施；最终批准范围、审查修复裁定与进度另见 paper-upgrade-progress.md、publication-fix-brief.md。

**Goal:** 此后生成的论文使用用户模板已有 Word 样式，具有规范图表题注、无内部编号泄漏，并交付一篇 Word 论文和包含对应代码、图片的支撑材料目录。

**Architecture:** 保留 Markdown → Pandoc DOCX → Word PDF 主链。写作阶段生成内容及内部证据映射，确定性的语义层生成正式编号，独立 DOCX 适配器绑定原始模板样式，独立交付器验证并发布 Word 与支撑材料；审计和中间产物仍留在内部版本目录。

**Tech Stack:** Python、现有 Markdown/Pandoc 工具链、OOXML ZIP/XML、Microsoft Word、pytest。

**Spec:** 本任务用户于 2026-08-31 提供的《写作 Agent 原生 Word Styles 接入方案》及三个补充要求；以下全局约束完整吸收这些要求。项目阶段与证据约束见 PROJECT.md、RESEARCH_LOOP.md。

## Global Constraints

- 模板固定为 `E:\项目\AutoMM\数模论文标准模板.docx`，原文件只读，不新增或重定义模板样式。
- 用户最终批准：可恢复撤下当前正式交付，保留历史v004；功能完成后从已验收证据重写新版本，不重新建模或计算。若证据变更先报告复核，不绕过门禁。
- 保留现有论文结构，不复制模板封面、示例文字、示例参考文献或分节骨架。
- 保留 Markdown → DOCX → Word PDF；最终对外交付仅 Word 和支撑材料。PDF、TEX、Markdown、审计报告继续内部归档。
- 版式必须依赖模板已有样式；允许内容性的加粗、斜体，不允许用直接格式模拟版式。摘要对有证据支撑的关键结果数据及专业名词适度加粗，不整段加粗。
- Writer 仅消费已通过原有科学门禁的 Evidence Pack；格式清理不能删除实质 warning、掩盖不确定性或补造缺失公式和数据。
- 图注在图下，表注在表上，均为独立段落，分别使用模板“图注”“表注”。图、表分别按首次出现顺序连续编号。
- 内部图表 ID、证据 ID、warning ID 与质检流水不进入论文可见内容；保留内部追溯记录。
- 实施前安全暂停 daemon 并确认在途动作结束；完成测试后恢复并核实状态。
- 不直接编辑工作流状态或受保护 manifest；状态迁移沿用已有命令和事务路径。

## 文件边界

| 文件 | 责任 |
|---|---|
| `config/paper.yaml` | 模板、样式映射、题注和交付配置 |
| `agents/paper-writer.md` | 正文、摘要强调、科学解释、图表标题与内部证据协议 |
| `scripts/automm/paper.py` | 集成语义转换、更新确定性草稿及门禁，保留 render_paper 调用接口 |
| `scripts/automm/paper_semantics.py`（新） | 结构解析、正式图表/文献编号、证据映射、公开文本检查 |
| `scripts/automm/docx_styles.py`（新） | 模板校验、OOXML 样式绑定、编号与有效正文节设置、格式审计 |
| `scripts/automm/paper_delivery.py`（新） | 支撑材料选择、临时目录构建、完整性验证与幂等发布 |
| `scripts/automm/runner.py` | 将交付检查接入现有发布门禁和恢复逻辑 |
| `tests/test_paper_semantics.py`（新） | 编号、题注、引用、内容清理、摘要强调 |
| `tests/test_docx_styles.py`（新） | 模板完整性、样式引用、直接格式、编号、有效节设置 |
| `tests/test_paper_delivery.py`（新） | 文件范围、哈希、断点与重复发布 |
| `tests/test_paper_rendering.py`、`tests/conftest.py` | 综合渲染与隔离模板 fixture |
| `PROJECT.md`、`RESEARCH_LOOP.md` | 更新对外交付与内部归档的区别 |

## 统一接口

以下为新增接口契约，不表示代码已经存在。路径均使用 pathlib.Path，公开结果使用可序列化 dict，禁止不同模块自行另算图表编号。

```python
# paper_semantics.py
def prepare_publication(markdown: str, evidence_pack: dict) -> dict:
    # 返回 {"pandoc_ast": dict, "manifest": dict, "issues": list[dict]}
    # manifest.figures/tables 每项含 internal_id, number, title, evidence_ids；
    # 图片另含 source_path，引用含内部键和正式序号；issues 非空则不发布。
    ...

# docx_styles.py
def inspect_template(template_path: Path, style_map: dict) -> dict: ...
def adapt_docx(docx_path: Path, template_path: Path,
               style_map: dict, publication_manifest: dict) -> dict: ...
# 上述适配返回审计结果，失败抛出明确异常，不修改模板。

# paper_delivery.py
def build_delivery(version_dir: Path, evidence_pack: dict,
                   publication_manifest: dict, destination: Path) -> dict: ...
# 返回发布路径、文件清单与哈希；清单保存在内部版本目录。
```

## Task 1：模板原生样式与页面适配

**Files:** config/paper.yaml、docx_styles.py、paper.py、test_docx_styles.py、conftest.py。

**Consumes:** 用户只读模板与现有 Pandoc DOCX。**Produces:** inspect_template、adapt_docx；渲染报告中的模板哈希、样式映射、样式与编号完整性、直接格式审计。

- [ ] 先在隔离测试目录提供用户模板副本，测试缺失文件、缺失必要样式、样式类型不符全部失败；测试保留原始文件 SHA-256。不要依赖 conftest 当前只复制目录的行为。
- [ ] 执行 `E:\anaconda\python.exe -m pytest tests/test_docx_styles.py -q`，确认测试因新增能力缺失失败。
- [ ] 实现按名称解析真实 styleId，映射如下；关闭 Pandoc 文本式章节编号，禁止找不到模板时降级。

```python
STYLE_MAP = {
    "title": "Title", "heading1": "heading 1", "heading2": "heading 2",
    "heading3": "heading 3", "body": "Normal", "image": "图片",
    "figure_caption": "图注", "table_caption": "表注", "table": "三线表",
    "table_text": "表格", "display_math": "行间公式辅助样式",
    "bibliography": "参考文献", "ordered_list": "有序列表",
    "unordered_list": "无序列表", "code": "Plain Text",
}
```

- [ ] 将首个论文标题绑定 Title，后续章节层级从 heading 1 开始。摘要、关键词、参考文献、附录标题使用已有标题样式但关闭该段编号；不修改样式定义。
- [ ] 恢复模板原始 styles.xml，保留其默认格式、继承、关联字符样式、字体与主题依赖。清理 BodyText、FirstParagraph、Compact 和语法高亮样式；所有 pStyle/rStyle/tblStyle 必须可解析。
- [ ] 采用属性白名单：移除模拟字体、字号、颜色、缩进、行距、对齐和边框的直接覆盖；保留语义强调、公式结构、图片尺寸及表格列宽。三线表启用首行条件样式，不逐格绘制边框。
- [ ] 解析模板摘要之后正文节的有效页面设置和继承页眉页脚，复制关系依赖，生成单节、页码从 1 开始。不得简单采用 reference document 的首节。
- [ ] 测试样式 XML 规范化后与模板一致，所有样式/编号引用有效，普通段落无版式直接覆盖，公式和图片未损坏；测试通过后形成独立可审查变更。

## Task 2：图表语义、题注和统一编号

**Files:** paper_semantics.py、paper.py、paper-writer.md、test_paper_semantics.py。

**Consumes:** 已接受证据、图片登记和 Markdown。**Produces:** prepare_publication 的结构化正文及统一 publication manifest。

- [ ] 编写测试，覆盖两幅图、一张表、重复正文引用、转义下划线 ID、缺少图题/表题、未知引用、同一图重复出现；先运行确认失败。
- [ ] 在 Markdown 结构层识别图表，不对整篇文本进行无差别正则替换。内部 ID 留在源稿专用标记和映射记录，不作为题注文字。
- [ ] 图和表分别按首次出现顺序分配 1、2、3；正文重复引用复用同一编号。现有无表格登记机制，新增论文级表格条目，记录标题、位置、证据 ID 和表格内部 ID，不引入独立建模阶段。
- [ ] 生成图片段落及独立图注段落；生成独立表注段落及三线表。数据表、符号说明表均须有题注；布局辅助结构不计入编号。
- [ ] 沿用模板原有编号格式，图与表建立独立计数实例，不受正文章节编号重置影响，不同时写入字面前缀造成双重编号。正文引用、Word 题注和支撑材料文件名均消费同一映射；实际显示编号必须与映射验收一致。
- [ ] 缺少标题、未找到证据或无法解析的引用明确返回内容问题，交由现有修订流程处理；禁止猜图号、补造表中数值。
- [ ] 修改现有“正文必须出现 stable_id”的校验，改为校验内部映射覆盖和读者引用完整性，保持证据追溯强度。
- [ ] 运行语义测试及已有论文校验测试，检查连续编号、无重复前缀、图下题注与表上题注，再形成独立可审查变更。

## Task 3：论文语言清理与摘要重点强调

**Files:** paper_semantics.py、paper.py、paper-writer.md、test_paper_semantics.py。

**Consumes:** Task 2 的结构化内容和证据映射。**Produces:** 无运行流水的科学正文、合规摘要强调、公开内容门禁。

- [ ] 将用户提供的长编号、转义编号、“自动质检 passed”“暗边框 0.0”“implementation §6.1”和缺失公式片段作为回归输入；另加入合法下标公式和科学质量评价作为不得误删的对照。
- [ ] 同时修改 LLM 提示与确定性草稿生成器，停止将 visual_review.reason 拼成正文。图后分析应描述对象、趋势、证据支持的结果及意义，不把“图例无遮挡”当作科学结论。
- [ ] 图题规范示例为“图1 三种反演方法的厚度估计对比”，正文引用为“如图1所示”。术语、单位及必要实验条件保留；源证据支持不足时不增加原稿没有的结论。
- [ ] 对确切已知内部标识及其转义形式做结构化映射；未知疑似内部标识报错等待修订，不能一删了之。核验正文、题注、表格、页眉页脚、批注和图片替代文字；审计标记仅留在内部源稿/报告。
- [ ] 实质性模型限制与 warning 改写成读者能理解的论文语言，保留证据标记直到内部验证完成，不能以“去流水”为由消除警告。
- [ ] 摘要使用 Markdown Strong 节点强调已核验关键结果的完整“数值＋单位”和必要专业名词。禁止整段加粗、额外事实、机械重复强调；摘要无数值证据时只强调确有必要的术语，不编造数据。
- [ ] 空括号、缺失结果槽位、丢失公式不能作为合格稿发布；检查源稿与 DOCX 的数学节点，保留正常数学下划线。失败进入内容修订，不自动填数。
- [ ] 运行回归测试，分别验证无 ID 泄漏、QA 叙述不进入论文、科学 warning 未丢失、语义加粗保留和公式可编辑，再形成独立可审查变更。

## Task 4：Word 与支撑材料交付包

**Files:** paper_delivery.py、test_paper_delivery.py、config/paper.yaml。

**Consumes:** 通过样式/内容门禁的版本 DOCX、Evidence Pack、publication manifest。**Produces:** build_delivery 和干净交付目录。

```text
交付/
  论文.docx
  支撑材料/
    代码/
      [按原依赖关系保留各小问、公共模块与必要配置]
    图片/
      图01_三种反演方法的厚度估计对比.png
      图02_反射率谱.png
    运行说明.md
```

- [ ] 先测试代码与图片选择、同名冲突、路径越界、文件缺失、源哈希变化、失败后不存在半成品正式交付、相同版本重复发布。
- [ ] 代码只选择已接受版本及明确的本地依赖，保留导入/资源查找所需目录关系，禁止直接复制全仓库。排除密钥、日志、缓存、历史试验及无关产物。
- [ ] 图片与论文采用相同受验收来源；仅交付副本改为正式图号和简短标题，原文件不改名。若代码依赖原图片名，在运行说明/交付配置中明确输出和交付名称的对应，不盲目改写代码字符串。
- [ ] 运行说明列出环境依赖、入口、输入约定、结果及图片对应关系。必要输入仅在已授权证据范围内包含；外部/未附数据明确说明，不声称缺数据仍可完全复现。
- [ ] 先在同一目标盘的临时目录完整组包并校验，再发布至该版本对应的交付位置；不覆盖指向其他版本的既有交付。内部清单记录源路径、版本和哈希，但不额外堆放在对外交付根目录。
- [ ] 测试交付根目录恰好包含论文.docx 和支撑材料，正文图片与交付图片一一对应，DOCX 与已通过验收版本哈希相同；测试通过形成独立可审查变更。

## Task 5：发布门禁、恢复和端到端验收

**Files:** runner.py、paper.py、test_paper_rendering.py、PROJECT.md、RESEARCH_LOOP.md。

**Consumes:** Tasks 1–4。**Produces:** 可恢复的完整写作、导出、交付链路。

- [ ] 增加集成失败测试：样式校验失败不导出为合格产物；PDF 导出失败保留中间文件；组包失败不发布、不进入 completed；重试相同版本不生成重复目录或覆盖历史。
- [ ] 保持 render_paper 的外部调用接口；新增内部检查接入其报告。runner 先完成现有内容/证据门禁、DOCX 样式检查及内部 PDF 导出，再验证交付包，全部通过后沿用事务路径发布完成状态。
- [ ] 一般升级不自动重开已完成项目；本次用户明确要求重写，通过单独授权的命令事务重开论文阶段，绑定已验收证据，不将正常completed迁移权限放开。
- [ ] 更新文档：内部版本仍有 Markdown/DOCX/TEX/PDF 与审计；用户入口指向干净交付目录，目录实际位置以项目解析器为准，纠正文档中的陈旧路径。
- [ ] 使用独立工作区构造综合论文，涵盖中文摘要强调、三级标题、嵌套列表、文献、多个图表、长表、行内和独立公式、脚注及必要 warning；不运行完整模型。
- [ ] 执行新测试、既有论文测试和全量回归，记录本次真实结果，不沿用历史通过数量。
- [ ] 使用 Word 检查综合样例的样式窗格、实际编号、三线表、公式和页码；检查图表与题注分离分页、重复前缀、公式空缺和明显异常空白页。PDF 仅作为内部分页验收产物。
- [ ] 比较模板与 v004 实施前后哈希完全一致；核查 daemon 恢复且当前项目保持原状态。若无法进行 Word 人工/界面验证，在报告中明确未验收项，不声称全部完成。

## 验收总表

| 用户要求 | 对应任务 | 发布条件 |
|---|---|---|
| 原生模板样式、单正文节与页码 | 1、5 | 样式定义保留，实际引用有效，无版式伪造 |
| 图注、表注及预设格式 | 2、5 | 每个论文图表有独立题注，编号和正文引用一致 |
| 内部编号不出现在论文 | 2、3 | 所有公开文本及替代文字检查通过 |
| 不出现内部质检流水、不丢警告 | 3 | 科学解释和实质限制保留，运行细节不公开 |
| 摘要重要结果及术语加粗 | 3、5 | 内容强调可见且有证据，不模拟版式 |
| 一篇 Word＋代码和图片 | 4、5 | 干净交付包完整、版本一致、无半成品 |
| 不影响当前 v004、原模板 | 全部 | 原文件哈希不变，无当前状态重置 |

## 实施顺序与交接

按 Task 1 → 2 → 3 → 4 → 5 在当前任务内分批实施，每批先失败测试、再最小修复、再回归与审查。代码提交仅包含本任务拥有的修改，不夹带现有用户或后台变更；是否提交服从后续用户指示。用户已确认实施。已授权撤下旧交付但历史不得覆盖；新论文因证据变化等待复核方向时，功能测试可继续，不能通过修改哈希直接推进。
