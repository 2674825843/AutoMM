# 实施记录：2026-08-31 论文样式与交付升级

用户最终批准的计划以当前会话最后的 PLEASE IMPLEMENT THIS PLAN 为准，替代旧计划的“不重写当前论文”条款。

- 基线：107 passed in 32.86s，分支 codex/paper-writer-agent；现有用户修改不覆盖、不一并提交。
- 2026-08-31T04:04Z：通过 harness control PAUSE 暂停；输出遇 GBK 错误但控制已生效。通过 stop.flag + pending_wakeup 正常退出 daemon PID 24048，锁/PID 已释放。
- 已撤下正式交付至 problems/2025-cumcm-b/paper/withdrawn/final-v004-20260831-0405；可恢复，未永久删除。
- 模板 SHA256：91710F1D43380961DAE3DCCEEBA78F2353F338704B979CE1C94D70A6F55574DC
- v004 DOCX SHA256：4D4BB5DF1C7345ED5C82FC94B7CB39CBB10B41D640F65C4170179DC5AE7917B9
- v004 Markdown SHA256：F5B23DC442398CF5EA82B58698A0E96EB67DCB690FC2E7AB93E1EEABFF27C6F3
- 设计交接：语义模块产生 publication_manifest，样式与交付模块共用它；不各自重算图号。渲染接口保持兼容。
- 待完成：模板样式、语义题注、公开内容门禁、交付与重写、回归、真实论文、Word验收、恢复daemon。

## 进度追加

- 新模块paper_semantics/paper_delivery及受控rewrite已实现基础链路；独立审查publication_review发现7项Important，集中修复由publication_fixes唯一代理负责，brief见publication-fix-brief.md。
- docx_styles子任务已完成：20样式+4渲染专项通过；真实Word烟测2页、图1/表1与样式窗格有效，图片/公式/三线表可见。视觉检查发现首个二级标题显示1.2，纳入集中修复第8项。
- 全量曾142 passed/1 schema失败（新const缺type），已修复且该测试及配置校验通过；需修复波后重跑全量。
- Ruling: 正式发布改为先完整准备临时final（内含交付），单次rename到paper/final，对外入口paper/final/交付 — 解决双目录发布导致的半成品和恢复死锁 — 路径变化需更新所有入口/测试/文档。
- 当前证据sha256从6374ef02fd5a459dc6388aff56c1d4e7f0c36a4b8ad40ee46b3c3ef77b769025变为5bef289233d22cb5f0348c85b19ff9cf74389b94235ed57bf8a05a1081bd94c9。仅三个question_summary.md变化；questions字段仅对应artifact_evidence_ids变化；其余模型/结果/图表/引用相同。已询问用户是否允许只读复核后登记新快照，未收到回复，禁止绕过。
- 附件2.xlsx当前sha256为2E67444B61B90826C1FFE043FB0F3E7D3470FAC9A005F8842F231EF3D64B34D1，与下载README中24B3113E80D5EC5458BA4F447DF9ED185578481E8B0081BDF0673689505E49D0不同。来源说明也未声明分发许可。已询问用户4个附件是否可分发，未收到回复；不打包未经许可的原始输入。
- 只读核验已确认新prob02/03摘要的关键厚度与既有results JSON相符；尚不代表全面重新验收或已获用户授权快照。

## 边界审查

|任务接口|检查结果|
|样式/语义|独立样式模块接收语义标记和统一manifest，需在集成时验证|
|语义/交付|图片正式序号与来源由同一manifest决定|
|交付/重写|归档旧final，保留历史；新版本交付验证完成才进入completed|
|旧计划/用户最终批准|用户明确改为重写并包含可分发数据，最终批准优先|

## 样式实现子任务（task-1-brief）

独占 scripts/automm/docx_styles.py（新）、tests/test_docx_styles.py（新）。不要修改 paper.py/config/conftest，由主代理集成。不要控制daemon、修改运行状态/产物、提交或创建分支。不派子代理。

实现 inspect_template(template_path: Path, style_map: dict | None = None) -> dict 和 adapt_docx(docx_path: Path, template_path: Path, style_map: dict | None = None, publication_manifest: dict | None = None) -> dict。定义 DEFAULT_STYLE_MAP。

用户模板 E:/项目/AutoMM/数模论文标准模板.docx 只读。按name查找真实styleId，必要样式或类型缺失严格失败。样式名称映射：title=Title、heading1..3=heading 1..3、body=Normal、image=图片、figure_caption=图注、table_caption=表注、table=三线表、table_text=表格、display_math=行间公式辅助样式、bibliography=参考文献、ordered_list=有序列表、unordered_list=无序列表、code=Plain Text。

保持模板原styles.xml、defaults、继承和关联样式；保留字体和主题依赖；清除Pandoc新增BodyText/FirstParagraph/Compact/高亮等未映射样式。清理版式直接覆盖（字体字号对齐缩进行距边框等），保留内容性bold/italic及数学、图片尺寸、表格列宽。表格绑定三线表并开启firstRow条件样式，单元格表格样式。

上游将使用Pandoc custom-style映射。未传自定义语义时适配默认Pandoc heading1为题目、heading2为正文一级；公式OMML独立段落绑定公式样式；图片和题注识别正确。列表保留层级，编号重绑定模板原定义。参考文献有序号，不双重编号。支持通过manifest中的figures/tables（number,title）核对题注；对接具体标记可与主代理沟通。

模板章节编号numId1同时有lvl7表和lvl8图：必须为图表独立实例引用模板定义，不重定义格式；图注继承表注编号。模板正文为摘要之后第3节，解析有效继承页眉页脚（footer PAGE字段在先前节），保持关系依赖，单节从1开始，不复制封面内容。

先写行为测试并看到失败再实现。使用真实模板+Pandoc生成隔离综合样例，无生产输出。测试模板哈希、规范化style XML一致、所有引用有效、页眉页脚关系、语义强调、公式图片、列表三线表。报告完整TDD命令输出及文件列表到 docs/superpowers/plans/task-1-report.md。上报精简结果及剩余接口疑问。
# 最终收尾（2026-08-31）

用户允许切回升级分支后，已完成三份摘要的限定范围复核、Word真实编号与图片替代文字缺陷修复、参数依赖补齐，并通过受控操作生成paper_v007。正式交付为paper/final/交付，含30页论文Word、38幅图片及支撑代码/配置；原始附件未获分发许可而排除。全量198项通过，daemon恢复且正常idle。详细审计见reports/paper-upgrade-final-acceptance.md。旧v004及模板哈希保持；无重新建模计算。以下为之前各阶段的历史进度。
