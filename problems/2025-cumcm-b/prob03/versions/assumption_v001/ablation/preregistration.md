# prob03 ablation 预注册方案（ablation_v001）

> 阶段：ablation ｜ Agent：ablation-analyst ｜ 版本：ablation_v001
> 依据：ablation-analyst 角色说明与 knowledge/robustness-ablation.md §消融设计
> （完整模型为内部对照，选择 3–4 个关键机制/公式项/算法模块/约束，每次只改变一个目标项，
> 保持数据、随机种子与其余配置一致；robustness-ablation.md §Sanity）。
> **本方案（核心结论与消融判据）在实验运行前固定，不得事后修改；**
> 中途若需调整必须创建新方案版本并保留旧版本与结果。

## 1. 核心结论（本次 ablation 检验的对象）

prob03（assumption_v001 / formulation_v002）的硅片（附件3/4）外延层厚度反演与多光束判定：

- 主反演（S1，variable projection，基线-干涉分解 + 一维相位频率扫描，两角共享 t）：
  `t̂(共享)=3.4477 µm`，每角 `3.4507 / 3.4463 µm`，`ε₁₂=0.130%`，`n̂_sub=3.558`（幅值弱可辨识）；
  主拟合加权 RMSE≈2.57e-3。
- 多光束判定：硅 `R̄=√(R₀₁R₁₂)≈0.0101`≤θ_mb=0.05、`F≈0.319`、`η_mb≈0.11%`≪τ_mb=10% → **两光束适用**；
  SiC `R̄≈0.0024` → **无需修正**，prob02 `t̂=7.2158 µm` 维持（C17）。
- Q1（多光束必要条件）：N1–N4 全部满足，L17「无吸收时 Airy 极值位置不变性」独立推导验证成立（§4.5）。

**ablation 检验的问题**：完整模型的哪些**公式项/算法模块/约束方向**真正贡献 `t̂` 与多光束判定结论？
- 色散项（Sellmeier vs 常数 n）是否是 t̂ 的关键复杂度？（A1）
- 多光束（Airy）高阶干涉项是否改变 t̂（验证 L17 / Q1 定量）？（A2）
- 基线多项式项（B(ν) 阶数）是否是 t̂ 的必要组件？（A3）
- 两角共享 t 约束是否强加偏差、还是有约束力？（A4）

## 2. 消融判据（运行前固定，不能事后修改）

基准场景：硅片附件 3/4，入射角 θ∈{10°,15°}，主反演带 ν∈[2000,4000] cm⁻¹（透明窗，C8），
多声子带 [400,1600] cm⁻¹ 剔除（w=0），基线/包络多项式 p=3/q=1（中心化正交化 Chebyshev 基），
两角共享 t，色散模型 N-SE（Sellmeier）。随机种子 20260830，与 computation/robustness 阶段一致。

| 实验 | 移除/替换操作 | 判据（实测满足即确认预期机制） | 预期依据 |
|---|---|---|---|
| F0 对照 | 无（完整模型） | t̂ 落在 [3.40,3.49] µm；加权 RMSE 有限、R∈[0,1] | computation/robustness 已实测 t̂=3.4477、RMSE≈2.57e-3、R∈[0,1] |
| A1 | N-SE → N-const（常数 n=n(5µm)） | Δt=|t̂_Nconst−t̂_NSE|/t̂_NSE×100% ≤ 2%；报告唯一性比值 | 硅色散弱（Δn/n≈0.51%，robustness R2 Δt_disp≈0.503%≤2%）；色散项非 t̂ 关键复杂度 |
| A2 | 两光束一阶 VP → 加 Airy 高阶谐波（cos2δ/sin2δ、cos3δ/sin3δ） | Δt=|t̂_harm−t̂_F0|/t̂_F0×100% ≤ 1%；报告 RMSE 变化 | L17 极值不变性：Airy 高阶不改变极值位置/相位频率 → 不改 t̂（robustness R5 η_mb≈0.11% 佐证） |
| A3 | p=3 → p=0（仅常数 DC 基线） | Δt=|t̂_p0−t̂_p3|/t̂_p3×100% ≤ 2%；报告 RMSE 上升 | B(ν) 吸收 DC/慢变基线，不进入 δ(t) 相位频率 → 不改 t̂（robustness 基线阶数稳健 p=1..6） |
| A4 | shared=True → False（每角独立 t） | max(|t̂_k−t̂_shared|)/t̂_shared×100% ≤ 2%；ε₁₂ ≤ 2% | 两角共享 t 为一致性约束（robustness R1 ε₁₂≈0.130%）；每角独立 t̂ 与共享一致（不强制偏差） |

**约束满足度（所有实验）**：拟合模型（基线+干涉分解）残差有限（无 NaN/Inf）；以最佳 t̂ 计算的两光束物理
正模型反射率 R∈[0,1]（能量守恒）；t̂>0。失败/异常实验计入结果并如实报告，不静默删除。

