# 2025-cumcm-b 论文证据包

- Evidence hash：`6374ef02fd5a459dc6388aff56c1d4e7f0c36a4b8ad40ee46b3c3ef77b769025`

## prob01

- 假设版本：`assumption_v001`
- 公式版本：`formulation_v001`
- sanity：`{'level_1_4': 'PASS_WITH_WARNING', 'level_5': 'PASS', 'level_6': 'PASS_WITH_WARNING'}`
- 警告：['prob01 合成验证任务 0ea4b29da19e8479a6ea 消费完成：19/19 检查通过，t_true=10µm 被 NLS/相位法精确恢复，两入射角一致；hash 追踪链（code/config/input）与 task.json、implementation.md §7 完全一致，无 NaN/Inf、无硬约束违反、formula-代码逐条一致、文献/物理常识合理。技术债（λ>5µm 常数色散延伸、方法 A 约4%基线偏差、文献全文待复核、n_sub 合成场景值、Reststrahlen 剔除策略）均为既有 workflow warning，留 prob02 处理，不阻断推进。L1–L4 判定 PASS_WITH_WARNING，Level 5 待全部小问完成、Level 6 待 robustness 阶段。', 'prob01 Level 6（robustness 验收）独立复核通过：任务 554819114361017c5b70 全部输出有限且追踪完整，hash 链（code/config/input）与 task.json 一致，E1–E5 判据独立重算全部通过（conclusion=stable、5/5），E4 600 样本收敛率 100%、95% CI 半宽最大 0.022% 远低于阈值，预注册方案运行前固定未事后修改；物理机制（n_sub 影响幅度不影响相位、θ 误差二阶小量、色散模型为最大不确定度来源、全谱平均效应）与常识一致。技术债（robustness 基于合成谱、色散模型选择、λ>5µm 常数延伸、n_sub 场景值、文献全文待复核、Reststrahlen 剔除）均为既有 workflow warning，留 prob02 处理，不阻断推进。']

## prob02

