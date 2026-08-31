# prob02 ablation 预注册方案（ablation_v001）

> 阶段：ablation ｜ Agent：ablation-analyst ｜ 版本：ablation_v001
> 依据：ablation-analyst 角色说明与 knowledge/robustness-ablation.md §消融设计
> （以当前完整模型为内部对照，选择 3–4 个有解释意义的公式项或算法模块，每次只改变一个目标项，
> 保持数据、随机种子与其余配置一致）。
> **本方案（核心结论与消融判据）在实验运行前固定，不得事后修改；**
> 中途若需调整必须创建新方案版本并保留旧版本与结果（knowledge/robustness-ablation.md）。

## 1. 核心结论（本次 ablation 检验的对象）

prob02（assumption_v001 / formulation_v003）的碳化硅外延层厚度实测反演：

- 主反演（M1 = 基线-干涉分解 + 一维相位-频率扫描，variable projection，两角共享 t，t 与 n_sub 解耦）：
  由 computation v003 给出 `t̂(共享)=7.2158 µm`，每角 `7.2214 / 7.2095 µm`，`ε₁₂=0.165%`，
  `n̂_sub=2.588`（弱可辨识），主拟合加权 RMSE≈6.3e-4；只读 FFT 周期图独立证实带内真实干涉周期
  Δg≈657/698、Δν≈247/263 cm⁻¹ → t≈7.2–8.0 µm，与主结果一致。

**ablation 检验的问题**：完整模型（M1）的哪些**公式项/算法模块**真正贡献厚度反演结果？
- 色散模型 n(ν)（Sellmeier，B6）是否必要？（A1：移除 → 常数 n 基线，B10 已知约 4.2–4.7% 偏差）
- 基线-稳健分解 B(ν)（§5.1/§5.3，v003 根因一修正）是否必要？（A2：移除 → 常数基线）
- 相位-频率 variable projection（§5.2/§5.5）相对全谱幅值 NLS（v002 主方法）是否更必要？（A3）
- 两角共享 t（M_shared，§5.6/§7.1）是否必要/是否为良性约束？（A4：移除 → 每角独立 t）

## 2. 消融判据（运行前固定，不能事后修改）

以 F0（完整模型）为内部对照；因 prob02 为实测数据、无真值 t_true，判据采用 **F0 相对差值** 与
**可辨识性/约束满足度**度量（不依赖外部的真值）。默认阈值在 `configs/ablation_config.yaml` 登记。

| 实验 | 移除/替换操作 | 判据（实测满足即确认预期机制） | 预期依据 |
|---|---|---|---|
| F0 对照 | 无（完整模型 M1） | t̂ 落在 FFT 周期图佐证的物理带区间（t≈7.2–8.0 µm）、J(t) 全局唯一（次小显著更高）、拟合残差低、R∈[0,1]、无 NaN/Inf | computation v003：t̂=7.2158 µm、唯一性 PASS |
| A1 | N-SE（Sellmeier）→ N-const（常数 n） | Δt_disp_abl=|t̂_A1−t̂_F0|/t̂_F0 **> τ=1%**（色散贡献，B10） | B10：常数 n 在 2000–4000 cm⁻¹ 引入约 4.2–4.7% 系统偏差 |
| A2 | 基线多项式 p=3 → p=0（常数基线） | Δt_base_abl=|t̂_A2−t̂_F0|/t̂_F0 **> τ=1%** 或主拟合 RMSE 显著上升（>2×F0 的 RMSE） | v003 §0.1：未建模慢变基线主导目标 → 收敛到非物理/偏置结果 |
| A3 | 相位-频率 variable projection → 全谱幅值 NLS（v002 M1） | Δt_vp_abl=|t̂_A3−t̂_F0|/t̂_F0 **> τ=1%**（相位-频率方法贡献） | v003 §6.4/cross-check：物理正模型 NLS 与主结果差约 5.5% |
| A4 | 两角共享 t（M_shared）→ 每角独立 t（M_indep） | 每角 t̂ 与共享 t̂ 最大相对差 ≤ τ=2% **且** ε₁₂ ≤ τ=2%（共享-t 为良性/安全约束，不扭曲 t̂） | v003 §7.1/computation：ε₁₂=0.165%≪2% |

**结论分级**：
- 全部判据与预期一致 → `components_confirmed`（色散、基线-稳健分解、相位-频率方法必要；两角共享-t
  为良性一致约束，全部确认）；
- 部分不一致（实验完整执行）→ `components_partially_confirmed`，如实报告反证项与边界；
- 不删除不利情景；A1/A2/A3 的「偏置/退化」是预期结论而非实验失败。

**约束满足度**（所有实验）：模型反射率 R∈[0,1]（能量守恒，formula_validation §4）；t̂>0；
无 NaN/Inf；消融模型物理上仍满足 0≤R≤1（A1 常数 n、A2 常数基线、A4 独立 t 均不破坏物理边界；
A3 使用正模型 (2.3)/(2.4)，本身满足 R∈[0,1]）。

## 3. 实验矩阵

