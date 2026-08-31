# prob01 实现计划（implementation.md）

> 版本：assumption_v001 / formulation_v001 ｜ 阶段：implementation ｜ Agent：implementation-agent
> 问题：2025 高教社杯 B 题问题 1 —— 两光束干涉测厚数学模型。
> 本问为纯解析建模（无附件实测数据），实现内容 = 模型代码 + 合成数据数值验证任务规格。

## 1. 实现目标

1. 将 formulation_v001 的两光束干涉正模型与反演公式实现为可复现 Python 代码；
2. 用正模型自洽生成的合成反射率谱做数值验证：物理边界、极值间隔律、三种反演方法
   （极值间隔基线、色散化相位法、全谱 NLS）、两入射角一致性；
3. 完成静态检查（compileall、ruff、CLI --help、接口探针）并登记全部追踪信息；
4. 交付 computation 阶段可直接提交的任务规格（configs/task_spec.yaml）。

不运行完整数据集、不运行正式任务（由 Runner/tasks.py 在 computation 阶段创建 supervised worker 任务）。

## 2. 代码结构

```
problems/2025-cumcm-b/prob01/versions/assumption_v001/
├── code/
│   ├── model.py     # 核心模型与反演（无副作用，可 import；含探针 run_probes）
│   ├── compute.py   # CLI 入口：合成验证流水线 + 输出证据 JSON/CSV
│   └── probe.py     # 接口探针入口（秒级）
├── configs/
│   ├── task_config.yaml   # 计算任务执行配置（场景/容差/超时）
│   └── task_spec.yaml     # 计算任务规格（computation 阶段提交依据）
└── implementation.md      # 本文件
```

## 3. 公式映射（model.py 函数 ↔ formulation_v001 公式）

| 函数 | 公式 | 说明 |
|---|---|---|
| `sellmeier_n4hsi` | (4.1) | 4H-SiC Sellmeier，n²=6.79485+0.15558/(λ²−0.03535)−0.02296λ² |
| `dispersion_epi` / `dispersion_from_nu` | A5 | λ≤5µm Sellmeier；λ>5µm constant 延续（prob02 数据反演确定），记录 extrapolated |
| `theta_prime` / `cos_theta_prime` / `theta_double_prime` | (2.2)/(2.3) | Snell 折射角（n_air=1） |
| `optical_path_difference` | (2.6) | Δ=2t√(n²−sin²θ) |
| `phase_delta` | (2.8) | δ=4π×1e-4·n(ν)·t·ν·cosθ′(ν)，色散逐点计算 |
| `fresnel_interface` / `interface_reflectivities` | (3.1)-(3.3) | s/p 振幅与强度反射率 |
| `forward_reflectance` | (3.5)/(3.6) | 两光束反射率正模型（s/p 平均） |
| `two_beam_envelope` | (3.5) 包络 | center±amp，能量守恒核验 |
| `thickness_from_delta_nu` | (3.10) | t=1e4/(2n·cosθ′·Δν) |
| `thickness_from_phase_gap` / `invert_phase_method` | (3.13) | t=1e4/(2·Δg)，Δg=同型相邻极值 g 差 |
| `find_extrema` / `same_type_spacings` / `invert_from_spacing` | (3.7)/(3.8)/(3.9) | 方法 A 基线 |
| `invert_nls` / `invert_nls_multistart` | §3.6 方法 B | 全谱/弱色散 NLS，多初值规避周期歧义 |
| `evaluate_spacing_theory` | (3.8) | 常数 n 理论间隔（基线对照） |

符号与全局符号表一致（t、n、n_sub、n_air、theta、theta_prime、nu、lambda、delta、m、delta_nu）；
局部中间量 R1、R2、theta''、g(ν) 不入全局符号表（formulation_v001 §7 约定）。

## 4. 数据契约

### 4.1 输入

| 路径 | 内容 |
|---|---|
| `formulations/formulation_v001/parameters.yaml`（--input） | 参数登记权威来源：n_air、nu_range、reststrahlen_exclude、sellmeier_boundary（代码读取并交叉核验） |
| `configs/task_config.yaml`（--config） | 场景：t_true_um=10、n_sub=3.0、theta=[10,15]°、nu 400–4000 cm⁻¹、nu_points=3601、noise=0；反演/验证容差；compute 段（timeout 120s、memory 1GB） |
| 环境变量（worker 注入） | `AUTOMM_OUTPUT_DIR`（输出目录）、`AUTOMM_SEED`（种子）、`AUTOMM_TASK_ID` |

