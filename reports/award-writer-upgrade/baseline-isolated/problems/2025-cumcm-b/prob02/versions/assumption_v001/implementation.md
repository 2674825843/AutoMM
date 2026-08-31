# prob02 实现计划（implementation.md）

> 版本：assumption_v001 / formulation_v003 ｜ 阶段：implementation ｜ Agent：implementation-agent
> 问题：2025 高教社杯 B 题问题 2 —— 依据问题 1 的两光束干涉数学模型，设计确定 SiC 外延层厚度的算法；对附件 1（10°）与附件 2（15°）的实测光谱给出厚度计算结果并分析可靠性。
> 本问为**实测数据反演**（连续参数估计，精确方法）。实现内容 = 模型代码（复用 prob01 正模型/色散/Fresnel，**新增 v003 主反演＝基线-干涉分解 + 一维相位频率扫描（variable projection）**、n_sub 幅度弱辨识、两角一致性对相位-频率拟合的嵌套 F 检验）+ 附件数据反演流水线 + 任务规格。
> 本版为 **formulation_v003 的实现**（继承 assumption_v001）；相对 v001/v002 的差异见 §3/§5：主反演由"全谱幅值 NLS"改为"基线-干涉分解 + 一维相位频率扫描"，t 与 n_sub 结构解耦，从而消除 v002 computation 暴露的 M1/M2/M3 两数量级冲突与四项可靠性判据超阈（根因见 formulation §0）。

## 1. 实现目标

1. 将 formulation_v003 的实测数据反演链路实现为可复现 Python 代码：数据预处理（B1–B3 + 谱段截断 [2000,4000]）→ **主反演（基线-干涉分解 + 一维相位频率扫描，variable projection，两角共享 t）** → 可靠性分析（B11–B13/B7，两角嵌套 F 检验/带内色散敏感性 + Δt_inv_band/n_sub 解耦诊断/轮廓似然 CI/异常点/多光束）。
2. 复用 prob01 已核验的两光束正模型与色散模型（Fresnel、相位、Sellmeier、n_ref 锚点），针对 v003 方法修订为**基线/包络多项式（中心化正交化 Chebyshev 基）+ 一维 t 扫描**、t 由相位频率确定、n_sub 由幅值 A=√(C²+S²) 事后弱辨识。
3. 完成静态检查（compileall、ruff、CLI `--help`、接口探针、make_task_spec 预检）并登记全部追踪信息；
4. 交付 computation 阶段可直接提交的任务规格（configs/task_spec.yaml，输出目录 `thickness_inversion_v003`，与 v001/v002 分离）。

不运行完整数据集、不运行正式任务（由 Runner/tasks.py 在 computation 阶段创建 supervised worker 任务）；实现阶段仅做秒级接口探针与数据契约核验（本次以小型合成谱做端到端运维探针，见 §6.1）。

## 2. 代码结构

```
problems/2025-cumcm-b/prob02/versions/assumption_v001/
├── code/
│   ├── model.py            # 核心模型与反演（无副作用，可 import；含 run_probes）
│   ├── compute.py          # CLI 入口：附件数据反演流水线 + 输出证据 JSON/CSV（formulation_v003）
│   ├── probe.py            # 接口探针入口（秒级）
│   └── data/
│       └── n_ref_anchor.csv  # λ>5µm n_ref(λ) 锚点（Sellmeier<=5µm + Fischer>=17µm；5-17µm 缺口代理，
│                             #   仅作 Δt_inv_band 全谱诊断背景，不进入主反演）
├── configs/
│   ├── task_config.yaml    # 计算任务执行配置（附件路径/谱段截断/扫描/可靠性设置）
│   └── task_spec.yaml      # 计算任务规格（computation 阶段提交依据）
└── implementation.md       # 本文件
```

## 3. 公式映射（model.py / compute.py 函数 ↔ formulation_v003 公式）

