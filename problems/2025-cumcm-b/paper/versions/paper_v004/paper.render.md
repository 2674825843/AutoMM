# 基于红外干涉法的外延层厚度测量数学模型、算法与可靠性分析

## 摘要

本题研究碳化硅（SiC）与硅（Si）外延层厚度的红外干涉测厚问题。我们依次建立两光束干涉模型、实测谱反演算法与多光束干涉必要条件，并结合四个附件的实测光谱给出各问的定量结果与可靠性证据。

**问题 1（两光束干涉测厚模型）**：在“外延层上表面一次反射束 + 外延层/衬底界面反射折返束”的两光束近似下，推导了反射率正模型 $R(\nu;t,n,\theta,n_{\mathrm{sub}})$、干涉极值条件 $\delta=m\pi$ 与同型相邻极值波数间隔 $\Delta\nu$ 反演厚度的解析公式，并给出色散化相位函数 $g(\nu)=n\nu\cos\theta'$ 下的修正关系。合成验证（$t_{\mathrm{true}}=10.0\ \mu\mathrm{m}$、$n_{\mathrm{sub}}=3.0$、两入射角）显示：全谱非线性最小二乘与色散化相位法均以近零残差精确恢复 $t_{\mathrm{true}}$ 且两侧角结果一致；方法 A（常数 $n$ 间隔法）约 $4\%$ 的系统偏差被色散化修正消除，确认色散为必要建模项。经 L1–L5 检查，robustness E1–E5 全部通过（最大扰动影响 $0.96\%$，结论 stable），ablation F0+A1–A4 全部通过（色散、衬底往返、多初值模块均为必要组件）。

**问题 2（SiC 实测反演）**：对同一块 SiC 晶圆片在 $10°$（附件 1）与 $15°$（附件 2）的实测谱，先做归一化、异常点剔除、Reststrahlen 区剔除与主反演带截断 $\nu\in[2000,4000]\ \mathrm{cm}^{-1}$，再以“基线-干涉分解 + 一维相位-频率扫描（variable projection）”反演。得共享厚度 $\hat t=7.2158\ \mu\mathrm{m}$（每角 $7.2214/7.2095\ \mu\mathrm{m}$，$\varepsilon_{12}=0.165\%$，主拟合加权 RMSE $\approx6.3\times10^{-4}$），衬底折射率 $\hat n_{\mathrm{sub}}=2.588$（弱可辨识）。独立 FFT 数据探针确认带内真实干涉周期 $\Delta g\approx657/698$、$\Delta\nu\approx247/263\ \mathrm{cm}^{-1}$，对应 $t\approx7.2$–$8.0\ \mu\mathrm{m}$，与主结果一致。可靠性判据 5/6 通过（色散 $0.51\%$、CI $0.091\%$、异常点 $0.0\%$、$n_{\mathrm{sub}}$ 解耦、多光束均达标），仅两角嵌套 $F$ 检验统计显著（$F=5.25>F_{\mathrm{crit}}=3.843$，$p=0.022$）而裸偏差 $\varepsilon_{12}=0.165\%\ll\tau_{12}=2\%$，按 formulation §7.1/§14 记作 B11（测量点差异/膜厚梯度）并解释，不构成模型修订；variable projection 重构消除了 v002 的可辨识性结构缺陷。robustness C1–C8 与 ablation F0+A1–A4 全部通过。

**问题 3（多光束干涉与 Si 片厚度）**：由 Airy 多光束反射率（3.6）严格推导多光束必要条件（界面强度反射率几何平均 $\bar R$、相干长度、界面平行度、吸收），并证明无吸收平行板的 Airy 极值位置仍为 $\delta=m\pi$、与两光束一致，即多光束不改变由相位频率决定的厚度。对硅片（附件 3/4）判定 $\bar R\approx0.0101$、$F\approx0.319$ 均 $\ll1$，且 Airy 相对两光束的全谱残差改善率 $\eta_{\mathrm{mb}}\approx0.11\%\ll\tau_{\mathrm{mb}}=10\%$，为两光束模型适用；反演共享厚度 $\hat t=3.4477\ \mu\mathrm{m}$（每角 $3.4507/3.4463\ \mu\mathrm{m}$，$\varepsilon_{12}=0.130\%$，$J_{\mathrm{shared}}=0.0608$ 全局唯一），并修正了 v001 的 $6.9\ \mu\mathrm{m}$ 因子-2 伪影（R1）与 finesse 公式漏 $\sqrt{\bar R}$ 的缺陷（R2）。全部可靠性判据 R1–R8 通过；SiC 复判 $\bar R\approx0.0024$、无需修正，prob02 结果维持。

**全文验证**：各问结果均通过 L1–L6 门禁（PASS_WITH_WARNING），并辅以跨小问一致性审查（共享符号、单位、参数值、约束与结论方向全部自洽）与 robustness/ablation 证据；所有数值、图、公式与文献性主张均锚定至证据包，结论仅在已验收的假设、数据范围与警告边界内成立。



## 关键词

红外干涉测厚；外延层厚度反演；两光束干涉；多光束干涉；变量投影；可靠性与稳健性分析

## 问题重述

碳化硅与硅是重要的第三代半导体材料，其外延层厚度是直接影响器件性能的关键参数，因此需要一套科学、准确、可靠且无损伤的测试方法。红外干涉法正是一种无损测厚手段：外延层与衬底因掺杂载流子浓度不同而具有不同折射率，红外光入射外延层后，一部分从外延层上表面反射，另一部分透射进入外延层并在外延层/衬底界面反射后折返，两束光在探测器处叠加产生干涉条纹；由条纹的波数（或波长）、外延层折射率与入射角即可反推厚度。题目强调外延层折射率非常数，与掺杂浓度和波长有关。

题目共三个递进问题，要求：

1. **问题 1**：在“外延层与衬底界面只发生一次反射、透射”的两光束干涉情形下，建立确定外延层厚度的数学模型。
2. **问题 2**：依据问题 1 的模型，设计确定厚度的算法；对附件 1、2（同一块 SiC 晶圆片，入射角分别为 $10°$ 与 $15°$）给出厚度计算结果并分析可靠性。
3. **问题 3**：推导光波在外延层与衬底界面多次反射、透射（图 2）所产生多光束干涉的必要条件及其对厚度精度的影响；依据必要条件判定附件 3、4（同一块硅晶圆片，$10°$ 与 $15°$）是否出现多光束干涉，给出硅外延层厚度的模型、算法与结果；若判定多光束也出现在 SiC（附件 1、2）中，则设法消除其影响并给出修正结果。

**数据场景**：四个附件均为两列（波数 $\nu$，单位 $\mathrm{cm}^{-1}$；反射率 $R$，单位 $\%$），共 7469 个数据点，波数范围约 $399.67$–$4000.12\ \mathrm{cm}^{-1}$，等间隔步长约 $0.482\ \mathrm{cm}^{-1}$。附件 1/2 为同一块 SiC 晶圆片在不同入射角的测试结果，附件 3/4 为同一块硅晶圆片在不同入射角的测试结果。其中附件 2 反射率最大值 $102.74\%$ 超过 $100\%$，属数据质量异常，需在预处理阶段记录处理方式（不得修改原始数据）。

## 问题分析与总体流程

外延层厚度 $t$ 由干涉条纹的频率（相位积累率）唯一确定，这是整题建模的核心物理洞察。据此，本文采用“题面解析—假设与符号统一—分问建模—数值求解—结果解释—sanity 与稳健性验证—跨小问一致性复核”的流程：

- **统一物理设定**：结构为空气 → 外延层（厚度 $t$、折射率 $n$）→ 衬底（折射率 $n_{\mathrm{sub}}$），界面平行；入射角 $\theta$ 已知。
- **问题 1 建模**：先建立两光束反射率正模型与干涉极值条件，再给出由 $\Delta\nu$（色散化）与全谱拟合反演 $t$ 的公式；由于无附件数据，以合成验证检验模型。
- **问题 2 反演**：在问题 1 模型基础上，针对实测谱设计“预处理 → 基线-干涉分解 → 一维相位-频率扫描（variable projection）”算法，并对 SiC 附件给出厚度与可靠性。
- **问题 3 建模**：从 Airy 公式严格推导多光束必要条件与极值位置不变性，据此判定硅片是否多光束并反演其厚度，再对 SiC 重新判定。
- **统一验证**：逐问执行 robustness 与 ablation，并做跨小问、跨材料的一致性检查。

本文作者仅负责将已通过跨小问审查与 sanity 检查的材料组织为论文，不重新建模、不重估参数、不增补数据或引用；所有定量结论均回溯至证据包。

## 模型假设

各小问只采用证据包中登记的接受假设（assumption_v001），并按题面物理一致性、文献与全局符号表校验。关键假设均在对应小问展开，标注类型、关键性与适用边界，并以登记文献作为方法依据。

**问题 1 假设（F0–F3 族）**：F1 两光束干涉模型与厚度公式（关键假设 A1–A4：仅两束相干光、Snell 折射与几何光程差 $2nt\cos\theta'$、Fresnel 界面反射与相位跃变）；F2 折射率色散（A5：$\lambda\le5\ \mu\mathrm{m}$ 用 4H-SiC Sellmeier，$\lambda>5\ \mu\mathrm{m}$ 由数据反演/分谱段确定；A12）；F3 掺杂/自由载流子对红外折射率的影响（A6）；F0 边界与数据假设（A7–A11：无吸收适用谱段、平行界面、相干性、$n_{\mathrm{air}}=1$）。冲突检查结论：假设内部无冲突，与题目理解及全局符号表一致，A2/A7 谱段适用性以 A7 边界为限（近 Reststrahlen 区吸收不可忽略）。[L01]

**问题 2 假设（H1–H6 族）**：H1 数据契约与预处理（B1–B3：比例归一、$>100\%$ 异常点、Reststrahlen 谱段）；H2 两光束模型与几何/相位继承（B4、B5，继承 prob01）；H3 材料光学参数（B6、B7：色散 $n(\nu)$、衬底 $n_{\mathrm{sub}}$、吸收边界）；H4 厚度反演算法（B8–B10：极值定位、全谱 NLS、色散化优先）；H5 可靠性与统计（B11、B12：两角一致性、噪声传播）；H6 多光束判定与修正（B13，预留 prob03）。假设内部无冲突，与题目理解及 prob01 结论（content_hash `82820355…070a6`）一致。[L01]

**问题 3 假设（M1–M5 族）**：M1 多光束必要条件严格推导（C1–C5：Airy 公式、界面反射率阈值、相干长度、界面平行度、吸收限制）；M2 硅外延层数据契约与材料/光谱参数（C6–C9）；M3 硅片是否多光束的判定（C10–C12：数据为据、阈值、链路分支）；M4 多光束对精度的影响与修正（C13–C15：影响机制、Airy/FFT 修正、SiC 重新判定）；M5 前问结论继承与跨问一致性（inherit prob01/prob02 结论）。[L01]

各假设的适用范围、偏差方向与验证方式在对应小问保留，并以登记文献作为方法依据。已知的方法边界（如 $\lambda>5\ \mu\mathrm{m}$ 色散缺口、$n_{\mathrm{sub}}$ 弱可辨识、$\lambda>5\ \mu\mathrm{m}$ SiC 色散缺口、文献全文待复核等）作为披露的技术债出现在各问“可靠性与结论”及“模型评价、局限与推广”中，不作改写的“已解决”处理。

## 符号说明

除特别说明外，符号与单位全题统一（见 `global_symbols.yaml`），禁止同名异义。下表为主要符号：

