# prob02 文献研究（SiC 外延层厚度确定算法与可靠性分析）

> 本文件是 prob02（根据 prob01 模型设计厚度确定算法，对附件 1/2 实测光谱给出计算结果并分析可靠性）
> 的文献证据综述。完整结构化记录见 `literature_pool.yaml`（本问文献池）与
> `problems/2025-cumcm-b/citations.yaml`（题目级引用登记）。
> 检索核验时间：2026-08-29（UTC）；执行 Agent：literature-researcher。
> 说明：prob01 已建立两光束干涉测厚模型（F1–F5，L01–L24，见 prob01/share/literature.md）。
> 本问在 prob01 基础上，聚焦 prob02 特有的三个未决点：① SiC 折射率色散在 λ > 5 µm
> （ν < 2000 cm⁻¹）的取值与全谱段光学常数；② 衬底/外延层折射率差（n_sub 相关，受掺杂/
> 自由载流子影响）；③ 厚度反演算法（极值定位、周期估计、全谱拟合）与可靠性量化，以及
> prob02 要求的"多光束干涉对 SiC 厚度的影响与修正"。

## 1. 检索概况

- 检索对象：4H/6H/3C-SiC 中红外折射率与光学常数（含 reststrahlen 区、λ>5 µm）、
  掺杂/自由载流子对 SiC 红外折射率的影响、FTIR 反射光谱测外延层厚度的算法与标准化、
  多光束干涉修正。
- 检索词族（机理/公式/算法/应用）：
  - `4H-SiC / 6H-SiC optical constants infrared ellipsometry n k`
  - `SiC dispersion λ > 5 µm mid-infrared / Sellmeier`（色散延伸）
  - `SiC reststrahlen band phonon dielectric function infrared`
  - `doped SiC infrared reflectance free carrier / phonon-plasmon / Drude`（n_sub 机制）
  - `SiC epitaxial layer thickness FTIR reflectance algorithm / peak-valley / fitting`
  - `multi-beam interference correction SiC epitaxial thickness`（prob02 修正 + prob03 预留）
- 核验途径：Crossref API（18 条 DOI 直接核验，含作者/年份/卷期页），辅以出版方页与
  机构库（Surface Science Spectra、SPIE、IEEE、MDPI、Elsevier、MSF）。
- 文献池统计：本问新增 18 条（L25–L42）；A 级 9 条、C 级 9 条、D 级 0 条；
  已绑定（used）8 条、候选（new）10 条、拒绝（rejected）0 条。
- dry 判定：**false**（18 < 25 条上限，单轮未达 30 分钟，且发现新假设族 G1–G4，未进入 dry）。

## 2. 假设族与证据

### G1 SiC 折射率色散 / 全谱段光学常数（prob02 关键，解决 λ > 5 µm 缺口）

prob01 指出 [L09] 的 4H-SiC Sellmeier 仅覆盖 λ ≤ 5 µm，λ > 5 µm（ν < 2000 cm⁻¹）色散数据
来源有限。本问检索确认存在覆盖题目全谱段（2.5–25 µm）的公开光学常数来源，可支撑色散模型选择
与数据反演初值：

- Mainali et al. (2024, Surface Science Spectra 31) [L26] 用椭偏测量给出 **4H-SiC 与 6H-SiC
  在 0.05–8.5 eV（约 0.146–24.8 µm）范围的 n/k 光学常数**，正好覆盖题目 2.5–25 µm（含 λ > 5 µm
  与 reststrahlen 区）。这是本问色散延伸的最直接来源。
- Lindquist et al. (2004, Thin Solid Films 455-456) [L27] 给出 3C/4H/6H-SiC 从红外到真空紫外
  的光学常数（椭偏测量），为不同多型体提供跨谱段 n/k；其 2003 年 Materials Science Forum 论文
  [L28] 给出 3C/4H/6H-SiC 的红外光学性质（偏红外谱段）。两个来源相互印证。
- Tong et al. (2018, Physica B 537) [L29] 给出 3C/4H/6H-SiC 的温度依赖红外光学性质，
  可量化温度不确定度对 n(λ) 的影响（prob02 可靠性分析小项）。
- Guo et al. (2021, Optical Materials Express 11) [L42] 给出 4H/6H-SiC 在该谱段的光学性质
  （主要为非线性光学性质，作同谱段参考与候选，不用于关键公式）。