| 函数 | 公式 | 说明 |
|---|---|---|
| `sellmeier_n4hsi` | (4.1) | 4H-SiC Sellmeier，n²=6.79485+0.15558/(λ²−0.03535)−0.02296λ²（λ≤5µm，L09） |
| `fischer_n4hsi` | (4.2) 数据来源 | Fischer et al. 2017，n²=6.055+2.669λ²/(λ²−167.8)（4H-SiC n(o)，17–150µm） |
| `dispersion_epi`(N-SE/N-SE-delta/N-const) | (4.1) | 分段色散：ν≥2000 Sellmeier；ν<2000 n_ref 插值×c_disp。N-SE 主（带内退化纯 Sellmeier）；N-SE-δ=×c_disp（灵敏度）；N-const=常数 n 基线（B10 对照，不入 Δt_disp 候选集） |
| `theta_prime`/`cos_theta_prime`/`theta_double_prime` | (2.1) | Snell 折射角（n_air=1） |
| `optical_path_difference`/`phase_delta` | (2.1)/(2.2) | Δ=2t√(n²−sin²θ)；δ=4π×1e-4·n(ν)·t·ν·cosθ′(ν)（色散逐点） |
| `phase_function` | (2.2) | g(ν)=n(ν)·ν·cosθ′(ν)（相位函数，g 空间恒定周期） |
| `fresnel_interface`/`interface_reflectivities`/`forward_reflectance` | (2.3)/(2.4) | s/p 振幅与强度反射率、两光束反射率正模型（s/p 平均） |
| **`poly_basis_cheb`** | (5.3)/§7 | 中心化/正交化多项式基（Chebyshev Vandomer：ν→[-1,1] 后 T_0..T_p），替代原始 ν^p 幂基 |
| **`vp_design_matrix`** | (5.4) | 基线-干涉分解设计矩阵 Φ(t)=[B(0..p), C(0..q)·cosδ, S(0..q)·sinδ] |
| **`vp_linear_ls`** | (5.5) | 固定 t 的加权线性 LS（lstsq），返回 β、RSS、秩、条件数 |
| **`variable_projection_scan`** | (5.6)/(5.7) | 一维 t 全局扫描；shared=True 两角共享 t（J(t)=ΣJ_k(t)），shared=False 每角独立；含抛物线精化、每角 t̂ 处 B/C/S 系数与干涉幅值 A=√(C²+S²) |
| **`nsub_from_amplitude`** | §7.3 | 由 A=2(1−R₁)√(R₁R₂) 反演 R₂→n̂_sub（brentq，弱可辨识） |
| **`profile_ci_from_Jcurve`** | §7.4 | 轮廓似然 95% CI（J(t) 曲率/夹逼区间；χ²_{0.95,1}·σ²） |
| **`two_angle_ftest_vp`** | (7.1) | 嵌套 F 检验 M_shared（共享 t）vs M_indep（每角独立 t，df1=1，df2=N_tot−n_params_indep） |
| `invert_from_spacing`/`invert_phase_method`/`thickness_from_phase_gap` | (6.1)/(6.2) | M3 常数 n 基线、M2 色散相位法（初值/交叉验证）；t=1e4/(2·Δg) |
| `invert_nls`/`invert_nls_multistart`/`invert_nls_indep` | §6.4 | 物理正模型 NLS（局部交叉校验，起点 t̂；M1-P1/P2） |
| `_airy_reflectance` | §7.6 | 多光束（Airy）反射率（B13 诊断） |

符号与全局符号表一致（t、n、n_sub、n_air、theta、theta_prime、nu、lambda、delta、m、delta_nu）；新增局部量 B、C、S、A、g、ρ（相位）、Δt_inv_band、F、p、q、Δg 不入全局符号表（formulation §11）。

## 4. 数据契约

### 4.1 输入

