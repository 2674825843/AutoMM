# 2025-cumcm-b 最终研究摘要

- 生成时间：2026-08-30T17:24:28.067135+00:00
- 小问数量：3
- 跨小问审查：passed
- 本文件是研究结果归档，不是比赛论文。

## prob01

- 接受假设版本：`assumption_v001`
- 接受公式版本：`formulation_v001`
- L1-L4 sanity：PASS_WITH_WARNING
- L5 sanity：PASS
- 鲁棒性：{'decision': 'completed', 'reason': 'robustness 适用并已完成：formulation_v001 §5.2 将鲁棒性列为比较标准，A5/A6/A10 要求灵敏度分析，workflow warnings 需量化色散/n_sub/截断对厚度的影响。预注册方案 robustness_v001（核心结论+稳定性判据运行前固定，robustness/ 目录），隔离任务 554819114361017c5b70 执行 E1–E5（n_sub/θ ±5/±10/±20% 扰动、色散三模型、噪声 σ=0.5/1/2%×100 次×2 入射角、谱段截断 6 组），5/5 判据通过 conclusion=stable（E1 0.008%、E2 0.22%、E3 替代模型 0.96%、E4 CI 半宽<0.03% 且收敛率 100%、E5 0%）；发现噪声下极值定位初值失真并升级网格扫描初值（prob02 复用）；原始样本/汇总表/置信区间/敏感性图/稳定性结论已归档 robustness/ 与 results/robustness/，交 sanity-checker 执行 Level 6'}
- 消融：{'decision': 'completed', 'reason': 'ablation 适用并已完成：formulation_v001 (3.5) 正模型含可解释可分离的公式项（界面反射项/衬底往返项/干涉振荡项）与算法模块（NLS 多初值），REQUEST.md 要求复杂算法必要性证据，robustness 已覆盖输入/情景不确定性、ablation 补充模型组件必要性，二者互补。预注册方案 ablation_v001（核心结论+判据运行前固定，ablation/ 目录），隔离任务 5dcb72876c5fcb2c7e95 执行 F0+A1–A4（干涉项消融、衬底反射消融、偏振平均消融、多初值模块消融），5/5 判据通过 conclusion=components_confirmed（A1/A2 不可辨识=组件必要、A3 最大差 0.012%、A4 单初值 6.03% vs 多初值 ~0）；消融结论/汇总表/3 张消融图（自动质检+视觉复核 passed）已归档 ablation/、results/ablation/ 与 figures.yaml，prob01 全部阶段完成，进入 locally_completed'}

### 小问总结

# 小问总结

本问建立了考虑折射率色散与斜入射 Snell 几何的两光束 Fresnel 干涉模型，并推导同型相邻极值间隔与外延层厚度的关系。合成验证中，色散化相位法得到约 $10.002\,\mu\mathrm{m}$，全谱非线性最小二乘得到 $10.000\,\mu\mathrm{m}$，均恢复 $t_{\mathrm{true}}=10\,\mu\mathrm{m}$；常数折射率间隔法约有 4% 系统偏差，因此仅作初值或交叉校验。两入射角结果一致，E1–E5 稳健性判据和消融判据全部通过。结论仅适用于无显著吸收、界面近似平行且采用已登记色散模型的谱段；$\lambda>5\,\mu\mathrm{m}$ 色散延伸和 Reststrahlen 区处理仍作为边界条件保留。

### 任务追踪

- `0ea4b29da19e8479a6ea`：succeeded，阶段 `computation`
- `554819114361017c5b70`：succeeded，阶段 `robustness`
- `5dcb72876c5fcb2c7e95`：succeeded，阶段 `ablation`

### 图表索引

