# Sanity Check Report

- problem_id: 2025-cumcm-b
- question_id: prob03
- assumption_version: assumption_v001
- formulation_version: formulation_v002
- overall: PASS_WITH_WARNING
- checked_at: 2026-08-30T20:37:39+08:00
- 检查对象：robustness_v001（formulation_v002 §8.5 预注册判据 R1–R8）+ 主 computation 结果（任务 `7e209043973692d067ed`，results/silicon_mb_verify）
- 复核 Agent：sanity-checker（独立于结果/鲁棒性生成 Agent）

> 本版为对 prob03 的**合并 sanity 复核**。Level 1–4 已由主 computation 验收记录为 PASS_WITH_WARNING（见
> `results/silicon_mb_verify/sanity_report.md` 与 workflow_state）；本次（同步动作）执行 **Level 6（robustness 验收）**，
> 并给出整体判定与路由。

## Level 1：文件和运行完整性

**PASS**（已由 computation 验收记录）

- 任务 `7e209043973692d067ed` **succeeded**（returncode=0，finished_at=2026-08-30T07:54:58Z）；输出齐全：
  `result.json`/`solver_status.json`/`verification.json`/`metadata.json`/`preprocessing.json`/`dispersion_ref.json`/`mb_conditions.json`/`reflectance_theta10.csv`/`reflectance_theta15.csv`。
- 追踪链复算一致：`code_hash=482f5abb…`（compute.py）`config_hash=8cbd2e89…` `source_config_hash=1b44bfb1…` `input_hash=bff09b1f…`，
  与 task.json/implementation.md §7 一致；原始附件只读。
- 数据契约：附件1/3/4 的 SHA-256 与 README 一致；仅**附件2（SiC 15°）SHA-256/大小与 README 不符**
  （磁盘 2E67444B…/780,181B vs README 24B3113E…/186,957B），属 prob02 起全流程共用偏差，仅用于 Q3 SiC 只读量级复核，
  **不进入硅厚度主反演**（Q2 用附件3/4，契约完好）——数据契约告警，不作结果否决依据。

## Level 2：数值范围和约束

**PASS**（已由 computation 验收记录 + robustness 只读探针复核）

- `machine_sanity.json`：10 个数值文件**全部有限、无 NaN/Inf、`failures=[]`**。
- 模型约束：硅主带 ν∈[2000,4000] cm⁻¹（透明窗，多声子带 [400,1600] 剔除）；t̂=3.4477 µm ∈ [2,12] µm 扫描区间；R∈[0,1]；
  R̄≥0；n_sub∈(1, n_epi) 物性边界。无硬约束违反。
- robustness R7 只读探针：各窗口 t、J_min、weighted_rmse、n_points、delta_t_percent 全部有限、合理（不修改原始数据/代码）。

## Level 3：量纲、公式与实现一致性

**PASS**（已由 computation 验收记录）

- 单位约定一致：t[µm]、ν[cm⁻¹]、λ[µm]=10⁴/ν、θ[°]→rad、δ[rad]、g[cm⁻¹]、R/R̄ 无量纲。
- R1（硅厚度基准）：主反演忠实实现 (2.7)/(6.1)-(6.5)，**全局唯一极小 t̂=3.4477 µm**（J_shared=0.0608，RMSE≈2.57e-3）；
  t≈6.9 µm 为倍周期假极小（RMSE≈1.11e-2，高约 4.3×），v001 的因子 2/RMSE-标签互换伪影已消除。
- R2（精细度公式）：`finesse=π·√R̄/(1−R̄)`（(4.2)），result.json N1 报告 finesse=0.3186 与公式一致，v001 漏 √R̄ 的 bug 已修复。
- formulation 与实现无相抵触项。

## Level 4：常识与文献合理性

**PASS**（已由 computation 验收记录 + 本次复核）

- 硅 t̂=3.4477 µm（共享）/3.4507、3.4463 µm（每角），与该外延层量级、带内约 4–5 同型极大、Δν≈423 cm⁻¹ 一致；硅 Sellmeier 在主带全程有效、**无 λ>5 µm 色散缺口**（区别于 SiC B6）。
- 多光束判定（硅）：N1 R̄≈0.0101≤θ_mb=0.05、F≈0.319；N2 m_max^coh≈439≥2；N3 α≈0.0033°；N4 硅透明窗 k≈0；
  η_mb≈0.11%≪τ_mb=10% → 两光束适用；SiC R̄≈0.0024 ≤0.05 → 无显著多光束、无需修正（prob02 t̂=7.2158 µm 维持）。
- n̂_sub≈3.558 为干涉幅值弱可辨识值（范围 3.5–3.7），与 t 解耦；L43–L47、硅 Sellmeier（L12/L13）为题名/摘要级核验
  （正文全文待复核）——登记警告，不阻断。

## Level 5：跨小问一致性

**pending**（未触发）

- 触发条件（全部小问 locally_completed）未完全达到：prob01/prob02 已 locally_completed，prob03 尚待
  ablation→locally_completed 后，由 cross_question_review 统一执行 Level 5。
- 本次仅做局部核对：硅（t̂=3.4477 µm）与 SiC（t̂=7.2158 µm）为不同材料、厚度各异，无冲突；SiC 多光束重新判定
  （no_correction_needed）与 prob02 维持一致；全局符号/单位一致；prob03 依赖 prob02-conclusion-v1（content_hash 27b0ce…），
  该基准未被改动（dependency_graph 已登记）。

## Level 6：鲁棒性和敏感性

**PASS_WITH_WARNING**（本次验收；对 robustness_v001 独立复核）

