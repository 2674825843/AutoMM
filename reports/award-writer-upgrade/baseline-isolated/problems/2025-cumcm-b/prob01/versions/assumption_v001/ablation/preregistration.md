# prob01 ablation 预注册方案（ablation_v001）

> 阶段：ablation ｜ Agent：ablation-analyst ｜ 版本：ablation_v001
> 依据：ablation-analyst 角色说明与 knowledge/robustness-ablation.md §消融设计
> （完整模型为内部对照，选择 3–4 个关键机制/公式项/算法模块，每次只改变一个目标项，
> 保持数据、随机种子与其余配置一致）。
> **本方案（核心结论与消融判据）在实验运行前固定，不得事后修改；**
> 中途若需调整必须创建新方案版本并保留旧版本与结果（knowledge/robustness-ablation.md）。

## 1. 核心结论（本次 ablation 检验的对象）

prob01（assumption_v001 / formulation_v001）的两光束干涉测厚模型与反演方法：

- 正模型 (3.5)/(3.6)：`R(ν; t, n(ν), θ, n_sub) = R1 + (1-R1)²R2 + 2(1-R1)√(R1R2)·cosδ`；
- 反演：全谱 NLS（§3.6 方法 B，网格扫描初值 + ±period 多初值布点）为主方法，
  方法 A 极值间隔 (3.9) 为基线/初值，色散化相位法 (3.13) 交叉验证；
- 合成验证已确认：t_true=10 µm 被 NLS/相位法精确恢复（<0.03%），两入射角一致。

**ablation 检验的问题**：完整模型的哪些**公式项与算法模块**真正贡献厚度反演结果？
- 干涉叠加项（cosδ 项）是否是厚度信息的唯一载体？（A1：相干叠加假设 A11 的贡献）
- 衬底界面反射项（R2）是否是干涉条纹的必要条件？（A2：衬底-外延层折射率差 A6 的贡献）
- 偏振平均（(3.6)）是否是安全简化，还是引入偏差？（A3：s/p 平均的贡献）
- NLS 多初值模块是否必要，移除后是否因周期歧义退化？（A4：初值策略模块的贡献）

## 2. 消融判据（运行前固定，不能事后修改）

| 实验 | 移除/替换操作 | 判据（实测满足即确认预期机制） | 预期依据 |
|---|---|---|---|
| F0 对照 | 无（完整模型） | NLS 厚度相对真值最大误差 ≤ 1%（两入射角）且 rmse(t) 网格在 t_true 处为全局极小（rmse 深度比 ≥ 100） | 合成验证已知：NLS 精确恢复（implementation §5/§6.1） |
| A1 | 干涉项置零（非相干叠加模型） | rmse(t) 网格（t∈[1,25] µm）平坦度 ≤ 5% → 厚度不可辨识 | 非相干模型不含 t（R1、R2 仅依赖 n、θ、n_sub）→ 无厚度信息 |
| A2 | 衬底界面反射置零（R2→0） | rmse(t) 网格平坦度 ≤ 5% → 厚度不可辨识 | R2→0 后条纹幅度 ∝√(R1R2)→0，模型退化为界面 1 反射 → 无厚度信息 |
| A3 | s/p 平均替换为单 s / 单 p | s/p/avg 三种反演厚度最大相对差 ≤ 1%（两入射角） | 相位 δ 与偏振无关（A4：跃变只改峰谷类型、不改变同型极值间隔） |
| A4 | 移除多初值（仅方法 A 解析初值） | 单初值 NLS 相对真值误差 > 2% 且多初值 ≤ 1%（两入射角） | formula_validation §6 周期歧义：cosδ 对 t 周期约 0.9 µm，implementation §6.1 实测单初值落入局部极小（t0=10.44 → 10.63） |

**结论分级**：
- 全部判据与预期一致 → `components_confirmed`（干涉项/衬底反射项必要、偏振平均简化安全、
  多初值模块必要，全部确认）；
- 部分不一致（实验完整执行）→ `components_partially_confirmed`，如实报告反证项与边界，
  prob02 需关注相应组件；
- 不删除不利情景；A1/A2 的「不可辨识」是预期结论而非实验失败。

## 3. 实验矩阵

基准场景（与 computation 阶段 synthetic_verify / robustness 阶段一致）：t_true=10 µm、
n_sub=3.0、θ ∈ {10°, 15°}、谱段 [400, 4000] cm⁻¹（3601 点）、弱色散反演段 [2000, 4000] cm⁻¹、
Reststrahlen 区 [700, 1000] cm⁻¹ 排除（A7）。

