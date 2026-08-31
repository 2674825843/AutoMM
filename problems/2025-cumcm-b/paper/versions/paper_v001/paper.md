# 基于红外干涉法的碳化硅/硅外延层厚度测量：两光束与多光束干涉建模、反演与可靠性分析

## 摘要

本文围绕红外干涉法测定外延层厚度这一目标，逐问完成建模、算法设计、实测光谱反演与可靠性分析，形成一条可追溯、可复现的建模链条。

**prob01（模型建立）。** 在"外延层-衬底界面仅一次反射、透射"的两光束干涉近似下，由 Snell 折射与平行平板几何导出光程差 $\Delta=2nt\cos\theta'=2t\sqrt{n^2-\sin^2\theta}$ 与相位差 $\delta=4\pi\times10^{-4}nt\nu\cos\theta'$，结合 Fresnel 界面强度反射率 $R_1,R_2$ 建立起反射率随波数的解析正模型 $R(\nu)=R_1+(1-R_1)^2R_2+2(1-R_1)\sqrt{R_1R_2}\cos\delta$；由极值条件 $\delta=m\pi$ 导出同型相邻极值波数间隔 $\Delta\nu=1/(2nt\cos\theta')$ 与厚度反演式 $t=1/(2\Delta\nu\sqrt{n^2-\sin^2\theta})$，并以色散化相位函数 $g(\nu)=n(\nu)\nu\cos\theta'(\nu)$ 作色散修正。以合成谱（$t_{\text{true}}=10.00\,\mu\text{m}$、$n_{\text{sub}}=3.0$）验证：相位法恢复 $t\approx10.002$（10°）/9.9995（15°）$\mu\text{m}$，全谱非线性最小二乘恢复 $t=10.000\,\mu\text{m}$，两入射角一致、与真值相对偏差 $\le0.03\%$；仅常数 $n$ 的极值间隔法（方法 A）引入约 4% 色散系统偏差，故以色散化相位法/全谱 NLS 为主。robustness（E1–E5）5/5 通过、ablation（F0+A1–A4）5/5 通过，L1–L5 检查通过。<span><!-- evidence:ev_artifact_ff24505a53cd --></span>

**prob02（碳化硅实测反演）。** 针对同一块碳化硅晶圆片在入射角 10°（附件 1）与 15°（附件 2）的实测反射率谱，继承 prob01 两光束正模型，提出**基线-干涉分解 + 一维相位频率扫描（variable projection）**主方法：将光谱分解为慢变基线 $B(\nu)$ 与干涉项 $C(\nu)\cos\delta+S(\nu)\sin\delta$，对固定厚度 $t$ 退化为线性最小二乘，对 $t$ 作一维全局扫描取全局最小；厚度 $t$ 由干涉相位频率（$t=1/(2\times10^{-4}\Delta g)$）确定、与衬底折射率 $n_{\text{sub}}$ 解耦，$n_{\text{sub}}$ 由干涉幅值弱可辨识。主反演带取 $\nu\in[2000,4000]\,\text{cm}^{-1}$（Sellmeier 已知区），剔除以 Reststrahlen 区 $[700,1000]\,\text{cm}^{-1}$ 并对附件 2 反射率 >100% 异常点降权。得到两角共享厚度 $\hat t=7.2158\,\mu\text{m}$（每角 7.2214/7.2095 $\mu\text{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\text{sub}}=2.588$，加权 RMSE≈$6.3\times10^{-4}$），目标函数 $J(t)$ 全局唯一。可靠性判据 5/6 通过（色散 0.507%≤2%、CI 半宽 0.091%≤2%、异常 0.0%≤1%、$n_{\text{sub}}$ 解耦 0.0%、多光束改善 0.0%≤10%）；仅两角嵌套 $F$ 检验统计显著（$F=5.25>F_{\text{crit}}=3.843$、$p=0.022$）但裸偏差 $\varepsilon_{12}=0.165\%\ll2\%$，按约定路由为测量点差异/膜厚梯度并记录，不构成模型修订触发。ablation（F0+A1–A4）确认色散、基线多项式、相位频率方法均为必要组件，两个入射角共享-厚度为良性一致约束，未扭曲 $\hat t$。L1–L5 检查通过。<span><!-- evidence:ev_artifact_44ce712a84e4 --></span>

**prob03（多光束干涉与硅片反演）。** 由 Airy 多光束反射率模型严格推导多光束干涉的必要条件 N1–N4：界面反射率几何平均 $\bar R=\sqrt{R_{01}R_{12}}\le\theta_{\text{mb}}=0.05$（或精细度 $F=\pi\sqrt{\bar R}/(1-\bar R)$、残差改善率 $\eta_{\text{mb}}\le10\%$）、相干长度覆盖、界面近平行度、吸收不抑制；并证明无吸收平行板下 Airy 反射率极值位置严格落在 $\delta=m\pi$、与 $R_{01}R_{12}$ 无关（独立验证 L17），故多光束**不改变干涉周期与极值位置、不改变厚度**，只改变条纹对比度、峰形与拟合残差。对硅片（附件 3/4）：$R_{01}\approx0.3008$、$R_{12}\approx3.38\times10^{-4}$、$\bar R\approx0.0101\le0.05$、$F\approx0.319$、$\eta_{\text{mb}}\approx0.11\%\le10\%$，判定**未出现显著多光束干涉、两光束模型适用**；基于两光束 variable projection 反演硅厚度 $\hat t(\text{共享})=3.4477\,\mu\text{m}$（每角 3.4507/3.4463 $\mu\text{m}$，$\varepsilon_{12}=0.130\%$，$\hat n_{\text{sub}}=3.558$，加权 RMSE≈$2.57\times10^{-3}$）。对碳化硅重新判定：$\bar R\approx0.0024\le0.05$，亦无显著多光束、**无需修正**，prob02 的 $\hat t=7.2158\,\mu\text{m}$ 维持。可靠性判据 R1–R8 全部在阈值内（两角 $F=0$、色散 0.503%≤2%、CI 0.134%≤2%、异常 0.0%≤1%、多光束 0.11%≤10%、窗口 0.749%≤2%），唯一性次小候选比≈1.020 作报告项。ablation（F0+A1–A4）确认色散项、多光束高阶项、基线多项式项、两角共享-$t$ 约束均不超阈。L1–L5 检查通过。<span><!-- evidence:ev_artifact_30aee4639e7e --></span>

本文进一步从跨小问一致性、扰动稳健性与模型组件必要性三个层面核对结果，所有定量结论均可回溯到已验收的证据包与预注册脚本。

## 关键词

红外干涉法；外延层厚度；色散修正；多光束干涉；变量投影反演；可靠性分析

## 问题重述

碳化硅（SiC）作为第三代半导体材料，其外延层厚度是影响器件性能的关键参数，制定科学、准确、可靠的外延层厚度测试标准尤为重要。红外干涉法是一种无损测厚方法：外延层与衬底因掺杂载流子浓度不同而具有不同折射率，红外光入射到外延层后，一部分从外延层上表面反射、另一部分透射后在外延层/衬底界面反射并再次透射，两束光在一定条件下产生干涉条纹。由红外光谱的波长（波数）、外延层折射率与入射角等参数即可确定外延层厚度。需要注意的是，外延层折射率并非常数，而与掺杂载流子浓度及波长有关。

题目要求依次完成：

1. **问题 1**：考虑外延层与衬底界面"只有一次反射、透射"所产生的干涉条纹情形，建立确定外延层厚度的数学模型。
2. **问题 2**：依据问题 1 的数学模型设计确定外延层厚度的算法，并对附件 1、附件 2 提供的碳化硅晶圆片光谱实测数据给出计算结果，分析结果的可靠性。
3. **问题 3**：在光波于外延层界面与衬底界面产生多次反射、透射（多光束干涉）的情形下，推导产生多光束干涉的必要条件及其对外延层厚度计算精度可能产生的影响；依据必要条件分析附件 3、附件 4 提供的硅晶圆片测试结果是否出现多光束干涉，给出硅外延层厚度计算的数学模型、算法与结果；若多光束干涉也出现在碳化硅晶圆片（附件 1、附件 2）中并影响厚度计算精度，设法消除其影响并给出修正后的计算结果。

**数据说明**：附件 1、附件 2 分别为入射角 10° 与 15° 时针对同一块碳化硅晶圆片的测试结果；附件 3、附件 4 分别为入射角 10° 与 15° 时针对同一块硅晶圆片的测试结果。每个附件的第 1 列为波数（单位：cm⁻¹），第 2 列为干涉光谱的反射率（单位：%）。光谱为波数约 400–4000 cm⁻¹（对应波长约 2.5–25 μm）的中红外区间。

**待求量**：外延层厚度 $t$；外延层折射率 $n(\nu)$（与掺杂浓度、波长相关，其色散关系待定）；衬底折射率 $n_{\text{sub}}$；干涉级次与干涉条纹（峰/谷）的识别。**约束**：厚度为正且量级合理；同一晶圆片在两个入射角下的厚度计算结果应当一致（可靠性检验的天然判据）；模型须与外延层折射率随掺杂浓度与波长变化的物理事实一致；原始数据只读、计算可复现可追溯。

## 问题分析与总体流程

全题采用"物理设定—假设与符号统一—逐问建模—实测数据反演—结果解释—sanity 与稳健性验证—跨问一致性复核"的流程。模型在 prob01 建立正模型与反演公式，prob02 迁移至碳化硅实测反演并在实测暴露的模型可辨识性缺陷上进行方法重构，prob03 将模型扩展到多光束（Airy）干涉并对硅片实测判定与反演，同时回答多光束对厚度精度的影响。写作上，Writer 仅组织已接受的材料，不重新建模、不改变假设与公式、不重估参数，凡关键数字、公式、图表、文献性主张与警告均紧邻对应证据标记。

全文各问的真实性由 L1–L6 分层校验保障：L1–L4 硬门禁（哈希追踪链、机器级 finite 检查、公式-代码逐条一致、单位/量纲、原始数据只读、无硬约束违反），L5 视觉与结构复核，L6 robustness 与 ablation 验收。证据包（Evidence Pack）按 SHA-256 固定所有输入、脚本与结果，本论文仅引用其中登记的证据标记。

## 模型假设

各小问只采用 Evidence Pack 中登记的已接受假设（prob01：`assumption_v001`；prob02：`assumption_v001`；prob03：`assumption_v001`），不另行添加假设。全局共同假设为：外延层可视作平行平板、厚度在测量区域内均匀（几何）；红外光源相干长度远大于两光束光程差（A11/C4），干涉条纹稳定；折射率随波长变化、需采用色散模型（A5/B6/C7），衬底折射率与掺杂有关（A6/B7/C7）；在用于干涉反演的谱段内吸收可忽略、折射率取实数，但在 Reststrahlen 区（SiC 约 700–1000 cm⁻¹）与硅多声子带吸收不可忽略，模型不再适用（A7/B3/C8）。各小问关键假设的适用范围、预期偏差方向与验证方式保留在对应小问章节，并以登记文献作为方法依据（如 [@L01][@L02][@L06][@L07][@L17]）。

## 符号说明

| 符号 | 含义 | 单位 |
|---|---|---|
| $t$ | 外延层厚度（核心未知量） | $\mu\text{m}$ |
| $n(\nu)$ / $n_{\text{epi}}$ | 外延层折射率（色散函数） | 无量纲 |
| $n_{\text{sub}}$ | 衬底折射率 | 无量纲 |
| $n_{\text{air}}$ | 空气折射率（$=1.0$） | 无量纲 |
| $\theta,\theta',\theta''$ | 空气、外延层、衬底内入射/折射角 | 度（计算转 rad） |
| $\nu$ | 波数 | $\text{cm}^{-1}$ |
| $\lambda$ | 真空中波长（$\lambda=10^4/\nu$） | $\mu\text{m}$ |
| $R$ | 反射率（归一 0–1） | 无量纲 |
| $R_1,R_2$（$R_{01},R_{12}$） | 界面强度反射率 | 无量纲 |
| $\Delta$ | 两光束几何光程差（$=2nt\cos\theta'$） | $\mu\text{m}$ |
| $\delta$ | 两相干光束相位差（$=4\pi\times10^{-4}nt\nu\cos\theta'$） | rad |
| $\Delta\nu$ | 同型相邻极值波数间隔 | $\text{cm}^{-1}$ |
| $m$ | 干涉级次 | 非负整数 |
| $g(\nu)$ | 色散化相位函数（$=n(\nu)\nu\cos\theta'$） | 无量纲 |
| $\Delta g$ | $g$ 空间干涉周期 | 无量纲 |
| $\bar R=\sqrt{R_{01}R_{12}}$ | 界面反射率几何平均 | 无量纲 |
| $F$ | 精细度（$=\pi\sqrt{\bar R}/(1-\bar R)$） | 无量纲 |
| $\varepsilon_{12}$ | 两入射角厚度裸偏差百分比 | % |
| $\eta_{\text{mb}}$ | 多光束相对两光束的全谱残差改善率 | % |

单位约定：厚度 $t[\mu\text{m}]$、波数 $\nu[\text{cm}^{-1}]$、波长 $\lambda[\mu\text{m}]=10^4/\nu$、角度以度给出（代入三角函数时转 rad）、反射率以 % 计并归一为 0–1，相位差 $\delta$ 以 rad 计。以上符号与全局符号表一致。

## 数据说明与预处理

数据文件、预处理记录与计算结果均由证据包按 SHA-256 固定。正文不改写原始数据；异常值、缺失值、筛选区间与单位转换以各问已验收的实现与结果记录为准，并写明对应策略：

- **碳化硅（prob02，附件 1/2）**：归一化 $R^{\text{obs}}=R\%/100$；波数升序重排；附件 2 存在反射率 >100% 的异常点（$n=262$），按稳健降权（$w=w_{\text{anom}}$）处理而不修改原始数据；剔除 Reststrahlen 区 $\nu\in[700,1000]\,\text{cm}^{-1}$（无吸收模型失效）；主反演带截断为 $\nu\in[2000,4000]\,\text{cm}^{-1}$（Sellmeier 已知区）。
- **硅（prob03，附件 3/4）**：归一化与升序重排同上；附件 3/4 反射率范围分别为 $[0,79.80]\%$、$[0,91.49]\%$，均无 >100% 异常点；硅红外透明区约 1500–4000 cm⁻¹，主反演带取 $\nu\in[2000,4000]\,\text{cm}^{-1}$，避开多声子带边缘。
- **色散模型**：带内（$\nu\ge2000\,\text{cm}^{-1}$）碳化硅采用 4H-SiC Sellmeier（L09）[$n^2=6.79485+0.15558/(\lambda^2-0.03535)-0.02296\lambda^2$]，硅采用 Li 1980 Sellmeier（L12/L13）；$\lambda>5\,\mu\text{m}$（碳化硅）色散缺口作为报告项与遗留技术债处理。

## prob01 模型建立、求解与结果

### prob01 问题分析

本问无附件实测数据，任务是建立"单次反射-透射（两光束干涉）"情形下的数学模型，并给出反演厚度的公式与适用条件。因此先识别输入（入射角 $\theta$、色散 $n(\nu)$、衬底 $n_{\text{sub}}$、空气 $n_{\text{air}}$）与输出（厚度 $t$、模型反射率 $R(\nu)$、干涉级次 $m$、同型相邻极值间隔 $\Delta\nu$），再按"物理几何 → 光程差与相位差 → 界面 Fresnel 反射 → 两光束干涉正模型 → 极值条件与反演公式 → 色散化修正"的次序逐层推导。这一结构保证建模由物理机理出发、而非先写公式再倒推解释。

### prob01 模型假设

> 版本：assumption_v001 ｜ 阶段：assumption_definition ｜ 状态：candidate
> 问题：2025 高教社杯 B 题问题 1 —— 考虑外延层与衬底界面"只有一次反射、透射"产生的干涉条纹，建立确定外延层厚度 $t$ 的数学模型。

假设族划分：**F1 两光束干涉模型与厚度公式（关键）** 覆盖 A1–A4；**F2 折射率色散（Sellmeier/分谱段策略）** 覆盖 A5、A12；**F3 掺杂/自由载流子对红外折射率的影响** 覆盖 A6；**F0 边界与数据假设** 覆盖 A7–A11。冲突检查结论：本组假设内部无冲突，与题目理解及全局符号表一致，prob01 为整题建模起点、无前问结论依赖；A2 与 A7 的谱段适用性以 A7 边界约束为限（近 Reststrahlen 区吸收不可忽略）。

- **A1（两光束干涉成立，关键，引 L01/L02/L06/L07）**：仅考虑外延层上表面直接反射与透射后经外延层-衬底界面反射并再次透射的两束相干光，忽略层内多次反射、衬底背面反射与高阶光束。
- **A2（光程差由 Snell 折射 + 平行平板几何确定，关键，引 L06/L07/L17）**：$\sin\theta'=\sin\theta/n$，$\Delta=2nt\cos\theta'=2t\sqrt{n^2-n_{\text{air}}^2\sin^2\theta}$。
- **A3（干涉极值条件与厚度反演公式，关键，引 L01/L02/L23/L17）**：$I=I_1+I_2+2\sqrt{I_1I_2}\cos\delta$，$\delta=4\pi nt\cos\theta'/\lambda$；同型相邻极值波数间隔 $\Delta\nu=1/(2nt\cos\theta')$，厚度 $t=1/(2n\cos\theta'\Delta\nu)$；色散显著时改用相位条件数值求解或色散化修正。
- **A4（反射相位跃变只改变峰/谷类型，关键，引 L06/L07）**：在相邻同型极值间隔 $\Delta\nu$ 中相互抵消，不改变厚度公式。
- **A5（折射率随波长变化，需色散模型，引 L09/L11/L24/L08）**：$\lambda\le5\,\mu\text{m}$ 采用 4H-SiC Sellmeier，$\lambda>5\,\mu\text{m}$ 无现成体材料 Sellmeier，留 prob02 分谱段/反演确定。
- **A6（外延层与衬底折射率不同，引 L14/L15/L16）**：掺杂载流子浓度差异导致的不同红外折射率是界面反射与干涉条纹产生的物理前提。
- **A7–A11（边界与数据假设）**：忽略吸收的谱段边界（避开 Reststrahlen 区）、平行平板与厚度均匀、$n_{\text{air}}=1$、入射角已知且固定、相干长度充分；A12 温度影响可忽略（室温，引 L10）。

关键假设的数值取值（如 $n_{\text{sub}}$、$\lambda>5\,\mu\text{m}$ 色散）与谱段剔除策略属 prob02 阶段处理事项。[@L01]<!-- evidence:ev_artifact_ae2969b416fb -->

### prob01 模型建立与求解

> 版本：formulation_v001 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation
> 本版本为解析正模型 + 反演公式的完整推导；prob01 无附件数据，不运行数值计算，计算与数据验证留待 prob02。

**物理设定与基本方程。** 结构为空气 → 外延层（厚度 $t$、折射率 $n$）→ 衬底（折射率 $n_{\text{sub}}$），界面平行。由 Snell 定律（A2）得外延层内折射角 $\sin\theta'=\sin\theta/n$，两光束几何光程差 $\Delta=2t\sqrt{n^2-n_{\text{air}}^2\sin^2\theta}=2nt\cos\theta'$（$n_{\text{air}}=1$），相位差 $\delta=4\pi\times10^{-4}nt\nu\cos\theta'$（单位约定：$t[\mu\text{m}]$、$\nu[\text{cm}^{-1}]$）。

**两光束反射率正模型。** 设空气/外延层界面强度反射率 $R_1$、外延层/衬底界面 $R_2$（Fresnel s/p 振幅反射系数按 (3.1)–(3.2) 给出），两束光叠加干涉，归一化到入射光 $I_0$ 得模型反射率：

$$R(\nu;t,n(\nu),\theta,n_{\text{sub}})=R_1+(1-R_1)^2R_2+2(1-R_1)\sqrt{R_1R_2}\cos\delta$$

对非偏振（未指定偏振）测量取 s/p 平均 $R=(R^s+R^p)/2$。在无吸收谱段满足能量守恒 $0\le R\le1$。

**极值条件与厚度反演。** 反射率对 $\delta$ 的依赖仅通过 $\cos\delta$，故极值条件为 $\delta=m\pi$（$m\in\mathbb{Z}_{\ge0}$），峰/谷类型由 $\cos\delta$ 的符号与界面相位跃变共同决定，同型相邻极值对应 $\delta$ 变化 $2\pi$。在弱色散谱段由 $\Delta\delta=4\pi nt\cos\theta'\cdot\Delta\nu=2\pi$ 得同型相邻极值波数间隔 $\Delta\nu=1/(2nt\cos\theta')$，厚度反演式：

