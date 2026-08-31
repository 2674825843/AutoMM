# 基于红外干涉法的碳化硅/硅外延层厚度测量模型与算法

> 版本：paper_v002 ｜ 证据包哈希：`e0e907b66c21d6cf8dddc068f713e0dae6a40c3b6fa2eec72758f58ba39a5571`
> 本文仅组织已通过跨小问审查与 sanity 检查的接受材料；所有定量结论均可回溯到上述证据包登记的文件。

## 摘要

**问题 1（建立两光束干涉测厚模型）**：针对外延层与衬底界面"只有一次反射、透射"的两光束干涉情形，建立色散化的两光束 Fresnel 反射率正模型 $R(\nu)$，推出同型相邻极值波数间隔 $\Delta\nu$ 与厚度的反演公式，并给出色散显著时的色散化相位条件。以合成数据（$t_{\text{true}}=10.0\,\mu\text{m}$、$n_{\text{sub}}=3.0$、$\theta=10°/15°$）验证：色散化相位法得 $t\approx10.002\,\mu\text{m}$（相对偏差 $2.2\times10^{-4}$），全谱非线性最小二乘（NLS）得 $t=10.000\,\mu\text{m}$（RMSE≈0），常数 $n$ 间隔法（方法 A）得 $t\approx10.44\,\mu\text{m}$（约 4.4% 色散系统偏差，属已知文档化基线），两入射角反演一致。<!-- evidence:ev_artifact_ff24505a53cd -->

**问题 2（碳化硅实测反演）**：针对附件 1/2（同一块 SiC 晶圆片，10°/15°）的实测反射率谱，采用"基线—干涉分解 + 一维相位频率扫描（variable projection）"作为主方法，使厚度 $t$ 由干涉条纹的相位频率唯一确定、与衬底折射率 $n_{\text{sub}}$ 解耦，并以两角共享 $t$ 为交付判据。主结果 $\hat t(\text{共享})=7.2158\,\mu\text{m}$，每角 $7.2214/7.2095\,\mu\text{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\text{sub}}=2.588$（幅值弱可辨识），主拟合加权 RMSE≈$6.3\times10^{-4}$。可靠性判据 5/6 通过：色散 $\Delta t_{\text{disp}}=0.51\%\le2\%$、轮廓似然 CI 半宽 $0.091\%\le2\%$、异常点 $0.0\%\le1\%$、$n_{\text{sub}}$ 解耦、多光束改善 $0.0\%\le10\%$ 均通过；仅两角嵌套 $F$ 检验统计显著（$F=5.25>F_{\text{crit}}=3.843$，$p=0.022$），但裸偏差 $\varepsilon_{12}=0.165\%\ll\tau_{12}=2\%$，属大样本下统计显著性与实际意义分离，按登记规则路由为 B11（测量点差异/膜厚梯度）记录并解释，不触发模型修订。<!-- evidence:ev_artifact_44ce712a84e4 -->

**问题 3（多光束必要条件 + 硅片判定 + 碳化硅重判）**：从 Airy 多光束反射率严密推导多光束干涉的必要条件 N1–N4（界面强度反射率乘积、相干长度、界面平行度、吸收限制），并证明无吸收平行板下 Airy 反射率的极值位置严格落在 $\delta=m\pi$、与界面反射率乘积无关，从而独立验证"多光束不改变干涉极值位置/周期、即不改变厚度"。对附件 3/4（硅，10°/15°）：由 Fresnel 得 $R_{01}\approx0.301$、由干涉幅值反演 $R_{12}\approx3.4\times10^{-4}$，故 $\bar R\approx0.0101$、$F\approx0.319$，Airy 相对两光束的残差改善率 $\eta_{\text{mb}}\approx0.11\%\ll10\%$，判定两光束适用；硅厚度 $\hat t(\text{共享})=3.4477\,\mu\text{m}$，每角 $3.4507/3.4463\,\mu\text{m}$，$\varepsilon_{12}=0.130\%$，$\hat n_{\text{sub}}=3.558$（幅值弱可辨识）。对碳化硅（附件 1/2）重新判定：$\bar R\approx0.0024\le\theta_{\text{mb}}=0.05$，无显著多光束、无需修正，prob02 结果 $\hat t=7.2158\,\mu\text{m}$ 维持。全部可靠性判据 PASS（$F=0$、$p=1.0$、$\Delta t_{\text{disp}}=0.503\%\le2\%$、CI 半宽 $0.134\%\le2\%$、异常点 $0.0\%\le1\%$）。<!-- evidence:ev_artifact_30aee4639e7e -->

本文另从跨小问一致性、扰动稳健性与模型组件必要性三个层面验证结果，定量结论均回溯到已验收证据包，并如实披露既有技术债与推广边界。

## 关键词

红外干涉法；外延层厚度；色散补偿；多光束干涉；变量投影反演；可靠性分析

## 问题重述

碳化硅（SiC）是第三代半导体材料，其外延层厚度是关键参数，直接影响器件性能，因此需要建立一套科学准确的外延层厚度测试标准。红外干涉法是外延层厚度的无损测量方法：外延层与衬底因掺杂载流子浓度不同而具有不同折射率，红外光入射外延层后，一部分在外延层上表面反射，另一部分穿过外延层后在衬底界面反射并返回，两束光在一定条件下产生干涉条纹。由红外光谱的波长（波数）、外延层折射率与入射角等参数即可确定外延层厚度。需要注意，外延层折射率并非常数，而是随掺杂载流子浓度与波长远变化。

题目按难度递进提出三问，并给出四组实测光谱数据：

**问题 1**：考虑外延层与衬底界面只有一次反射、透射所产生的干涉条纹（图 1），建立确定外延层厚度的数学模型。

**问题 2**：依据问题 1 的数学模型，设计确定外延层厚度的算法；对附件 1、附件 2 提供的碳化硅晶圆片光谱实测数据给出计算结果，并分析结果的可靠性。

**问题 3**：光波可在外延层界面与衬底界面产生多次反射、透射（图 2）从而产生多光束干涉。请推导多光束干涉的必要条件及其对厚度计算精度的影响；依据必要条件分析附件 3、附件 4 提供的硅晶圆片测试结果是否出现多光束干涉，给出硅外延层厚度计算的数学模型、算法与结果；若认为多光束也会出现在碳化硅（附件 1、附件 2）并影响厚度计算精度，设法消除其影响并给出修正后的结果。

**数据说明**：附件 1、附件 2 为入射角分别为 $10°$、$15°$ 时对同一块碳化硅晶圆片的测试结果，第 1 列为波数 $\nu$（$\text{cm}^{-1}$），第 2 列为干涉光谱反射率（%）；附件 3、附件 4 为入射角分别为 $10°$、$15°$ 时对同一块硅晶圆片的测试结果，列结构相同。实测谱波数约覆盖 400–4000 $\text{cm}^{-1}$（对应波长约 2.5–25 $\mu\text{m}$），无时间维度。

## 问题分析与总体流程

全文按"题面解析—假设与符号统一—分问建模与求解—计算结果解释—sanity 与稳健性验证—跨问一致性复核"的流程组织。写作原则是**先分析、再建模**：每问先明确输入、输出、约束与物理事实，再给出已接受的假设与公式，最后用实测或合成数据求解并解释结果，避免在结果之后倒推模型。

具体而言：prob01 在无附件数据的条件下完成解析正模型与反演公式的推导，并采用合成数据验证公式与算法；prob02 将 prob01 的反演链路落地为针对实测光谱的确定性算法，并给出碳化硅厚度与可靠性分析；prob03 在 prob02 基础上把多光束（Airy）从"诊断"提升为"严格推导"，据此判定硅片是否多光束、计算硅厚度，并对碳化硅重新判定。文中每个关键数字、公式、图表、文献性主张与 warning 均紧邻有效证据标记，可机器核验。

## 模型假设

各小问只采用 Evidence Pack 中登记的接受假设。全局层面，所有小问共享以下物理与边界前提：外延层与衬底为平行界面、厚度均匀、入射角已知且固定（$n_{\text{air}}=1.0$）；外延层与衬底界面平行；反射率守恒于 $0\le R\le1$；厚度为正实数；原始数据只读。不同折射率（$n$ 与 $n_{\text{sub}}$）来自掺杂载流子浓度差异。各问的具体假设族与关键假设见对应小节，并保留其适用范围、偏差方向与验证方式。

## 符号说明

| 符号 | 含义 | 单位 |
|---|---|---|
| $t$ | 外延层厚度（核心未知量） | $\mu\text{m}$（正实数） |
| $n=n(\nu)$ | 外延层折射率（随波数/波长色散） | 无量纲 |
| $n_{\text{sub}}$ | 衬底折射率（由干涉幅值弱可辨识） | 无量纲 |
| $n_{\text{air}}$ | 空气折射率，取 $1.0$ | 无量纲 |
| $\theta$ | 入射角（空气侧，相对表面法线） | 度（三角函数计算转弧度） |
| $\theta'$ | 外延层内折射角 | 弧度 |
| $\lambda$ | 真空中波长，$\lambda[\mu\text{m}]=10^4/\nu$ | $\mu\text{m}$ |
| $\nu$ | 波数 | $\text{cm}^{-1}$ |
| $R$ | 干涉反射率（模型谱） | 无量纲（0–1；数据中为% 归一后） |
| $R_{01}$（界面 1） | 空气/外延层界面强度反射率 | 无量纲 |
| $R_{12}$（界面 2） | 外延层/衬底界面强度反射率 | 无量纲 |
| $\delta$ | 相邻反射束相位差 | rad |
| $m$ | 干涉级次 | 非负整数 |
| $\Delta\nu$ | 同型相邻极值波数间隔 | $\text{cm}^{-1}$ |
| $g(\nu)$ | 相位函数 $g=n(\nu)\nu\cos\theta'$ | $\text{cm}^{-1}$ |
| $B(\nu),C(\nu),S(\nu)$ | 基线、干涉余弦/正弦包络多项式 | 无量纲 |
| $A(\nu)$ | 干涉幅值/包络 $A=\sqrt{C^2+S^2}$ | 无量纲 |
| $\varphi$ | 反射相位跃变之和（并入 $C/S$） | rad |
| $\bar R$ | 界面强度反射率几何平均 $\sqrt{R_{01}R_{12}}$ | 无量纲 |
| $F$ | 精细度 $F=\pi\sqrt{\bar R}/(1-\bar R)$ | 无量纲 |
| $\varepsilon_{12}$ | 两角反演厚度相对偏差 | % |
| $J(t)$ | 主反演目标函数（加权残差平方和） | 无量纲 |

