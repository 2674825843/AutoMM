# prob01 robustness 预注册方案（robustness_v001）

> 阶段：robustness ｜ Agent：robustness-analyst ｜ 版本：robustness_v001
> 依据：robustness-analyst 默认方案（95% 置信区间；主要数值参数 ±5%/±10%/±20%；
> 随机实验至少 100 次）与 knowledge/robustness-ablation.md。
> **本方案（核心结论与稳定性判据）在实验运行前固定，不得事后修改；**
> 中途若需调整必须创建新方案版本并保留旧版本与结果（knowledge/robustness-ablation.md）。

## 1. 核心结论（本次 robustness 检验的对象）

prob01（assumption_v001 / formulation_v001）的两光束干涉测厚模型与反演方法：

- 正模型 (3.5)/(3.6)：`R(ν; t, n(ν), θ, n_sub)`；
- 厚度反演公式：方法 A 极值间隔 (3.9)/(3.10)、色散化相位法 (3.13)、全谱 NLS（§3.6 方法 B）；
- 合成验证已确认：t_true=10 µm 被相位法/NLS 精确恢复（<0.03%），两入射角一致，
  方法 A 存在约 4% 文档化色散偏差（implementation §6.1）。

**robustness 检验的问题**：该厚度反演结论是否依赖脆弱参数（n_sub、入射角）、
数据噪声、色散模型结构或谱段截断？在合成基准（t_true=10 µm）下量化各因素对
NLS 反演厚度的影响，为 prob02 实测反演的不确定度控制提供方法层证据。

## 2. 稳定性判据（运行前固定，不能事后修改）

| 实验 | 判据（实测不超过阈值即「稳定」） | 阈值依据 |
|---|---|---|
| E1 n_sub 扰动 | NLS 厚度相对真值最大误差 ≤ 3% | n_sub 仅影响界面反射率幅度，条纹相位由 n(ν) 决定；3% 为宽松上限 |
| E2 入射角扰动 | NLS 厚度相对真值最大误差 ≤ 2% | t ∝ 1/cosθ′，θ 误差传播为一阶小量（A10 预期） |
| E3 色散模型情景 | 基准 Sellmeier 下 NLS 误差 ≤ 1%；替代模型（分段常数/常数 n）偏差 ≤ 5% | 正确色散模型应精确恢复；替代模型偏差为已知方法限制（A3/A5 文档化），≤5% 判定可接受 |
| E4 数据噪声 | σ=0.5%/1.0%/2.0% 的 NLS 厚度 95% CI 半宽分别 ≤ 2%/4%/8%；收敛率 100% | 全谱拟合（3601 点）平均效应强，噪声影响预期远小于阈值；失败运行计入收敛率 |
| E5 谱段截断 | NLS 厚度相对基准截断 [2000,4000] 最大变化 ≤ 2% | 谱段边界选择不应显著改变厚度估计 |

**结论分级**（knowledge/robustness-ablation.md §结果分级）：
- 全部判据通过 → `stable`；
- 部分未通过（实验完整执行）→ `conditionally_stable`，报告边界与脆弱参数，prob02 必须优先精确确定；
- 不删除不利情景；E4 失败运行计入收敛率。

## 3. 实验矩阵

基准场景（与 computation 阶段 synthetic_verify 一致）：t_true=10 µm、n_sub=3.0、
θ ∈ {10°, 15°}、谱段 [400, 4000] cm⁻¹（3601 点）、弱色散反演段 [2000, 4000] cm⁻¹、
Reststrahlen 区 [700, 1000] cm⁻¹ 排除（A7）。