| 路径 | 内容 |
|---|---|
| `data/2025_cumcm_B/附件1.xlsx`（--config scenario.attachment1） | θ=10°，2 列 × 7469 行，列「波数 (cm-1)」「反射率 (%)」，ν 升序 |
| `data/2025_cumcm_B/附件2.xlsx`（--config scenario.attachment2） | θ=15°，同结构，ν 原为**降序**（读入后重排升序），反射率最大值 102.74%（B2 异常点） |
| `formulations/formulation_v003/parameters.yaml`（--input） | 参数登记权威来源：n_air、nu_c、nu_inv、reststrahlen_exclude、t_scan_range、t_scan_step、baseline_poly_deg、envelope_poly_deg、tau_* 等（代码核验一致性） |
| `code/data/n_ref_anchor.csv` | λ>5µm 色散代理锚点（见 §6.1，仅作 Δt_inv_band 背景） |
| `configs/task_config.yaml`（--config） | 附件路径、色散模型、反演谱段、扫描/容差、可靠性阈值 |
| 环境变量（worker 注入） | `AUTOMM_OUTPUT_DIR`、`AUTOMM_SEED`、`AUTOMM_TASK_ID` |

### 4.2 输出（`AUTOMM_OUTPUT_DIR`，即 `results/thickness_inversion_v003/`）

| 文件 | 内容 |
|---|---|
| `result.json` | `feasible_incumbent`（worker 读取）、共享 t 与每角 t、n_sub 幅度弱辨识、两角度一致性、可靠性判据汇总 |
| `solver_status.json` | 主 variable projection 扫描状态（t_root、t_refined、J_min、t_range/t_step/p/q、抽样 J 曲线）+ 物理正模型 NLS 交叉校验 |
| `verification.json` | 检查明细（checks：F 检验/色散/CI/异常点/多光束/n_sub 诊断）+ 公式引用 |
| `metadata.json` | 场景、种子、输入/配置 hash、单位约定、公式引用 |
| `preprocessing.json` | 预处理日志（异常点计数、Reststrahlen 剔除、**谱段截断 [2000,4000]**、归一化）+ 附件 SHA-256 |
| `dispersion_ref.json` | 所用色散模型 n(λ) 对照与锚点核验 + 基线/包络阶数 |
| `reflectance_theta10.csv`、`reflectance_theta15.csv` | 反演带内 nu, R_obs, R_model_best, weight（供可视化/归档） |

### 4.3 单位约定（parameters.yaml 一致）

t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[deg]（三角转 rad）、Δν[cm⁻¹]、δ[rad]、g[cm⁻¹]；R%→R/100 归一；(2.2) 的 1e-4 换算因子即 µm/cm 与 cm⁻¹ 的归一。

## 5. 数值方法与验证设计

- **数据预处理（B1–B3 + 谱段截断）**：`%→0-1` 归一；ν 升序重排（附件 2 降序）；Reststrahlen [700,1000] cm⁻¹ w=0；异常点（R%>100 或 <0）降权 w=0.05（附件 2 实测 262 点 >100%，附件 1 为 0）；**主反演谱段截断 ν∈[2000,4000]**（Sellmeier 已知区，v003 (3.1)）。原始数据只读。
- **色散 n(ν)（B6）**：主反演带内用 Sellmeier（L09）= 模型 **N-SE**；N-SE-δ（×c_disp，c_disp=1±0.5%）用于带内色散敏感性（§7.2）；N-const（n(5µm) 常数）作 M3 基线（不入 Δt_disp）。λ>5µm（ν<2000）锚点插值代理仅作 Δt_inv_band 全谱诊断背景。
- **主反演（v003 §5/§6，M1=主）**：**基线-干涉分解 + 一维相位频率扫描（variable projection）**。将 R_obs = B(ν) + C(ν)cosδ + S(ν)sinδ，B/C/S 用**中心化正交化 Chebyshev 多项式**（p=3/q=1，计算前固定）；对固定 t 解线性 LS（(5.5)），对 t 在 [t_lo,t_hi] 一维扫描（t_step≤0.01µm，默认 [3,20]）取 J(t) 全局最小（(5.6)/(5.7)），再做抛物线精化。**两角共享 t**（B/C/S 按角度独立、t 全局共享）。t 由干涉相位频率确定，与 n_sub 结构解耦（B7、B10 升级）。
- **n_sub 弱辨识（B7）**：由每个角度共享 t̂ 处的干涉幅值 A=√(C²+S²)（在参考波数 3000 cm⁻¹）按 A=2(1−R₁)√(R₁R₂) 反演 R₂→n̂_sub（brentq）；t 不依赖 n_sub，故 n_sub 弱可辨识不影响 t。
- **三方法/模型交叉验证**：M1-ind（每角独立 t，一致性检验 §7.1）、M1-P1/P2（物理正模型 NLS 局部交叉校验，起点 t̂，§6.4）、M2（色散相位法）、M3（常数 n 基线）、M4（Airy 多光束诊断）。
- **可靠性（§7）**：两角一致性＝对相位-频率拟合的嵌套 F 检验（M_shared vs M_indep，α=0.05，τ12=2% 作裸偏差报告/解释阈值）；色散敏感性 τ_disp=2%（带内 N-SE vs N-SE-δ，δ=0.5%）+ Δt_inv_band 报告；n_sub 解耦灵敏度诊断 τ_nsub_diag=3%（主方法 t 与 n_sub 解耦；物理正模型 NLS 交叉校验灵敏度）；噪声 CI＝**轮廓似然**（J(t) 曲率/夹逼区间，χ²_{0.95,1}·σ² 由 J 曲线求，τ_ci=2%；bootstrap 留 computation 备选，规避 v001 的 bootstrap 超时）；异常点 τ_anom=1%（剔除/降权/保留三策略，重跑主扫描）；多光束诊断（两光束 vs Airy 残差改善 >10% 则需修正）。
- **数学物理一致性**：基线阶数/带区稳健性已在 formulation §13.2 与接口探针核验（p=1..6 下 t 稳定）；t=1/(2×1e-4·Δg) 与 phase 函数关系一致。

