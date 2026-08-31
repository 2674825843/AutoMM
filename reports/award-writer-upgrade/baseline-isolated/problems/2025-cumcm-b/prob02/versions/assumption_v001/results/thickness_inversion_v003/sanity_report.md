# Sanity Check Report

- problem_id: 2025-cumcm-b
- question_id: prob02
- assumption_version: assumption_v001
- formulation_version: formulation_v003
- overall: PASS_WITH_WARNING
- checked_at: 2026-08-29T18:37:00Z
- task_id: 30bedd3be5a2c9a36d3a
- action: inspect_compute_result（computation 终态验收 / Level 1–4）

> 检查对象：`results/thickness_inversion_v003/`（任务 `30bedd3be5a2c9a36d3a`，formulation_v003 / assumption_v001，seed=20260829）。
> 主结果：t̂(共享，variable projection)=**7.2158 µm**；每角 t̂=[7.2214 µm(10°), 7.2095 µm(15°)]，ε₁₂=0.165%；n̂_sub(幅值弱辨识)=2.588。
> 独立判据：**5/6 通过**，仅 `reliability_two_angle_ftest` 未达显著性接受（但裸偏差 ε₁₂=0.165% ≪ τ₁₂=2%）。

## Level 1：文件和运行完整性（PASS）

- 任务 `30bedd3be5a2c9a36d3a` status=succeeded、returncode=0、finished_at=2026-08-29T18:24:13Z；stdout/stderr 日志落盘完整（stderr 仅一行「未通过判据：reliability_two_angle_ftest」）。
- 输出齐全：result.json、solver_status.json、verification.json、metadata.json、preprocessing.json、dispersion_ref.json、reflectance_theta10.csv、reflectance_theta15.csv。
- 追踪 hash 链独立复现：用 `automm.common.hash_path` 复算 `code_hash=3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e`（compute.py，含相对路径前缀），与 task.json 及 implementation.md §7 完全一致；`config_hash=c300447d45a46b0d9620b5984109e4e0d5cdd132b1b80ad1e9b0c7c9e8f24478`、`input_hash=8353356ddbb1f99b342dc4092467853cab083ca8e312369b9dfda605d28ab563` 均一致。
- 输出目录 `thickness_inversion_v003` 与 v001（results/thickness_inversion）、v002（results/thickness_inversion_v002）分离，未覆盖旧结果；原始附件只读（preprocessing.json 登记 SHA-256）。

## Level 2：数值范围和约束（PASS）

- 机器级 L2-finite 检查：全部 8 个数值文件有限，无 NaN/Inf（machine_sanity.json，failures=[]）。
- 反射率守恒：模型与观测 R 均落在 [0,1]（R%/100 归一）；无硬约束违反。t̂∈[3,20] scanning 区间内。
- 主拟合残差优良：J_min_shared=0.0032474（两角 N_tot=8296）→ 加权 RMSE≈6.3×10⁻⁴（≈0.06% 反射率）。
- 预处理正确：附件1 无异常点（n_anomaly=0）、附件2 262 个 R%>100 异常点按 w=0.05 降权（不修改原始数据）；Reststrahlen [700,1000] cm⁻¹ 各剔除 623 点（w=0）；主反演谱段截断 ν∈[2000,4000]（n_points_inv_band_all_angles=8296）。
- 色散对照 `dispersion_ref.json` 对 λ>5µm（Sellmeier 超界）用 `null` 标记，未再出现 v001 的 NaN 缺陷；锚点 n(5µm)=2.4954、Fischer n(25µm)=3.1150 单调合理。

## Level 3：量纲和公式（PASS_WITH_WARNING）