| 实验 | 扰动对象 | 设计 | 生成谱 | 反演 |
|---|---|---|---|---|
| E1 | n_sub（衬底折射率） | 扰动集 {2.40, 2.70, 2.85, 3.00, 3.15, 3.30, 3.60}（±5/±10/±20%）× 2 入射角 = 14 点 | 基准 n_sub=3.0 | 扰动 n_sub（模拟 prob02 衬底折射率估计误差） |
| E2 | θ（入射角） | 扰动集 ±5/±10/±20%（θ=10° → 8/9/9.5/10.5/11/12°；θ=15° → 12/13.5/14.25/15.75/16.5/18°）× 2 基准角 = 24 点 | 基准 θ | 扰动 θ（模拟入射角测量误差） |
| E3 | 色散模型结构 | S1 Sellmeier+constant（基准）／S2 分段常数（弱色散段均值）／S3 常数 n（全谱段均值）× 2 入射角 = 6 点 | S1 基准色散 | 三种色散模型（模拟 prob02 色散模型选择不确定） |
| E4 | 数据噪声 | σ ∈ {0.5%, 1.0%, 2.0%}（反射率相对高斯噪声）× 2 入射角 × 100 次随机实验 = 600 次 | 基准参数 + 加噪 | 全谱 NLS（网格扫描初值 + ±period 布点） |
| E5 | 反演谱段截断 | 截断集 {[1800,4000],[1900,4000],[2000,4000](基准),[2100,4000],[2000,3800],[2000,3600]} × 2 入射角 = 12 点 | 基准参数（full 谱） | 截断谱段 NLS |

## 4. 初值策略（预注册声明）

全谱 NLS 初值：**网格扫描初值（t ∈ [1, 25] µm，200 点均匀扫描最小 rmse）+ ±period 平移布点**
（period 由 (2.8) 周期估计，formula_validation §6 周期歧义）。

调试依据：噪声 σ=1% 下方法 A/相位法的极值定位初值可严重失真（实测偏离到 ~109 µm），
网格初值不依赖极值定位，σ=2% × 100 次实验收敛率 100%（小型预实验实测）。
该策略与 prob02 实测反演兼容（prob02 同样面对噪声下的初值问题）。

## 5. 随机性与复现

- 主种子：20260829（与 computation 阶段 synthetic_verify 一致，AUTOMM_SEED 优先）；
- E4 各 σ 独立种子：`seed + round(σ×100)`（σ=0.5→seed+50、1.0→seed+100、2.0→seed+200）；
- 每次随机实验从该 σ 种子派生 rng 顺序抽取，可复现；
- 各方案使用相同数据、种子策略与计算预算（knowledge/robustness-ablation.md §Sanity）。

## 6. 失败处理

- E4 中 NLS 不收敛/异常：计入收敛率（不静默删除），raw_samples 记录 success=False 与错误；
- 任务级失败（进程/超时）：按 failure_class 路由（code_runtime → 复现后重试或修订；
  infrastructure_transient → 重试），不直接人工阻塞（PROJECT.md §失败和门禁）；
- 输出 `result.json` 的 `feasible_incumbent=true` 表示实验完整执行、判据评估完成；
  未通过判据是「条件稳定」结论而非任务失败。

## 7. 输出与追踪

输出目录 `results/robustness/`（隔离 task，supervised worker）：
- `result.json`（判据通过情况、conclusion、feasible_incumbent）、`summary.json`（汇总表）、
  `checks.json`（判据逐条检查）、`metadata.json`（场景/种子/hash/单位）、
  `raw_samples/e4_noise_raw.csv`（E4 原始样本，与汇总分开保存）；
- 代码 `code/robustness.py`、配置 `configs/robustness_config.yaml`；
- 任务经 `scripts/compute_dispatcher.py submit` 创建（stage=robustness），task hash 追踪
  （code/config/input）与任务输出目录一致。

## 8. 与 formulation/假设的对应

| 实验 | 对应假设/公式 | 对应 workflow warning |
|---|---|---|
| E1 | A6（n_sub 灵敏度）、(3.5) R2 | n_sub=3.0 为合成场景值 |
| E2 | A10（入射角误差传播）、(3.10) | — |
| E3 | A3/A5（色散模型选择）、(4.1) | λ>5 µm 常数延伸、方法 A 约 4% 偏差 |
| E4 | 方法 B §3.6、formula_validation §6 周期歧义 | 图表基于合成数据（prob01 无实测） |
| E5 | A7 谱段边界、§4 适用性 | Reststrahlen 剔除策略 |

## 9. 遗留与移交（prob02）

- 实测数据反演的真实噪声水平、异常点（反射率 >100%）与 Reststrahlen 区剔除策略
  属 prob02 预处理，本阶段基于合成噪声给出方法层稳健性证据；
- n_sub 与色散模型的实测取值/反演属 prob02，本阶段结论用于设定 prob02 的不确定度预期
  （E1/E3 实测偏差即为 prob02 参数估计误差可容忍的上界参考）。
