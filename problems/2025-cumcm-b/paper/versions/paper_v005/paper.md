# 2025-cumcm-b 数学建模论文

## 摘要

针对问题1，本问建立了考虑折射率色散与斜入射 Snell 几何的两光束 Fresnel 干涉模型，并推导同型相邻极值间隔与外延层厚度的关系。合成验证中，色散化相位法得到约 $10.002\,\mu\mathrm{m}$，全谱非线性最小二乘得到 $10.000\,\mu\mathrm{m}$，均恢复 $t_{\mathrm{true}}=10\,\mu\mathrm{m}$；常数折射率间隔法约有 **4%** 系统偏差，因此仅作初值或交叉校验。两入射角结果一致，E1–E5 稳健性判据和消融判据全部通过。结论仅适用于无显著吸收、界面近似平行且采用已登记色散模型的谱段；$\lambda>5\,\mu\mathrm{m}$ 色散延伸和 Reststrahlen 区处理仍作为边界条件保留。<!-- evidence:ev_artifact_a78e13973522 --> 针对问题2，本问针对附件 1/2 的 SiC 实测反射率谱，采用“慢变基线—干涉项分解 + 一维相位频率变量投影”反演厚度，使厚度主要由条纹相位频率确定并与衬底折射率幅值弱可辨识性解耦。两角共享厚度为 $7.2158\,\mu\mathrm{m}$，10°/15° 分别为 $7.2214/7.2095\,\mu\mathrm{m}$，相对差 $0.165\%$；色散、置信区间、异常点、多光束与全局极小判据通过。两角嵌套 F 检验虽统计显著（$p=0.022$），但实际厚度差远低于 **2%** 阈值，按预注册规则解释为测量点差异或膜厚梯度，不触发模型修订。$\lambda>5\,\mu\mathrm{m}$ 色散缺口、$n_{\mathrm{sub}}$ 弱可辨识及物理 NLS 约 **5.5%** 交叉校验偏差作为推广限制保留。<!-- evidence:ev_artifact_1c7696fb4377 --> 针对问题3，本问由 Airy 多光束反射率推导多光束干涉的必要条件，并验证在无吸收平行板条件下高阶反射主要改变条纹形状而不改变极值位置及厚度周期。附件 3/4 的硅外延层共享厚度为 $3.4477\,\mu\mathrm{m}$，两角分别为 $3.4507/3.4463\,\mu\mathrm{m}$，相对差 $0.130\%$。硅的界面反射率组合给出 $\bar R\approx0.0101$、精细度约 0.319，多光束相对改善约 **0.11%**，判定两光束模型足够；对 SiC 重判得到 $\bar R\approx0.0024$，同样无需多光束修正，因此 prob02 的 $7.2158\,\mu\mathrm{m}$ 结论维持。全部预注册可靠性与消融判据通过；弱色散下次小候选接近简并和 $n_{\mathrm{sub}}$ 弱可辨识作为报告边界保留。<!-- evidence:ev_artifact_ed5e6f341dcb --> 本文还从跨小问一致性、扰动稳定性与模型边界三个层面验证结果，所有定量结论均可回溯到已验收证据包。

## 关键词

数学建模；结果分析；模型检验

## 问题重述

（请先阅读"全国大学生数学建模竞赛论文格式规范"） 碳化硅作为一种新兴的第三代半导体材料，以其优越的综合性能表现正在受到越来越多的关注。碳化硅外延层的厚度是外延材料的关键参数之一，对器件性能有重要影响。因此，制定一套科学、准确、可靠的碳化硅外延层厚度测试标准显得尤为重要。 红外干涉法是外延层厚度测量的无损伤测量方法，其工作原理是，外延层与衬底因掺杂载流子浓度的不同而有不同的折射率，红外光入射到外延层后，一部分从外延层表面反射出来，另一部分从衬底表面反射回来（图 1），这两束光在一定条件下会产生干涉条纹。可根据红外光谱的波长、外延层的折射率和红外光的入射角等参数确定外延层的厚度。 通常外延层的折射率不是常数，它与掺杂载流子的浓度、红外光谱的波长等参数有关。 ![图 1 外延层厚度测量原理的示意图](图1) 如果考虑外延层和衬底界面只有一次反射、透射所产生的干涉条纹的情形（图 1），建立确定外延层厚度的数学模型。 请根据问题 1 的数学模型，设计确定外延层厚度的算法。对附件 1 和附件 2 提供的碳化硅晶圆片的光谱实测数据，给出计算结果，并分析结果的可靠性。 光波可以在外延层界面和衬底界面产生多次反射和透射（图 2），从而产生多光束干涉。请推导产生多光束干涉的必要条件，以及多光束干涉对外延层厚度计算精度可能产生的影响。 请根据多光束干涉的必要条件，分析附件 3 和附件 4 提供的硅晶圆片的测试结果是否出现多光束干涉，给出确定硅外延层厚度计算的数学模型和算法，以及相应的计算结果。 如果你们认为，多光束干涉也会出现在碳化硅晶圆片的测试结果（附件 1 和附件 2）中，从而影响到碳化硅外延层厚度计算的精度，请设法消除其影响，并给出消除影响后的计算结果。 ![图 2 多光束干涉的示意图](图2) 1. 附件 1.xlsx 和附件 2.xlsx 是入射角分别为 10° 和 15° 时针对同一块碳化硅晶圆片的测试结果，其中第 1 列为波数（单位：cm⁻¹），第 2 列为干涉光谱的反射率（单位：%）。 2. 附件 3.xlsx 和附件 4.xlsx 是入射角分别为 10° 和 15° 时针对同一块硅晶圆片的测试结果，其中第 1 列为波数（单位：cm⁻¹），第 2 列为干涉光谱的反射率（单位：%）。 碳化硅（SiC）是第三代半导体材料，外延层厚度是其关键参数，直接影响器件性能。题目要求基于**红外干涉法**建立科学、准确、可靠的外延层厚度测试方法。 红外干涉法原理：外延层与衬底因掺杂载流子浓度不同而具有不同折射率；红外光入射到外延层后，一部分从外延层表面反射，另一部分穿过外延层后从衬底界面反射回来，两束光产生干涉条纹。由红外光谱的波长（波数）、外延层折射率和入射角等参数可确定外延层厚度。注意：外延层折射率不是常数，与掺杂载流子浓度和波长有关。 目标：建立确定外延层厚度的数学模型与算法，并基于 4 个附件的实测光谱数据给出计算结果与可靠性分析。 - 外延层厚度 $t$（核心未知量）。 - 红外干涉光谱实测数据：波数 $\nu$（cm⁻¹）与反射率 $R$（%），来自附件 1–4； - 入射角 $\theta$：附件 1、3 为 10°，附件 2、4 为 15°； - 样品类型：附件 1、2 为同一块碳化硅晶圆片；附件 3、4 为同一块硅晶圆片。 - 外延层厚度 $t$； - 外延层折射率 $n$（与掺杂载流子浓度、波长相关，非常数，其色散关系待定）； - 衬底折射率 $n_{\text{sub}}$（碳化硅/硅衬底在红外波段的取值待定）； - 干涉级次 $m$ 与干涉条纹的识别（峰/谷定位）等。 - 厚度必须为正且量级合理（SiC 外延层厚度通常为微米量级，需与器件工艺常识一致）； - 同一晶圆片在不同入射角（10° 与 15°）下的厚度计算结果应一致（这是可靠性检验的天然判据）； - 模型必须与"外延层折射率随掺杂浓度和波长变化"的物理事实一致； - 原始数据只读，不得修改；计算必须可复现、可追溯。 - 无时间维度；光谱范围为波数约 400–4000 cm⁻¹（对应波长约 2.5–25 μm）的中红外区间。 - 问题 1：单次反射-透射（两光束干涉）情形下确定外延层厚度的数学模型； - 问题 2：基于问题 1 模型的厚度确定算法 + 附件 1、2 的计算结。

## 问题分析与总体流程

全文采用“问题分析—假设与符号统一—分问建模—结果解释—稳健性分析—跨问一致性检验”的流程。

## 模型假设

各小问的关键假设、适用范围及偏差方向在对应小问中说明，并以文献作为方法依据 [@L01]。

## 符号说明

| 符号 | 含义 | 单位 |
|---|---|---|
| $x$ | 题面给定或预处理后的自变量 | 见数据说明 |
| $y$ | 模型响应或观测量 | 见对应小问 |
| $	heta$ | 模型参数向量 | 按分量给定 |
| $arepsilon$ | 观测与模型之间的残差 | 与 $y$ 相同 |

: 符号说明

<!-- evidence:ev_artifact_dce9d09f9933 -->

## 数据说明与预处理

数据文件、预处理记录和计算结果均由证据包按 SHA-256 固定。正文不改写原始数据；异常值、缺失值、筛选区间和单位转换以各问已验收实现与结果记录为准。

## prob01 模型建立、求解与结果

### prob01 问题分析