- `prob01_fig_reflectance_spectrum_1d4fb899d1`：两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_reflectance_spectrum_1d4fb899d1.png`
- `prob01_fig_dispersion_curve_d85564d2fc`：外延层 4H-SiC 折射率色散模型 n(ν)，`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_dispersion_curve_d85564d2fc.png`
- `prob01_fig_phase_function_gap_459c486470`：色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_phase_function_gap_459c486470.png`
- `prob01_fig_thickness_methods_compare_5eac465fc8`：三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_thickness_methods_compare_5eac465fc8.png`
- `prob01_fig_spacing_constant_n_bias_2245b6eda4`：方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_spacing_constant_n_bias_2245b6eda4.png`
- `prob01_fig_nls_multistart_e64919ab13`：全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_nls_multistart_e64919ab13.png`
- `prob01_fig_response_surface_d0691c5dd8`：两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_response_surface_d0691c5dd8.png`
- `prob01_fig_sensitivity_tornado_6983566848`：prob01 robustness 敏感性 tornado 汇总（E1–E5），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_sensitivity_tornado_6983566848.png`
- `prob01_fig_noise_robustness_ci_30d4fa737f`：E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_noise_robustness_ci_30d4fa737f.png`
- `prob01_fig_ablation_summary_ee3c34dcfa`：prob01 ablation 判据汇总（F0 + A1–A4），`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_summary_ee3c34dcfa.png`
- `prob01_fig_ablation_polarization_da59250d1b`：A3 偏振一致性：avg/s/p 反演厚度 vs t_true，`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_polarization_da59250d1b.png`
- `prob01_fig_ablation_init_strategy_7c59622d5a`：A4 初值策略对比：单初值局部极小 vs 多初值全局解，`problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_init_strategy_7c59622d5a.png`

## prob02

- 接受假设版本：`assumption_v001`
- 接受公式版本：`formulation_v003`
- L1-L4 sanity：PASS_WITH_WARNING
- L5 sanity：PASS
- 鲁棒性：{'decision': 'completed', 'reason': 'robustness 适用并完成：formulation_v003 §7.1–§7.6 预注册可靠性判据（阈值计算前登记于 parameters.yaml）已在 computation 阶段完整执行并归档于 results/thickness_inversion_v003/result.json——C2 色散 Δt_disp=0.507%≤2%、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）、C5 CI 半宽 0.091%≤2%、C7 异常点 0.0%≤1%、C8 多光束改善 0.0%≤10%（两光束适用）、C6 全局极小唯一 全部 PASS；仅 C1 两角嵌套 F 检验统计显著（F=5.25,p=0.022）但 ε₁₂=0.165%≪τ₁₂=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。结论=STABLE（t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588 弱可辨识）。判定与敏感性可视化图已归档 robustness/（decision/preregistration/experiment_matrix/conclusion）与 figures/，交 sanity-checker 执行 Level 6。'}
- 消融：{'decision': 'completed', 'reason': 'ablation 适用并完成：formulation_v003 主方法 M1（基线-干涉分解 + 一维相位-频率扫描，variable projection，N-SE，p=3/q=1，两角共享 t，t 与 n_sub 解耦）含可解释、可分离的公式项/算法模块，REQUEST.md 要求复杂算法必要性证据，robustness 已覆盖输入/情景不确定性、本阶段补充模型组件必要性，二者互补。预注册方案 ablation_v001（ablation/decision.md、preregistration.md、experiment_matrix.yaml，判据运行前固定），隔离任务 1d41cd2ff79a3ec91cbd 执行 F0+A1–A4（色散消融、基线多项式消融、相位-频率方法消融、两角共享-t 消融），全部判据符合预期 conclusion=components_confirmed：A1 Δt_disp=8.44%>1%（色散必要）、A2 Δt_base=5.55%>1% 且 RMSE 升 7.03×（基线-稳健分解必要）、A3 Δt_vp=5.44%>1%（相位-频率方法必要）、A4 每角 t̂≈共享 t̂ 且 ε12=0.165%≤2%（两角共享-t 良性一致约束，不扭曲 t̂）。消融结论/汇总表/3 张消融图（自动质检+视觉复核 passed）已归档 ablation/、results/ablation/ 与 figures.yaml；compution v003 的 t̂=7.2158 µm 仍为主交付，本阶段不改变已接受的 formulation_v003，未触发模型修订。Level 5 待全部小问局部完成后执行。'}

### 小问总结

# 小问总结

本问针对附件 1/2 的 SiC 实测反射率谱，采用“慢变基线—干涉项分解 + 一维相位频率变量投影”反演厚度，使厚度主要由条纹相位频率确定并与衬底折射率幅值弱可辨识性解耦。两角共享厚度为 $7.2158\,\mu\mathrm{m}$，10°/15° 分别为 $7.2214/7.2095\,\mu\mathrm{m}$，相对差 $0.165\%$；色散、置信区间、异常点、多光束与全局极小判据通过。两角嵌套 F 检验虽统计显著（$p=0.022$），但实际厚度差远低于 2% 阈值，按预注册规则解释为测量点差异或膜厚梯度，不触发模型修订。$\lambda>5\,\mu\mathrm{m}$ 色散缺口、$n_{\mathrm{sub}}$ 弱可辨识及物理 NLS 约 5.5% 交叉校验偏差作为推广限制保留。

