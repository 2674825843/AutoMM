# prob01 数学模型（formulation_v001）

> 版本：formulation_v001 ｜ 假设版本：assumption_v001 ｜ 阶段：mathematical_formulation
> 问题：2025 高教社杯 B 题问题 1 —— 考虑外延层与衬底界面"只有一次反射、透射"产生的干涉条纹，建立确定外延层厚度 $t$ 的数学模型。
> 本版本为解析正模型 + 反演公式的完整推导；prob01 无附件数据，不运行数值计算，计算与数据验证留待 prob02（implementation/computation 阶段）。

## 1. 模型目标与输入输出

### 1.1 目标

给定外延层-衬底结构的物理设定（图 1），在两光束干涉近似下建立：

1. 反射率 $R$ 与厚度 $t$、折射率 $n$、入射角 $\theta$、波数 $\nu$ 的解析关系式；
2. 干涉极值（峰/谷）条件及同型相邻极值波数间隔 $\Delta\nu$ 与厚度的定量关系；
3. 由 $\Delta\nu$（或全谱拟合）反演厚度 $t$ 的公式与适用条件。

### 1.2 输入（已知量）

| 量 | 符号 | 单位 | 来源 |
|---|---|---|---|
| 入射角（空气侧，相对表面法线） | $\theta$ | 度 | 题面；prob02 附件 1/2 为 10°、15° |
| 外延层折射率（色散） | $n(\nu)$ 或 $n(\lambda)$ | 无量纲 | A5；L09 Sellmeier（$\lambda\le5\,\mu\text{m}$）；$\lambda>5\,\mu\text{m}$ 由 prob02 数据反演/分谱段确定 |
| 衬底折射率 | $n_{\text{sub}}$ | 无量纲 | A6；prob02 反演/文献取值 |
| 空气折射率 | $n_{\text{air}}$ | 无量纲 | A9；$n_{\text{air}}=1.0$ |

### 1.3 输出（未知量/待求）

| 量 | 符号 | 单位 |
|---|---|---|
| 外延层厚度 | $t$ | $\mu\text{m}$（正实数） |
| 模型反射率谱 | $R(\nu)$ | 无量纲（0–1） |
| 干涉级次 | $m$ | 非负整数 |
| 同型相邻极值波数间隔 | $\Delta\nu$ | $\text{cm}^{-1}$ |

## 2. 物理设定与基本方程

结构为空气 → 外延层（厚度 $t$，折射率 $n$）→ 衬底（折射率 $n_{\text{sub}}$），界面平行（A8）。

红外光以入射角 $\theta$ 入射到外延层上表面（空气/外延层界面）。**光束 1** 在该界面直接反射；**光束 2** 透射进入外延层，在外延层/衬底界面反射后再次透射回空气（A1，忽略多次反射与衬底背面反射）。两束光在探测器处叠加干涉。

### 2.1 Snell 折射与折射角

由 Snell 定律（A2；L06、L07）：

$$n_{\text{air}}\sin\theta = n\sin\theta' \tag{2.1}$$

外延层内折射角：

$$\sin\theta' = \frac{n_{\text{air}}}{n}\sin\theta \;\xrightarrow{n_{\text{air}}=1}\; \sin\theta' = \frac{\sin\theta}{n} \tag{2.2}$$

衬底内折射角 $\theta''$（透射到衬底的路径仅在第二界面反射，不影响两光束几何光程差推导，但 Fresnel 系数需要）：

$$n\sin\theta' = n_{\text{sub}}\sin\theta'' \tag{2.3}$$

### 2.2 几何光程差

两光束的光程差由平行平板几何确定（A2；L06、L07、L17）。光束 2 在外延层内往返一次的光程为 $2nt/\cos\theta'$，光束 1 在空气中的附加光程为 $2t\tan\theta'\cdot n_{\text{air}}\sin\theta$，二者之差：

