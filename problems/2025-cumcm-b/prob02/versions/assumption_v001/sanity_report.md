# Sanity Check Report

- problem_id: 2025-cumcm-b
- question_id: prob02
- assumption_version: assumption_v001
- formulation_version: formulation_v001
- overall: NEEDS_REVISION
- checked_at: 2026-08-30T00:33:45Z
- task_id: 0670bb687607edb7dd91
- action: inspect_compute_result（async computation 终态验收）

## Level 1：文件和运行完整性（PASS）

- 任务 `0670bb687607edb7dd91` status=succeeded、returncode=0、finished_at=2026-08-29T16:22:28Z；stdout/stderr 日志落盘完整。
- 追踪 hash 链独立复现：用 `automm.common.hash_path` 复算 `code_hash=36f9a654ee61c8bad1c1150732f12fcf0d01669799e786c2ed762f9692e84c12`、`source_config_hash=eadc8c57540e232cc64dd557c1fa2514a6ea27f3d0c77c38dffb632bda03dd13`、`input_hash=23b8d41f72d40ba12d10ac9c5d899a9acca886f203191833b191b60ee31b96e0`，与 task.json 及 implementation.md §7 完全一致。
- metadata.json 登记的 `input_parameters_yaml_hash=ea0976b4…`、`task_config_yaml_hash=2fb57993…` 为文件原始字节 SHA-256（`sha256_file`），与实测 `compute.py=EF08A427…`、`task_config.yaml=2FB57993…`、`parameters.yaml=EA0976B4…` 一致；与 task.json 使用不同的 hash 约定（`hash_path` 含相对路径前缀、`hash_json` 合并有效配置），分工明确、无矛盾。
- 输出齐全：result.json、solver_status.json、verification.json、metadata.json、preprocessing.json、dispersion_ref.json、reflectance_theta10.csv、reflectance_theta15.csv。

## Level 2：数值范围和约束（PASS_WITH_WARNING）

- 关键结果文件全部有限：result.json / solver_status.json / metadata.json / preprocessing.json / verification.json / reflectance_*.csv，无 NaN/Inf。
- 反射率能量守恒成立：正模型 R 与观测 R 均落在 [0,1]（R%/100 归一），无硬约束违反。
- 预处理正确：附件1 无异常点、附件2 262 个 R%>100 异常点按 (5.2) 降权 w=0.05（不修改原始数据，preprocessing.json 登记 SHA-256=2e67444b…）；Reststrahlen [700,1000] cm⁻¹ 各剔除 623 点（w=0）。
- 警示项：`dispersion_ref.json` 中 `n_sellmeier` 在 λ=17/20/25µm 处为 0.3999 / NaN / NaN——这是把 Sellmeier（L09，仅适用于 λ≤5µm）外推到超界谱段的自然结果，属模型适用范围标注，非计算输出。该文件为色散模型核验/对照用途，不进入厚度结果；但机器级 L2-finite 检查因其含 NaN 判为 NEEDS_REVISION。建议后续用 null / 单侧标记表示超界值，避免在结果目录留下 NaN。

## Level 3：量纲和公式（PASS）

- formula-代码逐条一致：(2.1) Snell、(2.2) 相位差、(2.3)/(2.4) 两光束正模型、(3.1)–(3.3) Fresnel、(3.9)/(3.10) 间隔-厚度、(3.11)–(3.13) 色散相位法、(4.1) Sellmeier、(4.2) 色散参考、(5.1)/(5.2) 加权全谱 NLS、(6.1)–(6.3) 极值/周期歧义、(7.1)–(7.6) 可靠性。
- 单位约定一致：t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[deg]（内部转 rad）、δ[rad]、R 无量纲（R%/100）；(2.2) 的 1e-4 换算因子正确。与全局符号表及 parameters.yaml 无冲突。
- P1（仅 t）与 P2（联合 t,n_sub）目标函数 (5.1) 实现正确；多初值（网格扫描 + 相位法 + ±0.96µm 周期布点）消除厚度周期歧义。

