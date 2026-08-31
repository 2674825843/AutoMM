# 论文升级集中审查修复

本轮仅修复已审查问题及直接相关回归。不得改原模板、实际证据/数据、正式论文或状态，不运行模型，不commit/派子代理。逐项TDD，报告到publication-fix-report.md。最终计划见用户会话批准边界：原生styles、独立图表题注、无公开内部信息、完整支撑材料、故障不发布、证据绑定且用户授权才重写。

## 已确认审查发现及修复裁定

1. paper_semantics 图片可混在Para正文，转换后无声丢弃文字。先测试 `Before ![Result](plot.png) after with warning.`，必须issues非空。仅支持单独Image加空白/审计comment的段落，其余拒绝；别静默删字。嵌套BlockQuote/List中的Figure/Table目前未登记；本轮明确拒绝这些不支持的图表布局，别输出无题注表。不改正常列表/表格内公式。

2. 公开门禁不足。补测并拦截 `L5 passed, implementation section 6.1, quality_status=passed.`、`reports/problems/demo/task_123/metadata.json`、Windows项目绝对路径、ev_/warn_/task内部标识；避免误报正常数学L5符号或合法参考链接。增加 `audit_public_docx(docx_path)->dict`，只读ZIP检查所有word XML的w:t、字段显示、图片docPr name/descr/title、批注、页眉页脚中的公开内容；不对资源关系路径/数学下划线一刀切。render_paper在Word导出前调用且报告结果，问题严格失败。新测试可用最小docx修改副本插入泄漏，以真实审计拒绝。

3. request_paper_rewrite丢弃授权证据hash，准备新版本时重抓可接受变化。将已核验hash留为rewrite_evidence_hash；prepare_paper_writing从当前paper读取expected hash（重写hash或内容修订已有evidence_hash），build_evidence_pack(persist=False)先比较，成功才持久化与创建新版本。测试授权后证据变化，准备失败且不创建版本、不覆盖shared evidence。

4. runner validate_and_render_paper读取共享evidence，render优先版本evidence，交付又共享。统一以活动版本不可变 evidence_pack.json为事实入口；核对 paper.evidence_hash、writer_manifest.evidence_hash 与快照hash，必要验证快照canonical实际内容hash。旧测试fixture补齐真实快照与manifest，不用mock掩盖。render_report记录source_sha256/docx/pdf/tex哈希与evidence_hash；build_delivery必须核对PASS报告与DOCX哈希，以及同一快照和publication manifest，不接受任意Word字节配假PASS。测试cross snapshot/改动Word拒绝。

5. 支撑代码缺本地依赖，requirements直接拿当前未哈希版本。准备版本时新增 support_dependencies.json 固定代码依赖快照：从evidence中的代码.py静态分析本地imports，递归解析ROOT/scripts模块（含automm/__init__.py，common.py，visualization.py及其实际本地导入）及相对模块，保留ROOT相对目录；包含requirements.txt hash。只取明确本地Python文件，拒绝越界，不复制凭据/整个仓库/运行状态。交付按这份hash白名单复制到代码/<原路径>，无法解析必须存在的本地模块则失败或明确登记缺项，不能称完整。prepare与直接build_delivery测试应提供此快照；修改requirements或依赖后打包失败。必要已验收生成结果/配置若作为绘图输入，应在运行说明明确位置与准备方式，不私自复制原始授权未明数据。

6. 发布分两步导致半成品final和永久拒绝。裁定采用单目录原子发布：先在paper内创建唯一临时final目录，完整复制内部论文产物/报告并在其中构建“交付”（含论文.docx和支撑材料）；所有文件、hash、manifest完成后，单次rename到paper/final。对外入口改为 paper/final/交付（此前paper/交付尚无生产交付，不需迁移）。manifest中的delivery路径写最终路径，不留临时路径；版本侧delivery_manifest同步记录最终路径。既有final只允许相同版本且完整hash匹配后恢复状态，不重拷贝/覆盖。模拟copy中断、manifest写失败、rename成功后state写失败，重试均不永久卡住，第一次失败不得留下半成品正式final。

若已经有PASS渲染且Markdown/evidence哈希没变，重试复用已验收产物，不重新渲染导致DOCX随机元数据hash变化；产物hash不符严格失败，不偷偷重生成。

7. 摘要确定性生成硬加“参数反演”可能无来源。改为仅强调摘要中已经有证据的结果数值+单位/百分数，不引入方法名；没有合适强调内容可保留原文交Writer补充，不能发明术语。补测试关键结果确实Strong且整段粗体被拦截/反馈，不仅断言有**。

## 当前检查情况

8. 实际Word两页样例的首个二级章节显示“1.2 检查层级”，而其前面没有二级章节，应为1.1。请查模板多级编号start设置/旧counter继承，保留abstract定义但为新正文编号实例的各使用级别显式startOverride=1；避免套用模板示例的历史起始值。覆盖一级标题后首个二级、第三层首个子节、二章首个子节的实际或OOXML验证。

- 基线107 passed；新增后142 passed唯一schema const未声明type已修复并专项通过。
- 图表语义9、校验/草稿14、交付4、重写2、workflow5已有测试，集成与独立style21通过。
- 原生模板样式模块由上一代理完成，不需要全盘重写，根本功能有实际Word两页烟测：标题/摘要/图1/表1显示正确。
- 当前真实证据hash变化仅3个question_summary.md，用户是否授权复核新摘要尚未回复。不得为完成任务绕过它；本轮测试仅隔离样例。
- 要保留根目录其他用户未提交改动。所需模块均为本轮修改，git基线c8f7a4af095f05901ad5044607a2b68aee361f2b。

## 报告

逐项给出RED/GREEN证据、文件、接口变更、剩余风险，末尾一次全量pytest。若需更大设计变化先消息告知主代理。主代理同期只做样例视觉验收/证据只读核对，不编辑你接手文件。