**与本题的差异**：[L26]/[L27]/[L28] 为椭偏测量或薄膜/多型体数据，[L29] 为温度依赖数据，
与真实外延层/衬底的体单晶参数存在差异；且不同来源的 n(λ) 在 reststrahlen 区变化剧烈。
因此这些来源用于**色散模型选择、谱段适用性判定与数据反演初值**，最终本样品 n(λ) 仍需由
prob02 分谱段数据反演确定（project_assumption）。

### G2 掺杂/自由载流子对衬底与外延层折射率的影响（支撑 n_sub）

题面要求外延层与衬底因掺杂载流子浓度不同而有不同折射率；prob01 已给出机制性来源
（[L14]/[L15]/[L16]），本问补充与 SiC 外延层/衬底折射率直接相关的谱学证据：

- Sunkari et al. (2005, Journal of Electronic Materials 34) [L30] 用 FTIR 反射研究了 SiC 外延层
  中 **LO 声子-等离子体耦合模**，将掺杂（自由载流子）与反射光谱直接关联——这是衬底（重掺）
  与外延层（轻掺）折射率差异的直接谱学证据。
- Mazzola et al. (2005, Materials Science Forum 483-485) [L31] 用 FTIR 反射光谱提高外延薄膜
  掺杂浓度的分辨能力，进一步支持"FTIR 反射谱可反演掺杂/自由载流子 → 折射率"的链路。

**与本题的差异**：这些来源给出掺杂→反射光谱的机制与方向，但**没有**给出本样品外延层/衬底的
具体掺杂浓度-折射率定量曲线；n_sub 及外延层折射率的取值仍属 project_assumption，需在 prob02
由文献取值（如 [L26] 的 n 数据）+ 数据反演确定，并纳入可靠性分析（灵敏传播）。

### G3 厚度反演算法族（极值定位、周期估计、全谱拟合、色散补偿）

prob01 给出方法级候选（[L17] 峰谷间隔初值 + 非线性最小二乘；[L23] 包络/条纹间距反演）。
本问补充更贴近"光谱信号处理 + 全谱拟合 + 色散补偿"的算法来源：

- Liu et al. (2026, Sensors 26(10)) [L25] 提出"色散补偿 + 多光束干涉修正"的 SiC 外延层厚度
  测量算法，直接覆盖 prob02 的色散与多光束修正需求（A 级期刊，元数据经 Crossref 核验）。
- Zhou et al. (1993, Journal of Applied Physics 73) [L32] 给出外延硅薄膜厚度测量的
  红外发射/反射 FTIR 基础（测量原理、谱图解释），是 FTIR 测厚的方法级/背景来源。
- 会议论文候选（C 级，正文未核验，仅登记为方法对照/检索线索）：Wang & Liang (2025, MAEIE)
  [L33]（SiC/Si 多光束建模测厚）、Wu et al. (2026, SPIE CIDT) [L34]（双光束→多光束建模）、
  Yang (2026, SPIE CTIEEM) [L35]（多光束 SiC 测厚）、Zhang (2026, IEEE ICPEGE) [L36]
  （红外干涉光谱鲁棒信号处理测厚）、Bao et al. (2026, SPIE ICOMOD) [L37]（无损伤测厚算法）、
  Deng & Xing (2026, IEEE CICSE) [L38]（光谱数值计算 + 多光束修正）、Leng et al. (2026, SPIE BDCIA)
  [L39]（干涉光谱测厚算法）、Gao & Luo (2026, World J Eng Res) [L40]（双光束→多光束渐进建模）、
  Liu (2026, ICACEIIP) [L41]（双光束理论定量反演与实验验证）。

**用于本问**：L25/L32 为 A 级、可用于确认"极值定位—周期/FFT 估计—全谱非线性拟合—色散补偿"
的算法主干；L33–L41 为 C 级会议论文，作为方法族候选与对照，不单独支撑关键公式。

### G4 多光束干涉对测厚精度的影响与修正（prob02 SiC 部分 + prob03 预留）

- Liu et al. (2026, Sensors) [L25] 的"色散补偿 + 多光束干涉修正"直接对口 prob02
  "若多光束也出现在 SiC，请设法消除其影响"；Wang & Liang [L33]、Wu et al. [L34]、Yang [L35]、
  Deng & Xing [L38]、Gao & Luo [L40] 均涉及双光束→多光束的建模与修正。
- **保留**：prob01 已登记 [L17] 提出"多光束仅改变峰形与对比度、不改变极值位置"，该结论为
  候选主张，prob02/prob03 需独立推导验证后方可采用；本问不把该候选结论直接当作结果。

## 3. 陈述类别划分（本问）

