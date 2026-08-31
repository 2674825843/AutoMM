# prob03 ablation 适用性决定

> 阶段：ablation ｜ Agent：ablation-analyst ｜ 日期：2026-08-30
> 问题：2025-cumcm-b / prob03（外延层多光束干涉必要条件 + 硅片（附件3/4）多光束判定与厚度反演 + SiC 重新判定，
> assumption_v001 / formulation_v002）

## 决定：适用（completed）

## 理由

1. **模型存在可解释且可分离的公式项/算法模块/约束方向**：formulation_v002 的主反演（S1）
   为「基线-干涉分解 + 一维相位频率扫描（variable projection）」——由可分离的组件构成：
   - **色散项**：`n(ν)` 用硅 Sellmeier（(6.1)，N-SE），对应 `dispersion_epi_si(model=...)`；
   - **基线多项式项**：`B(ν)`（阶数 `p`，默认 3）吸收 DC 基线/慢变趋势，对应 `BASELINE_POLY_DEG`；
   - **包络多项式项**：`C(ν)/S(ν)`（阶数 `q`，默认 1）吸收干涉幅值 `A` 与相位 `φ`，对应 `ENVELOPE_POLY_DEG`；
   - **两角共享 t 约束**：`shared=True`（(7.5) 两角联合），对应 `variable_projection_scan(shared=...)`；
   - **多光束（Airy）模型项**：S2 判定模型（(3.6) Airy vs (3.8) 两光束）。
   这些组件可以单独替换/移除而不改变题目定义，满足 knowledge/robustness-ablation.md §消融设计的适用条件。

2. **REQUEST.md 质量标准要求复杂算法必要性证据**：「复杂算法必须有必要性、对比实验和可解释性」。
   prob03 的主反演含色散、基线多项式、包络多项式、两角共享 t 约束等建模复杂度；题面 Q1 明确要求
   「多光束干涉对厚度计算精度可能产生的影响」定量化——这些复杂度项是否真正贡献 `t̂` 与多光束判定结论，
   需要 ablative 证据。robustness 阶段已覆盖**输入/情景不确定性**（R1 两角一致性、R2 色散敏感性、
   R3 CI、R4 异常、R5 多光束、R6 n_sub、R7 窗口、R8 唯一性），但未检验**模型内部公式项/算法模块/约束的必要性**，
   二者互补。

3. **存在可检验的核心机制断言**：formulation §4.5/§8.1 的 L17「无吸收时 Airy 多光束极值位置不变、
   不影响厚度」是本问 Q1 的核心结论，且 robustness R5 只以 `η_mb≈0.11%`（残差改善率）佐证、未直接检验
   「Airy 高阶干涉项是否改变 `t̂`」。ablation 把该断言升级为预注册的定量证据：以**加 Airy 高阶谐波
   项的 VP** 对比两光束一阶 VP，检验多光束复杂度是否贡献 `t̂`。

## 消融方向（3–4 个公式项/算法模块/约束方向，与 robustness 不重复）

| 编号 | 消融对象 | 移除/替换操作 | 理论作用 | 预期方向 |
|---|---|---|---|---|
| F0 | 完整模型（对照） | 无 | S1 主反演：N-SE 色散 + 基线( p=3 ) + 包络( q=1 ) + 两角共享 t | t̂=3.4477 µm、加权 RMSE≈2.6e-3（f01 实测基准） |
| A1 | 色散项（(6.1) Sellmeier） | N-SE → N-const（常数 n=n(5µm)） | n(ν) 进入 δ(t) 相位频率与 g(ν) 周期，色散也用于打破周期歧义 | Δt 小（色散弱，Δn/n≈0.51%）；色散项非 t̂ 点估计的关键复杂度，但相关性需报告 |
| A2 | 多光束（Airy）高阶干涉项 | 两光束一阶 VP（cosδ/sinδ）→ 加 Airy 高阶谐波（cos2δ/sin2δ、cos3δ/sin3δ） | Airy (3.6) 含高阶反射（O(R̄^m)），其高次谐波是两光束模型未捕获的多光束复杂度 | Δt≈0（L17 极值不变性）→ 多光束复杂度不改变 t̂；Q1 定量证据 |
| A3 | 基线多项式项（B(ν)，p=3） | p=3 → p=0（仅常数 DC 基线） | B(ν) 吸收 DC/慢变基线，隔离干涉项 | t̂ 稳定（基线只改拟合残差、不改相位频率）；报告 RMSE 上升 |
| A4 | 两角共享 t 约束（(7.5)） | shared=True → False（每角独立 t） | 共享 t 是两角联合反演的一致性约束 | 每角独立 t̂ 与共享 t̂ 一致（ε12≈0.13%）；共享约束为安全约束、不强加偏差 |

## 不适用部分（如实记录）

- **求解器/算法族对比（VP vs NLS vs MILP）**：formulation §7.7 已论证本问为 1 维连续扫描 + 每点线性 LS
  的精确/确定性方法，无需离散/元启发式；ablation 不重复算法族对比。
- **外部 baseline**：本问为物理模型 + 可解性反演（无外部真值可比），按 ablation 约定以**完整模型为内部对照**，
  不要求外部 baseline；主反演 F0 以 computation 阶段对审定公式的忠实实现值（t̂=3.4477 µm）为基准。
- **真实噪声/异常点与数据预处理策略**：robustness R4/R7 已覆盖（硅片无 R%>100 异常、窗口敏感性 Δt_win=0.749%），
  ablation 不重复（异常点降权、谱段截断属鲁棒性/预处理，非模型组件必要性）。
- **SiC 重新判定（prob02 对照）**：robustness/R5、computation 已判 SiC `Rbar≈0.0024` 无显著多光束、
  无需修正；SiC 非本问主反演部件，ablation 不单独消融（其多光束必要性由 Q1 通用结论覆盖）。

## 本阶段交付（ablation/ 目录）

- `decision.md`：本决定与理由
- `preregistration.md`：预注册方案（核心结论 + 消融判据 + 实验矩阵，判据运行前固定）
- `experiment_matrix.yaml`：实验矩阵机器可读版本（与 `ablation.py PREREGISTERED` 一致）
- `code/ablation.py` + `configs/ablation_config.yaml`：消融实验代码与任务配置（复用已审定 model.py，不修改模型代码）
- 计算结果输出至 `results/ablation/`（隔离 task 运行，supervised worker 执行）；
  数值结果消费后登记 `ablation/conclusion.md` 与图表（后续唤醒完成，本动作仅提交任务，不提前登记 worker 尚未创建的产物）。