- **结论**：robustness **STABLE**。预注册判据 R1–R7 全部在阈值内通过；R8 唯一性为报告项（非硬门禁，
  由 §7.6 预注册判据确认全局唯一）。主结果 t̂(共享)=**3.4477 µm**、每角 3.4507/3.4463 µm（ε₁₂=0.130%）、n̂_sub=3.558。
- **判据对照（实测 vs 预注册阈值，来源 result.json + r7_window_sensitivity.json）**：

| 判据 | 对象 | 实测 | 阈值 | 判定 |
|---|---|---|---|---|
| R1 两角一致性 | F/p/ε₁₂ | F=0、p=1.0；ε₁₂=0.130% | ε₁₂≤2% | PASS |
| R2 色散模型 | Δt_disp（N-SE vs N-SE-δ±0.5%） | 0.503% | 2% | PASS |
| R3 噪声/CI | 95% CI 半宽（轮廓似然） | 0.134% | 2% | PASS |
| R4 异常点 | Δt_anom（剔除/保留/降权） | 0.0% | 1% | PASS |
| R5 多光束 | η_mb（Airy vs 两光束） | 0.111% | 10% | PASS（两光束适用） |
| R6 n_sub 解耦 | 主方法 t 对 n_sub | 0.0%（解耦；n̂_sub=3.558 弱可辨识） | 3% 诊断 | PASS |
| R7 谱段窗口 | Δt_win（[1600/1800/2200,4000]） | 0.749% | 2% | PASS（只读探针补登） |
| R8 唯一性 | 次小候选比值 | 1.020（接近 1） | 远离 1 越好 | REPORT（非硬门禁；§7.6 确认全局唯一） |

- **补充判据**：多光束必要条件 N1–N4 全部满足（R̄=0.01008≤0.05、m_max^coh=439≥2、α_bound≈0.0033°、k≈0）；
  SiC 重新判定 R̄_max=0.0024≤θ_mb=0.05 → no_correction_needed（prob02 t̂=7.2158 µm 维持）。
- **物理/常识一致性**：t 由相位频率确定、与 n_sub 结构解耦；色散为相对最敏感项但带内 0.503%<2%（硅无 λ>5µm 缺口）；
  噪声二阶小量（主拟合低残差 + CI 半宽 0.134%）；异常点降权无影响（硅无 R%>100）；多光束可忽略；两角一致（无 prob02 大样本显著性分离）。
- **结论分级**：全部定量判据受阈值内通过 → `stable`；附条件边界（n_sub 弱可辨识 B7、唯一性近简并 R8）为登记边界，
  不影响 t̂ 稳健性。

## 路由

- **overall：PASS_WITH_WARNING**（Level 1–4 与 Level 6 均通过，无硬失败、无 VERSION_REJECTED、无 NEEDS_REVISION）
- **failure_type：null**（未触发硬失败；非关键技术债以 quality_warning 登记）
- **return_to_stage：null**（无需回退修订）
- **blocking_reasons：[]**
- **recommended_next_stage：ablation**（Level 6 通过、robustness STABLE；ablation 为下一条件阶段，交由 ablation-analyst 判定适用性）
- **本次动作（复核确认）**：基于已有产物独立复核 robustness_v001 与 computation 结果（`results/silicon_mb_verify`，任务 `7e209043973692d067ed`），Level 6 结论 PASS_WITH_WARNING 维持；发出 `record_sanity(level_6, PASS_WITH_WARNING)` 与 `transition(ablation)`。未发起新计算、未改动 computation 结果与 formulation/assumption 历史文件（遵守「不覆盖结果历史」，manifest 状态通过命令更新）。
- **warnings（非阻断技术债）**：
  1. bootstrap CI（B≥200）未运行：R3 用轮廓似然/夹逼区间（J(t) 曲率），半宽 0.134%≪2%（方法债，留论文/后续补）。
  2. R7（窗口敏感性）由只读探针补登（`robustness/r7_window_sensitivity.json` + `code/robustness_probe.py`，复用已审定 model.py，不修改数据/代码）——降级审查模式，方法边界已注明。
  3. n_sub 弱可辨识（B7）：n̂_sub≈3.558 为幅值弱辨识值（范围 3.5–3.7），与 t 结构解耦、不影响 t̂；文献取值与掺杂机制（L12/L13、L45）待全文复核。
  4. R8 唯一性次小候选比值≈1.020 接近 1（弱色散下周期邻近候选接近简并）：由 §7.6 预注册判据（全局极小唯一+嵌套 F 检验）确认全局唯一，作为报告项而非硬门禁。
  5. multibeam_improvement 基线差异：η_mb 以物理两光束正模型（Fresnel 刚性 DC 基线，θ10 RMSE≈0.0294）为基准，与主方法 variable projection（多项式吸收基线，RMSE≈0.0026）基线不同，论文须说明。
  6. λ>5 µm（ν<2000 cm⁻¹）为 SiC 色散缺口（B6）：prob03 主反演不入（硅无此缺口），SiC 多光束判定用 prob02 对照（R̄≈0.0024），Δt_inv_band 由 prob02 承接（58.4% 作为截断合理性证据）；L26 全文 n/k 表待文献全文复核。
  7. L43–L47、硅 Sellmeier（L12/L13）为题名/摘要级核验（正文全文未获取），定量参数需论文/文献阶段对照原文复核。
  8. 附件2（SiC 15°）SHA-256/大小与 data/2025_cumcm_B/README.md 不符（数据契约偏差）：仅用于 Q3 SiC 只读量级复核、不进入硅主反演；建议由数据所有者确认后更正 README（input_missing），不作为结果否决依据。
  9. 两角一致性 F 检验 F=0、p=1.0 且 ss_shared==ss_indep（退化的显著性检验）：因两角 t 估计几乎重合（ε₁₂=0.130%）所致，实际一致性仍以 ε₁₂ 为报告项，不改变 R1 判定。
