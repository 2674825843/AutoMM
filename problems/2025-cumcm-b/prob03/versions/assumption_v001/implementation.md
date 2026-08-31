# prob03 实现计划（implementation.md）

> 版本：assumption_v001 / formulation_v002 ｜ 阶段：implementation ｜ Agent：implementation-agent
> 问题：2025 高教社杯 B 题问题 3 ——（1）推导光波在外延层界面与衬底界面多次反射、透射产生**多光束干涉的必要条件**（N1–N4）及其对厚度精度的影响（并独立验证 L17「多光束不改变极值位置」）；（2）判定硅片（附件3=10°/附件4=15°）**是否出现显著多光束**，给出硅外延层厚度模型/算法/结果；（3）SiC（附件1/2，prob02 对照）**是否需多光束修正**。
> 本问为**物理模型 + 可解性反演**（非优化问题）。实现内容 = 模型代码（**硅 Sellmeier + 一般 Airy 多光束正模型 + 必要条件 N1–N4 + 基线-干涉分解的一维相位频率扫描（variable projection，复用 prob02 方法族）** + 两光束 vs Airy 残差改善率判定）+ 硅片反演流水线 + SiC 重新判定 + 任务规格。
> 本版为 **formulation_v002 的实现**（继承 assumption_v001）。v002 相对 v001 的两处必改勘误（sanity NEEDS_REVISION）已落实：(**R1**) 硅厚度基准由 v001 伪影 6.9 µm 更正为对审定公式的忠实实现值 **t̂≈3.4477 µm**（共享）/3.4507、3.4463 µm（每角），ε₁₂=0.130%；(**R2**) 精细度公式统一为 **F=π√R̄/(1−R̄)**（v001 模型代码 `π·R̄/(1−R̄)` 漏 √R̄ 为 bug，0.032 应为 ≈0.319），对应 `model.py` 已修正。
> 主方法 S1（硅厚度）＝**基线-干涉分解 + 一维相位频率扫描（variable projection，两角共享 t）**；多光束判定 S2＝**两光束 (2.8) vs Airy (2.6) 全谱残差改善率 η_mb**；SiC 仅作只读量级复核（§7.3/§13.5）。

## 1. 实现目标

1. 将 formulation_v002 的硅片多光束判定 + 厚度反演链路实现为可复现 Python 代码：数据预处理（C6/C8：硅透明谱段 [2000,4000]、多声子带剔除、异常点降权）→ **主反演（基线-干涉分解 + 一维相位频率扫描，variable projection，两角共享 t）** → **多光束必要条件 N1–N4 + η_mb 判定** → SiC 只读重新判定 → 可靠性（两角一致性/带内色散/轮廓似然 CI/异常点）。
2. 复用 prob01/prob02 的两光束正模型与色散链路（Fresnel、相位、Snell、variable projection），针对硅（Sellmeier，L12/L13）与多光束（Airy (2.6)）修正；t 由干涉相位频率确定、与 n_sub 结构解耦；n_sub 由幅值 A=√(C²+S²) 事后弱辨识。
3. 完成静态检查（compileall、ruff、CLI `--help`、接口探针 27/27、make_task_spec 预检）并登记全部追踪信息；
4. 交付 computation 阶段可直接提交的任务规格（configs/task_spec.yaml，输出目录 `results/silicon_mb_verify`）。

不运行完整数据集、不运行正式任务（由 Runner/tasks.py 在 computation 阶段创建 supervised worker 任务）；实现阶段仅做秒级接口探针 + 只读数据契约核验（见 §6.1）。

## 2. 代码结构

```
problems/2025-cumcm-b/prob03/versions/assumption_v001/
├── code/
│   ├── model.py            # 核心模型与反演（无副作用，可 import；含 run_probes）
│   ├── compute.py          # CLI 入口：硅片反演 + 多光束判定 + SiC 重新判定 + 输出证据 JSON/CSV
│   └── probe.py            # 接口探针入口（秒级）
├── configs/
│   ├── task_config.yaml    # 计算任务执行配置（附件路径/谱段截断/扫描/多光束/可靠性设置）
│   └── task_spec.yaml      # 计算任务规格（computation 阶段提交依据）
└── implementation.md       # 本文件
```