### 任务追踪

- `0670bb687607edb7dd91`：succeeded，阶段 `computation`
- `1295103e6926a59e5ed2`：succeeded，阶段 `computation`
- `1d41cd2ff79a3ec91cbd`：succeeded，阶段 `ablation`
- `30bedd3be5a2c9a36d3a`：succeeded，阶段 `computation`
- `e4a68a3fb8cbbfc02fe1`：timed_out，阶段 `computation`

### 图表索引

- `prob02_fig_reflectance_spectrum_6b2265d217`：附件 1/2 碳化硅晶圆片实测反射率谱（两入射角），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reflectance_spectrum_6b2265d217.png`
- `prob02_fig_model_fit_0ca711689b`：两入射角实测谱与两光束物理正模型 (2.3) 拟合对比，`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_model_fit_0ca711689b.png`
- `prob02_fig_thickness_estimate_efa7359eb9`：prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_thickness_estimate_efa7359eb9.png`
- `prob02_fig_dispersion_curve_af50244106`：外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_dispersion_curve_af50244106.png`
- `prob02_fig_reliability_summary_78cd97014b`：prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reliability_summary_78cd97014b.png`
- `prob02_fig_variable_projection_jcurve_7a9a903650`：主反演目标函数 J(t) 与全局唯一性，`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_variable_projection_jcurve_7a9a903650.png`
- `prob02_fig_g_space_phase_gap_f500d9c0db`：相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照，`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_g_space_phase_gap_f500d9c0db.png`
- `prob02_fig_nsub_decoupling_39b4128d09`：n_sub 幅值弱可辨识性与 t-n_sub 解耦，`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_nsub_decoupling_39b4128d09.png`
- `prob02_fig_response_surface_cfe5827835`：两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_response_surface_cfe5827835.png`
- `prob02_fig_methods_compare_99386076f5`：prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_methods_compare_99386076f5.png`
- `prob02_fig_ablation_summary_dcd697b29e`：prob02 ablation 判据汇总（F0 + A1–A4），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_summary_dcd697b29e.png`
- `prob02_fig_ablation_thickness_d29e3fc1f0`：prob02 ablation 厚度对照（F0 + A1–A4），`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_thickness_d29e3fc1f0.png`
- `prob02_fig_ablation_shared_t_14e5362fa7`：A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致，`problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_shared_t_14e5362fa7.png`

## prob03

- 接受假设版本：`assumption_v001`
- 接受公式版本：`formulation_v002`
- L1-L4 sanity：PASS_WITH_WARNING
- L5 sanity：PASS
- 鲁棒性：{'decision': 'completed', 'reason': 'prob03 robustness 复核完成：formulation_v002 §8.5 预注册判据 R1–R8 全部在阈值内通过（R1 两角 0.130%≤2%、R2 色散 0.503%≤2%、R3 CI 0.134%≤2%、R4 异常 0.0%≤1%、R5 多光束 0.111%≤10%、R6 n_sub 解耦 0.0%、R7 窗口 0.749%≤2%（只读探针补登）、R8 唯一性次小候选≈1.020 为报告项由 §7.6 判据保障全局唯一）；结论 STABLE，送至 sanity-checker 执行 Level 6 验收。'}
- 消融：{'decision': 'completed', 'reason': 'ablation 适用并已完成：formulation_v002 主反演（基线-干涉分解 + 一维相位频率扫描 variable projection，两角共享 t）含可解释、可分离的公式项/算法模块/约束方向（色散项 N-SE、基线多项式 p、包络多项式 q、两角共享 t 约束、多光束 Airy 高阶项），REQUEST.md 要求复杂算法必要性证据，robustness 已覆盖输入/情景不确定性、ablation 补充模型内部组件必要性，二者互补。预注册方案 ablation_v001（核心结论+消融判据运行前固定，ablation/ 目录），隔离任务 bd175bb7b9a82f35e054（stage=ablation，supervised worker，returncode=0，feasible_incumbent=true）执行 F0 完整模型对照 + A1 色散项 / A2 多光束(Airy)高阶项 / A3 基线多项式项 / A4 两角共享 t 约束，5/5 判据通过，conclusion=components_confirmed：A1 Δt=0.446%≤2%、A2 Δt=0.300%≤1%（L17 极值不变性/Q1 定量）、A3 Δt=0.574%≤2%（RMSE +9.5%，基线项为拟合优度必要组件）、A4 每角偏差 0.089%≤2% 且 ε12=0.130%≤2%（共享为安全一致性约束）。消融结论/汇总表/3 张消融图（自动质检+视觉复核 passed）已归档 ablation/、results/ablation/ 与 figures.yaml；未删除任何不利情景，模型组件必要性证据供论文/Q1 引用。ablation 为最后一个可选阶段，required artifacts 全部满足，提交局部完成。'}

### 小问总结

# 小问总结

本问由 Airy 多光束反射率推导多光束干涉的必要条件，并验证在无吸收平行板条件下高阶反射主要改变条纹形状而不改变极值位置及厚度周期。附件 3/4 的硅外延层共享厚度为 $3.4477\,\mu\mathrm{m}$，两角分别为 $3.4507/3.4463\,\mu\mathrm{m}$，相对差 $0.130\%$。硅的界面反射率组合给出 $\bar R\approx0.0101$、精细度约 0.319，多光束相对改善约 0.11%，判定两光束模型足够；对 SiC 重判得到 $\bar R\approx0.0024$，同样无需多光束修正，因此 prob02 的 $7.2158\,\mu\mathrm{m}$ 结论维持。全部预注册可靠性与消融判据通过；弱色散下次小候选接近简并和 $n_{\mathrm{sub}}$ 弱可辨识作为报告边界保留。

### 任务追踪

- `7e209043973692d067ed`：succeeded，阶段 `computation`
- `bd175bb7b9a82f35e054`：succeeded，阶段 `ablation`
- `f1c4e3ed425ff6b0e73f`：succeeded，阶段 `computation`
- `fc633110c86bfd0aeec2`：failed，阶段 `computation`

### 图表索引

- `prob03_fig_reflectance_spectrum_41a3800f70`：附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reflectance_spectrum_41a3800f70.png`
- `prob03_fig_model_fit_3e94d2fac7`：两入射角实测谱与两光束物理正模型 (2.8) 拟合对比，`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_model_fit_3e94d2fac7.png`
- `prob03_fig_thickness_estimate_59f1546ed7`：prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_thickness_estimate_59f1546ed7.png`
- `prob03_fig_dispersion_curve_aac3dcebea`：硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_dispersion_curve_aac3dcebea.png`
- `prob03_fig_reliability_summary_50b4f34a17`：prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reliability_summary_50b4f34a17.png`
- `prob03_fig_variable_projection_jcurve_4b30b360a4`：主反演目标函数 J(t) 与全局唯一性，`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_variable_projection_jcurve_4b30b360a4.png`
- `prob03_fig_mb_conditions_9571a5012b`：多光束干涉必要条件 N1–N4 与硅片判定，`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_mb_conditions_9571a5012b.png`
- `prob03_fig_sic_multibeam_recheck_4cbb136f9c`：多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_sic_multibeam_recheck_4cbb136f9c.png`
- `prob03_fig_response_surface_06cfec9b1e`：两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_response_surface_06cfec9b1e.png`
- `prob03_fig_phase_freq_gspace_a936624612`：相位频率（g 空间）测厚机制与条纹计数，`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_phase_freq_gspace_a936624612.png`
- `prob03_fig_ablation_summary_9f93c3dd2d`：prob03 ablation 判据汇总（F0 + A1–A4），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_summary_9f93c3dd2d.png`
- `prob03_fig_ablation_t_consistency_ec44908369`：prob03 ablation 厚度对照（F0 + A1–A4），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_t_consistency_ec44908369.png`
- `prob03_fig_ablation_rmse_ce4b523efa`：prob03 ablation 拟合优度对照（加权 RMSE），`problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_rmse_ce4b523efa.png`


## 跨小问一致性

跨小问一致性审查通过：共享符号（t,n,n_sub,θ,θ′,λ,ν,R,δ,R_01/R_12,finesse）与单位、参数值（Sellmeier 一致、主带 ν∈[2000,4000]cm⁻¹、θ=10/15°、Reststrahlen [700,1000]cm⁻¹ 剔除）、假设、数据版本、约束（R∈[0,1]、t>0、n>1）、结论方向与数量级全部跨问自洽；软依赖 conclusion hash（prob01=828203556617be979f7345dce7c274dd1850b62fe950a6e108015ad161b070a6、prob02=27b0ce8689e1eb2b345e5803309ea80bb6b84a620f189ed6cd589e75f23a12ea）完整匹配，无 stale 传播、无回退。唯一共享符号元数据不一致（finesse domain ≥1 vs 实际 F≈0.32<1）已由本审查修订为 >0，属全局符号表规范修订，不影响任何计算结果。裁决依据：题目硬约束、sanity 硬门禁、文献/机理、鲁棒性、解释性、时间顺序均一致；无硬门禁失败版本。recommended_next_stage=paper_writing（须先行补齐三问 question_summary 并披露既有技术债）。

## 文献索引

- `?`：Thickness Measurement of Epitaxial Films by the Infrared Interference Method，Journal of The Electrochemical Society（1962）
- `?`：The Infrared Interference Method of Measuring Epitaxial Layer Thickness，Journal of The Electrochemical Society（1969）
- `?`：ASTM F95-89(2000): Standard Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer，ASTM International（标准组织正式文件）（2000）
- `?`：SEMI MF95 (SEMI MF009500): Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer，SEMI International Standards（2013）
- `?`：Thickness Measurement of Thin (1.0-µm) Epitaxial Silicon Layers by Infrared Reflectance，Silicon Processing (ASTM STP 804)（1983）
- `?`：Principles of Optics: Electromagnetic Theory of Propagation, Interference and Diffraction of Light (7th ed.)，Cambridge University Press（权威教材）（1999）
- `?`：Optics (5th ed., Global Edition)，Pearson（权威教材）（2017）
- `?`：Refractive Index, Dispersion, and Birefringence of Silicon Carbide Polytypes，Applied Optics（1971）
- `?`：4H-SiC: a new nonlinear material for midinfrared lasers，Laser & Photonics Reviews（2013）
- `?`：Temperature dependence of refractive indices for 4H- and 6H-SiC，Journal of Applied Physics（2014）
- `?`：Refractiveindex.info database of optical constants，Scientific Data（2024）
- `?`：Refractive index of silicon and germanium and its wavelength and temperature derivatives，Journal of Physical and Chemical Reference Data（1980）
- `?`：Handbook of Optical Constants of Solids (Vol. 1-3)，Academic Press（权威手册）（1998）
- `?`：Infrared Absorption in n-Type Silicon，Physical Review（1957）
- `?`：From Transport Measurements to Infrared Reflectance Spectra of n-Type Doped 4H-SiC Layer Stacks，Materials Science Forum（2003）
- `?`：Temperature dependence of the anisotropy of the infrared dielectric properties and phonon-plasmon coupling in n-doped 4H-SiC，Journal of Physics and Chemistry of Solids（2023）
- `?`：基于色散修正与全谱拟合的红外干涉测厚模型研究，数学建模及其应用（Mathematical Modeling and Its Applications）（2026）
- `?`：Non-destructive measurement of SiC Epitaxial Layer Thickness Using FTIR Spectroscopy with Cauchy Dispersion Optimization，Highlights in Science, Engineering and Technology（2025）
- `?`：Precise Measurement of Silicon Carbide Epitaxial Layer Thickness Based on Infrared Interferometric Spectroscopy and Nonlinear Iterative Inversion，Proceedings of the 1st International Conference on Smart System Design, Application and Mechatronics（2026）
- `?`：Precise Measurement of Silicon Carbide Epitaxial Layer Thickness，Proceedings of the 1st International Conference on Smart System Design, Application and Mechatronics（2026）
- `?`：Accurate SiC Epitaxial Thickness Measurement via Hybrid Deep Learning and Physical Interference Model for Power Device Applications，Journal of Nanoelectronics and Optoelectronics（2025）
- `?`：cumcm-2025b-sic-epitaxy: 2025 年高教社杯全国大学生数学建模竞赛 B 题解题文档，GitHub（公开仓库，非权威来源）（2025）
- `?`：Determination of Refractive Index and Film Thickness from Interference Fringes，Applied Optics（1971）
- `?`：Self-consistent optical constants of SiC thin films，Journal of the Optical Society of America A（2011）
- `?`：Dispersion Compensation and Multi-Beam Interference Correction Algorithm for Thickness Measurement of SiC Epitaxial Layer，Sensors（2026）
- `?`：Optical properties of 4H-SiC and 6H-SiC from infrared to vacuum ultraviolet spectral range ellipsometry (0.05–8.5 eV)，Surface Science Spectra（2024）
- `?`：Infrared to vacuum ultraviolet optical properties of 3C, 4H and 6H silicon carbide measured by spectroscopic ellipsometry，Thin Solid Films（2004）
- `?`：Infrared Optical Properties of 3C, 4H and 6H Silicon Carbide，Materials Science Forum（2003）
- `?`：Temperature-dependent infrared optical properties of 3C-, 4H- and 6H-SiC，Physica B: Condensed Matter（2018）
- `?`：Investigation of longitudinal-optical phonon-plasmon coupled modes in SiC epitaxial film using Fourier transform infrared reflection，Journal of Electronic Materials（2005）
- `?`：Improved Resolution of Epitaxial Thin Film Doping Using FTIR Reflectance Spectroscopy，Materials Science Forum（2005）
- `?`：Fundamentals of epitaxial silicon film thickness measurements using emission and reflection Fourier transform infrared spectroscopy，Journal of Applied Physics（1993）
- `?`：Infrared Thickness Measurement of SiC/Si Epitaxial Layers with Multibeam Interference Modeling，2025 5th International Conference on Mechanical Automation and Electronic Information Engineering (MAEIE)（2025）
- `?`：High-precision thickness measurement of SiC epitaxial layers by infrared interference: from two-beam to multi-beam modeling，Second International Conference on Communication, Information, and Digital Technologies (CIDT 2025)（2026）
- `?`：A method for determining the thickness of semiconductor epitaxial layers under multibeam interference—taking SiC as an example，Fifth International Conference on Computer Technology, Information Engineering, and Electron Materials (CTIEEM 2025)（2026）
- `?`：Robust Spectral Signal Processing-Based Framework for Infrared Interferometry-Driven SiC Epitaxial Thickness Estimation，2026 IEEE International Conference on Power, Electronics and Green Energy (ICPEGE)（2026）
- `?`：Non-destructive thickness measurement algorithm for SiC epitaxial layers based on infrared interferometry，International Conference on Optoelectronic Materials and Devices (ICOMD 2025)（2026）
- `?`：Spectral Numerical Computation and Multi-Beam Correction for Epitaxial Layer Thickness Measurement，2026 International Conference on Computer Intelligence and Software Engineering (CICSE)（2026）
- `?`：Measurement and algorithm for silicon carbide epitaxial layer thickness via interference spectroscopy，Third International Conference on Big Data, Computational Intelligence, and Applications (BDCIA 2025)（2026）
- `?`：PROGRESSIVE MODELING FOR SILICON CARBIDE EPITAXIAL LAYER THICKNESS MEASUREMENT: FROM DUAL-BEAM THEORY TO MULTI-BEAM INTERFERENCE CORRECTION，World Journal of Engineering Research（2026）
- `?`：Quantitative Inversion of Silicon Carbide Epitaxial Layer Thickness Based on Dual-Beam Interference Theory and Experimental Algorithm Validation，Proceedings of the 1st International Conference on Advanced Computation, Engineering Intelligence and Information Processing（2026）
- `?`：Nonlinear optical properties of 6H-SiC and 4H-SiC in an extensive spectral range，Optical Materials Express（2021）
- `?`：An improved method for measuring epi-wafer thickness based on the infrared interference principle: Addressing interference quality and multiple interferences in double-layer structures，Results in Physics（2023）
- `?`：On the Infrared Thickness Measurement of Epitaxially Grown Silicon Layers，Applied Optics（1970）
- `?`：Infrared interference spectra observed in silicon epitaxial wafers，Solid-State Electronics（1966）
- `?`：Multiple reflections in an approximately parallel plate，Optics Communications（1997）
- `?`：Influence of coating thickness on the performance of a Fabry–Perot interferometer，Applied Optics（1991）
- `?`：High-Precision Thickness Inversion of SiC Epitaxial Layers via Multi-Beam Interferometric Spectroscopy and Nonlinear Optimization，2026 11th International Conference on Intelligent Computing and Signal Processing (ICSP)（2026）
- `?`：High-precision thickness measurement of epitaxial layers via FFT-based inversion algorithm for multi-beam interference correction，IET Conference Proceedings（2026）
- `?`：Research on Thickness Modeling of Silicon Carbide and Silicon Wafer Epitaxial Layer Based on Infrared Interference Method，Proceedings of the 1st International Conference on Smart System Design, Application and Mechatronics（2026）