基准场景（与 computation/robustness 阶段一致）：附件 1/2（θ=10°/15°）、主反演带 ν∈[2000,4000] cm⁻¹
（Sellmeier 已知区，B6）、Reststrahlen [700,1000] cm⁻¹ 剔除（w=0，B3）、异常点（反射率>100%，n=262）
按 weight_anomaly=0.05 降权（不修改原始数据，B2）、基线/包络多项式 p=3/q=1（中心化正交化 Chebyshev 基，
Vandomer 归一化）、扫描区间 [3.0,20.0] µm/步长 0.01 µm、种子 20260829。

| 实验 | 观测谱 | 反演模型 | 反演方法 | 输出 |
|---|---|---|---|---|
| F0 | 附件 1/2 实测（预处理后） | 完整 M1（N-SE, p=3, q=1） | 变量投影：基线-干涉分解 + 一维相位-频率扫描（共享 t） | t̂、J(t)、唯一性、RMSE |
| A1 | 同上 | N-const（常数 n） | 同上（共享 t） | t̂、Δt_disp_abl、RMSE |
| A2 | 同上 | N-SE, p=0（常数基线） | 同上（共享 t） | t̂、Δt_base_abl、RMSE |
| A3 | 同上 | 完整正模型 (2.3)/(2.4) | 全谱幅值 NLS（invert_nls_multistart，网格扫描初值） | t̂_nls、Δt_vp_abl、RMSE |
| A4 | 同上 | N-SE, p=3, q=1 | 变量投影（每角独立 t） | 每角 t̂、ε₁₂、Δt_shared_abl |

## 4. 随机性与复现

- 主种子：20260829（与 computation/robustness 阶段一致，AUTOMM_SEED 优先）；
- 本方案全部实验为确定性计算（无随机噪声注入；A3 的网格扫描与多初值为确定性布点），seed 仅用于
  元数据与可复现性登记；
- 各实验使用相同观测谱、预处理、谱段、扫描配置、种子策略与计算预算
  （knowledge/robustness-ablation.md §Sanity）。

## 5. 失败处理

- 实验级异常（如消融模型全反射、NLS 异常、参数越界）：记录错误行，不静默删除，计入结果并如实报告；
- 任务级失败（进程/超时）：按 failure_class 路由（code_runtime → 复现后重试或修订；
  infrastructure_transient → 重试），不直接人工阻塞（PROJECT.md §失败和门禁）；
- 输出 `result.json` 的 `feasible_incumbent=true` 表示实验完整执行、判据评估完成；
  判据与预期不一致是「components_partially_confirmed」结论而非任务失败。

## 6. 输出与追踪

输出目录 `results/ablation/`（隔离 task，supervised worker）：
- `result.json`（F0 + A1–A4 各实验判定、conclusion、feasible_incumbent）；
- `summary.json`（汇总表：各实验 t̂、RMSE、Δt/ε₁₂、约束满足度、判定）；
- `checks.json`（预注册判据逐条检查，预期 vs 实测）；
- `metadata.json`（场景、种子、输入/配置 hash、单位约定、公式引用）；
- 代码 `code/ablation.py`、配置 `configs/ablation_config.yaml`；
- 任务经 `scripts/compute_dispatcher.py submit` 创建（stage=ablation），task hash 追踪
  （code/config/input）与任务输出目录一致。

## 7. 与 formulation/假设的对应

| 实验 | 对应公式/假设 | 对应既有预警/结论 |
|---|---|---|
| F0 | (5.1)-(5.7)、§5/§6 主方法 | computation v003：t̂=7.2158 µm、唯一性 PASS、RMSE≈6.3e-4 |
| A1 | (4.1) Sellmeier；B6；M3 常数 n 基线 (B10) | B10：常数 n 在 2000–4000 cm⁻¹ 约 4.2–4.7% 系统偏差 |
| A2 | (5.1)/(5.3) 基线多项式；v003 §0.1 根因一 | v002 根因一：未建模慢变基线主导目标（全谱 NLS 收敛 t≈0.3µm） |
| A3 | (5.2)/(5.5) variable projection；§6.4 正模型 NLS 交叉校验 | v003 §6.4/cross-check：P1=6.816 µm 与主结果差约 5.5% |
| A4 | (5.6)/(5.7) M_shared；§7.1 两角一致性 F 检验 | v003 §7.1/computation：ε₁₂=0.165%≪2%（B11） |

## 8. 遗留与移交（prob03 / 论文）

- 本阶段给出方法层证据：色散修正、基线-稳健分解、相位-频率方法为厚度反演的必要/关键组件（A1/A2/A3），
  两角共享-t 为良性一致约束（A4 预期每角≈共享）；
  若实测与预期不符，prob02 需优先核查相应组件/假设；
- 多光束（Airy）对极值位置的影响属 prob03 独立验证（B13），本阶段的两光束组件消融为其提供基线对照；
- λ>5µm 色散缺口（B6）与 n_sub 弱可辨识（B7）为既有 workflow warning，ablation 不重复覆盖，
  由论文讨论与文献复核承接。