## 3. 公式映射（model.py / compute.py 函数 ↔ formulation_v002 公式）

| 函数 | 公式 | 说明 |
|---|---|---|
| `sellmeier_si` | (5.1) | 硅 Sellmeier（L12/L13），n²=1+10.6684293λ²/(λ²−0.301516485²)+0.0030434748λ²/(λ²−1.13475115²)+1.54133408λ²/(λ²−1104.0²)，λ≤11µm |
| `dispersion_epi_si`(N-SE/N-SE-delta/N-const) | §5.1 | 硅色散：N-SE 主（Sellmeier）、N-SE-δ=×c_disp（灵敏度）、N-const=常数 n 基线（S5 对照）。硅无 λ>5µm 缺口（Sellmeier 全程有效） |
| `sellmeier_n4hsi`/`dispersion_epi_sic` | prob02 (4.1) | 4H-SiC Sellmeier（L09）；仅用于 SiC §7.3 重新判定 |
| `theta_prime`/`cos_theta_prime`/`theta_double_prime` | (2.1) | Snell 折射角（n_air=1） |
| `optical_path_difference`/`phase_delta`/`phase_function` | (2.7)/(2.9) | δ=4π×1e-4·n(ν)·t·ν·cosθ′；g(ν)=n·ν·cosθ′（相位函数，g 空间恒定周期 Δg=1/(2×1e-4·t)） |
| `fresnel_interface`/`interface_reflectivities`/`forward_reflectance` | (2.2)–(2.4)/(2.8) | s/p 振幅与强度反射率、两光束反射率正模型（s/p 平均） |
| **`airy_reflectance`** | (2.5)/(2.6) | 一般 Airy 多光束反射率（强度式，R=(R01+R12+2√(R01R12)cosδ)/(1+R01R12+2√(R01R12)cosδ)，与两光束 (2.8) 同极值位置、仅差对比度/峰形/DC） |
| **`interface_reflectivity_product`** | §3.1/§7.2 | R01、R12、Rbar=√(R01R12)、finesse=π√R̄/(1−R̄) |
| **`r12_from_amplitude`/`nsub_from_amplitude`** | §3.1/§7.2 | 由幅值 A=2(1−R01)√(R01R12) 反演 R12→n̂_sub（brentq，弱可辨识） |
| **`coherence_order_limit`** | (3.3)/(3.4) | N2：L_c≈1/(2Δν_res)，m_max^coh=⌊L_c/(2n t cosθ′)⌋ |
| **`parallelism_angle_bound`** | (3.5) | N3：α≪λ/(2nD cosθ′)（返回允许最大楔角 rad/度） |
| **`absorption_order_limit`** | (3.6) | N4：κ=4πkνt cosθ′，m_max^abs=⌊1/κ⌋ |
| **`necessary_conditions`** | §3.6 | N1–N4 汇总判定（标准+阈值+正交性） |
| **`poly_basis_cheb`** | (6.3) | 中心化/正交化多项式基（Chebyshev Vandomer：ν→[-1,1] 后 T_0..T_p） |
| **`vp_design_matrix`/`vp_linear_ls`** | (6.4) | 基线-干涉分解设计矩阵 Φ(t)=[B(0..p), C(0..q)·cosδ, S(0..q)·sinδ]；固定 t 加权线性 LS |
| **`variable_projection_scan`** | (6.5) | 一维 t 全局扫描；shared=True 两角共享 t，shared=False 每角独立；含抛物线精化、每角 t̂ 处 B/C/S 系数与干涉幅值 A=√(C²+S²) |
| **`profile_ci_from_Jcurve`** | §7.5 | 轮廓似然 95% CI（J(t) 曲率/夹逼区间；χ²_{0.95,1}·σ²） |
| **`two_angle_ftest_vp`** | §7.2 | 嵌套 F 检验 M_shared（共享 t）vs M_indep（每角独立 t，df1=1，df2=N_tot−n_params_indep） |
| **`multibeam_improvement`** | §7.1/(7.2) | Airy (2.6) vs 两光束 (2.8) 全谱残差改善率 η_mb=(SSE_2b−SSE_Airy)/SSE_2b×100% |
| `_sanitize`/`sha256_file`/`load_yaml` | — | 输出 JSON 序列化、文件哈希、配置加载 |