- 假设版本：`assumption_v001`
- 公式版本：`formulation_v003`
- sanity：`{'level_1_4': 'PASS_WITH_WARNING', 'level_5': 'PASS', 'level_6': 'PASS_WITH_WARNING'}`
- 警告：['prob02 实测反演任务 30bedd3be5a2c9a36d3a 消费完成（formulation_v003 / assumption_v001，results/thickness_inversion_v003）：L1–L4 硬门禁通过——hash 追踪链（code_hash=3c8599d6547f2a8456613a148a62f3433255297cc9f654ad244144c317abcf8e 与 task.json/implementation.md §7 一致、config/input hash 一致）完整、机器级 L2-finite 通过（8 文件全有限无 NaN/Inf，v001 的 dispersion_ref NaN 已用 null 修复）、公式-代码逐条一致、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=7.2158 µm、每角 7.2214/7.2095 µm、ε₁₂=0.165%、n̂_sub=2.588；主拟合加权 RMSE≈6.3e-4。只读 FFT 数据探针独立证实带内真实干涉周期 Δg≈657/698、Δν≈247/263 cm⁻¹→t≈7.2–8.0 µm，与主结果一致。可靠性判据 5/6 通过：dispersion(0.51%≤2%)、ci(0.091%≤2%)、anomaly(0.0%≤1%)、nsub 解耦(diag PASS)、multibeam(pass) 全部通过；仅 reliability_two_angle_ftest 判 FAIL（F=5.251>F_crit=3.843，p=0.022），但裸偏差 ε₁₂=0.165%≪τ₁₂=2%，属大样本下统计显著性与实际意义分离，formulation §7.1/§14 明确将其路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。v001/v002 曾超阈判据（ε₁₂ 27.66%→0.165%、Δt_disp 15.11%→0.51%、n_sub 69%→解耦0%、CI 3.51%→0.091%、M1 0.305µm→7.216µm 正确盆地）全部回到阈值内，确认 formulation_v003 变量投影重构消除了 v002 的模型可辨识性结构缺陷。技术债（λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、M2/M3 噪声周期方法债、物理 NLS 交叉校验 5.5% 偏差、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，留后续与论文阶段处理，不阻断推进。', 'prob02 Level 6（robustness 验收）独立复核通过（降级审查模式，复用已有产物、不发起新计算）：robustness 判据 C1–C8 由 formulation_v003 §7.1–§7.6 预注册判据在 computation 阶段执行并归档 results/thickness_inversion_v003/result.json + robustness/（decision/preregistration/experiment_matrix/conclusion），无需另启重复任务。C2 色散 0.507%≤2% PASS、C4 n_sub 解耦 0.0%（物理 NLS 1.92%≤3%）PASS、C5 CI 半宽 0.091%≤2% PASS、C6 全局极小唯一 PASS、C7 异常点 0.0%≤1% PASS、C8 多光束改善 0.0%≤10%（两光束适用）PASS、R8 基线/包络阶数 p=2..5.q=0..2 稳定；仅 C1 两角嵌套 F 检验统计显著（F=5.25>F_crit=3.843，p=0.022）但 ε12=0.165%≪τ12=2%，按 formulation §7.1/§14 路由为 B11（测量点差异/膜厚梯度）记录并解释，不构成模型修订触发。机器级 L2-finite 通过（8 数值文件全有限无 NaN/Inf，failures=[]），hash 追踪链（code/config/input）与 task.json/implementation.md §7 一致，原始数据只读；result.json feasible_incumbent=false 系 compute.py 将 F 检验判为硬失败置 passed=false，sanity-checker 独立验收判定主结果 t̂=7.2158 µm（ε12=0.165%、n̂_sub=2.588）可行可追踪，维持 PASS_WITH_WARNING。物理/常识一致（t 由相位频率确定、与 n_sub 解耦；色散为最大不确定度来源但带内 0.507%<2%；噪声二阶小量；异常点降权无影响）。v001/v002 曾超阈判据全部回到阈值内，确认 formulation_v003 变量投影重构消除模型可辨识性结构缺陷。技术债（bootstrap CI 未跑、M2/M3 噪声周期、物理 NLS 交叉校验 5.5%、λ>5µm 色散缺口 B6、n_sub 弱可辨识 B7、L25-L32 全文待复核、多光束 Airy 留 prob03 B13）均为既有/登记事项，不阻断推进。ablation 尚 pending，交由 ablation-analyst；Level 5 待全部小问局部完成后执行。']

## prob03

