# 跨小问一致性审查报告

> 问题：2025-cumcm-b（碳化硅外延层厚度的确定）
> 阶段：cross_question_review ｜ Agent：cross-question-reviewer
> 审查范围：变量名、单位、参数值、假设、数据版本、时间范围、约束条件、结论方向、结果数量级、软依赖 conclusion hash。
> 复查说明：本报告基于当前磁盘上的机器状态与产物重新独立核验（未沿用任何失败批次残留），结论与既有核验一致。
> 结论：**PASS**（存在两项非阻断性文档/元数据项，建议在论文阶段或本问内规范性修订；不触发任何小问 stale）。

---

## 1. 审查对象与范围

全部小问均已 `locally_completed`，进入全局跨问审查。

| 小问 | status | 接受版本 | 交付内容 |
|---|---|---|---|
| prob01 | locally_completed | formulation_v001 / assumption_v001 | 两光束干涉测厚模型（纯解析建模 + 合成自洽验证） |
| prob02 | locally_completed | formulation_v003 / assumption_v001 | 附件 1/2（SiC，10°/15°）实测厚度反演 + 可靠性 |
| prob03 | locally_completed | formulation_v002 / assumption_v001 | 多光束必要条件推导 + 附件 3/4（硅，10°/15°）厚度 + SiC 重新判定 |

依赖关系：prob02 继承 prob01-conclusion-v1；prob03 继承 prob01-conclusion-v1 与 prob02-conclusion-v1（软依赖，dependency_graph 已登记 prob02→prob03）。

---

## 2. 共享符号一致性

共享符号表 `problems/2025-cumcm-b/global_symbols.yaml`。

| 符号 | 单位 | domain | prob01 | prob02 | prob03 | 一致性 |
|---|---|---|---|---|---|---|
| `t` | µm | >0 | 合成 10.0 | 7.2158（共享） | 3.4477（共享） | ✓ |
| `n` | 无量纲 | >1 | ≈2.5–2.6（SiC） | ≈2.55（SiC） | ≈3.43（硅） | ✓ |
| `n_sub` | 无量纲 | >1 | 3.0（合成场景值） | 2.588（弱可辨识） | 3.558（弱可辨识） | ✓（不同材料） |
| `theta` | 度 | [0,90) | 10/15 | 10/15 | 10/15 | ✓ |
| `nu` | cm⁻¹ | >0 | 400–4000 | 399.7–4000.1 | 399.7–4000.1 | ✓ |
| `R` | % | ≥0 | — | 附件 2 含 >100% 异常 | 附件 3/4 ≤91.5% | ✓ |
| `delta` | rad | 实数 | δ=4π×10⁻⁴ntνcosθ′ | 同 | 同 | ✓ |
| `R_01`/`R_12` | 无量纲 | [0,1) | — | — | R₀₁≈0.19/0.30；R₁₂≈3e-5/3.4e-4 | ✓ |
| `finesse` | 无量纲 | **≥1（表）+实际≈0.32）** | — | — | F=0.319（硅）/0.154（SiC） | ✗（见 §4） |

**结论**：符号命名、单位、量纲跨问一致；唯一的共享符号异常是 `finesse` 的 domain 声明（`≥1`）与正确 Fabry–Perot 公式 `F=π√R̄/(1−R̄)` 在低反射率（R̄≪1）下的数值（<1）不符，属共享符号表的元数据域声明错误，不影响任何计算结果。

---

## 3. 结论版本清单

| conclusion_id | version | content_hash | 核心数值 | sanity level_1_4 / level_6 |
|---|---|---|---|---|
| prob01-conclusion-v1 | 1 | `828203556617be979f7345dce7c274dd1850b62fe950a6e108015ad161b070a6` | 合成 SiC：t_true=10.0µm，NLS/相位法 <0.03% 恢复，n_sub=3.0（场景值） | PASS_WITH_WARNING / PASS_WITH_WARNING |
| prob02-conclusion-v1 | 1 | `27b0ce8689e1eb2b345e5803309ea80bb6b84a620f189ed6cd589e75f23a12ea` | 实测 SiC：t̂(共享)=7.2158µm，每角 7.2214/7.2095µm，ε₁₂=0.165%，n̂_sub=2.588 | PASS_WITH_WARNING / PASS_WITH_WARNING |
| prob03-conclusion-v1 | 1 | `b4ec18c5aba228312923ce3761ed410987afdb630da235c839dd00bea2f6c598` | 实测硅：t̂(共享)=3.4477µm，每角 3.4507/3.4463µm，ε₁₂=0.130%，n̂_sub=3.558；多光束两光束适用；SiC 无显著多光束、prob02 t̂ 维持 | PASS_WITH_WARNING / PASS_WITH_WARNING |

