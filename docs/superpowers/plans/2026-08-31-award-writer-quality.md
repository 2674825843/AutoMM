# 获奖论文写作质量升级实施记录

## 约束
- 用户批准的计划：范文全量清点、至少12篇分层精读，规则库；语义写作提纲、证据取舍、独立审阅、最多3轮修订；仅影响未来论文。
- v007、paper/final、原始Word模板保持字节不变；不重写当前题目，不重算研究，不改范文原件。
- 初稿→审阅→有限修订→既有渲染和原子交付；所有新版本绑定规则、证据、草稿哈希，旧版本兼容。
- 不提交或覆盖既有未提交改动。当前分支 codex/paper-writer-agent，基线HEAD 70f939d59362aff25400b0ac7d305f426f7c39f0。

## 任务
1. 基线/保护：35项既有论文测试通过；127个保护文件见 reports/award-writer-upgrade/protected-baseline.json。原PID40184不存活，已用apply_control(PAUSE)暂停。
2. 范文分析：独立分析agent清点源目录并精读12篇以上，输出临时报告；主agent审核并集成。
3. 运行实现：按 runtime-brief.md 测试先行，实现语义计划/材料筛选/审阅/有限恢复及发布约束。
4. 复核：独立审查新增差异，修复后隔离样稿、全量回归、源文件hash核验；恢复原控制状态，不触发已完成题目重写。

## 决策和接口核对
|交界|产出/消费|处理|
|范文分析→运行写作|规则 JSON / frozen rule snapshot|只传规则、不传范文全文，sources只作出处|
|写作→审阅|plan + draft + evidence|三者绑定哈希，语义评审不能仅凭标记PASS|
|审阅→渲染发布|validated report|新版本必需，旧版本不追补|
|修订→准备下一版本|persistent revision lineage|上限3轮不能被prepare覆盖清零|

Ruling: 沿用当前已有功能分支、原位增量修改，不新建缺少既有未提交产物的worktree；隔离测试使用AUTOMM_ROOT。风险是改动混合，因此记录保护hash和每项修改清单，不做git批量提交/重置。
Ruling: 原daemon已退出；恢复先前running控制状态时重新启动单实例，核验只执行completed/idle，不重开题目。

## 进度
- Task 1: complete（35 passed；保护清单已保存；后台无活进程、控制paused）
- Task 2: in progress /root/award_corpus_analysis
- Task 3: pending
- Task 4: pending
