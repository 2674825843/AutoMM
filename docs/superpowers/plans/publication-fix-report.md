# 论文升级集中审查修复报告

日期：2026-08-31。实现范围为 publication-fix-brief.md 第 1–8 项及直接相关入口。

## 结果与验证范围

- 论文专项最终组合：**110 passed in 35.92s**。命令：`E:/anaconda/python.exe -m pytest tests/test_paper_semantics.py tests/test_paper_writer.py tests/test_docx_styles.py tests/test_paper_rewrite.py tests/test_paper_delivery.py tests/test_paper_workflow.py tests/test_paper_rendering.py tests/test_paper_evidence.py tests/test_paper_validation.py -q`。
- 最后为摘要测试补了实际 Pandoc `Strong` 节点断言，单独重跑 Writer 测试：**2 passed**。
- 涉及的 8 个生产 Python 模块/入口和 8 个测试文件 Ruff：**All checks passed**；生产模块 compileall：退出码 **0**。
- 全程设置 `PYTHONIOENCODING=utf-8`，使用指定解释器；测试环境由 conftest 指向隔离临时项目。未运行完整模型、未控制 daemon、未改真实数据/论文/证据/工作流状态、未 commit、未建分支或 worktree。
- 按主代理后续明确指示，**不在子任务执行全量 pytest**；全量测试、真实 Word 验收和针对性复审留给主代理统一执行。

## 逐项 RED / GREEN

### 1. 混排图片丢字与嵌套图表

文件：`scripts/automm/paper_semantics.py`、`tests/test_paper_semantics.py`。

- RED：`Before ![Result](plot.png) after with warning.`、BlockQuote 表格、List 表格原先均返回空 issues，三个断言失败。
- GREEN：独立单 Image 段落只允许空白与合法 evidence/warning 审计注释；混排、嵌套 Figure/Table 返回 issues。原文不会再被当成合法图段而静默删除。
- 已验证正常列表、表格里的数学公式 `x_1=2` / `y_2` 不受影响。

### 2. 公开 Markdown / DOCX 门禁

文件：`paper_semantics.py`、`paper.py`、`test_paper_semantics.py`、`test_paper_rendering.py`。

- RED：`L5 passed, implementation section 6.1, quality_status=passed.`、内部 reports 路径、Windows 绝对路径、ev_/warn_/task_ 标识均漏检；DOCX 审计接口不存在，注入正文/页眉/页脚字段显示/批注/docPr 泄漏均不能拒绝。
- GREEN：新增只读 `audit_public_docx(docx_path) -> dict`，检查全部 word XML 中 w:t / 删除文本与 docPr/cNvPr 的 name/descr/title；按段拼接文本，覆盖跨 run 标识；非段落 w:t 同样检查。报告含 status、issues、checked_parts。
- 渲染在 Word 导出前执行真实 DOCX 审计，结果写入 `render_report.public_audit`，失败不导出 PDF、不 PASS。
- Windows 源路径需在 Pandoc 可能吞掉反斜线指令前识别；源级扫描排除了审计注释和图片/链接资源目标。合法 DOI URL、数学 L5、内部图片资源路径均有不误报测试。
- 审计不扫描媒体关系路径、公式源码和任意数学下划线。

### 3. 授权哈希贯穿新版本准备

文件：`workflow.py`、`paper.py`、`test_paper_rewrite.py`。

- RED：受控重写后缺少 rewrite_evidence_hash；授权或内容修订后改写 summary，prepare 仍创建新版本并覆盖 shared evidence。
- GREEN：受控重写保存 `paper.rewrite_evidence_hash`。prepare 首先 `build_evidence_pack(persist=False)`，与 rewrite hash 或已有 evidence_hash 比较，成功才冻结依赖、持久化共享证据和创建版本。
- 两种哈希入口的变更拒绝测试都确认：**没有创建 paper/versions，也没有覆盖共享 evidence_pack.json**。
- 未增加任何忽略哈希、重核摘要或授权绕过选项。

### 4. 单一版本快照、渲染和交付哈希绑定