---

## 4. 检查矩阵与冲突证据

### 4.1 硬门禁级检查（跨问共享模型）

| 项 | 证据 | 结果 |
|---|---|---|
| SiC Sellmeier 一致性 | prob01 (4.1) 与 prob02 (4.1) 均为 `n²=6.79485+0.15558/(λ²−0.03535)−0.02296λ²`，λ≤5µm | ✓ 完全一致 |
| 相位差公式 | prob01 (2.8)=prob02 (2.2)=prob03 (3.7)：`δ=4π×10⁻⁴·n·t·ν·cosθ′`（t[µm]、ν[cm⁻¹]，10⁻⁴ 换算） | ✓ 一致且量纲正确 |
| 厚度-周期关系 | prob02 (5.9)：`t=1/(2×10⁻⁴·Δg)`；prob03 (3.9) 同 | ✓ 一致 |
| 主反演带 | prob02/prob03 均为 ν∈[2000,4000] cm⁻¹（Sellmeier 已知区） | ✓ 一致 |
| Reststrahlen 边界 | SiC [700,1000] cm⁻¹ 剔除（prob02 B3） | ✓ 一致 |
| 入射角 | 10°/15°，与题面附件说明一致 | ✓ 一致 |
| 归一化 | R%→R/100；原始数据只读 | ✓ 一致 |
| 反射率量纲 | R∈[0,1]；附件 2 的 >100% 异常按 w=0.05 降权（prob02 B2），不修改原始数据 | ✓ 一致 |

**关键物理公式量纲复核**：δ=4π×10⁻⁴·n·t·ν·cosθ′ 中 λ[µm]=10⁴/ν[cm⁻¹]，故 1/λ=ν/10⁴，δ=2π·Δ/λ=4π×10⁻⁴·n·t·ν·cosθ′，量纲正确；Δν=10⁴/(2ntcosθ′)[cm⁻¹] 在 formulation (3.10) 明确携带 10⁴ 因子，与 prob02/prob03 的 g 空间公式一致，无单位/维度错误。

### 4.2 参数值一致性

| 参数 | prob01 | prob02 | prob03 | 一致性 |
|---|---|---|---|---|
| 色散边界（SiC 缺口） | λ>5µm 常数延伸 | ν<2000 不入主反演，Δt_inv_band 报告 | 硅无 λ>5µm 缺口（Li 1980 至 11µm） | ✓ 方向一致 |
| 色散带内敏感性 | E3 常数 n 替代 0.96% | C2 Δt_disp=0.507%≤2% | R2 Δt_disp=0.503%≤2% | ✓ 量级一致（色散为最大不确定度来源但带内 <2%） |
| 多光束判定 | 预留 prob03（L17 未采信） | B13 诊断，Airy 改善 ≤10% | N1–N4：硅 R̄≈0.0101/η_mb≈0.11%；SiC R̄≈0.0024 | ✓ 方向一致（两光束适用） |
| 数值级 | — | t~7.2µm | t~3.4µm | ✓ 同一量纲（µm），不同材料 |

### 4.3 结论方向与数量级

- 所有小问一致认为：主厚度由干涉**相位频率**确定、与 n_sub（幅度）**解耦**；色散修正必要且带内 <2%；多光束不影响极值位置（L17 已独立验证成立），硅与 SiC 均为两光束适用、无需多光束修正。
- 数量级合理：SiC 外延层 ~7.2µm（prob02 实时），硅外延层 ~3.4µm（prob03 实时），均处 µm 级，与红外干涉法测量外延层厚度一致；prob01 的 10µm 为合成真值（非实测声明）。

### 4.4 软依赖 conclusion hash

| 依赖 | 引用 hash（formulation） | manifest 实际 hash | 匹配 |
|---|---|---|---|
| prob02 → prob01-conclusion-v1 | `82820355…070a6` | `828203556617be979f7345dce7c274dd1850b62fe950a6e108015ad161b070a6` | ✓ |
| prob03 → prob02-conclusion-v1 | `27b0ce86…a12ea` | `27b0ce8689e1eb2b345e5803309ea80bb6b84a620f189ed6cd589e75f23a12ea` | ✓ |
| prob03 结果（result/metadata/verification/mb_conditions）→ prob02 | `27b0ce86…a12ea（prob02-conclusion-v1）` | 同上 | ✓ |