- formula-代码逐条一致：(2.1) Snell、(2.2) 相位差 δ=4π×10⁻⁴ntν·cosθ′、(2.3)/(2.4) 两光束正模型、(3.1)/(3.2) 谱段截断与权重、(4.1) Sellmeier、(5.1)–(5.7) 基线-干涉分解与 variable projection、(5.8)/(5.9) 相位频率→厚度、(6.1)–(6.4) 极值/周期歧义与初值、(7.1)–(7.6) 可靠性；公式引用登记于 metadata.json `formula_refs`。
- 单位约定一致：t[µm]、ν[cm⁻¹]、λ[µm]=1e4/ν、θ[deg]（内部转 rad）、δ[rad]、g[cm⁻¹]、R 无量纲；(2.2) 的 1e-4 换算因子正确。与全局符号表及 parameters.yaml 无冲突。
- **独立交叉验证（只读数据探针）**：对附件1/2 在带 [2000,4000] 去基线后做 FFT 周期图，g 空间主峰周期 Δg≈657（10°）/698（15°）cm⁻¹ → t≈7.62/7.16 µm；ν 空间主峰周期 Δν≈247/263 cm⁻¹ → t≈7.95/7.48 µm。两参考系均指向 **t≈7.2–8.0 µm**，与主结果 t̂=7.216 µm 一致（在周期图分辨率内），证实主反演落到正确的物理周期。
- **警示（方法债，非主结果缺陷）**：M2/M3（色散相位法/间隔法）报告 t=54–65 µm（Δg_median≈80 cm⁻¹）。该值来自把「小幅噪声纹波」当成干涉极值（formulation §13.3：ν 空间约 30 cm⁻¹ 的极值间距为噪声周期），其在 g/ν 空间周期图主峰并不对应真实干涉周期；M2/M3 仅作初值/交叉验证，不构成对主结果 t̂=7.216 µm 的反证。formulation §0 声称「消除 M1/M2/M3 量级冲突」——本轮 M1 已回到正确盆地（7.216 vs v002 的 0.305），但 M2/M3 仍对噪声周期给出 54–65 µm，故该方法是已知/登记的方法债，应记录并在论文中说明（M2/M3 不适用，M1 为主交付）。

## Level 4：常识与文献合理性（PASS_WITH_WARNING）

- 物理量合理：t̂=7.216 µm 为 SiC 外延层厚度的合理量级；干涉条纹周期（FFT 证实 Δν≈250–270 cm⁻¹）与物理薄膜干涉测厚关系一致。
- n̂_sub=2.588 > n≈2.554（衬底折射率略高于外延层，方向正确，对应重掺杂衬底），弱对比度（R₂≈3×10⁻⁵，条纹对比度约 3–17%）与 B7 弱可辨识前提一致；n̂_sub 由干涉幅值 A=√(C²+S²)≈0.00387 反演得到。
- 色散：带内用 4H-SiC Sellmeier（L09，经 L11 数据页交叉核验），λ∈[2.5,5]µm 来源权威；λ>5µm（ν<2000）为色散缺口区，不进入主反演，仅有 Δt_inv_band=58.4% 作为谱段截断合理性证据（L26 全文 n/k 表待 literature 全文复核）。
- 无违反物理/经济常识之处；异常点（R%>100，B2）降权而非修改原始数据、Reststrahlen 区（B3）剔除，均符合两光束无吸收模型的适用边界（B13 多光束诊断证明两光束适用）。
- 技术债延续：L25–L32 关键来源为题名/摘要级核验（正文全文待复核）；λ>5µm 色散缺口（B6）；n_sub 数值弱可辨识（B7）；多光束完整 Airy 推导预留 prob03（B13）。

## Level 5：跨小问一致性（pending）

- 触发条件（所有小问 locally completed）未满足，留 prob01/prob02/prob03 完成后执行；本问单位/符号与全局约定、prob01-conclusion-v1 依赖一致（t、n、n_sub、θ、ν、λ、δ 复用全局符号表）。

## Level 6：鲁棒性和敏感性（本次即计算阶段可靠性）

- 六项可靠性判据 (§7.1–§7.6) 已在 computation 阶段执行：
  - reliability_two_angle_ftest：**FAIL（F=5.251 > F_crit=3.843，p=0.022，α=0.05）**，但裸偏差 **ε₁₂=0.165% ≪ τ₁₂=2%**。两角 t̂=[7.2214, 7.2095] µm 在 8000+ 样本下差异（约 0.012 µm）被 F 检验判为「统计显著」，属大样本下统计显著性与实际意义分离的典型情形；formulation §7.1/§14 明确：F 检验拒绝 H₀ 时判为**测量点差异/膜厚梯度（B11）**，记录并解释，而非模型修订。建议在结论中将此作为 B11 情形解释并报告 ε₁₂。
  - reliability_dispersion：**PASS**（Δt_disp=0.51% ≤ τ=2%；Δt_inv_band=58.4% 为谱段截断合理性报告项，v002 错误盆地的 117% 假象已消除）。
  - reliability_ci：**PASS**（轮廓似然 95% CI 半宽=0.091% ≤ τ=2%，t̂=7.2158[+0.091%/-0.091%] µm）。
  - reliability_anomaly：**PASS**（Δt_anom=0.0% ≤ τ=1%；降权/剔除/保留三策略结果一致，原始数据未改）。
  - reliability_nsub_diag：**DIAGNOSTIC（PASS）**（主方法 t 与 n_sub 结构解耦，主方法 t 对 n_sub 灵敏度 0%（main_t_nsub_delta_percent=0）；物理正模型 NLS 交叉校验灵敏度 1.92% ≤ τ=3% 诊断上限，B7 解耦成立）。
  - reliability_multibeam：**PASS**（Airy 相对两光束残差改善 0.0% ≤ 10%，无需多光束修正，B13 两光束适用）。