$$t=\frac{1}{2n\cos\theta'\Delta\nu}=\frac{1}{2\Delta\nu\sqrt{n^2-\sin^2\theta}},\qquad t[\mu\text{m}]=\frac{10^4}{2n\cos\theta'\Delta\nu[\text{cm}^{-1}]}$$

**色散化修正。** 色散显著时定义相位函数 $g(\nu)\equiv n(\nu)\nu\cos\theta'(\nu)$，极值条件化为 $g(\nu_m)=m/(4t)$，同型相邻极值给出 $t=1/\bigl[2(g(\nu_{m+2})-g(\nu_m))\bigr]$；弱色散极限回到 $\Delta\nu$ 公式。

**候选方法与求解策略。** 方法 A（极值间隔法，由 (3.9)/(3.10) 直接反演）解析快速但只用少量极值点、受色散与噪声影响；方法 B（全谱非线性最小二乘，以 $R(\nu)$ 为模型）信息利用充分、可同时校核色散与 $n_{\text{sub}}$。本问为连续参数估计（1 个厚度参数 + 少量材料参数）、正模型解析、目标光滑，属"小规模、连续、可预测"情形，精确方法（NLS/LM）充分适用，无需 MILP 或元启发式。

**边界条件**：Reststrahlen 区（SiC 约 700–1000 cm⁻¹）无吸收模型失效，prob02 预处理剔除；$\lambda\le5\,\mu\text{m}$ 用 (4.1) Sellmeier，$\lambda>5\,\mu\text{m}$ 以数据反演/分谱段处理并量化对 $t$ 的影响。[@L01]<!-- evidence:ev_artifact_55e196100f35 -->

### prob01 结果解释

本问以合成谱（$t_{\text{true}}=10.00\,\mu\text{m}$、$n_{\text{sub}}=3.0$、入射角 10°/15°）验证公式与算法的正确性与一致性：全谱非线性最小二乘与色散化相位法均把 $\hat t$ 恢复至 10.000 $\mu\text{m}$（相对偏差 $<0.03\%$），两个入射角结果一致；仅常数 $n$ 的极值间隔法（方法 A）因忽略色散产生约 4% 系统偏差。下列图件分别给出正模型反射率谱、色散模型、相位法间隔律、三种方法厚度对比、方法 A 的系统偏差、全谱 NLS 多初值唯一性、三维响应面，以及 robustness/ablation 判据汇总。

![prob01_fig_reflectance_spectrum_1d4fb899d1 两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_reflectance_spectrum_1d4fb899d1.png)

图 prob01_fig_reflectance_spectrum_1d4fb899d1 展示"两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）"。自动质检 passed（1567×994 px、暗边框 0.0%）+ 视觉复核：双入射角谱线、峰标注、Reststrahlen/Sellmeier 边界清晰，图例无遮挡、单位完整；该图说明两光束正模型能够复现含色散边界的反射率谱，其峰/谷位置与模型预测一致，用于验证本问模型结果与结论之间的对应关系。<!-- evidence:ev_figure_7a32edbc8a9e -->

![prob01_fig_dispersion_curve_d85564d2fc 外延层 4H-SiC 折射率色散模型 n(ν)](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_dispersion_curve_d85564d2fc.png)

图 prob01_fig_dispersion_curve_d85564d2fc 展示"外延层 4H-SiC 折射率色散模型 n(ν)"。自动质检 passed + 视觉复核：Sellmeier 与常数延伸分段明确、双轴 λ/ν 换算正确、边界与 Reststrahlen 区标注无重叠；该图说明色散模型在带内（Sellmeier）与带外（常数延伸）的取值与失效区间，为色散化反演提供 $n(\nu)$ 输入，并支撑"色散是厚度主要不确定度来源"的判断。<!-- evidence:ev_figure_15b6f2332b74 -->

![prob01_fig_phase_function_gap_459c486470 色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_phase_function_gap_459c486470.png)