**结论分级**：
- 全部判据与预期一致 → `components_confirmed`（色散项/基线/包络/共享 t 约束为安全简化、多光束高阶对 t̂ 无贡献——L17 定量成立）；
- 部分不一致（实验完整执行）→ `components_partially_confirmed`，如实报告反证项与边界；
- 不删除不利情景；A1–A4 的「t̂ 稳定/Δt≈0」是「复杂度不贡献 t̂」的正常结论，不是实验失败。

## 3. 实验矩阵

| 实验 | 反演模型 | 色散 | p | q | shared | Δt vs F0 阈值 | 报告指标 |
|---|---|---|---|---|---|---|---|
| F0 | VP（完整模型） | N-SE | 3 | 1 | True | — | t̂、加权 RMSE、R∈[0,1]、唯一性比值 |
| A1 | VP | N-const | 3 | 1 | True | ≤2% | t̂、Δt%、唯一性比值 |
| A2 | VP + Airy 高阶谐波 | N-SE | 3 | 1 | True | ≤1% | t̂、Δt%、加权 RMSE |
| A3 | VP | N-SE | 0 | 1 | True | ≤2% | t̂、Δ t%、加权 RMSE |
| A4 | VP | N-SE | 3 | 1 | False | ≤2% | 每角 t̂、ε₁₂、与共享 t̂ 偏差 |

主判定量：Δt%（vs F0）与相对阈值；加权 RMSE（最优拟合）；物理正模型 R∈[0,1]。
每实验输出 `result.json` 的 `experiment` 块 + `summary.json` 汇总表（F0 + A1–A4）。

## 4. 随机性与复现

- 主种子：20260830（与 computation/robustness 阶段一致，AUTOMM_SEED 优先）；
- 本方案全部实验为**确定性计算**（无随机噪声注入，实测观测谱固定），seed 仅用于元数据与可复现性登记；
- 各实验使用相同数据、种子策略与计算预算（knowledge/robustness-ablation.md §Sanity）；
- 原始数据只读（`sha256` 校验与 README 一致），不修改数据/代码/历史结果。

## 5. 失败处理

- 实验级异常（如全反射、线性 LS 秩亏、NaN/Inf）：记录错误行，不静默删除，计入结果并如实报告；
- 任务级失败（进程/超时）：按 failure_class 路由（code_runtime → 复现后重试或修订；
  infrastructure_transient → 重试），不直接人工阻塞（PROJECT.md §失败和门禁）；
- 输出 `result.json` 的 `feasible_incumbent=true` 表示实验完整执行、判据评估完成；
  判据与预期不一致是「components_partially_confirmed」结论而非任务失败。

## 6. 输出与追踪

输出目录 `results/ablation/`（隔离 task，supervised worker）：
- `result.json`（各实验判定、conclusion、feasible_incumbent）、`summary.json`（汇总表：F0 + A1–A4 的
  t̂、Δt%、加权 RMSE、R∈[0,1]、判定）、`checks.json`（判据逐条检查）、
  `metadata.json`（场景、种子、输入/配置 hash、单位约定、公式引用）；
- 代码 `code/ablation.py`、配置 `configs/ablation_config.yaml`（复用已审定 model.py，不修改模型代码，
  保持 computation/robustness 既有 hash 追踪链稳定）；
- 任务经 `scripts/compute_dispatcher.py submit` 创建（stage=ablation），task hash 追踪
  （code/config/input）与任务输出目录一致。

## 7. 与 formulation/假设的对应

| 实验 | 对应公式/假设 | 说明 |
|---|---|---|
| F0 | (7.1)–(7.5)、§7.3；C8/C11 | 主反演（基线-干涉分解 + 一维相位频率扫描，两角共享 t） |
| A1 | (6.1)、C8；parameters.yaml `dispersion_model=[N-SE,N-const]` | 色散项（Sellmeier vs 常数 n）；robustness R2 只测 ±0.5% 扰动、ablation 测去除整项 |
| A2 | (3.6)、(4.5)/(4.8)；L17 | Airy 多光束高阶干涉项；robustness R5 只测 η_mb（固定 t̂ 的残差改善）、ablation 测是否改变 t̂ |
| A3 | (7.2)/(7.3)，BASELINE_POLY_DEG | 基线多项式项；robustness 只做阶数稳健 p=1..6、ablation 测去除基线项 |
| A4 | (7.5)、B11 | 两角共享 t 约束；robustness R1 用嵌套 F 检验、ablation 测共享约束本身对 t̂ 的影响 |

## 8. 遗留与移交

- **本阶段给出模型组件必要性证据**：色散项/基线/包络/共享 t 约束是否为安全简化、多光束高阶对 t̂ 是否无贡献
  （L17 定量），供论文/后续小问引用；
- **与 robustness 关系**：robustness 给出 t̂ 对输入/情景不确定性的稳定性（stable）；ablation 给出模型内部
  组件/约束的必要性，二者共同支撑「模型复杂度与参数选择对结论稳健、答案由相位频率机制主导」；
- **多光束修正预留下一步**：若某样品 η_mb>τ_mb（本版硅/SiC 均不触发），启用 formulation §8.4 并记录 t̂ 位移
  （预期≈0，验证 L17）——ablation 的 A2 恰为该预注册判断提供定量基线。