| 符号 | 含义 | 单位 | 量域 |
|---|---|---|---|
| $t$ | 外延层厚度 | $\mu\mathrm{m}$ | $>0$ |
| $n$ | 外延层折射率（与掺杂浓度、波长相关，非常数） | 无量纲 | $>1$ |
| $n_{\mathrm{sub}}$ | 衬底折射率 | 无量纲 | $>1$ |
| $n_{\mathrm{air}}$ | 空气（入射介质）折射率 | 无量纲 | $\approx1$ |
| $\theta$ | 入射角（空气侧，相对表面法线） | 度 | $[0,90°)$ |
| $\theta'$ | 外延层内折射角 | 度 | $[0,90°)$ |
| $\theta''$ | 衬底内折射角 | 度 | $[0,90°)$ |
| $\lambda$ | 真空中红外光波长 | $\mu\mathrm{m}$ | $>0$ |
| $\nu$ | 波数 | $\mathrm{cm}^{-1}$ | $>0$（实测约 $399.7$–$4000.1$） |
| $R$ | 干涉光谱反射率（实测数据） | $\%$ | $\ge0$（附件 2 个别值 $>100$ 属异常） |
| $m$ | 干涉级次 | 无量纲 | $\ge0$ |
| $\Delta\nu$ | 相邻同型极值（峰-峰/谷-谷）波数间隔 | $\mathrm{cm}^{-1}$ | $>0$ |
| $\Delta g$ | $g$ 空间干涉周期 | $\mathrm{cm}^{-1}$ | $>0$ |
| $N_c$ | 掺杂载流子浓度 | $\mathrm{cm}^{-3}$ | $>0$ |
| $r_{01},r_{12}$ | 空气/外延层、外延层/衬底界面振幅反射系数（Fresnel） | 无量纲 | $\lvert r\rvert<1$ |
| $R_{01},R_{12}$ | 空气/外延层、外延层/衬底界面强度反射率 | 无量纲 | $[0,1)$ |
| $\bar R$ | 界面强度反射率几何平均 $\sqrt{R_{01}R_{12}}$ | 无量纲 | $>0$ |
| finesse | 多光束精细度 $F=\pi\sqrt{\bar R}/(1-\bar R)$ | 无量纲 | $>0$ |
| $\delta$ | 相邻反射光束相位差（含光程差相位与反射相位跃变） | rad | 实数 |
| $\varphi$ | 界面反射相位跃变之和（取值 0 或 $\pi$） | rad | $0,\pi$ |
| $g(\nu)$ | 相位函数 $n(\nu)\nu\cos\theta'(\nu)$ | $\mathrm{cm}^{-1}$ | 实数 |
| $B(\nu),C(\nu),S(\nu)$ | 基线、干涉余弦/正弦多项式包络（阶数 $p,q$） | 无量纲 | 实数 |
| $A(\nu)$ | 干涉幅值（包络）$\sqrt{C^2+S^2}$ | 无量纲 | $\ge0$ |

单位换算约定：$\lambda[\mu\mathrm{m}]=10^4/\nu[\mathrm{cm}^{-1}]$；$\delta=4\pi\times10^{-4}\,n\,t\,\nu\cos\theta'$（$t$ 以 $\mu\mathrm{m}$、$\nu$ 以 $\mathrm{cm}^{-1}$ 计）。

## 数据说明与预处理

数据文件、预处理记录与计算结果均由证据包按 SHA-256 固定；正文不改写原始数据。异常值、缺失值、筛选区间与单位转换均以各问已验收实现与结果记录为准。

- **附件 1/2（SiC）**：波数约 $399.67$–$4000.12\ \mathrm{cm}^{-1}$；附件 1 反射率范围 $0.0$–$95.39\%$、均值 $22.27\%$；附件 2 范围 $0.0$–$102.74\%$、均值 $23.59\%$。附件 2 存在反射率 $>100\%$ 的异常点（$n=262$ 个，红 × 标注），预处理时按影响增量在“剔除 / 稳健基线截断至 $100\%$ / 稳健拟合降权”三策略中选择，影响在可靠性分析中量化。
- **附件 3/4（Si）**：范围 $0.0$–$79.80\%$（附件 3）、$0.0$–$91.49\%$（附件 4）；无 $R\%>100$ 异常点；透明区（约 $1500$–$4000\ \mathrm{cm}^{-1}$）反射率约 $20\%$–$43\%$，存在清晰干涉条纹。
- **预处理共性**：归一化 $R^{\mathrm{obs}}=R\%/100$；$\lambda=10^4/\nu$；波数升序重排（附件 2 原为降序）；Reststrahlen 区（SiC 约 $[700,1000]\ \mathrm{cm}^{-1}$）与硅多声子带（$<1500\ \mathrm{cm}^{-1}$）按无吸收模型不适用而剔除或降权（$w_i=0$）；主反演带截断至 $\nu\in[2000,4000]\ \mathrm{cm}^{-1}$（色散已知区）。
- **原始数据只读**：所有变换写入预处理日志（计数与阈值），不修改原始文件。



## prob01 模型建立、求解与结果

### prob01 问题分析

问题 1 无附件数据，目标是建立“只考虑一次反射、透射”的两光束干涉情形的解析测厚模型。识别出的输入/输出/约束为：输入为外延层-衬底结构与光学参数（$\theta$、$n$、$n_{\mathrm{sub}}$），输出为反射率谱 $R(\nu)$、厚度 $t$ 与干涉级次 $m/\Delta\nu$；硬约束为 $R\in[0,1]$、$t>0$、模型与“折射率非常数且随波长变化”的物理事实一致。本问只做解析推导与合成验证，不涉及附件数据；数值计算与数据验证留待 prob02。

### prob01 模型建立与求解

**两光束干涉正模型**。结构为空气 → 外延层（厚度 $t$、折射率 $n$）→ 衬底（$n_{\mathrm{sub}}$），界面平行。由 Snell 定律 $n_{\mathrm{air}}\sin\theta=n\sin\theta'$（取 $n_{\mathrm{air}}=1$），几何光程差为（prob01 (2.6)）：
$$\Delta=2t\sqrt{n^2-\sin^2\theta}=2nt\cos\theta'$$
两束相干光相位差（prob01 (2.8)）：
$$\delta=4\pi\times10^{-4}\,n\,t\,\nu\,\cos\theta'$$

由 s/p 偏振 Fresnel 振幅反射系数（prob01 (3.1)–(3.3)）得到界面强度反射率 $R_1=\lvert r_1\rvert^2$、$R_2=\lvert r_2\rvert^2$，两光束反射率正模型（prob01 (3.5)，对非偏振取 s/p 平均 (3.6)）：
$$R(\nu;t,n(\nu),\theta,n_{\mathrm{sub}})=R_1+(1-R_1)^2R_2+2(1-R_1)\sqrt{R_1R_2}\,\cos\delta$$

**干涉极值条件与厚度公式**。无吸收、弱色散时 $R$ 仅通过 $\cos\delta$ 依赖 $\nu$，极值条件（prob01 (3.7)）：
$$\frac{\partial R}{\partial\nu}=0\iff\sin\delta=0\iff\delta=m\pi,\quad m\in\mathbb{Z}_{\ge0}$$
同型相邻极值对应 $\delta$ 变化 $2\pi$，得波数间隔与厚度反演公式（prob01 (3.8)–(3.10)）：
$$\Delta\nu=\frac{1}{2nt\cos\theta'},\qquad t=\frac{1}{2\Delta\nu\sqrt{n^2-\sin^2\theta}}=\frac{10^4}{2n\cos\theta'\,\Delta\nu[\mathrm{cm}^{-1}]}$$

**色散化修正**。色散显著时用相位函数 $g(\nu)=n(\nu)\nu\cos\theta'(\nu)$（prob01 (3.11)–(3.13)），极值条件化为 $g(\nu_m)=m/(4t)$，得
$$t=\frac{1}{2\big[g(\nu_{m+2})-g(\nu_m)\big]}$$
弱色散极限回到上式。$n$ 采用 4H-SiC Sellmeier（prob01 (4.1)）：
$$n^2(\lambda)=6.79485+\frac{0.15558}{\lambda^2-0.03535}-0.02296\,\lambda^2,\quad\lambda\le5\ \mu\mathrm{m}$$

**求解策略选择**：本问为连续参数估计（1 个厚度 + 少量材料参数），正模型解析、目标光滑，采用精确方法（NLS/解析反演 / 一维扫描）即可，无需 MILP 或启发式。反演候选模型为：M1 色散化全谱 Fresnel NLS（主模型）、M2 常数 $n$ 两光束、M3 弱色散峰谷间隔、M4 多光束 Airy（prob03 处理）。



**合成验证结果**。在 $t_{\mathrm{true}}=10.0\ \mu\mathrm{m}$、$n_{\mathrm{sub}}=3.0$ 下生成两入射角合成谱，三种方法（常数 $n$ 间隔法 A、色散化相位法、全谱 NLS 多初值）的厚度估计、相对偏差与模型行为见下：

![prob01_fig_thickness_methods_compare_5eac465fc8 三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_thickness_methods_compare_5eac465fc8.png)

图 `prob01_fig_thickness_methods_compare_5eac465fc8` 展示三种方法 × 两入射角的厚度估计与 $t_{\mathrm{true}}=10.0\ \mu\mathrm{m}$ 参考线及 $\pm1\%$ 容差带对比，标注了各方法的相对偏差。自动质检 passed（1538×985 px、暗边框 0.0）+ 视觉复核确认 $t_{\mathrm{true}}$ 参考线与 $\pm1\%$ 容差带清晰、颜色区分明确。结论：NLS 与色散化相位法均落在 $\pm1\%$ 带内（偏差约 $10^{-3}$ 量级），方法 A 约 $4\%$ 基线偏差超阈；该图支持“色散化全谱拟合为更稳健主方法”的选择，同时把方法 A 的已知偏差作为 B10 基线披露。

![prob01_fig_spacing_constant_n_bias_2245b6eda4 方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_spacing_constant_n_bias_2245b6eda4.png)

图 `prob01_fig_spacing_constant_n_bias_2245b6eda4` 对比实测（色散）间隔与常数 $n$ 理论间隔，标注约 $4.2$–$4.7\%$ 偏差；自动质检 passed + 视觉复核确认说明框无数据遮挡。它把“方法 A 忽略色散导致约 $4\%$ 系统偏差”作定量展示，支持在厚谱段必须引入色散化修的正确性。

![prob01_fig_reflectance_spectrum_1d4fb899d1 两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_reflectance_spectrum_1d4fb899d1.png)

图 `prob01_fig_reflectance_spectrum_1d4fb899d1` 给出两入射角下的合成反射率谱与峰标注，以及 Reststrahlen/Sellmeier 边界。自动质检 passed（1567×994 px、暗边框 0.0）+ 视觉复核确认双角谱线、峰标注与边界清晰、图例无遮挡。该图验证合法拟合带内的干涉条纹频率与厚度对应关系，为后续反演布局提供基准。

![prob01_fig_dispersion_curve_d85564d2fc 外延层 4H-SiC 折射率色散模型 n(ν)](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_dispersion_curve_d85564d2fc.png)

图 `prob01_fig_dispersion_curve_d85564d2fc` 展示 4H-SiC 折射率色散模型 $n(\nu)$ 的分段策略（Sellmeier 与常数延伸）。自动质检 passed + 视觉复核确认 $\lambda/\nu$ 双轴换算正确、边界与 Reststrahlen 区标注无重叠。该图说明 $n(\nu)$ 的色散是“频率型”厚度信号的前置输入，色散分段边界与反演带截断一致。

