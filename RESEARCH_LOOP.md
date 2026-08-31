# AutoMM 自动数学建模循环

## 目标

系统追求假设有效、模型完整、结果合理、实现可复现、图表统一和全链路可追溯，不以单一 leaderboard 分数替代数学判断。

## 主循环

Python 唤醒器启动 one-shot Runner。Runner 获取锁、轮询邮箱、对账 task 和状态、选择下一个动作，然后调用一个专职 Agent 或创建一个异步计算 task。命令响应通过 JSON schema 校验，并以事务方式提交；异常会释放锁并写入恢复记录。

## 恢复

Agent 超时只影响当前 action，保留日志和草稿并重试当前阶段；相同错误连续两次进入收敛模式。十次有实质进展的恢复后进入降级审查。只有输入缺失、凭据或远端不可用、必须人工选择、所有合法模型失败或 Harness 无法安全恢复时才允许人工阻塞。

## 结果门禁

有可行 incumbent 但未证明全局最优、`mip_gap` 缺失或附加实验不足，可以通过 `PASS_WITH_WARNING`，但必须保留求解器状态、约束残差、输入、配置、代码 hash 和随机种子。NaN/Inf、硬约束违反、单位维度错误、公式与代码不一致、数据被修改和追踪链缺失必须失败。

## 自动论文与归档

每个小问完成后发送通知。全部小问完成并通过跨问审查后，Runner 构建 Evidence Pack，Paper Writer 按竞赛论文结构生成 Markdown，再由确定性门禁检查证据、引用、图表、warning 和章节覆盖。通过后用 Pandoc 生成 DOCX/TEX，并由 Microsoft Word 从 DOCX 导出 PDF；四类正文产物和检查报告按 `paper_vNNN` 保留。

工作流为 `cross_question_review → paper_writing → paper_validation → completed`。内容失败回 `paper_writing` 创建新版本；渲染失败停留在 `paper_validation` 重试同一版本。只有 final DOCX/PDF/TEX 发布成功后才进入 completed，随后仍生成 `final_summary.md` 作为研究归档索引。

论文阶段新增原生模板样式、题注、公开内容和交付包门禁；对外只交付 Word 与支撑材料，PDF/TEX/Markdown 继续内部归档。交付先准备临时目录并检查来源哈希，再发布，失败不得进入 completed。重新写作只能由用户明确授权的受控命令启动，不自动重开已完成项目。