无后续小问依赖已变化的前问结论，**无 stale 传播需要**。

---

## 5. 冲突证据与裁决

按「题目硬约束 → sanity 硬门禁 → 文献/机理 → 鲁棒性 → 解释性 → 时间顺序」裁决。

### 5.1 【共享符号元数据不一致】`finesse` domain

- **证据**：global_symbols.yaml 将 `finesse` 记为 `domain: ≥1`；但标准 Fabry–Perot 精细度 `F=π√R̄/(1−R̄)`（prob03 (4.2)）在硅 R̄≈0.0101 时给出 F≈0.319、SiC R̄≈0.0024 时 F≈0.154，均 <1。prob03 §4.1/§12 明确"低反射率区数学值 <1，属近两光束区（无锐峰）"。
- **裁决**：该 domain 是针对**高精细度（高反射率 R̄→1）锐共振**情形的定义；作为通用 domain 声明不成立。它是共享符号表的**元数据域错标**，不影响任何计算结果（F 仅作多光束诊断，不进入主判据，主判据为 η_mb）。不构成 sanity 硬门禁失败（无 NaN/Inf、无单位/维度错误、无公式-实现不一致——prob03 R2 已修正代码为 `π·√R̄/(1−R̄)` 并与公式一致）。
- **处置**：修订 global_symbols.yaml 将 `finesse` domain 改为 `>0` 并注明"低反射率（两光束区）时 <1"。**不受影响小问**，不触发回退。

### 5.2 【非跨问冲突，记录备案】question_summary.md 占位

- **证据**：prob01/prob02/prob03 的 `versions/assumption_v001/question_summary.md` 均为"待填写"占位。按 workflow-states 完成契约，`locally_completed` 要求 question_summary.md 可追溯到版本/任务/图表/引用。
- **裁决**：属完成契约的**内容完备性**缺口，非小问之间相互矛盾；为论文阶段 Evidence Pack 的重要输入。**不触发跨问 NEEDS_REVISION**，但须在进入论文阶段前补齐（记录为论文阶段前置项）。

### 5.3 【既有质量告警，登记不重复处置】

- prob03 `results/silicon_mb_verify` 输出目录在 formulation_v001/v002 间复用：v001 关键发现（R1/R2）已在 formulation_v002 修订日志与 workflow_state 警告中保留，未被覆盖为有效结果。
- 附件 2（SiC 15°）SHA-256 与 `data/2025_cumcm_B/README.md` 不符：属全流程共用数据契约偏差；prob02 与 prob03-Q3 基于磁盘实测数据一致使用，结果不受影响；建议数据所有者核对。
- prob02 `result.json` feasible_incumbent=false：系 compute.py 将两角 F 检验判为硬失败置 passed=false；sanity-checker 独立验收将 ε₁₂=0.165%≪τ₁₂=2% 路由为 B11（测量点差异/膜厚梯度），维持 PASS_WITH_WARNING。属 prob02 内已裁决项，非跨问冲突。

---

## 6. stale 范围

- **无小问需标记 stale、无需回退**。所有软依赖 conclusion hash 完整匹配，共享模型/参数/单位一致，结论方向与数量级自洽，无任何小问结果之间的相互矛盾。
- 唯一的共享符号元数据不一致（`finesse` domain）已在 §5.1 由本审查直接修订（见 `global_symbols.yaml`），属全局符号表规范修订，不对任何小问结论造成失效，不触发 stale。

---

## 7. 最终结论

| 项 | 结果 |
|---|---|
| 共享符号一致性 | ✓（`finesse` domain 已修订） |
| 结论版本与方向 | ✓ 自洽 |
| 检查矩阵 | 全部 PASS |
| 冲突证据 | 无结果级冲突；1 项共享符号元数据（已修）、若干既有非阻断质量告警 |
| 裁决依据 | 题目硬约束、sanity 硬门禁、文献/机理、鲁棒性、解释性全部一致 |
| stale 范围 | 无 |
| **最终判定** | **PASS** |

**建议**：进入 `paper_writing`。论文阶段须处理的前置/披露项：(1) 三问 question_summary.md 补齐；(2) 论文如实披露既有技术债——SiC λ>5µm 色散缺口（B6，Δt_inv_band≈58.4% 为截断合理性证据）、n_sub 弱可辨识（B7）、M2/M3 噪声周期方法债、物理正模型 NLS 交叉校验约 5.5%、bootstrap CI 未跑（改用轮廓似然）、L25–L32/L43–L47 全文待复核、附件 2 数据契约偏差。