- 物理正模型 NLS 交叉校验（P1/P2）从主 t̂=7.216 起点局部拟合收敛到 P1 t=6.816 / P2 t=6.975 µm（RMSE≈0.009），与主方法相差约 5.5%。该差异来自物理正模型 (2.3) 用刚性 Fresnel DC 基线、未吸收带内慢变基线趋势（即 v002 根因一），而主方法 variable projection 用低阶多项式吸收基线并把 t 交给相位频率；故物理正模型 NLS 仅作交叉校验/诊断，其偏差记录为方法债（formulation §6.4），不构成对主结果 t̂ 的反证。主结果由 FFT 周期图与低残差拟合双重佐证。
- `feasible_incumbent`（task 字段）为 `false`，因 compute.py 把 `reliability_two_angle_ftest` 判为硬失败并置 `passed=false`；但 sanity-checker 独立验收判定：主结果 t̂=7.216 µm 可行、可追踪，F 检验为大样本下统计显著性与实际意义分离的 B11 可解释事项（formulation §7.1/§14 明确其路由），故本报告判 PASS_WITH_WARNING（主结果由 FFT 周期图与低残差拟合双重佐证，且所有曾超阈判据均已回到阈值内）。

## 路由

- overall: **PASS_WITH_WARNING**
- failure_type: null
- return_to_stage: null（推进，不修订）
- blocking_reasons: []
- 核心结论：formulation_v003 采用「基线-干涉分解 + 一维相位频率扫描（variable projection，两角共享 t）」，消除了 v001/v002 的模型可辨识性结构缺陷——此前超阈的判据全部回到阈值内（ε₁₂ 27.66%→0.165%、Δt_disp 15.11%→0.51%、n_sub 69%→解耦0%、CI 3.51%→0.091%、M1 0.305µm→7.216µm）。主结果 t̂=7.216 µm 由数据 FFT 周期图（Δg/Δν 均对应 t≈7.2–8 µm）与低残差拟合相互印证，物理、单位、质量守恒、文献与常识均成立。唯一「FAIL」的 F 检验是 8000+ 样本下统计显著性与实际意义分离的典型情形（ε₁₂=0.165%），formulation 已将其路由为 B11（测量点差异/膜厚梯度）记录并解释，不阻断推进。
- warnings（技术债，记录并移交后续阶段/论文）：
  - `reliability_two_angle_ftest` 以 F 检验拒绝共享 t（p=0.022，F=5.25），但 ε₁₂=0.165%≪2%；按 B11 解释为测量点差异/膜厚梯度并在结论中说明。
  - M2/M3（间隔/相位法）报告 t=54–65 µm，为噪声周期伪影（已知方法债），M1 为主交付；论文需说明 M2/M3 不适用性。
  - 物理正模型 NLS 交叉校验收敛到 6.8–7.0 µm（比主结果低约 5.5%），源于其刚性 Fresnel 基线未吸收带内慢变背景；主结果以 FFT 周期图+低残差佐证。
  - λ>5µm（ν<2000）色散缺口（B6）：Δt_inv_band=58.4% 作为谱段截断合理性证据，L26 全文 n/k 表待 literature 复核。
  - n_sub 弱可辨识（B7）：主方法解耦、t 不依赖 n_sub；n̂_sub=2.588 为幅值弱辨识值，文献取值待复核。
  - L25–L32 关键来源为题名/摘要级核验（正文全文待复核）。
  - 多光束（Airy）完整推导与修正预留 prob03；本问仅诊断。
  - 本次为 sanity 验收结论，未改动 computation 结果、formulation/assumption 历史文件。