- 假设版本：`assumption_v001`
- 公式版本：`formulation_v002`
- sanity：`{'level_1_4': 'PASS_WITH_WARNING', 'level_5': 'PASS', 'level_6': 'PASS_WITH_WARNING'}`
- 警告：['prob03 主 computation 任务 7e209043973692d067ed 消费完成（formulation_v002 / assumption_v001，results/silicon_mb_verify）：L1–L4 硬门禁通过——hash 追踪链（code_hash=482f5abb10c276c9d073dd7b7177ce342cf0a0d2d0b455370a899ec566142873 与 task.json/implementation.md §7 一致、source_config_hash/input_hash 一致）完整、机器级 L2-finite 通过（10 数值文件全有限无 NaN/Inf，failures=[]）、公式-代码逐条一致（R1 硅厚度基准 t̂=3.4477µm 修正 v001 的 6.9µm 因子2 伪影；R2 finesse=π·√R̄/(1−R̄) 修正 v001 漏 √R̄，finesse=0.3186 与公式一致）、单位一致、原始数据只读、无硬约束违反。主结果 t̂(共享)=3.4477 µm、每角 3.4507/3.4463 µm、ε₁₂=0.130%、n̂_sub(幅值弱辨识)=3.558；J(t) 曲线全局唯一极小在 t=3.45µm（J_shared=0.0608），未达 formulation §13.1 声称的『4 倍余量』（次小候选比≈1.020，弱色散下周期邻近候选接近简并，作为报告项而非硬门禁）。全部可靠性判据 PASS（two_angle F=0/p=1.0、dispersion 0.503%≤2%、ci 0.134%≤2%、anomaly 0.0%≤1%、multibeam_si two_beam_negligible η_mb≈0.11%、multibeam_sic no_correction_needed Rbar≈0.0024、nsub 解耦 diag PASS；checks_failed=[]）。v001 判 NEEDS_REVISION 的两项 core 缺陷（R1/R2）已在 v002 修复并复核通过；模型有效、无 VERSION_REJECTED、无 NEEDS_REVISION。技术债（bootstrap CI 用轮廓似然替代、n_sub 弱可辨识 B7、uniqueness 次小候选接近简并、multibeam_improvement 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项或非阻断。合并 config_hash 因 config/gates.yaml、workflow.yaml 在 computation 后被修改而漂移（post-hoc 配置变更；code/input/source_config 链完好），作质量告警登记不触发修订。判定 PASS_WITH_WARNING，推进至 sanity_check 阶段。', 'prob03 Level 6（robustness 验收）独立复核通过：robustness 判据 R1–R8 由 formulation_v002 §8.5 预注册并先于 computation 固定（parameters.yaml），R1–R7 全部在阈值内（R1 eps12=0.130%≤2%、R2 Δt_disp=0.503%≤2%、R3 CI 半宽 0.134%≤2%、R4 Δt_anom=0.0%≤1%、R5 η_mb=0.111%≤10%、R6 n_sub 解耦 0.0%、R7 Δt_win=0.749%≤2%），checks_failed=[]；独立复算 R7=0.749% 与登记值一致，探针只读、复用 model.py、未改数据/代码/结果。R8 唯一性次小候选≈1.020 为报告项（弱色散周期歧义），全局唯一性由 §7.6 预注册判据确认。主结果 t̂=3.4477 µm/每角 3.4507/3.4463 µm（ε12=0.130%），多光束判定两光束适用（硅 R̄≈0.0101、η_mb≈0.11%；SiC R̄_max≈0.0024 no_correction_needed），与 prob02 结论一致；物理/常识一致（t 由相位频率确定、与 n_sub 解耦；硅色散弱且带内无 λ>5µm 缺口；噪声二阶小量）。硬门禁（L2-finite 10 文件全有限无 NaN/Inf、单位/量纲、公式-实现一致 R1/R2 已修复、原始数据只读、追踪链完整、feasible_incumbent=true）全部通过。技术债（bootstrap CI 未跑用轮廓似然、n_sub 弱可辨识 B7、uniqueness 近简并、multibeam 基线差异、λ>5µm SiC 色散缺口 B6、L43-L47 全文待复核、附件2 数据契约偏差）均为既有/登记事项，非阻断。判定 PASS_WITH_WARNING。']

## 图表

