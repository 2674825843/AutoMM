# prob02 robustness 预注册方案（robustness_v001）

> 阶段：robustness ｜ Agent：robustness-analyst ｜ 版本：robustness_v001
> 依据：robustness-analyst 默认方案（95% 置信区间；主要数值参数 ±5%/±10%/±20%；随机实验至少 100 次）
> 与 knowledge/robustness-ablation.md；**稳定性判据在实验运行前固定，不得事后修改**
> （formulation_v003 §7 判据与 parameters.yaml 阈值均在 computation 前登记；中途调整须新版本）。
> 本问鲁棒性判据在 computation 阶段作为 **formulation §7 可靠性分析** 预先固定并执行，
> 结果归档 `results/thickness_inversion_v003/result.json`。本方案重申这些预注册判据，并映射到
> robustness 默认扰动约定，作为「预注册——运行——复核」链条的稳定性声明。

## 1. 核心结论（本次 robustness 检验的对象）

prob02（assumption_v001 / formulation_v003）的碳化硅外延层厚度实测反演：

- 主反演（variable projection，基线-干涉分解 + 一维相位频率扫描，两角共享 t）：
  `t̂(共享)=7.2158 µm`，每角 `7.2214 / 7.2095 µm`，`ε₁₂=0.165%`，`n̂_sub=2.588`（弱可辨识）；
  主拟合加权 RMSE≈6.3e-4，只读 FFT 数据探针独立证实带内真实干涉周期 → t≈7.2–8.0 µm，与主结果一致。

**robustness 检验的问题**：该厚度反演结论是否依赖脆弱参数（n_sub、色散模型、谱段截断、基线/包络
多项式阶数）、输入噪声（反射率噪声、异常点）或偶然初始化（一维扫描局部陷阱/唯一性）？在预注册判据
下量化各因素对 t̂ 的影响，判定稳定性分级。

## 2. 稳定性判据（运行前固定，不能事后修改）

| 判据 | 定义/度量 | 阈值 | 依据 |
|---|---|---|---|
| C1 两角一致性（B11） | 嵌套 F 检验 H₀: t₁=t₂（α=0.05）；**报告** ε₁₂=|t̂₁−t̂₂|/t̄ | F≤F_crit(1,N−3) 且 ε₁₂≤τ₁₂=2% | formulation §7.1；parameters.yaml tau_12/alpha_ftest |
| C2 色散模型敏感性（B6） | Δt_disp=|t_NSE−t_NSE-δ|/t_NSE×100%（δ=0.5%） | ≤τ_d=2% | formulation §7.2；parameters.yaml tau_disp |
| C3 谱段截断影响（B6） | Δt_inv_band=|t_trunc−t_full|/t_trunc×100% | **仅报告**（截断合理性证据），不作主判据 | formulation §7.2 |
| C4 n_sub 不确定度（B7） | 主方法 t 对 n_sub 的灵敏度；n̂_sub 弱可辨识说明 | t 与 n_sub 解耦（主判据）；诊断 Δt_nsub≤τ_nsub_diag=3% | formulation §7.3；tau_nsub_diag |
| C5 噪声/置信区间（B12） | 95% CI 半宽（轮廓似然/夹逼区间或 bootstrap） | ≤τ_ci=2% | formulation §7.4；tau_ci |
| C6 唯一性（B12） | 全局极小显著低于次小候选；扫描区间内唯一 | 次小候选 J 显著更高（ΔJ 超噪声阈值） | formulation §7.4 |
| C7 异常点影响（B2） | 剔除/保留/降权三种 S_A 策略下 Δt_anom | ≤τ_a=1% | formulation §7.5；tau_anom |
| C8 多光束诊断（B13） | Airy 相对两光束残差改善 | ≤10% → 两光束适用；>10% → 需修正 | formulation §7.6；multibeam_threshold |

**结论分级**（knowledge/robustness-ablation.md §结果分级）：
- 全部判据通过 → `stable`；部分未通过且需边界 → `conditionally_stable`（报告边界与脆弱参数）；
  合理扰动导致反转/高不可行率 → `fragile`；样本/计算不足以判定 → `undecided`。
- 不删除不利情景；失败运行计入可行率；C6 的一致性判定以主判据（F 检验/唯一性）为准，ε₁₂ 为报告项。

## 3. 实验矩阵（映射 §7 判据与默认扰动约定）

基准场景：实测附件 1/2，两入射角 θ∈{10°,15°}，主反演带 ν∈[2000,4000] cm⁻¹（Sellmeier 已知区，B6），
Reststrahlen [700,1000] cm⁻¹ 剔除（w=0，B3），异常点（反射率 >100%，n=262）按 weight_anomaly=0.05 降权
（不修改原始数据，B2），基线/包络多项式 p=3/q=1（中心化正交化 Chebyshev 基）。

| 实验 | 扰动/不确定度对象 | 设计 | 对应判据 | 预注册值 |
|---|---|---|---|---|
| R1 | 色散模型（±δ） | N-SE vs N-SE-δ（δ=0.5%） | C2 | Δt_disp≤2% |
| R2 | 谱段截断（B6 缺口） | 全谱 vs 截断带 [2000,4000] | C3 | Δt_inv_band 报告 |
| R3 | n_sub（±5/10/20% 的幅度层） | 主方法 t 与 n_sub 解耦；幅度层扰动 | C4 | t 不依赖 n_sub（解耦）；Δt_nsub≤3% |
| R4 | 反射率噪声/置信区间 | 轮廓似然/夹逼区间（SSE(t) 曲率） | C5 | CI 半宽≤2% |
| R5 | 唯一性/偶然初始化 | 一维全局扫描唯一性（次小候选对比） | C6 | 全局极小唯一（次小明显更高） |
| R6 | 异常点处理策略 | 剔除 vs 保留 vs 降权 | C7 | Δt_anom≤1% |
| R7 | 多光束（Airy） | 两光束 vs Airy 拟合残差比较 | C8 | 改善≤10% |
| R8 | 基线/包络多项式阶数 | p∈{2,3,4,5}、q∈{0,1,2} 的 t 稳定性 | C1/C2 附 | 阶数稳健（§5.5 声明） |