符号与全局符号表一致（t、n、n_sub、n_air、theta、theta_prime、nu、lambda、delta、m、delta_nu）；新增局部量 B、C、S、A、g、φ、η_mb、θ_mb、τ_mb、Rbar、finesse、m_max、κ、α、Δt_amb 不入全局符号表（formulation §11）。

## 4. 数据契约

### 4.1 输入

| 路径 | 内容 |
|---|---|
| `data/2025_cumcm_B/附件3.xlsx`（--config scenario.attachment_si10） | 硅，θ=10°，2 列 × 7469 行，列「波数 (cm-1)」「反射率 (%)」，ν 升序 |
| `data/2025_cumcm_B/附件4.xlsx`（--config scenario.attachment_si15） | 硅，θ=15°，同结构（均无 R%>100 异常点，区别于 SiC 附件2） |
| `data/2025_cumcm_B/附件1.xlsx`（--config scenario.attachment_sic10） | SiC，θ=10°（Q3 重新判定，prob02 复用） |
| `data/2025_cumcm_B/附件2.xlsx`（--config scenario.attachment_sic15） | SiC，θ=15°（Q3 重新判定） |
| `formulations/formulation_v002/parameters.yaml`（--input） | 参数登记权威来源：nu_inv_si、theta_mb、tau_mb、t_scan_range、t_scan_step、baseline_poly_deg、envelope_poly_deg、tau_* 等（代码核验一致性） |
| `configs/task_config.yaml`（--config） | 附件路径、色散模型、反演谱段、扫描/容差、多光束/可靠性阈值 |
| 环境变量（worker 注入） | `AUTOMM_OUTPUT_DIR`、`AUTOMM_SEED`、`AUTOMM_TASK_ID` |

### 4.2 输出（`AUTOMM_OUTPUT_DIR`，即 `results/silicon_mb_verify/`）

| 文件 | 内容 |
|---|---|
| `result.json` | `feasible_incumbent`（worker 读取）、硅厚度（共享+每角）、n_sub 幅度弱辨识、多光束判定（Si/SiC）、可靠性判据汇总 |
| `solver_status.json` | 主 variable projection 扫描状态（t_root、t_refined、J_min、t_range/t_step/p/q、抽样 J 曲线） |
| `verification.json` | 检查明细（checks：两角一致性/色散/CI/异常点/多光束（Si/SiC）/n_sub 诊断）+ 公式引用 |
| `metadata.json` | 场景、种子、输入/配置 hash、单位约定、公式引用 |
| `preprocessing.json` | 预处理日志（硅透明谱段截断 [2000,4000]、多声子带剔除、异常点计数、SiC 对照）+ 附件 SHA-256 |
| `dispersion_ref.json` | 硅/碳化硅 Sellmeier n(λ) 对照 + 基线/包络阶数 |
| `mb_conditions.json` | 多光束必要条件 N1–N4 数值 + η_mb + SiC 重新判定 |
| `reflectance_theta10.csv`、`reflectance_theta15.csv` | 硅反演带内 nu, R_obs, R_model_best, weight |

### 4.3 单位约定（parameters.yaml 一致）

t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[deg]（三角转 rad）、Δν[cm⁻¹]、δ[rad]、g[cm⁻¹]、Rbar 无量纲；R%→R/100 归一；(2.7) 的 1e-4 换算因子即 µm/cm 与 cm⁻¹ 的归一。