| 实验 | 观测谱生成 | 反演模型 | 反演方法 | 行数 |
|---|---|---|---|---|
| F0 | 完整模型 (3.5) avg（基准） | 完整模型 avg | 全谱 NLS 多初值 | 2（θ×1） |
| A1 | 完整模型 avg（基准） | 非相干模型（去 cosδ 项） | rmse 网格 + NLS | 2 |
| A2 | 完整模型 avg（基准） | 无衬底模型（R2→0） | rmse 网格 + NLS | 2 |
| A3 | 完整模型 avg（基准） | avg / s / p 三种 | 全谱 NLS 多初值 | 6（3 pol × 2 θ） |
| A4 | 完整模型 avg（基准） | 完整模型 avg | 单初值 NLS vs 多初值 NLS | 4（2 初值策略 × 2 θ） |

**可辨识性度量**（A1/A2）：rmse(t) 网格，t ∈ [1, 25] µm、200 点均匀（与 robustness 网格扫描
一致）；平坦度 flatness = (max(rmse) - min(rmse)) / (min(rmse) + ε)，ε=1e-12 防除零；
flatness ≤ 5% 判定「厚度不可辨识」。F0 对照组报告 rmse 深度比 = max/min（t_true 处接近 0，
深度比预期 ≥ 100）。

**约束满足度**（所有实验）：模型反射率 R ∈ [0, 1]（能量守恒，(3.5) 物理边界）；
A1/A2 消融模型物理上仍应满足 0 ≤ R ≤ 1。

## 4. 初值策略（预注册声明）

- F0 / A3：全谱 NLS 初值 = 网格扫描（t ∈ [1, 25] µm，200 点最小 rmse）+ ±period 平移布点
  （与 robustness 阶段一致，robustness.py run_nls）；
- A4 单初值分支：仅用方法 A 解析初值（弱色散段 [2000,4000] cm⁻¹ 峰定位 → 同型间隔中位数 →
  (3.10)），单次 NLS，**不**做网格扫描与 ±period 布点（模拟 prob02 若仅用解析初值的退化情景）；
- A4 多初值分支：与 F0 相同。

## 5. 随机性与复现

- 主种子：20260829（与 computation/robustness 阶段一致，AUTOMM_SEED 优先）；
- 本方案全部实验为确定性计算（无随机噪声注入，观测谱固定），seed 仅用于元数据与可复现性登记；
- 各实验使用相同观测谱、种子策略与计算预算（knowledge/robustness-ablation.md §Sanity）。

## 6. 失败处理

- 实验级异常（如消融模型全反射、NLS 异常）：记录错误行，不静默删除，计入结果并如实报告；
- 任务级失败（进程/超时）：按 failure_class 路由（code_runtime → 复现后重试或修订；
  infrastructure_transient → 重试），不直接人工阻塞（PROJECT.md §失败和门禁）；
- 输出 `result.json` 的 `feasible_incumbent=true` 表示实验完整执行、判据评估完成；
  判据与预期不一致是「components_partially_confirmed」结论而非任务失败。

## 7. 输出与追踪

输出目录 `results/ablation/`（隔离 task，supervised worker）：
- `result.json`（各实验判定、conclusion、feasible_incumbent）、`summary.json`（汇总表：
  F0 + A1–A4 的 t、rmse、平坦度/深度比、约束满足度、判定）、`checks.json`（判据逐条检查）、
  `metadata.json`（场景、种子、输入/配置 hash、单位约定、公式引用）；
- 代码 `code/ablation.py`、配置 `configs/ablation_config.yaml`；
- 任务经 `scripts/compute_dispatcher.py submit` 创建（stage=ablation），task hash 追踪
  （code/config/input）与任务输出目录一致。

## 8. 与 formulation/假设的对应

| 实验 | 对应公式/假设 | 对应既有预警 |
|---|---|---|
| F0 | (3.5)/(3.6)、§3.6 方法 B | implementation §5 合成验证基线 |
| A1 | (3.5) 干涉项、A11（相干性）、A3（干涉强度叠加） | A11 非关键假设（可观测验证：条纹对比度） |
| A2 | (3.5) R2 项、A6（衬底折射率差是条纹前提）、A1（两光束） | A6 预期偏差方向：折射率差过小则条纹对比度差 |
| A3 | (3.6) s/p 平均、A4（相位跃变不改变间隔） | A4 消除峰谷判定歧义 |
| A4 | §3.6 方法 B 多初值、formula_validation §6 周期歧义 | implementation §6.1 单初值局部极小预警 |

## 9. 遗留与移交（prob02 / prob03）

- 本阶段给出方法层证据：干涉项与衬底界面反射是厚度反演的必要组件（A1/A2 预期不可辨识）、
  偏振平均是安全简化（A3 预期不敏感）、多初值模块必要（A4 预期单初值退化）；
  若实测与预期不符，prob02 需优先核查相应组件/假设；
- 多光束（Airy）对极值位置的影响属 prob03 独立验证（A1 移交项），本阶段的两光束组件消融
  为其提供基线对照；
- 实测数据的真实噪声/异常点处理仍属 prob02 预处理（robustness 已移交，不重复）。
