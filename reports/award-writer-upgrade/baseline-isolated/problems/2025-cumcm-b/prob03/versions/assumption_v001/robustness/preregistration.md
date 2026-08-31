# prob03 robustness 预注册方案（robustness_v001）

> 阶段：robustness ｜ Agent：robustness-analyst ｜ 版本：robustness_v001
> 依据：robustness-analyst 默认方案（95% 置信区间；主要数值参数 ±5%/±10%/±20%；随机实验至少 100 次）
> 与 knowledge/robustness-ablation.md；**稳定性判据在实验运行前固定，不得事后修改**
> （formulation_v002 §8.5 判据与 parameters.yaml 阈值均在 computation 前登记；中途调整须新版本）。
> 本问鲁棒性判据在 computation 阶段作为 **formulation §8.5 可靠性分析** 预先固定并执行，
> 结果归档 `results/silicon_mb_verify/result.json`；本方案重申这些预注册判据并映射到 robustness
> 默认扰动约定，作为「预注册——运行——复核」链条的稳定性声明。

## 1. 核心结论（本次 robustness 检验的对象）

prob03（assumption_v001 / formulation_v002）的硅片（附件3/4）外延层厚度反演：

- 主反演（variable projection，基线-干涉分解 + 一维相位频率扫描，两角共享 t）：
  `t̂(共享)=3.4477 µm`，每角 `3.4507 / 3.4463 µm`，`ε₁₂=0.130%`，`n̂_sub=3.558`（幅值弱可辨识）；
  主拟合加权 RMSE≈2.57e-3。
- 多光束判定：硅 `R̄=√(R₀₁R₁₂)≈0.0101`≤θ_mb=0.05、`F≈0.319`、`η_mb≈0.11%`≪τ_mb=10% → **两光束适用**；
  SiC `R̄≈0.0024` → **无需修正**，prob02 `t̂=7.2158 µm` 维持（C17）。
- Q1（多光束必要条件）：N1–N4 全部满足（界面反射率乘积、相干长度、界面平行度、吸收限制），
  L17「无吸收时 Airy 极值位置不变性」独立推导验证成立（§4.5）。

**robustness 检验的问题**：该厚度反演结论是否依赖脆弱参数（n_sub、色散模型、谱段窗口、基线/包络阶数）、
输入噪声（反射率噪声、异常点）或偶然初始化（一维扫描局部陷阱/唯一性）？在预注册判据下量化各因素对 t̂
的影响，判定稳定性分级。

## 2. 稳定性判据（运行前固定，不能事后修改）

| 判据 | 定义/度量 | 阈值 | 依据 |
|---|---|---|---|
| R1 两角一致性（B11） | 嵌套 F 检验 H₀: t₁=t₂（α=0.05）；**报告** ε₁₂=|t̂₁−t̂₂|/t̄ | F≤F_crit(1,N−3) 且 ε₁₂≤τ₁₂=2% | formulation §8.5；parameters.yaml tau_12/alpha_ftest |
| R2 色散模型敏感性（B6） | Δt_disp=|t_NSE−t_NSE-δ|/t_NSE×100%（δ=0.5%） | ≤τ_d=2% | formulation §8.5；tau_disp |
| R3 噪声/置信区间 | 95% CI 半宽（轮廓似然/夹逼区间） | ≤τ_ci=2% | formulation §8.5；tau_ci |
| R4 异常点影响（B2） | 剔除/保留/降权三种策略下 Δt_anom | ≤τ_a=1% | formulation §8.5；tau_anom |
| R5 多光束（B13） | Airy 相对两光束残差改善率 η_mb | ≤τ_mb=10% → 两光束适用 | formulation §8.5；tau_mb |
| R6 n_sub 解耦（B7） | 主方法 t 对 n_sub 灵敏度 | t 与 n_sub 解耦；诊断 ≤τ_nsub_diag=3% | formulation §8.5；tau_nsub_diag |
| R7 硅谱段窗口 | [1600,4000]/[1800,4000]/[2200,4000] 的 t 稳定性 | t 对窗口稳健（同 R2 量级） | formulation §8.5；nu_inv_si 注 |
| R8 唯一性 | J(t) 全局极小唯一 + 次小候选比值 | 次小候选距 1 越远越好（报告项） | formulation §8.5 |