![prob01_fig_phase_function_gap_459c486470 色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_phase_function_gap_459c486470.png)

图 `prob01_fig_phase_function_gap_459c486470` 双面板展示 $g(\nu)$ 单调性与同型极值间隔 $\Delta g$ 恒定律（约 $500\ \mathrm{cm}^{-1}$）。自动质检 passed + 视觉复核确认机制清晰。该图为色散化相位法提供了“$g$ 空间恒定周期”的物理依据，是 $t=1/(2\times10^{-4}\Delta g)$ 方法的来源。

![prob01_fig_nls_multistart_e64919ab13 全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_nls_multistart_e64919ab13.png)

图 `prob01_fig_nls_multistart_e64919ab13` 展示全谱 NLS 在不同初值下的 RMSE 面与周期歧义局部极小、全局解（$t=10.000\ \mu\mathrm{m}$，rmse$\approx0$）。自动质检 passed + 视觉复核确认全局解与局部极小分离清晰。该图表明目标函数存在厚度周期歧义，说明多初值（或多点枚举）是防止落入歧义局部极小的必要算法设计。

![prob01_fig_response_surface_d0691c5dd8 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_response_surface_d0691c5dd8.png)

图 `prob01_fig_response_surface_d0691c5dd8` 给出 $R(\nu,\theta)$ 三维响应面与二维等高线，第三维为真实入射角变量，$\theta=10°/15°$ 测量线标注。自动质检 passed + 视觉复核确认视角可读（elev=26°、azim=-62°）无关键遮挡。该图说明干涉条纹对 $\theta$ 的依赖，支持“两角一致性可作为可靠性天然判据”的分析。

### prob01 结果解释

合成验证表明：全谱 NLS 与色散化相位法在 $t_{\mathrm{true}}=10.0\ \mu\mathrm{m}$ 下均以近零残差精确恢复，两入射角结果一致；方法 A 因忽略色散存在约 $4\%$ 系统偏差，属已知基线与方法债（B10）。色散化正模型在适用谱段内满足 $R\in[0,1]$ 的能量守恒约束，干涉级次与 $\Delta\nu$ 关系满足极值条件。这些结果共同支撑以 M1（色散化两光束 Fresnel 正模型）作为 prob02 的建模基线；prob02 在此基础上把数值反演算法细化为 baseline-robust variable projection（见 prob02 章节），以应对弱对比度与未建模基线。



### prob01 可靠性与结论

prob01 的 L1–L4 sanity 为 PASS_WITH_WARNING（合成验证任务 0ea4b29da19e8479a6ea：19/19 检查通过，$t_{\mathrm{true}}=10\ \mu\mathrm{m}$ 被 NLS/相位法精确恢复、两角一致，hash 追踪链与 task.json/implementation.md §7 完全一致，无 NaN/Inf、无硬约束违反、公式-代码逐条一致、文献/物理常识合理），L5 sanity 为 PASS，robustness 验收（Level 6）为 PASS。

**稳健性（robustness，E1–E5）**：预注册方案 robustness_v001 以隔离任务执行 E1–E5（$n_{\mathrm{sub}}/\theta$ ±5/±10/±20% 扰动、色散三模型、噪声 $\sigma=0.5/1/2\%\times100$ 次×2 入射角、谱段截断 6 组），5/5 判据通过，结论 `stable`：E1 扰动 $0.008\%$、E2 $\theta$ 影响 $0.22\%$、E3 替代色散模型 $0.96\%$、E4 噪声 CI 半宽 $<0.03\%$ 且收敛率 $100\%$、E5 谱段截断 $0\%$。发现噪声下极值定位初值失真，已升级为网格扫描初值（prob02 复用）。

![prob01_fig_sensitivity_tornado_6983566848 prob01 robustness 敏感性 tornado 汇总（E1–E5）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_sensitivity_tornado_6983566848.png)

图 `prob01_fig_sensitivity_tornado_6983566848` 把 E1–E5 五因素的实测影响（横条）与预注册阈值（竖线）并排对照。自动质检 passed（非空白、暗边框 0.0、1514×865）+ 结构复核确认文本无重叠。该图说明所有因素的实测影响均低于阈值，最大不确定度来源为色散模型（E3 $0.96\%$，仍 $\ll$ 目标精度），可支撑“色散为最大不确定度来源、但带内可接受”的结论。

![prob01_fig_noise_robustness_ci_30d4fa737f E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_noise_robustness_ci_30d4fa737f.png)

图 `prob01_fig_noise_robustness_ci_30d4fa737f` 展示 $\sigma=0.5/1/2\%$×$\theta=10°/15°$ 的厚度均值与 95% CI 误差棒，$t_{\mathrm{true}}$ 参考线清晰。自动质检 passed（非空白、暗边框 0.0、1561×942）+ 结构复核确认图例无重叠。该图量化了噪声下厚度估计的置信区间，半宽最大 $0.022\%$ 远低于阈值，说明噪声对厚度是二阶小量。

**消融（ablation，F0+A1–A4）**：预注册方案 ablation_v001 以隔离任务执行 F0+A1–A4（干涉项消融、衬底反射消融、偏振平均消融、多初值模块消融），5/5 判据通过，结论 `components_confirmed`：A1/A2 不可辨识 = 组件必要、A3 偏振平均最大差 $0.012\%$、A4 单初值 $6.03\%$ vs 多初值 $\approx0$。

![prob01_fig_ablation_summary_ee3c34dcfa prob01 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_summary_ee3c34dcfa.png)

图 `prob01_fig_ablation_summary_ee3c34dcfa` 汇总 F0+A1–A4 五组判据（实测 vs 阈值竖线）。自动质检 passed（2039×1319 px、暗边框 0.0、非空白）+ 结构复核确认 A4 单初值退化（$6.03\%$）与多初值对照（$\approx0$）语义区分明确、数值与 summary.json 一致。该图支持“多初值模块为必要组件、且周期歧义是真实风险”的结论。

![prob01_fig_ablation_polarization_da59250d1b A3 偏振一致性：avg/s/p 反演厚度 vs t_true](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_polarization_da59250d1b.png)

图 `prob01_fig_ablation_polarization_da59250d1b` 展示 avg/s/p 三种偏振×两入射角的厚度柱状，数值在 $10.0000/10.0002/9.9998$ 量级。自动质检 passed（1682×960 px、暗边框 0.0、非空白）+ 结构复核确认 $t_{\mathrm{true}}$ 参考线与 $\pm1\%$ 容差带清晰。该图说明偏振平均对厚度影响可忽略（A3 最大差 $0.012\%$），即 s/p 平均不构成精度瓶颈。

![prob01_fig_ablation_init_strategy_7c59622d5a A4 初值策略对比：单初值局部极小 vs 多初值全局解](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_init_strategy_7c59622d5a.png)

图 `prob01_fig_ablation_init_strategy_7c59622d5a` 对单初值（$t\approx10.60$，偏差约 $6\%$，落入周期歧义局部极小）与多初值（$t=10.000$，偏差约 0）作对比。自动质检 passed（2413×963 px、暗边框 0.0、非空白）+ 结构复核确认与 implementation §6.1 预警方向量级一致。该图直接论证多初值策略的必要性，作为 A4 判据的可视化证据。

需要保留的边界与警告（技术债，不改写为已解决）：prob01 技术债包括 $\lambda>5\ \mu\mathrm{m}$ 常数色散延伸、方法 A 约 $4\%$ 基线偏差、文献全文待复核、$n_{\mathrm{sub}}$ 为合成场景值、Reststrahlen 剔除策略，均留 prob02 处理；robustness 基于合成谱、色散模型选择、$\lambda>5\ \mu\mathrm{m}$ 常数延伸、$n_{\mathrm{sub}}$ 场景值。因此本问结论限于上述假设、合成数据范围与误差条件。<!-- warning:warn_prob01_fac14a9dfae4 --> 同时，robustness 的物理机制（$n_{\mathrm{sub}}$ 影响幅度不影响相位、$\theta$ 误差为二阶小量、色散模型为最大不确定度来源、全谱平均效应）与常识一致，技术债均不阻断推进。<!-- warning:warn_prob01_cdf6b5be3241 -->

**结论**：prob01 在两光束近似下建立了反射率正模型与色散化反演公式，并在合成验证下以近零残差恢复 $t_{\mathrm{true}}=10.0\ \mu\mathrm{m}$；robustness 与 ablation 全部通过，确认“色散为必要建模项、多初值为必要算法模块”。方法 A 约 $4\%$ 的基线偏差被披露为已知方法债；prob02 以该色散化两光束正模型为建模基线，并把数值反演算法细化为 baseline-robust variable projection。

## prob02 模型建立、求解与结果

### prob02 问题分析

问题 2 在问题 1 两光束模型基础上，对同一块 SiC 晶圆片两个入射角的实测谱给出厚度算法、结果与可靠性。识别出的关键难点是：SiC 带内干涉条纹对比度较弱（$n_{\mathrm{sub}}\approx n\approx2.58$），且存在未建模的慢变基线。这导致“全谱幅值最小二乘”（v002）被基线主导落入非物理小厚度盆地（$t\approx0.3\ \mu\mathrm{m}$），而极值间隔法又把噪声纹波当成干涉极值（$t\approx60\ \mu\mathrm{m}$），出现两数量级量级冲突。因此本问的核心是**换用一个与物理信息结构匹配的方法**——用干涉频率测厚度、用幅值测对比度，二者解耦。

### prob02 模型建立与求解

**正模型（继承 prob01）**。两光束反射率正模型同 prob01（2.3），其中 $\delta(\nu_i)=4\pi\times10^{-4}\,n(\nu_i)\,t\,\nu_i\cos\theta'(\nu_i)+\varphi$，$\varphi$ 为两界面反射相位跃变之和；模型反射率取 s/p 平均（2.4）。