## Level 4：常识与文献合理性（PASS_WITH_WARNING）

- 物理量合理：t≈2.17µm（P1）-2.42µm（P2）为 SiC 外延层厚度同量级；P2 反演 n_sub≈2.53 与重掺 SiC 衬底折射率量级相符；色散 n 由 5µm 的 2.495 升至 17µm 的 3.524（趋向 Reststrahlen 吸收带）方向正确；Reststrahlen 剔除、>100% 异常点降权策略均合理。
- 三方法体系一致：M1 色散化全谱 NLS（主）、M2 色散相位法、M3 常数 n 基线，交叉验证结构正确。
- **重大警示（决定整体结论）**：可靠性分析已把本问两大已知不确定度来源量化，且均远超阈值——色散模型选择 Δt_disp=37.4%（N-const 2.966 vs N-L26 2.170 vs N-scaled 2.154，τ=2%）与 n_sub ±20% 扰动 Δt_nsub=69.0%（+7.44% / −69.01%，τ=0.5%）。这正是 formulation/assumption 已登记的 B6（λ>5µm 5–17µm 数据缺口）与 B7（n_sub 数值未定/可辨识性弱）技术债；bootstrap 残差再拟合残差 RMSE≈0.046（约 4.6% 反射率）表明两光束+色散代理模型残差偏大。

## Level 5：跨小问一致性（pending）

- 触发条件（所有小问局部完成）未满足，留 prob02/prob03 完成后执行；本问单位/符号与全局约定、prob01-conclusion-v1 依赖一致。

## Level 6：鲁棒性和敏感性（本次即计算阶段可靠性，未通过）

- 本问的六项可靠性判据 (§7.1-§7.6) 已在 computation 阶段执行，其结果即敏感性/鲁棒性诊断：
  - reliability_two_angle：FAIL（eps12=6.56% > τ=2%）
  - reliability_dispersion：FAIL（37.41% > τ=2%）
  - reliability_nsub：FAIL（69.01% > τ=0.5%）
  - reliability_ci：FAIL（CI 半宽 3.51% > τ=2%）
  - reliability_anomaly：PASS（0.91% < τ=1%）
  - multibeam_diagnostic：无显著改善（0.14% < 10%），**不需要**多光束修正（B13 PASS）
- `feasible_incumbent = false`（5 项判据中仅 anomaly 通过）；这不是实现错误，而是模型在当前假设下无法给出满足可靠性阈值、可复现的厚度结果。

## 路由

- overall: NEEDS_REVISION
- failure_type: quality_warning
- return_to_stage: mathematical_formulation
- blocking_reasons: []
- 核心原因：无可行 incumbent（feasible_incumbent=false），色散模型选择（37.4%）与 n_sub（69.0%）对厚度的敏感性远超预注册阈值（2% / 0.5%），且两入射角厚度不一致（6.56%）、bootstrap CI 偏宽（3.51%）。须在 formulation 阶段修正模型（如：将反演谱段截断至 ν≥2000 cm⁻¹ 色散已知区、改进/拟合适配色散模型、固定 n_sub 或重构可辨识性结构、评估多光束修正），并配套 assumption/literature 支持（L26 全文 n/k 表、n_sub 文献取值）。代码/实现层面无硬失败，异常点处理与多光束诊断通过。
- warnings:
  - dispersion_ref.json 含 Sellmeier 超界 NaN 值（自动 L2 标记），建议用 null 标记。
  - λ>5µm 色散为厚度反演最大不确定度来源（B6，37.4% 敏感性）；n_sub 数值未定且敏感性 69.0%（B7）；两光束+色散代理模型残差 RMSE≈0.046（约 4.6% 反射率）；以上均留 formulation 修订并量化。
  - 本次为 sanity 验收结论，未改动 computation 结果、formulation/assumption 历史文件。
