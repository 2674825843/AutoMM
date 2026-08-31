# prob03 robustness 适用性决定

> 阶段：robustness ｜ Agent：robustness-analyst ｜ 日期：2026-08-30
> 问题：2025-cumcm-b / prob03（外延层多光束干涉必要条件 + 硅片（附件3/4）多光束判定与厚度反演 + SiC 重新判定，
> assumption_v001 / formulation_v002）

## 决定：适用（completed）

## 理由

1. **formulation_v002 §8.5 已把「鲁棒性」明确列为模型比较标准并预注册判据**：§8.5 列出 R1–R8
   可靠性/稳健性判据（两角一致性、带内色散、噪声/CI、异常点、多光束、n_sub 解耦、谱段窗口、唯一性），
   阈值在计算前登记于 `parameters.yaml`（tau_12=2%、tau_disp=2%、tau_ci=2%、tau_anom=1%、tau_mb=10%、
   theta_mb=0.05、tau_nsub_diag=3%）。该标准在 computation 前固定，robustness 阶段必须执行并验收。
2. **关键假设要求可靠性支撑**：B2（异常点/数据契约）、B5（相位）、B6（色散缺口/谱段截断）、
   B7（n_sub 弱可辨识）、B11（两角一致性）、B13（多光束）均指向不确定度与敏感性检验。
3. **evidence 链条要求**：题目要求「多光束干涉对厚度计算精度的影响」定量化（Q1）、硅片多光束判定须由数据给出
   （Q2）、SiC 重新判定（Q3）。这些依赖 R1–R8 对 t̂ 的稳定性分级——robustness 阶段给出定量影响与分级。
4. **workflow_state warnings 已登记未量化/待确认的不确定度**：uniqueness 次小候选接近简并（≈1.020）、
   n_sub 弱可辨识（B7，n̂_sub≈3.558）、bootstrap CI 未跑（用轮廓似然）、multibeam_improvement 基线差异。
   robustness 阶段应给出这些因素对 t̂（≈3.4477 µm）的定量影响与稳定性分级。

## 本阶段执行方式（与 §8.5 的关系）

本问的鲁棒性/敏感性判据（R1–R6、R8）已在 computation 阶段由 **formulation_v002 §8.5** 作为**预注册判据**
完整执行，结果归档 `results/silicon_mb_verify/result.json`：全部定量判据在阈值内通过。
仅 **R7（硅谱段窗口敏感性）** 在 formulation §8.5 登记为「预注册、computation 实测」但未在 compute.py 单独执行
（result.json 无对应字段）；robustness 阶段以**只读探针**（`code/robustness_probe.py`，复用已审定
model.py 模块，不修改原始数据/代码）补齐该判据实测值（Δt_win=0.749%≤2%，见
`robustness/r7_window_sensitivity.json`）。据此**复核并归纳**稳定性结论，无需另行启动重复的敏感性计算任务，
以免与 computation 阶段 §8.5 重复（延续 prob02 robustness 处理范式）。

## 不适用部分（如实记录）

- **求解器/算法选择稳健性**：主反演为一维全局扫描 + 每点线性 LS（variable projection），属精确/确定性方法，
  无离散决策、无组合爆炸（formulation §7.7）。§8.5 R8 唯一性判据（全局极小唯一）已含「偶然初始化/局部陷阱」
  检验，robustness 不再重复求解器/初值对比。
- **独立 bootstrap CI（B≥200）**：§8.5 R3 采用轮廓似然/夹逼区间（J(t) 曲率）给出 95% CI，未运行重采样
  bootstrap。作为方法债登记（见 preregistration §8 与 conclusion），留论文/后续小问讨论，不阻断
  （CI 半宽 0.134%≪2%）。

## 本阶段交付（robustness/ 目录）

- `decision.md`：本决定与理由
- `preregistration.md`：预注册方案（核心结论 + 稳定性判据 + 实验矩阵，判据计算前已固定）
- `experiment_matrix.yaml`：实验矩阵机器可读版本（映射 §8.5 判据与默认方案扰动 + 实测值）
- `conclusion.md`：robustness 稳定性结论与后续移交
- `r7_window_sensitivity.json`：R7 谱段窗口敏感性实测（只读探针补齐）
- `../code/robustness_probe.py`：R7 只读探针代码