**结论分级**（knowledge/robustness-ablation.md §结果分级）：
- 全部判据通过 → `stable`；部分未通过且需边界 → `conditionally_stable`（报告边界与脆弱参数）；
  合理扰动导致反转/高不可行率 → `fragile`；样本/计算不足以判定 → `undecided`。
- 不删除不利情景；失败运行计入可行率；R8 唯一性以预注册判据（全局极小唯一）确认，次小比值作为报告项。

## 3. 实验矩阵（映射 §8.5 判据与默认扰动约定）

基准场景：硅片附件 3/4，两入射角 θ∈{10°,15°}，主反演带 ν∈[2000,4000] cm⁻¹（透明窗，C8），
多声子带 [400,1600] cm⁻¹ 剔除（w=0，B3/C8；主反演带截断至 ν≥2000），基线/包络多项式 p=3/q=1
（中心化正交化 Chebyshev 基）。硅片无 R%>100 异常点；异常点降权策略沿用作鲁棒（B2，不修改原始数据）。

| 实验 | 扰动/不确定度对象 | 设计 | 对应判据 | 预注册值 |
|---|---|---|---|---|
| R1 | 两角一致性（B11） | 嵌套 F 检验 + 裸偏差 ε₁₂ | R1 | ε₁₂≤2% |
| R2 | 色散模型（±δ） | N-SE vs N-SE-δ（δ=0.5%） | R2 | Δt_disp≤2% |
| R3 | 噪声/置信区间 | 轮廓似然/夹逼区间（J(t) 曲率） | R3 | CI 半宽≤2% |
| R4 | 异常点处理策略 | 剔除 vs 保留 vs 降权 | R4 | Δt_anom≤1% |
| R5 | 多光束（Airy） | 两光束 vs Airy 残差改善率 | R5 | η_mb≤10% |
| R6 | n_sub（±5/10/20% 幅度层） | 主方法 t 与 n_sub 解耦；幅度层扰动 | R6 | t 不依赖 n_sub（解耦）；Δt_nsub≤3% |
| R7 | 谱段窗口 | [2000,4000]（基准）vs [1600/1800/2200,4000] | R7 | t 对窗口稳健（同 R2 量级≤2%） |
| R8 | 唯一性/偶然初始化 | 一维全局扫描唯一性（次小候选对比） | R8 | 全局极小唯一（次小远离 1；报告项） |

> 注：参数扰动 ±5/10/20% 的默认约定对**有**不确定度的对象适用。本问经 formulation §8.5 物理化：
> 色散不确定度由 Sellmeier 系数可复现性 δ=0.5% 量化；n_sub 因与 t 结构解耦（t 由相位频率确定），
> 扰动仅影响幅度层、经主方法验证对 t 影响趋近 0；多光束显著度由 R̄ 与 η_mb 物理量控制。
> 故采用「物理化扰动范围」而非一刀切 ±5/10/20%，并在 R6 保留 n_sub 幅度层扰动以对照（延续 prob02 范式）。

## 4. 随机性与复现

- 主种子：20260830（与 computation 阶段一致，AUTOMM_SEED 优先）；
- R3 轮廓似然为确定性（由 SSE(t) 曲率/夹逼区间给出），无随机抽样；bootstrap（B≥200）作为残留
  方法债登记（见 §8），非阻断；
- R7 只读探针确定性（固定扫描区间/步长/模型，复用 model.py），无随机成分；
- 各方案使用相同数据、种子策略与计算预算（knowledge/robustness-ablation.md §Sanity）；
- 原始数据只读，异常点按 B2 策略处理，不修改原始数据。

## 5. 失败处理

- 某判据超阈值：计入**条件稳定/脆弱**结论（不静默删除）；若为建模缺陷则路由 implementation/formulation
  修订（按 failure_class），而非直接人工阻塞（PROJECT.md §失败和门禁）；
- 任务级失败（进程/超时）：按 failure_class 路由（code_runtime → 复现后重试或修订；
  infrastructure_transient → 重试），不直接人工阻塞；