## 6. 静态检查与探针结果（全部通过）

| 检查 | 结果 |
|---|---|
| `compileall` | passed |
| `ruff check`（E/F/I，line-length 120，pyproject 配置） | passed |
| `compute.py --help` | usage 正常 |
| `probe.py` / `compute.py --self-check`（27 项探针） | 27/27 passed（含 v002 既有项：Sellmeier n(5µm)=2.4954、Fischer n(25µm)=3.115 单调、带内 N-SE 退化纯 Sellmeier、N-SE-delta=×c_disp、N-const 基线常数、锚点插值无 NaN、正模型 R∈[0,1]、P2 联合往返反演、t–n_sub 解耦、独立 t 拟合、解析 CI 正性、异常点 >100% 标记、Reststrahlen 剔除；新增 **v003 项**：vp 带内纯 Sellmeier、**vp 变量投影往返恢复（shared 与 indep 两模式）**、**基线阶数稳健（p=1..6 t 稳定）**、**n_sub 由幅值弱辨识返回有限值**、**vp 轮廓似然 CI 为正**、**vp 两角嵌套 F 检验接受共享 t**） |
| `make_task_spec` 静态预检 | passed（compileall/ruff preflight；output 目录位于假设版本内；公式版本 formulation_v003＝accepted_formulation_version；backend local；timeout 1200s；task_id 预测 `30bedd3be5a2c9a36d3a`） |
| 小型合成谱端到端运维探针（见 §6.1） | 通过：t(shared vp)=7.3931µm 恢复 t_true=7.40（误差 <0.1%），t 每角 [7.3908,7.3955]，n_sub(amp)=2.606（目标 2.6）；6/6 判据通过、feasible_incumbent=true、输出全部 JSON/CSV 写入正确 |

### 6.1 实现阶段发现（供 sanity/computation 复核）