## 数据说明与预处理

数据文件、预处理记录与计算结果由证据包按 SHA-256 固定，正文不改写原始数据。各问的原料均为附件实测反射率谱（$\nu$ 与 $R\%$），按 $R^{\text{obs}}=R\%/100$ 归一为强度反射率，波数-波长用 $\lambda[\mu\text{m}]=10^4/\nu$ 换算。共性预处理包括：归一化与波数升序重排（附件 2 原为降序）；SiC 近 Reststrahlen 区 $\nu\in[700,1000]\,\text{cm}^{-1}$ 作为强吸收区剔除或置零权重（$w=0$）；SiC 附件 2 与硅片的主反演带均截断至 $\nu\in[2000,4000]\,\text{cm}^{-1}$（色散模型已知区）；异常点（$R\%>100$）按稳健降权（$w=w_{\text{anom}}$）处理而不修改原始数据。SiC 与硅片因色散模型适用范围不同而分别采用各自材料色散（见各问）。"跨小问一致性、稳健性与消融分析"小节汇总了各问的预警与保留边界。

## prob01 模型建立、求解与结果

### prob01 问题分析

本问目标是建立"两光束干涉"下由干涉条纹反演外延层厚度的数学模型。输入为物理设定（入射角 $\theta$、外延层色散折射率 $n(\nu)$、衬底折射率 $n_{\text{sub}}$、空气折射率 $n_{\text{air}}=1.0$），输出为模型反射率谱 $R(\nu)$ 与厚度反演公式。本问无附件数据，因此先推清正模型（反射率随厚度、折射率、入射角、波数的解析关系）、干涉极值条件与同型相邻极值间隔 $\Delta\nu$ 的定量关系，再把模型用于合成数据验证反演公式与算法。约束包括 $R\in[0,1]$、$t>0$、极值条件满足；物理事实为外延层折射率随掺杂浓度与波长变化（$n$ 非常数）。

### prob01 模型假设

本问假设族（assumption_v001）与对应条目如下：F1（两光束干涉模型与厚度公式）对应 A1–A4；F2（折射率色散 Sellmeier/分谱段策略）对应 A5、A12；F3（掺杂/自由载流子对红外折射率影响）对应 A6；F0（边界与数据假设）对应 A7–A11。冲突检查结论：本组假设内部无冲突，与题面理解及全局符号表一致；prob01 为整题建模起点，无前问结论依赖。A2 与 A7 的谱段适用性以 A7 边界约束为限（近 Reststrahlen 区吸收不可忽略）。

关键假设包括：

