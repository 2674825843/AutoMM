# prob01 图表视觉复核报告（visualization-agent）

> 小问：prob01 ｜ 版本：assumption_v001 / formulation_v001 ｜ 阶段：visualization
> 复核时间：2026-08-29 ｜ 复核方式：自动质检（inspect_png）+ 程序化统计 + 元素级核验
> 配置：`config/visualization.yaml`（theme=publication，字体=Microsoft YaHei，10×6 in，180 dpi，PNG）

## 复核依据

1. **自动质检**（`automm.visualization.inspect_png`）：分辨率 ≥ 800×480 px、非空、非纯色、暗边框比例 ≤ 0.35 —— 7/7 passed；
2. **程序化统计**（PIL）：每张 PNG 尺寸、白底比例、暗像素比例、唯一颜色数 —— 全部健康（见下表）；
3. **元素级核验**（生成脚本逐函数）：标题、轴标签与单位、图例、颜色区分、文本标注、三维视角与二维配套；
4. **渲染日志**：matplotlib 无 Glyph 缺失警告（中文字体 Microsoft YaHei 探测成功并完整渲染，无方框乱码）。

## 统计表

| stable_id | 尺寸 (px) | 白底比 | 暗像素比 | 唯一颜色 | 自动质检 |
|---|---|---|---|---|---|
| prob01_fig_reflectance_spectrum_1d4fb899d1 | 1567×994 | 82.1% | 2.0% | 7855 | passed |
| prob01_fig_dispersion_curve_d85564d2fc | 1566×1068 | 89.9% | 1.8% | 774 | passed |
| prob01_fig_phase_function_gap_459c486470 | 1809×926 | 93.4% | 3.1% | 1081 | passed |
| prob01_fig_thickness_methods_compare_5eac465fc8 | 1538×985 | 73.7% | 2.1% | 1022 | passed |
| prob01_fig_spacing_constant_n_bias_2245b6eda4 | 1531×1002 | 94.5% | 1.9% | 1716 | passed |
| prob01_fig_nls_multistart_e64919ab13 | 1605×994 | 94.8% | 2.3% | 536 | passed |
| prob01_fig_response_surface_d0691c5dd8 | 1741×1057 | 52.8% | 2.8% | 20539 | passed |

## 逐图复核

### 1. reflectance_spectrum —— 两光束干涉合成反射率谱
- 标题/轴/单位：完整（标题含 t_true、n_sub 条件；x=波数 ν (cm^-1)、y=反射率 R 无量纲）。
- 内容：θ=10°（主色 #1F4E79）、θ=15°（对照 #70AD47）双谱对比；干涉峰（橙色三角）标注；Reststrahlen 区 [700,1000] cm^-1 灰色阴影；Sellmeier 边界 ν=2000 cm^-1 虚线；弱色散段橙色浅底。
- 图例位置 lower-left，不与数据区重叠；颜色区分明确（深蓝/绿/橙/灰语义一致）。
- 判定：**passed**（无截断、无重叠、信息完整）。

### 2. dispersion_curve —— 外延层折射率色散
- 标题/轴/单位：完整（x=波数 ν (cm^-1)，顶部双轴 λ (µm)；y=n 无量纲）。
- 内容：Sellmeier 段实线（主色）与常数延伸段虚线（灰色）分界明确；Sellmeier 边界虚线+文本；Reststrahlen 区阴影；图例 upper-right。
- 双轴刻度换算正确（λ=1e4/ν：25/10/5/2.5 µm ↔ 400/1000/2000/4000 cm^-1）。
- 判定：**passed**。

### 3. phase_function_gap —— 色散化相位法机制
- 双面板：左 g(ν) 单调递增曲线+峰位置竖线；右同型相邻极值 Δg 序列点线图+理论 500 cm^-1 虚线。
- 单位：g(ν) 与 Δg 均 (cm^-1)；图例/标题完整；Δg y 轴 [495,505] 显式缩放展示恒定律。
- 判定：**passed**。

### 4. thickness_methods_compare —— 三方法厚度估计对比
- 分组柱状图（θ=10°/15°×三方法），每柱标注 t 值与相对偏差 %；t_true=10.000 µm 参考线 + ±1% 容差带（绿色浅底）。
- 颜色区分明确；图例 lower-left ncol=2；y 轴 [9.6,11.2] 无截断关键信息。
- 判定：**passed**。

### 5. spacing_constant_n_bias —— 方法 A 常数 n 系统偏差
- 实测 Δν 序列（两入射角）点线图 vs 常数 n 理论水平虚线（196.2/196.8 cm^-1）；左下角白底红框说明框量化 4.2–4.7% 偏差与修正方向。
- 说明框置于 axes 左下（transAxes 0.02,0.02），不与数据散点重叠。
- 判定：**passed**。

### 6. nls_multistart —— NLS 多初值收敛与周期歧义
- 散点：x=起始 t0 (µm)，y=拟合 RMSE；全局解（橙色圆点+黑边，rmse≈0）vs 局部极小（蓝/绿叉）；每点标注 t0→t；θ=10° 周期≈0.90 µm 竖线标注。
- 图例 upper-right 用显式 handles（o/x），与散点符号一致；y 轴 [−0.002,0.075] 展示全局解与局部极小分离。
- 判定：**passed**。

### 7. response_surface —— 三维响应面 + 二维等高线配套
- 左：3D 曲面 R(ν,θ)，x=ν (cm^-1)、y=θ (°)、z=R；视角 elev=26°、azim=−62°（可读视角，条纹结构无关键遮挡）；viridis 色带连续。
- 右：2D 等高线配套（消歧），θ=10°/15° 测量虚线标注；Reststrahlen 区阴影；colorbar 标注 R。
- 第三维语义真实（入射角为真实物理变量，非机械立体柱）；静态 PNG 下 2D 等高线保证条纹结构可读。
- 判定：**passed**。

## 结论

7 张图全部通过自动质检与视觉复核，均为最终接受版本（assumption_v001）产物，
功能互补（光谱/色散/机制/对比/偏差诊断/求解器诊断/三维响应面），满足每问至少 5 张的门禁。
无被拒绝版本图表；全部登记于 `problems/2025-cumcm-b/figures.yaml`，`included_in_summary=true`。