文件：新模块 `paper_integrity.py`；`paper.py`、`runner.py`、`paper_delivery.py`、`build_paper.py`；对应 evidence/rendering/delivery/workflow 测试。

- RED：替换版本证据、Writer manifest、publication manifest、Word 字节或任意 `{status: PASS}` 均未被旧交付拒绝；render 缺 evidence_hash，快照修改后仍渲染成功。
- GREEN：`load_version_evidence(version_dir, expected_hash=None)` 验证 canonical 实际内容哈希（排除 created_at 和 evidence_hash 本身），并绑定 writer_manifest；Runner 另核对活动 paper.evidence_hash。
- `verify_rendered_version(...)` 要求 PASS 报告绑定版本、证据、源稿、DOCX/PDF/TEX、publication_manifest 和已有 support_dependencies 文件哈希；交付重新审计实际 DOCX。
- 渲染只读版本快照，无 shared fallback；报告增加 evidence_hash、publication_manifest_sha256、support_dependencies_sha256（快照存在时），保留四种论文产物哈希。
- 新增 RED 还发现渲染过程中源稿变化会让旧 Word 被绑定到新 Markdown；现从实际读取的源字节计算 source_sha256，并在转换后及 Word 导出后复核源稿、图片、DOCX 哈希。图片从读取位置核对 evidence 中的 sha256。
- CLI validate/render/build 同样改用版本快照；没有版本时走 prepare，不能自行 create+generate 绕过授权。CLI 测试将 shared evidence 改成其他快照后，实际版本内容校验仍 PASS。

### 5. 支撑代码依赖快照

文件：`paper_delivery.py`、`paper.py`、`test_paper_delivery.py`、`test_paper_evidence.py`。

- RED：无 build_support_dependencies；修改 requirements 后交付仍 PASS。
- GREEN：`build_support_dependencies(evidence_pack) -> dict` 静态解析 evidence 中的 .py，递归解析同目录/相对模块和 ROOT/scripts 本地导入，并包含包 __init__.py。明确本地模块缺失、越界、疑似凭据、语法无法解析均严格失败。
- 准备版本生成 `support_dependencies.json`，包含 evidence_hash、逐文件 path/sha256、missing、external_imports。requirements.txt 固定为 `scripts/requirements.txt` 的同版哈希；匹配 evidence 的代码配置也列入白名单。
- 交付只按此快照复制到 `支撑材料/代码/<原项目相对路径>`，每个文件复制后再次核对目标哈希。实际递归覆盖 `automm/__init__.py`、`common.py`、`visualization.py` 及其本地依赖；直接交付测试确认这些文件存在。
- 修改 requirements 或本地依赖、以及检查和复制之间修改 code 源文件，均拒绝发布。
- 运行说明指明 `代码/scripts/requirements.txt`、数据位置、计算输出与绘图 results-dir 的准备方式；未私自复制未授权原始数据或验收运行状态。

### 6. 单目录原子发布及中断恢复

文件：`paper_delivery.py`、`runner.py`、`test_paper_workflow.py`、`PROJECT.md`。

- RED：原发布流程不能复用已验收产物；新故障注入用例不能恢复 copy / manifest / state 中断。
- GREEN：新增 `publish_paper(version_dir, evidence, paper_state, final_dir)`。创建唯一 `.final-pending-*`，复制并核验内部产物，在里面构建 `交付`，完成 delivery_manifest 和 final manifest，**单次 rename 到 paper/final**。
- 正式对外入口现在为 **paper/final/交付**；所有记录写最终路径，无 staging 路径。版本侧 delivery_manifest 记录相同最终入口。
- 三类注入均通过：copy 中断、final manifest 写失败时正式 final 不存在；rename 成功后 problem_state 写失败时 final 已完整，重试只校验并恢复状态，不覆盖它。
- 既有 final 必须版本/证据/完整文件清单哈希与当前已验收来源一致；损坏已发布 Word 被严格拒绝，损坏内容不被覆盖。
- 相同源稿与证据的 PASS 渲染会复用；已验收 DOCX 损坏时拒绝，不偷偷重渲染。恢复测试确认版本与交付 Word 字节始终相同。
- `build_delivery` 新增仅发布器使用的 `published_destination` 关键字参数，使临时构建位置与正式 manifest 路径分离。