### 4.2 输出（AUTOMM_OUTPUT_DIR，即 `results/synthetic_verify/`）

| 文件 | 内容 |
|---|---|
| `result.json` | `feasible_incumbent`（worker 读取）、厚度估计汇总、检查失败列表、说明 |
| `solver_status.json` | 各 NLS 拟合 status/cost/nfev/message、多初值 starts、周期估计、容差 |
| `verification.json` | 全部检查明细（name/passed/detail/tolerance） |
| `metadata.json` | 场景、种子、输入/配置 hash、单位约定、公式引用 |
| `synthetic_spectrum_theta10.csv`、`synthetic_spectrum_theta15.csv` | nu, R_clean, R_noisy（供可视化/归档） |

### 4.3 单位约定（parameters.yaml 一致）

t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[deg]（三角转 rad）、Δν[cm⁻¹]、δ[rad]；
(2.8) 的 1e-4 换算因子即 µm/cm 与 cm⁻¹ 的归一。

## 5. 数值方法与验证设计

- **方法 A（基线，§3.6）**：弱色散谱段 [2000, 4000] cm⁻¹ 定位同型极值 → 间隔中位数 →
  (3.10) 反演。**实测确认 A3 文档化偏差**：该谱段色散效应显著（ν·dn/dν 约 9%），
  (3.8) 常数 n 近似带来约 4% 系统偏差（t_A≈10.44 vs t_true=10），故方法 A 作为
  基线/初值，容忍 10%（task_config method_a_tol_rel=0.10）。
- **色散化相位法（(3.13)，主方法之一）**：同型相邻极值（级次 m→m+2，即极值列表中相邻项）
  g 差 Δg = 1/(2×1e-4·t) = 5000/t[µm]（t=10 时 Δg=500 cm⁻¹），t=1e4/(2·Δg)。
  实测 t_phase≈10.00（10°/15° 均 <0.03% 误差）。
- **方法 B 全谱 NLS（§3.6，主方法）**：`scipy.optimize.least_squares` 单参数 t，
  初值 = 方法 A + 相位法，多初值布点 [t0, t0±period]（period≈0.9µm，厚度周期歧义，
  formula_validation §6）取 rmse 最小者。实测 t_NLS=10.000000，rmse≈0。
- **两入射角一致性（A10）**：10°/15° 反演厚度 rel 差 <2%。
- **Reststrahlen 边界（A7）**：700–1000 cm⁻¹ 无吸收模型不适用，方法 A/B 谱段均在其外。

## 6. 静态检查与探针结果（全部通过）

| 检查 | 结果 |
|---|---|
| `compileall` | passed |
| `ruff check`（E/F/I，line-length 120） | passed |
| `compute.py --help` | usage 正常 |
| `probe.py` / `compute.py --self-check`（9 项探针） | 9/9 passed（Sellmeier n(5µm)≈2.495、(2.5)=(2.6) 等价、Δν 数量级≈193、R∈[0,1] 且在 (3.5) 理论包络内、三种方法往返反演） |
| 端到端探针（任务命令原样运行，scratch 输出目录） | 19/19 检查通过，feasible_incumbent=true |

### 6.1 实现阶段发现（供 sanity 复核）

1. **formula_validation §4 数值例 [0.16, 0.24] 为近似值**：按 (3.5) 精确计算
   （n=2.6、n_sub=3.0、θ=10°、s/p 平均），R_s∈[0.1540,0.2569]、R_p∈[0.1456,0.2468]、
   平均包络 [0.1498, 0.2519]。实现与公式 (3.5) 逐项一致（已手算复核），文档例为粗略估计，
   不构成公式/实现不一致；本问验证以理论包络为准。
2. **(3.8) 常数 n 间隔在 2000–4000 cm⁻¹ 的偏差实测约 4.2–4.7%**（Δν_obs≈188 vs
   Δν_theory≈196 cm⁻¹）：与 A3 预期偏差方向一致，证实 formulation §3.5 的色散化必要性；
   相位法/NLS 无此偏差。