## 5. 数值方法与验证设计

- **数据预处理（C6/C8）**：`%→0-1` 归一；ν 升序重排；硅多声子吸收带 [400,1600] cm⁻¹（C8）w=0（模型不适用）；异常点（R%>100 或 <0）降权 w=0.05（硅片附件 3/4 实测 0 个 >100%，策略沿用为鲁棒）；**硅主反演谱段截断 ν∈[2000,4000]**（透明窗，Sellmeier 全程有效）。原始数据只读。
- **色散 n(ν)（C7/C8）**：硅主模型 **N-SE**（Sellmeier L12/L13）；N-SE-δ（×c_disp，c_disp=1±0.5%）用于带内色散敏感性（§7.2）；N-const（n(5µm) 常数，S5 基线，不入 Δt_disp 候选集）。硅 **无** λ>5µm 色散缺口（与 SiC 不同，L12/L13 在主反演带全程有效）。SiC 用 prob02 4H-SiC Sellmeier（L09）。**实测反演谱段 [2000,4000]**。
- **主反演（S1，§6/M1=主）**：**基线-干涉分解 + 一维相位频率扫描（variable projection）**。R_obs = B(ν) + C(ν)cosδ + S(ν)sinδ，δ=4π×1e-4·t·g(ν)，B/C/S 用**中心化正交化 Chebyshev 多项式**（p=3/q=1，计算前固定）；对固定 t 解线性 LS，对 t 在 [t_lo,t_hi] 一维扫描取 J(t) 全局最小，抛物线精化。**两角共享 t**（B/C/S 按角度独立、t 全局共享）。t 由干涉相位频率确定、与 n_sub 结构解耦。
- **多光束必要条件（S2 判定，§3/§7）**：N1——Rbar=√(R01R12)≤θ_mb=0.05 或 η_mb≤τ_mb=10%（**主判据**）；N2——L_c≈1e4µm ≫ 单程 OPD≈47µm（m_max^coh≈437≫2）；N3——α≪λ/(2nDcosθ′)≈0.003°；N4——硅透明窗 k≈0（m_max^abs 极大）。Airy (2.6) vs 两光束 (2.8) 全谱残差改善率 η_mb（§7.2）。**n_sub 由幅值 A=√(C²+S²) 弱辨识**（brentq 反演 R2→n̂_sub）。
- **SiC 重新判定（Q3，§7.3/§13.5）**：在 prob02 的 t̂=7.2158µm 处对附件1/2 做**只读固定 t 的基线-干涉分解**（不重新求解厚度），取干涉幅值反演 R12→Rbar=√(R01·R12)，确认 ≤θ_mb（实测 Rbar≈0.0024，prob02 对照 R12≈3.2e-5）。
- **可靠性（§7.2/§7.5）**：两角一致性＝对相位-频率拟合的嵌套 F 检验（α=0.05，τ12=2% 作裸偏差报告/解释阈值）；带内色散敏感性 τ_disp=2%（N-SE vs N-SE-δ，δ=0.5%）；噪声 CI＝轮廓似然（J(t) 曲线，χ²_{0.95,1}·σ²，τ_ci=2%）；异常点 τ_anom=1%（剔除/降权/保留三策略重跑主扫描）；多光束（Airy vs 两光束 η_mb≤τ_mb）。
- **数学物理一致性**：基线阶数/带区稳健性已在接口探针核验（p=1..6 下 t 稳定）；t=1/(2×1e-4·Δg) 与相位函数关系一致；Airy↔两光束极限（Rbar→0）与极值位置不变性（L17）已在接口探针核验。

## 6. 静态检查与探针结果（全部通过）