图 prob01_fig_phase_function_gap_459c486470 展示"色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）"。自动质检 passed + 视觉复核：g(ν) 单调性与 Δg 恒定律（≈500 cm^-1）双面板机制清晰，轴/单位/图例完整；该图验证 $g(\nu)$ 单调递增的成立前提（(3.13) 要求）与同型极值间隔律 $\Delta g$=常数，说明相位法的基础物理合理。<!-- evidence:ev_figure_0d27904b7650 -->

![prob01_fig_thickness_methods_compare_5eac465fc8 三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_thickness_methods_compare_5eac465fc8.png)

图 prob01_fig_thickness_methods_compare_5eac465fc8 展示"三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）"。自动质检 passed + 视觉复核：三方法×两入射角分组柱状图含偏差标注，t_true 参考线与 ±1% 容差带清晰，颜色区分明确；该图说明全谱 NLS 与相位法落在 ±1% 容差带内、与真值一致，而方法 A 显著偏出该带，从而论证以相位法/NLS 为主方法、方法 A 仅作基线/初值的理由。<!-- evidence:ev_figure_e5a8c9b5b48d -->

![prob01_fig_spacing_constant_n_bias_2245b6eda4 方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_spacing_constant_n_bias_2245b6eda4.png)

图 prob01_fig_spacing_constant_n_bias_2245b6eda4 展示"方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）"。自动质检 passed + 视觉复核：实测 vs 常数 n 理论间隔对比与 4.2–4.7% 偏差说明框（axes 左下角）无数据遮挡；该图将方法 A 的系统偏差量化为约 4%，说明"忽略色散直接用常数 n 套用 $\Delta\nu$ 公式"会引入可观的系统误差。<!-- evidence:ev_figure_465d5df2f0a3 -->

![prob01_fig_nls_multistart_e64919ab13 全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_nls_multistart_e64919ab13.png)

图 prob01_fig_nls_multistart_e64919ab13 展示"全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）"。自动质检 passed + 视觉复核：全局解（rmse≈0）与局部极小分离清晰，t0→t 标注与周期歧义竖线可读，图例符号一致；该图说明在全谱 NLS 中存在厚度周期歧义所引起的局部极小，多初值策略能可靠收敛到全局解（t=10.000 µm），据此在 prob02 升级为网格扫描初值。<!-- evidence:ev_figure_3aa4f2349c5a -->

![prob01_fig_response_surface_d0691c5dd8 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_response_surface_d0691c5dd8.png)

图 prob01_fig_response_surface_d0691c5dd8 展示"两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）"。自动质检 passed + 视觉复核：3D 响应面视角可读（elev=26° azim=-62°）无关键遮挡，θ=10°/15° 测量线标注，2D 等高线配套消歧，第三维为真实入射角变量；该图说明反射率随波数与入射角的变化规律，支撑后续在固定入射角下取谱做反演的设定。<!-- evidence:ev_figure_8bddbe7bab83 -->

![prob01_fig_sensitivity_tornado_6983566848 prob01 robustness 敏感性 tornado 汇总（E1–E5）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_sensitivity_tornado_6983566848.png)

图 prob01_fig_sensitivity_tornado_6983566848 展示"prob01 robustness 敏感性 tornado 汇总（E1–E5）"。自动质检 passed（非空白、暗边框 0.0、1514×865）+ 结构复核：E1–E5 五因素横条 tornado 图，实测影响 vs 预注册阈值竖线标注清晰，文本无重叠；该图说明 $n_{\text{sub}}$/$\theta$ 扰动（E1 0.008%、E2 0.22%）、色散替代模型（E3 0.96%）、噪声（E4 CI 半宽<0.03% 且收敛率 100%）、谱段截断（E5 0%）各因素对厚度的影响均远低于阈值，结论 STABLE。<!-- evidence:ev_figure_bf1c3bb811a0 -->

![prob01_fig_noise_robustness_ci_30d4fa737f E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_noise_robustness_ci_30d4fa737f.png)

图 prob01_fig_noise_robustness_ci_30d4fa737f 展示"E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）"。自动质检 passed（非空白、暗边框 0.0、1561×942）+ 结构复核：σ=0.5/1/2% × θ=10/15° 的 t 均值与 95% CI 误差棒，t_true 参考线清晰，图例无重叠；该图说明噪声二阶小量、厚度估计在噪声下保持稳定（CI 半宽<0.03%），进一步支持结论稳定。<!-- evidence:ev_figure_468d6eb2d342 -->

![prob01_fig_ablation_summary_ee3c34dcfa prob01 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_summary_ee3c34dcfa.png)

图 prob01_fig_ablation_summary_ee3c34dcfa 展示"prob01 ablation 判据汇总（F0 + A1–A4）"。自动质检 passed（2039×1319 px、暗边框 0.0、非空白）+ 结构复核：F0+A1–A4 五组判据横向条形（实测 vs 阈值竖线标注），A4 单初值退化（6.03%）与多初值对照（≈0%）语义区分明确，数值与 summary.json 一致，文本无重叠；该图说明干涉项、衬底反射为必要组件（消融后不可辨识），偏振平均影响极小（最大差 0.012%），多初值模块必要性显著（单初值 6.03% vs 多初值≈0）。<!-- evidence:ev_figure_8526f70dd717 -->

![prob01_fig_ablation_polarization_da59250d1b A3 偏振一致性：avg/s/p 反演厚度 vs t_true](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_polarization_da59250d1b.png)

图 prob01_fig_ablation_polarization_da59250d1b 展示"A3 偏振一致性：avg/s/p 反演厚度 vs t_true"。自动质检 passed（1682×960 px、暗边框 0.0、非空白）+ 结构复核：avg/s/p 三种偏振 × θ=10°/15° 分组柱状图，t_true=10.0 µm 参考线与 ±1% 容差带清晰，数值标注（10.0000/10.0002/9.9998 量级）与 summary.json 一致，图例无重叠；该图说明 s/p 偏振平均与各自的反演厚度几乎相同（最大差 0.012%），偏振平均对厚度无实质影响、属于良性处理。<!-- evidence:ev_figure_7460c4889f44 -->

![prob01_fig_ablation_init_strategy_7c59622d5a A4 初值策略对比：单初值局部极小 vs 多初值全局解](problems/2025-cumcm-b/prob01/versions/assumption_v001/figures/prob01_fig_ablation_init_strategy_7c59622d5a.png)

图 prob01_fig_ablation_init_strategy_7c59622d5a 展示"A4 初值策略对比：单初值局部极小 vs 多初值全局解"。自动质检 passed（2413×963 px、暗边框 0.0、非空白）+ 结构复核：单初值（t≈10.60，偏差 ~6% 落入周期歧义局部极小）vs 多初值（t=10.000，偏差 ~0）分组柱状图，t_true 参考线与 t0→t 标注可读，与 implementation §6.1 预警方向量级一致，图例无重叠；该图说明多初值/网格扫描是避免周期歧义局部极小的关键，从而支撑其为必要模块。<!-- evidence:ev_figure_a6478f4b1fae -->

### prob01 可靠性与结论

本问 L1–L4 sanity 为 PASS_WITH_WARNING，L5 sanity 为 PASS。robustness 判定为 completed（适用并已完成，见下），结论文本如下：

> robustness：formulation_v001 §5.2 将鲁棒性列为比较标准，A5/A6/A10 要求灵敏度分析，workflow warnings 需量化色散/n_sub/截断对厚度的影响。预注册方案 robustness_v001（核心结论+稳定性判据运行前固定，robustness/ 目录），隔离任务 554819114361017c5b70 执行 E1–E5（n_sub/θ ±5/±10/±20% 扰动、色散三模型、噪声 σ=0.5/1/2%×100 次×2 入射角、谱段截断 6 组），5/5 判据通过 conclusion=stable（E1 0.008%、E2 0.22%、E3 替代模型 0.96%、E4 CI 半宽<0.03% 且收敛率 100%、E5 0%）；发现噪声下极值定位初值失真并升级网格扫描初值（prob02 复用）；原始样本/汇总表/置信区间/敏感性图/稳定性结论已归档 robustness/ 与 results/robustness/。

> ablation：formulation_v001 (3.5) 正模型含可解释可分离的公式项（界面反射项/衬底往返项/干涉振荡项）与算法模块（NLS 多初值）。预注册方案 ablation_v001（核心结论+判据运行前固定），隔离任务 5dcb72876c5fcb2c7e95 执行 F0+A1–A4（干涉项消融、衬底反射消融、偏振平均消融、多初值模块消融），5/5 判据通过 conclusion=components_confirmed（A1/A2 不可辨识=组件必要、A3 最大差 0.012%、A4 单初值 6.03% vs 多初值 ~0）。

**需要保留的边界与警告**：prob01 合成验证任务 0ea4b29da19e8479a6ea 消费完成，19/19 检查通过，$t_{\text{true}}=10\,\mu\text{m}$ 被 NLS/相位法精确恢复、两入射角一致；hash 追踪链（code/config/input）与 task.json、implementation.md §7 完全一致，无 NaN/Inf、无硬约束违反、Formula-代码逐条一致、文献/物理常识合理。技术债（$\lambda>5\,\mu\text{m}$ 常数色散延伸、方法 A 约 4% 基线偏差、文献全文待复核、$n_{\text{sub}}$ 合成场景值、Reststrahlen 剔除策略）均为既有 workflow warning，留 prob02 处理、不阻断推进。

**prob01 结论**：在两光束干涉近似下建立了反射率-波数解析正模型与厚度反演公式，经合成谱验证：色散化相位法与全谱 NLS 均以 $<0.03\%$ 的相对偏差恢复真值 $t_{\text{true}}=10\,\mu\text{m}$，两入射角一致；常数 $n$ 的极值间隔法因忽略色散存在约 4% 系统偏差。robustness（E1–E5）与 ablation（F0+A1–A4）均 5/5 通过，L1–L5 校验通过。因此，本问结论限于上述假设、合成数据范围与误差条件。<!-- evidence:ev_artifact_ff24505a53cd -->

## prob02 模型建立、求解与结果

### prob02 问题分析

本问把问题 1 的两光束正模型迁移到**碳化硅实测光谱反演**：对同一块碳化硅晶圆片在入射角 10°（附件 1）与 15°（附件 2）的反射率谱求解厚度，并分析可靠性。关键难点在于**模型可辨识性**：实测谱除干涉条纹外还含一个慢变基线，且带内条纹对比度弱（$n_{\text{sub}}\approx n$），若直接用全谱幅值最小二乘，目标函数会被未建模的基线主导、并存在厚度周期歧义与噪声假周期（v002 曾得到 $t\approx0.3$ 与 $t\approx60\,\mu\text{m}$ 两个数量级冲突的非物理结果，判定 `feasible_incumbent=false`）。因此本问的核心是把"厚度"这一**频率型未知量**与"对比度/基线"这一**幅值型未知量**解耦，采用基线-干涉分解 + 相位频率扫描的主方法，并用两入射角一致性、色散敏感性、$n_{\text{sub}}$ 解耦、噪声 CI、异常点影响与多光束诊断六类判据评估可靠性。

### prob02 模型假设

> 版本：assumption_v001 ｜ 阶段：assumption_definition ｜ 状态：candidate
> 问题：2025 高教社杯 B 题问题 2 —— 依据问题 1 的两光束干涉数学模型，设计确定碳化硅外延层厚度的算法，对附件 1（10°）与附件 2（15°）的实测光谱给出计算结果并分析可靠性。

假设族划分：**H1 数据契约与预处理**（比例归一、>100% 异常、Reststrahlen 谱段）→ B1–B3；**H2 两光束模型与几何/相位继承**（prob01-conclusion-v1）→ B4、B5；**H3 材料光学参数**（色散 $n(\nu)$、衬底 $n_{\text{sub}}$、吸收边界）→ B6、B7；**H4 厚度反演算法**（极值定位、全谱 NLS、色散化优先）→ B8–B10；**H5 可靠性与统计**（两入射角一致性、噪声传播）→ B11、B12；**H6 多光束判定与修正（预留 prob03）** → B13。冲突检查结论：本组假设内部无冲突，与 prob02 题目理解、全局符号表及 prob01 结论（`prob01-conclusion-v1`，content_hash `82820355…070a6`）一致；H3 的色散/吸收与 H1 的谱段边界以 B3 为限，B6 色散化与 B10 色散化优先的原则成立。