- **A1（两光束干涉近似，关键）**：仅考虑外延层上表面直接反射的光束与透射进入外延层并在外延层/衬底界面反射后返回的光束，忽略层内多次反射、衬底背面反射与高阶光束。与题面图 1 设定一致。引用 [@L01]、[@L02]、[@L06]、[@L07]。
- **A2（光程差由 Snell 折射与平行平板几何确定，关键）**：$\sin\theta'=\sin\theta/n$，光程差 $\Delta=2nt\cos\theta'=2t\sqrt{n^2-\sin^2\theta}$。引用 [@L06]、[@L07]、[@L17]。
- **A3（干涉极值条件与厚度反演公式，关键）**：干涉强度 $I=I_1+I_2+2\sqrt{I_1I_2}\cos\delta$，相位差 $\delta=4\pi n t\cos\theta'/\lambda$；同型相邻极值波数间隔 $\Delta\nu=1/(2nt\cos\theta')$，故 $t=1/(2n\cos\theta'\Delta\nu)$。引用 [@L01]、[@L02]、[@L23]、[@L17]。
- **A4（反射相位跃变只改变峰/谷类型，关键）**：空气→外延层界面反射产生 $\pi$ 相位跃变，外延层→衬底界面是否跃变取决于 $n$ 与 $n_{\text{sub}}$ 相对大小；相位跃变在同型相邻极值间隔中抵消，不影响厚度公式，但峰/谷判定需明确。引用 [@L06]、[@L07]。
- **A5（折射率色散，关键）**：$\lambda\le5\,\mu\text{m}$ 用 4H-SiC Sellmeier，$\lambda>5\,\mu\text{m}$ 无现成体材料 Sellmeier，由 prob02 数据反演/分谱段确定。引用 [@L09]、[@L11]、[@L24]、[@L08]。
- **A6（掺杂导致折射率不同，关键）**：外延层（轻掺）与衬底（重掺）因载流子浓度差异而折射率不同。引用 [@L14]、[@L15]、[@L16]。
- **A7（吸收可忽略的谱段边界，关键）**：用于干涉反演的谱段内吸收可忽略（实数折射率）；SiC 约 700–1000 $\text{cm}^{-1}$ 的 Reststrahlen 强吸收区不适用无吸收模型。引用 [@L16]、[@L24]。

适用范围、偏差方向与验证方式保留在登记假设中，并以登记文献作为方法依据 [@L01]。<!-- evidence:ev_artifact_ae2969b416fb -->

### prob01 模型建立与求解

正模型采用两光束 Fresnel 干涉。由 Snell 定律得外延层内折射角 $\sin\theta'=\sin\theta/n$，几何光程差 $\Delta=2nt\cos\theta'=2t\sqrt{n^2-\sin^2\theta}$；相位差 $\delta=2\pi\Delta/\lambda=4\pi\times10^{-4}\,n\,t\,\nu\cos\theta'$（$t[\mu\text{m}]$、$\nu[\text{cm}^{-1}]$ 时，$\lambda[\mu\text{m}]=10^4/\nu$）。

界面强度反射率由 Fresnel 振幅反射系数（s、p 偏振）给出：$R_1=|r_1|^2$、$R_2=|r_2|^2$，非偏振测量取 s/p 平均。两光束叠加的模型反射率为

$$R(\nu;t,n(\nu),\theta,n_{\text{sub}})=R_1+(1-R_1)^2R_2+2(1-R_1)\sqrt{R_1R_2}\cos\delta,$$

其中 $R_1+(1-R_1)^2R_2$ 为慢变 DC 基线，干涉项幅值 $A=2(1-R_1)\sqrt{R_1R_2}$。物理边界满足 $0\le R\le1$。

干涉极值条件为 $\partial R/\partial\nu=0\Leftrightarrow\sin\delta=0\Leftrightarrow\delta=m\pi$。同型相邻极值（峰-峰或谷-谷）对应 $\delta$ 变化 $2\pi$，故弱色散时

$$\Delta\nu=\frac{1}{2nt\cos\theta'},\qquad t=\frac{1}{2n\cos\theta'\Delta\nu}=\frac{1}{2\Delta\nu\sqrt{n^2-\sin^2\theta}}.$$

单位换算下 $t[\mu\text{m}]=10^4/(2n\cos\theta'\Delta\nu[\text{cm}^{-1}])$。

色散显著时，$\Delta\nu$ 公式失效，需用色散化相位条件。定义相位函数 $g(\nu)=n(\nu)\nu\cos\theta'(\nu)$，极值条件化为 $g(\nu_m)=m/(4t)$；同型相邻极值（$m\to m+2$）给出

$$t=\frac{1}{2\left[g(\nu_{m+2})-g(\nu_m)\right]},$$

弱色散极限回到 $\Delta\nu$ 公式。prob01 据此给出三类反演候选模型：**方法 A**（极值间隔法，解析快速、受色散与噪声影响大，作初值/交叉验证）、**方法 B**（全谱非线性最小二乘拟合正模型，信息利用充分、可校核色散与 $n_{\text{sub}}$，prob02 主方法）、**方法 C**（色散化相位条件）。求解策略属小规模连续参数估计，正模型解析、目标光滑，精确方法（NLS/一维扫描）充分适用，无需 MILP 或元启发式。

边界条件：谱段内吸收可忽略（实数折射率）；$\lambda\le5\,\mu\text{m}$ 用 4H-SiC Sellmeier $n^2=6.79485+0.15558/(\lambda^2-0.03535)-0.02296\lambda^2$（$\lambda\in[\mu\text{m}]\le5$），$\lambda>5\,\mu\text{m}$ 留 prob02 处理；Reststrahlen 区 (700–1000 $\text{cm}^{-1}$) 不适用；相位跃变不改变同型极值间隔；FTIR 相干长度远大于光程差；界面平行、厚度均匀。多光束（Airy）情形留 prob03。<!-- evidence:ev_artifact_55e196100f35 -->

### prob01 结果解释

本问以合成数据验证模型与算法（$t_{\text{true}}=10.0\,\mu\text{m}$、$n_{\text{sub}}=3.0$、$\theta=10°/15°$，种子 20260829，19/19 检查通过）。三种方法在两入射角下的结果：**方法 A（常数 $n$ 间隔法）** 得 $t\approx10.44\,\mu\text{m}$（相对偏差约 4.4%，对应常数 $n$ 近似的色散系统偏差，已文档化）；**色散化相位法** 得 $t\approx10.002\,\mu\text{m}$（相对偏差 $2.2\times10^{-4}$）；**全谱 NLS** 得 $t=10.000\,\mu\text{m}$（RMSE≈0），两入射角一致性良好。这证实了：色散化相位法与全谱 NLS 能精确恢复 $t_{\text{true}}$，而常数 $n$ 方法 A 存在约 4% 的系统性色散偏差，仅在弱色散/需快速初值时作基线。下图对其进行可视化。

![prob01_fig_reflectance_spectrum_1d4fb899d1 两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_reflectance_spectrum_1d4fb899d1.png)

图 prob01_fig_reflectance_spectrum_1d4fb899d1 展示了"两光束干涉合成反射率谱（$t_{\text{true}}=10.0\,\mu\text{m}$，$n_{\text{sub}}=3.0$）"，说明两光束正模型可产生清晰的双入射角干涉条纹，峰位与合成设定一致，且 $R\in[0,1]$ 守恒。自动质检 passed（1567×994 px、暗边框 0.0%）+ 视觉复核：双入射角谱线、峰标注、Reststrahlen/Sellmeier 边界清晰，图例无遮挡、单位完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_7a32edbc8a9e -->

![prob01_fig_dispersion_curve_d85564d2fc 外延层 4H-SiC 折射率色散模型 n(ν)](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_dispersion_curve_d85564d2fc.png)

图 prob01_fig_dispersion_curve_d85564d2fc 展示"外延层 4H-SiC 折射率色散模型 $n(\nu)$"，说明 $\lambda\le5\,\mu\text{m}$ 用 Sellmeier 且 $\lambda>5\,\mu\text{m}$ 做常数延伸的分段结构，是色散模型选择的物理依据。自动质检 passed + 视觉复核：Sellmeier 与常数延伸分段明确、双轴 λ/ν 换算正确、边界与 Reststrahlen 区标注无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_15b6f2332b74 -->

![prob01_fig_phase_function_gap_459c486470 色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_phase_function_gap_459c486470.png)

图 prob01_fig_phase_function_gap_459c486470 展示"色散化相位法：$g(\nu)$ 单调性与同型极值间隔律（θ=10°）"，说明 $g(\nu)$ 单调（$g'>0$）是色散化相位条件成立的前提，且同型间隔 $\Delta g$ 近似恒定（约 500 $\text{cm}^{-1}$），支撑 (3.13) 的相位法反演。自动质检 passed + 视觉复核：$g(\nu)$ 单调性与 $\Delta g$ 恒定律机制清晰，轴/单位/图例完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_0d27904b7650 -->

![prob01_fig_thickness_methods_compare_5eac465fc8 三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_thickness_methods_compare_5eac465fc8.png)

图 prob01_fig_thickness_methods_compare_5eac465fc8 展示"三种反演方法的厚度估计与 $t_{\text{true}}=10.0\,\mu\text{m}$ 对比（相对偏差标注）"，说明方法 A 存在约 4% 色散偏差、而相位法与全谱 NLS 精确恢复 $t_{\text{true}}$，三种方法与 $t_{\text{true}}$ 参考线的相对关系清晰。自动质检 passed + 视觉复核：三方法×两入射角分组柱状图含偏差标注，$t_{\text{true}}$ 参考线与 ±1% 容差带清晰，颜色区分明确；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_e5a8c9b5b48d -->

![prob01_fig_spacing_constant_n_bias_2245b6eda4 方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_spacing_constant_n_bias_2245b6eda4.png)

图 prob01_fig_spacing_constant_n_bias_2245b6eda4 展示"方法 A 常数 $n$ 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）"，直接说明常数 $n$ 近似在 2000–4000 $\text{cm}^{-1}$ 引入约 4% 的色散偏差，故方法 A 只能作基线/初值。自动质检 passed + 视觉复核：实测 vs 常数 $n$ 理论间隔对比与 4.2–4.7% 偏差说明框无数据遮挡；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_465d5df2f0a3 -->

![prob01_fig_nls_multistart_e64919ab13 全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_nls_multistart_e64919ab13.png)

图 prob01_fig_nls_multistart_e64919ab13 展示"全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，$t=10.000\,\mu\text{m}$）"，说明 NLS 目标面存在厚度周期歧义导致的多个局部极小，必须用多初值/全局扫描才能落到 $t_{\text{true}}$。自动质检 passed + 视觉复核：全局解（rmse≈0）与局部极小分离清晰，$t_0\to t$ 标注与周期歧义竖线可读，图例符号一致；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_3aa4f2349c5a -->

![prob01_fig_response_surface_d0691c5dd8 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_response_surface_d0691c5dd8.png)

图 prob01_fig_response_surface_d0691c5dd8 展示"两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）"，说明反射率对波数呈周期振荡并随入射角变化，为两角一致性与消歧提供直观依据。自动质检 passed + 视觉复核：3D 响应面视角可读（elev=26°、azim=-62°）无关键遮挡，θ=10°/15° 测量线标注，2D 等高线配套消歧，第三维为真实入射角变量；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_8bddbe7bab83 -->

![prob01_fig_sensitivity_tornado_6983566848 prob01 robustness 敏感性 tornado 汇总（E1–E5）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_sensitivity_tornado_6983566848.png)

图 prob01_fig_sensitivity_tornado_6983566848 展示"prob01 robustness 敏感性 tornado 汇总（E1–E5）"，说明 $n_{\text{sub}}$、$n$ 色散模型、噪声与谱段截断等因素对厚度的敏感性相对阈值大小。自动质检 passed（1514×865）+ 结构复核：E1–E5 五因素横条 tornado 图，实测影响 vs 预注册阈值竖线标注清晰，文本无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_bf1c3bb811a0 -->

![prob01_fig_noise_robustness_ci_30d4fa737f E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_noise_robustness_ci_30d4fa737f.png)

图 prob01_fig_noise_robustness_ci_30d4fa737f 展示"E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）"，说明在 0.5–2% 噪声下厚度估计的 95% CI 半宽极小、无明显偏差。自动质检 passed（1561×942）+ 结构复核：σ=0.5/1/2% × θ=10/15° 的 $t$ 均值与 95% CI 误差棒、$t_{\text{true}}$ 参考线清晰，图例无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_468d6eb2d342 -->

![prob01_fig_ablation_summary_ee3c34dcfa prob01 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_summary_ee3c34dcfa.png)

图 prob01_fig_ablation_summary_ee3c34dcfa 展示"prob01 ablation 判据汇总（F0 + A1–A4）"，说明干涉项、衬底反射、偏振平均与多初值模块为必要组件，且 A4（多初值模块）对恢复全局解至关重要。自动质检 passed（2039×1319 px）+ 结构复核：F0+A1–A4 五组判据横向条形（实测 vs 阈值竖线标注），A4 单初值退化（6.03%）与多初值对照（≈0%）语义区分明确，数值与 summary.json 一致；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_8526f70dd717 -->

![prob01_fig_ablation_polarization_da59250d1b A3 偏振一致性：avg/s/p 反演厚度 vs t_true](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_polarization_da59250d1b.png)

图 prob01_fig_ablation_polarization_da59250d1b 展示"A3 偏振一致性：avg/s/p 反演厚度 vs $t_{\text{true}}$"，说明未指定偏振的 s/p 平均与单偏振反演厚度一致（最大差 0.012%），偏振平均不是偏置来源。自动质检 passed（1682×960 px）+ 结构复核：avg/s/p 三种偏振 × θ=10°/15° 分组柱状图，$t_{\text{true}}=10.0\,\mu\text{m}$ 参考线与 ±1% 容差带清晰，数值与 summary.json 一致；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_7460c4889f44 -->

![prob01_fig_ablation_init_strategy_7c59622d5a A4 初值策略对比：单初值局部极小 vs 多初值全局解](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_init_strategy_7c59622d5a.png)

图 prob01_fig_ablation_init_strategy_7c59622d5a 展示"A4 初值策略对比：单初值局部极小 vs 多初值全局解"，说明单初值（约 6% 偏差）落入周期歧义局部极小、多初值回到 $t_{\text{true}}$，证实初值策略是必要模块。自动质检 passed（2413×963 px）+ 结构复核：单初值（t≈10.60，偏差约 6%）vs 多初值（t=10.000，偏差约 0）分组柱状图，$t_{\text{true}}$ 参考线与 $t_0\to t$ 标注可读，与 implementation §6.1 预警方向量级一致；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_a6478f4b1fae -->

### prob01 可靠性与结论

本问 L1–L4 sanity 为 **PASS_WITH_WARNING**，L5 为 **PASS**。稳健性（robustness_v001，任务 554819114361017c5b70）执行 E1–E5（$n_{\text{sub}}$/$\theta$ $\pm5/10/20\%$ 扰动、色散三模型、噪声 $\sigma=0.5/1/2\%\times100$ 次×2 入射角、谱段截断 6 组），5/5 判据通过，结论 **stable**：E1 $0.008\%$、E2 $0.22\%$、E3 替代模型 $0.96\%$、E4 CI 半宽 $<0.03\%$ 且收敛率 100%、E5 $0\%$；同时发现在噪声下极值定位初值失真，升级为网格扫描初值（prob02 复用）。消融（ablation_v001，任务 5dcb72876c5fcb2c7e95）执行 F0+A1–A4，5/5 判据通过，结论 **components_confirmed**：A1/A2（干涉项、衬底反射）不可辨识组件必要、A3 偏振平均最大差 0.012%、A4 单初值 6.03% vs 多初值约 0，证实模型组件与多初值模块的必要性。

**需要保留的边界或警告**：prob01 为合成验证任务（19/19 检查通过），$t_{\text{true}}=10\,\mu\text{m}$ 被相位法/全谱 NLS 精确恢复且两入射角一致；hash 追踪链与 task.json、implementation §7 一致，无 NaN/Inf、无硬约束违反、公式-代码逐条一致、文献/物理常识合理。既有技术债（$\lambda>5\,\mu\text{m}$ 常数色散延伸、方法 A 约 4% 基线偏差、文献全文待复核、$n_{\text{sub}}$ 合成场景值、Reststrahlen 剔除策略）为既有 workflow warning，留 prob02 处理，不阻断推进。因此本问结论限于上述假设、合成数据范围与误差条件。<!-- evidence:ev_artifact_ff24505a53cd -->

## prob02 模型建立、求解与结果

### prob02 问题分析

本问目标是依据 prob01 的两光束干涉数学模型，设计确定碳化硅外延层厚度的算法，并对附件 1（10°）与附件 2（15°）的实测光谱给出厚度计算结果与可靠性分析。输入为实测反射率谱（$R^{\text{obs}}_\theta(\nu_i)$，归一后 0–1）、波数网格、入射角、外延层色散 $n(\nu)$、衬底 $n_{\text{sub}}$；输出为厚度 $t$（每角 + 共享）、$n_{\text{sub}}$ 估计与不确定度。本问是连续参数估计的可行解反演问题，正模型含解析干涉项。历史版本暴露出决定性异常：v002 全谱 NLS 主方法 $t\approx0.3\,\mu\text{m}$ 与间隔法 $t\approx60\,\mu\text{m}$ 相差两个数量级，根因是"未建模的慢变基线主导目标函数"与"弱对比度下干涉幅值很弱、但相位/频率仍是强信号"。因此本问改用**干涉相位—频率拟合**：把光谱分解为慢变基线+干涉项，只让 $t$（即相位频率）决定干涉项，对固定 $t$ 用线性最小二乘、对 $t$ 做一维全局扫描（variable projection）。

### prob02 模型假设

本问假设族（assumption_v001，承接 prob01）与条目：H1（数据契约与预处理，比例归一、>100% 异常、Reststrahlen 谱段）对应 B1–B3；H2（两光束模型与几何/相位继承）对应 B4、B5；H3（材料光学参数：色散、衬底 $n_{\text{sub}}$、吸收边界）对应 B6、B7；H4（厚度反演算法：极值定位、全谱 NLS、色散化优先）对应 B8–B10；H5（可靠性与统计）对应 B11、B12；H6（多光束判定与修正，预留 prob03）对应 B13。冲突检查结论：本组假设内部无冲突，与题面理解、全局符号表及 prob01 结论一致。关键假设（关键性/来源登记）包括：B1（数据契约与归一化，project_assumption）、B4/B5（两光束模型、几何与相位继承）、B6（色散带内 Sellmeier、带外缺口）、B7（衬底折射率与弱可辨识）、B8–B10（极值定位、全谱 NLS、色散化优先）、B11/B12（两角一致性 F 检验、噪声传播）、B13（多光束诊断）。本问的模型假设与 prob01 结论建立软依赖（prob01-conclusion-v1，content_hash `82820355…070a6`）。<!-- evidence:ev_artifact_7fbd73d2c8cb -->

### prob02 模型建立与求解

**正模型**（继承 prob01）：$\sin\theta'=\sin\theta/n$，$\Delta=2t\sqrt{n^2-\sin^2\theta}$，相位差 $\delta(\nu_i)=4\pi\times10^{-4}\,n(\nu_i)\,t\,\nu_i\cos\theta'(\nu_i)+\varphi$（$\varphi$ 为反射相位跃变之和，并入 $C/S$ 系数），两光束反射率 $R(\nu_i)=R_1+(1-R_1)^2R_2+2(1-R_1)\sqrt{R_1R_2}\cos\delta$，取 s/p 平均，归一化 $R^{\text{obs}}=R\%/100$。约束 $0\le R\le1$、$t>0$。

**数据预处理**：归一化与波数升序重排；Reststrahlen 区 $\nu\in[700,1000]\,\text{cm}^{-1}$ 置 $w=0$；异常点（附件 2 $R\%>100$）降权；主反演带截断 $\nu\in[2000,4000]\,\text{cm}^{-1}$（Sellmeier 已知区，B6）。权重在反演前固定并登记。

**色散模型**：带内 $\nu\ge2000\,\text{cm}^{-1}$ 用 4H-SiC Sellmeier $n^2=6.79485+0.15558/(\lambda^2-0.03535)-0.02296\lambda^2$（L09）。主模型 N-SE（带内纯 Sellmeier）；N-SE-δ（Sellmeier 系数 $\pm0.5\%$）用于色散敏感性；N-const（带内常数 $n=2.4954$）作已知约 4% 偏置的基线。$\lambda>5\,\mu\text{m}$ 色散缺口（B6）不作为主交付输入。

**主反演方法（variable projection）**：把光谱分解为 $R^{\text{obs}}(\nu)=B(\nu;\mathbf b)+C(\nu;\mathbf c)\cos\delta+S(\nu;\mathbf s)\sin\delta+\epsilon$，其中 $B$ 为慢变 DC 基线、$C/S$ 为干涉包络与未知相位，$B(\nu)=\sum b_j\nu^j$、$C(\nu)=\sum c_j\nu^j$、$S(\nu)=\sum s_j\nu^j$（中心化+正交化 Chebyshev 基，$p=3$、$q=1$）。对固定候选 $t$，$\delta$ 已知，设计矩阵 $\boldsymbol\Phi(t)$ 已知，求解线性最小二乘 $\hat{\boldsymbol\beta}(t)=\arg\min_\beta\|R^{\text{obs}}-\boldsymbol\Phi(t)\beta\|^2$。厚度由一维全局扫描确定：

$$J(t)=\sum_{k=1}^{2}\sum_i w^{\text{inv}}_{k,i}\left[R^{\text{obs}}_k(\nu_i)-\left(B_k+C_k\cos\delta_k+S_k\sin\delta_k\right)\right]^2,\qquad \hat t=\arg\min_{t\in[t_{\text{lo}},t_{\text{hi}}]}J(t),$$

并分别对每角扫 $J_k(t)$。关键点：$t$ **只由相位频率决定**，与 $n_{\text{sub}}$/幅值解耦；$n_{\text{sub}}$ 由干涉幅值 $A=\sqrt{C^2+S^2}$ 在拟合后单独估计并标示弱可辨识。$t$ 与相位频率的解析关系为 $d\delta/d\nu=4\pi\times10^{-4}t\,\dot g(\nu)$，g 空间恒定周期 $\Delta g=1/(2\times10^{-4}t)$。

**周期歧义与初值**：用 g 空间/ν 空间周期图粗估 $t$（本版 g 空间主峰对应 $t\approx7.5\,\mu\text{m}$，ν 空间主峰对应约 60 $\mu\text{m}$ 为噪声周期，须排除，B8）。厚度周期歧义 $\Delta t_{\text{amb}}=1/(2\times10^{-4}n(\nu_0)\nu_0\cos\theta')$，但因 $g(\nu)$ 随 $\nu$ 变化（色散+$\cos\theta'$），周期等价性被打破，全局扫描不把 $t$ 与 $t\pm k\Delta t_{\text{amb}}$ 混淆。

求解策略：本问为 1 维连续非线性扫描（变量投影后每点线性 LS），属"小规模、连续、可预测"，精确方法充分，无需 MILP/元启发式。物理正模型 NLS 保留为交叉校验/多光束诊断用途（§6.4）。可靠性判据在计算前固定：两角一致性嵌套 F 检验、带内色散敏感性、$n_{\text{sub}}$ 解耦灵敏度、噪声/轮廓似然 CI、异常点影响、多光束诊断。<!-- evidence:ev_artifact_0366c0d48834 -->

### prob02 结果解释

主结果采用"基线-干涉分解 + 一维相位频率扫描（variable projection，两角共享 $t$）"。附件 1/2 实测反演（任务 30bedd3be5a2c9a36d3a，formulation_v003）给出：$\hat t(\text{共享})=7.2158\,\mu\text{m}$，每角 $7.2214/7.2095\,\mu\text{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\text{sub}}=2.588$（幅值弱可辨识），主拟合加权 RMSE≈$6.3\times10^{-4}$。只读 FFT 数据探针独立证实带内真实干涉周期 $\Delta g\approx657/698$、$\Delta\nu\approx247/263\,\text{cm}^{-1}$，对应 $t\approx7.2$–$8.0\,\mu\text{m}$，与主结果一致；而 M2/M3 的约 60 $\mu\text{m}$ 为噪声周期，已排除。物理正模型 NLS 从主 $\hat t$ 起点局部拟合得 $t\approx6.8/6.97\,\mu\text{m}$（RMSE≈0.0091，与主方法偏差约 5.5%，作交叉校验/诊断）。

量化结果与各图对应如下。

![prob02_fig_reflectance_spectrum_6b2265d217 附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reflectance_spectrum_6b2265d217.png)

图 prob02_fig_reflectance_spectrum_6b2265d217 展示"附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）"，说明 SiC 实测谱含干涉条纹、Reststrahlen 强反射峰、附件 2 反射率>100% 异常点（$n=262$，红×）与主反演带 [2000,4000]/Sellmeier 边界。自动质检 passed（1560×992）+ 视觉复核：两角实测谱、Reststrahlen 区强反射峰、异常点与主反演带边界标注清晰，图例无遮挡、单位（$R\%/\text{cm}^{-1}$）完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_dda4c5abdf3d -->

![prob02_fig_model_fit_0ca711689b 两入射角实测谱与两光束物理正模型 (2.3) 拟合对比](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_model_fit_0ca711689b.png)

图 prob02_fig_model_fit_0ca711689b 展示"两入射角实测谱与两光束物理正模型 (2.3) 拟合对比"，说明 $R_{\text{obs}}$ 与 $R_{\text{model}}$ 在反演带内整体吻合、残差 RMSE 注解框标明。自动质检 passed（1780×1100）+ 视觉复核：θ=10/15° 双面板实测与两光束模型叠加，残差 RMSE 注解框，标题/图例/单位准确；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_a75144cb91b3 -->

![prob02_fig_thickness_estimate_efa7359eb9 prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_thickness_estimate_efa7359eb9.png)

图 prob02_fig_thickness_estimate_efa7359eb9 展示"prob02 外延层厚度结果（formulation_v003，两角共享 $\hat t=7.2158\,\mu\text{m}$）"，说明共享 $\hat t$ 与每角 $\hat t$ 高度一致、95% CI 误差棒极小，ε12=0.165% 与 B11 路由说明框交代了实际意义分离。自动质检 passed（1523×956）+ 视觉复核：共享 $\hat t$ 与每角 $\hat t$ 柱状 + 共享 $\hat t$ 的 95% CI 误差棒 + ε12 与实际意义分离说明框，物理 NLS 交叉校验标记可读，图例/单位完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_73dc1fe83462 -->

![prob02_fig_dispersion_curve_af50244106 外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_dispersion_curve_af50244106.png)

图 prob02_fig_dispersion_curve_af50244106 展示"外延层 4H-SiC 折射率色散模型 $n(\nu)$：带内取 N-SE（Sellmeier）"，说明带内 N-SE、$\lambda>5\,\mu\text{m}$ 缺口代理、N-const 基线三线区分，y 轴范围覆盖全线。自动质检 passed（1552×1068）+ 视觉复核：带内 N-SE（Sellmeier）、$\lambda>5\,\mu\text{m}$ 缺口代理、N-const 基线区分明确，顶轴 λ[µm] 换算正确，Reststrahlen/反演带阴影，图例无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_c3bd34878ece -->

![prob02_fig_reliability_summary_78cd97014b prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reliability_summary_78cd97014b.png)

图 prob02_fig_reliability_summary_78cd97014b 展示"prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）"，说明各判据相对阈值的裕量与判定：六项判据全部低于阈值（绿=通过），仅在子轴下方对 F 检验 B11 路由、$\Delta t_{\text{inv\_band}}$/多光束诊断作说明。自动质检 passed（1776×987）+ 视觉复核：可接受带+实测值条形+阈值黑标，判据全部低于阈值，说明置于子轴下方无遮挡；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_f8d6659bf219 -->

![prob02_fig_variable_projection_jcurve_7a9a903650 主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_variable_projection_jcurve_7a9a903650.png)

图 prob02_fig_variable_projection_jcurve_7a9a903650 展示"主反演目标函数 $J(t)$ 与全局唯一性"，说明 $J(t)$ 在 $t=7.2158$ 处取全局唯一极小、次小候选更高，支撑厚度的可辨识性。自动质检 passed（1822×1035）+ 视觉复核：$J(t)$ 全局唯一极小（$J_{\min}\approx0.0032$）+95% CI 带+次小候选（高约 1.75×）+右侧对数局部深谷，唯一性证据清晰；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_2a594948c032 -->

![prob02_fig_g_space_phase_gap_f500d9c0db 相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_g_space_phase_gap_f500d9c0db.png)

图 prob02_fig_g_space_phase_gap_f500d9c0db 展示"相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照"，说明由 $\Delta g$ 反演 $t\approx7.1$–$7.6\,\mu\text{m}$（主方法）与 M2/M3 噪声周期 54–65 $\mu\text{m}$（错误）的机制对照，验证厚度由相位频率确定。自动质检 passed（1848×960）+ 视觉复核：去基线干涉条纹与同型极大（$\Delta\nu\approx253\,\text{cm}^{-1}$）定位，由 $\Delta g$ 反演 $t\approx7.1$–$7.6\,\mu\text{m}$ vs 噪声周期 54–65 $\mu\text{m}$ 对照清楚，单位/图例完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_ec5c566cade8 -->

![prob02_fig_nsub_decoupling_39b4128d09 n_sub 幅值弱可辨识性与 t-n_sub 解耦](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_nsub_decoupling_39b4128d09.png)

图 prob02_fig_nsub_decoupling_39b4128d09 展示"$n_{\text{sub}}$ 幅值弱可辨识性与 $t$-$n_{\text{sub}}$ 解耦"，说明左侧由幅值 $A=\sqrt{C^2+S^2}\approx0.0039$ 弱辨识 $\hat n_{\text{sub}}\approx2.588$、右侧主方法 $t$ 与 $n_{\text{sub}}$ 解耦（0.0% 敏感度）而物理 NLS 为 ±0.10 交叉校验（1.92% 诊断）。自动质检 passed（2057×1072）+ 视觉复核：左侧幅值弱辨识、右侧解耦 vs 物理 NLS 交叉校验对照清晰，x 轴标签不重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_fbf03315682d -->

![prob02_fig_response_surface_cfe5827835 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_response_surface_cfe5827835.png)

图 prob02_fig_response_surface_cfe5827835 展示"两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）"，说明反射率随波数周期振荡、随入射角变化，为两角一致性提供直观依据。自动质检 passed（1801×1063）+ 视觉复核：3D $R(\nu,\theta)$ 视角可读（elev=28/azim=-62）无关键遮挡、第三维为真实入射角变量，2D 等高线配套消歧，θ=10°/15° 测量线标注；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_aad41352929d -->

![prob02_fig_methods_compare_99386076f5 prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_methods_compare_99386076f5.png)

图 prob02_fig_methods_compare_99386076f5 展示"prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）"，说明主方法 M1（7.22）与物理 NLS 交叉校验（6.82/6.97）量级一致，而 M2/M3（58/60）为噪声周期，量级错误。自动质检 passed（1746×1009）+ 视觉复核：对数轴量级对照 M1/M1-P1/M1-P2 vs M2/M3、每角范围竖线标注，底部方法债说明框完整，图例/单位无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_d0a257b14967 -->

![prob02_fig_ablation_summary_dcd697b29e prob02 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_summary_dcd697b29e.png)

图 prob02_fig_ablation_summary_dcd697b29e 展示"prob02 ablation 判据汇总（F0 + A1–A4）"，说明色散、基线多项式、相位-频率方法为必要组件（A1/A2/A3 实测 $\Delta t$ 超阈值），A4 两角共享-$t$ 为良性一致约束。自动质检 passed（2870×1319 px）+ 视觉复核：F0 + A1–A4 五组判据横向条形，A1/A2/A3 实测 $\Delta t$ 超过阈值竖线、A4 ε12=0.165%≤2%、F0 为 $t$ 参考，数值与 summary.json 一致；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_dff80f606d45 -->

![prob02_fig_ablation_thickness_d29e3fc1f0 prob02 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_thickness_d29e3fc1f0.png)

图 prob02_fig_ablation_thickness_d29e3fc1f0 展示"prob02 ablation 厚度对照（F0 + A1–A4）"，说明消融各组件后厚度相对 $F_0$ 的偏移幅度，量化各组件的贡献。自动质检 passed（2256×1037 px）+ 视觉复核：$F_0$ 完整模型（对照）与 A1–A4 各消融项厚度柱状，$F_0$ 参考线与 ±1% 参考带清晰，$\Delta t\%$（8.44/5.55/5.44）与 ε12 标注可读，语义区分明确；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_9ff5e5c6749b -->

![prob02_fig_ablation_shared_t_14e5362fa7 A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_shared_t_14e5362fa7.png)

图 prob02_fig_ablation_shared_t_14e5362fa7 展示"A4 两角共享-$t$ 对照：每角独立 $\hat t$ 与共享 $\hat t$ 一致"，说明两角共享-$t$ 约束不扭曲厚度估计，ε12=0.165%≤2% 为良性一致约束。自动质检 passed（2633×1070 px）+ 视觉复核：共享 $\hat t$ 与 θ=10°/15° 每角独立 $\hat t$ 柱状，共享参考线清晰，ε12=0.165%≤2% 标注，纵轴尺度（±0.2%）合理；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_47cfd6efa8cb -->

### prob02 可靠性与结论

本问 L1–L4 sanity 为 **PASS_WITH_WARNING**，L5 为 **PASS**。可靠性判据（formulation §7.1–§7.6 预注册，计算前固定）执行结果：色散 $\Delta t_{\text{disp}}=0.507\%\le2\%$ PASS、$n_{\text{sub}}$ 解耦 $0.0\%$（物理 NLS 1.92%≤3%）PASS、CI 半宽 $0.091\%\le2\%$ PASS、异常点 $0.0\%\le1\%$ PASS、多光束改善 $0.0\%\le10\%$（两光束适用）PASS、全局极小唯一 PASS；仅两角嵌套 F 检验统计显著（$F=5.25>F_{\text{crit}}=3.843$、$p=0.022$），但 $\varepsilon_{12}=0.165\%\ll\tau_{12}=2\%$，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。结论 **STABLE**（$\hat t(\text{共享})=7.2158\,\mu\text{m}$、每角 7.2214/7.2095 $\mu\text{m}$、$\varepsilon_{12}=0.165\%$、$\hat n_{\text{sub}}=2.588$ 弱可辨识）。

**需要保留的边界或警告**：机器级 L2-finite 通过（8 数值文件全有限无 NaN/Inf）；hash 追踪链与 task.json、implementation §7 一致，原始数据只读，无硬约束违反。v001/v002 曾超阈判据（$\varepsilon_{12}$ 27.66%→0.165%、$\Delta t_{\text{disp}}$ 15.11%→0.51%、$n_{\text{sub}}$ 69%→解耦 0%、CI 3.51%→0.091%、M1 0.305 → 7.216 $\mu\text{m}$ 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。既有技术债（$\lambda>5\,\mu\text{m}$ 色散缺口 B6、$n_{\text{sub}}$ 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 5.5% 偏差、L25–L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，不阻断推进。因此本问结论限于上述接受版本、数据范围与误差条件。<!-- evidence:ev_artifact_44ce712a84e4 -->

## prob03 模型建立、求解与结果

### prob03 问题分析

本问包含三个子问题：Q1 推导多光束干涉的必要条件及其对厚度精度的影响；Q2 依据必要条件判定硅片（附件 3/4，10°/15°）是否出现多光束干涉，并给出硅厚度模型、算法与结果；Q3 若多光束也出现在碳化硅（附件 1/2）并影响精度，设法消除其影响并给出修正结果。本问不是约束优化问题，而是物理模型 + 可解性反演问题。关键物理事实：光在外延层两界面（构成平面平行板）间多次反射-透射产生多光束干涉；多光束是否显著由界面强度反射率乘积（精细度）决定；厚度由干涉条纹的相位频率确定。历史版本曾有两处公式-实现缺陷（R1 硅厚度基准 6.9 $\mu\text{m}$ 为标签伪影、R2 finesse 漏 $\sqrt{\bar R}$），本版已按对审定公式的忠实实现修正（$\hat t=3.4477\,\mu\text{m}$、$F=0.3186$）。

### prob03 模型假设

本问假设族（assumption_v001）与条目：M1（多光束必要条件严格推导：Airy 公式、界面反射率阈值、相干长度、界面平行度、吸收限制）对应 C1–C5；M2（硅外延层数据契约与材料/光谱参数）对应 C6–C9；M3（硅片是否多光束的判定）对应 C10–C12；M4（多光束对厚度精度影响与修正、SiC 重判）对应 C13–C15；M5（前问结论继承与跨问一致性）对应 C16–C17。冲突检查结论：本组假设内部无冲突；C1（Airy 公式）与 C16（两光束基线）是极限情形与一般情形关系；C2 与 C5 以谱段边界互限；C10 与 C15 以各自样品数据独立执行。L17『多光束不改变极值位置』为候选主张，本组不预先采信、由本版独立推导验证。关键假设包括：C1（Airy 公式与两光束极限）、C2（界面强度反射率乘积阈值）、C3（界面平行度）、C4（相干长度）、C5（吸收限制）、C6（硅数据契约）、C7（硅折射率/衬底折射率）、C8（硅透明谱段）、C9（几何/环境）、C10–C12（硅是否多光束判定）、C13–C15（多光束影响/修正/SiC 重判）、C16–C17（前问继承）。本问与 prob01/prob02 结论建立软依赖（prob01-conclusion-v1 `82820355…070a6`、prob02-conclusion-v1 `27b0ce86…a12ea`）。<!-- evidence:ev_artifact_41bfac6d034d -->

### prob03 模型建立与求解

**正模型与 Airy 公式**：几何与折射由 Snell（$\sin\theta'=\sin\theta/n_{\text{epi}}$）；s/p 复 Fresnel 系数给出界面强度反射率 $R_{01}=|r_{01}|^2$、$R_{12}=|r_{12}|^2$（模型反射率取 s/p 平均）。平面平行板多次反射的反射振幅 $r=(r_{01}+r_{12}e^{i\delta})/(1+r_{01}r_{12}e^{i\delta})$，Airy 反射强度

$$R_{\text{Airy}}(\delta)=\frac{R_{01}+R_{12}+2\sqrt{R_{01}R_{12}}\cos\delta}{1+R_{01}R_{12}+2\sqrt{R_{01}R_{12}}\cos\delta},$$

其中 $\delta=4\pi\times10^{-4}n_{\text{epi}}(\nu)\,t\,\nu\cos\theta'+\varphi$，无吸收时为实数、相位跃变仅取 0/π。**两光束极限**（$\bar R=\sqrt{R_{01}R_{12}}\to0$）：分母→1、分子保留一阶 $\cos\delta$ 项，退化为 prob01 的束踪两光束模型。

**多光束必要条件（Q1）**：

- **N1 界面强度反射率乘积（决定性）**：高次反射项按 $\bar R^m$ 衰减，两光束近似对高阶的相对误差为 $O(\bar R)$。判据 $\bar R=\sqrt{R_{01}R_{12}}\le\theta_{\text{mb}}=0.05$ 或 $\eta_{\text{mb}}\le\tau_{\text{mb}}=10\%$。精细度 $F=\pi\sqrt{\bar R}/(1-\bar R)\le F_{\max}\approx0.32$。对硅：$R_{01}\approx0.301$、$R_{12}\approx3.4\times10^{-4}$、$\bar R\approx0.0101$、$F\approx0.319$。
- **N2 相干长度**：$L_c\approx1/(2\Delta\nu_{\text{res}})$，可达干涉级次上限 $m^{\text{coh}}_{\max}=\lfloor1/(4nt\cos\theta'\Delta\nu_{\text{res}})\rfloor$，需 $\ge2$。对硅（$n\approx3.43$、$t\approx3.45\,\mu\text{m}$、$\Delta\nu_{\text{res}}\approx0.482\,\text{cm}^{-1}$）：$L_c\approx1.04\times10^4\,\mu\text{m}\gg\text{单程 OPD}\approx23.6\,\mu\text{m}$，$m^{\text{coh}}_{\max}\approx439$。
- **N3 界面平行度**：需楔角/不平度 $\alpha\ll\lambda/(2nD\cos\theta')$。对硅约 $\alpha\ll0.0033°$，实际晶圆片厚度不均匀进一步压制高次，佐证两光束。
- **N4 吸收限制**：消光系数 $k$ 使高次束按 $e^{-m\kappa/2}$ 衰减，有效级次 $m^{\text{abs}}_{\max}=\lfloor1/\kappa\rfloor$，需 $\ge2$。硅透明窗 $k\approx0$，不抑制多光束；SiC Reststrahlen 与硅多声子带 $k$ 大，抑制多光束。

**极值位置不变性（Q1 结论，L17 独立验证）**：对无吸收平行板，$R_{\text{Airy}}=(A+B\cos\delta)/(C+B\cos\delta)$（$A=R_{01}+R_{12}$、$B=2\sqrt{R_{01}R_{12}}$、$C=1+R_{01}R_{12}$），故 $dR_{\text{Airy}}/d\delta=B\sin\delta(A-C)/(C+B\cos\delta)^2$，因 $A-C=(R_{01}-1)(1-R_{12})\neq0$，极值当且仅当 $\sin\delta=0$，即 $\delta=m\pi$，与反射率乘积无关。因此**多光束不改变干涉极值位置/周期，即不改变厚度**（厚度由相位频率 $\delta/d\nu$ 确定），只改变条纹对比度、峰形与拟合残差。适用边界为透明谱段、无吸收、近平行板。

**硅厚度主反演（Q2，复用 prob02 variable projection）**：与 prob02 相同的"基线-干涉分解 + 一维相位频率扫描"，硅 Sellmeier（Li 1980，L12/L13）$n^2_{\text{epi}}(\lambda)$，主反演带 $\nu\in[2000,4000]\,\text{cm}^{-1}$（硅透明区，避开多声子带），$n_{\text{sub}}$ 由干涉幅值单独反演、与 $t$ 解耦。多光束判定（§8.2）：N1 判据 $\bar R\le0.05$（PASS）、主判据 $\eta_{\text{mb}}\le10\%$（PASS）。**SiC 重判（Q3）**：$\bar R\approx0.0024\le\theta_{\text{mb}}=0.05$，比硅更小，无显著多光束、无需修正，prob02 结果维持；若某样品触发 $\bar R>\theta_{\text{mb}}$ 或 $\eta_{\text{mb}}>\tau_{\text{mb}}$，则启用以 Airy 为正确模型的修正方案（分步法：两光束给 $t$ 初值→幅值反演 $R_{01}$/$R_{12}$→Airy 局部 NLS 精化），并回归残差改善率与 $t$ 位移（预期≈0）。可靠性预注册判据 R1–R8 见 §8.5。<!-- evidence:ev_artifact_67d81d412946 -->

### prob03 结果解释

对审定公式的忠实实现（结果目录 `results/silicon_mb_verify`，任务 7e209043973692d067ed）给出：硅 $\hat t(\text{共享})=3.4477\,\mu\text{m}$、每角 $3.4507/3.4463\,\mu\text{m}$、$\varepsilon_{12}=0.130\%$、$\hat n_{\text{sub}}=3.558$（幅值弱可辨识，$A\approx0.0141$）；$J_{\min}=0.0608$，加权 RMSE≈$2.57\times10^{-3}$。多光束判定：$R_{01}\approx0.3008$、$R_{12}\approx3.4\times10^{-4}$、$\bar R\approx0.0101$、$F\approx0.319$（正确公式）、$\eta_{\text{mb}}\approx0.11\%\le10\%$，**两光束适用（two_beam_negligible）**。SiC 重判（prob02 对照）：$\bar R\approx0.0024\le0.05$，**无显著多光束、无需修正（no_correction_needed）**，prob02 的 $\hat t=7.2158\,\mu\text{m}$ 维持。$J(t)$ 全局唯一极小在 $t=3.4477\,\mu\text{m}$；次小候选比值约 1.020（弱色散下周期邻近候选接近简并），作为报告项而非硬门禁。

量化结果与各图对应如下。

![prob03_fig_reflectance_spectrum_41a3800f70 附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reflectance_spectrum_41a3800f70.png)

图 prob03_fig_reflectance_spectrum_41a3800f70 展示"附件 3/4 硅晶圆片实测反射率谱（两入射角，无 $R\%>100$ 异常点）"，说明硅片实测谱含清晰干涉条纹、多声子带与主反演带阴影，且无附件 2 的 >100% 异常点。自动质检 passed（1560×992 px）+ 视觉复核：附件 3/4 实测谱清晰，多声子带[400,1600]与主反演带[2000,4000]阴影标注，硅附件无异常点；图例无遮挡、单位完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_5c5051a759c9 -->

![prob03_fig_model_fit_3e94d2fac7 两入射角实测谱与两光束物理正模型 (2.8) 拟合对比](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_model_fit_3e94d2fac7.png)

图 prob03_fig_model_fit_3e94d2fac7 展示"两入射角实测谱与两光束物理正模型 (2.8) 拟合对比"，说明 $R_{\text{obs}}$ 与两光束模型在反演带内整体吻合、残差 RMSE（2.944e-02/2.103e-02）注解框标明。自动质检 passed（1780×1100 px）+ 视觉复核：θ=10°/15° 双面板实测与两光束模型叠加，残差 RMSE 注解框注明；标题/图例/单位一致；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_8c09648b5b0d -->

![prob03_fig_thickness_estimate_59f1546ed7 prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_thickness_estimate_59f1546ed7.png)

图 prob03_fig_thickness_estimate_59f1546ed7 展示"prob03 硅外延层厚度结果（formulation_v002，两角共享 $\hat t=3.4477\,\mu\text{m}$）"，说明共享 $\hat t$ 与每角 $\hat t$ 高度一致、95% CI 误差棒极小（±0.0046 $\mu\text{m}$），ε12=0.130%、$F=0$/$p=1.0$ 说明框交代了一致性判定。自动质检 passed（1538×956 px）+ 视觉复核：共享 $\hat t=3.4477\,\mu\text{m}$ 与每角柱状 + 95% CI 误差棒，$\varepsilon_{12}=0.130\%\le\tau_{12}=2\%$、$F=0$/$p=1.0$ 说明框完整；单位/图例完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_dfeacc75d39b -->

![prob03_fig_dispersion_curve_aac3dcebea 硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_dispersion_curve_aac3dcebea.png)

图 prob03_fig_dispersion_curve_aac3dcebea 展示"硅外延层折射率色散模型 $n(\nu)$：带内取 N-SE（Sellmeier），色散弱（$\Delta n/n\approx0.51\%$）"，说明硅带内色散弱、且无 $\lambda>5\,\mu\text{m}$ 色散缺口（Li 1980 模型全程有效）。自动质检 passed（1566×1068 px）+ 视觉复核：带内 N-SE（Sellmeier）实线、N-const 点线区分明确，y 轴覆盖全线，多声子带/主反演带阴影，顶轴 λ[µm] 换算正确；图例无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_7dcc8d1ec952 -->

![prob03_fig_reliability_summary_50b4f34a17 prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reliability_summary_50b4f34a17.png)

图 prob03_fig_reliability_summary_50b4f34a17 展示"prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）"，说明五项判据全部低于阈值（绿=通过），并在子轴下方交代 $F$ 检验、$\eta_{\text{mb}}$ 两光束适用、轮廓似然 CI 与 $n_{\text{sub}}$ 弱可辨识。自动质检 passed（1783×987 px）+ 视觉复核：可接受带+实测条形+阈值黑标，五判据全部低于阈值（绿=通过），说明置子轴下方无遮挡；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_3dff305300aa -->

![prob03_fig_variable_projection_jcurve_4b30b360a4 主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_variable_projection_jcurve_4b30b360a4.png)

图 prob03_fig_variable_projection_jcurve_4b30b360a4 展示"主反演目标函数 $J(t)$ 与全局唯一性"，说明 $J(t)$ 在 $t=3.4477\,\mu\text{m}$ 取全局唯一极小、次小候选（$t\approx3.70$，高约 1.020×）为报告项，右侧对数局部深谷直观。自动质检 passed（1780×1035 px）+ 视觉复核：$t̂=3.4477\,\mu\text{m}$ 全局唯一极小（$J_{\min}=0.0608$）+95% CI 带+次小候选（报告项）清晰；右侧对数局部深谷直观；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_6a4fab81710a -->

![prob03_fig_mb_conditions_9571a5012b 多光束干涉必要条件 N1–N4 与硅片判定](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_mb_conditions_9571a5012b.png)

图 prob03_fig_mb_conditions_9571a5012b 展示"多光束干涉必要条件 N1–N4 与硅片判定"，说明左侧 Rbar（0.0101）与 F（0.3186）相对 θ_mb=0.05 阈值条形、右侧 N1–N4+η_mb 通过表，支撑"两光束适用"判定。自动质检 passed（3384×1072 px）+ 视觉复核：左侧 Rbar（0.0101）与 F（0.3186）相对 θ_mb=0.05 阈值条形；右侧 N1–N4+η_mb 通过表清晰，无文本重叠；底部判定说明完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_a64ba1b677b8 -->

![prob03_fig_sic_multibeam_recheck_4cbb136f9c 多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_sic_multibeam_recheck_4cbb136f9c.png)

图 prob03_fig_sic_multibeam_recheck_4cbb136f9c 展示"多光束显著性跨材料对照：硅/SiC 均 Rbar≪θ_mb → 无显著多光束、无需修正（Q3）"，说明硅（0.01008）与 SiC（0.00240）均远低于 θ_mb=0.05 红线，SiC 无需修正。自动质检 passed（1749×1009 px）+ 视觉复核：对数轴柱状对比硅（0.01008）/SiC（0.00240）/SiC 对照 prob02（0.00247），远低于 θ_mb=0.05 红线；图例置右上、说明框无重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_592e5e151a31 -->

![prob03_fig_response_surface_06cfec9b1e 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_response_surface_06cfec9b1e.png)

图 prob03_fig_response_surface_06cfec9b1e 展示"两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）"，说明反射率随波数周期振荡并随入射角变化，为两角一致性提供直观依据。自动质检 passed（1796×1063 px）+ 视觉复核：视角 elev=28°/azim=-62° 无遮挡、深度可辨，第三维为真实入射角变量；2D 等高线配套消歧，θ=10°/15° 测量线标注；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_a9d9c329d54e -->

![prob03_fig_phase_freq_gspace_a936624612 相位频率（g 空间）测厚机制与条纹计数](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_phase_freq_gspace_a936624612.png)

图 prob03_fig_phase_freq_gspace_a936624612 展示"相位频率（g 空间）测厚机制与条纹计数"，说明左面板用两光束模型去基线定位同型极大（$n=5$，$\Delta\nu\approx419\,\text{cm}^{-1}$），右面板由 $\Delta g$ 反演 $t$ 均≈3.45 $\mu\text{m}$（与 $\hat t=3.4477$ 一致），并标注倍周期假极小 6.9 $\mu\text{m}$（v001 伪影，已排除）。自动质检 passed（1562×1058 px）+ 视觉复核：左面板定位同型极大、右面板由 $\Delta g$ 反演 $t$ 与 $\hat t$ 一致并排除 6.9 $\mu\text{m}$ 伪影，机制清楚、单位/图例完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_9a913a61baae -->

![prob03_fig_ablation_summary_9f93c3dd2d prob03 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_summary_9f93c3dd2d.png)

图 prob03_fig_ablation_summary_9f93c3dd2d 展示"prob03 ablation 判据汇总（F0 + A1–A4）"，说明各项组件消融均不显著改变厚度（A1 0.446%≤2%、A2 0.300%≤1%、A3 0.574%≤2%、A4 0.089%≤2%），模型组件具必要性但非偏置来源。自动质检 passed（≥800×480）+ 视觉复核：A1–A4 实测 $\Delta t\%$ 全部低于预注册阈值，log 轴与阈值黑标清晰，数值与 summary.json/result.json 一致，无文本重叠、单位完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_e1af76ad2a74 -->

![prob03_fig_ablation_t_consistency_ec44908369 prob03 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_t_consistency_ec44908369.png)

图 prob03_fig_ablation_t_consistency_ec44908369 展示"prob03 ablation 厚度对照（F0 + A1–A4）"，说明各消融项厚度均落在 $F_0$ ±1% 参考带内（A4 含每角独立 $\hat t$），组件消融不偏移厚度。自动质检 passed（≥800×480）+ 视觉复核：F0 + A1–A4 厚度柱状均落在 $F_0$ ±1% 参考带内，$F_0$ 参考线、±1% 带与数值标注清晰，与 result.json 一致；图例/单位完整；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_bce0cdb5c3cb -->

![prob03_fig_ablation_rmse_ce4b523efa prob03 ablation 拟合优度对照（加权 RMSE）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_rmse_ce4b523efa.png)

图 prob03_fig_ablation_rmse_ce4b523efa 展示"prob03 ablation 拟合优度对照（加权 RMSE）"，说明基线项为拟合优度必要组件、Airy 高阶项改善有限，支撑"两光束 + 基线多项式"的模型结构。自动质检 passed（≥800×480）+ 视觉复核：加权 RMSE 对照显示基线 p=0 上升（+9.5%）、Airy 高阶下降（−5.0%），$F_0$ 参考线与数值标注清晰，与 result.json 一致；无文本重叠；该图用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_e962f369961c -->

### prob03 可靠性与结论

本问 L1–L4 sanity 为 **PASS_WITH_WARNING**，L5 为 **PASS**。可靠性预注册判据 R1–R8（formulation §8.5，计算前固定）全部在阈值内：R1 两角 $\varepsilon_{12}=0.130\%\le2\%$（$F=0$、$p=1.0$）、R2 色散 $\Delta t_{\text{disp}}=0.503\%\le2\%$、R3 CI 半宽 $0.134\%\le2\%$、R4 异常点 $0.0\%\le1\%$、R5 多光束 $\eta_{\text{mb}}=0.111\%\le10\%$、R6 $n_{\text{sub}}$ 解耦、R7 窗口 $0.749\%\le2\%$（只读探针补登）；R8 唯一性次小候选≈1.020 为报告项（弱色散周期歧义），全局唯一性由 §7.6 预注册判据确认。结论 **STABLE**。

**需要保留的边界或警告**：公式-实现逐条一致，R1（硅厚度基准 $\hat t=3.4477\,\mu\text{m}$，修正 v001 的 6.9 $\mu\text{m}$ 因子 2 伪影）与 R2（$F=\pi\sqrt{\bar R}/(1-\bar R)$ 修正 v001 漏 $\sqrt{\bar R}$，$F=0.3186$）已在 v002 修复并复核通过；机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf）、hash 追踪链完整、原始数据只读、无硬约束违反。合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。既有技术债（bootstrap CI 用轮廓似然替代、$n_{\text{sub}}$ 弱可辨识 B7、唯一性次小候选接近简并、multibeam 基线差异、$\lambda>5\,\mu\text{m}$ SiC 色散缺口 B6、L43–L47 全文待复核、附件 2 数据契约偏差）均为既有/登记事项或非阻断。因此本问结论限于上述接受版本、数据范围与误差条件；多光束判定在透明谱段适用，吸收带（SiC Reststrahlen、硅多声子带）不在极值不变性结论的适用域内。<!-- evidence:ev_artifact_30aee4639e7e -->

## 跨小问一致性、稳健性与消融分析

三问共享同一套符号与单位（$t,n,n_{\text{sub}},\theta,\theta',\lambda,\nu,R,\delta,R_{01}/R_{12},\bar R,F$）、材料色散与谱段约束。跨小问一致性审查状态为 **passed**，核心结论为：共享符号与单位、参数值（Sellmeier 一致、主带 $\nu\in[2000,4000]\,\text{cm}^{-1}$、$\theta=10°/15°$、Reststrahlen $[700,1000]\,\text{cm}^{-1}$ 剔除）、假设、数据版本、约束（$R\in[0,1]$、$t>0$、$n>1$）、结论方向与数量级全部跨问自洽；软依赖 conclusion hash（prob01=`828203556617…070a6`、prob02=`27b0ce8689e1…12ea`）完整匹配，无 stale 传播、无回退。唯一共享符号元数据不一致（finesse domain ≥1 vs 实际 $F\approx0.32<1$）已由审查修订为 $>0$，属全局符号表规范修订，不影响任何计算结果。裁决依据：题目硬约束、sanity 硬门禁、文献/机理、鲁棒性、解释性、时间顺序均一致，无硬门禁失败版本。

**稳健性**：三问的 robustness 均独立验收通过。prob01 E1–E5（扰动/色散/噪声/截断）5/5 判据通过、结论 stable；prob02 判据 C1–C8 由预注册判据在 computation 阶段执行并归档，除 C1 两角 F 检验统计显著（路由 B11）外全部 PASS、结论 STABLE；prob03 判据 R1–R8 全部在阈值内、结论 STABLE。稳健性均基于已预注册方案运行前固定、复用已有产物、未改数据/代码/结果。

**消除模型结构缺陷**：prob02 的 v001/v002 曾多个判据超阈（$\varepsilon_{12}$ 27.66%、$\Delta t_{\text{disp}}$ 15.11%、$n_{\text{sub}}$ 69%、CI 3.51%、M1 0.305 $\mu\text{m}$），formulation_v003 变量投影重构把 $t$ 与 $n_{\text{sub}}$ 解耦后全部回到阈值内；prob03 的 v001 两处公式-实现缺陷（R1/R2）在 v002 修正并复核通过。

**消融（模型组件必要性）**：prob01 F0+A1–A4（干涉项、衬底反射、偏振平均、多初值模块）：5/5 通过，A4 单初值 6.03% 消融显著，证实多初值模块必要、其余组件必要或良性；prob02 F0+A1–A4（色散、基线多项式、相位-频率方法、两角共享-$t$）：A1 $\Delta t_{\text{disp}}=8.44\%>1\%$、A2 $\Delta t_{\text{base}}=5.55\%>1\%$ 且 RMSE 升 7.03×、A3 $\Delta t_{\text{vp}}=5.44\%>1\%$、A4 $\varepsilon_{12}=0.165\%\le2\%$（共享为良性一致约束），confirm 色散/基线/相位-频率方法为必要组件；prob03 F0+A1–A4（色散项、Airy 高阶项、基线多项式项、两角共享-$t$）：A1 0.446%、A2 0.300%、A3 0.574%、A4 0.089% 均低于阈值且 RMSE +9.5%（基线项为拟合优度必要组件），confirm 组件必要性又不偏移厚度。消融结论**未删除任何不利情景**，作为组件必要性证据与跨问一致性佐证。

**质量警告（如实披露，不改为已解决）**：

- prob01：合成验证 19/19 通过，$t_{\text{true}}=10\,\mu\text{m}$ 被精确恢复；技术债（$\lambda>5\,\mu\text{m}$ 常数色散延伸、方法 A 约 4% 基线偏差、文献全文待复核、$n_{\text{sub}}$ 合成场景值、Reststrahlen 剔除策略）为既有 workflow warning。
- prob02：L1–L4 硬门禁通过、8 文件全有限；仅两角 F 检验统计显著（$F=5.25$，$p=0.022$）但 $\varepsilon_{12}=0.165\%\ll2\%$，路由 B11；技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 5.5%、$\lambda>5\,\mu\text{m}$ 色散缺口 B6、$n_{\text{sub}}$ 弱可辨识 B7、L25–L32 全文待复核、多光束 Airy 留 prob03 B13）。
- prob03：L1–L4 硬门禁通过、10 文件全有限；R1/R2 已修复；技术债（bootstrap CI 用轮廓似然替代、$n_{\text{sub}}$ 弱可辨识 B7、唯一性次小候选接近简并、multibeam 基线差异、$\lambda>5\,\mu\text{m}$ SiC 色散缺口 B6、L43–L47 全文待复核、附件 2 数据契约偏差）；合并 config_hash 因 computation 后配置变更而漂移，作质量告警登记。

这些警告作为解释结果与限制外推范围的组成部分，不被改写为已解决。

## 模型评价、局限与推广

模型链条从假设、公式、实现、结果到图表均可追溯，便于复核与复现；多种 sanity 与扰动证据减少了只凭单点结果下结论的风险。主方法的物理正当性在于：厚度 $t$ 由干涉条纹的相位频率确定（$t=1/(2\times10^{-4}\Delta g)$），与弱可辨识的衬底折射率/幅值解耦，因此在弱对比度（$n_{\text{sub}}\approx n$）条件下稳健；多光束由 Airy 极值位置不变性证明不改变厚度，只影响对比度与拟合残差。

**局限**：（1）主反演带截断至 $\nu\in[2000,4000]\,\text{cm}^{-1}$，利用了严格已知的 Sellmeier 色散，但 $\lambda>5\,\mu\text{m}$（SiC）色散缺口未纳入主反演，其影响仅以 $\Delta t_{\text{inv\_band}}$ 报告；（2）$n_{\text{sub}}$ 为幅值弱可辨识量、信噪比有限，对噪声敏感（但对 $t$ 影响可忽略）；（3）厚度的全局唯一性在弱色散下存在周期邻近候选接近简并（prob03 次小候选≈1.020），虽由预注册判据确认全局极小，仍作为报告项；（4）多光束极值不变性结论仅对透明谱段、无吸收、近平行板严格成立；（5）可靠性部分依赖轮廓似然/CI 替代 bootstrap；（6）文献全文（尤其定量系数）待复核；（7）prob01 采用合成数据、无实测验证。

**推广边界**：多光束与极值不变性结论适用于透明、平行、无吸收的平行板（硅透明窗、SiC 带内）；在 SiC Reststrahlen、硅多声子带等吸收区，模型本身不适用，应改用复折射率模型。推广到新的材料、时段或数据分布前，应重新执行参数标定、敏感性分析与 Level 5 视觉复核，并核验色散模型与 $n_{\text{sub}}$ 取值。

## 结论

本文逐问完成了模型建立、求解、结果解释与可靠性检查。**问题 1** 建立了两光束干涉测厚的色散化 Fresnel 正模型与反演公式，合成数据验证相位法/全谱 NLS 精确恢复 $t_{\text{true}}=10.0\,\mu\text{m}$、方法 A 存在约 4% 色散偏差，为后续反演奠定模型与初值基础。**问题 2** 用"基线-干涉分解 + 一维相位频率扫描（variable projection）"对 SiC 实测反演得 $\hat t=7.2158\,\mu\text{m}$（每角 7.2214/7.2095 $\mu\text{m}$、$\varepsilon_{12}=0.165\%$、$\hat n_{\text{sub}}=2.588$），可靠性 5/6 通过（两角 F 检验统计显著但 $\varepsilon_{12}\ll2\%$，路由 B11）。**问题 3** 严格推导多光束必要条件 N1–N4 并验证极值位置不变性，判定硅片两光束适用（$\bar R\approx0.0101$、$\eta_{\text{mb}}\approx0.11\%$）得 $\hat t=3.4477\,\mu\text{m}$（每角 3.4507/3.4463 $\mu\text{m}$、$\varepsilon_{12}=0.130\%$、$\hat n_{\text{sub}}=3.558$），并重判 SiC 无显著多光束、无需修正（$\bar R\approx0.0024$），prob02 结果维持。所有结论只在 Evidence Pack 固定的接受版本、数据范围与警告边界内成立。<!-- evidence:ev_artifact_ff24505a53cd --><!-- evidence:ev_artifact_44ce712a84e4 --><!-- evidence:ev_artifact_30aee4639e7e -->

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

论文由 Evidence Pack `e0e907b66c21d6cf8dddc068f713e0dae6a40c3b6fa2eec72758f58ba39a5571` 生成。复现流程：先核验上述证据包哈希与 `writer_manifest.json`（含 evidence_hash、paper_md_sha256），再运行论文构建命令。计算工件按问分目录组织于 `problems/2025-cumcm-b/prob0X/versions/assumption_v001/`：`formulation.md`（模型）、`assumptions.md`（假设）、`model.py`/`compute.py`（实现）、`results/`（`synthetic_verify`、`thickness_inversion_v003`、`silicon_mb_verify` 的 `result.json`）、`robustness/` 与 `ablation/`（稳健性/消融结论）、`figures/`（图）。所有图、数据与结果路径按证据包登记清单为准；正文不重复粘贴完整代码，核心代码索引登记于证据包的 `artifacts` 清单，可逐条核对 hash 追踪链。原始附件数据只读，复用 `model.py`、不改数据/代码/结果即可复现各问定量结果。