| 检查 | 结果 |
|---|---|
| `compileall` | passed |
| `ruff check`（E/F/I，line-length 120，pyproject 配置） | passed |
| `compute.py --help` | usage 正常 |
| `compute.py --self-check` / `probe.py`（27 项探针） | 27/27 passed（含：硅 Sellmeier n(5µm)≈3.4221、n(3.333µm)≈3.4293、n(2.5µm)≈3.4394；SiC Sellmeier n(5µm)≈2.4954；色散 N-SE/N-SE-δ/N-const；Airy↔两光束极限（Rbar→0 → RMS|ΔR| 小，n_sub→n_epi 越小）；**Airy 极值位置不变性 L17（δ=mπ 处为极值，与 R01·R12 无关）**；必要条件 N1–N4 判据；**R2 finesse=π√R̄/(1−R̄)（Rbar≈0.0101 → ≈0.319，v001 bug 0.032 已修正）**；变量投影往返（shared/indep，恢复 t=3.45µm 正确盆地）；基线阶数稳健 p=1..6；n_sub 幅值弱辨识；轮廓似然 CI 为正；两角嵌套 F 检验接受共享 t；多光束改善率 η_mb 小；SiC R̄≤θ_mb） |
| `make_task_spec` 静态预检 | passed（compileall/ruff preflight；output 目录位于假设版本内；公式版本 formulation_v002 为 accepted（question_manifest accepted_formulation_version=2）；backend local；timeout 1200s；task_id 预测 `7e209043973692d067ed`） |
| 只读数据契约/量级复核（见 §6.1） | 通过：SiC 附件1/2 在 prob02 t̂ 处只读复核 Rbar≈0.0024≤θ_mb（no_correction_needed）；硅片附件3/4 主反演 t̂≈3.4477µm（见 §6.1 关键发现） |

### 6.1 实现阶段发现（供 sanity/computation 复核；其中一项为**关键**，已由 formulation_v002 修正）

1. **【关键发现·已由 formulation_v002-R1 修正】硅片厚度基准：formulation_v001 §13.1 的探针值 t̂≈6.9µm 与文档公式/实测数据不一致，实为 t̂≈3.45µm。** 本文档忠实实现审定公式 (2.7)/(6.1)–(6.5)（δ=4π×1e-4·n·t·ν·cosθ′、variable projection、中心化 Chebyshev 基），对附件3/4 主反演得 **t̂≈3.4477（10°）/3.4463（15°）µm**，两角一致（ε12≈0.13%），拟合加权 RMSE≈2.57e-3。多重独立验证确认 3.45µm 为正确值：
   - **干涉条纹计数**：数据在 [2000,4000] 仅 4 个极大/5 个极小；t=3.45µm 的 δ 在带内扫约 30 rad（≈4.8 个周期，对应 4–5 个极大），而 t=6.9µm 扫约 60 rad（≈9.5 个周期，应 9–10 个极大）——t=6.9 会预测过多的干涉条纹，与数据不符。
   - **直接条纹间距测量**：带内同型极大间距 Δν≈432 cm⁻¹、极小间距≈424 cm⁻¹，由 t=1/(2×1e-4·n·cosθ′·Δν) 得 **t≈3.4 µm**（一致）。
   - **RMSE 数值互换**：formulation §13.1 报告「t≈6.9 → RMSE 2.58e-3；t≈3.55 → RMSE 1.11e-2（高 4 倍）」；本文档按文档公式计算机实为「t≈3.45 → RMSE 2.575e-3；t≈6.9 → RMSE 1.11e-2」——**RMSE 值完全相同，t 标签互换**，即 §13.1 探针存在因子 2 的相位频率/标签伪影（把 half-period 当作 whole-period，或 t 公式差因子 2）。
   - **影响**：prob03 硅片主结果应为 **t̂≈3.45µm**（非公式 §13.1 的 6.9µm）。formulation_v002（R1）已将该基准更正为 t̂=3.4477µm 并复核 §13.2/§13.4 相关探针值，本实现与之一致，不再触发 formulation-实现不一致硬门禁；computation 正式 t̂ 以实测数据为准。
