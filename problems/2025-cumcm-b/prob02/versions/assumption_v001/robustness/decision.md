# prob02 robustness 适用性决定

> 阶段：robustness ｜ Agent：robustness-analyst ｜ 日期：2026-08-30
> 问题：2025-cumcm-b / prob02（碳化硅外延层厚度实测反演与可靠性分析，assumption_v001 / formulation_v003）

## 决定：适用（completed）

## 理由

1. **formulation_v003 §8.2 已把「鲁棒性」列为模型比较标准**：明确要求量化基线趋势（B 多项式阶数）、
   色散（N-SE/N-SE-δ）、n_sub（幅度弱辨识/解耦）、噪声、异常点、Reststrahlen 剔除、谱段截断对 t̂ 的影响。
   该标准在计算结果前固定，robustness 阶段必须执行。
2. **关键假设要求可靠性支撑**：B2（附件 2 反射率 >100% 异常点处理）、B3（Reststrahlen 区剔除）、
   B6（λ>5µm 色散缺口/谱段截断）、B7（n_sub 弱可辨识）、B11（两角度一致性）、B12（噪声/置信区间）、
   B13（多光束诊断）均指向不确定度与敏感性检验。
3. **formulation_v003 §7 已预注册判据**（计算前固定，不事后修改）：§7.1 两角嵌套 F 检验（α=0.05）+ε₁₂≤τ₁₂=2%、
   §7.2 色散敏感性 Δt_disp≤τ_d=2% +Δt_inv_band 报告、§7.3 n_sub 解耦灵敏度、§7.4 唯一性/置信区间
   CI 半宽≤τ_ci=2%、§7.5 异常点 Δt_anom≤τ_a=1%、§7.6 多光束诊断（Airy 改善 ≤10% 判定两光束适用）。
   这些判据在计算前登记于 parameters.yaml，正是「预注册的鲁棒性/稳定性判据」。
4. **workflow_state warnings 已登记多处未量化/待确认的不确定度**：λ>5µm 色散缺口（B6）、n_sub 弱可辨识（B7）、
   色散模型为厚度反演最大不确定度来源（延续 prob01 robustness E3）、两角一致性需解释（B11）。robustness
   阶段应给出这些不确定度对 t̂ 的**定量**影响与稳定性分级。

## 本阶段执行方式（与 §7 的关系）

本问的鲁棒性/敏感性检验已在 computation 阶段由 **formulation_v003 §7.1–§7.6** 作为**预注册判据**完整执行，
结果归档于 `results/thickness_inversion_v003/result.json`：6 项判据中 5 项直接在阈值内通过，
1 项（两角一致性嵌套 F 检验）统计显著但裸偏差 ε₁₂=0.165%≪τ₁₂=2%，按 formulation §7.1/§14 路由为
B11（测量点差异/膜厚梯度）记录并解释。robustness 阶段据此**复核并归纳**稳定性结论，无需另行启动
重复的敏感性计算任务，以免与 computation 阶段 §7 重复。

## 不适用部分（如实记录）

- **求解器/算法选择稳健性**：主反演为一维全局扫描 + 每点线性 LS（variable projection），非梯度/元启发式，
  无组合爆炸；§7.4 唯一性判据（全局极小 vs 次小候选高 1.75×）已含「偶然初始化/局部陷阱」检验，
  robustness 不再重复求解器/初值对比。
- **独立 bootstrap CI（B≥200）**：§7.4 采用轮廓似然/夹逼区间（SSE(t) 曲率）给出 CI，未运行重采样 bootstrap。
  作为方法债登记（见 preregistration §8 与 conclusion），留论文/后续小问讨论，不阻断（CI 半宽 0.091%≪2%）。

## 本阶段交付（robustness/ 目录）

- `decision.md`：本决定与理由
- `preregistration.md`：预注册方案（核心结论 + 稳定性判据 + 实验矩阵，判据计算前已固定）
- `experiment_matrix.yaml`：实验矩阵机器可读版本（映射 §7 判据与默认方案扰动）
- `conclusion.md`：robustness 稳定性结论与后续移交
