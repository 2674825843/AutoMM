# AutoMM 项目指南

## 语言与角色边界

- Harness 文档、Agent、状态报告和控制文件使用简体中文；论文标题、方法名、公式、代码标识符和参考文献标题可保留原文。
- Orchestrator 只选择下一个动作、委派 Agent、校验响应并落盘状态，不替代专职 Agent 做研究判断。
- Agent 只能处理自己的阶段，不得直接编辑受保护的 workflow state 或 manifest 字段；状态变更必须通过 schema 白名单中的 `commands`。

## 单次唤醒

Python Runner 每次唤醒最多执行一个动作。它先获取锁、轮询邮箱、对账运行中的 task，再依据持久化状态选择动作。研究 Agent 同步返回结构化 JSON；计算由 `tasks.py` 创建隔离 task，交给 supervised worker 异步运行。

## 小问与版本

- 小问命名为 `prob01`、`prob02`……，主阶段顺序执行；同一小问内部候选实验可在配置并发上限内并行。
- 假设和 formulation 版本不可覆盖。代码可在当前版本内更新，但输出目录、task、日志和结论历史必须保留。
- 每个结论必须有 `conclusion_id`、`version`、`content_hash`，前序结论变化会令后续小问 stale 并重新审查。

## 失败和门禁

Harness invariant（非法迁移、事务不一致、schema/context 不匹配、task ID/hash/output 不一致）严格失败。Agent 超时、worker 中断、SMTP 失败、Python 或求解器异常、单次 infeasible 和非关键图表失败不能直接人工阻塞，按 `failure_class` 路由到重试、修订或降级审查。

允许人工阻塞的情况：题目或必要数据缺失；凭据无效或远端不可用；必须人工选择的互斥建模目标；所有合法模型版本均失败；Harness 历史状态无法安全恢复。

## 结果验收

`PASS_WITH_WARNING` 可接受有可行 incumbent 但未证明全局最优、`mip_gap` 缺失、达到时限、bootstrap/Monte Carlo 次数不足等技术债，前提是 solver 状态、约束残差和追踪链完整。NaN/Inf、硬约束违反、单位或维度错误、formulation 与实现不一致、原始数据被修改或追踪缺失必须失败。

## 自动论文

跨小问审查通过后，状态机依次进入 `paper_writing` 和 `paper_validation`。Runner 先构建带路径、版本和 SHA-256 的 Evidence Pack，再创建不可覆盖的 `paper_vNNN`；Paper Writer 只能读取该白名单，不得重新建模或计算。

主源是 Markdown，Pandoc 生成含可编辑 OMML 公式的 DOCX 和 TEX，Microsoft Word 从同一 DOCX 导出 PDF。内容、证据、引用、图表、warning 披露与渲染检查全部 PASS 后，版本才发布到 `reports/problems/<problem_id>/paper/final/` 并进入 `completed`。内容失败创建新版本；Word/Pandoc 故障保留当前 Markdown、DOCX、TEX 和日志后重试。

## 文件和依赖

项目内路径使用相对路径和 `pathlib`。Python 依赖写入 `scripts/requirements.txt`，仅安装到项目虚拟环境。论文阶段要求 Pandoc 和 Microsoft Word。运行前通过 `compileall`、Ruff、配置校验和故障注入测试。
