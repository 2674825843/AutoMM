# Sanity Check Report

- problem_id: 2025-cumcm-b
- question_id: prob01
- assumption_version: assumption_v001
- formulation_version: formulation_v001
- overall: PASS_WITH_WARNING
- checked_at: 2026-08-29T06:18:32+00:00
- 检查范围：computation 阶段结果验收（Level 1–4；Level 5/6 按触发条件留待后续阶段）
- 任务：`0ea4b29da19e8479a6ea`（prob01-synthetic-verification，supervised worker，returncode=0，feasible_incumbent=true）

## Level 1：文件和运行完整性 — PASS

- task 追踪：`runtime/tasks/0ea4b29da19e8479a6ea/` 下 task.json、status.json、attempt-001-status.json、attempt-001-stdout.log、attempt-001-stderr.log、worker_started.json 齐全；status=succeeded、returncode=0、stderr 为空、stdout 输出“合成验证 通过：19/19 检查通过”。
- hash 一致性（复现验证，全部一致）：
  - `code_hash` = `d22acb3f3c95eb64c6f9b58e5c67d265eda6af1f69d03c3a9940073ff39cca01`（hash_path(compute.py)，与 task.json 及 implementation.md §7 一致）；
  - `source_config_hash` = `fea85c71160c3ec06ee5be1780ce4e6ab0a7a45704e3da30da62ba4a0e0df26b`（hash_path(task_config.yaml)，一致）；
  - `input_hash` = `ae4931470efcd30efa95ce7cf677890005d8dd4422f13aced03b6a81af6e48f8`（hash_path(parameters.yaml)，一致）；
  - `config_hash` = `eac5599ff69aadde7f00…`（hash_json(merged_config)，前缀与 implementation.md §7 登记一致）；
  - metadata.json 原始文件 SHA256：input_parameters_yaml_hash=`1f74e51c…`、task_config_yaml_hash=`4f97e8eb…`，与文件实测一致（注：metadata 用原始字节 sha256，task 用 hash_path/hash_json，两套均为项目约定）。
- 输出完整性：task_spec `expected_outputs` 6 项（result.json、solver_status.json、verification.json、metadata.json、synthetic_spectrum_theta10.csv、synthetic_spectrum_theta15.csv）全部存在于 `results/synthetic_verify/`，与 task.json output_directory 一致；output 目录位于 assumption 版本目录内。
- 自动化检查：`scripts/run_sanity_check.py`（task-id=0ea4b29da19e8479a6ea）输出 machine_sanity.json：failures=0，task_status=succeeded，automated_status=PASS_WITH_WARNING。

## Level 2：数值范围和约束 — PASS

- 全部数值文件有限：无 NaN/Inf（machine_sanity.json 对 5 个数值文件均 finite=true）。
- 正模型物理边界：R_clean ∈ [0.124494, 0.252852]（θ=10°）、[0.124581, 0.252889]（θ=15°），满足 0 ≤ R ≤ 1（能量守恒，formula_validation §4）。
- 极值定位：θ=10°/15° 均定位 11 个同型极值，间隔 Δν_obs=188.0 cm⁻¹，无异常极值。
- 求解器：scipy.optimize.least_squares 全部收敛，best status=1（gtol 终止），cost=0、rmse=0、max_residual=0；多初值 starts 各态记录完整（status/cost/nfev/message），best 选择与 rmse 排序一致。
- 反演结果：t_NLS(10°)=t_NLS(15°)=10.000000 µm（vs t_true=10.0），两入射角 rel 差 = 0（< 2% 容差）；t_phase(10°)=10.002189、t_phase(15°)=9.999529，rel<2.2e-04（< 1% 容差）；方法 A 基线 t_A≈10.44/10.47（rel≈4.4–4.7%，在 10% 基线容差内，A3 文档化色散偏差）。
- 硬约束：厚度为正、间隔为正、相位函数单调（g_monotonic=true）。

## Level 3：量纲和公式 — PASS