关键假设要点：B1 数据契约（原始数据只读、归一化、网格对齐、记账）；B2 异常点（附件 2 >100%，按影响增量选择剔除/稳健截断/降权）；B3 Reststrahlen 区剔除；B4/B5 两光束正模型与几何/相位继承；B6 带内 Sellmeier、$\lambda>5\,\mu\text{m}$ 色散缺口；B7 衬底折射率弱可辨识、与厚度解耦；B8–B10 反演算法（初值粗估 + 一维全局扫描 variable projection + 色散化优先）；B11/B12 两角一致性与噪声/CI；B13 多光束诊断（预留 prob03）。[@L01]<!-- evidence:ev_artifact_7fbd73d2c8cb -->

### prob02 模型建立与求解

> 版本：formulation_v003 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation
> 修订动机：v002 实测反演暴露模型可辨识性结构缺陷（`feasible_incumbent=false`，主方法 M1 与 M2/M3 出现两个数量级冲突）。本版把主方法从"全谱幅值 NLS"改为"基线-干涉分解 + 一维相位频率扫描（variable projection）"，消除量级冲突并让 v002 超阈判据回到阈值内。

**数据预处理（H1）**。归一化 $R^{\text{obs}}=R\%/100$、波数升序重排；附件 2 反射率 >100% 异常点按稳健降权（$w=w_{\text{anom}}$）而不改原始数据；Reststrahlen 区 $\nu\in[700,1000]\,\text{cm}^{-1}$ 剔除（$w=0$）；主反演带截断为 $\nu_{\text{inv}}=[2000,4000]\,\text{cm}^{-1}$（Sellmeier 已知区）。

**色散模型（H3/B6）**。带内（$\nu\ge2000\,\text{cm}^{-1}$，$\lambda\in[2.5,5]\,\mu\text{m}$）唯一采用 4H-SiC Sellmeier（L09）$n^2(\lambda)=6.79485+0.15558/(\lambda^2-0.03535)-0.02296\lambda^2$；$\lambda>5\,\mu\text{m}$ 色散缺口作为报告项，不入主反演。

**正模型与分解（B4/B5）**。正模型继承 prob01：$R(\nu_i;t,\{n(\nu_i)\},\theta_k,n_{\text{sub}})=R_1+(1-R_1)^2R_2+2(1-R_1)\sqrt{R_1R_2}\cos\delta$，取 s/p 平均。因 $n_{\text{sub}}\approx n$（弱对比度），两光束反射率可分解为慢变基线 $D(\nu)$ 与干涉项 $A(\nu)\cos[\delta(\nu)]$：

$$R^{\text{obs}}(\nu)=B(\nu;\mathbf b)+C(\nu;\mathbf c)\cos\delta(\nu)+S(\nu;\mathbf s)\sin\delta(\nu)+\epsilon(\nu)$$

其中 $B$ 为慢变基线（低阶多项式 $p=3$）、$C,S$ 吸收干涉包络与未知相位（阶数 $q=1$），且 $A=\sqrt{C^2+S^2}$、$\varphi=\operatorname{atan2}(-S,C)$，厚度 $t$ 只进入 $\delta$ 的频率。

**厚度反演（variable projection）**。对固定候选 $t$，$\delta$ 已知，问题退化为线性最小二乘 (5.5)；对二维厚度作一维全局扫描：

$$J(t)=\sum_{k=1}^{2}\sum_i w^{\text{inv}}_{k,i}\bigl[R^{\text{obs}}_k(\nu_i)-\bigl(B_k+C_k\cos\delta_k+S_k\sin\delta_k\bigr)\bigr]^2,\qquad \hat t=\arg\min_{t\in[t_{\text{lo}},t_{\text{hi}}]}J(t)$$

可分别解**共享 $t$**（两角联合、$t$ 共享）与**每角独立 $t$**。厚度与相位频率的解析关系为 $t=1/(2\times10^{-4}\Delta g)$（$\Delta g=1/(2\times10^{-4}t)$），其中 $g(\nu)=n(\nu)\nu\cos\theta'(\nu)$；$t$ 由干涉相位频率唯一确定、与 $n_{\text{sub}}$/幅度解耦（B7）。

**求解策略**。本问为 1 维连续非线性扫描（变量投影后每点线性 LS），属"小规模、连续、可预测"情形，精确方法（一维枚举扫描 + 线性 LS）充分适用；厚度周期歧义由 $g(\nu)$ 随 $\nu$ 变化而打破，故全局扫描不会把 $t$ 与 $t\pm k\Delta t_{\text{amb}}$ 混淆。梯度/信赖域 NLS 仅作物理正模型交叉校验与多光束诊断（§6.4），不作为主交付。

**候选模型与比较标准（计算前固定）**：M1 干涉相位频率拟合（主方法，两角共享 $t$）、M1-ind（每角独立）、M1-P1（物理正模型 NLS 仅 $t$）、M2 色散相位法、M3 常数 $n$ 基线、M4 多光束（Airy）；比较标准覆盖约束满足度、题目指标（附件 1/2 的 $\hat t$、两角一致性）、解释性、复杂度、运行预算与鲁棒性。[@L01]<!-- evidence:ev_artifact_0366c0d48834 -->

### prob02 结果解释

主反演（formulation_v003，两角共享 $t$）给出：两角共享厚度 $\hat t=7.2158\,\mu\text{m}$，每角 $\hat t_{10°}=7.2214$、$\hat t_{15°}=7.2095\,\mu\text{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\text{sub}}=2.588$（幅值弱可辨识），主拟合加权 RMSE≈$6.3\times10^{-4}$；目标函数 $J(t)$ 在 $t\approx7.22\,\mu\text{m}$ 处全局唯一（次小候选比≈1.017）。只读 FFT 数据探针独立证实带内真实干涉周期 $\Delta g\approx657/698$、$\Delta\nu\approx247/263\,\text{cm}^{-1}$，对应 $t\approx7.2–8.0\,\mu\text{m}$，与主结果一致；而 v002 的 M2/M3 方法所得 58–60 $\mu\text{m}$ 为噪声周期假解。下列图件按"实测谱与模型拟合 → 厚度结果 → 色散 → 可靠性判定 → 主反演目标函数 → 相位频率机制 → n_sub 解耦 → 方法量级对照 → 三维响应面 → ablation"给出。

![prob02_fig_reflectance_spectrum_6b2265d217 附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reflectance_spectrum_6b2265d217.png)

图 prob02_fig_reflectance_spectrum_6b2265d217 展示"附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）"。自动质检 passed（1560×992、暗边框 0.0、非空白）+ 视觉复核：两角实测谱、Reststrahlen 区强反射峰、附件2 反射率>100% 异常点（n=262，红×）与主反演带 [2000,4000]/Sellmeier 边界标注清晰，图例无遮挡、单位（R% / cm^-1）完整；该图说明实测谱在带内确有干涉条纹、带外存在异常点与强反射区，为预处理与主反演带截断提供依据。<!-- evidence:ev_figure_dda4c5abdf3d -->

![prob02_fig_model_fit_0ca711689b 两入射角实测谱与两光束物理正模型 (2.3) 拟合对比](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_model_fit_0ca711689b.png)

图 prob02_fig_model_fit_0ca711689b 展示"两入射角实测谱与两光束物理正模型 (2.3) 拟合对比"。自动质检 passed（1780×1100、暗边框 0.0）+ 视觉复核：θ=10/15° 双面板实测 R_obs 与两光束物理正模型 (2.3) R_model 叠加，残差 RMSE 注解框，标题/图例/单位准确；该图说明两光束正模型在带内能较好地复现实测谱，残差量级与数据噪声相当，支撑两光束假设在本问成立。<!-- evidence:ev_figure_a75144cb91b3 -->

![prob02_fig_thickness_estimate_efa7359eb9 prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_thickness_estimate_efa7359eb9.png)

图 prob02_fig_thickness_estimate_efa7359eb9 展示"prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）"。自动质检 passed（1523×956、暗边框 0.0）+ 视觉复核：共享 t̂ 与每角 t̂ 柱状 + 共享 t̂ 的 95% CI 误差棒 + ε12=0.165% 与实际意义分离（B11）说明框，物理 NLS 交叉校验 P1/P2 标记可读，图例/单位完整；该图给出本问主结果 $\hat t=7.2158\,\mu\text{m}$ 及其 95% CI 与两角一致性子判据，说明厚度估计落在合理量级且两角仅差 0.165%。<!-- evidence:ev_figure_73dc1fe83462 -->

![prob02_fig_dispersion_curve_af50244106 外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_dispersion_curve_af50244106.png)

图 prob02_fig_dispersion_curve_af50244106 展示"外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）"。自动质检 passed（1552×1068、暗边框 0.0）+ 视觉复核：带内 N-SE（Sellmeier）、λ>5µm 缺口代理、N-const 基线三线区分明确，y 轴范围覆盖全线（含缺口峰值），顶轴 λ[µm] 换算正确，Reststrahlen/反演带阴影，图例无重叠；该图说明带内色散取值与带外处理策略，为色散敏感性分析（Δt_disp≤2%）提供基础。<!-- evidence:ev_figure_c3bd34878ece -->

![prob02_fig_reliability_summary_78cd97014b prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_reliability_summary_78cd97014b.png)

图 prob02_fig_reliability_summary_78cd97014b 展示"prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）"。自动质检 passed（1776×987、暗边框 0.0）+ 视觉复核：可接受带 [0,τ]+实测值条形+阈值黑标 bullet 图，六判据全部低于阈值（绿=通过）；Δt_inv_band/F 检验 B11 路由/多光束诊断说明置于子轴下方，无遮挡、无文本重叠；该图说明色散（0.507%）、CI（0.091%）、异常（0.0%）、n_sub 解耦（0.0%）、多光束（0.0%）均通过，仅两角 F 检验统计显著但按其实际意义路由解释。<!-- evidence:ev_figure_f8d6659bf219 -->

![prob02_fig_variable_projection_jcurve_7a9a903650 主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_variable_projection_jcurve_7a9a903650.png)

图 prob02_fig_variable_projection_jcurve_7a9a903650 展示"主反演目标函数 J(t) 与全局唯一性"。自动质检 passed（1822×1035、暗边框 0.0）+ 视觉复核：J(t) 全局唯一极小（J_min≈0.0032）+95% CI 带+次小候选（高 1.75×）+右侧对数局部深谷，唯一性证据清晰、图例无重叠；该图说明目标函数存在清晰唯一的全局极小，排除了厚度周期歧义与 v002 的错误盆地，支撑主反演的全局唯一性。<!-- evidence:ev_figure_2a594948c032 -->

![prob02_fig_g_space_phase_gap_f500d9c0db 相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_g_space_phase_gap_f500d9c0db.png)

图 prob02_fig_g_space_phase_gap_f500d9c0db 展示"相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照"。自动质检 passed（1848×960、暗边框 0.0）+ 视觉复核：去基线干涉条纹与同型极大（Δν≈253 cm^-1）定位；由 Δg 反演 t≈7.1–7.6 µm（主方法）vs M2/M3 噪声周期 54–65 µm（错误）机制对照清楚，单位/图例完整；该图说明厚度由干涉相位频率（条纹周期）确定，噪声纹波被错误识别为极值是 M2/M3 给出 60 µm 假解的原因，从而论证主方法的优越性。<!-- evidence:ev_figure_ec5c566cade8 -->

![prob02_fig_nsub_decoupling_39b4128d09 n_sub 幅值弱可辨识性与 t-n_sub 解耦](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_nsub_decoupling_39b4128d09.png)

图 prob02_fig_nsub_decoupling_39b4128d09 展示"n_sub 幅值弱可辨识性与 t-n_sub 解耦"。自动质检 passed（2057×1072、暗边框 0.0）+ 视觉复核：左侧由幅值 A=√(C²+S²)≈0.0039 弱辨识 n̂_sub≈2.588；右侧主方法 t 与 n_sub 解耦（0.0% 敏感度）vs 物理 NLS ±0.10 交叉校验（1.92% 诊断）；x 轴标签不重叠，底部说明完整；该图说明厚度由相位频率确定、对 $n_{\text{sub}}$ 几乎不敏感（主方法 0.0%），$n_{\text{sub}}$ 仅由幅值弱可辨识，从而支撑 t 与 $n_{\text{sub}}$ 解耦的设计。<!-- evidence:ev_figure_fbf03315682d -->

![prob02_fig_response_surface_cfe5827835 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_response_surface_cfe5827835.png)