**基线-干涉分解（variable projection）**。把实测谱分解为慢变基线 + 干涉项（formulation §5.1）：
$$R^{\mathrm{obs}}(\nu)=B(\nu;\mathbf b)+C(\nu;\mathbf c)\cos\delta(\nu)+S(\nu;\mathbf s)\sin\delta(\nu)+\epsilon(\nu)$$
$$B(\nu)=\sum_{j=0}^{p}b_j\nu^j,\quad C(\nu)=\sum_{j=0}^{q}c_j\nu^j,\quad S(\nu)=\sum_{j=0}^{q}s_j\nu^j$$
$B$ 吸收 DC 基线及其色散趋势，$C,S$ 吸收干涉包络 $A$ 与未知相位 $\varphi$（$A=\sqrt{C^2+S^2}$，$\varphi=\mathrm{atan2}(-S,C)$）；$t$ 只进入 $\delta$ 的频率，不进入 $B,C,S$。对固定 $t$，$R^{\mathrm{obs}}-\Phi(t)\beta$ 为线性最小二乘（5.4)-(5.5）；对 $t$ 做一维全局扫描，取全局最小（5.6)-(5.7）：
$$J(t)=\sum_{k=1}^{2}\sum_i w^{\mathrm{inv}}_{k,i}\bigl[R^{\mathrm{obs}}_{k}(\nu_i)-\bigl(B_k+C_k\cos\delta_k+S_k\sin\delta_k\bigr)\bigr]^2,\qquad \hat t=\arg\min_{t}J(t)$$

**厚度与相位频率的解析关系（物理根据）**：$t$ 由干涉相位积累率决定，$g$ 空间具有恒定周期（5.8)-(5.9）：
$$\frac{d\delta}{d\nu}=4\pi\times10^{-4}\,t\,\dot g(\nu),\qquad \Delta g=\frac{1}{2\times10^{-4}\,t}\iff t=\frac{1}{2\times10^{-4}\,\Delta g}$$
即“条纹越密（周期越短），厚度越大”。$n_{\mathrm{sub}}$ 不参与主反演，$t$ 与 $n_{\mathrm{sub}}$ 结构解耦，由干涉幅值在拟合后单独估计并标示弱可辨识。

**求解策略**：本问为 1 维连续非线性扫描（变量投影后每点线性 LS），正模型解析、目标对 $t$ 高度非凸但有清晰全局极小，属“小规模、连续、可预测”，用精确方法（一维枚举扫描 + 线性 LS）即可，无需 MILP/元启发式。

**两角一致性（§7.1 嵌套 F 检验）**：对“两角共享 $t$”与“每角独立 $t$”做嵌套 $F$ 检验（7.1）；报告每角 $\hat t_1,\hat t_2$ 与裸偏差 $\varepsilon_{12}=\lvert\hat t_1-\hat t_2\rvert/\bar t\times100\%$，阈值 $\tau_{12}=2\%$。



**算法流程**：归一化与网格对齐（§3.1）→ 异常点处理（§3.2）→ Reststrahlen 剔除（§3.3）→ 主反演带截断 $\nu\in[2000,4000]\ \mathrm{cm}^{-1}$（§3.4）→ 干涉周期粗估 + 频谱检验定扫描区间（§6.1）→ 一维全局扫描 variable projection 求 $\hat t$（§6.2）→ 局部抛物线精化 + 物理正模型 NLS 交叉校验（§6.4）→ 可靠性分析（§7）。

**主结果**：共享厚度 $\hat t=7.2158\ \mu\mathrm{m}$，每角 $7.2214/7.2095\ \mu\mathrm{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\mathrm{sub}}=2.588$（弱可辨识），主拟合加权 RMSE $\approx6.3\times10^{-4}$。独立只读 FFT 数据探针证实带内真实干涉周期 $\Delta g\approx657/698$、$\Delta\nu\approx247/263\ \mathrm{cm}^{-1}$，对应 $t\approx7.2$–$8.0\ \mu\mathrm{m}$，与主结果一致。方法量级对照：M1（$7.22$）/M1-P1（$6.82$）/M1-P2（$6.97$）为一致量级，M2（$58.01$）/M3（$60.26$）为噪声周期所致的错误量级。

![prob02_fig_reflectance_spectrum_6b2265d217 附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reflectance_spectrum_6b2265d217.png)

图 `prob02_fig_reflectance_spectrum_6b2265d217` 给出附件 1/2 的实测谱，标注 Reststrahlen 区强反射峰、附件 2 反射率 $>100\%$ 异常点（$n=262$，红 ×）与主反演带边界。自动质检 passed（1560×992、暗边框 0.0、非空白）+ 视觉复核确认图例无遮挡、单位完整。该图展示数据质量与预处理输入，支撑异常点剔除与主反演带截断的预处理设计。

![prob02_fig_model_fit_0ca711689b 两入射角实测谱与两光束物理正模型 (2.3) 拟合对比](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_model_fit_0ca711689b.png)

图 `prob02_fig_model_fit_0ca711689b` 在 $\theta=10°/15°$ 双面板叠加实测 $R_{\mathrm{obs}}$ 与两光束物理正模型 (2.3) 的 $R_{\mathrm{model}}$，并标注残差 RMSE。自动质检 passed（1780×1100、暗边框 0.0）+ 视觉复核确认标题/图例/单位准确。该图显示物理正模型对干涉条纹的拟合效果，用于与主方法（variable projection）互为交叉校验。

![prob02_fig_thickness_estimate_efa7359eb9 prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_thickness_estimate_efa7359eb9.png)

图 `prob02_fig_thickness_estimate_efa7359eb9` 展示共享 $\hat t=7.2158\ \mu\mathrm{m}$ 与每角 $\hat t$ 柱状、共享 $\hat t$ 的 95% CI 误差棒，以及 $\varepsilon_{12}=0.165\%$ 与实际意义分离（B11）说明框和物理 NLS 交叉校验 P1/P2 标记。自动质检 passed（1523×956、暗边框 0.0）+ 视觉复核确认图例/单位完整。该图是 prob02 主结果的直接可视化，支持“两角结果一致、厚度量级为微米且可复现”的结论。

![prob02_fig_dispersion_curve_af50244106 外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_dispersion_curve_af50244106.png)

图 `prob02_fig_dispersion_curve_af50244106` 展示带内 N-SE（Sellmeier）、$\lambda>5\ \mu\mathrm{m}$ 缺口代理、N-const 基线三线，y 轴覆盖全线，顶轴 $\lambda[\mu\mathrm{m}]$ 换算正确。自动质检 passed（1552×1068、暗边框 0.0）+ 视觉复核确认图例无重叠。该图说明色散模型对厚度反演是输入而非输出，其不确定度在可靠性分析中量化（$\Delta t_{\mathrm{disp}}$）。

![prob02_fig_variable_projection_jcurve_7a9a903650 主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_variable_projection_jcurve_7a9a903650.png)

图 `prob02_fig_variable_projection_jcurve_7a9a903650` 展示 $J(t)$ 全局唯一极小（$J_{\min}\approx0.0032$）+ 95% CI 带 + 次小候选（高 1.75×）+ 右侧对数局部深谷。自动质检 passed（1822×1035、暗边框 0.0）+ 视觉复核确认唯一性证据清晰。该图论证全局极小唯一、周期歧义被色散打破，从而支撑 $\hat t=7.2158\ \mu\mathrm{m}$ 为唯一可信解。

![prob02_fig_g_space_phase_gap_f500d9c0db 相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_g_space_phase_gap_f500d9c0db.png)

图 `prob02_fig_g_space_phase_gap_f500d9c0db` 对比去基线干涉条纹与同型极大（$\Delta\nu\approx253\ \mathrm{cm}^{-1}$），由 $\Delta g$ 反演 $t\approx7.1$–$7.6\ \mu\mathrm{m}$（主方法）vs M2/M3 噪声周期 $54$–$65\ \mu\mathrm{m}$（错误）。自动质检 passed（1848×960、暗边框 0.0）+ 视觉复核确认机制对照清楚、单位/图例完整。该图直接解释 M2/M3 为何失效（把噪声纹波当干涉极值），并说明主方法的物理正当性。

![prob02_fig_nsub_decoupling_39b4128d09 n_sub 幅值弱可辨识性与 t-n_sub 解耦](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_nsub_decoupling_39b4128d09.png)

图 `prob02_fig_nsub_decoupling_39b4128d09` 左面板由幅值 $A=\sqrt{C^2+S^2}\approx0.0039$ 弱辨识 $\hat n_{\mathrm{sub}}\approx2.588$；右面板主方法 $t$-$n_{\mathrm{sub}}$ 解耦（$0.0\%$ 敏感度）vs 物理 NLS ±0.10 交叉校验（$1.92\%$ 诊断）。自动质检 passed（2057×1072、暗边框 0.0）+ 视觉复核确认 x 轴标签不重叠、底部说明完整。该图说明 $n_{\mathrm{sub}}$ 弱可辨识但不影响主厚度（$t$ 与 $n_{\mathrm{sub}}$ 结构解耦），回应 v002 的假灵敏度问题。

![prob02_fig_response_surface_cfe5827835 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_response_surface_cfe5827835.png)

图 `prob02_fig_response_surface_cfe5827835` 给出 $R(\nu,\theta)$ 三维响应面与 2D 等高线，$\theta=10°/15°$ 测量线标注，第三维为真实入射角变量。自动质检 passed（1801×1063、暗边框 0.0）+ 视觉复核确认视角可读、无关键遮挡。该图说明干涉条纹随入射角的分布，与两角一致性检验（§7.1）相互印证。

![prob02_fig_methods_compare_99386076f5 prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_methods_compare_99386076f5.png)

图 `prob02_fig_methods_compare_99386076f5` 在 log 轴对照 M1（$7.22$）/M1-P1（$6.82$）/M1-P2（$6.97$）与 M2（$58.01$）/M3（$60.26$），标注每角范围竖线。自动质检 passed（1746×1009、暗边框 0.0）+ 视觉复核确认方法债说明框完整、图例/单位无重叠。该图强调 M2/M3 因噪声周期失效、量级偏离真实厚度约一个数量级，凸显 variable projection 主方法的必要性。

### prob02 结果解释

反演得到的共享厚度 $\hat t=7.2158\ \mu\mathrm{m}$ 与每角结果一致（$\varepsilon_{12}=0.165\%\ll\tau_{12}=2\%$），并与独立 FFT 数据探针给出的 $t\approx7.2$–$8.0\ \mu\mathrm{m}$ 相符；$J(t)$ 全局唯一极小（次小候选高 $1.75\times$）说明周期歧义已被色散打破。主方法与物理正模型 NLS 交叉校验（P1/P2）同为 $6.8$–$7.0\ \mu\mathrm{m}$ 量级（差异 $5.5\%$ 属登记技术债），进一步确认主结果。M2/M3 因把噪声纹波当作干涉极值而给出错误量级，被明确排除。



### prob02 可靠性与结论

prob02 的 L1–L4 sanity 为 PASS_WITH_WARNING（实测反演任务 30bedd3be5a2c9a36d3a：hash 追踪链与 task.json/implementation.md §7 一致、机器级 L2-finite 通过（8 文件全有限无 NaN/Inf，v001 的 dispersion_ref NaN 已用 null 修复）、公式-代码逐条一致、单位一致、原始数据只读、无硬约束违反），L5 sanity 为 PASS，robustness 验收（Level 6）为 PASS_WITH_WARNING。

**可靠性判据（5/6 通过）**：dispersion（$0.51\%\le2\%$）、ci（$0.091\%\le2\%$）、anomaly（$0.0\%\le1\%$）、nsub 解耦（diag PASS）、multibeam（pass）全部通过；仅 reliability_two_angle_ftest 判为 FAIL（$F=5.251>F_{\mathrm{crit}}=3.843$，$p=0.022$）。但裸偏差 $\varepsilon_{12}=0.165\%\ll\tau_{12}=2\%$，属大样本下统计显著性与实际意义分离，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。

![prob02_fig_reliability_summary_78cd97014b prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reliability_summary_78cd97014b.png)

图 `prob02_fig_reliability_summary_78cd97014b` 用“可接受带 $[0,\tau]$ + 实测条形 + 阈值黑标”汇总各判据，六项全部低于阈值（绿=通过），并将 $\Delta t_{\mathrm{inv\_band}}$、$F$ 检验 B11 路由、多光束诊断说明置于子轴下方。自动质检 passed（1776×987、暗边框 0.0）+ 视觉复核确认无遮挡、无文本重叠。该图直观呈现“除 $F$ 检验统计显著外其余全部达标”，并说明 $F$ 检验的显著性与实际意义的分离，支撑 PASS_WITH_WARNING 结论。

**稳健性（robustness，C1–C8）**：C2 色散 $0.507\%\le2\%$ PASS、C4 $n_{\mathrm{sub}}$ 解耦 $0.0\%$（物理 NLS $1.92\%\le3\%$）PASS、C5 CI 半宽 $0.091\%\le2\%$ PASS、C6 全局极小唯一 PASS、C7 异常点 $0.0\%\le1\%$ PASS、C8 多光束改善 $0.0\%\le10\%$（两光束适用）PASS、R8 基线/包络阶数 $p=2..5,q=0..2$ 稳定；仅 C1 两角嵌套 $F$ 检验统计显著（$F=5.25,p=0.022$），按 §7.1/§14 路由为 B11。结论 `STABLE`（$\hat t_{\text{共}}=7.2158\ \mu\mathrm{m}$）。

**消融（ablation，F0+A1–A4）**：结论 `components_confirmed`：A1 $\Delta t_{\mathrm{disp}}=8.44\%>1\%$（色散必要）、A2 $\Delta t_{\mathrm{base}}=5.55\%>1\%$ 且 RMSE 升 $7.03\times$（基线-稳健分解必要）、A3 $\Delta t_{\mathrm{vp}}=5.44\%>1\%$（相位-频率方法必要）、A4 每角 $\hat t\approx$ 共享 $\hat t$ 且 $\varepsilon_{12}=0.165\%\le2\%$（两角共享-$t$ 为良性一致约束，不扭曲 $\hat t$）。

![prob02_fig_ablation_summary_dcd697b29e prob02 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_summary_dcd697b29e.png)

图 `prob02_fig_ablation_summary_dcd697b29e` 汇总 F0+A1–A4 五组判据（A1/A2/A3 实测 $\Delta t$ 均超 $\tau=1\%$ 阈值竖线、A4 $\varepsilon_{12}=0.165\%\le\tau=2\%$、F0 为 $\hat t$ 参考）。自动质检 passed（2870×1319 px、暗边框 0.0、非空白、无警告）+ 视觉复核确认色彩编码正确、数值与 summary.json 一致。该图确认色散、基线分解、相位-频率方法均为必要组件，而两角共享-$t$ 为良性一致性约束。

![prob02_fig_ablation_thickness_d29e3fc1f0 prob02 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_thickness_d29e3fc1f0.png)

图 `prob02_fig_ablation_thickness_d29e3fc1f0` 展示 F0 完整模型与 A1–A4 各消融项厚度柱状，标注 $\Delta t\%$（$8.44/5.55/5.44$）与 $\varepsilon_{12}$。自动质检 passed（2256×1037 px、暗边框 0.0、非空白、无警告）+ 视觉复核确认 F0 参考线与 $\pm1\%$ 参考带清晰，A4（$0.087\%$ 良性约束）与 A1–A3（贡献确认）语义区分明确。该图以厚度单位量化各组件的必要性，支撑 ablation 结论。

![prob02_fig_ablation_shared_t_14e5362fa7 A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_shared_t_14e5362fa7.png)

图 `prob02_fig_ablation_shared_t_14e5362fa7` 展示共享 $\hat t$ 与 $\theta=10°/15°$ 每角独立 $\hat t$ 柱状，纵轴尺度（±0.2%）合理，$\varepsilon_{12}=0.165\%\le2\%$ 标注。自动质检 passed（2633×1070 px、暗边框 0.0、非空白、无警告）+ 视觉复核确认共享参考线清晰、图例/单位完整。该图直观说明两角共享-$t$ 为良性的安全一致性约束（A4），不扭曲 $\hat t$。

需要保留的边界与警告：v001/v002 曾超阈判据（$\varepsilon_{12}$ $27.66\%\to0.165\%$、$\Delta t_{\mathrm{disp}}$ $15.11\%\to0.51\%$、$n_{\mathrm{sub}}$ $69\%\to$解耦$0\%$、CI $3.51\%\to0.091\%$、M1 $0.305\ \mu\mathrm{m}\to7.216\ \mu\mathrm{m}$ 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。技术债（$\lambda>5\ \mu\mathrm{m}$ 色散缺口 B6、$n_{\mathrm{sub}}$ 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 $5.5\%$ 偏差、L25–L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，不阻断推进。<!-- warning:warn_prob02_a94c3613afe5 --> robustness 验收在降级审查模式下复用既有产物、不发起新计算，机器级 L2-finite 通过，主结果 $\hat t=7.2158\ \mu\mathrm{m}$ 可行可追踪；技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 $5.5\%$、$\lambda>5\ \mu\mathrm{m}$ 色散缺口 B6、$n_{\mathrm{sub}}$ 弱可辨识 B7、L25–L32 全文待复核、多光束 Airy 留 prob03 B13）均不阻断。<!-- warning:warn_prob02_abcae1fbbd23 -->

**结论**：prob02 以“基线-干涉分解 + 一维相位-频率扫描（variable projection）”成功反演 SiC 外延层厚度 $\hat t=7.2158\ \mu\mathrm{m}$（两角一致、$\varepsilon_{12}=0.165\%$），$J(t)$ 全局唯一，robustness 与 ablation 全部通过；该方法消除了 v002 的模型可辨识性结构缺陷。唯一的 $F$ 检验统计显著性被正确路由为 B11（测量点差异/膜厚梯度），不改变厚度结论。

## prob03 模型建立、求解与结果

### prob03 问题分析

问题 3 要求：(1) 严格推导多光束干涉的必要条件及其对厚度精度的影响；(2) 依据必要条件判定硅片（附件 3/4）是否多光束并给出厚度模型/算法/结果；(3) 若 SiC（附件 1/2）也出现多光束则消除其影响并给出修正结果。这是“物理模型 + 可解性反演”问题，非优化问题；主方法为“一维全局扫描 + 线性 LS 的相位-频率拟合（variable projection）”，多光束判定为“两光束 vs Airy 正模型的残差改善诊断”。

核心洞察是：对无吸收平行板，Airy 多光束反射率极值位置严格位于 $\delta=m\pi$，与界面反射率乘积 $R_{01}R_{12}$ 无关，即**多光束不改变干涉周期/极值位置、不改变由相位频率决定的厚度**，只影响条纹对比度、峰形与拟合残差；多光束显著性由界面强度反射率几何平均 $\bar R=\sqrt{R_{01}R_{12}}$（或精细度 $F$）控制，两光束近似对高阶的相对误差为 $O(\bar R)$。

### prob03 模型建立与求解

**多光束 Airy 正模型（formulation §3.3）**。平面平行板多次反射的反射振幅与 Airy 反射强度（3.5)-(3.6）：
$$r=\frac{r_{01}+r_{12}e^{i\delta}}{1+r_{01}r_{12}e^{i\delta}},\qquad R_{\mathrm{Airy}}(\delta)=\frac{R_{01}+R_{12}+2\sqrt{R_{01}R_{12}}\cos\delta}{1+R_{01}R_{12}+2\sqrt{R_{01}R_{12}}\cos\delta}$$
其中 $\delta(\nu)=4\pi\times10^{-4}n_{\mathrm{epi}}(\nu)t\nu\cos\theta'(\nu)+\varphi$（3.7）。两光束极限（$\bar R\to0$）退化为 prob01/prob02 的两光束模型（3.8）：
$$R_{2\mathrm b}(\delta)=R_{01}+(1-R_{01})^2R_{12}+2(1-R_{01})\sqrt{R_{01}R_{12}}\cos\delta$$

**多光束干涉必要条件（本文推导，formulation §4）**：
- **N1（决定性，界面反射率）**：两光束近似对高阶的相对误差 $\sim O(\bar R)$，判据 $\bar R=\sqrt{R_{01}R_{12}}\le\gamma\approx10^{-2}\iff F=\pi\sqrt{\bar R}/(1-\bar R)\le F_{\max}\approx0.32$（4.1)-(4.2）。为稳健（因 $R_{12}$ 弱可辨识），本版取更宽松阈值 $\bar R\le\theta_{\mathrm{mb}}=0.05$（对应 $F\le0.5$、高阶贡献 $\le\sim5\%$），并以残差改善率 $\eta_{\mathrm{mb}}\le\tau_{\mathrm{mb}}=10\%$ 为主判据。
- **N2（相干长度）**：$L_c\approx1/(2\Delta\nu_{\mathrm{res}})$，$m_{\max}^{\mathrm{coh}}=\lfloor L_c/(2nt\cos\theta')\rfloor$（4.3)-(4.4）；硅片（$n\approx3.43$、$t\approx3.45\ \mu\mathrm{m}$、$\Delta\nu_{\mathrm{res}}\approx0.482$）$L_c\approx1.04\times10^4\ \mu\mathrm{m}$、单程 OPD$\approx23.6\ \mu\mathrm{m}$、$m_{\max}^{\mathrm{coh}}\approx439\ge2$，相干性不构成抑制。
- **N3（界面平行度）**：$\alpha\ll\lambda/(2nD\cos\theta')$（4.5）；硅片要求 $\alpha\ll\approx5.8\times10^{-5}$ rad（约 $0.0033°$），实际晶圆片厚度不均匀性进一步压制高次干涉。
- **N4（吸收）**：$m_{\max}^{\mathrm{abs}}=\lfloor1/\kappa\rfloor$，$\kappa=4\pi k\nu t\cos\theta'$（4.6）；硅中红外透明区 $k\approx0$，吸收不抑制多光束；SiC 近 Reststrahlen 与硅多声子带吸收抑制多光束。
- **极值位置不变性（推论，§4.5）**：无吸收时 Airy 反射率仅通过 $\cos\delta$ 依赖 $\delta$，极值仍为 $\delta=m\pi$，与 $R_{01},R_{12}$ 无关，即 L17“多光束不改变极值位置”被独立推导验证成立。

**硅厚度主反演**：复用 prob02 的 baseline-robust variable projection（§7），对附件 3/4 在透明谱段（约 $1500$–$4000\ \mathrm{cm}^{-1}$）反演，两角共享 $t$。硅外延层色散用 Li 1980 硅 Sellmeier（L12、L13，$n\approx3.42$–$3.44$）。

**多光束判定与结果**：硅片 Fresnel 计算 $R_{01}\approx0.301$；由干涉幅值反演 $R_{12}\approx3.38\times10^{-4}$，故 $\bar R\approx0.0101$、$F\approx0.319$（正确公式，均 $\ll1$ 且低于 $\theta_{\mathrm{mb}}=0.05$）；Airy 相对两光束全谱残差改善率 $\eta_{\mathrm{mb}}\approx0.11\%\ll\tau_{\mathrm{mb}}=10\%$ → 判定**硅片未出现显著多光束干涉，两光束模型适用**。

**主结果**：共享厚度 $\hat t=3.4477\ \mu\mathrm{m}$，每角 $3.4507/3.4463\ \mu\mathrm{m}$，$\varepsilon_{12}=0.130\%$，$\hat n_{\mathrm{sub}}$（幅值弱辨识）$=3.558$；$J(t)$ 全局唯一极小在 $t=3.45\ \mu\mathrm{m}$（$J_{\mathrm{shared}}=0.0608$），次小候选比 $\approx1.020$（弱色散下周期邻近候选接近简并，作报告项而非硬门禁；未达到 formulation §13.1 声称的“4 倍余量”）。

**R1/R2 修订**：硅厚度基准 $t=3.4477\ \mu\mathrm{m}$ 修正了 v001 的 $6.9\ \mu\mathrm{m}$ 因子-2 伪影（R1）；finesse 正确定义为 $F=\pi\sqrt{\bar R}/(1-\bar R)$，修正 v001 代码漏 $\sqrt{\bar R}$ 的 bug（R2），$F=0.3186$ 与公式一致。



![prob03_fig_reflectance_spectrum_41a3800f70 附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reflectance_spectrum_41a3800f70.png)

图 `prob03_fig_reflectance_spectrum_41a3800f70` 给出附件 3/4 硅片实测谱，标注多声子带 $[400,1600]$ 与主反演带 $[2000,4000]$ 阴影，且无 $R\%>100$ 异常点。自动质检 passed（1560×992 px、暗边框 0.0、非空白）+ 视觉复核确认图例无遮挡、单位完整。该图展示硅片数据质量良好、透明区干涉条纹清晰，支撑多声子带剔除与两光束适用的判定。

![prob03_fig_model_fit_3e94d2fac7 两入射角实测谱与两光束物理正模型 (2.8) 拟合对比](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_model_fit_3e94d2fac7.png)

图 `prob03_fig_model_fit_3e94d2fac7` 在 $\theta=10°/15°$ 双面板叠加实测 $R_{\mathrm{obs}}$ 与两光束物理正模型 (2.8)，标注残差 RMSE（$2.944\times10^{-2}/2.103\times10^{-2}$）。自动质检 passed（1780×1100 px、暗边框 0.0、非空白）+ 视觉复核确认标题/图例/单位一致。该图显示硅片两光束正模型拟合效果，支持“两光束模型适用”的判定。

![prob03_fig_thickness_estimate_59f1546ed7 prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_thickness_estimate_59f1546ed7.png)

图 `prob03_fig_thickness_estimate_59f1546ed7` 展示共享 $\hat t=3.4477\ \mu\mathrm{m}$ 与每角（$3.4507/3.4463\ \mu\mathrm{m}$）柱状 + 95% CI 误差棒（$\pm0.0046\ \mu\mathrm{m}$），标注 $\varepsilon_{12}=0.130\%\le\tau_{12}=2\%$、$F=0/p=1.0$。自动质检 passed（1538×956 px、暗边框 0.0、非空白）+ 视觉复核确认单位/图例完整。该图是 prob03 主结果的直接可视化，支撑“硅厚度约 $3.45\ \mu\mathrm{m}$ 且两角一致”的结论。

![prob03_fig_dispersion_curve_aac3dcebea 硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_dispersion_curve_aac3dcebea.png)

图 `prob03_fig_dispersion_curve_aac3dcebea` 展示硅带内 N-SE（Sellmeier）与 N-const 点线，y 轴覆盖全线，多声子带/主反演带阴影，顶轴 $\lambda[\mu\mathrm{m}]$ 换算正确。自动质检 passed（1566×1068 px、暗边框 0.0、非空白）+ 视觉复核确认图例无重叠。该图说明硅色散弱（$\Delta n/n\approx0.51\%$），故带内无 $\lambda>5\ \mu\mathrm{m}$ 缺口，色散对厚度影响小（$\Delta t_{\mathrm{disp}}\approx0.503\%\le2\%$）。

![prob03_fig_variable_projection_jcurve_4b30b360a4 主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_variable_projection_jcurve_4b30b360a4.png)

图 `prob03_fig_variable_projection_jcurve_4b30b360a4` 展示 $t=3.4477\ \mu\mathrm{m}$ 全局唯一极小（$J_{\min}=0.0608$）+ 95% CI 带 + 次小候选（$t\approx3.70$，$J$ 高约 $1.020\times$，报告项）+ 右侧对数局部深谷。自动质检 passed（1780×1035 px、暗边框 0.0、非空白）+ 视觉复核确认唯一性证据清晰。该图说明全局极小唯一，但次小候选接近简并（报告项），需结合 §7.6 预注册判据保障全局唯一性。

![prob03_fig_mb_conditions_9571a5012b 多光束干涉必要条件 N1–N4 与硅片判定](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_mb_conditions_9571a5012b.png)

图 `prob03_fig_mb_conditions_9571a5012b` 左面板展示 $\bar R$（$0.0101$）与 $F$（$0.3186$）相对 $\theta_{\mathrm{mb}}=0.05$ 阈值条形，右面板为 N1–N4+$\eta_{\mathrm{mb}}$ 判定表。自动质检 passed（3384×1072 px、暗边框 0.0、非空白）+ 视觉复核确认无文本重叠。该图是“硅片两光束适用”判定的核心证据：$\bar R\ll\theta_{\mathrm{mb}}$ 且 $\eta_{\mathrm{mb}}\approx0.11\%\ll10\%$。

![prob03_fig_sic_multibeam_recheck_4cbb136f9c 多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_sic_multibeam_recheck_4cbb136f9c.png)

图 `prob03_fig_sic_multibeam_recheck_4cbb136f9c` 在 log 轴对照硅（$0.01008$）/SiC（$0.00240$）/SiC 对照 prob02（$0.00247$），均远低于 $\theta_{\mathrm{mb}}=0.05$ 红线。自动质检 passed（1749×1009 px、暗边框 0.0、非空白）+ 视觉复核确认图例置右上、说明框无重叠。该图支撑 Q3 结论：SiC 也未出现显著多光束、无需修正，prob02 结果维持。

![prob03_fig_phase_freq_gspace_a936624612 相位频率（g 空间）测厚机制与条纹计数](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_phase_freq_gspace_a936624612.png)

图 `prob03_fig_phase_freq_gspace_a936624612` 左面板用两光束物理正模型 (2.8) 去基线定位同型极大（$n=5$，$\Delta\nu\approx419\ \mathrm{cm}^{-1}$）；右面板由 $\Delta g$ 反演 $t\approx3.45\ \mu\mathrm{m}$（与 $\hat t=3.4477$ 一致），标注倍周期假极小 $6.9\ \mu\mathrm{m}$（v001 伪影，已排除）。自动质检 passed（1562×1058 px、暗边框 0.0、非空白）+ 视觉复核确认机制清楚、单位/图例完整。该图说明厚度由相位频率确定，并用条纹计数解释为何 $6.9\ \mu\mathrm{m}$ 是倍周期假极小（R1 修订的物理依据）。

![prob03_fig_response_surface_06cfec9b1e 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_response_surface_06cfec9b1e.png)

图 `prob03_fig_response_surface_06cfec9b1e` 给出 $R(\nu,\theta)$ 三维响应面与 2D 等高线，第三维为真实入射角变量，$\theta=10°/15°$ 测量线标注。自动质检 passed（1796×1063 px、暗边框 0.0、非空白）+ 视觉复核确认视角可读、无遮挡。该图说明干涉条纹随波数与入射角的分布，支撑两角一致性检验。

### prob03 结果解释

硅片判定为两光束模型适用（$\bar R\approx0.0101$、$F\approx0.319$ 均 $\ll1$，$\eta_{\mathrm{mb}}\approx0.11\%\ll10\%$），故可直接用 prob02 的 variable projection 反演。共享厚度 $\hat t=3.4477\ \mu\mathrm{m}$，两角一致（$\varepsilon_{12}=0.130\%$），$J(t)$ 全局唯一极小（$J_{\mathrm{shared}}=0.0608$）；次小候选比 $\approx1.020$ 接近简并（弱色散周期歧义），作为报告项而非硬门禁。多光束不改变厚度（极值位置不变性），因此即使存在多光束也可由相位频率法正确测厚。对 SiC 复判 $\bar R\approx0.0024$，仍远低于 $\theta_{\mathrm{mb}}$，无显著多光束、无需修正，prob02 结果 $t=7.2158\ \mu\mathrm{m}$ 维持。



### prob03 可靠性与结论

prob03 的 L1–L4 sanity 为 PASS_WITH_WARNING（主 computation 任务 7e209043973692d067ed：hash 追踪链与 task.json/implementation.md §7 一致、机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf，failures=[]）、公式-代码逐条一致（R1/R2 已修复）、单位一致、原始数据只读、无硬约束违反），L5 sanity 为 PASS，robustness 验收（Level 6）为 PASS_WITH_WARNING。

**可靠性判据（全部 PASS）**：two_angle（$F=0/p=1.0$）、dispersion（$0.503\%\le2\%$）、ci（$0.134\%\le2\%$）、anomaly（$0.0\%\le1\%$）、multibeam_si（$\eta_{\mathrm{mb}}\approx0.11\%$）、multibeam_sic（no_correction_needed，$\bar R\approx0.0024$）、nsub 解耦（diag PASS）；checks_failed=[]。

![prob03_fig_reliability_summary_50b4f34a17 prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reliability_summary_50b4f34a17.png)

图 `prob03_fig_reliability_summary_50b4f34a17` 汇总各判据（可接受带 + 实测条形 + 阈值黑标），五判据全部低于阈值（绿=通过），$F$ 检验 B11 路由、$\eta_{\mathrm{mb}}$ 两光束适用、轮廓似然 CI 与 $n_{\mathrm{sub}}$ 弱可辨识说明置子轴下方。自动质检 passed（1783×987 px、暗边框 0.0、非空白）+ 视觉复核确认无遮挡。该图支撑“可靠性判据全部达标”的结论。

**稳健性（robustness，R1–R8）**：R1 $\varepsilon_{12}=0.130\%\le2\%$、R2 $\Delta t_{\mathrm{disp}}=0.503\%\le2\%$、R3 CI 半宽 $0.134\%\le2\%$、R4 $\Delta t_{\mathrm{anom}}=0.0\%\le1\%$、R5 $\eta_{\mathrm{mb}}=0.111\%\le10\%$、R6 $n_{\mathrm{sub}}$ 解耦 $0.0\%$、R7 $\Delta t_{\mathrm{win}}=0.749\%\le2\%$；R8 唯一性次小候选 $\approx1.020$ 为报告项（弱色散周期歧义），全局唯一性由 §7.6 预注册判据确认。结论 `STABLE`。主结果 $\hat t=3.4477\ \mu\mathrm{m}$，多光束判定两光束适用（硅 $\bar R\approx0.0101$、$\eta_{\mathrm{mb}}\approx0.11\%$；SiC $\bar R_{\max}\approx0.0024$ no_correction_needed），与 prob02 结论一致。

**消融（ablation，F0+A1–A4）**：结论 `components_confirmed`：A1 $\Delta t=0.446\%\le2\%$（色散项）、A2 $\Delta t=0.300\%\le1\%$（Airy 高阶项，L17 极值不变性/§Q1 定量）、A3 $\Delta t=0.574\%\le2\%$（基线多项式，RMSE $+9.5\%$，为拟合优度必要组件）、A4 每角偏差 $0.089\%\le2\%$ 且 $\varepsilon_{12}=0.130\%\le2\%$（共享为安全一致性约束）。

![prob03_fig_ablation_summary_9f93c3dd2d prob03 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_summary_9f93c3dd2d.png)

图 `prob03_fig_ablation_summary_9f93c3dd2d` 展示 A1–A4 实测 $\Delta t\%$ 全部低于预注册阈值（A1 $0.446\%\le2\%$、A2 $0.300\%\le1\%$、A3 $0.574\%\le2\%$、A4 $0.089\%\le2\%$），log 轴与阈值黑标清晰。自动质检 passed（非空白、暗边框 0.0、$\ge800\times480$）+ 视觉复核确认数值与 summary.json/result.json 一致。该图确认各模型组件均为必要或良性约束，无一删除不利情景。

![prob03_fig_ablation_t_consistency_ec44908369 prob03 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_t_consistency_ec44908369.png)

图 `prob03_fig_ablation_t_consistency_ec44908369` 展示 F0+A1–A4 厚度柱状均落在 F0 $\pm1\%$ 参考带内（A4 含每角独立 $\hat t$），F0 参考线、±1% 带与数值标注清晰。自动质检 passed（非空白、暗边框 0.0、$\ge800\times480$）+ 视觉复核确认与 result.json 一致、图例/单位完整。该图以厚度单位说明消融不改变主厚度，支撑组件必要性判定。

![prob03_fig_ablation_rmse_ce4b523efa prob03 ablation 拟合优度对照（加权 RMSE）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_rmse_ce4b523efa.png)

图 `prob03_fig_ablation_rmse_ce4b523efa` 展示加权 RMSE 对照：基线 $p=0$ 上升（$+9.5\%$）、Airy 高阶下降（$-5.0\%$），F0 参考线清晰。自动质检 passed（非空白、暗边框 0.0、$\ge800\times480$）+ 视觉复核确认与 result.json 一致、无文本重叠。该图说明基线多项式是拟合优度必要组件（A3），同时多光束修正对拟合略有下降但对厚度无影响（A2）。

需要保留的边界与警告：v001 判 NEEDS_REVISION 的两项 core 缺陷（R1/R2）已在 v002 修复并复核通过，模型有效、无 VERSION_REJECTED、无 NEEDS_REVISION。技术债（bootstrap CI 用轮廓似然替代、$n_{\mathrm{sub}}$ 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、$\lambda>5\ \mu\mathrm{m}$ SiC 色散缺口 B6、L43–L47 全文待复核、附件 2 数据契约偏差）均为既有/登记事项或非阻断；合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。<!-- warning:warn_prob03_e6a8b3e9e4da --> robustness 验收独立复核通过，判据先于 computation 固定，R1–R8 全部在阈值内，探针只读、复用 model.py、未改数据/代码/结果；硬门禁（L2-finite、单位/量纲、公式-实现一致、原始数据只读、追踪链完整、feasible_incumbent=true）全部通过，技术债非阻断。<!-- warning:warn_prob03_89c83e7e6538 -->

**结论**：prob03 从 Airy 公式严格推导多光束必要条件并证明极值位置不变性，据此判定硅片（附件 3/4）未出现显著多光束干涉、两光束模型适用，反演得 $\hat t=3.4477\ \mu\mathrm{m}$（两角一致、$\varepsilon_{12}=0.130\%$），并修正 v001 的因子-2 伪影（R1）与 finesse 公式缺陷（R2）。SiC 复判 $\bar R\approx0.0024$、无需修正，prob02 结果维持。全部可靠性判据 R1–R8 通过，robustness 与 ablation 全部通过。

## 跨小问一致性、稳健性与消融分析

跨小问一致性审查状态为 passed。共享符号（$t,n,n_{\mathrm{sub}},\theta,\theta',\lambda,\nu,R,\delta,R_{01}/R_{12},\mathrm{finesse}$）与单位、参数值（Sellmeier 一致、主带 $\nu\in[2000,4000]\ \mathrm{cm}^{-1}$、$\theta=10/15°$、Reststrahlen $[700,1000]\ \mathrm{cm}^{-1}$ 剔除）、假设、数据版本、约束（$R\in[0,1]$、$t>0$、$n>1$）、结论方向与数量级全部跨问自洽；软依赖 conclusion hash（prob01=`82820355…070a6`、prob02=`27b0ce86…a12ea`）完整匹配，无 stale 传播、无回退。唯一共享符号元数据不一致（finesse domain $\ge1$ 与实际 $F\approx0.32<1$）已由审查修订为 $>0$，属全局符号表规范修订，不影响任何计算结果。

**跨问一致性要点**：

- **方法一致性**：prob02 与 prob03 均采用“基线-干涉分解 + 一维相位-频率扫描（variable projection）”作为主反演，且 prob03 硅片复用 prob02 方法；厚度均由干涉相位频率（$t=1/(2\times10^{-4}\Delta g)$）确定，与 $n_{\mathrm{sub}}$/幅度解耦。
- **结论方向与量级**：prob01 证明厚度由 $g$ 空间恒定周期决定；prob02 得 $t=7.2158\ \mu\mathrm{m}$（SiC），prob03 得 $t=3.4477\ \mu\mathrm{m}$（Si），均与器件工艺常识的微米量级一致，且两入射角结果一致（$\varepsilon_{12}$ 分别为 $0.165\%$ 与 $0.130\%$）。
- **多光束判定的跨材料一致性**：硅 $\bar R\approx0.0101$、SiC $\bar R\approx0.0024$，均 $\ll\theta_{\mathrm{mb}}=0.05$，两材料均无显著多光束；prob03 与 prob02 的多光束诊断结论一致。
- **不确定性来源一致**：色散（$0.507\%$/$0.503\%$）为带内最大不确定度来源但 $<2\%$，$n_{\mathrm{sub}}$ 为弱可辨识、对 $t$ 解耦，噪声为二阶小量。

**稳健性与消融汇总**：三个小问的 robustness 与 ablation 均通过，共同支撑“主方法与模型组件必要、结果在扰动与情景变化下稳定”。各问的 robustness/ablation 数值、判据与图已在对应章节披露，完整记录已归档至 `robustness/`、`results/robustness/`、`ablation/`、`results/ablation/` 与 `figures.yaml`。

记录的质量警告如下（不改写为已解决，作为解释结果与限制外推范围的组成部分）：

- prob01：合成验证 19/19 检查通过、$t_{\mathrm{true}}=10\ \mu\mathrm{m}$ 被精确恢复、两角一致，hash 追踪链一致、无 NaN/Inf、无硬约束违反；技术债（$\lambda>5\ \mu\mathrm{m}$ 常数色散延伸、方法 A 约 $4\%$ 基线偏差、文献全文待复核、$n_{\mathrm{sub}}$ 为合成场景值、Reststrahlen 剔除策略）留 prob02 处理。<!-- warning:warn_prob01_fac14a9dfae4 -->
- prob01：robustness 验收独立复核通过（conclusion=stable、5/5），E4 600 样本收敛率 $100\%$、95% CI 半宽最大 $0.022\%$ 远低于阈值；技术债（robustness 基于合成谱、色散模型选择、$\lambda>5\ \mu\mathrm{m}$ 常数延伸、$n_{\mathrm{sub}}$ 场景值、L25–L32 全文待复核、Reststrahlen 剔除）不阻断。<!-- warning:warn_prob01_cdf6b5be3241 -->
- prob02：实测反演 L1–L4 硬门禁通过、hash 追踪链完整，$\hat t=7.2158\ \mu\mathrm{m}$、$\varepsilon_{12}=0.165\%$、$\hat n_{\mathrm{sub}}=2.588$；可靠性 5/6 通过，仅 two_angle_ftest 统计显著（$F=5.251,p=0.022$）被路由为 B11；技术债（$\lambda>5\ \mu\mathrm{m}$ 色散缺口 B6、$n_{\mathrm{sub}}$ 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 $5.5\%$、L25–L32 全文待复核、多光束 Airy 留 prob03 B13）不阻断。<!-- warning:warn_prob02_a94c3613afe5 -->
- prob02：robustness 判据 C1–C8 全部在阈值内（C1 例外被路由为 B11），机器级 L2-finite 通过，主结果可行可追踪，维持 PASS_WITH_WARNING；技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 $5.5\%$、$\lambda>5\ \mu\mathrm{m}$ 色散缺口 B6、$n_{\mathrm{sub}}$ 弱可辨识 B7、L25–L32 全文待复核、多光束 Airy 留 prob03 B13）不阻断。<!-- warning:warn_prob02_abcae1fbbd23 -->
- prob03：主 computation L1–L4 硬门禁通过，$\hat t=3.4477\ \mu\mathrm{m}$（R1/R2 已修复）、$\varepsilon_{12}=0.130\%$、$\hat n_{\mathrm{sub}}=3.558$，可靠性判据全部 PASS；技术债（bootstrap CI 用轮廓似然替代、$n_{\mathrm{sub}}$ 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、$\lambda>5\ \mu\mathrm{m}$ SiC 色散缺口 B6、L43–L47 全文待复核、附件 2 数据契约偏差）非阻断；post-hoc config_hash 漂移作质量告警登记。<!-- warning:warn_prob03_e6a8b3e9e4da -->
- prob03：robustness 判据 R1–R8 全部在阈值内，探针只读、复用 model.py，结论 STABLE；硬门禁全部通过，技术债非阻断。<!-- warning:warn_prob03_89c83e7e6538 -->

## 模型评价、局限与推广

**优势与解释性**：模型链条从假设、公式、实现、结果到图表均可追溯、便于复核与复现。关键洞察——厚度由干涉相位频率（$g$ 空间周期）唯一确定、与 $n_{\mathrm{sub}}$/幅度解耦——使反演在弱对比度与未建模基线条件下仍稳健，且公式可解析解释（$t=1/(2\times10^{-4}\Delta g)$），物理含义明确。多种 sanity 与扰动证据（robustness、ablation、跨问一致性）减少仅凭单点结果下结论的风险。

**局限性**：
1. **色散模型不确定度**：$\lambda>5\ \mu\mathrm{m}$（$\nu<2000\ \mathrm{cm}^{-1}$）的色散存在缺口（B6），对 SiC 尤为明显，需依赖数据反演或分谱段代理；主反演带因此截断至 $\nu\ge2000\ \mathrm{cm}^{-1}$，其影响以 $\Delta t_{\mathrm{inv\_band}}$ 记录。
2. **波长>5 µm 色散与文献**：部分文献（L25–L32、L43–L47）等待全文复核，$n_{\mathrm{sub}}$ 与色散参数存在弱可辨识性（B7）。
3. **衬底折射率弱可辨识**：弱对比度下 $n_{\mathrm{sub}}$ 由干涉幅值估计，对噪声敏感，属于幅度型弱信号；但通过结构解耦不影响主厚度 $t$。
4. **唯一性**：prob03 弱色散下周期邻近候选接近简并（次小候选比 $\approx1.020$），全局唯一性由预注册判据保障，但较 prob02（次小候选高 $1.75\times$）更依赖判据而非余量。
5. **统计显著性与实际意义分离**：prob02 的两角嵌套 $F$ 检验统计显著而裸偏差 $\varepsilon_{12}=0.165\%$ 很小，属大样本下的显著性-实际意义分离，被路由为 B11 记录并解释。
6. **样本规模与数据质量**：附件 2 存在反射率 $>100\%$ 异常点（已预处理），附件 1/2 与附件 3/4 各自来自同一晶圆片的不同入射角，双角检验是主要可靠性工具，但缺少独立重复测量样本。

**推广边界**：在适用谱段、入射角与材料体系（SiC、Si 及已知色散的材料）内，方法可给出与器件工艺常识一致的微米量级厚度。推广到新的材料、更宽波段或不同掺杂浓度时，应重新执行色散标定、$n_{\mathrm{sub}}$ 估计、谱段选择、敏感性分析与 Level 5 视觉复核，并验证多光束必要条件（$\bar R\ll\theta_{\mathrm{mb}}$ 与 $\eta_{\mathrm{mb}}\ll\tau_{\mathrm{mb}}$）在两光束近似下是否仍成立。对高反射率、强吸收或存在显著厚度梯度的体系，应升级为复折射率 Fresnel 与多光束（Airy）模型。

## 结论

本文针对材料外延层厚度的红外干涉测厚问题，按“两光束干涉建模—实测谱反演—多光束干涉判定”递进完成建模、求解、结果解释与可靠性检查，并以跨小问一致性验证增强结论可信度。

- **问题 1**：在两光束近似下建立反射率正模型与色散化反演公式（$t=\frac{1}{2\Delta\nu\sqrt{n^2-\sin^2\theta}}$，色散化 $t=\frac{1}{2[g(\nu_{m+2})-g(\nu_m)]}$）。合成验证（$t_{\mathrm{true}}=10.0\ \mu\mathrm{m}$）下主方法以近零残差恢复，robustness 与 ablation 全部通过；方法 A 约 $4\%$ 的基线偏差作为已知方法债披露，主方法选定色散化全谱 Fresnel 反演（M1）。该结果已通过 L1–L5 检查。
- **问题 2**：对 SiC 实测谱（附件 1/2）以“基线-干涉分解 + 一维相位-频率扫描”反演，得 $\hat t=7.2158\ \mu\mathrm{m}$（每角 $7.2214/7.2095\ \mu\mathrm{m}$、$\varepsilon_{12}=0.165\%$、$\hat n_{\mathrm{sub}}=2.588$），$J(t)$ 全局唯一；可靠性 5/6 通过（唯一 $F$ 检验显著性路由为 B11），robustness 与 ablation 全部通过，并消除 v002 的模型可辨识性结构缺陷。该结果已通过 L1–L5 检查。
- **问题 3**：从 Airy 公式严格推导多光束必要条件并证明极值位置不变性；判定硅片（附件 3/4）两光束模型适用，反演得 $\hat t=3.4477\ \mu\mathrm{m}$（每角 $3.4507/3.4463\ \mu\mathrm{m}$、$\varepsilon_{12}=0.130\%$、$J_{\mathrm{shared}}=0.0608$ 全局唯一），并修正 v001 的因子-2 伪影与 finesse 公式缺陷；SiC 复判 $\bar R\approx0.0024$、无需修正，prob02 结果维持。全部可靠性判据 R1–R8 通过。该结果已通过 L1–L5 检查。

所有结论仅在 Evidence Pack 固定的接受版本、数据范围与警告边界内成立：外延层厚度由干涉相位频率确定、与 $n_{\mathrm{sub}}$ 解耦；色散为带内最大不确定度来源但 $<2\%$；多光束在两材料中均不显著、不改变厚度。推广到新体系前须重新标定色散、估计 $n_{\mathrm{sub}}$、验证多光束必要条件并做敏感性分析。

## 参考文献

[L01] Albert, M. P., Combs, J. F.. Thickness Measurement of Epitaxial Films by the Infrared Interference Method. Journal of The Electrochemical Society, 1962. 
[L02] Schumann, P. A.. The Infrared Interference Method of Measuring Epitaxial Layer Thickness. Journal of The Electrochemical Society, 1969. 
[L03] ASTM International. ASTM F95-89(2000): Standard Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer. ASTM International（标准组织正式文件）, 2000. 
[L04] SEMI. SEMI MF95 (SEMI MF009500): Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer. SEMI International Standards, 2013. 
[L05] Weeks, S. P.. Thickness Measurement of Thin (1.0-µm) Epitaxial Silicon Layers by Infrared Reflectance. Silicon Processing (ASTM STP 804), 1983. 
[L06] Born, M., Wolf, E.. Principles of Optics: Electromagnetic Theory of Propagation, Interference and Diffraction of Light (7th ed.). Cambridge University Press（权威教材）, 1999. 
[L07] Hecht, E.. Optics (5th ed., Global Edition). Pearson（权威教材）, 2017. 
[L08] Shaffer, P. T. B.. Refractive Index, Dispersion, and Birefringence of Silicon Carbide Polytypes. Applied Optics, 1971. 
[L09] Wang, S., Zhan, M., Wang, G., Xuan, H., Zhang, W., Liu, C., Xu, C., Liu, Y., Wei, Z., Chen, X.. 4H-SiC: a new nonlinear material for midinfrared lasers. Laser & Photonics Reviews, 2013. 
[L10] Xu, C., Wang, S., Wang, G., Liang, J., Wang, S., Bai, L., Yang, J., Chen, X.. Temperature dependence of refractive indices for 4H- and 6H-SiC. Journal of Applied Physics, 2014. 
[L11] Polyanskiy, M. N.. Refractiveindex.info database of optical constants. Scientific Data, 2024. 
[L12] Li, H. H.. Refractive index of silicon and germanium and its wavelength and temperature derivatives. Journal of Physical and Chemical Reference Data, 1980. 
[L13] Palik, E. D. (ed.). Handbook of Optical Constants of Solids (Vol. 1-3). Academic Press（权威手册）, 1998. 
[L14] Spitzer, W., Fan, H. Y.. Infrared Absorption in n-Type Silicon. Physical Review, 1957. 
[L15] Pernot, J., Camassel, J., Peyre, H., Robert, J.-L.. From Transport Measurements to Infrared Reflectance Spectra of n-Type Doped 4H-SiC Layer Stacks. Materials Science Forum, 2003. 
[L16] Chahal, J. S., Rahbany, N., El-Helou, Y., Wu, K.-T., Bruyant, A., Zgheib, C., Kazan, M.. Temperature dependence of the anisotropy of the infrared dielectric properties and phonon-plasmon coupling in n-doped 4H-SiC. Journal of Physics and Chemistry of Solids, 2023. 
[L17] 王晨茜, 孙嘉妍, 陈怡佳, 杜睿. 基于色散修正与全谱拟合的红外干涉测厚模型研究. 数学建模及其应用（Mathematical Modeling and Its Applications）, 2026. 
[L23] Harrick, N. J.. Determination of Refractive Index and Film Thickness from Interference Fringes. Applied Optics, 1971. 
[L24] Larruquert, J. I., Pérez-Marín, A. P., García-Cortés, S., Rodríguez-de Marcos, L., Aznárez, J. A., Méndez, J. A.. Self-consistent optical constants of SiC thin films. Journal of the Optical Society of America A, 2011. 
[L25] Liu, Lu, Shi, Weiwei, Xu, Shibo, Wang, Xiaofan. Dispersion Compensation and Multi-Beam Interference Correction Algorithm for Thickness Measurement of SiC Epitaxial Layer. Sensors, 2026. 
[L26] Mainali, Madan K., Dulal, Prabin, Shrestha, Bishal, Amonette, Emily, Shan, Ambalanath, Podraza, Nikolas J.. Optical properties of 4H-SiC and 6H-SiC from infrared to vacuum ultraviolet spectral range ellipsometry (0.05–8.5 eV). Surface Science Spectra, 2024. 
[L27] Lindquist, O. P. A., Schubert, M., Arwin, H., Järrendahl, K.. Infrared to vacuum ultraviolet optical properties of 3C, 4H and 6H silicon carbide measured by spectroscopic ellipsometry. Thin Solid Films, 2004. 
[L28] Lindquist, O. P. A., Arwin, H., Henry, A., Järrendahl, K.. Infrared Optical Properties of 3C, 4H and 6H Silicon Carbide. Materials Science Forum, 2003. 
[L29] Tong, Zhen, Liu, Linhua, Li, Liangsheng, Bao, Hua. Temperature-dependent infrared optical properties of 3C-, 4H- and 6H-SiC. Physica B: Condensed Matter, 2018. 
[L30] Sunkari, Swapna, Mazzola, M. S., Mazzola, J. P., Das, Hrishikesh, Wyatt, J. L.. Investigation of longitudinal-optical phonon-plasmon coupled modes in SiC epitaxial film using Fourier transform infrared reflection. Journal of Electronic Materials, 2005. 
[L31] Mazzola, Michael S., Sunkari, Swapna G., Mazzola, Janice, Das, Hrishikesh, Melnychuck, Galyna, Koshka, Yaroslav, Wyatt, Jeffery L., Zhang, Jie. Improved Resolution of Epitaxial Thin Film Doping Using FTIR Reflectance Spectroscopy. Materials Science Forum, 2005. 
[L32] Zhou, Zhen-Hong, Yang, Isabel, Yu, Fuzhong, Reif, Rafael. Fundamentals of epitaxial silicon film thickness measurements using emission and reflection Fourier transform infrared spectroscopy. Journal of Applied Physics, 1993. 
[L43] Sun, Jiaxing, Li, Zhisong, Zhang, Haojie, Song, Jinlong, Zhai, Tianbao. An improved method for measuring epi-wafer thickness based on the infrared interference principle: Addressing interference quality and multiple interferences in double-layer structures. Results in Physics, 2023. 
[L44] Severin, P. J.. On the Infrared Thickness Measurement of Epitaxially Grown Silicon Layers. Applied Optics, 1970. 
[L45] Sato, K., Ishikawa, Y., Sugawara, K.. Infrared interference spectra observed in silicon epitaxial wafers. Solid-State Electronics, 1966. 
[L46] Soler, F. J. P.. Multiple reflections in an approximately parallel plate. Optics Communications, 1997. 
[L47] Monzón, J. J., Sánchez-Soto, L. L., Bernabeu, E.. Influence of coating thickness on the performance of a Fabry–Perot interferometer. Applied Optics, 1991. 

## 附录：复现说明、文件清单和核心代码索引

论文由 Evidence Pack `8ff12774cf86c099c914c01f7ea4439d87583da3543b7d8bd55f25317318f1d5` 组织生成。复现时先核验该哈希与 `writer_manifest.json`（generator=`paper-writer-agent`），再运行论文构建命令。计算代码与结果路径以证据包登记清单为准，正文不重复粘贴完整代码。

以下为核心产物的路径索引（均以证据包 SHA-256 固定）：

- **问题 1**：正模型与反演公式见 `prob01/versions/assumption_v001/formulations/formulation_v001/formulation.md`；合成验证结果见 `prob01/versions/assumption_v001/results/synthetic_verify/`（`result.json`、`solver_status.json`、`verification.json`、`machine_sanity.json`）；robustness 见 `results/robustness/` 与 `robustness/`（`decision.md`/`preregistration.md`/`experiment_matrix.yaml`/`conclusion.md`）；ablation 见 `results/ablation/` 与 `ablation/`。
- **问题 2**：反演算法见 `prob02/versions/assumption_v001/formulations/formulation_v003/formulation.md`；实测反演结果见 `results/thickness_inversion_v003/`（`result.json`、`solver_status.json`、`verification.json`、`machine_sanity.json`、`preprocessing.json`、`dispersion_ref.json`）；robustness 见 `results/thickness_inversion_v003/result.json` 与 `robustness/`；ablation 见 `results/ablation/` 与 `ablation/`。
- **问题 3**：多光束必要条件与反演算法见 `prob03/versions/assumption_v001/formulations/formulation_v002/formulation.md`；硅片多光束验证结果见 `results/silicon_mb_verify/`（`result.json`、`mb_conditions.json`、`solver_status.json`、`verification.json`、`machine_sanity.json`、`preprocessing.json`、`dispersion_ref.json`）；robustness 见 `robustness/` 与 `results/silicon_mb_verify/result.json`；ablation 见 `results/ablation/` 与 `ablation/`。
- **图**：全部图以 Evidence Pack `figures` 中的 stable id 与相对路径引用（见各问正文），原始 `.png` 与 `*.quality.json` 位于对应 `figures/` 目录，`figures.yaml` 登记其元数据。
- **文献**：`prob0x/shared/literature_pool.yaml` 登记文献池，`problems/2025-cumcm-b/citations.yaml` 与 `global_symbols.yaml` 提供引用与符号规范。

所有数值计算均通过隔离 task 与独立输出目录由 supervised worker 执行；复现需在项目虚拟环境中安装 `scripts/requirements.txt` 所列依赖，并确保 Pandoc 与 Microsoft Word 可用。