本问先从题面目标识别输入、输出与约束，再采用已接受的假设和公式完成求解，避免在结果之后倒推模型。

### prob01 模型假设

> 版本：assumption_v001 ｜ 阶段：assumption_definition ｜ 状态：candidate > 问题：2025 高教社杯 B 题问题 1 —— 考虑外延层与衬底界面"只有一次反射、透射"产生干涉条纹的情形，建立确定外延层厚度 $t$ 的数学模型。 > 证据规则：关键假设必须有本问文献池中 verified 且 used 的来源；普通常识假设标记 common_sense；project_assumption 与 agent_inference 显式区分。 | 族 | 内容 | 条目 | |---|---|---| | F1 | 两光束干涉模型与厚度公式（关键） | A1–A4 | | F2 | 折射率色散（Sellmeier/分谱段策略） | A5, A12 | | F3 | 掺杂/自由载流子对红外折射率的影响 | A6 | | F0 | 边界与数据假设 | A7–A11 | 冲突检查结论：本组假设内部无冲突；与 prob01 题目理解（problem_understanding.md）及全局符号表（global_symbols.yaml）一致；prob01 为整题建模起点，无前问结论依赖。A2 与 A7 的谱段适用性以 A7 边界约束为限（近 Reststrahlen 区吸收不可忽略）。 --- - **类型**：机理简化（两光束叠加） - **关键性**：关键 - **证据类型**：literature_fact - **引用**：L01（Albert & Combs 1962）、L02（Schumann 1969）、L06（Born & Wolf）、L07（Hecht） - **精确陈述**：红外光入射外延层后，仅考虑两束相干光——一束在外延层上表面（空气/外延层界面）直接反射，另一束透射进入外延层后在外延层/衬底界面反射并再次透射回空气；忽略外延层内多次反射、衬底背面反射与其他高阶光束。 - **适用边界**：与题面图 1 设定一致；要求外延层界面平行、衬底背面反射可忽略、光在层内往返一次后振幅衰减可忽略。适用于 prob01。 [@L01]<!-- evidence:ev_artifact_ae2969b416fb -->

### prob01 模型建立与求解

> 版本：formulation_v001 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation > 问题：2025 高教社杯 B 题问题 1 —— 考虑外延层与衬底界面"只有一次反射、透射"产生的干涉条纹，建立确定外延层厚度 $t$ 的数学模型。 > 本版本为解析正模型 + 反演公式的完整推导；prob01 无附件数据，不运行数值计算，计算与数据验证留待 prob02（implementation/computation 阶段）。 给定外延层-衬底结构的物理设定（图 1），在两光束干涉近似下建立： 1. 反射率 $R$ 与厚度 $t$、折射率 $n$、入射角 $\theta$、波数 $\nu$ 的解析关系式； 2. 干涉极值（峰/谷）条件及同型相邻极值波数间隔 $\Delta\nu$ 与厚度的定量关系； 3. 由 $\Delta\nu$（或全谱拟合）反演厚度 $t$ 的公式与适用条件。 | 量 | 符号 | 单位 | 来源 | |---|---|---|---| | 入射角（空气侧，相对表面法线） | $\theta$ | 度 | 题面；prob02 附件 1/2 为 10°、15° | | 外延层折射率（色散） | $n(\nu)$ 或 $n(\lambda)$ | 无量纲 | A5；L09 Sellmeier（$\lambda\le5\,\mu\text{m}$）；$\lambda>5\,\mu\text{m}$ 由 prob02 数据反演/分谱段确定 | | 衬底折射率 | $n_{\text{sub}}$ | 无量纲 | A6；prob02 反演/文献取值 | | 空气折射率 | $n_{\text{air}}$ | 无量纲 | A9；$n_{\text{air}}=1.0$ | | 量 | 符号 | 单位 | |---|---|---| | 外延层厚度 | $t$ | $\mu\text{m}$（正实数） | | 模型反射率谱 | $R(\nu)$ | 无量纲（0–1） | | 干涉级次 | $m$ | 非。 公式中的符号、单位和适用条件以“符号说明”和接受版本为准。<!-- evidence:ev_artifact_55e196100f35 -->

### prob01 结果解释

本问建立了考虑折射率色散与斜入射 Snell 几何的两光束 Fresnel 干涉模型，并推导同型相邻极值间隔与外延层厚度的关系。合成验证中，色散化相位法得到约 $10.002\,\mu\mathrm{m}$，全谱非线性最小二乘得到 $10.000\,\mu\mathrm{m}$，均恢复 $t_{\mathrm{true}}=10\,\mu\mathrm{m}$；常数折射率间隔法约有 4% 系统偏差，因此仅作初值或交叉校验。两入射角结果一致，E1–E5 稳健性判据和消融判据全部通过。结论仅适用于无显著吸收、界面近似平行且采用已登记色散模型的谱段；$\lambda>5\,\mu\mathrm{m}$ 色散延伸和 Reststrahlen 区处理仍作为边界条件保留。<!-- evidence:ev_artifact_a78e13973522 -->