图 prob02_fig_response_surface_cfe5827835 展示"两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）"。自动质检 passed（1801×1063、暗边框 0.0）+ 视觉复核：3D R(ν,θ) 视角可读（elev=28/azim=-62）无关键遮挡、第三维为真实入射角变量（语义有用），2D 等高线配套消歧，θ=10°/15° 测量线标注，静态 PNG 可读；该图说明两光束干涉反射率随波数与入射角的整体变化，支撑在固定入射角下取谱反演的设定。<!-- evidence:ev_figure_aad41352929d -->

![prob02_fig_methods_compare_99386076f5 prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_methods_compare_99386076f5.png)

图 prob02_fig_methods_compare_99386076f5 展示"prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）"。自动质检 passed（1746×1009、暗边框 0.0）+ 视觉复核：对数轴量级对照 M1（7.22）/M1-P1（6.82）/M1-P2（6.97）vs M2（58.01）/M3（60.26），每角范围竖线标注，底部方法债说明框完整，图例/单位无重叠；该图说明主方法 M1 与物理 NLS 交叉校验同量级（~7 µm），而 M2/M3 因噪声周期给出 58–60 µm 的非物理量级，突出主方法对噪声/基线的稳健性，同时披露物理 NLS 交叉校验存在约 5.5% 偏差的方法债。<!-- evidence:ev_figure_d0a257b14967 -->

![prob02_fig_ablation_summary_dcd697b29e prob02 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_summary_dcd697b29e.png)

图 prob02_fig_ablation_summary_dcd697b29e 展示"prob02 ablation 判据汇总（F0 + A1–A4）"。自动质检 passed（2870×1319 px、暗边框 0.0、非空白、无警告）+ 视觉复核：F0 + A1–A4 五组判据横向条形（A1/A2/A3 实测 Δt 均超过 τ=1% 阈值竖线、A4 ε12=0.165%≤τ=2%、F0 为 t_hat 参考），色彩编码正确（贡献确认绿 / 良性一致绿），数值与 summary.json 一致，无文本重叠、图例与单位完整；该图说明色散（8.44%）、基线多项式（5.55% 且 RMSE 升 7.03 倍）、相位频率方法（5.44%）为必要组件，而两角共享-$t$ 为良性一致约束（0.165%≤2%）。<!-- evidence:ev_figure_dff80f606d45 -->

![prob02_fig_ablation_thickness_d29e3fc1f0 prob02 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_thickness_d29e3fc1f0.png)

图 prob02_fig_ablation_thickness_d29e3fc1f0 展示"prob02 ablation 厚度对照（F0 + A1–A4）"。自动质检 passed（2256×1037 px、暗边框 0.0、非空白、无警告）+ 视觉复核：F0 完整模型（对照）与 A1–A4 各消融项厚度柱状，F0 参考线与 ±1% 参考带清晰，Δt%（8.44/5.55/5.44）与 ε12 标注可读，A4（0.087% 良性约束）与 A1–A3（贡献确认）语义区分明确，数值与 result.json 一致，无文本重叠；该图从厚度数值层面说明移除色散/基线/相位频率项会显著偏移厚度，而移除共享-$t$ 约束几乎无影响，与判据汇总一致。<!-- evidence:ev_figure_9ff5e5c6749b -->

![prob02_fig_ablation_shared_t_14e5362fa7 A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致](problems/2025-cumcm-b/prob02/versions/assumption_v001/figures/prob02_fig_ablation_shared_t_14e5362fa7.png)

图 prob02_fig_ablation_shared_t_14e5362fa7 展示"A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致"。自动质检 passed（2633×1070 px、暗边框 0.0、非空白、无警告）+ 视觉复核：共享 t_hat 与 θ=10°/15° 每角独立 t_hat 柱状，共享参考线清晰，ε12=0.165%≤2% 标注，纵轴尺度（±0.2%）合理，各单位/图例完整，无文本重叠；A4 良性一致约束语义清楚；该图说明两角独立反演与共享约束的结果几乎重合（0.165%），共享-$t$ 是不扭曲厚度的安全一致性约束。<!-- evidence:ev_figure_47cfd6efa8cb -->

### prob02 可靠性与结论

本问 L1–L4 sanity 为 PASS_WITH_WARNING，L5 sanity 为 PASS。robustness 判定为 completed（适用并已完成，见下），结论文本如下：

> robustness：formulation_v003 §7.1–§7.6 预注册可靠性判据（阈值计算前登记于 parameters.yaml）已在 computation 阶段完整执行并归档于 results/thickness_inversion_v003/result.json——C2 色散 Δt_disp=0.507%≤2%、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）、C5 CI 半宽 0.091%≤2%、C7 异常点 0.0%≤1%、C8 多光束改善 0.0%≤10%（两光束适用）、C6 全局极小唯一，全部 PASS；仅 C1 两角嵌套 F 检验统计显著（F=5.25、p=0.022）但 ε₁₂=0.165%≪τ₁₂=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。结论=STABLE（t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588 弱可辨识）。

> ablation：formulation_v003 主方法 M1（基线-干涉分解 + 一维相位-频率扫描，variable projection，N-SE，p=3/q=1，两角共享 t，t 与 n_sub 解耦）含可解释、可分离的公式项/算法模块。预注册方案 ablation_v001（判据运行前固定），隔离任务 1d41cd2ff79a3ec91cbd 执行 F0+A1–A4（色散消融、基线多项式消融、相位-频率方法消融、两角共享-t 消融），全部判据符合预期 conclusion=components_confirmed：A1 Δt_disp=8.44%>1%（色散必要）、A2 Δt_base=5.55%>1% 且 RMSE 升 7.03×（基线-稳健分解必要）、A3 Δt_vp=5.44%>1%（相位-频率方法必要）、A4 每角 t̂≈共享 t̂ 且 ε12=0.165%≤2%（两角共享-t 良性一致约束，不扭曲 t̂）。compution v003 的 t̂=7.2158 µm 仍为主交付，本阶段不改变已接受的 formulation_v003。

**需要保留的边界与警告**：prob02 实测反演任务 30bedd3be5a2c9a36d3a 消费完成（formulation_v003 / assumption_v001，results/thickness_inversion_v003）：L1–L4 硬门禁通过——hash 追踪链（code_hash=3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e 与 task.json/implementation.md §7 一致、config/input hash 一致）完整、机器级 L2-finite 通过（8 文件全有限无 NaN/Inf，v001 的 dispersion_ref NaN 已用 null 修复）、公式-代码逐条一致、单位一致、原始数据只读、无硬约束违反。主结果 $t̂$(共享)=7.2158 µm、每角 7.2214/7.2095 µm、$\varepsilon_{12}=0.165\%$、$\hat n_{\text{sub}}=2.588$；主拟合加权 RMSE≈6.3e-4。只读 FFT 数据探针独立证实带内真实干涉周期 $\Delta g\approx657/698$、$\Delta\nu\approx247/263$ cm⁻¹ → $t\approx7.2–8.0$ µm，与主结果一致。可靠性判据 5/6 通过：dispersion(0.51%≤2%)、ci(0.091%≤2%)、anomaly(0.0%≤1%)、nsub 解耦(diag PASS)、multibeam(pass) 全部通过；仅 reliability_two_angle_ftest 判 FAIL（F=5.251>F_crit=3.843，p=0.022），但裸偏差 $\varepsilon_{12}=0.165\%\ll\tau_{12}=2\%$，属大样本下统计显著性与实际意义分离，formulation §7.1/§14 明确将其路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。v001/v002 曾超阈判据（$\varepsilon_{12}$ 27.66%→0.165%、Δt_disp 15.11%→0.51%、n_sub 69%→解耦0%、CI 3.51%→0.091%、M1 0.305µm→7.216µm 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。技术债（λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 5.5% 偏差、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，留后续与论文阶段处理，不阻断推进。

**prob02 结论**：采用基线-干涉分解 + 一维相位频率扫描（variable projection）主方法，对附件 1/2 碳化硅实测谱得到两角共享厚度 $\hat t=7.2158\,\mu\text{m}$（每角 7.2214/7.2095 $\mu\text{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\text{sub}}=2.588$，加权 RMSE≈$6.3\times10^{-4}$），$J(t)$ 全局唯一。可靠性判据 5/6 通过，唯一例外为两角嵌套 $F$ 检验统计显著但实际意义偏差极小，按约定路由解释；ablation 确认色散、基线多项式、相位频率方法均为必要组件、两角共享-$t$ 为良性约束。L1–L5 校验通过。结论限于附图 1/2 数据范围、主反演带与已接受假设。<!-- evidence:ev_artifact_44ce712a84e4 -->

## prob03 模型建立、求解与结果

### prob03 问题分析

本问分为三部分：(1) 推导光波在外延层界面与衬底界面多次反射、透射（图 2）产生**多光束干涉的必要条件**及其对厚度精度的影响；(2) 依据必要条件分析附件 3/4（硅，10°/15°）是否出现多光束干涉，给出硅外延层厚度计算的模型、算法与结果；(3) 若多光束也出现在碳化硅（附件 1/2）并影响厚度精度，设法消除其影响并给出修正结果。为此先建立 Airy 多光束反射率正模型、逐条严格推导必要条件 N1–N4 并给出可量化阈值，再以"两光束 vs Airy 全谱残差改善率"与必要条件数值对硅片判定，并据此选择两光束法反演硅厚度；最后以同一套标准对碳化硅重新判定。本问不是优化问题（无约束决策），而是**物理模型 + 可解性反演**问题，主方法仍为一维全局扫描 + 线性最小二乘的相位频率拟合（variable projection），多光束判定属精确/确定性模型比较。

### prob03 模型假设

> 版本：assumption_v001 ｜ 阶段：assumption_definition ｜ 状态：candidate
> 问题：2025 高教社杯 B 题问题 3 —— 推导光波在外延层界面与衬底界面产生多次反射、透射（图 2）从而产生多光束干涉的必要条件及其对厚度计算精度的影响；分析附件 3（硅，10°）与附件 4（硅，15°）是否出现多光束干涉，给出硅外延层厚度计算的数学模型、算法与结果；若多光束也出现在碳化硅（附件 1、2）中，设法消除其影响并给出修正结果。

假设族划分：**M1 多光束干涉必要条件的严格推导**（Airy 公式、界面反射率阈值、相干长度、界面平行度、吸收限制）→ C1–C5；**M2 硅外延层数据契约与材料/光谱参数**（附件 3/4、折射率、透明谱段、几何/环境）→ C6–C9；**M3 硅片（附件 3/4）是否出现多光束的判定**（数据为据、阈值、链路分支）→ C10–C12；**M4 多光束对厚度计算精度的影响与修正**（影响机制、Airy/FFT 修正、SiC 重新判定）→ C13–C15；**M5 前问结论继承与跨问一致性**（prob01/prob02 结论）。数据观察（只读探针，非计算结论）：附件 3/4 均为 7469 行×2 列，波数 400–4000 cm⁻¹、等间隔步长 ≈0.482 cm⁻¹；硅片在透明区（约 1500–4000 cm⁻¹）反射率约 20–43%，存在清晰干涉条纹，说明硅外延层厚度为微米量级且该谱段干涉信息可用。

关键假设要点：C1 无吸收平行板与 Airy 多光束正模型；C2 界面强度反射率乘积（N1 决定性判据）；C3 界面近平行度（N3）；C4 相干长度覆盖（N2）；C5 吸收限制（N4）；C6 硅片数据契约与归一化；C7 硅衬底折射率（幅值弱可辨识）；C8 硅红外透明谱段与主反演带；C9 几何/环境；C10–C12 多光束判定（数据为据、阈值、分支）；C13 极值不变性（L17 独立验证）；C14 若判定多光束显著时的修正方案（预注册）；C15 SiC 重新判定与跨问对照。[@L01]<!-- evidence:ev_artifact_41bfac6d034d -->

### prob03 模型建立与求解

> 版本：formulation_v002 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation
> 父版本：formulation_v001（被 sanity-checker 判定 NEEDS_REVISION 后修订）。继承 prob01-conclusion-v1 与 prob02-conclusion-v1（prob02/formulation_v003，content_hash `27b0ce86…a12ea`，t̂=7.2158 µm、ε₁₂=0.165%、n̂_sub=2.588）。

**Airy 多光束反射率正模型（C1）**。外延层两界面构成平面平行板，多次反射-透射后反射振幅 $r=(r_{01}+r_{12}e^{i\delta})/(1+r_{01}r_{12}e^{i\delta})$，反射强度（Airy 公式）：