3. **厚度周期歧义**：cosδ 对 t 的周期约 0.9 µm（谱段中心估计），NLS 单初值可能落入
   错误局部极小（实测 t0=10.44 → 10.63），相位法初值 + 多初值布点后收敛到全局解
   （rmse≈0）。与 formula_validation §6 预警一致。

## 7. 追踪信息

| 项 | 值 |
|---|---|
| 假设版本 | assumption_v001（accepted） |
| 公式版本 | formulation_v001（accepted，content_hash bee86f0e…82277） |
| 代码目录 hash | `599ebe6536932f56fc40febd0faced2e090589791dea6b3459fa12df7314cdd5`（hash_path） |
| 代码入口 hash（compute.py） | `d22acb3f3c95eb64c6f9b58e5c67d265eda6af1f69d03c3a9940073ff39cca01` |
| 任务配置源文件 hash | `fea85c71160c3ec06ee5be1780ce4e6ab0a7a45704e3da30da62ba4a0e0df26b` |
| 任务配置合并 hash（tasks.py） | `eac5599ff69aadde7f00…`（config_hash 身份字段） |
| 输入参数 hash（parameters.yaml） | `ae4931470efcd30efa95ce7cf677890005d8dd4422f13aced03b6a81af6e48f8` |
| 随机种子 | 20260829（AUTOMM_SEED 优先） |
| 输出目录 | `problems/2025-cumcm-b/prob01/versions/assumption_v001/results/synthetic_verify` |
| 工作目录 | 项目根（.） |
| 任务 ID（预测，提交时以 tasks.py 实算为准） | `0ea4b29da19e8479a6ea` |
| Python | 3.13.9（numpy 2.3.5、scipy 1.16.3、ruff 0.12.0） |

### 7.1 失败条件与路由

- 进程非零退出 → `code_runtime`：先用 compileall/ruff/探针复现，再决定重试或修订（可修复一次）；
- `result.json` 缺失或 `feasible_incumbent=false` → 合成验证未通过：交由 sanity 路由，
  不盲目重跑（数值异常但进程成功按失败策略进入 sanity）；
- 输出目录与 spec 不一致或输出锁冲突 → `harness_invariant`，人工对账。

## 8. 计算任务规格（computation 阶段提交）

唯一任务：`prob01-synthetic-verification`（详细字段见 `configs/task_spec.yaml`）。
提交命令（Runner 以 sys.executable 替换 {python}）：

```
python scripts/compute_dispatcher.py submit --problem-id 2025-cumcm-b --question-id prob01 \
  --stage computation \
  --code-path problems/2025-cumcm-b/prob01/versions/assumption_v001/code/compute.py \
  --config-path problems/2025-cumcm-b/prob01/versions/assumption_v001/configs/task_config.yaml \
  --input-path problems/2025-cumcm-b/prob01/versions/assumption_v001/formulations/formulation_v001/parameters.yaml \
  --assumption-version assumption_v001 --formulation-version formulation_v001 \
  --output-directory problems/2025-cumcm-b/prob01/versions/assumption_v001/results/synthetic_verify \
  --working-directory . --timeout-seconds 120 --seed 20260829 \
  -- {python} problems/2025-cumcm-b/prob01/versions/assumption_v001/code/compute.py \
     --config problems/2025-cumcm-b/prob01/versions/assumption_v001/configs/task_config.yaml \
     --input problems/2025-cumcm-b/prob01/versions/assumption_v001/formulations/formulation_v001/parameters.yaml \
     --output problems/2025-cumcm-b/prob01/versions/assumption_v001/results/synthetic_verify
```

该规格已用 `make_task_spec` 静态校验通过（preflight：compileall/ruff passed；
output 目录位于假设版本内；公式版本为 accepted；后端 local；timeout 120s）。

## 9. 遗留与移交

- **prob02**：附件 1/2 实测数据反演（真实噪声、反射率 >100% 异常点预处理、
  Reststrahlen 剔除策略、n_sub 反演/文献取值、λ>5µm 色散分谱段/数据反演、灵敏度分析）；
  本实现的反演流水线（峰谷定位、相位法、NLS 多初值）直接复用。
- **prob03**：多光束（Airy）模型扩展（M4），本问未实现。
- **可视化**：合成谱 CSV 已落盘，visualization 阶段可据此生成图。
- 合成验证使用 λ>5µm 常数色散延续（prob01 无数据可反演），其物理精度不构成结论，
  仅用于验证公式/算法自洽性。