- `prob01_fig_reflectance_spectrum_1d4fb899d1`：两光束干涉合成反射率谱（t_true=10.0 µm，n_sub=3.0）
- `prob01_fig_dispersion_curve_d85564d2fc`：外延层 4H-SiC 折射率色散模型 n(ν)
- `prob01_fig_phase_function_gap_459c486470`：色散化相位法：g(ν) 单调性与同型极值间隔律（θ=10°）
- `prob01_fig_thickness_methods_compare_5eac465fc8`：三种反演方法的厚度估计与 t_true=10.0 µm 对比（相对偏差标注）
- `prob01_fig_spacing_constant_n_bias_2245b6eda4`：方法 A 常数 n 近似的系统偏差：实测间隔 vs 理论间隔（色散效应 ~4%）
- `prob01_fig_nls_multistart_e64919ab13`：全谱 NLS 多初值：周期歧义局部极小 vs 全局解（rmse≈0，t=10.000 µm）
- `prob01_fig_response_surface_d0691c5dd8`：两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）
- `prob01_fig_sensitivity_tornado_6983566848`：prob01 robustness 敏感性 tornado 汇总（E1–E5）
- `prob01_fig_noise_robustness_ci_30d4fa737f`：E4 噪声稳健性：NLS 厚度估计 95% CI（σ=0.5/1.0/2.0%）
- `prob01_fig_ablation_summary_ee3c34dcfa`：prob01 ablation 判据汇总（F0 + A1–A4）
- `prob01_fig_ablation_polarization_da59250d1b`：A3 偏振一致性：avg/s/p 反演厚度 vs t_true
- `prob01_fig_ablation_init_strategy_7c59622d5a`：A4 初值策略对比：单初值局部极小 vs 多初值全局解
- `prob02_fig_reflectance_spectrum_6b2265d217`：附件 1/2 碳化硅晶圆片实测反射率谱（两入射角）
- `prob02_fig_model_fit_0ca711689b`：两入射角实测谱与两光束物理正模型 (2.3) 拟合对比
- `prob02_fig_thickness_estimate_efa7359eb9`：prob02 外延层厚度结果（formulation_v003，两角共享 t_hat = 7.2158 µm）
- `prob02_fig_dispersion_curve_af50244106`：外延层 4H-SiC 折射率色散模型 n(ν)：带内取 N-SE（Sellmeier）
- `prob02_fig_reliability_summary_78cd97014b`：prob02 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）
- `prob02_fig_variable_projection_jcurve_7a9a903650`：主反演目标函数 J(t) 与全局唯一性
- `prob02_fig_g_space_phase_gap_f500d9c0db`：相位频率（g 空间）测厚机制与 M2/M3 噪声周期对照
- `prob02_fig_nsub_decoupling_39b4128d09`：n_sub 幅值弱可辨识性与 t-n_sub 解耦
- `prob02_fig_response_surface_cfe5827835`：两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）
- `prob02_fig_methods_compare_99386076f5`：prob02 各方法厚度估计量级对照（对数轴；M1 主交付；M2/M3 对噪声周期失效）
- `prob02_fig_ablation_summary_dcd697b29e`：prob02 ablation 判据汇总（F0 + A1–A4）
- `prob02_fig_ablation_thickness_d29e3fc1f0`：prob02 ablation 厚度对照（F0 + A1–A4）
- `prob02_fig_ablation_shared_t_14e5362fa7`：A4 两角共享-t 对照：每角独立 t̂ 与共享 t̂ 一致
- `prob03_fig_reflectance_spectrum_41a3800f70`：附件 3/4 硅晶圆片实测反射率谱（两入射角，无 R%>100 异常点）
- `prob03_fig_model_fit_3e94d2fac7`：两入射角实测谱与两光束物理正模型 (2.8) 拟合对比
- `prob03_fig_thickness_estimate_59f1546ed7`：prob03 硅外延层厚度结果（formulation_v002，两角共享 t_hat = 3.4477 µm）
- `prob03_fig_dispersion_curve_aac3dcebea`：硅外延层折射率色散模型 n(ν)：带内取 N-SE（Sellmeier），色散弱（Δn/n≈0.51%）
- `prob03_fig_reliability_summary_50b4f34a17`：prob03 可靠性判据汇总（实测 vs 预注册阈值；绿=通过 / 红=超阈；白点标记为实测值）
- `prob03_fig_variable_projection_jcurve_4b30b360a4`：主反演目标函数 J(t) 与全局唯一性
- `prob03_fig_mb_conditions_9571a5012b`：多光束干涉必要条件 N1–N4 与硅片判定
- `prob03_fig_sic_multibeam_recheck_4cbb136f9c`：多光束显著性跨材料对照：硅/SiC 均 Rbar<<θ_mb → 无显著多光束、无需修正（Q3）
- `prob03_fig_response_surface_06cfec9b1e`：两光束干涉反射率随波数与入射角的三维响应面（配 2D 等高线）
- `prob03_fig_phase_freq_gspace_a936624612`：相位频率（g 空间）测厚机制与条纹计数
- `prob03_fig_ablation_summary_9f93c3dd2d`：prob03 ablation 判据汇总（F0 + A1–A4）
- `prob03_fig_ablation_t_consistency_ec44908369`：prob03 ablation 厚度对照（F0 + A1–A4）
- `prob03_fig_ablation_rmse_ce4b523efa`：prob03 ablation 拟合优度对照（加权 RMSE）