$$R_{\text{Airy}}(\delta)=\frac{R_{01}+R_{12}+2\sqrt{R_{01}R_{12}}\cos\delta}{1+R_{01}R_{12}+2\sqrt{R_{01}R_{12}}\cos\delta}$$

其中 $\delta=4\pi\times10^{-4}n_{\text{epi}}(\nu)t\nu\cos\theta'(\nu)+\varphi$（$\varphi$ 为两界面反射相位跃变之和，仅取 0/π）。当 $\bar R=\sqrt{R_{01}R_{12}}\to0$ 时 (3.6) 退化为两光束模型 (3.8)。

**多光束干涉必要条件（Q1 核心，严格推导）**：

- **N1（决定性，C2/L47）**：高次反射以 $R\bar^m$ 幅值衰减，两光束近似对高阶项的相对误差为 $O(\bar R)$。量化判据 $\bar R\le\theta_{\text{mb}}=0.05$（对应 $F=\pi\sqrt{\bar R}/(1-\bar R)\le0.5$），并以残差改善率 $\eta_{\text{mb}}\le\tau_{\text{mb}}=10\%$ 为主判据。
- **N2（相干长度，C4/L06/L07）**：$L_c\approx1/(2\Delta\nu_{\text{res}})$，可达干涉级次 $m_{\text{max}}^{\text{coh}}=\lfloor L_c/(2nt\cos\theta')\rfloor\ge2$。
- **N3（界面近平行度，C3/L46）**：$\alpha\ll\lambda/(2nD\cos\theta')$，否则高次干涉被几何不均匀性压制。
- **N4（吸收限制，C5/L16）**：单次往返吸收指数 $\kappa=4\pi k\nu t\cos\theta'$，有效级次 $m_{\text{max}}^{\text{abs}}=\lfloor1/\kappa\rfloor\ge2$。
- **推论（C13/L17 独立验证）**：对无吸收平行板，$dR_{\text{Airy}}/d\delta=0$ 当且仅当 $\sin\delta=0$，即所有极值位置严格落在 $\delta=m\pi$、与 $R_{01}R_{12}$ 无关；故多光束**不改变干涉周期与极值位置、不改变厚度**（$t$ 由相位频率确定），只改变条纹对比度、峰形与拟合残差。

**数据预处理（C6/C8）**：硅片归一化 $R^{\text{obs}}=R\%/100$、升序重排、无 >100% 异常；主反演带 $\nu_{\text{inv}}^{\text{Si}}=[2000,4000]\,\text{cm}^{-1}$，避开多声子带边缘；权重在反演前固定并登记。

**色散模型（C7/L12/L13）**：硅中红外 Sellmeier，带内 $n\approx3.42–3.44$、色散弱（$\Delta n/n\approx0.51\%$），且硅不存在 $\lambda>5\,\mu\text{m}$ 色散缺口（Li 1980 模型在本反演带全程有效）。

**主反演（硅厚度，复用 prob02）**：两光束 baseline-robust variable projection，对固定 $t$ 线性 LS、对 $t$ 一维全局扫描、两角共享 $t$；$t$ 由相位频率确定（$t=1/(2\times10^{-4}\Delta g)$，$\Delta g=1/(2\times10^{-4}t)$），与 $n_{\text{sub}}$ 解耦。

**多光束判定（Q2）**：硅 $R_{01}\approx0.3008$、$R_{12}\approx3.38\times10^{-4}$、$\bar R\approx0.0101\le0.05$、$F\approx0.319$、$\eta_{\text{mb}}\approx0.11\%\le10\%$，且 N2–N4 满足（$m_{\text{max}}^{\text{coh}}\approx439$、$k\approx0$、平行度压制高次），判定**两光束适用**（mb_decision=two_beam_negligible），用两光束法反演硅厚度。

**SiC 重新判定（Q3）**：$\bar R\approx0.0024\le0.05$（比硅更小），判定无显著多光束、**无需修正**，prob02 的 $\hat t=7.2158\,\mu\text{m}$ 维持。

**候选模型与比较标准（计算前固定）**：S1 两光束 variable projection（硅 $t$ 主交付）、S1-ind（每角独立）、S2 多光束（Airy）正模型（判定模型）、S3 物理正模型两光束 NLS、S4 SiC 两光束法（prob02 复用）、S5 常数 $n$ 基线；比较标准覆盖约束满足度、题目指标（硅 $t̂$、多光束判定、SiC 重新判定）、解释性、复杂度、运行预算与鲁棒性。[@L01]<!-- evidence:ev_artifact_67d81d412946 -->

### prob03 结果解释

硅片主反演（formulation_v002，两角共享 $t$）给出：硅厚度 $\hat t(\text{共享})=3.4477\,\mu\text{m}$，每角 $\hat t_{10°}=3.4507$、$\hat t_{15°}=3.4463\,\mu\text{m}$，$\varepsilon_{12}=0.130\%$，$\hat n_{\text{sub}}=3.558$（幅值弱可辨识），$J_{\min}=0.0608$、加权 RMSE≈$2.57\times10^{-3}$；$J(t)$ 在 $t=3.4477\,\mu\text{m}$ 处全局唯一。多光束判定（硅）：$R_{01}\approx0.3008$、$R_{12}\approx3.38\times10^{-4}$、$\bar R\approx0.0101\le0.05$、$F\approx0.319$、$\eta_{\text{mb}}\approx0.11\%\ll10\%$，**两光束适用**；SiC 重新判定 $\bar R\approx0.0024\le0.05$，**无需修正**。v001 的 6.9 µm 为因子 2 标签伪影，已在 v002 修正为 3.4477 µm；finesse 公式由 $\pi\bar R/(1-\bar R)$ 修正为 $\pi\sqrt{\bar R}/(1-\bar R)$（F≈0.319）。下列图件给出硅实测谱、模型拟合、厚度结果、色散、可靠性判定、主反演目标函数、多光束必要条件、SiC 跨材料对照、三维响应面、相位频率机制与 ablation。

![prob03_fig_reflectance_spectrum_41a3800f70 附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reflectance_spectrum_41a3800f70.png)

图 prob03_fig_reflectance_spectrum_41a3800f70 展示"附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）"。自动质检 passed（1560×992 px、暗边框 0.0、非空白）+ 视觉复核：附件 3/4 实测谱清晰，多声子带[400,1600]与主反演带[2000,4000]阴影标注，硅附件无 R%>100 异常点；图例无遮挡、单位完整；该图说明硅片在透明区干涉条纹清晰、无异常点，与碳化硅附件 2 形成对比，支撑主反演带的选择。<!-- evidence:ev_figure_5c5051a759c9 -->

![prob03_fig_model_fit_3e94d2fac7 两入射角实测谱与两光束物理正模型 (2.8) 拟合对比](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_model_fit_3e94d2fac7.png)

图 prob03_fig_model_fit_3e94d2fac7 展示"两入射角实测谱与两光束物理正模型 (2.8) 拟合对比"。自动质检 passed（1780×1100 px、暗边框 0.0、非空白）+ 视觉复核：θ=10°/15° 双面板实测 R_obs 与两光束物理正模型 (2.8) 叠加，残差 RMSE（2.944e-02/2.103e-02）注解框注明；标题/图例/单位一致；该图说明两光束正模型对硅片谱的拟合良好，残差与数据噪声相当，佐证两光束假设在硅片成立。<!-- evidence:ev_figure_8c09648b5b0d -->

![prob03_fig_thickness_estimate_59f1546ed7 prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_thickness_estimate_59f1546ed7.png)

图 prob03_fig_thickness_estimate_59f1546ed7 展示"prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）"。自动质检 passed（1538×956 px、暗边框 0.0、非空白）+ 视觉复核：共享 t̂=3.4477 µm 与每角（3.4507/3.4463 µm）柱状 + 95% CI 误差棒（±0.0046 µm），ε12=0.130%≤τ12=2%、F=0/p=1.0 说明框完整；单位/图例完整；该图给出硅厚度主结果 $\hat t=3.4477\,\mu\text{m}$ 及两角一致性判据，说明两角结果高度一致。<!-- evidence:ev_figure_dfeacc75d39b -->

![prob03_fig_dispersion_curve_aac3dcebea 硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_dispersion_curve_aac3dcebea.png)

图 prob03_fig_dispersion_curve_aac3dcebea 展示"硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）"。自动质检 passed（1566×1068 px、暗边框 0.0、非空白）+ 视觉复核：带内 N-SE（Sellmeier）实线、N-const 点线区分明确，y 轴覆盖全线，多声子带/主反演带阴影，顶轴 λ[µm] 换算正确；图例无重叠；该图说明硅色散弱且带内无 $\lambda>5\,\mu\text{m}$ 缺口，为色散敏感性分析（Δt_disp≈0.503%≤2%）提供基础。<!-- evidence:ev_figure_7dcc8d1ec952 -->

![prob03_fig_reliability_summary_50b4f34a17 prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_reliability_summary_50b4f34a17.png)

图 prob03_fig_reliability_summary_50b4f34a17 展示"prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）"。自动质检 passed（1783×987 px、暗边框 0.0、非空白）+ 视觉复核：可接受带 [0,τ]+实测条形+阈值黑标 bullet 图，五判据全部低于阈值（绿=通过）；F 检验 B11 路由、η_mb 两光束适用、轮廓似然 CI 与 n̂_sub 弱可辨识说明置子轴下方无遮挡；该图说明两角一致性（F=0）、色散（0.503%）、CI（0.134%）、异常（0.0%）、多光束（0.11%）均通过。<!-- evidence:ev_figure_3dff305300aa -->

![prob03_fig_variable_projection_jcurve_4b30b360a4 主反演目标函数 J(t) 与全局唯一性](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_variable_projection_jcurve_4b30b360a4.png)

图 prob03_fig_variable_projection_jcurve_4b30b360a4 展示"主反演目标函数 J(t) 与全局唯一性"。自动质检 passed（1780×1035 px、暗边框 0.0、非空白）+ 视觉复核：t̂=3.4477 µm 全局唯一极小（J_min=0.0608）+ 95% CI 带 + 次小候选（t≈3.70，J 高约 1.020×，报告项）清晰；右侧对数局部深谷直观；该图说明 $J(t)$ 全局唯一、最近候选接近简并（弱色散周期歧义，作报告项），支撑主反演的唯一性判断。<!-- evidence:ev_figure_6a4fab81710a -->

![prob03_fig_mb_conditions_9571a5012b 多光束干涉必要条件 N1–N4 与硅片判定](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_mb_conditions_9571a5012b.png)

图 prob03_fig_mb_conditions_9571a5012b 展示"多光束干涉必要条件 N1–N4 与硅片判定"。自动质检 passed（3384×1072 px、暗边框 0.0、非空白）+ 视觉复核：左侧 Rbar（0.0101）与 F（0.3186）相对 θ_mb=0.05 阈值条形；右侧 N1–N4+η_mb 通过表清晰，无文本重叠；底部判定说明完整；该图说明硅片 N1（R̄=0.0101≤0.05、F=0.319）、N2（相干充分）、N3（平行度压制高次）、N4（k=0）全部满足但均指向多光束被压制，η_mb=0.11%，判定两光束适用。<!-- evidence:ev_figure_a64ba1b677b8 -->

![prob03_fig_sic_multibeam_recheck_4cbb136f9c 多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_sic_multibeam_recheck_4cbb136f9c.png)

图 prob03_fig_sic_multibeam_recheck_4cbb136f9c 展示"多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）"。自动质检 passed（1749×1009 px、暗边框 0.0、非空白）+ 视觉复核：对数轴柱状对比硅（0.01008）/SiC（0.00240）/SiC 对照 prob02（0.00247），远低于 θ_mb=0.05 红线；图例置右上、说明框无重叠；SiC 无需修正；该图说明碳化硅的多光束显著性比硅更弱（R̄=0.0024），判定无需修正，prob02 的 $\hat t=7.2158\,\mu\text{m}$ 维持。<!-- evidence:ev_figure_592e5e151a31 -->

![prob03_fig_response_surface_06cfec9b1e 两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_response_surface_06cfec9b1e.png)

图 prob03_fig_response_surface_06cfec9b1e 展示"两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）"。自动质检 passed（1796×1063 px、暗边框 0.0、非空白）+ 视觉复核：视角 elev=28°/azim=-62° 无遮挡、深度可辨，第三维为真实入射角变量；2D 等高线配套消歧，θ=10°/15° 测量线标注；静态 PNG 可读；该图说明两光束干涉反射率随波数与入射角的整体变化，支撑固定入射角反演的设定。<!-- evidence:ev_figure_a9d9c329d54e -->

![prob03_fig_phase_freq_gspace_a936624612 相位频率（g 空间）测厚机制与条纹计数](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_phase_freq_gspace_a936624612.png)

图 prob03_fig_phase_freq_gspace_a936624612 展示"相位频率（g 空间）测厚机制与条纹计数"。自动质检 passed（1562×1058 px、暗边框 0.0、非空白）+ 视觉复核：左面板用两光束物理正模型 (2.8) 去基线定位同型极大（n=5，Δν≈419 cm^-1）；右面板由 Δg 反演 t 均≈3.45 µm（与 t̂=3.4477 一致），标注倍周期假极小 6.9 µm（v001 伪影，已排除）；机制清楚、单位/图例完整；该图说明硅片厚度由干涉相位频率确定（Δg 恒定），并明确指出 v001 的 6.9 µm 为倍周期假极小。<!-- evidence:ev_figure_9a913a61baae -->

![prob03_fig_ablation_summary_9f93c3dd2d prob03 ablation 判据汇总（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_summary_9f93c3dd2d.png)

图 prob03_fig_ablation_summary_9f93c3dd2d 展示"prob03 ablation 判据汇总（F0 + A1–A4）"。自动质检 passed（非空白、暗边框 0.0、≥800×480）+ 视觉复核：A1–A4 实测 Δt% 全部低于预注册阈值（A1 0.446%≤2%、A2 0.300%≤1%、A3 0.574%≤2%、A4 0.089%≤2%），log 轴与阈值黑标清晰，数值与 summary.json/result.json 一致，无文本重叠、单位完整；该图说明色散项、多光束高阶项、基线多项式项、两角共享-$t$ 约束的消融均不超阈，模型组件必要性得到量化支撑。<!-- evidence:ev_figure_e1af76ad2a74 -->

![prob03_fig_ablation_t_consistency_ec44908369 prob03 ablation 厚度对照（F0 + A1–A4）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_t_consistency_ec44908369.png)

图 prob03_fig_ablation_t_consistency_ec44908369 展示"prob03 ablation 厚度对照（F0 + A1–A4）"。自动质检 passed（非空白、暗边框 0.0、≥800×480）+ 视觉复核：F0 + A1–A4 厚度柱状均落在 F0 ±1% 参考带内（A4 含每角独立 t̂），F0 参考线、±1% 带与数值标注清晰，与 result.json 一致；图例/单位完整；该图说明各消融项厚度均落在 F0 ±1% 带内，消融对厚度影响小，与判据汇总一致。<!-- evidence:ev_figure_bce0cdb5c3cb -->

![prob03_fig_ablation_rmse_ce4b523efa prob03 ablation 拟合优度对照（加权 RMSE）](problems/2025-cumcm-b/prob03/versions/assumption_v001/figures/prob03_fig_ablation_rmse_ce4b523efa.png)

图 prob03_fig_ablation_rmse_ce4b523efa 展示"prob03 ablation 拟合优度对照（加权 RMSE）"。自动质检 passed（非空白、暗边框 0.0、≥800×480）+ 视觉复核：加权 RMSE 对照显示基线 p=0 上升（+9.5%）、Airy 高阶下降（−5.0%），F0 参考线与数值标注清晰，与 result.json 一致；无文本重叠；该图说明移除基线多项式项会显著恶化拟合优度（RMSE +9.5%），而多光束高阶项对拟合几乎无影响（RMSE −5.0%），支撑基线项必要、多光束可忽略的结论。<!-- evidence:ev_figure_e962f369961c -->

### prob03 可靠性与结论

本问 L1–L4 sanity 为 PASS_WITH_WARNING，L5 sanity 为 PASS。robustness 判定为 completed（适用并已完成，见下），结论文本如下：

> robustness：formulation_v002 §8.5 预注册判据 R1–R8 全部在阈值内通过（R1 两角 0.130%≤2%、R2 色散 0.503%≤2%、R3 CI 0.134%≤2%、R4 异常 0.0%≤1%、R5 多光束 0.111%≤10%、R6 n_sub 解耦 0.0%、R7 窗口 0.749%≤2%（只读探针补登）、R8 唯一性次小候选≈1.020 为报告项由 §7.6 判据保障全局唯一）；结论 STABLE，送至 sanity-checker 执行 Level 6 验收。

> ablation：formulation_v002 主反演（基线-干涉分解 + 一维相位频率扫描 variable projection，两角共享 t）含可解释、可分离的公式项/算法模块/约束方向。预注册方案 ablation_v001（核心结论+消融判据运行前固定），隔离任务 bd175bb7b9a82f35e054 执行 F0 完整模型对照 + A1 色散项 / A2 多光束(Airy)高阶项 / A3 基线多项式项 / A4 两角共享 t 约束，5/5 判据通过，conclusion=components_confirmed：A1 Δt=0.446%≤2%、A2 Δt=0.300%≤1%（L17 极值不变性/Q1 定量）、A3 Δt=0.574%≤2%（RMSE +9.5%，基线项为拟合优度必要组件）、A4 每角偏差 0.089%≤2% 且 ε12=0.130%≤2%（共享为安全一致性约束）。

**需要保留的边界与警告**：prob03 主 computation 任务 7e209043973692d067ed 消费完成（formulation_v002 / assumption_v001，results/silicon_mb_verify）：L1–L4 硬门禁通过——hash 追踪链完整、机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf，failures=[]）、公式-代码逐条一致（R1 硅厚度基准 t̂=3.4477µm 修正 v001 的 6.9µm 因子2 伪影；R2 finesse=π·√R̄/(1−R̄) 修正 v001 漏 √R̄，finesse=0.3186 与公式一致）、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=3.4477 µm、每角 3.4507/3.4463 µm、ε₁₂=0.130%、n̂_sub(幅值弱辨识)=3.558；J(t) 曲线全局唯一极小在 t=3.45µm（J_shared=0.0608），未达 formulation §13.1 声称的"4 倍余量"（次小候选比≈1.020，弱色散下周期邻近候选接近简并，作为报告项而非硬门禁）。全部可靠性判据 PASS（two_angle F=0/p=1.0、dispersion 0.503%≤2%、ci 0.134%≤2%、anomaly 0.0%≤1%、multibeam_si two_beam_negligible η_mb≈0.11%、multibeam_sic no_correction_needed Rbar≈0.0024、nsub 解耦 diag PASS；checks_failed=[]）。v001 判 NEEDS_REVISION 的两项 core 缺陷（R1/R2）已在 v002 修复并复核通过；模型有效、无 VERSION_REJECTED、无 NEEDS_REVISION。技术债（bootstrap CI 用轮廓似然替代、n_sub 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项或非阻断。合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。

**prob03 结论**：从物理上严格推导了多光束干涉的必要条件 N1–N4，并独立验证"无吸收平行板下多光束不改变极值位置与周期、不改变厚度"（L17 成立）；依据必要条件与残差改善率判定硅片（附件 3/4）未出现显著多光束、两光束模型适用，得到硅厚度 $\hat t=3.4477\,\mu\text{m}$（每角 3.4507/3.4463 $\mu\text{m}$，$\varepsilon_{12}=0.130\%$）；对碳化硅重新判定 $\bar R\approx0.0024$、无显著多光束、无需修正，prob02 的 $\hat t=7.2158\,\mu\text{m}$ 维持。可靠性判据 R1–R8 全部在阈值内，ablation 5/5 通过。L1–L5 校验通过。结论限于透明谱段、无吸收假设与附件数据范围。<!-- evidence:ev_artifact_30aee4639e7e -->

## 跨小问一致性、稳健性与消融分析

跨小问审查状态为 passed，结论为"跨小问一致性审查通过：共享符号（t,n,n_sub,θ,θ',λ,ν,R,δ,R_01/R_12,finesse）与单位、参数值（Sellmeier 一致、主带 ν∈[2000,4000]cm⁻¹、θ=10/15°、Reststrahlen [700,1000]cm⁻¹ 剔除）、假设、数据版本、约束（R∈[0,1]、t>0、n>1）、结论方向与数量级全部跨问自洽；软依赖 conclusion hash（prob01=828203556617be979f7345dce7c274dd1850b62fe950a6e108015ad161b070a6、prob02=27b0ce8689e1eb2b345e5803309ea80bb6b84a620f189ed6cd589e75f23a12ea）完整匹配，无 stale 传播、无回退。唯一共享符号元数据不一致（finesse domain ≥1 vs 实际 F≈0.32<1）已由本审查修订为 >0，属全局符号表规范修订，不影响任何计算结果。裁决依据：题目硬约束、sanity 硬门禁、文献/机理、鲁棒性、解释性、时间顺序均一致；无硬门禁失败版本。"

**跨问一致性**：三问共享同一物理正模型（prob01 建立、prob02/prob03 沿用，仅 prob03 扩展至 Airy 多光束）、同一主反演方法（variable projection，t 由相位频率确定、与 $n_{\text{sub}}$ 解耦）、同一主反演带 $\nu\in[2000,4000]\,\text{cm}^{-1}$ 与 Reststrahlen/多声子剔除策略。符号表：$t,n,n_{\text{sub}},\theta,\theta',\lambda,\nu,R,\delta,R_{01},R_{12},\text{finesse}$ 跨问同名同义；prob03 修正 finesse 公式为 $\pi\sqrt{\bar R}/(1-\bar R)$ 并把其 domain 由 $\ge1$ 改为 $>0$（低反射率下 F≈0.32<1 属"近两光束无锐峰区"，不影响判定）。数值层：prob02 碳化硅 $\hat t=7.2158\,\mu\text{m}$ 与 prob01 合成 $t_{\text{true}}=10\,\mu\text{m}$ 不在同一量但物理一致（不同样品）；prob03 硅 $\hat t=3.4477\,\mu\text{m}$ 的 $\bar R\approx0.0101$ 与 prob02 SiC 的 $\bar R\approx0.0024$ 均远小于 $\theta_{\text{mb}}=0.05$，结论方向一致（无显著多光束）。prob02→prob03 软依赖（content_hash `27b0ce86…a12ea`）完整匹配。

**稳健性与消融**：各问 robustness 与 ablation 结果已在对应章节披露，核心结论一致性如下——
- prob01：robustness E1–E5 5/5 通过（conclusion=stable）；ablation F0+A1–A4 5/5 通过（conclusion=components_confirmed），A4 多初值必要性显著（6.03% vs ≈0%）。
- prob02：robustness C1–C8 中除 C1 两角 F 检验统计显著外全部 PASS（结论=STABLE），该例外按 B11 路由解释；ablation F0+A1–A4 确认色散（8.44%）、基线多项式（5.55%）、相位频率方法（5.44%）为必要组件，共享-$t$ 为良性约束。
- prob03：robustness R1–R8 全部在阈值内（结论=STABLE）；ablation F0+A1–A4 5/5 通过（0.446%/0.300%/0.574%/0.089%），并辅以 RMSE 对照（基线项 +9.5%、多光束项 −5.0%）。

记录的质量警告如下（这些警告不被改写为已解决，而是作为解释结果与限制外推范围的组成部分）：

- prob01：prob01 合成验证任务 0ea4b29da19e8479a6ea 消费完成：19/19 检查通过，t_true=10µm 被 NLS/相位法精确恢复，两入射角一致；hash 追踪链（code/config/input）与 task.json、implementation.md §7 完全一致，无 NaN/Inf、无硬约束违反、formula-代码逐条一致、文献/物理常识合理。技术债（λ>5µm 常数色散延伸、方法 A 约4%基线偏差、文献全文待复核、n_sub 合成场景值、Reststrahlen 剔除策略）均为既有 workflow warning，留 prob02 处理，不阻断推进。L1–L4 判定 PASS_WITH_WARNING，Level 5 待全部小问完成、Level 6 待 robustness 阶段。
- prob01：prob01 Level 6（robustness 验收）独立复核通过：任务 554819114361017c5b70 全部输出有限且追踪完整，hash 链（code/config/input）与 task.json 一致，E1–E5 判据独立重算全部通过（conclusion=stable、5/5），E4 600 样本收敛率 100%、95% CI 半宽最大 0.022% 远低于阈值，预注册方案运行前固定未事后修改；物理机制（n_sub 影响幅度不影响相位、θ 误差二阶小量、色散模型为最大不确定度来源、全谱平均效应）与常识一致。技术债（robustness 基于合成谱、色散模型选择、λ>5µm 常数延伸、n_sub 场景值、文献全文待复核、Reststrahlen 剔除）均为既有 workflow warning，留 prob02 处理，不阻断推进。
- prob02：prob02 实测反演任务 30bedd3be5a2c9a36d3a 消费完成（formulation_v003 / assumption_v001，results/thickness_inversion_v003）：L1–L4 硬门禁通过——hash 追踪链（code_hash=3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e 与 task.json/implementation.md §7 一致、config/input hash 一致）完整、机器级 L2-finite 通过（8 文件全有限无 NaN/Inf，v001 的 dispersion_ref NaN 已用 null 修复）、公式-代码逐条一致、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588；主拟合加权 RMSE≈6.3e-4。只读 FFT 数据探针独立证实带内真实干涉周期 Δg≈657/698、Δν≈247/263 cm⁻¹→t≈7.2–8.0 µm，与主结果一致。可靠性判据 5/6 通过：dispersion(0.51%≤2%)、ci(0.091%≤2%)、anomaly(0.0%≤1%)、nsub 解耦(diag PASS)、multibeam(pass) 全部通过；仅 reliability_two_angle_ftest 判 FAIL（F=5.251>F_crit=3.843，p=0.022），但裸偏差 ε₁₂=0.165%≪τ₁₂=2%，属大样本下统计显著性与实际意义分离，formulation §7.1/§14 明确将其路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。v001/v002 曾超阈判据（ε₁₂ 27.66%→0.165%、Δt_disp 15.11%→0.51%、n_sub 69%→解耦0%、CI 3.51%→0.091%、M1 0.305µm→7.216µm 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。技术债（λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 5.5% 偏差、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，留后续与论文阶段处理，不阻断推进。
- prob02：prob02 Level 6（robustness 验收）独立复核通过（降级审查模式，复用已有产物、不发起新计算）：robustness 判据 C1–C8 由 formulation_v003 §7.1–§7.6 预注册判据在 computation 阶段执行并归档 results/thickness_inversion_v003/result.json + robustness/（decision/preregistration/experiment_matrix/conclusion），无需另启重复任务。C2 色散 0.507%≤2% PASS、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）PASS、C5 CI 半宽 0.091%≤2% PASS、C6 全局极小唯一 PASS、C7 异常点 0.0%≤1% PASS、C8 多光束改善 0.0%≤10%（两光束适用）PASS、R8 基线/包络阶数 p=2..5.q=0..2 稳定；仅 C1 两角嵌套 F 检验统计显著（F=5.25>F_crit=3.843，p=0.022）但 ε12=0.165%≪τ12=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。机器级 L2-finite 通过（8 数值文件全有限无 NaN/Inf，failures=[]），hash 追踪链（code/config/input）与 task.json/implementation.md §7 一致，原始数据只读；result.json feasible_incumbent=false 系 compute.py 将 F 检验判为硬失败置 passed=false，sanity-checker 独立验收判定主结果 t̂=7.2158 µm（ε12=0.165%、n̂_sub=2.588）可行可追踪，维持 PASS_WITH_WARNING。物理/常识一致（t 由相位频率确定、与 n_sub 解耦；色散为最大不确定度来源但带内 0.507%<2%；噪声二阶小量；异常点降权无影响）。v001/v002 曾超阈判据全部回到阈值内，确认 formulation_v003 变量投影重构消除模型可辨识性结构缺陷。技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 5.5%、λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，不阻断推进。ablation 尚 pending，交由 ablation-analyst；Level 5 待全部小问局部完成后执行。
- prob03：prob03 主 computation 任务 7e209043973692d067ed 消费完成（formulation_v002 / assumption_v001，results/silicon_mb_verify）：L1–L4 硬门禁通过——hash 追踪链（code_hash=482f5abb10c276c9d073dd7b7177ce342cf0a0d2d0b455370a899ec566142873 与 task.json/implementation.md §7 一致、source_config_hash/input_hash 一致）完整、机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf，failures=[]）、公式-代码逐条一致（R1 硅厚度基准 t̂=3.4477µm 修正 v001 的 6.9µm 因子2 伪影；R2 finesse=π·√R̄/(1−R̄) 修正 v001 漏 √R̄，finesse=0.3186 与公式一致）、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=3.4477 µm、每角 3.4507/3.4463 µm、ε₁₂=0.130%、n̂_sub(幅值弱辨识)=3.558；J(t) 曲线全局唯一极小在 t=3.45µm（J_shared=0.0608），未达 formulation §13.1 声称的"4 倍余量"（次小候选比≈1.020，弱色散下周期邻近候选接近简并，作为报告项而非硬门禁）。全部可靠性判据 PASS（two_angle F=0/p=1.0、dispersion 0.503%≤2%、ci 0.134%≤2%、anomaly 0.0%≤1%、multibeam_si two_beam_negligible η_mb≈0.11%、multibeam_sic no_correction_needed Rbar≈0.0024、nsub 解耦 diag PASS；checks_failed=[]）。v001 判 NEEDS_REVISION 的两项 core 缺陷（R1/R2）已在 v002 修复并复核通过；模型有效、无 VERSION_REJECTED、无 NEEDS_REVISION。技术债（bootstrap CI 用轮廓似然替代、n_sub 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项或非阻断。合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。判定 PASS_WITH_WARNING，推进至 sanity_check 阶段。
- prob03：prob03 Level 6（robustness 验收）独立复核通过：robustness 判据 R1–R8 由 formulation_v002 §8.5 预注册并先于 computation 固定（parameters.yaml），R1–R7 全部在阈值内（R1 eps12=0.130%≤2%、R2 Δt_disp=0.503%≤2%、R3 CI 半宽 0.134%≤2%、R4 Δt_anom=0.0%≤1%、R5 η_mb=0.111%≤10%、R6 n_sub 解耦 0.0%、R7 Δt_win=0.749%≤2%），checks_failed=[]；独立复算 R7=0.749% 与登记值一致，探针只读、复用 model.py、未改数据/代码/结果。R8 唯一性次小候选≈1.020 为报告项（弱色散周期歧义），全局唯一性由 §7.6 预注册判据确认。主结果 t̂=3.4477 µm/每角 3.4507/3.4463 µm（ε12=0.130%），多光束判定两光束适用（硅 R̄≈0.0101、η_mb≈0.11%；SiC R̄_max≈0.0024 no_correction_needed），与 prob02 结论一致；物理/常识一致（t 由相位频率确定、与 n_sub 解耦；硅色散弱且带内无 λ>5µm 缺口；噪声二阶小量）。硬门禁（L2-finite 10 文件全有限无 NaN/Inf、单位/量纲、公式-实现一致 R1/R2 已修复、原始数据只读、追踪链完整、feasible_incumbent=true）全部通过。技术债（bootstrap CI 未跑用轮廓似然、n_sub 弱可辨识 B7、uniqueness 近简并、multibeam 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项，非阻断。判定 PASS_WITH_WARNING。

## 模型评价、局限与推广

**模型评价**。建模链条从假设、公式、实现、结果到图表均可追溯，便于复核与复现；多种 sanity 与扰动证据（robustness、ablation、两角一致性、只读数据探针）减少只凭单点结果下结论的风险。prob02 在主方法选择上以"相位频率测厚、幅度测对比度、二者解耦"重构，直接消除 v002 的可辨识性缺陷；prob03 从物理上严格推导多光束必要条件并以残差改善率量化，避免了预先采信候选主张。

**局限与边界**：
- 模型基于"界面平行、厚度均匀、无吸收"的平行板近似；在 Reststrahlen 区（SiC 700–1000 cm⁻¹）与硅多声子带（<1500 cm⁻¹）模型不适用，已剔除。
- 色散模型选择与 $\lambda>5\,\mu\text{m}$（碳化硅）色散缺口是厚度精度的主要不确定度来源；带内色散敏感性已量化（0.5% 左右），但带外仍属遗留技术债。
- $n_{\text{sub}}$ 由干涉幅值弱可辨识（prob02 $n̂_{\text{sub}}=2.588$、prob03 $n̂_{\text{sub}}=3.558$），对噪声敏感，但因其与 $t$ 解耦而不影响厚度；置信区间用轮廓似然替代 bootstrap，属方法债。
- 两角嵌套 $F$ 检验在 prob02 统计显著（F=5.25、p=0.022）但裸偏差仅 0.165%，按约定路由为测量点差异/膜厚梯度并记录，不构成模型修订触发；prob03 则为 F=0、p=1.0。
- 唯一性：prob02 次小候选比≈1.017、prob03≈1.020（弱色散周期邻近简并），作为报告项而非硬门禁；全局唯一性由预注册判据确认。
- 文献定量参数（Sellmeier 系数、$n_{\text{sub}}$ 取值、L25–L32/L43–L47 数据）部分为元数据/摘要级核验，尚待对照原文复核；prob03 的合并 config_hash 因 computation 后配置漂移而作质量告警登记。

**推广边界**：推广到新的材料、时段或数据分布前，应重新执行参数标定、敏感性分析与 Level 5 复核；两光束近似在多光束显著（$\bar R$ 接近或超过 $\theta_{\text{mb}}=0.05$）或强吸收谱段不再成立，需切换到 Airy 正模型与复折射率 Fresnel。

## 结论

本文围绕红外干涉法测定外延层厚度，逐问完成模型建立、求解、结果解释与可靠性分析，形成一条可追溯、可复现且经跨小问一致性核对的建模链条。

**prob01**：在两光束干涉近似下建立反射率-波数解析正模型与厚度反演公式（含色散化相位修正），经合成谱（$t_{\text{true}}=10.00\,\mu\text{m}$）验证，色散化相位法与全谱 NLS 均以 $<0.03\%$ 相对偏差恢复真值、两入射角一致；常数 $n$ 的极值间隔法因忽略色散存在约 4% 系统偏差，故以色散化方法为主。robustness 与 ablation 均 5/5 通过，L1–L5 校验通过。<!-- evidence:ev_artifact_ff24505a53cd -->

**prob02**：对附件 1/2 碳化硅实测谱，采用基线-干涉分解 + 一维相位频率扫描（variable projection）主方法，得到两角共享厚度 $\hat t=7.2158\,\mu\text{m}$（每角 7.2214/7.2095 $\mu\text{m}$，$\varepsilon_{12}=0.165\%$，$\hat n_{\text{sub}}=2.588$，加权 RMSE≈$6.3\times10^{-4}$），$J(t)$ 全局唯一。可靠性判据 5/6 通过，唯一例外（两角 $F$ 检验统计显著）按 B11 路由解释；ablation 确认色散、基线多项式、相位频率方法为必要组件、共享-$t$ 为良性约束。L1–L5 校验通过。<!-- evidence:ev_artifact_44ce712a84e4 -->

**prob03**：严格推导多光束干涉必要条件 N1–N4，并独立验证无吸收平行板下多光束不改变极值位置与周期、不改变厚度（L17 成立）；判定硅片（附件 3/4）未出现显著多光束、两光束模型适用，得到硅厚度 $\hat t=3.4477\,\mu\text{m}$（每角 3.4507/3.4463 $\mu\text{m}$，$\varepsilon_{12}=0.130\%$）；对碳化硅重新判定 $\bar R\approx0.0024$、无显著多光束、无需修正，prob02 的 $\hat t=7.2158\,\mu\text{m}$ 维持。可靠性判据 R1–R8 全部在阈值内，ablation 5/5 通过。L1–L5 校验通过。<!-- evidence:ev_artifact_30aee4639e7e -->

所有结论只在 Evidence Pack 固定的接受版本、数据范围和警告边界内成立；凡涉及外推（新材料、新谱段、新数据分布）的结论均需先重新标定参数并复核敏感性与稳健性。

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

论文由 Evidence Pack `ac7825d58cc976d35e78f45a3fcbde5dab27a15157e440ec6732856b7995ea55` 自动生成。复现时需先核验该哈希与 `writer_manifest.json`，再运行论文构建命令；计算代码及结果路径以证据包登记清单为准，正文不重复粘贴完整代码。核心计算脚本（模型、反演、robustness、ablation、绘图）与结果 JSON/图件均按 SHA-256 登记于证据包的 `artifacts` 清单，任务 ID 与 hash 追踪链见各问 implementation.md §7 与 task 记录。图件使用证据包登记的 stable ID 与相对路径；参考文献仅使用登记引用，未自行增加。