- `result.json` 的 `feasible_incumbent=true` 表示判据评估完整执行；超阈值是「条件稳定」/「脆弱」结论
  而非任务失败。

## 6. 输出与追踪

- robustness 判据结果（R1–R6、R8）由 computation 结果目录 `results/silicon_mb_verify/result.json` 提供，
  其 `metadata.json`/`solver_status.json`/`verification.json` 记录代码/config/input hash 追踪链；
- R7 由只读探针补登（`robustness/r7_window_sensitivity.json`），代码 `../code/robustness_probe.py`，复用的
  model.py/compute.py hash 追踪链（task `482f5abb10…`）保持不变；
- 本 robustness 目录归档：decision.md、preregistration.md、experiment_matrix.yaml、conclusion.md、
  r7_window_sensitivity.json；敏感性可视化已由 visualization 阶段生成（reliability_summary、response_surface、
  variable_projection_jcurve、mb_conditions 等，见 figures.yaml）；
- 全部以版本（assumption_v001 / formulation_v002）归档，与 v001 阶段结果目录分离。

## 7. 与 formulation/假设/既有 warning 的对应

| 判据 | 对应假设/公式 | 对应 workflow warning |
|---|---|---|
| R1 | B11、(3.7)/(3.8)、(4.5)；§8.5 | 两角 ε₁₂=0.130%≪τ₁₂=2%，F=0/p=1.0 接受共享 t（B11） |
| R2 | B6、(6.1)；§8.5 | 硅色散弱（Δn/n≈0.51%，Δt_disp≈0.503%≤2%）；无 λ>5µm 缺口 |
| R3 | B12、§8.5 | CI 半宽 0.134%≪2%（轮廓似然替代 bootstrap，方法债） |
| R4 | B2、(5.2) 降权 | 硅片无 R%>100 异常；异常点降权 w=0.05，Δt_anom=0.0%<1% |
| R5 | B13、§8.2 | η_mb≈0.11%≪10%，两光束适用（Airy 仅诊断，完整推导 prob03 §4.5） |
| R6 | B7、§7.4 | n_sub 弱可辨识（n̂_sub≈3.558），t 与 n_sub 解耦 |
| R7 | C8、§5.2 | 谱段窗口敏感性（[1600/1800/2200,4000]）Δt_win=0.749%<2%（本阶段只读探针补登） |
| R8 | §7.6 | uniqueness 次小候选比值≈1.020（弱色散周期歧义，报告项而非硬门禁） |

## 8. 遗留与移交

- **bootstrap CI 未运行**（§8.5 R3 用轮廓似然/夹逼区间）：为方法债，CI 半宽 0.134%≪2%，不阻断；
  如需更稳健的抽样分布，可在论文/后续小问补 B≥200 残差重采样 bootstrap。
- **n_sub（B7）**：n̂_sub≈3.558 为幅值弱可辨识值（范围 3.5–3.7），与 t 解耦；文献取值与掺杂机制
  （L12/L13 硅、L45）待全文复核，必要时回退文献取值并记录 t 对 n_sub 灵敏度（预期趋近 0）。
- **唯一性（R8）**：次小候选比值≈1.020 接近 1（弱色散下周期邻近候选接近简并）；全局唯一性由
  §7.6 预注册判据（全局极小唯一 + 嵌套 F 检验）确认，该比值作为报告项而非硬门禁。
- **多光束（B13）**：本问两光束适用（硅 R̄≈0.0101、SiC R̄≈0.0024），无需 Airy 修正；
  若后续判定 η_mb>τ_mb 则启用 §8.4 修正并记录 t 位移（预期≈0，验证 §4.5）。
- **multibeam_improvement 基线差异**：η_mb 以物理两光束正模型（Fresnel 刚性 DC 基线，θ10 RMSE≈0.0294）
  为基准，与主方法 variable projection（低阶多项式吸收基线，RMSE≈0.0026）基线不同，论文须说明。
- **L43–L47、硅 Sellmeier（L12/L13）**：多为元数据/摘要级核验，定量参数需论文/文献阶段对照原文复核。