2. **多光束判定**：即便 t 基准更正为 3.45µm，硅片多光束判定结论不变——N1 Rbar≈0.0101≤θ_mb、η_mb≈0.11%≪τ_mb=10%（两光束充分）；SiC Rbar≈0.0024≤θ_mb（无需修正）。L17 极值不变性独立验证成立（δ=mπ，与 R01·R12 无关）。
3. **多项式基归一化（防绝对厚度对基敏感）**：采用中心化+正交化 Chebyshev 基（ν→[-1,1] 后 T_0..T_p），良态；接口探针核验 p=1..6 下 t 稳定。
4. **t 与 n_sub 解耦**：主方法 t 由相位频率确定、不依赖 n_sub；n_sub 由共享 t̂ 处干涉幅值 A=√(C²+S²) 事后弱辨识（实测 n̂_sub≈3.56，弱可辨识，与公式 §5.2 范围 3.5–3.7 一致）。若正式 computation 中幅值信噪比过低（n_sub=None/触界），回退文献取值（L12/L13 高掺硅）并记录 t 对 n_sub 灵敏度（预期趋近 0）。
5. **噪声 CI 用轮廓似然**：由 J(t) 曲线求 95% CI（χ²_{0.95,1}·σ²），秒级、避免 bootstrap 超时（B12）；残差重采样 bootstrap 作为 computation 备选保留。
6. **Airy 相位约定一致性**：`airy_reflectance` 用**强度式** (2.6)（R01/R12 为正强度反射率、+cosδ），与两光束 (2.8) 同极值位置、仅差对比度/峰形/DC 基线——避免 prob02 曾直接把带符号 Fresnel 振幅代入的 π 相位跳变带来的反相伪影（该伪影会在强对比度硅片上把 Airy 与两光束误判为反相）。

## 7. 追踪信息

| 项 | 值 |
|---|---|
| 假设版本 | assumption_v001（accepted） |
| 公式版本 | formulation_v002（accepted；parameters.yaml input_hash 见下） |
| 代码入口 hash（compute.py，= code_hash） | `482f5abb10c276c9d073dd7b7177ce342cf0a0d2d0b455370a899ec566142873` |
| model.py hash | `1a04f2509f5fbb2b7a4114ba3678d636e606cc529df55d2939c753fa7e1664f2` |
| probe.py hash | `33843aa9489349180951a3f431b13d54c9de191c0108df5b890a7dc404f4b127` |
| 任务配置源文件 hash（task_config.yaml） | `1b44bfb13cdb4cbb6ed75ea19de0915238d7f14cf57751c3afb1bf05ca8bbbd2` |
| 任务配置合并 hash（tasks.py config_hash） | `8cbd2e89a4c7bafa3f2264aecd52c311998332c4a85051c56fb54327e92aa676` |
| 输入参数 hash（formulation_v002/parameters.yaml） | `bff09b1f0d37e5c9acdb18d4432266277115c10db400116fc2fb9c62c9cc78f7` |
| 随机种子 | 20260830（AUTOMM_SEED 优先） |
| 输出目录 | `problems/2025-cumcm-b/prob03/versions/assumption_v001/results/silicon_mb_verify` |
| 工作目录 | 项目根（.） |
| 任务 ID（预测，提交时以 tasks.py 实算为准） | `7e209043973692d067ed`（formulation_v002、finesse/model/compute/config/params 修正所致；首次 fc633110c86bfd0aeec2→f1c4e3ed425ff6b0e73f 为历史计划变更）。上一有效 computation 任务（f1c4e3ed425ff6b0e73f，formulation_v001）结果目录 results/silicon_mb_verify 予以保留，新任务以 7e209043… 提交至同一输出目录。 |
| Python | 3.13.9（numpy 2.3.5、scipy 1.16.3、pandas 2.3.3、openpyxl、ruff 0.12.0） |

### 7.1 失败条件与路由