### 7. 摘要只强调已有结果

文件：`paper.py`、`paper_semantics.py`、`test_paper_writer.py`、`test_paper_semantics.py`。

- RED：摘要只有虚构固定方法名“参数反演”被加粗，已有 10.2 um / 0.8% 未被强调；整段 Strong 被接受。
- GREEN：仅对原摘要已存在的数值与受支持单位/百分数加粗，不补方法名称；没有合适匹配就保留原文。关键词也不再固定插入“参数反演”。
- 测试检查实际 Pandoc Strong 中存在 `10.2 um` 与 `0.8%`，并拒绝摘要整段加粗。

### 8. 正文标题编号从 1 开始

文件：`docx_styles.py`、`test_docx_styles.py`。

- RED：正文标题没有独立 numPr，继承了模板示例历史值；首次二级编号显示 1.2 的根因得到定位。
- GREEN：保留原始 abstractNum，全新正文共享编号实例按每个使用级别显式增加 startOverride=1，正文段落绑定该实例。
- OOXML 测试覆盖第一章、首个二级、首个三级、第二章、第二章首个二级，逐项检查 ilvl、startOverride=1 和共享新实例；原模板字节与 abstractNum 定义保留测试继续通过。

## 接口 / 配置注意

- `prepare_paper_writing` 返回 evidence 已改为当前版本的 evidence_pack.json。
- Writer 指令同步为版本快照入口，明确不能改 evidence_pack/support_dependencies/support_inputs。
- 直接 build_delivery 的调用者必须提供同版 evidence_pack、writer_manifest、publication_manifest、support_dependencies 和带实际产物哈希的 PASS render_report，不能再用任意字节 + 简单 PASS fixture。
- `paper/final/交付` 替代旧的 `paper/交付`。原先没有生产交付，不做迁移。
- 不重写旧论文/旧证据来满足新门禁；真实摘要变化仍待用户授权复核。

## 主代理烟测入口

`tests/test_paper_rendering.py::_version(tmp_path)` 是最小合法合成渲染夹具：在传入的新独立目录下创建 paper_v001、白色测试图、Markdown、canonical evidence_pack、匹配 writer_manifest。可复用其构建逻辑，使用 `paper.render_paper(version_dir, {minimum_pdf_pages: 1})` 调用真实 Word 导出（不传测试 PDF exporter）；不会要求或修改真实问题状态。

已有复杂样例 `reports/paper-upgrade-smoke/paper.md` 如继续使用，需要在独立样例版本内补同结构快照：图条目的 path 与 Markdown 精确相同、sha256 为实际图字节；evidence_hash 用 `paper_integrity.evidence_digest` 计算；Writer manifest 使用同 hash。包含表格审计注释时应保留相应 evidence_id 登记。不要挪用/刷新真实论文 evidence 以通过样例。

完整交付测试夹具见 `tests/test_paper_delivery.py::setup`；它包含逐文件真实哈希与 DOCX ZIP，但 PDF/TEX 是隔离测试字节，**不能用于宣称真实排版验收**。真实 Word 排版验收仍需主代理另行执行。

## 剩余范围与风险

- 已完成的是静态依赖闭包与逐文件来源一致性，不是新环境完整数值复现；外部包依赖由已哈希 requirements 安装。动态导入/外部数据仍需实际入口说明和后续运行验证，不声称已运行完整模型。
- 失败留下的 `.final-pending-*` / `.delivery-pending-*` 被保留作检查，不会作为正式交付，也不会覆盖或递归删除用户目录；未来如清理须按明确路径另行授权。
- `render_report` 是受控本地流水线产物，不是数字签名防篡改系统；实现防止快照混用、文件变更和未绑定 PASS，不宣称抵御能同时重写所有受控状态/报告的攻击者。
- 全量 pytest、真实 Word 页面与样式实开复审待主代理。真实新论文仍因摘要证据变化待用户授权，不能自动发布。
