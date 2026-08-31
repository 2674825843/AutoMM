# Sanity Check Report（prob03 主 computation 验收 · formulation_v002）

- 自动检查状态：PASS_WITH_WARNING
- 检查时间：2026-08-30T08:09:14.109367+00:00
- 任务 ID：`7e209043973692d067ed`（formulation_v002 / assumption_v001）
- 验收 Agent：sanity-checker
- **最终判定：PASS_WITH_WARNING**

> v001 判定为 NEEDS_REVISION 的两项 core 发现（R1/R2）在 v002 已修复并复核通过；本版为可行、可追踪结果，予以推进。v001 的计算与 sanity 结论作为历史保留在 workflow_state 警告与 formulation_v002 修订日志，不作为被覆盖的有效结果。

## Level 1：文件和运行完整性

- 任务 `7e209043973692d067ed` **succeeded**，`returncode=0`，`finished_at=2026-08-30T07:54:58Z`，`feasible_incumbent=true`；stdout/stderr 落盘，无非零退出。
- 输出齐全：`result.json` / `solver_status.json` / `verification.json` / `metadata.json` / `preprocessing.json` / `dispersion_ref.json` / `mb_conditions.json` / `reflectance_theta10.csv` / `reflectance_theta15.csv`。
- **追踪链复算一致**：`code_hash=482f5abb10c276c9d073dd7b7177ce342cf0a0d2d0b455370a899ec566142873`（compute.py）、`config_hash=8cbd2e89a4c7bafa3f2264aecd52c311998332c4a85051c56fb54327e92aa676`、`source_config_hash=1b44bfb13cdb4cbb6ed75ea19de0915238d7f14cf57751c3afb1bf05ca8bbbd2`（task_config.yaml）、`input_hash=bff09b1f0d37e5c9acdb18d4432266277115c10db400116fc2fb9c62c9cc78f7`（formulation_v002/parameters.yaml），与 `task.json` 及 `implementation.md §7` 完全一致。
- 原始附件只读（`preprocessing.json` 登记逐文件 SHA-256），无就地覆盖。

### 【数据契约·需人工确认】附件2 SHA-256/大小与 README 不符

- 磁盘实测：`附件2.xlsx` **SHA-256=2E67444B61B90826C1FFE043FB0F3E7D3470FAC9A005F8842F231EF3D64B34D1**、大小 **780,181 B**；而 `data/2025_cumcm_B/README.md` 记录 **24B3113E80D5EC5458BA4F447DF9ED185578481E8B0081BDF0673689505E49D0**、大小 **186,957 B**。
- 附件1/3/4 的 SHA-256 与大小均与 README 完全一致，仅附件2 不一致。
- **受影响范围**：附件2 = SiC 15°实测数据，仅用于 prob03 Q3 的 **SiC 多光束只读量级复核**（Rbar≈0.0024），**不进入硅厚度主反演**（Q2 用附件3/4，二者与 README 一致）。
- **性质判定**：该文件（hash `2e67444b`）自 prob02 起即被全流程使用并接受（prob02 sanity_report 已登记同一 hash 与其 R%>100 异常点=262），属**既有、全流程共用的数据契约偏差**，非 prob03 引入；最可能是 README@附件2 条目错误（下载版本与 README 记录不一致），而非 prob03 数据被篡改。
- **路由建议**：按 `implementation.md §7.1`「附件缺失或 SHA-256 与 README 不符 → `input_missing`」，建议由数据所有者/资源管理确认附件2 的真实来源 hash 与 README 条目后更正 README；**不作为 prob03 结果否决依据**（主结果安全、附件3/4 契约完好）。

## Level 2：数值范围和有限性

- `machine_sanity.json`：9 个数值文件**全部有限，无 NaN/Inf，`failures=[]`**。
- 模型特有约束：硅主反演带 `ν∈[2000,4000] cm⁻¹`，`t̂=3.4477 µm ∈ [2,12] µm` 扫描区间；反射率 `R∈[0,1]`；多声子带 `[400,1600]` 剔除、SiC Reststrahlen `[700,1000]` 剔除（`n_points_inv_band_si_all_angles=8296`）；附件2 的 262 个 `R%>100` 异常点按 `weight_anomaly=0.05` 降权（不修改原始数据）。无硬约束违反。

## Level 3：量纲、公式与实现一致性