- 进程非零退出 → `code_runtime`：先用 compileall/ruff/探针复现，再决定重试或修订（可修复一次）；
- `result.json` 缺失或 `feasible_incumbent=false` → 反演/判据未通过：交由 sanity/降级路由（不盲目重跑）；若某可靠性判据超阈值，按 `quality_warning` 记录技术债（如色散敏感性 Δt_disp>2%），交 sanity/文献复核决定是否修订 formulation；
- **t̂ 探针（formulation_v002）**：本实现与 formulation_v002（R1：硅厚度基准 t̂≈3.4477µm）一致；若 computation 正式 t̂ 与 formulation_v002 显著不一致，交由 sanity-checker 对照原文/数据仲裁（质量告警，非 Harness invariant / 非硬门禁）；若 sanity 判定 formulation 仍需修订，按 failure_class 路由至 formulation（不直接人工阻塞）；
- **finesse（formulation_v002-R2）**：model.py 已修正为 `finesse=π√R̄/(1−R̄)`（v001 漏 √R̄ 为 bug），与 formulation (3.2) 一致；若 sanity 复核仍发现 formula-代码不一致，按 `formula_boundary_dimension_solvability` 路由；
- 附件缺失或 SHA-256 与 `data/2025_cumcm_B/README.md` 不符 → `input_missing`，需人工/资源审批；
- 输出目录与 spec 不一致或输出锁冲突 → `harness_invariant`，人工对账。

### 7.2 computation_repair 记录（formulation_v002 / assumption_v001）

- **【已修复·formula_修正】v002 必改勘误落实**：(R1) 硅厚度基准由 v001 伪影 6.9 µm 更正为对审定公式的忠实实现值 t̂≈3.4477 µm（共享）/3.4507、3.4463 µm（每角），ε₁₂=0.130%；(R2) model.py 的 `finesse=π·R̄/(1−R̄)` 修正为 `finesse=π·√R̄/(1−R̄)`（`interface_reflectivity_product` 与 `necessary_conditions` 两处；v001 漏 √R̄ 为 bug：Rbar≈0.035→0.032 应得 ≈0.319）。对应代码/配置改动造成 code/model.py、probe.py、task_config.yaml source_config_hash、formulation_v002/parameters.yaml input_hash 变化。
- **【历史·code_runtime·已修】v001 首启 compute 任务（fc633110c86bfd0aeec2）在 `load_yaml(--input)` 处抛 `yaml.parser.ParserError` 并以非零退出**（parameters.yaml 的 `domain: "[0, 1)"（…）` 双引号提前闭合、残留未引用的全角括注 → 残缺标量）。已按原文语义修复为 `domain: "[0, 1)（…）"`（只校正引号靠位，**不改**数值/公式/单位/语义）。v002 的 parameters.yaml 不再含该问题。
- 修复验证（v002）：`compileall`/`ruff` 通过、`compute.py --help` 正常、`probe.py --self-check` 27/27 通过、`make_task_spec` 静态预检通过（task_id 预测 7e209043973692d067ed，code/config/input hash 与上表一致）。
- **code_hash（compute.py）已更新为 482f5abb…**（本次改动 compute.py 的 formulation 版本引用与 metadada 登记，改为 formulation_v002）；model.py/probe.py/task_config.yaml/formulation_v002 parameters.yaml 均更新。formulation_v002 的 computation 由资源管理在下次唤醒提交新任务（task_id=7e209043973692d067ed），原 results/silicon_mb_verify（v001）结果保留。

## 8. 计算任务规格（computation 阶段提交）

唯一任务：`prob03-silicon-multibeam-thickness`（详细字段见 `configs/task_spec.yaml`，formulation_version=formulation_v002，输出目录 `silicon_mb_verify`）。

提交命令（Runner 以 sys.executable 替换 {python}）：