1. **主反演改用变量投影（核心）**：`formulation_v003 §5` 将主反演由"全谱幅值 NLS"改为"基线-干涉分解 + 一维相位频率扫描"。实现确认：t 只进入干涉相位频率 δ=4π×1e-4·t·g(ν)，B/C/S 用正交化多项式吸收 DC 基线/包络；固定 t 为线性 LS，一维扫描取全局最小。合成端到端探针按 v003 重建后，t 精确恢复且两角一致，直接消除 v002 的 M1=0.305µm、M2/M3=54–65µm 两数量级冲突。
2. **多项式基归一化（防绝对厚度对基敏感）**：`formula_validation §7` 强调绝对厚度对基线多项式基选择敏感（原始 ν^3 基 vs 中心化基）。实现采用**中心化+正交化 Chebyshev 基**（`poly_basis_cheb`，ν→[-1,1] 后 T_0..T_p），良态且与 formulation §13.2 的 t 稳定性一致；接口探针核验 p=1..6 下 t 稳定。
3. **t 与 n_sub 解耦（B7）**：主方法 t 由相位频率确定、不依赖 n_sub；n_sub 由共享 t̂ 处的干涉幅值 A=√(C²+S²) 事后弱辨识（brentq 反演 R₂→n̂_sub）。合成端到端探针 n̂_sub≈2.606（目标 2.6）；若正式 computation 中幅值信噪比过低（n_sub=None/触界），回退 P1/文献取值并记录 t 对 n_sub 的灵敏度（预期趋近 0）。
4. **噪声 CI 用轮廓似然（B12）**：由 J(t) 曲线 + J(t̂) 附近的曲率/夹逼区间求 95% CI（χ²_{0.95,1}·σ²，σ²=J(t̂)/(N_tot−n_params)），秒级、避免 v001/v002 的 bootstrap 超时与解析协方差在错误盆地上的失真；残差重采样 bootstrap 作为 computation 替代方案保留。
5. **Δt_inv_band / 色散敏感性在正确盆地量化**：在变量投影主方法（正确盆地）上重跑 N-SE vs N-SE-δ 与全谱 vs 截断，回应 v002 在错误盆地上的 15.11%/117.55% 失效造假象。
6. **Sellmeier 超界 NaN 防御**：dispersion_ref 的 n_sellmeier 仅对 λ≤5µm 计算（λ>5µm 置 None），避免 v001 曾出现的 Sellmeier 超界 NaN（既有 workflow warning）。

## 7. 追踪信息

| 项 | 值 |
|---|---|
| 假设版本 | assumption_v001（accepted） |
| 公式版本 | formulation_v003（accepted；parameters.yaml input_hash 见下） |
| 代码目录 hash | `ce9731d607b6860eef3020dd51558dc860b11bc668ee3a11614fec842abd6bc6`（hash_path = compute.py/model.py/probe.py/data/n_ref_anchor.csv） |
| 代码入口 hash（compute.py，= code_hash） | `3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e` |
| model.py hash | `fa3c3c0851824f62d69955f271d51a16086d190f1cb67e789358f07c0fdb36f9` |
| probe.py hash | `357d958a9c4480a45ee7a40ba2ad3dc9851a2d662b8f1697ecc8479d3ae2c551` |
| n_ref 锚点 hash | `de4f2595cdbfa3029736d144267e4beb97640fb3bd7195da752c4b74bfb0a7f5`（未改） |
| 任务配置源文件 hash | `ac0d477f961a0f2723242031fce236e6e2582192e3ea755e9cf6f3bdbd6853f7` |
| 任务配置合并 hash（tasks.py config_hash） | `c300447d45a46b0d9620b5984109e4e0d5cdd132b1b80ad1e9b0c7c9e8f24478` |
| 输入参数 hash（formulation_v003/parameters.yaml） | `8353356ddbb1f99b342dc4092467853cab083ca8e312369b9dfda605d28ab563` |
| 随机种子 | 20260829（AUTOMM_SEED 优先） |
| 输出目录 | `problems/2025-cumcm-b/prob02/versions/assumption_v001/results/thickness_inversion_v003` |
| 工作目录 | 项目根（.） |
| 任务 ID（预测，提交时以 tasks.py 实算为准） | `30bedd3be5a2c9a36d3a`（v003；与 v001 `0670bb687607edb7dd91`、v002 `1295103e6926a59e5ed2` 分离） |
| Python | 3.13.9（numpy 2.3.5、scipy 1.16.3、pandas 2.3.3、openpyxl、ruff 0.12.0） |

### 7.1 失败条件与路由