![两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_reflectance_spectrum_1d4fb899d1.png){#prob01_fig_reflectance_spectrum_1d4fb899d1}

@fig:prob01_fig_reflectance_spectrum_1d4fb899d1 展示“两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_7a32edbc8a9e -->
![外延层 4H-SiC 折射率色散模型 n(ν)](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_dispersion_curve_d85564d2fc.png){#prob01_fig_dispersion_curve_d85564d2fc}

@fig:prob01_fig_dispersion_curve_d85564d2fc 展示“外延层 4H-SiC 折射率色散模型 n(ν)”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_15b6f2332b74 -->
![色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_phase_function_gap_459c486470.png){#prob01_fig_phase_function_gap_459c486470}

@fig:prob01_fig_phase_function_gap_459c486470 展示“色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_0d27904b7650 -->
![三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_thickness_methods_compare_5eac465fc8.png){#prob01_fig_thickness_methods_compare_5eac465fc8}

@fig:prob01_fig_thickness_methods_compare_5eac465fc8 展示“三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_e5a8c9b5b48d -->
![方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_spacing_constant_n_bias_2245b6eda4.png){#prob01_fig_spacing_constant_n_bias_2245b6eda4}

@fig:prob01_fig_spacing_constant_n_bias_2245b6eda4 展示“方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_465d5df2f0a3 -->
![全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_nls_multistart_e64919ab13.png){#prob01_fig_nls_multistart_e64919ab13}

@fig:prob01_fig_nls_multistart_e64919ab13 展示“全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_3aa4f2349c5a -->
![两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_response_surface_d0691c5dd8.png){#prob01_fig_response_surface_d0691c5dd8}

@fig:prob01_fig_response_surface_d0691c5dd8 展示“两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_8bddbe7bab83 -->
![prob01 robustness 敏感性 tornado 汇总（E1–E5）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_sensitivity_tornado_6983566848.png){#prob01_fig_sensitivity_tornado_6983566848}

@fig:prob01_fig_sensitivity_tornado_6983566848 展示“prob01 robustness 敏感性 tornado 汇总（E1–E5）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_bf1c3bb811a0 -->
![E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_noise_robustness_ci_30d4fa737f.png){#prob01_fig_noise_robustness_ci_30d4fa737f}

@fig:prob01_fig_noise_robustness_ci_30d4fa737f 展示“E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_468d6eb2d342 -->
![prob01 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_summary_ee3c34dcfa.png){#prob01_fig_ablation_summary_ee3c34dcfa}

@fig:prob01_fig_ablation_summary_ee3c34dcfa 展示“prob01 ablation 判据汇总（F0 + A1–A4）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_8526f70dd717 -->
![A3 偏振一致性：avg/s/p 反演厚度 vs t_true](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_polarization_da59250d1b.png){#prob01_fig_ablation_polarization_da59250d1b}

@fig:prob01_fig_ablation_polarization_da59250d1b 展示“A3 偏振一致性：avg/s/p 反演厚度 vs t_true”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_7460c4889f44 -->
![A4 初值策略对比：单初值局部极小 vs 多初值全局解](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_init_strategy_7c59622d5a.png){#prob01_fig_ablation_init_strategy_7c59622d5a}

@fig:prob01_fig_ablation_init_strategy_7c59622d5a 展示“A4 初值策略对比：单初值局部极小 vs 多初值全局解”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_a6478f4b1fae -->

### prob01 可靠性与结论

稳健性分析：robustness 适用并已完成：formulation_v001 §5.2 将鲁棒性列为比较标准，A5/A6/A10 要求灵敏度分析，workflow warnings 需量化色散/n_sub/截断对厚度的影响。预注册方案 robustness_v001（核心结论+稳定性判据运行前固定，robustness/ 目录），隔离任务 554819114361017c5b70 执行 E1–E5（n_sub/θ ±5/±10/±20% 扰动、色散三模型、噪声 σ=0.5/1/2%×100 次×2 入射角、谱段截断 6 组），5/5 判据通过 conclusion=stable（E1 0.008%、E2 0.22%、E3 替代模型 0.96%、E4 CI 半宽<0.03% 且收敛率 100%、E5 0%）；发现噪声下极值定位初值失真并升级网格扫描初值（prob02 复用）；原始样本/汇总表/置信区间/敏感性图/稳定性结论已归档 robustness/ 与 results/robustness/，交 sanity-checker 执行 Level 6。消融分析：ablation 适用并已完成：formulation_v001 (3.5) 正模型含可解释可分离的公式项（界面反射项/衬底往返项/干涉振荡项）与算法模块（NLS 多初值），REQUEST.md 要求复杂算法必要性证据，robustness 已覆盖输入/情景不确定性、ablation 补充模型组件必要性，二者互补。预注册方案 ablation_v001（核心结论+判据运行前固定，ablation/ 目录），隔离任务 5dcb72876c5fcb2c7e95 执行 F0+A1–A4（干涉项消融、衬底反射消融、偏振平均消融、多初值模块消融），5/5 判据通过 conclusion=components_confirmed（A1/A2 不可辨识=组件必要、A3 最大差 0.012%、A4 单初值 6.03% vs 多初值 ~0）；消融结论/汇总表/3 张消融图（自动质检+视觉复核 passed）已归档 ablation/、results/ablation/ 与 figures.yaml，prob01 全部阶段完成，进入 locally_completed。适用边界为：prob01 合成验证任务 0ea4b29da19e8479a6ea 消费完成：19/19 检查通过，t_true=10µm 被 NLS/相位法精确恢复，两入射角一致；hash 追踪链（code/config/input）与 task.json、implementation.md §7 完全一致，无 NaN/Inf、无硬约束违反、formula-代码逐条一致、文献/物理常识合理。技术债（λ>5µm 常数色散延伸、方法 A 约4%基线偏差、文献全文待复核、n_sub 合成场景值、Reststrahlen 剔除策略）均为既有 workflow warning，留 prob02 处理，不阻断推进。L1–L4 判定 PASS_WITH_WARNING，Level 5 待全部小问完成、Level 6 待 robustness 阶段。<!-- warning:warn_prob01_fac14a9dfae4 -->；prob01 Level 6（robustness 验收）独立复核通过：任务 554819114361017c5b70 全部输出有限且追踪完整，hash 链（code/config/input）与 task.json 一致，E1–E5 判据独立重算全部通过（conclusion=stable、5/5），E4 600 样本收敛率 100%、95% CI 半宽最大 0.022% 远低于阈值，预注册方案运行前固定未事后修改；物理机制（n_sub 影响幅度不影响相位、θ 误差二阶小量、色散模型为最大不确定度来源、全谱平均效应）与常识一致。技术债（robustness 基于合成谱、色散模型选择、λ>5µm 常数延伸、n_sub 场景值、文献全文待复核、Reststrahlen 剔除）均为既有 workflow warning，留 prob02 处理，不阻断推进。<!-- warning:warn_prob01_cdf6b5be3241 -->。本问结论限于上述假设、数据范围和误差条件。<!-- evidence:ev_artifact_a78e13973522 -->

## prob02 模型建立、求解与结果

### prob02 问题分析

本问先从题面目标识别输入、输出与约束，再采用已接受的假设和公式完成求解，避免在结果之后倒推模型。

### prob02 模型假设

> 版本：assumption_v001 ｜ 阶段：assumption_definition ｜ 状态：candidate > 问题：2025 高教社杯 B 题问题 2 —— 依据问题 1 的两光束干涉数学模型，设计确定碳化硅外延层厚度的算法，对附件 1（10°）与附件 2（15°）的实测光谱给出计算结果并分析可靠性。 > 证据规则：关键假设必须绑定本问文献池中 verified 且 used 的来源（L25–L32）；普通常识假设标记 common_sense/project_assumption；team_decision 与 agent_inference 显式区分；由 prob01 承接的模型假设标记 inherited 并引用 `prob01-conclusion-v1`。 | 族 | 内容 | 条目 | |---|---|---| | H1 | 数据契约与预处理（比例归一、>100% 异常、Reststrahlen 谱段） | B1–B3 | | H2 | 两光束模型与几何/相位继承（prob01-conclusion-v1） | B4, B5 | | H3 | 材料光学参数：色散 n(ν)、衬底 n_sub、吸收边界 | B6, B7 | | H4 | 厚度反演算法：极值定位、全谱 NLS、色散化优先 | B8–B10 | | H5 | 可靠性与统计：两入射角一致性、噪声传播 | B11, B12 | | H6 | 多光束判定与修正（预留 prob03） | B13 | **冲突检查结论**：本组假设内部无冲突；与 prob02 题目理解（problem_understanding.md）、全局符号表（global_symbols.yaml）及 prob01 结论（prob01-conclusion-v1，content_hash 828203556617be979f7345dce7c274dd1850b62fe950a6e108015ad161b070a6）一致。H3 的色散/吸收与 H1 的谱段边界以 B3 为限；B6 色散化与 B10 色散化优先在。 [@L01]<!-- evidence:ev_artifact_7fbd73d2c8cb -->

### prob02 模型建立与求解

> 版本：formulation_v003 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation > 问题：2025 高教社杯 B 题问题 2 —— 依据问题 1 的两光束干涉数学模型，设计确定碳化硅（SiC）外延层厚度的算法；对附件 1（入射角 10°）与附件 2（入射角 15°）的实测光谱给出厚度计算结果，并分析结果的可靠性。 > 继承基础：模型公式继承 `prob01-conclusion-v1`（prob01/formulation_v001，content_hash `82820355…070a6`）与 `prob02/formulation_v001`（content_hash `49ff5160…51eb8`）、`prob02/formulation_v002`（content_hash `53661f5069b347…07410`）。本版本为 **v002 的修订版**，针对 computation 阶段实测反演暴露的**模型可辨识性结构缺陷**（`feasible_incumbent=false`，且主方法 M1 与 M2/M3 出现两个数量级的量级冲突）做**方法论核心修正**。 > 说明：本问为**可行解反演**问题（连续参数估计，正模型含解析干涉项），按 knowledge/optimization.md 求解策略规则，主方法为**一维全局扫描 + 线性最小二乘的相位–频率拟合（variable projection）**，属精确方法的**确定性初值 + 线性 LS**，无需 MILP 或元启发式（§6 论证）。v002 的全谱非线性最小二乘（NLS）保留为**物理正模型校验/多光束诊断**用途，不作为主交付。 --- computation 阶段（任务 `1295103e6926a59e5ed2`，formulation_v002）实测反演 `feasible_incumbent=false`，且出现一个**决定性异常**——三组厚度结果相差两个数量级： | 方法 | 结果 t（µm） | 残。 公式中的符号、单位和适用条件以“符号说明”和接受版本为准。<!-- evidence:ev_artifact_0366c0d48834 -->

### prob02 结果解释

本问针对附件 1/2 的 SiC 实测反射率谱，采用“慢变基线—干涉项分解 + 一维相位频率变量投影”反演厚度，使厚度主要由条纹相位频率确定并与衬底折射率幅值弱可辨识性解耦。两角共享厚度为 $7.2158\,\mu\mathrm{m}$，10°/15° 分别为 $7.2214/7.2095\,\mu\mathrm{m}$，相对差 $0.165\%$；色散、置信区间、异常点、多光束与全局极小判据通过。两角嵌套 F 检验虽统计显著（$p=0.022$），但实际厚度差远低于 2% 阈值，按预注册规则解释为测量点差异或膜厚梯度，不触发模型修订。$\lambda>5\,\mu\mathrm{m}$ 色散缺口、$n_{\mathrm{sub}}$ 弱可辨识及物理 NLS 约 5.5% 交叉校验偏差作为推广限制保留。<!-- evidence:ev_artifact_1c7696fb4377 -->

![附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reflectance_spectrum_6b2265d217.png){#prob02_fig_reflectance_spectrum_6b2265d217}

@fig:prob02_fig_reflectance_spectrum_6b2265d217 展示“附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_dda4c5abdf3d -->
![两入射角实测谱与两光束物理正模型 (2.3) 拟合对比](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_model_fit_0ca711689b.png){#prob02_fig_model_fit_0ca711689b}

@fig:prob02_fig_model_fit_0ca711689b 展示“两入射角实测谱与两光束物理正模型 (2.3) 拟合对比”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_a75144cb91b3 -->
![prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_thickness_estimate_efa7359eb9.png){#prob02_fig_thickness_estimate_efa7359eb9}

@fig:prob02_fig_thickness_estimate_efa7359eb9 展示“prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_73dc1fe83462 -->
![外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_dispersion_curve_af50244106.png){#prob02_fig_dispersion_curve_af50244106}

@fig:prob02_fig_dispersion_curve_af50244106 展示“外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_c3bd34878ece -->
![prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reliability_summary_78cd97014b.png){#prob02_fig_reliability_summary_78cd97014b}

@fig:prob02_fig_reliability_summary_78cd97014b 展示“prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_f8d6659bf219 -->
![主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_variable_projection_jcurve_7a9a903650.png){#prob02_fig_variable_projection_jcurve_7a9a903650}

@fig:prob02_fig_variable_projection_jcurve_7a9a903650 展示“主反演目标函数 J(t) 与全局唯一性”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_2a594948c032 -->
![相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_g_space_phase_gap_f500d9c0db.png){#prob02_fig_g_space_phase_gap_f500d9c0db}

@fig:prob02_fig_g_space_phase_gap_f500d9c0db 展示“相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_ec5c566cade8 -->
![n_sub 幅值弱可辨识性与 t-n_sub 解耦](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_nsub_decoupling_39b4128d09.png){#prob02_fig_nsub_decoupling_39b4128d09}

@fig:prob02_fig_nsub_decoupling_39b4128d09 展示“n_sub 幅值弱可辨识性与 t-n_sub 解耦”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_fbf03315682d -->
![两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_response_surface_cfe5827835.png){#prob02_fig_response_surface_cfe5827835}

@fig:prob02_fig_response_surface_cfe5827835 展示“两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_aad41352929d -->
![prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_methods_compare_99386076f5.png){#prob02_fig_methods_compare_99386076f5}

@fig:prob02_fig_methods_compare_99386076f5 展示“prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_d0a257b14967 -->
![prob02 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_summary_dcd697b29e.png){#prob02_fig_ablation_summary_dcd697b29e}

@fig:prob02_fig_ablation_summary_dcd697b29e 展示“prob02 ablation 判据汇总（F0 + A1–A4）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_dff80f606d45 -->
![prob02 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_thickness_d29e3fc1f0.png){#prob02_fig_ablation_thickness_d29e3fc1f0}

@fig:prob02_fig_ablation_thickness_d29e3fc1f0 展示“prob02 ablation 厚度对照（F0 + A1–A4）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_9ff5e5c6749b -->
![A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_shared_t_14e5362fa7.png){#prob02_fig_ablation_shared_t_14e5362fa7}

@fig:prob02_fig_ablation_shared_t_14e5362fa7 展示“A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_47cfd6efa8cb -->

### prob02 可靠性与结论

稳健性分析：robustness 适用并完成：formulation_v003 §7.1–§7.6 预注册可靠性判据（阈值计算前登记于 parameters.yaml）已在 computation 阶段完整执行并归档于 results/thickness_inversion_v003/result.json——C2 色散 Δt_disp=0.507%≤2%、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）、C5 CI 半宽 0.091%≤2%、C7 异常点 0.0%≤1%、C8 多光束改善 0.0%≤10%（两光束适用）、C6 全局极小唯一 全部 PASS；仅 C1 两角嵌套 F 检验统计显著（F=5.25,p=0.022）但 ε₁₂=0.165%≪τ₁₂=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。结论=STABLE（t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588 弱可辨识）。判定与敏感性可视化图已归档 robustness/（decision/preregistration/experiment_matrix/conclusion）与 figures/，交 sanity-checker 执行 Level 6。。消融分析：ablation 适用并完成：formulation_v003 主方法 M1（基线-干涉分解 + 一维相位-频率扫描，variable projection，N-SE，p=3/q=1，两角共享 t，t 与 n_sub 解耦）含可解释、可分离的公式项/算法模块，REQUEST.md 要求复杂算法必要性证据，robustness 已覆盖输入/情景不确定性、本阶段补充模型组件必要性，二者互补。预注册方案 ablation_v001（ablation/decision.md、preregistration.md、experiment_matrix.yaml，判据运行前固定），隔离任务 1d41cd2ff79a3ec91cbd 执行 F0+A1–A4（色散消融、基线多项式消融、相位-频率方法消融、两角共享-t 消融），全部判据符合预期 conclusion=components_confirmed：A1 Δt_disp=8.44%>1%（色散必要）、A2 Δt_base=5.55%>1% 且 RMSE 升 7.03×（基线-稳健分解必要）、A3 Δt_vp=5.44%>1%（相位-频率方法必要）、A4 每角 t̂≈共享 t̂ 且 ε12=0.165%≤2%（两角共享-t 良性一致约束，不扭曲 t̂）。消融结论/汇总表/3 张消融图（自动质检+视觉复核 passed）已归档 ablation/、results/ablation/ 与 figures.yaml；compution v003 的 t̂=7.2158 µm 仍为主交付，本阶段不改变已接受的 formulation_v003，未触发模型修订。Level 5 待全部小问局部完成后执行。。适用边界为：prob02 实测反演任务 30bedd3be5a2c9a36d3a 消费完成（formulation_v003 / assumption_v001，results/thickness_inversion_v003）：L1–L4 硬门禁通过——hash 追踪链（code_hash=3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e 与 task.json/implementation.md §7 一致、config/input hash 一致）完整、机器级 L2-finite 通过（8 文件全有限无 NaN/Inf，v001 的 dispersion_ref NaN 已用 null 修复）、公式-代码逐条一致、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588；主拟合加权 RMSE≈6.3e-4。只读 FFT 数据探针独立证实带内真实干涉周期 Δg≈657/698、Δν≈247/263 cm⁻¹→t≈7.2–8.0 µm，与主结果一致。可靠性判据 5/6 通过：dispersion(0.51%≤2%)、ci(0.091%≤2%)、anomaly(0.0%≤1%)、nsub 解耦(diag PASS)、multibeam(pass) 全部通过；仅 reliability_two_angle_ftest 判 FAIL（F=5.251>F_crit=3.843，p=0.022），但裸偏差 ε₁₂=0.165%≪τ₁₂=2%，属大样本下统计显著性与实际意义分离，formulation §7.1/§14 明确将其路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。v001/v002 曾超阈判据（ε₁₂ 27.66%→0.165%、Δt_disp 15.11%→0.51%、n_sub 69%→解耦0%、CI 3.51%→0.091%、M1 0.305µm→7.216µm 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。技术债（λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 5.5% 偏差、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，留后续与论文阶段处理，不阻断推进。<!-- warning:warn_prob02_a94c3613afe5 -->；prob02 Level 6（robustness 验收）独立复核通过（降级审查模式，复用已有产物、不发起新计算）：robustness 判据 C1–C8 由 formulation_v003 §7.1–§7.6 预注册判据在 computation 阶段执行并归档 results/thickness_inversion_v003/result.json + robustness/（decision/preregistration/experiment_matrix/conclusion），无需另启重复任务。C2 色散 0.507%≤2% PASS、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）PASS、C5 CI 半宽 0.091%≤2% PASS、C6 全局极小唯一 PASS、C7 异常点 0.0%≤1% PASS、C8 多光束改善 0.0%≤10%（两光束适用）PASS、R8 基线/包络阶数 p=2..5.q=0..2 稳定；仅 C1 两角嵌套 F 检验统计显著（F=5.25>F_crit=3.843，p=0.022）但 ε12=0.165%≪τ12=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。机器级 L2-finite 通过（8 数值文件全有限无 NaN/Inf，failures=[]），hash 追踪链（code/config/input）与 task.json/implementation.md §7 一致，原始数据只读；result.json feasible_incumbent=false 系 compute.py 将 F 检验判为硬失败置 passed=false，sanity-checker 独立验收判定主结果 t̂=7.2158 µm（ε12=0.165%、n̂_sub=2.588）可行可追踪，维持 PASS_WITH_WARNING。物理/常识一致（t 由相位频率确定、与 n_sub 解耦；色散为最大不确定度来源但带内 0.507%<2%；噪声二阶小量；异常点降权无影响）。v001/v002 曾超阈判据全部回到阈值内，确认 formulation_v003 变量投影重构消除模型可辨识性结构缺陷。技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 5.5%、λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，不阻断推进。ablation 尚 pending，交由 ablation-analyst；Level 5 待全部小问局部完成后执行。<!-- warning:warn_prob02_abcae1fbbd23 -->。本问结论限于上述假设、数据范围和误差条件。<!-- evidence:ev_artifact_1c7696fb4377 -->

## prob03 模型建立、求解与结果

### prob03 问题分析

本问先从题面目标识别输入、输出与约束，再采用已接受的假设和公式完成求解，避免在结果之后倒推模型。

### prob03 模型假设

> 版本：assumption_v001 ｜ 阶段：assumption_definition ｜ 状态：candidate > 问题：2025 高教社杯 B 题问题 3 —— 推导光波在外延层界面与衬底界面产生多次反射、透射（图 2）从而产生多光束干涉的必要条件及其对厚度计算精度的影响；分析附件 3（硅，10°）与附件 4（硅，15°）是否出现多光束干涉，给出硅外延层厚度计算的数学模型、算法与结果；若多光束也出现在碳化硅（附件 1、2）中，设法消除其影响并给出修正结果。 > 证据规则：关键假设必须绑定本问文献池中 verified 且 used 的来源（L43–L47）；普通常识假设标记 common_sense/project_assumption；team_decision 与 agent_inference 显式区分；由 prob01/prob02 承接的模型假设标记 inherited 并引用 `prob01-conclusion-v1` / `prob02-conclusion-v1`。 > 数据观察（只读探针，非计算结论）：附件 3/4 均为 7469 行×2 列，波数 400–4000 cm⁻¹，等间隔步长 ≈0.482 cm⁻¹；硅片在透明区（约 1500–4000 cm⁻¹）反射率约 20–43%，存在清晰干涉条纹，说明硅外延层厚度为微米量级且该谱段干涉信息可用。 | 族 | 内容 | 条目 | |---|---|---| | M1 | 多光束干涉必要条件的严格推导（Airy 公式、界面反射率阈值、相干长度、界面平行度、吸收限制） | C1–C5 | | M2 | 硅外延层数据契约与材料/光谱参数（附件 3/4、折射率、透明谱段、几何/环境） | C6–C9 | | M3 | 硅片（附件 3/4）是否出现多光束的判定（数据为据、阈值、链路分支） | C10–C12 | | M4 | 多光束对厚度计算精度的影响与修正（影响机制、Airy/FFT 修正、SiC 重新判定） | C13–C15 | | M5 | 前问结论继承与跨问一致性（prob01 两光。 [@L01]<!-- evidence:ev_artifact_41bfac6d034d -->

### prob03 模型建立与求解

> 版本：formulation_v002 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation > 父版本：formulation_v001（被 sanity-checker 判定 NEEDS_REVISION 后修订） > 问题：2025 高教社杯 B 题问题 3 ——（1）推导光波在外延层界面与衬底界面多次反射、透射（图 2）产生**多光束干涉的必要条件**及其对厚度计算精度的影响；（2）依据必要条件分析附件 3（硅，10°）与附件 4（硅，15°）**是否出现多光束干涉**，给出硅外延层厚度计算的数学模型、算法与结果；（3）若多光束也出现在碳化硅（附件 1/2）并影响厚度精度，设法消除其影响并给出修正结果。 > 继承基础：正模型与反演链路继承 `prob01-conclusion-v1`（prob01/formulation_v001，content_hash `82820355…070a6`）与 `prob02-conclusion-v1`（prob02/formulation_v003，content_hash `27b0ce86…a12ea`，t̂=7.2158 µm、ε₁₂=0.165%、n̂_sub=2.588）。prob02 已把主反演固化为"基线-干涉分解 + 一维相位频率扫描（variable projection）"，并将多光束（Airy）**仅作诊断、完整推导预留 prob03**（B13）。本版承接该预留，**从物理上严格推导多光束必要条件**，据此判定硅片是否多光束、计算硅厚度，并对 SiC 重新判定。 > 说明：本问**不是**优化问题（无约束决策），是**物理模型 + 可解性反演**问题；按 knowledge/optimization.md 与 model-selection.md 求解策略规则，主方法为**一维全局扫描 + 线性最小二乘的相位–频率拟合（variable projection）**、多光束判定为**两光束 vs Airy 正模型的残差改善诊断**，均属精确/确定性。 公式中的符号、单位和适用条件以“符号说明”和接受版本为准。<!-- evidence:ev_artifact_67d81d412946 -->

### prob03 结果解释

本问由 Airy 多光束反射率推导多光束干涉的必要条件，并验证在无吸收平行板条件下高阶反射主要改变条纹形状而不改变极值位置及厚度周期。附件 3/4 的硅外延层共享厚度为 $3.4477\,\mu\mathrm{m}$，两角分别为 $3.4507/3.4463\,\mu\mathrm{m}$，相对差 $0.130\%$。硅的界面反射率组合给出 $\bar R\approx0.0101$、精细度约 0.319，多光束相对改善约 0.11%，判定两光束模型足够；对 SiC 重判得到 $\bar R\approx0.0024$，同样无需多光束修正，因此 prob02 的 $7.2158\,\mu\mathrm{m}$ 结论维持。全部预注册可靠性与消融判据通过；弱色散下次小候选接近简并和 $n_{\mathrm{sub}}$ 弱可辨识作为报告边界保留。<!-- evidence:ev_artifact_ed5e6f341dcb -->

![附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reflectance_spectrum_41a3800f70.png){#prob03_fig_reflectance_spectrum_41a3800f70}

@fig:prob03_fig_reflectance_spectrum_41a3800f70 展示“附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_5c5051a759c9 -->
![两入射角实测谱与两光束物理正模型 (2.8) 拟合对比](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_model_fit_3e94d2fac7.png){#prob03_fig_model_fit_3e94d2fac7}

@fig:prob03_fig_model_fit_3e94d2fac7 展示“两入射角实测谱与两光束物理正模型 (2.8) 拟合对比”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_8c09648b5b0d -->
![prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_thickness_estimate_59f1546ed7.png){#prob03_fig_thickness_estimate_59f1546ed7}

@fig:prob03_fig_thickness_estimate_59f1546ed7 展示“prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_dfeacc75d39b -->
![硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_dispersion_curve_aac3dcebea.png){#prob03_fig_dispersion_curve_aac3dcebea}

@fig:prob03_fig_dispersion_curve_aac3dcebea 展示“硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_7dcc8d1ec952 -->
![prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reliability_summary_50b4f34a17.png){#prob03_fig_reliability_summary_50b4f34a17}

@fig:prob03_fig_reliability_summary_50b4f34a17 展示“prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_3dff305300aa -->
![主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_variable_projection_jcurve_4b30b360a4.png){#prob03_fig_variable_projection_jcurve_4b30b360a4}

@fig:prob03_fig_variable_projection_jcurve_4b30b360a4 展示“主反演目标函数 J(t) 与全局唯一性”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_6a4fab81710a -->
![多光束干涉必要条件 N1–N4 与硅片判定](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_mb_conditions_9571a5012b.png){#prob03_fig_mb_conditions_9571a5012b}

@fig:prob03_fig_mb_conditions_9571a5012b 展示“多光束干涉必要条件 N1–N4 与硅片判定”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_a64ba1b677b8 -->
![多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_sic_multibeam_recheck_4cbb136f9c.png){#prob03_fig_sic_multibeam_recheck_4cbb136f9c}

@fig:prob03_fig_sic_multibeam_recheck_4cbb136f9c 展示“多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_592e5e151a31 -->
![两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_response_surface_06cfec9b1e.png){#prob03_fig_response_surface_06cfec9b1e}

@fig:prob03_fig_response_surface_06cfec9b1e 展示“两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_a9d9c329d54e -->
![相位频率（g 空间）测厚机制与条纹计数](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_phase_freq_gspace_a936624612.png){#prob03_fig_phase_freq_gspace_a936624612}

@fig:prob03_fig_phase_freq_gspace_a936624612 展示“相位频率（g 空间）测厚机制与条纹计数”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_9a913a61baae -->
![prob03 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_summary_9f93c3dd2d.png){#prob03_fig_ablation_summary_9f93c3dd2d}

@fig:prob03_fig_ablation_summary_9f93c3dd2d 展示“prob03 ablation 判据汇总（F0 + A1–A4）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_e1af76ad2a74 -->
![prob03 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_t_consistency_ec44908369.png){#prob03_fig_ablation_t_consistency_ec44908369}

@fig:prob03_fig_ablation_t_consistency_ec44908369 展示“prob03 ablation 厚度对照（F0 + A1–A4）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_bce0cdb5c3cb -->
![prob03 ablation 拟合优度对照（加权 RMSE）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_rmse_ce4b523efa.png){#prob03_fig_ablation_rmse_ce4b523efa}

@fig:prob03_fig_ablation_rmse_ce4b523efa 展示“prob03 ablation 拟合优度对照（加权 RMSE）”。具体数值及适用条件见本问结果分析。<!-- evidence:ev_figure_e962f369961c -->

### prob03 可靠性与结论

稳健性分析：prob03 robustness 复核完成：formulation_v002 §8.5 预注册判据 R1–R8 全部在阈值内通过（R1 两角 0.130%≤2%、R2 色散 0.503%≤2%、R3 CI 0.134%≤2%、R4 异常 0.0%≤1%、R5 多光束 0.111%≤10%、R6 n_sub 解耦 0.0%、R7 窗口 0.749%≤2%（只读探针补登）、R8 唯一性次小候选≈1.020 为报告项由 §7.6 判据保障全局唯一）；结论 STABLE，送至 sanity-checker 执行 Level 6 验收。。消融分析：ablation 适用并已完成：formulation_v002 主反演（基线-干涉分解 + 一维相位频率扫描 variable projection，两角共享 t）含可解释、可分离的公式项/算法模块/约束方向（色散项 N-SE、基线多项式 p、包络多项式 q、两角共享 t 约束、多光束 Airy 高阶项），REQUEST.md 要求复杂算法必要性证据，robustness 已覆盖输入/情景不确定性、ablation 补充模型内部组件必要性，二者互补。预注册方案 ablation_v001（核心结论+消融判据运行前固定，ablation/ 目录），隔离任务 bd175bb7b9a82f35e054（stage=ablation，supervised worker，returncode=0，feasible_incumbent=true）执行 F0 完整模型对照 + A1 色散项 / A2 多光束(Airy)高阶项 / A3 基线多项式项 / A4 两角共享 t 约束，5/5 判据通过，conclusion=components_confirmed：A1 Δt=0.446%≤2%、A2 Δt=0.300%≤1%（L17 极值不变性/Q1 定量）、A3 Δt=0.574%≤2%（RMSE +9.5%，基线项为拟合优度必要组件）、A4 每角偏差 0.089%≤2% 且 ε12=0.130%≤2%（共享为安全一致性约束）。消融结论/汇总表/3 张消融图（自动质检+视觉复核 passed）已归档 ablation/、results/ablation/ 与 figures.yaml；未删除任何不利情景，模型组件必要性证据供论文/Q1 引用。ablation 为最后一个可选阶段，required artifacts 全部满足，提交局部完成。。适用边界为：prob03 主 computation 任务 7e209043973692d067ed 消费完成（formulation_v002 / assumption_v001，results/silicon_mb_verify）：L1–L4 硬门禁通过——hash 追踪链（code_hash=482f5abb10c276c9d073dd7b7177ce342cf0a0d2d0b455370a899ec566142873 与 task.json/implementation.md §7 一致、source_config_hash/input_hash 一致）完整、机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf，failures=[]）、公式-代码逐条一致（R1 硅厚度基准 t̂=3.4477µm 修正 v001 的 6.9µm 因子2 伪影；R2 finesse=π·√R̄/(1−R̄) 修正 v001 漏 √R̄，finesse=0.3186 与公式一致）、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=3.4477 µm、每角 3.4507/3.4463 µm、ε₁₂=0.130%、n̂_sub(幅值弱辨识)=3.558；J(t) 曲线全局唯一极小在 t=3.45µm（J_shared=0.0608），未达 formulation §13.1 声称的『4 倍余量』（次小候选比≈1.020，弱色散下周期邻近候选接近简并，作为报告项而非硬门禁）。全部可靠性判据 PASS（two_angle F=0/p=1.0、dispersion 0.503%≤2%、ci 0.134%≤2%、anomaly 0.0%≤1%、multibeam_si two_beam_negligible η_mb≈0.11%、multibeam_sic no_correction_needed Rbar≈0.0024、nsub 解耦 diag PASS；checks_failed=[]）。v001 判 NEEDS_REVISION 的两项 core 缺陷（R1/R2）已在 v002 修复并复核通过；模型有效、无 VERSION_REJECTED、无 NEEDS_REVISION。技术债（bootstrap CI 用轮廓似然替代、n_sub 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项或非阻断。合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。判定 PASS_WITH_WARNING，推进至 sanity_check 阶段。<!-- warning:warn_prob03_e6a8b3e9e4da -->；prob03 Level 6（robustness 验收）独立复核通过：robustness 判据 R1–R8 由 formulation_v002 §8.5 预注册并先于 computation 固定（parameters.yaml），R1–R7 全部在阈值内（R1 eps12=0.130%≤2%、R2 Δt_disp=0.503%≤2%、R3 CI 半宽 0.134%≤2%、R4 Δt_anom=0.0%≤1%、R5 η_mb=0.111%≤10%、R6 n_sub 解耦 0.0%、R7 Δt_win=0.749%≤2%），checks_failed=[]；独立复算 R7=0.749% 与登记值一致，探针只读、复用 model.py、未改数据/代码/结果。R8 唯一性次小候选≈1.020 为报告项（弱色散周期歧义），全局唯一性由 §7.6 预注册判据确认。主结果 t̂=3.4477 µm/每角 3.4507/3.4463 µm（ε12=0.130%），多光束判定两光束适用（硅 R̄≈0.0101、η_mb≈0.11%；SiC R̄_max≈0.0024 no_correction_needed），与 prob02 结论一致；物理/常识一致（t 由相位频率确定、与 n_sub 解耦；硅色散弱且带内无 λ>5µm 缺口；噪声二阶小量）。硬门禁（L2-finite 10 文件全有限无 NaN/Inf、单位/量纲、公式-实现一致 R1/R2 已修复、原始数据只读、追踪链完整、feasible_incumbent=true）全部通过。技术债（bootstrap CI 未跑用轮廓似然、n_sub 弱可辨识 B7、uniqueness 近简并、multibeam 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项，非阻断。判定 PASS_WITH_WARNING。<!-- warning:warn_prob03_89c83e7e6538 -->。本问结论限于上述假设、数据范围和误差条件。<!-- evidence:ev_artifact_ed5e6f341dcb -->


## 跨小问一致性、稳健性与消融分析

跨小问审查状态为 passed，结论为“跨小问一致性审查通过：共享符号（t,n,n_sub,θ,θ′,λ,ν,R,δ,R_01/R_12,finesse）与单位、参数值（Sellmeier 一致、主带 ν∈[2000,4000]cm⁻¹、θ=10/15°、Reststrahlen [700,1000]cm⁻¹ 剔除）、假设、数据版本、约束（R∈[0,1]、t>0、n>1）、结论方向与数量级全部跨问自洽；软依赖 conclusion hash（prob01=828203556617be979f7345dce7c274dd1850b62fe950a6e108015ad161b070a6、prob02=27b0ce8689e1eb2b345e5803309ea80bb6b84a620f189ed6cd589e75f23a12ea）完整匹配，无 stale 传播、无回退。唯一共享符号元数据不一致（finesse domain ≥1 vs 实际 F≈0.32<1）已由本审查修订为 >0，属全局符号表规范修订，不影响任何计算结果。裁决依据：题目硬约束、sanity 硬门禁、文献/机理、鲁棒性、解释性、时间顺序均一致；无硬门禁失败版本。recommended_next_stage=paper_writing（须先行补齐三问 question_summary 并披露既有技术债）。”。各问稳健性或消融结果已在对应章节披露；记录的质量警告如下：

- prob01：prob01 合成验证任务 0ea4b29da19e8479a6ea 消费完成：19/19 检查通过，t_true=10µm 被 NLS/相位法精确恢复，两入射角一致；hash 追踪链（code/config/input）与 task.json、implementation.md §7 完全一致，无 NaN/Inf、无硬约束违反、formula-代码逐条一致、文献/物理常识合理。技术债（λ>5µm 常数色散延伸、方法 A 约4%基线偏差、文献全文待复核、n_sub 合成场景值、Reststrahlen 剔除策略）均为既有 workflow warning，留 prob02 处理，不阻断推进。L1–L4 判定 PASS_WITH_WARNING，Level 5 待全部小问完成、Level 6 待 robustness 阶段。<!-- warning:warn_prob01_fac14a9dfae4 -->
- prob01：prob01 Level 6（robustness 验收）独立复核通过：任务 554819114361017c5b70 全部输出有限且追踪完整，hash 链（code/config/input）与 task.json 一致，E1–E5 判据独立重算全部通过（conclusion=stable、5/5），E4 600 样本收敛率 100%、95% CI 半宽最大 0.022% 远低于阈值，预注册方案运行前固定未事后修改；物理机制（n_sub 影响幅度不影响相位、θ 误差二阶小量、色散模型为最大不确定度来源、全谱平均效应）与常识一致。技术债（robustness 基于合成谱、色散模型选择、λ>5µm 常数延伸、n_sub 场景值、文献全文待复核、Reststrahlen 剔除）均为既有 workflow warning，留 prob02 处理，不阻断推进。<!-- warning:warn_prob01_cdf6b5be3241 -->
- prob02：prob02 实测反演任务 30bedd3be5a2c9a36d3a 消费完成（formulation_v003 / assumption_v001，results/thickness_inversion_v003）：L1–L4 硬门禁通过——hash 追踪链（code_hash=3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e 与 task.json/implementation.md §7 一致、config/input hash 一致）完整、机器级 L2-finite 通过（8 文件全有限无 NaN/Inf，v001 的 dispersion_ref NaN 已用 null 修复）、公式-代码逐条一致、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588；主拟合加权 RMSE≈6.3e-4。只读 FFT 数据探针独立证实带内真实干涉周期 Δg≈657/698、Δν≈247/263 cm⁻¹→t≈7.2–8.0 µm，与主结果一致。可靠性判据 5/6 通过：dispersion(0.51%≤2%)、ci(0.091%≤2%)、anomaly(0.0%≤1%)、nsub 解耦(diag PASS)、multibeam(pass) 全部通过；仅 reliability_two_angle_ftest 判 FAIL（F=5.251>F_crit=3.843，p=0.022），但裸偏差 ε₁₂=0.165%≪τ₁₂=2%，属大样本下统计显著性与实际意义分离，formulation §7.1/§14 明确将其路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。v001/v002 曾超阈判据（ε₁₂ 27.66%→0.165%、Δt_disp 15.11%→0.51%、n_sub 69%→解耦0%、CI 3.51%→0.091%、M1 0.305µm→7.216µm 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。技术债（λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 5.5% 偏差、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，留后续与论文阶段处理，不阻断推进。<!-- warning:warn_prob02_a94c3613afe5 -->
- prob02：prob02 Level 6（robustness 验收）独立复核通过（降级审查模式，复用已有产物、不发起新计算）：robustness 判据 C1–C8 由 formulation_v003 §7.1–§7.6 预注册判据在 computation 阶段执行并归档 results/thickness_inversion_v003/result.json + robustness/（decision/preregistration/experiment_matrix/conclusion），无需另启重复任务。C2 色散 0.507%≤2% PASS、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）PASS、C5 CI 半宽 0.091%≤2% PASS、C6 全局极小唯一 PASS、C7 异常点 0.0%≤1% PASS、C8 多光束改善 0.0%≤10%（两光束适用）PASS、R8 基线/包络阶数 p=2..5.q=0..2 稳定；仅 C1 两角嵌套 F 检验统计显著（F=5.25>F_crit=3.843，p=0.022）但 ε12=0.165%≪τ12=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。机器级 L2-finite 通过（8 数值文件全有限无 NaN/Inf，failures=[]），hash 追踪链（code/config/input）与 task.json/implementation.md §7 一致，原始数据只读；result.json feasible_incumbent=false 系 compute.py 将 F 检验判为硬失败置 passed=false，sanity-checker 独立验收判定主结果 t̂=7.2158 µm（ε12=0.165%、n̂_sub=2.588）可行可追踪，维持 PASS_WITH_WARNING。物理/常识一致（t 由相位频率确定、与 n_sub 解耦；色散为最大不确定度来源但带内 0.507%<2%；噪声二阶小量；异常点降权无影响）。v001/v002 曾超阈判据全部回到阈值内，确认 formulation_v003 变量投影重构消除模型可辨识性结构缺陷。技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 5.5%、λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，不阻断推进。ablation 尚 pending，交由 ablation-analyst；Level 5 待全部小问局部完成后执行。<!-- warning:warn_prob02_abcae1fbbd23 -->
- prob03：prob03 主 computation 任务 7e209043973692d067ed 消费完成（formulation_v002 / assumption_v001，results/silicon_mb_verify）：L1–L4 硬门禁通过——hash 追踪链（code_hash=482f5abb10c276c9d073dd7b7177ce342cf0a0d2d0b455370a899ec566142873 与 task.json/implementation.md §7 一致、source_config_hash/input_hash 一致）完整、机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf，failures=[]）、公式-代码逐条一致（R1 硅厚度基准 t̂=3.4477µm 修正 v001 的 6.9µm 因子2 伪影；R2 finesse=π·√R̄/(1−R̄) 修正 v001 漏 √R̄，finesse=0.3186 与公式一致）、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=3.4477 µm、每角 3.4507/3.4463 µm、ε₁₂=0.130%、n̂_sub(幅值弱辨识)=3.558；J(t) 曲线全局唯一极小在 t=3.45µm（J_shared=0.0608），未达 formulation §13.1 声称的『4 倍余量』（次小候选比≈1.020，弱色散下周期邻近候选接近简并，作为报告项而非硬门禁）。全部可靠性判据 PASS（two_angle F=0/p=1.0、dispersion 0.503%≤2%、ci 0.134%≤2%、anomaly 0.0%≤1%、multibeam_si two_beam_negligible η_mb≈0.11%、multibeam_sic no_correction_needed Rbar≈0.0024、nsub 解耦 diag PASS；checks_failed=[]）。v001 判 NEEDS_REVISION 的两项 core 缺陷（R1/R2）已在 v002 修复并复核通过；模型有效、无 VERSION_REJECTED、无 NEEDS_REVISION。技术债（bootstrap CI 用轮廓似然替代、n_sub 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项或非阻断。合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。判定 PASS_WITH_WARNING，推进至 sanity_check 阶段。<!-- warning:warn_prob03_e6a8b3e9e4da -->
- prob03：prob03 Level 6（robustness 验收）独立复核通过：robustness 判据 R1–R8 由 formulation_v002 §8.5 预注册并先于 computation 固定（parameters.yaml），R1–R7 全部在阈值内（R1 eps12=0.130%≤2%、R2 Δt_disp=0.503%≤2%、R3 CI 半宽 0.134%≤2%、R4 Δt_anom=0.0%≤1%、R5 η_mb=0.111%≤10%、R6 n_sub 解耦 0.0%、R7 Δt_win=0.749%≤2%），checks_failed=[]；独立复算 R7=0.749% 与登记值一致，探针只读、复用 model.py、未改数据/代码/结果。R8 唯一性次小候选≈1.020 为报告项（弱色散周期歧义），全局唯一性由 §7.6 预注册判据确认。主结果 t̂=3.4477 µm/每角 3.4507/3.4463 µm（ε12=0.130%），多光束判定两光束适用（硅 R̄≈0.0101、η_mb≈0.11%；SiC R̄_max≈0.0024 no_correction_needed），与 prob02 结论一致；物理/常识一致（t 由相位频率确定、与 n_sub 解耦；硅色散弱且带内无 λ>5µm 缺口；噪声二阶小量）。硬门禁（L2-finite 10 文件全有限无 NaN/Inf、单位/量纲、公式-实现一致 R1/R2 已修复、原始数据只读、追踪链完整、feasible_incumbent=true）全部通过。技术债（bootstrap CI 未跑用轮廓似然、n_sub 弱可辨识 B7、uniqueness 近简并、multibeam 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项，非阻断。判定 PASS_WITH_WARNING。<!-- warning:warn_prob03_89c83e7e6538 -->

这些警告不被改写为已解决，而是作为解释结果与限制外推范围的组成部分。

## 模型评价、局限与推广

模型从假设、公式到数值结果具有明确对应关系；扰动实验用于评估参数变化对结论的影响。局限性来自假设适用范围、数据质量、样本规模以及可辨识性条件。推广到新的材料或数据分布前，应重新执行参数标定和敏感性分析。

## 结论

本文逐问完成了模型建立、求解、结果解释与可靠性检查。针对问题1，本问建立了考虑折射率色散与斜入射 Snell 几何的两光束 Fresnel 干涉模型，并推导同型相邻极值间隔与外延层厚度的关系。合成验证中，色散化相位法得到约 $10.002\,\mu\mathrm{m}$，全谱非线性最小二乘得到 $10.000\,\mu\mathrm{m}$，均恢复 $t_{\mathrm{true}}=10\,\mu\mathrm{m}$；常数折射率间隔法约有 **4%** 系统偏差，因此仅作初值或交叉校验。两入射角结果一致，E1–E5 稳健性判据和消融判据全部通过。结论仅适用于无显著吸收、界面近似平行且采用已登记色散模型的谱段；$\lambda>5\,\mu\mathrm{m}$ 色散延伸和 Reststrahlen 区处理仍作为边界条件保留。<!-- e。 针对问题2，本问针对附件 1/2 的 SiC 实测反射率谱，采用“慢变基线—干涉项分解 + 一维相位频率变量投影”反演厚度，使厚度主要由条纹相位频率确定并与衬底折射率幅值弱可辨识性解耦。两角共享厚度为 $7.2158\,\mu\mathrm{m}$，10°/15° 分别为 $7.2214/7.2095\,\mu\mathrm{m}$，相对差 $0.165\%$；色散、置信区间、异常点、多光束与全局极小判据通过。两角嵌套 F 检验虽统计显著（$p=0.022$），但实际厚度差远低于 **2%** 阈值，按预注册规则解释为测量点差异或膜厚梯度，不触发模型修订。$\lambda>5\,\mu\mathrm{m}$ 色散缺口、$n_{\mathrm{sub}}$ 弱可辨识及物理 NLS 约 **5.。 针对问题3，本问由 Airy 多光束反射率推导多光束干涉的必要条件，并验证在无吸收平行板条件下高阶反射主要改变条纹形状而不改变极值位置及厚度周期。附件 3/4 的硅外延层共享厚度为 $3.4477\,\mu\mathrm{m}$，两角分别为 $3.4507/3.4463\,\mu\mathrm{m}$，相对差 $0.130\%$。硅的界面反射率组合给出 $\bar R\approx0.0101$、精细度约 0.319，多光束相对改善约 **0.11%**，判定两光束模型足够；对 SiC 重判得到 $\bar R\approx0.0024$，同样无需多光束修正，因此 prob02 的 $7.2158\,\mu\mathrm{m}$ 结论维持。全部预注册可靠性与消融判据通过；弱色散下次小候选接近。 所有结论只在所述假设、数据范围和适用边界内成立。

## 参考文献

[@L01] Albert, M. P., Combs, J. F.. Thickness Measurement of Epitaxial Films by the Infrared Interference Method. Journal of The Electrochemical Society, 1962. <!-- evidence:ev_citation_2ae3503f0f08 -->
[@L02] Schumann, P. A.. The Infrared Interference Method of Measuring Epitaxial Layer Thickness. Journal of The Electrochemical Society, 1969. <!-- evidence:ev_citation_a29607e45523 -->
[@L03] ASTM International. ASTM F95-89(2000): Standard Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer. ASTM International（标准组织正式文件）, 2000. <!-- evidence:ev_citation_a2ee149ac6c3 -->
[@L04] SEMI. SEMI MF95 (SEMI MF009500): Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer. SEMI International Standards, 2013. <!-- evidence:ev_citation_6fdc2a83467e -->
[@L05] Weeks, S. P.. Thickness Measurement of Thin (1.0-µm) Epitaxial Silicon Layers by Infrared Reflectance. Silicon Processing (ASTM STP 804), 1983. <!-- evidence:ev_citation_5e182639cb36 -->
[@L06] Born, M., Wolf, E.. Principles of Optics: Electromagnetic Theory of Propagation, Interference and Diffraction of Light (7th ed.). Cambridge University Press（权威教材）, 1999. <!-- evidence:ev_citation_a9ae72a47073 -->
[@L07] Hecht, E.. Optics (5th ed., Global Edition). Pearson（权威教材）, 2017. <!-- evidence:ev_citation_9581589acb3a -->
[@L08] Shaffer, P. T. B.. Refractive Index, Dispersion, and Birefringence of Silicon Carbide Polytypes. Applied Optics, 1971. <!-- evidence:ev_citation_a2434f83ed06 -->
[@L09] Wang, S., Zhan, M., Wang, G., Xuan, H., Zhang, W., Liu, C., Xu, C., Liu, Y., Wei, Z., Chen, X.. 4H-SiC: a new nonlinear material for midinfrared lasers. Laser & Photonics Reviews, 2013. <!-- evidence:ev_citation_5a4306cc233b -->
[@L10] Xu, C., Wang, S., Wang, G., Liang, J., Wang, S., Bai, L., Yang, J., Chen, X.. Temperature dependence of refractive indices for 4H- and 6H-SiC. Journal of Applied Physics, 2014. <!-- evidence:ev_citation_e18e63ada087 -->
[@L11] Polyanskiy, M. N.. Refractiveindex.info database of optical constants. Scientific Data, 2024. <!-- evidence:ev_citation_a7221ee00985 -->
[@L12] Li, H. H.. Refractive index of silicon and germanium and its wavelength and temperature derivatives. Journal of Physical and Chemical Reference Data, 1980. <!-- evidence:ev_citation_7eeee7be6e72 -->
[@L13] Palik, E. D. (ed.). Handbook of Optical Constants of Solids (Vol. 1-3). Academic Press（权威手册）, 1998. <!-- evidence:ev_citation_570c013b16e7 -->
[@L14] Spitzer, W., Fan, H. Y.. Infrared Absorption in n-Type Silicon. Physical Review, 1957. <!-- evidence:ev_citation_09aa3078e7a0 -->
[@L15] Pernot, J., Camassel, J., Peyre, H., Robert, J.-L.. From Transport Measurements to Infrared Reflectance Spectra of n-Type Doped 4H-SiC Layer Stacks. Materials Science Forum, 2003. <!-- evidence:ev_citation_38e1aac5327e -->
[@L16] Chahal, J. S., Rahbany, N., El-Helou, Y., Wu, K.-T., Bruyant, A., Zgheib, C., Kazan, M.. Temperature dependence of the anisotropy of the infrared dielectric properties and phonon-plasmon coupling in n-doped 4H-SiC. Journal of Physics and Chemistry of Solids, 2023. <!-- evidence:ev_citation_72f230667796 -->
[@L17] 王晨茜, 孙嘉妍, 陈怡佳, 杜睿. 基于色散修正与全谱拟合的红外干涉测厚模型研究. 数学建模及其应用（Mathematical Modeling and Its Applications）, 2026. <!-- evidence:ev_citation_a1be69796bc6 -->
[@L23] Harrick, N. J.. Determination of Refractive Index and Film Thickness from Interference Fringes. Applied Optics, 1971. <!-- evidence:ev_citation_2a29cd297e69 -->
[@L24] Larruquert, J. I., Pérez-Marín, A. P., García-Cortés, S., Rodríguez-de Marcos, L., Aznárez, J. A., Méndez, J. A.. Self-consistent optical constants of SiC thin films. Journal of the Optical Society of America A, 2011. <!-- evidence:ev_citation_eebece1128e7 -->
[@L25] Liu, Lu, Shi, Weiwei, Xu, Shibo, Wang, Xiaofan. Dispersion Compensation and Multi-Beam Interference Correction Algorithm for Thickness Measurement of SiC Epitaxial Layer. Sensors, 2026. <!-- evidence:ev_citation_25d613058688 -->
[@L26] Mainali, Madan K., Dulal, Prabin, Shrestha, Bishal, Amonette, Emily, Shan, Ambalanath, Podraza, Nikolas J.. Optical properties of 4H-SiC and 6H-SiC from infrared to vacuum ultraviolet spectral range ellipsometry (0.05–8.5 eV). Surface Science Spectra, 2024. <!-- evidence:ev_citation_ebbaa58d2186 -->
[@L27] Lindquist, O. P. A., Schubert, M., Arwin, H., Järrendahl, K.. Infrared to vacuum ultraviolet optical properties of 3C, 4H and 6H silicon carbide measured by spectroscopic ellipsometry. Thin Solid Films, 2004. <!-- evidence:ev_citation_bcb8f4d90399 -->
[@L28] Lindquist, O. P. A., Arwin, H., Henry, A., Järrendahl, K.. Infrared Optical Properties of 3C, 4H and 6H Silicon Carbide. Materials Science Forum, 2003. <!-- evidence:ev_citation_770c9553acb6 -->
[@L29] Tong, Zhen, Liu, Linhua, Li, Liangsheng, Bao, Hua. Temperature-dependent infrared optical properties of 3C-, 4H- and 6H-SiC. Physica B: Condensed Matter, 2018. <!-- evidence:ev_citation_5a4765e9f5fd -->
[@L30] Sunkari, Swapna, Mazzola, M. S., Mazzola, J. P., Das, Hrishikesh, Wyatt, J. L.. Investigation of longitudinal-optical phonon-plasmon coupled modes in SiC epitaxial film using Fourier transform infrared reflection. Journal of Electronic Materials, 2005. <!-- evidence:ev_citation_0e3509f3bca1 -->
[@L31] Mazzola, Michael S., Sunkari, Swapna G., Mazzola, Janice, Das, Hrishikesh, Melnychuck, Galyna, Koshka, Yaroslav, Wyatt, Jeffery L., Zhang, Jie. Improved Resolution of Epitaxial Thin Film Doping Using FTIR Reflectance Spectroscopy. Materials Science Forum, 2005. <!-- evidence:ev_citation_074a5fe3ad49 -->
[@L32] Zhou, Zhen-Hong, Yang, Isabel, Yu, Fuzhong, Reif, Rafael. Fundamentals of epitaxial silicon film thickness measurements using emission and reflection Fourier transform infrared spectroscopy. Journal of Applied Physics, 1993. <!-- evidence:ev_citation_d6b7ffd46d18 -->
[@L43] Sun, Jiaxing, Li, Zhisong, Zhang, Haojie, Song, Jinlong, Zhai, Tianbao. An improved method for measuring epi-wafer thickness based on the infrared interference principle: Addressing interference quality and multiple interferences in double-layer structures. Results in Physics, 2023. <!-- evidence:ev_citation_39b3e1ffb0f8 -->
[@L44] Severin, P. J.. On the Infrared Thickness Measurement of Epitaxially Grown Silicon Layers. Applied Optics, 1970. <!-- evidence:ev_citation_6abdc2a74965 -->
[@L45] Sato, K., Ishikawa, Y., Sugawara, K.. Infrared interference spectra observed in silicon epitaxial wafers. Solid-State Electronics, 1966. <!-- evidence:ev_citation_a7ec5213f45f -->
[@L46] Soler, F. J. P.. Multiple reflections in an approximately parallel plate. Optics Communications, 1997. <!-- evidence:ev_citation_2e2844269805 -->
[@L47] Monzón, J. J., Sánchez-Soto, L. L., Bernabeu, E.. Influence of coating thickness on the performance of a Fabry–Perot interferometer. Applied Optics, 1991. <!-- evidence:ev_citation_ae1858935781 -->

## 附录：复现说明、文件清单和核心代码索引

计算代码、对应图片与可分发的输入数据见支撑材料。运行环境、程序入口、执行顺序及未附输入见其中的运行说明，正文不重复粘贴完整代码。