```
python scripts/compute_dispatcher.py submit --problem-id 2025-cumcm-b --question-id prob03 \
  --stage computation \
  --code-path problems/2025-cumcm-b/prob03/versions/assumption_v001/code/compute.py \
  --config-path problems/2025-cumcm-b/prob03/versions/assumption_v001/configs/task_config.yaml \
  --input-path problems/2025-cumcm-b/prob03/versions/assumption_v001/formulations/formulation_v002/parameters.yaml \
  --assumption-version assumption_v001 --formulation-version formulation_v002 \
  --output-directory problems/2025-cumcm-b/prob03/versions/assumption_v001/results/silicon_mb_verify \
  --working-directory . --timeout-seconds 1200 --seed 20260830 \
  -- {python} problems/2025-cumcm-b/prob03/versions/assumption_v001/code/compute.py \
     --config problems/2025-cumcm-b/prob03/versions/assumption_v001/configs/task_config.yaml \
     --input problems/2025-cumcm-b/prob03/versions/assumption_v001/formulations/formulation_v002/parameters.yaml \
     --output problems/2025-cumcm-b/prob03/versions/assumption_v001/results/silicon_mb_verify
```

该规格已用 `make_task_spec` 静态校验通过（preflight：compileall/ruff passed；output 目录位于假设版本内；公式版本 formulation_v002 为 accepted；后端 local；timeout 1200s；task_id 预测 7e209043973692d067ed）。输出目录 `silicon_mb_verify` 为 prob03 首个 computation 结果（v001 计算结果保留，新任务以同样输出目录归档 v002 结果）。

## 9. 遗留与移交

- **硅片厚度基准（已由 formulation_v002-R1 解决）**：本实现按审定公式得 t̂≈3.45µm；formulation_v002 已将该基准更正为 t̂=3.4477µm（R1），配方 §13.1 的 6.9µm 伪影。computation 正式 t̂ 以**实测数据**（干涉条纹计数/间距）为准，sanity/论文阶段对照原文与数据复核。
- **finesse（已由 formulation_v002-R2 解决）**：model.py 已统一为 `finesse=π√R̄/(1−R̄)`，与 formulation (3.2) 一致；computation 输出 finesse≈0.319（硅）、≈0.154（SiC）。
- **n_sub（硅，C7）**：n̂_sub≈3.56 为幅值弱可辨识值，与 t 解耦；文献取值（L12/L13、L45 掺杂机制）待全文复核，必要时回退并记录 t 对 n_sub 灵敏度（预期趋近 0）。
- **多光束修正（§7.4）**：本版硅（Rbar≈0.0101、η_mb≈0.11%）与 SiC（Rbar≈0.0024）均判定两光束适用，不触发 Airy 修正；若 computation 发现任意样品 η_mb>τ_mb，启用 §7.4 并记录 t 位移（预期≈0，验证 §3.5 极值不变性）。
- **硅色散/谱段（C8）**：主带 [2000,4000] 为保守选取（多声子带边缘 1500 cm⁻¹ 附近剔除/降权边界）；computation 用残差谱诊断边界，若 ν<2000 吸收/色散已可忽略可扩展，否则保留截断并记录。
- **L17**：本实现独立验证为成立（§3.5，δ=mπ 与 R01·R12 无关），可作为后续结论依据；但吸收场景不适用（已标注 C5/§3.5）。
- **SiC 对照（C17）**：本实现用 prob02 t̂=7.2158µm 做只读复核（Rbar≈0.0024≤θ_mb，no_correction_needed），依赖 prob02-conclusion-v1（content_hash 27b0ce…）；若其变化，prob03 置 stale 并重审（dependency_graph 已登记 prob02→prob03 依赖）。
- **L43–L47 全文**：多为元数据/摘要级核验，定量参数（硅 Sellmeier 系数、n_sub 值）需在论文/文献复核阶段对照原文复核后方可用于定量主张（延续既有 workflow warning）。

（prob02 的正模型/Fresnel/variable projection/编译→探针→make_task_spec 链路全部复用。）