- 进程非零退出 → `code_runtime`：先用 compileall/ruff/探针复现，再决定重试或修订（可修复一次）；
- `result.json` 缺失或 `feasible_incumbent=false` → 反演/判据未通过：交由 sanity/降级路由（不盲目重跑）；若某可靠性判据超阈值，按 `quality_warning` 记录技术债（如色散敏感性 Δt_disp>2%），交 sanity/文献复核决定是否修订 formulation；
- 附件缺失或 SHA-256 与 `data/2025_cumcm_B/README.md` 不符 → `input_missing`，需人工/资源审批；
- 输出目录与 spec 不一致或输出锁冲突 → `harness_invariant`，人工对账。

## 8. 计算任务规格（computation 阶段提交）

唯一任务：`prob02-epitaxy-thickness`（详细字段见 `configs/task_spec.yaml`，formulation_version=formulation_v003，输出目录 `thickness_inversion_v003`）。

提交命令（Runner 以 sys.executable 替换 {python}）：

```
python scripts/compute_dispatcher.py submit --problem-id 2025-cumcm-b --question-id prob02 \
  --stage computation \
  --code-path problems/2025-cumcm-b/prob02/versions/assumption_v001/code/compute.py \
  --config-path problems/2025-cumcm-b/prob02/versions/assumption_v001/configs/task_config.yaml \
  --input-path problems/2025-cumcm-b/prob02/versions/assumption_v001/formulations/formulation_v003/parameters.yaml \
  --assumption-version assumption_v001 --formulation-version formulation_v003 \
  --output-directory problems/2025-cumcm-b/prob02/versions/assumption_v001/results/thickness_inversion_v003 \
  --working-directory . --timeout-seconds 1200 --seed 20260829 \
  -- {python} problems/2025-cumcm-b/prob02/versions/assumption_v001/code/compute.py \
     --config problems/2025-cumcm-b/prob02/versions/assumption_v001/configs/task_config.yaml \
     --input problems/2025-cumcm-b/prob02/versions/assumption_v001/formulations/formulation_v003/parameters.yaml \
     --output problems/2025-cumcm-b/prob02/versions/assumption_v001/results/thickness_inversion_v003
```

该规格已用 `make_task_spec` 静态校验通过（preflight：compileall/ruff passed；output 目录位于假设版本内；公式版本 formulation_v003 为 accepted；后端 local；timeout 1200s）。输出目录 `thickness_inversion_v003` 与 v001（`results/thickness_inversion`）、v002（`results/thickness_inversion_v002`）分离，避免覆盖旧结果。

## 9. 遗留与移交

- **λ>5µm 色散（B6，延续）**：主反演已截断至 ν≥2000，λ>5µm 色散不再直接决定 t̂；L26 全文 n/k 表与缺口区色散模型仍需文献复核，用于 §7.2 的 Δt_inv_band 报告与论文讨论。
- **n_sub（B7）**：本版 t 与 n_sub 解耦，t 由相位频率确定，n_sub 由幅值弱辨识；若幅值信噪比过低（n_sub 弱可辨识触界），回退 P1 并用文献取值（L26 4H/6H-SiC n、L30/L31 掺杂机制），并记录 t 对 n_sub 的灵敏度（预期趋近 0）。
- **多光束修正（B13）**：prob02 仅做诊断（两光束 vs Airy 残差改善阈值）；完整 Airy 推导与修正预留 prob03。
- **异常点 S_A 策略**：附件 2 超 100% 点按降权处理；若 computation 发现该策略对 t 影响超 τ_anom=1%，则复核策略（剔除/截断）并记录。
- **prob03（硅晶圆片 10°/15°，附件 3/4）**：本问未涉及硅（Si），其参数（n≈3.4、色散模型）与多光束必要性留 prob03。
- **v001/v002 computation 遗留**：v001（formulation_v001，`0670bb687607edb7dd91`）与 v002（formulation_v002，`1295103e6926a59e5ed2`）均因可靠性判据超阈/模型可辨识性结构缺陷判 NEEDS_REVISION；其结果为历史，留在各自结果目录，不覆盖。

（prob01 的探针/复现链路（compileall → ruff → --help → 探针 → make_task_spec preflight）全部复用。）