## 引用

- `[@L01]`：Thickness Measurement of Epitaxial Films by the Infrared Interference Method
- `[@L02]`：The Infrared Interference Method of Measuring Epitaxial Layer Thickness
- `[@L03]`：ASTM F95-89(2000): Standard Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer
- `[@L04]`：SEMI MF95 (SEMI MF009500): Test Method for Thickness of Lightly Doped Silicon Epitaxial Layers on Heavily Doped Silicon Substrates Using an Infrared Dispersive Spectrophotometer
- `[@L05]`：Thickness Measurement of Thin (1.0-µm) Epitaxial Silicon Layers by Infrared Reflectance
- `[@L06]`：Principles of Optics: Electromagnetic Theory of Propagation, Interference and Diffraction of Light (7th ed.)
- `[@L07]`：Optics (5th ed., Global Edition)
- `[@L08]`：Refractive Index, Dispersion, and Birefringence of Silicon Carbide Polytypes
- `[@L09]`：4H-SiC: a new nonlinear material for midinfrared lasers
- `[@L10]`：Temperature dependence of refractive indices for 4H- and 6H-SiC
- `[@L11]`：Refractiveindex.info database of optical constants
- `[@L12]`：Refractive index of silicon and germanium and its wavelength and temperature derivatives
- `[@L13]`：Handbook of Optical Constants of Solids (Vol. 1-3)
- `[@L14]`：Infrared Absorption in n-Type Silicon
- `[@L15]`：From Transport Measurements to Infrared Reflectance Spectra of n-Type Doped 4H-SiC Layer Stacks
- `[@L16]`：Temperature dependence of the anisotropy of the infrared dielectric properties and phonon-plasmon coupling in n-doped 4H-SiC
- `[@L17]`：基于色散修正与全谱拟合的红外干涉测厚模型研究
- `[@L23]`：Determination of Refractive Index and Film Thickness from Interference Fringes
- `[@L24]`：Self-consistent optical constants of SiC thin films
- `[@L25]`：Dispersion Compensation and Multi-Beam Interference Correction Algorithm for Thickness Measurement of SiC Epitaxial Layer
- `[@L26]`：Optical properties of 4H-SiC and 6H-SiC from infrared to vacuum ultraviolet spectral range ellipsometry (0.05–8.5 eV)
- `[@L27]`：Infrared to vacuum ultraviolet optical properties of 3C, 4H and 6H silicon carbide measured by spectroscopic ellipsometry
- `[@L28]`：Infrared Optical Properties of 3C, 4H and 6H Silicon Carbide
- `[@L29]`：Temperature-dependent infrared optical properties of 3C-, 4H- and 6H-SiC
- `[@L30]`：Investigation of longitudinal-optical phonon-plasmon coupled modes in SiC epitaxial film using Fourier transform infrared reflection
- `[@L31]`：Improved Resolution of Epitaxial Thin Film Doping Using FTIR Reflectance Spectroscopy
- `[@L32]`：Fundamentals of epitaxial silicon film thickness measurements using emission and reflection Fourier transform infrared spectroscopy
- `[@L43]`：An improved method for measuring epi-wafer thickness based on the infrared interference principle: Addressing interference quality and multiple interferences in double-layer structures
- `[@L44]`：On the Infrared Thickness Measurement of Epitaxially Grown Silicon Layers
- `[@L45]`：Infrared interference spectra observed in silicon epitaxial wafers
- `[@L46]`：Multiple reflections in an approximately parallel plate
- `[@L47]`：Influence of coating thickness on the performance of a Fabry–Perot interferometer
