# prob01 robustness 适用性决定

> 阶段：robustness ｜ Agent：robustness-analyst ｜ 日期：2026-08-29
> 问题：2025-cumcm-b / prob01（两光束干涉测厚数学模型，assumption_v001 / formulation_v001）

## 决定：适用（completed）

## 理由

1. **formulation_v001 §5.2 已将「鲁棒性」列为模型比较标准**：明确要求量化
   「色散模型选择（Sellmeier vs 分段常数 vs 数据插值）、谱段截断、Reststrahlen 剔除、
   n_sub 灵敏度对厚度 t 的影响」。该标准在计算结果前固定，robustness 阶段必须执行。
2. **关键假设明确要求灵敏度分析**：A5（色散模型选择与 λ>5 µm 处理是 prob02 厚度精度
   主要不确定度来源）、A6（n_sub 灵敏度分析）、A10（入射角误差经 cosθ′ 传播到厚度）
   的「可观测验证」条目均指向灵敏度检验。
3. **workflow_state warnings 已登记多处未量化的不确定度**：λ>5 µm 常数色散延伸、
   方法 A 约 4% 系统偏差、n_sub=3.0 为合成场景值、Reststrahlen 区剔除策略——
   robustness 实验应在受控基准下量化这些因素对厚度反演的影响，为 prob02 实测反演
   的不确定度控制提供方法层证据。
4. **合成基准场景提供已知真值（t_true=10 µm）**：可在真值已知条件下检验反演方法
   对参数扰动、数据噪声、色散模型结构与谱段截断的稳健性，属方法层 robustness，
   与「prob01 无实测数据」不冲突（实验全部基于正模型合成谱，不涉及实测）。

## 不适用部分（如实记录）

- **求解器/算法选择稳健性**：prob01 已用 scipy NLS 并验证多初值规避周期歧义
  （formula_validation §6 / implementation §6.1），robustness 阶段不再重复求解器对比；
  改为检验**初值策略在噪声下的稳健性**（E4 网格扫描初值，见 preregistration）。
- **真实数据噪声与异常点**：prob01 无附件实测数据，真实噪声/异常点处理属 prob02
  预处理范围，不在本阶段（preregistration §9 移交说明）。

## 本阶段交付

- `preregistration.md`：预注册方案（核心结论、稳定性判据、实验矩阵，运行前固定）
- `experiment_matrix.yaml`：实验矩阵机器可读版本（与 robustness.py PREREGISTERED 一致）
- `code/robustness.py` + `configs/robustness_config.yaml`：实验代码与任务配置
- 计算结果输出至 `results/robustness/`（隔离 task 运行，supervised worker 执行）