- 公式-代码逐条核对（implementation.md §3 映射表 ↔ model.py）：
  - (2.2) Snell：`theta_prime`/`cos_theta_prime` 一致；
  - (2.6) 光程差 Δ=2t√(n²−sin²θ)：`optical_path_difference` 一致；(2.5)=(2.6) 等价性经探针数值验证；
  - (2.8) 相位差 δ=4π×1e-4·n·t[µm]·ν[cm⁻¹]·cosθ′：`phase_delta` 逐项一致（1e-4 为 µm/cm 与 cm⁻¹ 归一，单位换算复核正确）；
  - (3.1)–(3.3) Fresnel s/p 强度反射率：`fresnel_interface`/`interface_reflectivities` 与公式逐项一致；
  - (3.5)/(3.6) 两光束反射率 R=R1+(1−R1)²R2+2(1−R1)√(R1R2)cosδ：`forward_reflectance` 一致（s/p 平均）；
  - (3.8)/(3.10) 间隔与厚度：`evaluate_spacing_theory`/`thickness_from_delta_nu` 一致（Δν=1e4/(2nt cosθ′)，t=1e4/(2n cosθ′Δν)）；
  - (3.11)–(3.13) 色散化相位法：`phase_function`（g=n·ν·cosθ′）与 `thickness_from_phase_gap`（t=1e4/(2Δg)）一致；Δg_theory=1/(2×1e-4×t)=500 cm⁻¹（t=10）与观测 499.89/500.02 一致；
  - (4.1) 4H-SiC Sellmeier：`sellmeier_n4hsi` 与参数登记 formula 一致。
- 单位约定：t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[deg]（三角转 rad）、Δν[cm⁻¹]、δ[rad]，在 code/parameters.yaml/metadata.json 三处一致。
- 符号：t、n、n_sub、n_air、theta、theta_prime、nu、lambda、delta、m、delta_nu 与全局符号表一致，无同名异义（R1/R2/θ″/g 为局部中间量，不入全局表）。

## Level 4：常识与文献合理性 — PASS

- 物理常识：SiC（n≈2.5）表面 Fresnel 反射率与合成谱包络 [0.124, 0.253] 同量级；重掺衬底 n_sub=3.0 为合成验证场景值（A6，prob02 反演/文献确定）；干涉条纹随波数周期振荡、极值条件 δ=mπ 与 (3.7) 一致。
- 色散：4H-SiC Sellmeier (4.1) 系数（n²=6.79485+0.15558/(λ²−0.03535)−0.02296λ²，L09 经 L11 交叉核验）为文献登记值；n(5µm)≈2.495 探针通过；弱色散谱段 n_eff≈2.554 合理。
- 边界行为：方法 A 在 2000–4000 cm⁻¹ 的约 4% 系统偏差与 A3 预期偏差方向一致（色散显著，ν·dn/dν≈9%），作为基线/初值并文档化；相位法与 NLS 无此偏差。
- 谱段边界：Reststrahlen 区 [700, 1000] cm⁻¹（A7）已排除在方法 A/B 谱段之外，与 SiC 物理一致。
- 关键假设来源：A1–A7 均有文献/常识来源登记；L01–L05、L23 仍为题名/摘要级核验（正文全文未获取），属既有 workflow warning，不阻断本问合成验证结论，定量复核留 prob02。
- 合成验证定位正确：prob01 无实测数据，本任务为正模型自洽数值验证（不产出实测厚度结论），notes 中已明确。

## Level 5：跨小问一致性 — PENDING

- 触发条件为所有小问 locally completed（prob02/prob03 未完成），本阶段不执行；已核对 prob01 结果中的单位、符号与 problem_understanding/global_symbols 一致，作为 prob02 反演流水线的复用基础（峰谷定位、相位法、NLS 多初值）。

## Level 6：鲁棒性和敏感性 — NOT_APPLICABLE（记录理由）

- prob01 为纯解析建模+合成自洽验证，无实测数据可做数据级鲁棒性；噪声鲁棒性（noise_sigma_percent=0）与色散策略敏感性属于 prob02（实测数据反演）与 robustness 阶段范畴，本阶段跳过并记录理由。

## 路由

- overall: PASS_WITH_WARNING
- failure_type: null
- return_to_stage: null（无需返工；Runner 确定性迁移 computation → sanity_check）
- blocking_reasons: []
- warnings（技术债，全部已登记于 workflow_state，留 prob02）：
  1. λ>5 µm 色散延伸采用 constant（n(boundary) 常数延续），prob02 需数据反演/分谱段确定并量化对 t 的影响；
  2. 方法 A 常数 n 近似在 2000–4000 cm⁻¹ 引入约 4.2–4.7% 偏差（A3 文档化），仅作基线/初值；
  3. L01–L05、L23 为题名/摘要级核验，全文未获取，定量主张需在 prob02 对照原文/教科书复核；
  4. n_sub=3.0 为合成场景值，prob02 需反演/文献取值并做灵敏度分析；
  5. Reststrahlen 区 [700, 1000] cm⁻¹ 剔除策略由 prob02 预处理落实。
- 机器可读汇总：`results/synthetic_verify/machine_sanity.json`