$$\Delta = \frac{2nt}{\cos\theta'} - 2t\tan\theta'\cdot n_{\text{air}}\sin\theta
= 2t\left(\frac{n}{\cos\theta'} - n_{\text{air}}\sin\theta\tan\theta'\right) \tag{2.4}$$

代入 (2.1)：$n_{\text{air}}\sin\theta = n\sin\theta'$，得

$$\Delta = 2t\left(\frac{n}{\cos\theta'} - n\frac{\sin^2\theta'}{\cos\theta'}\right)
= 2nt\frac{1-\sin^2\theta'}{\cos\theta'} = 2nt\cos\theta' \tag{2.5}$$

等价形式（消去 $\theta'$，便于直接用 $\theta$、$n$ 计算）：

$$\Delta = 2nt\cos\theta' = 2t\sqrt{n^2 - n_{\text{air}}^2\sin^2\theta}
\;\xrightarrow{n_{\text{air}}=1}\; 2t\sqrt{n^2-\sin^2\theta} \tag{2.6}$$

### 2.3 相位差

两束相干光的相位差（A3；L01、L02）：

$$\delta = \frac{2\pi}{\lambda}\Delta = 2\pi\nu\,\Delta = 4\pi n t\nu\cos\theta' \tag{2.7}$$

其中 $\lambda$ 为真空中波长，$\nu=1/\lambda$ 为波数。**单位约定**（进入 formula_validation 量纲检查）：若 $t$ 以 $\mu\text{m}$、$\nu$ 以 $\text{cm}^{-1}$ 计，则波长 $\lambda[\mu\text{m}] = 10^4/\nu[\text{cm}^{-1}]$，光程差 $\Delta[\mu\text{m}] = 2nt\cos\theta'$，相位差

$$\delta = 2\pi\cdot\frac{\Delta[\mu\text{m}]}{\lambda[\mu\text{m}]}
= 2\pi\cdot 10^{-4}\,\nu[\text{cm}^{-1}]\cdot\Delta[\mu\text{m}]
= 4\pi\times 10^{-4}\, n\, t[\mu\text{m}]\,\nu[\text{cm}^{-1}]\cos\theta' \tag{2.8}$$

## 3. 关键公式逐步推导

### 3.1 界面反射强度（Fresnel）

设空气/外延层界面（界面 1）的强度反射率为 $R_1$，外延层/衬底界面（界面 2）的强度反射率为 $R_2$（本版本中的局部中间量；prob03 将登记 $R_{01}$、$R_{12}$ 为正式全局符号）。

无吸收（A7 适用谱段）时，Fresnel 振幅反射系数（s、p 偏振，L06、L07）：

$$r_1^s = \frac{n_{\text{air}}\cos\theta - n\cos\theta'}{n_{\text{air}}\cos\theta + n\cos\theta'},\qquad
r_1^p = \frac{n\cos\theta - n_{\text{air}}\cos\theta'}{n\cos\theta + n_{\text{air}}\cos\theta'} \tag{3.1}$$

$$r_2^s = \frac{n\cos\theta' - n_{\text{sub}}\cos\theta''}{n\cos\theta' + n_{\text{sub}}\cos\theta''},\qquad
r_2^p = \frac{n_{\text{sub}}\cos\theta' - n\cos\theta''}{n_{\text{sub}}\cos\theta' + n\cos\theta''} \tag{3.2}$$

强度反射率：

$$R_1 = |r_1|^2,\qquad R_2 = |r_2|^2 \tag{3.3}$$

**A4 相位跃变**：空气→外延层（$n>n_{\text{air}}$）反射产生 $\pi$ 相位跃变（$r_1$ 为负值，s 偏振在 $\theta<90°$ 时 $r_1^s<0$）；外延层→衬底界面的跃变取决于 $n$ 与 $n_{\text{sub}}$ 的相对大小。相位跃变只改变峰/谷类型与干涉级次 $m$ 的对应，在相邻同型极值间隔 $\Delta\nu$ 中抵消（A4；L06、L07），故厚度公式不受其影响，但峰/谷判定需明确。

### 3.2 两光束反射率模型（正模型）

两束光（振幅分别为 $E_1$、$E_2$）叠加，干涉强度（A3；L07）：

$$I = I_1 + I_2 + 2\sqrt{I_1 I_2}\cos\delta \tag{3.4}$$

其中 $I_1 = R_1 I_0$（界面 1 直接反射），$I_2 = (1-R_1)^2 R_2 I_0$（透射-反射-透射，无吸收时单次界面透射率 $T_1=1-R_1$）。归一化到 $I_0$ 得模型反射率：

$$\boxed{\;R(\nu;\, t, n(\nu), \theta, n_{\text{sub}})
= R_1 + (1-R_1)^2 R_2 + 2(1-R_1)\sqrt{R_1 R_2}\,\cos\delta\;} \tag{3.5}$$

其中 $\delta$ 由 (2.7)/(2.8) 给出，$R_1$、$R_2$ 由 (3.1)–(3.3) 给出，$\theta'$、$\theta''$ 由 (2.2)、(2.3) 给出。对非偏振（或未指定偏振）测量，取 s/p 平均：

$$R = \frac{R^s + R^p}{2} \tag{3.6}$$

**物理边界**：$0\le R(\nu) \le 1$（无吸收两光束模型，能量守恒约束，见 formula_validation §4）。

### 3.3 干涉极值条件

反射率对 $\delta$ 的依赖仅通过 $\cos\delta$（弱色散时 $R_1$、$R_2$ 随 $\nu$ 缓慢变化），极值条件：

$$\frac{\partial R}{\partial \nu}=0 \;\Longleftrightarrow\; \sin\delta = 0
\;\Longleftrightarrow\; \delta = m\pi,\quad m\in\mathbb{Z}_{\ge 0} \tag{3.7}$$

峰/谷类型由 $2(1-R_1)\sqrt{R_1R_2}\cos\delta$ 项的二阶导符号与界面相位跃变共同决定（A4）：若 $\cos\delta=+1$ 处取极大则 $\cos\delta=-1$ 处取极小，反之亦然。**同型相邻极值（峰-峰或谷-谷）对应 $\delta$ 变化 $2\pi$**。

### 3.4 同型相邻极值波数间隔与厚度公式（弱色散近似）

在弱色散谱段（$n$ 近似常数，A3、A5 边界），由 (2.7)：

$$\Delta\delta = 4\pi n t\cos\theta'\cdot\Delta\nu = 2\pi
\;\Longrightarrow\; \boxed{\;\Delta\nu = \frac{1}{2\,n\,t\cos\theta'}\;} \tag{3.8}$$

厚度反演公式（A3；L01、L02、L23）：

$$\boxed{\;t = \frac{1}{2\,n\cos\theta'\,\Delta\nu}
= \frac{1}{2\,\Delta\nu\sqrt{n^2-\sin^2\theta}}\;} \tag{3.9}$$

其中第二式利用 (2.6)（$n_{\text{air}}=1$）。单位：$t[\mu\text{m}]$、$\Delta\nu[\text{cm}^{-1}]$ 时，$\Delta\nu = 10^4/(2nt\cos\theta')$，即

$$t[\mu\text{m}] = \frac{10^4}{2\,n\cos\theta'\,\Delta\nu[\text{cm}^{-1}]} \tag{3.10}$$

### 3.5 色散化修正（$n = n(\nu)$）

色散显著时（A5：$\lambda>5\,\mu\text{m}$ 谱段、近 Reststrahlen 区外缘），(3.8) 的直接形式失效，需用相位条件数值求解。定义相位函数：

$$g(\nu) \equiv n(\nu)\,\nu\cos\theta'(\nu) \tag{3.11}$$

极值条件 (3.7) 化为 $4\pi t\,g(\nu_m) = m\pi$，即

$$g(\nu_m) = \frac{m}{4t} \tag{3.12}$$

同型相邻极值（$m\to m+2$）：

$$t = \frac{1}{2\big[g(\nu_{m+2}) - g(\nu_m)\big]} \tag{3.13}$$

弱色散极限：$g(\nu_{m+2})-g(\nu_m)\approx n\cos\theta'\,\Delta\nu$，回到 (3.8)/(3.9)。**prob02 反演策略**：以 (3.13) 或全谱非线性最小二乘拟合 (3.5) 为主，峰谷间隔法 (3.9) 提供初值与交叉验证。

### 3.6 反演模型（prob01 给出形式，prob02 实现）

- **方法 A（极值间隔法）**：定位峰/谷波数 → 求同型相邻间隔 $\Delta\nu$ → (3.9)/(3.10) 得 $t$。优点是解析、快速、可解释；缺点是仅用少量极值点，受色散与噪声影响（prob02 作交叉验证）。
- **方法 B（全谱非线性最小二乘）**：以 (3.5) 为模型，优化 $\min_{t}\sum_i w_i\left[R^{\text{obs}}(\nu_i) - R(\nu_i; t, n(\nu_i), \theta, n_{\text{sub}})\right]^2$（L17 同题方法）。优点是信息利用充分、可同时校核色散与 $n_{\text{sub}}$；prob02 主方法。
- **求解策略选择依据**（knowledge/optimization.md）：本问是**连续参数估计**（1 个厚度参数 + 少量材料参数），正模型解析、目标光滑，属"小规模、连续、可预测"情形，**精确方法（NLS/LM）充分适用**；无离散决策、无组合爆炸，**不需要** MILP、启发式或元启发式。引入复杂算法既不必要也无解释增益。

## 4. 边界条件与适用性

1. **谱段边界（A7）**：SiC 约 700–1000 cm⁻¹（约 10–14.3 µm）为 Reststrahlen 强吸收/强色散区，两光束无吸收模型 (3.5) 不适用；prob02 预处理剔除或降权该区间并记录策略。
2. **色散模型边界（A5）**：$\lambda\le5\,\mu\text{m}$（$\nu\ge2000\,\text{cm}^{-1}$）用 4H-SiC Sellmeier（L09）：
   $$n^2(\lambda) = 6.79485 + \frac{0.15558}{\lambda^2 - 0.03535} - 0.02296\,\lambda^2,\quad \lambda\in[\mu\text{m}]\le5 \tag{4.1}$$
   $\lambda>5\,\mu\text{m}$（$\nu<2000\,\text{cm}^{-1}$）无现成体材料 Sellmeier，prob02 采用分谱段/数据反演（L24/L16 为参考）并量化对 $t$ 的影响（workflow_state warnings 已登记）。
3. **相位跃变（A4）**：公式 (3.5) 中 $\delta$ 不含反射相位跃变常数项；峰/谷类型判定需按 A4 结合 $n$ 与 $n_{\text{sub}}$ 相对大小修正，**但不改变同型极值间隔 $\Delta\nu$**。
4. **相干性（A11）**：FTIR 相干长度远大于光程差 $\Delta$（数十 µm 量级），干涉条纹稳定。
5. **几何边界（A8、A10）**：界面平行、厚度均匀；入射角已知且固定。
6. **吸收边界（A7）**：适用谱段内 $n$、$n_{\text{sub}}$ 取实数；若 prob02 在 Reststrahlen 区外缘仍需使用，应改用复折射率 Fresnel（prob03 处理方向）。

## 5. 候选模型与比较标准

### 5.1 候选模型

| 编号 | 模型 | 说明 | 角色 |
|---|---|---|---|
| M1 | 色散化两光束 Fresnel 模型 (3.5) | $n=n(\nu)$，全谱 NLS 反演 + 峰谷间隔交叉验证 | **主模型（prob02）** |
| M2 | 常数折射率两光束模型 | $n$ 取谱段有效常数，(3.9) 直接反演 | 简化基线/初值 |
| M3 | 弱色散峰谷间隔模型 | 仅 (3.8)–(3.10)，忽略色散 | 纯解析对照、prob01 交付公式 |
| M4 | 多光束（Airy）模型 | 含多次反射 | **prob03 处理，本问不展开** |

### 5.2 比较标准（计算结果前固定）

| 标准 | 定义/度量 | 适用 |
|---|---|---|
| 约束满足度 | 模型反射率 $R\in[0,1]$；极值条件 (3.7) 满足；$t>0$ | M1–M3 |
| 题目指标 | 厚度反演值 $t$；两入射角（10°/15°）反演一致性；prob02 与参考值/残差比对 | M1–M3 |
| 解释性 | 公式可解析推导、参数物理含义明确、峰/谷可判定 | M1–M3 |
| 复杂度 | 正模型 $O(N)$ 谱点；NLS 每迭代 $O(N)$；无需离散求解器 | M1–M3 |
| 运行预算 | 秒级（prob02 数据量 ~4000 谱点 × 2 入射角） | M1–M3 |
| 鲁棒性 | 色散模型选择（Sellmeier vs 分段常数 vs 数据插值）、谱段截断、Reststrahlen 剔除、$n_{\text{sub}}$ 灵敏度对 $t$ 的影响 | M1（prob02 敏感性分析） |

**决策规则**：优先 M1；若色散影响量化后不显著（$t$ 变化小于 prob02 目标精度），M2/M3 可作为简化交付并记录理由；prob03 用 M4 校验"多光束不改变极值位置"（L17 候选主张，需独立验证）。

## 6. 公式来源登记

| 公式 | 内容 | 来源 |
|---|---|---|
| (2.1)–(2.3) | Snell 折射与折射角 | L06、L07（文献事实）；A2 |
| (2.4)–(2.6) | 几何光程差 $\Delta=2nt\cos\theta'$ | L06、L07、L17（文献事实）；A2 |
| (2.7)–(2.8) | 相位差 $\delta=4\pi nt\nu\cos\theta'$ | L01、L02（文献事实）；A3 |
| (3.1)–(3.3) | Fresnel 振幅/强度反射系数 | L06、L07（文献事实） |
| (3.4)–(3.5) | 两光束干涉反射率 | L07、L01、L02（文献事实）；A1、A3 |
| (3.7) | 极值条件 $\delta=m\pi$ | L06、L07、L01（文献事实）；A3 |
| (3.8)–(3.10) | 同型相邻极值间隔与厚度公式 | L01、L02、L23、L17（文献事实）；A3 |
| (3.11)–(3.13) | 色散化相位条件与厚度 | L17（方法级佐证，C 级）；A5；prob02 验证 |
| (4.1) | 4H-SiC Sellmeier | L09（经 L11 交叉核验，文献事实）；A5 |

## 7. 符号与单位核对

与 `global_symbols.yaml` 一致：$t$、$n$、$n_{\text{sub}}$、$n_{\text{air}}$、$\theta$、$\theta'$、$\lambda$、$\nu$、$R$、$m$、$\Delta\nu$、$\delta$ 均使用全局登记符号，无同名异义。局部中间量 $R_1$、$R_2$、$\theta''$、$g(\nu)$、$I_0$、$I_1$、$I_2$ 为公式推导量，不进入全局符号表；prob03 登记 $r_{01}$、$r_{12}$、$R_{01}$、$R_{12}$、finesse 时以本版本 Fresnel 系数为前置定义。

单位约定：$t[\mu\text{m}]$、$\nu[\text{cm}^{-1}]$、$\lambda[\mu\text{m}]=10^4/\nu$、$\theta[\text{度}]$（三角函数计算时转 rad）、$\Delta\nu[\text{cm}^{-1}]$、$\delta[\text{rad}]$。

## 8. 遗留与移交

- 色散模型选择与 $\lambda>5\,\mu\text{m}$ 处理策略 → prob02 反演并量化影响；
- $n_{\text{sub}}$ 定量取值 → prob02 反演/文献；
- Reststrahlen 区剔除策略 → prob02 预处理；
- 多光束对极值位置影响 → prob03 独立验证（L17 主张未采信）。