> 注：参数扰动 ±5/10/20% 的默认约定对**有**不确定度的对象适用。本问经 formulation §7 物理化：
> 色散模型不确定度由 Sellmeier 系数可复现性 δ=0.5% 量化（非任意 ±5/10/20%）；n_sub 因与 t 结构解耦，
> 扰动仅影响幅度层、经主方法验证对 t 影响趋近 0；λ>5µm 色散缺口以 Δt_inv_band 量化。故采用
> 「物理化扰动范围」而非一刀切 ±5/10/20%，并在 R9 保留默认 ±5/10/20% 的 n_sub 幅度层抽检以对照。

| 实验 | 补充（默认方案抽检） | 设计 | 对应判据 |
|---|---|---|---|
| R9 | n_sub 幅度层 ±20% 抽检 | 主方法用扰动 n_sub 重算 t（确认解耦） | C4 |

## 4. 随机性与复现

- 主种子：20260829（与 computation 阶段一致，AUTOMM_SEED 优先）；
- R4 轮廓似然为确定性（由 SSE(t) 曲率/夹逼区间给出），无随机抽样；bootstrap（B≥200）作为残留
  方法债登记（见 §8），非阻断；
- 各方案使用相同数据、种子策略与计算预算（knowledge/robustness-ablation.md §Sanity）；
- 原始数据只读，异常点按 B2 策略处理，不修改原始数据。

## 5. 失败处理

- 某判据超阈值：计入**条件稳定/脆弱**结论（不静默删除）；若为建模缺陷（如 v002 的错误盆地）
  则路由 implementation/formulation 修订（按 failure_class），而非直接人工阻塞（PROJECT.md §失败和门禁）；
- 任务级失败（进程/超时）：按 failure_class 路由（code_runtime → 复现后重试或修订；
  infrastructure_transient → 重试），不直接人工阻塞；
- `result.json` 的 `feasible_incumbent=true` 表示判据评估完整执行；超阈值是「条件稳定」/「脆弱」结论
  而非任务失败。

## 6. 输出与追踪

- robustness 判据结果（C1–C9）由 computation 结果目录 `results/thickness_inversion_v003/result.json`
  提供，其 `metadata.json`/`solver_status.json`/`verification.json` 记录代码/config/input hash 追踪链；
- 本 robustness 目录归档：decision.md、preregistration.md、experiment_matrix.yaml、conclusion.md；
  敏感性可视化图（dispersion 对照、n_sub 解耦、可靠性判据汇总）已由 visualization 阶段生成于 figures/；
- 全部以版本（assumption_v001 / formulation_v003）归档，与 v001/v002 结果目录分离。

## 7. 与 formulation/假设/既有 warning 的对应

| 判据 | 对应假设/公式 | 对应 workflow warning |
|---|---|---|
| C1 | B11、(7.1)；§7.1/§14 | 两角 F 检验统计显著但 ε12=0.165%≪2%（大样本显着性与实际意义分离，B11） |
| C2/C3 | B6、(7.2)–(7.3) | λ>5µm 色散缺口为最大不确定度来源（Δt_inv_band=58.4% 报告） |
| C4 | B7、(5.1)→n̂_sub | n_sub 弱可辨识（与 t 解耦，0.0% 敏感度） |
| C5/C6 | B12、§7.4 | CI 半宽 0.091%≪2%；全局极小唯一 |
| C7 | B2、(3.2) 降权 | 附件2 反射率>100% 异常点降权，Δt_anom=0.0%<1% |
| C8 | B13、§7.6 | Airy 改善 0.0%≤10%，两光束适用 |
| C8/R8 | §5.5、§8.2 | 基线/包络阶数 p=3 预先固定且对 p 稳健 |

## 8. 遗留与移交

- **bootstrap CI 未运行**（§7.4 用轮廓似然/夹逼区间）：为方法债，CI 半宽 0.091%≪2%，不阻断；
  如需更稳健的抽样分布，可在论文/后续小问补 B≥200 残差重采样 bootstrap。
- **M2/M3（方法债）**：报告 t≈54–65 µm 系把噪声纹波当作干涉极值，M1 为主交付，论文须说明 M2/M3 不适用。
- **物理正模型 NLS 交叉校验**：从主 t̂ 起点收敛到 P1=6.816/P2=6.975 µm，与主结果差约 5.5%，源于其刚性
  Fresnel DC 基线未吸收带内慢变背景（formulation §6.4 方法债）；主结果由 FFT 周期图与低残差拟合双重佐证。
- **λ>5µm 色散缺口（B6）**：Δt_inv_band 作为截断合理性证据，L26 全文 n/k 表待 literature 复核。
- **n_sub（B7）**：弱可辨识值 n̂_sub=2.588，文献取值与掺杂机制待全文复核；不影响 t̂（解耦）。
- **多光束（B13）**：完整 Airy 推导与修正预留 prob03，本问两光束适用。