- 单位约定一致（`metadata.json unit_conventions`）：t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[°] 内转 rad、δ[rad]、g[cm⁻¹]、R 无量纲、R̄ 无量纲。
- **R1（硅厚度基准，v001 伪影已修复）**：主反演（baseline-干涉分解 + 一维相位频率扫描 variable projection，两角共享 t）忠实实现 (2.7)/(6.1)-(6.5)。sanity-checker 独立核验 `solver_status.json` 的 J(t) 曲线：**全局唯一极小在 `t=3.45 µm（J_shared=0.0608，RMSE≈2.7e-3）`**，`t≈6.9 µm` 处 `J≈1.19（RMSE≈1.19e-2，高约 20×）` 为倍周期假极小；v001 的“因子 2 / RMSE-标签互换”伪影已消除。结果 `t̂=3.4477 µm` 与 formulation_v002（R1）一致。
- **R2（精细度公式，v001 漏 √R̄ 已修复）**：`model.py` `interface_reflectivity_product`/`necessary_conditions` 两处均改为 `finesse=π·√R̄/(1−R̄)`；`result.json` N1 报告 `finesse=0.3186`，与 (4.2) 公式对同一 `R̄≈0.0101` 的 `F≈0.319` 一致（不再是 v001 的 0.032），公式-代码一致性恢复。
- 无 formulation 与实现相抵触项。

## Level 4：物理、文献与常识合理性

- **硅厚度** `t̂=3.4477 µm`（共享）/3.4507/3.4463 µm（每角），为该外延层合理量级，且与干涉条纹计数（带内约 4–5 同型极大）、Δν≈423 cm⁻¹ 估计一致；硅 Sellmeier（L12/L13）在主反演带 `[2000,4000]`（λ∈[2.5,5]µm）全程有效，**无 λ>5µm 色散缺口**（区别于 SiC B6）。
- **多光束判定（硅）**：N1 `R̄=√(R₀₁R₁₂)≈0.0101 ≤ θ_mb=0.05`（F≈0.319，正确公式）；N2 相干长度≈1.04e4 µm ≫ 单程 OPD≈23.6 µm（m_max^coh≈439）；N3 平行度 α≈0.0033°（不作硬门禁）；N4 硅透明窗 k≈0。**实际 Airy vs 两光束残差改善率 η_mb≈0.11% ≪ τ_mb=10%** → **两光束适用（two_beam_negligible）**。
- **SiC 重新判定（Q3）**：在 prob02 的 `t̂=7.2158 µm` 处只读量级复核，`R̄_max≈0.00240 ≤ θ_mb=0.05` → **无显著多光束、无需修正（no_correction_needed）**，与 prob02 结论（prob02-conclusion-v1）一致。
- **物理常识**：`t` 由干涉相位频率唯一确定、与 `n_sub` 结构解耦（`main_t_decoupled=true`）；色散为不确定度来源但带内 `Δt_disp=0.503%≤τ=2%`；`n̂_sub≈3.558` 为干涉幅值弱可辨识值；异常点降权「无影响」（硅无 R%>100 异常）；轮廓似然 CI 半宽 `0.134%≤τ=2%`。

## Level 5：跨小问一致性

- 触发条件（所有小问 locally completed）未完全满足：prob03 稳健性/消融与最终留待后续，保持 pending。
- 部分核对：硅（t̂=3.4477 µm）与 SiC（t̂=7.2158 µm，prob02）为不同材料、厚度各异，无冲突；SiC 多光束重新判定（no_correction_needed）与 prob02 维持一致；全局符号/单位一致。

## Level 6：robustness/ablation

- 本版主反演已内嵌 `§7` 预注册可靠性判据（两角一致性/色散/CI/异常点/多光束/SiC），`verification.json` 7/7 通过、`checks_failed=[]`。
- 独立 robustness/ablation 阶段尚待编排；Level 6 于其后再验收。**本响应不发起新计算。**

## 路由

- **判定：PASS_WITH_WARNING**
- 原因：硬门禁（formulation-实现一致、数值有限、单位/量纲、物理常识、跨问一致）全部通过；v001 的 NEEDS_REVISION 两项已修复；无硬失败、无 VERSION_REJECTED、无 NEEDS_REVISION。存在**技术债**（非阻断）：bootstrap CI 未跑（用轮廓似然，半宽 0.134%≪2%）；`n_sub` 为幅值弱可辨识值（B7）；M2/M3（离散相位/间隔法）方法债仅作对照；λ>5µm SiC 色散缺口（B6，主反演不入）；L43–L47 等关键来源全文待复核；**附件2 SHA-256/大小与 README 不符（数据契约，建议按 input_missing 由数据所有者确认）**。
- **failure_type**：无（未触发硬失败）；`quality_warning` 用于登记非关键技术债。
- **return_to_stage**：推进至 prob03 robustness/ablation（Level 6）与后续跨问（Level 5）/结论/论文；附件2 数据契约偏差建议由资源/数据所有者确认（input_missing）。
- 机器报告：`problems/2025-cumcm-b/prob03/versions/assumption_v001/results/silicon_mb_verify/machine_sanity.json`
- 说明：v001（任务 `f1c4e3ed425ff6b0e73f`）的计算与 sanity 结论保存在 workflow_state 警告与 formulation_v002 修订日志（R1/R2）中；v002 复用输出目录 `results/silicon_mb_verify`，写入同名结果文件，属已登记的目录复用（quality_warning），v001 的关键发现未丢失。