| 陈述 | 类别 | 说明 |
|---|---|---|
| 4H/6H-SiC 在 0.05–8.5 eV（含 2.5–25 µm）有公开 n/k 光学常数 | literature_fact | [L26]（Crossref 核验；正文未逐点核验） |
| SiC 不同多型体（3C/4H/6H）跨谱段光学性质可由椭偏测量得到 | literature_fact | [L27][L28] |
| SiC 红外光学性质随温度变化（有温度依赖数据） | literature_fact | [L29] |
| 掺杂（自由载流子）改变 SiC 红外反射谱（声子-等离子体耦合） | literature_fact | [L30][L31]，机制与方向层面 |
| 色散补偿 + 多光束修正的 SiC 外延层厚度测量算法存在 | literature_fact | [L25]（A 级，正文未逐点核验） |
| 本样品外延层/衬底折射率的定量 n(λ) 与掺杂浓度关系 | project_assumption | 由 prob02 文献取值 + 数据反演确定并量化灵敏度 |
| λ > 5 µm 色散模型的最终形式与谱段截断策略 | project_assumption | 采用 [L26]-[L29] 数据初值 + prob02 分谱段反演 |
| 本样品厚度 t 的数值结果 | agent_inference | prob02 由数据反演 |
| 极值定位阈值、拟合谱段、剔除策略等 | team_decision | 假设/公式阶段选择并记录理由 |
| 多光束不改变极值位置 | literature_fact（候选） | [L17] 主张，prob02/prob03 独立验证前不采信 |

## 4. 与本题的差异与风险点

1. **λ > 5 µm 色散缺口可部分闭合但需验证**：[L26] 覆盖 0.05–8.5 eV（约含 λ>5 µm），
   但为椭偏测量且与体单晶存在差异；[L27]/[L28] 为多型体/薄膜数据。需在假设阶段
   **分谱段**采用并做数据反演，量化模型选择对厚度的影响（延续 prob01 E3 结论：
   色散模型是厚度反演最大不确定度来源）。
2. **Reststrahlen 区（约 700–1000 cm⁻¹）**：[L26]/[L28]/[L29] 给出该区强色散/吸收行为；
   prob02 预处理需剔除或降权并记录策略（延续 prob01 A7 边界）。
3. **n_sub/掺杂定量关系缺失**：机制明确（[L30][L31]），数值不定，需 prob02 数据反演；
   掺杂浓度→折射率的定量曲线文献未给出，须作 project_assumption 并灵敏分析。
4. **算法来源多为 C 级会议论文**：L33–L41 正文未核验，仅作方法对照；关键算法主干以
   [L25]/[L32]（A 级）与 prob01 [L17]/[L23] 支撑，并在 implementation 阶段对照原文复核。
5. **全文核验程度**：本问新增来源以 Crossref 元数据核验为主，正文多为摘要级；
   具体公式与数值需在假设/formulation 阶段对照原文（Sensors [L25]、Surface Science Spectra
   [L26] 的 n/k 数据表）复核后才可用于定量主张。

## 5. 使用状态汇总

- used（已绑定，8 条）：L25–L32（G1/G2/G3 关键来源：色散、n_sub 机制、算法主干、FTIR 基础）。
- new（候选，10 条）：L33–L41（多光束/算法会议论文、方法候选，正文未核验），L42（大谱段
  光学性质候选，非关键）。
- rejected（0 条）：本轮无来源被拒绝（候选来源均与题目相关，仅使用强度不同）。

## 6. dry 判定与下一步建议

- 文献池未 dry（本问新增 18 条，产出 G1–G4 新假设族）。
- 下一步建议：
  1. 假设阶段优先落实 **G1**（λ>5 µm 色散模型：以 [L26]/[L27]/[L28]/[L29] 为初值进行
     分谱段选择与数据反演，延续 prob01 E3 的色散化反演方向）与 **G2**（n_sub 与掺杂关系）；
  2. 实现阶段采用 **G3** 算法主干（极值定位 + 周期估计 + 全谱非线性拟合 + 色散补偿，
     以 [L25]/[L32] 与 prob01 [L17]/[L23] 为参考），并对 C 级会议论文（L33–L41）做方法对照；
  3. **G4** 多光束修正按 prob02 要求落实，[L17]"多光束不改变极值位置"结论须独立推导验证；
  4. 若 formulation 需要更精确 n(λ) 数值，从 [L26] 的 n/k 数据表与 [L27]/[L28][L29] 原文取数，
     并登记数据来源与换算方式；（对 prob03，本问 G4 与 [L25]-[L41] 中 Si/SiC 多光束来源可复用）。
