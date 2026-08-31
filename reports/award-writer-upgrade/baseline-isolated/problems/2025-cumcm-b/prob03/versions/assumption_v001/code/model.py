"""prob03 硅/碳化硅外延层多光束（Airy）干涉必要条件与厚度反演模型（formulation_v002）。

实现 `formulations/formulation_v002/formulation.md` 的公式。本问为物理模型 + 可解性反演
（非优化问题），主方法为「基线-干涉分解 + 一维相位频率扫描（variable projection）」（复用
prob02 方法族），多光束判定为「两光束 vs Airy 正模型残差改善率」诊断。
本版相对 formulation_v001 的必改勘误（sanity NEEDS_REVISION）：
  R1：硅厚度基准由 v001 伪影 6.9 µm 更正为对审定公式的忠实实现值 t̂≈3.4477 µm（共享）/每角。
  R2：精细度公式统一为 F = π√R̄/(1−R̄)（v001 代码 `π·R̄/(1−R̄)` 漏 √R̄ 为 bug，0.032 应为 ≈0.319）。
其余公式与 v001 一致（(2.1)-(2.8)、(2.5)-(2.6)、(2.7)、(5.1)、(3.1)-(3.6)、(3.7)-(3.8)、(6.1)-(6.5)）。

- (2.1)  Snell 折射角：sin(theta') = sin(theta)/n（n_air = 1）
- (2.2)-(2.4) 两光束反射率正模型 R(nu;t,n(nu),theta,n_sub)，s/p 平均（prob01/prob02 基线）
- (2.5)-(2.6) Airy 多光束反射率正模型（一般模型）
- (2.7)  相位差 delta = 4pi*1e-4*n*t*nu*cos(theta')
- (5.1)  硅 Sellmeier（Li 1980），覆盖本问主反演带（λ 约 2.5-5µm，n 约 3.42-3.44）
- (3.1)-(3.6) 多光束必要条件 N1-N4（界面反射率乘积、相干长度、界面平行度、吸收限制）
- (3.7)-(3.8) 无吸收时 Airy 极值位置不变性（L17 独立验证：极值在 delta = m*pi）
- (6.1)-(6.5) 主反演＝基线-干涉分解 + 一维相位频率扫描（variable projection），两角共享 t
- §7.2     硅片多光束判定（R01/R12/Rbar/finesse + 残差改善率 eta_mb）
- §7.3     SiC 重新判定（prob02 对照）

单位约定（与 parameters.yaml / formula_validation.md 一致）：
t [um]、nu [cm^-1]、lambda [um]=1e4/nu、theta [deg]（三角内转 rad）、delta [rad]、delta_nu [cm^-1]。

本模块为可复用/无副作用核心；`compute.py` 为 CLI，`probe.py` 为秒级接口探针。
实现阶段只做静态检查与小型探针，不运行完整数据集（由 supervised worker 在 computation 阶段执行）。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# ---- 物理常量与谱段边界（parameters.yaml 登记值，权威来源） ----
N_AIR: float = 1.0  # C1：空气折射率
SI_SELLMEIER: tuple[float, float, float, float, float, float] = (
    # (A1, lam1, A2, lam2, A3, lam3)，n^2 = 1 + A1*lam^2/(lam^2-lam1^2) + ...
    10.6684293,
    0.301516485,
    0.0030434748,
    1.13475115,
    1.54133408,
    1104.0,
)  # L12/L13：硅中红外 Sellmeier（Li 1980，经 L13 Palik 补充）
SI_SELLMEIER_BOUNDARY_UM: float = 11.0  # C8：硅 Sellmeier 有效上界（本问主反演带全程有效）
SIC_SELLMEIER: tuple[float, float, float, float] = (6.79485, 0.15558, 0.03535, 0.02296)  # L09：4H-SiC
SIC_SELLMEIER_BOUNDARY_UM: float = 5.0  # B6：SiC Sellmeier 适用上界（波长）

NU_RANGE_CM1: tuple[float, float] = (400.0, 4000.0)  # 题面谱段
SIC_INV_BAND_CM1: tuple[float, float] = (2000.0, 4000.0)  # prob02：SiC 主反演带（Sellmeier 已知区）
SI_INV_BAND_CM1: tuple[float, float] = (2000.0, 4000.0)  # C8：硅主反演带（透明谱段，多声子带外）
SI_MULTIPHONON_EXCLUDE_CM1: tuple[float, float] = (400.0, 1600.0)  # C8：硅多声子吸收带（模型不适用）
SIC_RESTSTRAHLEN_EXCLUDE_CM1: tuple[float, float] = (700.0, 1000.0)  # prob02 B3：SiC 近 Reststrahlen
ANOMALY_UPPER_PCT: float = 100.0  # B2：反射率 >100% 判定为异常点
ANOMALY_LOWER_PCT: float = 0.0  # B2：下界（物理下限，防御性标记）

# 多光束必要条件阈值（formulation §3.6：本版从物理上严格推导并登记；decomposer 不预设）
THETA_MB: float = 0.05  # N1：Rbar=sqrt(R01*R12) 阈值（两光束适用）
TAU_MB_PERCENT: float = 10.0  # 主判据：Airy vs 两光束残差改善率阈值（eta_mb<=tau_mb 则两光束适用）
FINESS_MAX: float = 0.739  # N1 对应精细度上限（Rbar<=0.05 → F<=π√0.05/(1−0.05)≈0.739；R2 公式 π√R̄/(1−R̄)）
DELTA_NU_RES_CM1: float = 0.482  # C4：FTIR 光谱分辨率（对应 L_c = 1/(2*delta_nu_res)；附件步长）
BEAM_DIAMETER_CM: float = 1.0  # C3：光束横向尺度 D（平行度判据 α 估算用）
ALPHA_WEDGE_RAD: float = 1.0e-6  # C3：界面楔角/不平度 α 保守估算（约 0.00006°，抛光外延片），判据 α<<λ/(2nDcosθ')
SI_N_SUB_BOUNDS: tuple[float, float] = (3.0, 4.2)  # C7：硅衬底折射率合理性区间（重掺硅）
SIC_N_SUB_BOUNDS: tuple[float, float] = (2.4, 4.0)  # prob02 B7：SiC 衬底折射率区间

# ---- v003 基线-干涉分解 + 一维相位频率扫描（variable projection）登记参数 ----
BASELINE_POLY_DEG: int = 3  # B(ν) 基线多项式阶数 p（formulation §6.1：默认 3，计算前固定）
ENVELOPE_POLY_DEG: int = 1  # C(ν)/S(ν) 包络多项式阶数 q（formulation §6.1：默认 1，计算前固定）
T_SCAN_RANGE_SI: tuple[float, float] = (2.0, 12.0)  # 硅主反演一维扫描区间（formulation parameters.yaml）
T_SCAN_STEP: float = 0.01  # 扫描步长（≤0.01µm，全局极小捕获与唯一性分辨率）
DELTA_C_DISP: float = 0.005  # §7.2：Sellmeier 系数可复现性扰动半宽（0.5%）
AMP_REF_NU_CM1: float = 3000.0  # 取干涉幅值 A=√(C²+S²) 的代表波数（带内中心）
N_SUB_SI_INIT: float = 3.54  # C7：硅 n_sub 幅值弱辨识初值（formulation §13.2 q=0 常数包络约 0.014）
SIC_N_SUB_REF: float = 2.588  # prob02 B7：SiC n_sub 对照值（prob02 实测）
SIC_R12_REF: float = 3.2e-5  # prob02：SiC 界面反射率 R12 对照值（prob02 实测）
SIC_R01_REF: float = 0.19  # prob02：SiC 空气/外延层界面反射率 R01 对照值（n≈2.55）
SIC_T_REF_UM: float = 7.2158  # prob02：SiC 厚度对照（prob02-conclusion-v1，C17）

# ---- 硅 recheck 的 prob02 对照值（只读探针，不参与主反演） ----


def nu_to_lambda(nu_cm1: np.ndarray | float) -> np.ndarray | float:
    """波长换算：lambda[um] = 1e4 / nu[cm^-1]。"""
    return 1e4 / np.asarray(nu_cm1, dtype=float)


def lambda_to_nu(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """波数换算：nu[cm^-1] = 1e4 / lambda[um]。"""
    return 1e4 / np.asarray(lambda_um, dtype=float)


# ---------------------------------------------------------------------------
# 色散模型（C7/C8/C15）
# ---------------------------------------------------------------------------
def sellmeier_si(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """硅 Sellmeier 折射率 n(lambda)（formulation.md (5.1)，L12/L13）。

    n^2 = 1 + A1*lam^2/(lam^2-lam1^2) + A2*lam^2/(lam^2-lam2^2) + A3*lam^2/(lam^2-lam3^2)，
    lambda 单位 um。带内（λ∈[2.5,5]µm，ν∈[2000,4000]）n≈3.422-3.439，色散弱（Δn/n≈0.51%）。
    """
    lam2 = np.asarray(lambda_um, dtype=float) ** 2
    a1, l1, a2, l2, a3, l3 = SI_SELLMEIER
    return np.sqrt(1.0 + a1 * lam2 / (lam2 - l1 * l1) + a2 * lam2 / (lam2 - l2 * l2) + a3 * lam2 / (lam2 - l3 * l3))


def sellmeier_n4hsi(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """4H-SiC Sellmeier 折射率 n(lambda)（prob02 (4.1)，L09；本问仅用于 SiC 重新判定 §7.3）。

    n^2 = 6.79485 + 0.15558/(lambda^2 - 0.03535) - 0.02296*lambda^2，lambda 单位 um。
    仅适用于 lambda <= SIC_SELLMEIER_BOUNDARY_UM。
    """
    lam2 = np.asarray(lambda_um, dtype=float) ** 2
    a, b, c, d = SIC_SELLMEIER
    return np.sqrt(a + b / (lam2 - c) - d * lam2)


def dispersion_epi_si(
    nu_cm1: np.ndarray | float,
    *,
    model: str = "N-SE",
    c_disp: float = 1.0,
) -> np.ndarray | float:
    """硅外延层色散折射率 n(nu)（formulation §5.1，C7/C8）。

    模型：
      - N-SE（主）：Sellmeier（L12/L13），λ≤SI_SELLMEIER_BOUNDARY_UM；
      - N-SE-delta：N-SE × c_disp（带内色散灵敏度，§7.2；c_disp = 1±delta_c_disp）；
      - N-const：常数 n = Sellmeier(5um)（S5 基线 B10 对照，不列入 Δt_disp 候选集）。
    与 SiC 不同，硅不存在「λ>5µm 色散缺口」——Sellmeier 在本问主反演带全程有效（λ≤11 µm）。
    """
    if model not in {"N-SE", "N-SE-delta", "N-const"}:
        raise ValueError(f"未知色散模型：{model!r}")
    nu_arr = np.atleast_1d(np.asarray(nu_cm1, dtype=float))
    scalar = np.ndim(nu_cm1) == 0
    lam = nu_to_lambda(nu_arr)

    if model == "N-const":
        n_ref = float(np.asarray(sellmeier_si(5.0), dtype=float))
        result = np.full(nu_arr.shape, n_ref, dtype=float)
    else:
        result = np.asarray(sellmeier_si(lam), dtype=float)
        if model == "N-SE-delta":
            result = result * c_disp
    return float(result[0]) if scalar else result


def dispersion_epi_sic(nu_cm1: np.ndarray | float) -> np.ndarray | float:
    """SiC 外延层折射率（prob02 B6/L09 Sellmeier；本问 §7.3 重新判定用）。"""
    nu_arr = np.atleast_1d(np.asarray(nu_cm1, dtype=float))
    scalar = np.ndim(nu_cm1) == 0
    lam = nu_to_lambda(nu_arr)
    result = np.asarray(sellmeier_n4hsi(lam), dtype=float)
    return float(result[0]) if scalar else result


# ---------------------------------------------------------------------------
# 几何 / 相位（B5，继承 prob01/prob02）
# ---------------------------------------------------------------------------
def theta_prime(theta_deg: float, n: float, n_air: float = N_AIR) -> float:
    value = n_air * np.sin(np.deg2rad(theta_deg)) / n
    if value > 1.0:
        raise ValueError(f"全反射：sin(theta') = {value:.6f} > 1")
    return float(np.rad2deg(np.arcsin(value)))


def cos_theta_prime(theta_deg: float, n: float, n_air: float = N_AIR) -> float:
    value = n_air * np.sin(np.deg2rad(theta_deg)) / n
    if value > 1.0:
        raise ValueError(f"全反射：sin(theta') = {value:.6f} > 1")
    return float(np.sqrt(1.0 - value * value))


def theta_double_prime(theta_prime_deg: float, n: float, n_sub: float) -> float:
    value = n * np.sin(np.deg2rad(theta_prime_deg)) / n_sub
    if value > 1.0:
        raise ValueError(f"全反射：sin(theta'') = {value:.6f} > 1")
    return float(np.rad2deg(np.arcsin(value)))


def optical_path_difference(t_um: float, n: float, theta_deg: float, n_air: float = N_AIR) -> float:
    return 2.0 * t_um * np.sqrt(n * n - n_air * n_air * np.sin(np.deg2rad(theta_deg)) ** 2)


def phase_delta(
    nu_cm1: np.ndarray | float,
    t_um: float,
    n: np.ndarray | float,
    theta_deg: float,
    n_air: float = N_AIR,
) -> np.ndarray | float:
    nu_arr = np.asarray(nu_cm1, dtype=float)
    n_arr = np.asarray(n, dtype=float)
    sin_tp = n_air * np.sin(np.deg2rad(theta_deg)) / n_arr
    if np.any(sin_tp > 1.0):
        raise ValueError("全反射：sin(theta') > 1")
    cos_tp = np.sqrt(1.0 - sin_tp * sin_tp)
    return 4.0 * np.pi * 1e-4 * n_arr * t_um * nu_arr * cos_tp


def phase_function(
    nu_cm1: np.ndarray | float,
    n_nu: np.ndarray | float,
    theta_deg: float,
    n_air: float = N_AIR,
) -> np.ndarray | float:
    nu_arr = np.asarray(nu_cm1, dtype=float)
    n_arr = np.asarray(n_nu, dtype=float)
    cosv = np.sqrt(np.clip(1.0 - (n_air * np.sin(np.deg2rad(theta_deg)) / n_arr) ** 2, 0.0, 1.0))
    return nu_arr * n_arr * cosv


# ---------------------------------------------------------------------------
# Fresnel 正模型（B4，继承 prob01/prob02）
# ---------------------------------------------------------------------------
def fresnel_interface(
    n_incident: float,
    n_transmitted: float,
    theta_incident_deg: float,
    theta_transmitted_deg: float,
) -> tuple[float, float]:
    cos_i = np.cos(np.deg2rad(theta_incident_deg))
    cos_t = np.cos(np.deg2rad(theta_transmitted_deg))
    r_s = (n_incident * cos_i - n_transmitted * cos_t) / (n_incident * cos_i + n_transmitted * cos_t)
    r_p = (n_transmitted * cos_i - n_incident * cos_t) / (n_transmitted * cos_i + n_incident * cos_t)
    return float(r_s), float(r_p)


def interface_reflectivities(
    n: float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
) -> dict[str, tuple[float, float]]:
    tp = theta_prime(theta_deg, n, n_air)
    tpp = theta_double_prime(tp, n, n_sub)
    r1s, r1p = fresnel_interface(n_air, n, theta_deg, tp)
    r2s, r2p = fresnel_interface(n, n_sub, tp, tpp)
    return {"R1": (r1s * r1s, r1p * r1p), "R2": (r2s * r2s, r2p * r2p)}


def forward_reflectance(
    nu_cm1: np.ndarray | float,
    t_um: float,
    n: np.ndarray | float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
    pol: str = "avg",
) -> np.ndarray | float:
    """两光束反射率正模型 R(nu;t,n(nu),theta,n_sub)（formulation.md (2.8)，prob01/prob02 基线）。

    n 为标量或与 nu 同形数组；R1、R2、theta'、delta 逐点由 n(nu) 计算。返回无量纲 0-1 强度反射率。
    """
    if pol not in {"s", "p", "avg"}:
        raise ValueError(f"pol 只能是 s/p/avg，得到 {pol!r}")
    nu_arr = np.asarray(nu_cm1, dtype=float)
    n_arr = np.asarray(n, dtype=float)
    if n_arr.ndim == 0:
        n_arr = np.full(nu_arr.shape, float(n_arr))
    if n_arr.shape != nu_arr.shape:
        raise ValueError(f"n 与 nu 形状不一致：n={n_arr.shape}，nu={nu_arr.shape}")

    sin_tp = n_air * np.sin(np.deg2rad(theta_deg)) / n_arr
    if np.any(sin_tp > 1.0):
        raise ValueError("全反射：sin(theta') > 1")
    cos_tp = np.sqrt(1.0 - sin_tp * sin_tp)
    sin_tpp = n_arr * sin_tp / n_sub
    if np.any(sin_tpp > 1.0):
        raise ValueError("全反射：sin(theta'') > 1")
    cos_tpp = np.sqrt(1.0 - sin_tpp * sin_tpp)
    cos_theta = np.cos(np.deg2rad(theta_deg))

    r1s = (n_air * cos_theta - n_arr * cos_tp) / (n_air * cos_theta + n_arr * cos_tp)
    r1p = (n_arr * cos_theta - n_air * cos_tp) / (n_arr * cos_theta + n_air * cos_tp)
    r2s = (n_arr * cos_tp - n_sub * cos_tpp) / (n_arr * cos_tp + n_sub * cos_tpp)
    r2p = (n_sub * cos_tp - n_arr * cos_tpp) / (n_sub * cos_tp + n_arr * cos_tpp)

    delta = phase_delta(nu_arr, t_um, n_arr, theta_deg, n_air)

    def two_beam(r1: np.ndarray, r2: np.ndarray) -> np.ndarray:
        r1i, r2i = r1 * r1, r2 * r2
        return r1i + (1.0 - r1i) ** 2 * r2i + 2.0 * (1.0 - r1i) * np.sqrt(r1i * r2i) * np.cos(delta)

    r_s = two_beam(r1s, r2s)
    r_p = two_beam(r1p, r2p)
    if pol == "s":
        return r_s
    if pol == "p":
        return r_p
    return 0.5 * (r_s + r_p)


def airy_reflectance(
    nu_cm1: np.ndarray | float,
    t_um: float,
    n: np.ndarray | float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
    pol: str = "avg",
) -> np.ndarray | float:
    """Airy 多光束反射率正模型 R_Airy(nu;t,n,theta,n_sub)（formulation.md (2.5)/(2.6)，一般模型）。

    以**强度**反射率写出 (2.6)：R = (R01 + R12 + 2√(R01R12) cosδ)/(1 + R01R12 + 2√(R01R12) cosδ)，
    R01=|r01|²、R12=|r12|² 为 s/p 平均强度反射率。反射相位跃变 φ 已吸收进 δ 的参考原点
    （与两光束模型 (2.8) 的 +cosδ 约定一致，故两模型**同极值位置**、仅差对比度/峰形/DC 基线，
    见 §3.5 / §13.2）。s/p 平均。
    """
    if pol not in {"s", "p", "avg"}:
        raise ValueError(f"pol 只能是 s/p/avg，得到 {pol!r}")
    nu_arr = np.asarray(nu_cm1, dtype=float)
    n_arr = np.asarray(n, dtype=float)
    if n_arr.ndim == 0:
        n_arr = np.full(nu_arr.shape, float(n_arr))
    if n_arr.shape != nu_arr.shape:
        raise ValueError(f"n 与 nu 形状不一致：n={n_arr.shape}，nu={nu_arr.shape}")

    sin_tp = n_air * np.sin(np.deg2rad(theta_deg)) / n_arr
    if np.any(sin_tp > 1.0):
        raise ValueError("全反射：sin(theta') > 1")
    cos_tp = np.sqrt(1.0 - sin_tp * sin_tp)
    sin_tpp = n_arr * sin_tp / n_sub
    if np.any(sin_tpp > 1.0):
        raise ValueError("全反射：sin(theta'') > 1")
    cos_tpp = np.sqrt(1.0 - sin_tpp * sin_tpp)
    cos_theta = np.cos(np.deg2rad(theta_deg))

    r1s = (n_air * cos_theta - n_arr * cos_tp) / (n_air * cos_theta + n_arr * cos_tp)
    r1p = (n_arr * cos_theta - n_air * cos_tp) / (n_arr * cos_theta + n_air * cos_tp)
    r2s = (n_arr * cos_tp - n_sub * cos_tpp) / (n_arr * cos_tp + n_sub * cos_tpp)
    r2p = (n_sub * cos_tp - n_arr * cos_tpp) / (n_sub * cos_tp + n_arr * cos_tpp)

    delta = np.asarray(phase_delta(nu_arr, t_um, n_arr, theta_deg, n_air), dtype=float)
    cos_d = np.cos(delta)

    def airy_intensity(r1: np.ndarray, r2: np.ndarray) -> np.ndarray:
        r1i = r1 * r1
        r2i = r2 * r2
        a = r1i + r2i
        b = 2.0 * np.sqrt(r1i * r2i)
        cc = 1.0 + r1i * r2i
        return (a + b * cos_d) / (cc + b * cos_d)

    r_s = airy_intensity(r1s, r2s)
    r_p = airy_intensity(r1p, r2p)
    if pol == "s":
        return r_s
    if pol == "p":
        return r_p
    return 0.5 * (r_s + r_p)


def _r1_pol_avg(n: float, theta_deg: float, n_air: float = N_AIR) -> float:
    """空气/外延层界面强度反射率 R1（s/p 平均）。"""
    tp = theta_prime(theta_deg, n, n_air)
    r1s, r1p = fresnel_interface(n_air, n, theta_deg, tp)
    return float(0.5 * (r1s * r1s + r1p * r1p))


def _r2_pol_avg(n: float, n_sub: float, theta_deg: float, n_air: float = N_AIR) -> float:
    """外延层/衬底界面强度反射率 R2（s/p 平均）。"""
    tp = theta_prime(theta_deg, n, n_air)
    tpp = theta_double_prime(tp, n, n_sub)
    r2s, r2p = fresnel_interface(n, n_sub, tp, tpp)
    return float(0.5 * (r2s * r2s + r2p * r2p))


# ---------------------------------------------------------------------------
# 多光束必要条件（§3，本问 Q1 核心）
# ---------------------------------------------------------------------------
def interface_reflectivity_product(
    n: float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
) -> dict[str, float]:
    """R01、R12、Rbar=sqrt(R01 R12)、finesse（formulation §3.1，N1）。"""
    rf = interface_reflectivities(n, n_sub, theta_deg, n_air)
    r01 = float(0.5 * (rf["R1"][0] + rf["R1"][1]))  # s/p 平均
    r12 = float(0.5 * (rf["R2"][0] + rf["R2"][1]))
    rbar = float(np.sqrt(max(r01, 0.0) * max(r12, 0.0)))
    # R2（formulation_v002）：精细度采用标准等厚干涉定义 F = π√R̄/(1−R̄)。
    # v001 实现 `π·R̄/(1−R̄)` 漏 √R̄ 为 bug（Rbar=0.0101 → 0.032，应得 ≈0.319）。
    finesse = float(np.pi * np.sqrt(rbar) / (1.0 - rbar)) if rbar < 1.0 else float("inf")
    return {"R01": r01, "R12": r12, "Rbar": rbar, "finesse": finesse}


def r12_from_amplitude(
    amplitude: float,
    r01: float,
) -> float | None:
    """由干涉幅值 A=2(1-R01)·sqrt(R01·R12) 反演 R12（formulation §3.1/§7.2）。

    A 为 (6.1) 干涉项的幅值（模型拟合后由 A=sqrt(C^2+S^2) 得到）。返回 R12；若幅值过小/不可逆返回 None。
    """
    if amplitude is None or amplitude <= 0.0:
        return None
    if r01 <= 0.0 or r01 >= 1.0:
        return None
    denom = 2.0 * (1.0 - r01) * np.sqrt(r01)
    if denom <= 0.0:
        return None
    r12 = (amplitude / denom) ** 2
    return float(r12) if r12 > 0.0 else None


def nsub_from_amplitude(
    amplitude: float,
    n: float,
    theta_deg: float,
    *,
    n_air: float = N_AIR,
    n_sub_max: float = 4.2,
    pol: str = "avg",
) -> dict:
    """由干涉幅值 A 反演衬底折射率 n̂_sub（formulation §7.2，C7；幅度弱辨识）。

    A = 2(1−R01)·sqrt(R01·R12) → R12 = (A/[2(1−R01)sqrt(R01)])²；
    再由 Fresnel R12(n, n_sub, θ') 对 n_sub 做单调二分反演。返回 {n_sub, R1, R2, amplitude}；
    若幅值过小/不可逆返回 n_sub=None（弱可辨识/回退文献取值）。
    """
    if amplitude is None or amplitude <= 0.0:
        return {"n_sub": None, "R1": None, "R2": None, "amplitude": amplitude}
    r1 = float(_r1_pol_avg(n, theta_deg, n_air))
    denom = 2.0 * (1.0 - r1)
    if denom <= 0.0 or r1 <= 0.0:
        return {"n_sub": None, "R1": r1, "R2": None, "amplitude": amplitude}
    r2_target = (amplitude / denom) ** 2 / r1
    if r2_target <= 0.0 or r2_target >= 0.5:
        return {"n_sub": None, "R1": r1, "R2": r2_target, "amplitude": amplitude}

    def r2_of_nsub(n_sub: float) -> float:
        return float(_r2_pol_avg(n, n_sub, theta_deg, n_air))

    try:
        from scipy.optimize import brentq

        nvec = np.linspace(n + 1e-6, n_sub_max, 400)
        rvec = np.array([r2_of_nsub(v) for v in nvec], dtype=float)
        diff = rvec - r2_target
        sign_changes = np.flatnonzero(diff[:-1] * diff[1:] <= 0)
        if sign_changes.size == 0:
            return {"n_sub": None, "R1": r1, "R2": r2_target, "amplitude": amplitude}
        idx0 = int(sign_changes[0])
        n_lo, n_hi = float(nvec[idx0]), float(nvec[idx0 + 1])
        n_sub_est = float(brentq(lambda v: r2_of_nsub(v) - r2_target, n_lo, n_hi, xtol=1e-9))
    except Exception:
        return {"n_sub": None, "R1": r1, "R2": r2_target, "amplitude": amplitude}
    return {"n_sub": n_sub_est, "R1": r1, "R2": r2_target, "amplitude": amplitude}


def coherence_order_limit(
    t_um: float,
    n: float,
    theta_deg: float,
    delta_nu_res: float = DELTA_NU_RES_CM1,
    n_air: float = N_AIR,
) -> dict:
    """N2：时间相干/相干长度 → 可达干涉级次上限（formulation (3.3)/(3.4)）。

    L_c = 1/(2*delta_nu_res)；m_max_coh = floor(L_c/(2*n*t*cosθ'))。
    """
    lc = 1.0 / (2.0 * delta_nu_res)  # cm
    lc_um = lc * 1e4  # 1 cm = 1e4 µm
    opd_single = 2.0 * n * t_um * cos_theta_prime(theta_deg, n, n_air)
    m_max = int(np.floor(lc_um / opd_single)) if opd_single > 0 else 0
    return {
        "coherence_length_um": lc_um,
        "opd_single_roundtrip_um": opd_single,
        "m_max_coh": m_max,
        "criterion_met": bool(m_max >= 2),
    }


def absorption_order_limit(
    t_um: float,
    n: float,
    nu_cm1: float,
    theta_deg: float,
    extinction_k: float = 0.0,
    n_air: float = N_AIR,
) -> dict:
    """N4：吸收限制 → 有效干涉级次（formulation (3.6)）。

    κ = 4π k ν t cosθ'；m_max_abs = floor(1/κ)。k≈0 时吸收不抑制（m_max_abs 极大）。
    """
    ctp = cos_theta_prime(theta_deg, n, n_air)
    kappa = 4.0 * np.pi * extinction_k * nu_cm1 * t_um * ctp
    if kappa <= 0.0 or not np.isfinite(kappa):
        m_max = int(1e9)  # k≈0：吸收可忽略，不抑制多光束
    else:
        m_max = int(np.floor(1.0 / kappa))
    return {
        "extinction_k": extinction_k,
        "kappa": float(kappa),
        "m_max_abs": m_max,
        "criterion_met": bool(m_max >= 2),
    }


def parallelism_angle_bound(
    lambda_um: float,
    n: float,
    theta_deg: float,
    beam_diameter_cm: float = BEAM_DIAMETER_CM,
    n_air: float = N_AIR,
) -> dict:
    """N3：界面近似平行判据（formulation (3.5)）。

    α << λ/(2 n D cosθ')。返回允许的最大楔角（rad/度）与是否满足给定 α。
    """
    ctp = cos_theta_prime(theta_deg, n, n_air)
    bound_rad = lambda_um * 1e-4 / (2.0 * n * beam_diameter_cm * ctp)  # λ[um]→cm：1um=1e-4 cm
    bound_deg = float(np.rad2deg(bound_rad))
    return {
        "alpha_bound_rad": float(bound_rad),
        "alpha_bound_deg": bound_deg,
        "criterion_met": bool(ALPHA_WEDGE_RAD < bound_rad),
        "note": "实际晶圆片含不平度/厚度梯度（C3），紧平行度压制高次、佐证两光束；不作硬门禁",
    }


def necessary_conditions(
    n: float,
    n_sub: float,
    theta_deg: float,
    t_um: float,
    *,
    amplitude: float | None,
    nu_cm1: float,
    delta_nu_res: float = DELTA_NU_RES_CM1,
    extinction_k: float = 0.0,
    lambda_um: float = 4.0,
) -> dict:
    """多光束必要条件 N1–N4 汇总判定（formulation §3.6，本问 Q1 核心）。

    返回每条必要条件的量化值与判定，以及总判定（N1–N4 全部满足才可能显著多光束）。
    """
    rp = interface_reflectivity_product(n, n_sub, theta_deg)
    r01 = rp["R01"]
    r12 = rp["R12"] if amplitude is None else (r12_from_amplitude(amplitude, r01) or rp["R12"])
    rbar = float(np.sqrt(max(r01, 0.0) * max(r12, 0.0)))
    # R2（formulation_v002）：F = π√R̄/(1−R̄)（标准等厚干涉精细度；v001 漏 √R̄ 已修正）。
    finesse = float(np.pi * np.sqrt(rbar) / (1.0 - rbar)) if rbar < 1.0 else float("inf")
    coh = coherence_order_limit(t_um, n, theta_deg, delta_nu_res)
    para = parallelism_angle_bound(lambda_um, n, theta_deg)
    absr = absorption_order_limit(t_um, n, nu_cm1, theta_deg, extinction_k)
    n1_met = rbar <= THETA_MB
    n2_met = coh["criterion_met"]
    n3_met = para["criterion_met"]
    n4_met = absr["criterion_met"]
    return {
        "N1": {
            "criterion": "Rbar=sqrt(R01*R12) <= theta_mb",
            "R01": r01,
            "R12": r12,
            "Rbar": rbar,
            "finesse": finesse,
            "theta_mb": THETA_MB,
            "criterion_met": n1_met,
        },
        "N2": coh,
        "N3": para,
        "N4": absr,
        "all_conditions_met": bool(n1_met and n2_met and n3_met and n4_met),
        "note": "N1–N4 为标准+阈值登记（formulation §3.6）；全部满足才可能显著多光束，任一不满足都可能抑制多光束",
    }


# ---------------------------------------------------------------------------
# 数据加载与预处理（C6/C8）
# ---------------------------------------------------------------------------
def load_attachment(path: Path | str) -> dict:
    """读取附件 xlsx：列『波数 (cm-1)』『反射率 (%)』。

    返回 {nu: 升序 ndarray, r_obs: 0-1 归一 ndarray}。附件 2 波数列为降序，读入后重排为升序。
    """
    import pandas as pd

    df = pd.read_excel(str(path))
    if df.shape[1] != 2:
        raise ValueError(f"附件应有 2 列，实际为 {df.shape[1]} 列：{path}")
    nu = df.iloc[:, 0].astype(float).to_numpy()
    r_pct = df.iloc[:, 1].astype(float).to_numpy()
    order = np.argsort(nu)
    nu_sorted = nu[order]
    r_sorted = r_pct[order]
    return {
        "nu": np.asarray(nu_sorted, dtype=float),
        "r_pct": np.asarray(r_sorted, dtype=float),
        "r_obs": np.asarray(r_sorted / 100.0, dtype=float),
    }


def preprocess_spectrum(
    nu: np.ndarray,
    r_obs: np.ndarray,
    *,
    exclude_band: tuple[float, float] | None = None,
    anomaly_upper_pct: float = ANOMALY_UPPER_PCT,
    weight_anomaly: float = 0.05,
) -> dict:
    """预处理：归一化、吸收带剔除/降权、异常点标记/降权（B1-B3/C6/C8）。

    exclude_band：模型不适用谱段（硅多声子带 / SiC Reststrahlen），该区 w=0。
    返回 {nu, r_obs, weights, mask_valid, anomaly_idx, excluded_idx, log}。原始数据只读。
    """
    nu_arr = np.asarray(nu, dtype=float)
    r_obs_arr = np.asarray(r_obs, dtype=float)
    if nu_arr.shape != r_obs_arr.shape:
        raise ValueError("nu 与 r_obs 形状不一致")

    if exclude_band is not None:
        excl_mask = (nu_arr >= exclude_band[0]) & (nu_arr <= exclude_band[1])
    else:
        excl_mask = np.zeros(nu_arr.shape, dtype=bool)

    r_pct = r_obs_arr * 100.0
    anomaly_upper = r_pct > anomaly_upper_pct
    anomaly_lower = r_pct < ANOMALY_LOWER_PCT
    anomaly_base = anomaly_upper | anomaly_lower

    weights = np.ones(nu_arr.shape, dtype=float)
    weights[excl_mask] = 0.0
    weights[anomaly_base] = weight_anomaly

    log = {
        "n_points": int(nu_arr.size),
        "exclude_band": list(exclude_band) if exclude_band is not None else None,
        "n_excluded": int(np.count_nonzero(excl_mask)),
        "anomaly_rule": f"R% > {anomaly_upper_pct} 或 R% < {ANOMALY_LOWER_PCT}（超界）",
        "n_anomaly": int(np.count_nonzero(anomaly_base)),
        "n_anomaly_upper": int(np.count_nonzero(anomaly_upper)),
        "n_anomaly_lower": int(np.count_nonzero(anomaly_lower)),
        "weight_anomaly": weight_anomaly,
        "n_valid_points": int(np.count_nonzero(weights > 0.0)),
        "note": "原始数据只读；反射率 %->0-1 归一；吸收带 w=0；异常点降权 w=weight_anomaly",
    }
    return {
        "nu": nu_arr,
        "r_obs": r_obs_arr,
        "weights": weights,
        "mask_valid": weights > 0.0,
        "anomaly_idx": np.flatnonzero(anomaly_base),
        "excluded_idx": np.flatnonzero(excl_mask),
        "log": log,
    }


def restrict_band(nu_cm1: np.ndarray, lo: float, hi: float) -> tuple[np.ndarray, np.ndarray]:
    nu_arr = np.asarray(nu_cm1, dtype=float)
    mask = (nu_arr >= lo) & (nu_arr <= hi)
    return nu_arr[mask], mask


# ---------------------------------------------------------------------------
# 主反演：基线-干涉分解 + 一维相位频率扫描（baseline-robust variable projection，§6，复用 prob02）
# ---------------------------------------------------------------------------
def vp_basis_deg() -> tuple[int, int]:
    return BASELINE_POLY_DEG, ENVELOPE_POLY_DEG


def _poly_scale_center(nu_cm1: np.ndarray, nu_ref: float | None = None) -> tuple[float, float]:
    nu_arr = np.asarray(nu_cm1, dtype=float)
    if nu_ref is not None:
        nu0 = float(nu_ref)
    else:
        nu0 = float(np.mean(nu_arr))
    half = max(float(np.max(nu_arr) - nu0), float(nu0 - np.min(nu_arr)), 1e-12)
    return nu0, half


def poly_basis_cheb(nu_cm1: np.ndarray, deg: int, nu0: float, half: float) -> np.ndarray:
    """中心化/正交化的多项式基（Chebyshev Vandomer：ν→[-1,1] 后的 Chebyshev 多项式）。"""
    x = (np.asarray(nu_cm1, dtype=float) - nu0) / half
    return np.polynomial.chebyshev.chebvander(x, deg)


def vp_design_matrix(
    nu_cm1: np.ndarray,
    n_nu: np.ndarray,
    theta_deg: float,
    t_um: float,
    p: int,
    q: int,
    nu0: float,
    half: float,
) -> np.ndarray:
    """基线-干涉分解设计矩阵 Φ(t)（formulation (6.4)）。

    列 = [B 多项式(0..p), C 多项式(0..q)*cos δ, S 多项式(0..q)*sin δ]。
    δ(ν) = 4π×1e-4·t·g(ν)（(2.7)；φ 相位跃变吸收进 C/S 系数）。
    """
    g = np.asarray(phase_function(nu_cm1, n_nu, theta_deg), dtype=float)
    delta = 4.0 * np.pi * 1e-4 * float(t_um) * g
    b_poly = poly_basis_cheb(nu_cm1, p, nu0, half)
    c_poly = poly_basis_cheb(nu_cm1, q, nu0, half)
    s_poly = poly_basis_cheb(nu_cm1, q, nu0, half)
    cos_d = np.cos(delta)[:, None]
    sin_d = np.sin(delta)[:, None]
    return np.concatenate([b_poly, c_poly * cos_d, s_poly * sin_d], axis=1)


def vp_linear_ls(phi: np.ndarray, r_obs: np.ndarray, weights: np.ndarray) -> dict:
    """对固定 t 求解加权线性最小二乘 β（formulation (6.4)），返回 β、残差平方和、秩、条件数。"""
    w = np.clip(np.asarray(weights, dtype=float), 0.0, None)
    sq_w = np.sqrt(w)
    a = sq_w[:, None] * np.asarray(phi, dtype=float)
    b = sq_w * np.asarray(r_obs, dtype=float)
    beta, _, rank, sv = np.linalg.lstsq(a, b, rcond=None)
    residual = a @ beta - b
    rss = float(np.dot(residual, residual))
    cond = float(sv[0] / sv[-1]) if sv.size and sv[-1] > 0 else float("inf")
    return {"beta": beta, "rss": rss, "rank": int(rank), "cond": cond}


def vp_angle_j(
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    n_nu: np.ndarray,
    theta_deg: float,
    weights: np.ndarray,
    t_um: float,
    p: int,
    q: int,
    nu0: float,
    half: float,
) -> dict:
    phi = vp_design_matrix(nu_cm1, n_nu, theta_deg, t_um, p, q, nu0, half)
    return vp_linear_ls(phi, r_obs, weights)


def _scan_angle(
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    n_nu: np.ndarray,
    theta_deg: float,
    weights: np.ndarray,
    t_range: tuple[float, float],
    t_step: float,
    p: int,
    q: int,
    nu0: float,
    half: float,
) -> dict:
    t_lo, t_hi = float(t_range[0]), float(t_range[1])
    n_points = int(np.floor((t_hi - t_lo) / t_step)) + 1
    t_grid = t_lo + np.arange(n_points) * t_step
    j_vals = np.empty(n_points, dtype=float)
    for i, t in enumerate(t_grid):
        j_vals[i] = vp_angle_j(nu_cm1, r_obs, n_nu, theta_deg, weights, float(t), p, q, nu0, half)["rss"]
    idx = int(np.argmin(j_vals))
    t_hat = float(t_grid[idx])
    j_min = float(j_vals[idx])
    t_refined = t_hat
    if 0 < idx < n_points - 1:
        _, b, _ = t_grid[idx - 1], t_grid[idx], t_grid[idx + 1]
        ja, jb, jc = j_vals[idx - 1], j_vals[idx], j_vals[idx + 1]
        denom = ja - 2.0 * jb + jc
        if abs(denom) > 1e-15:
            shift = 0.5 * (ja - jc) / denom
            t_refined = float(b + shift * t_step)
    return {
        "t_grid": t_grid,
        "j_vals": j_vals,
        "t_hat": t_hat,
        "j_min": j_min,
        "t_refined": t_refined,
        "idx_min": idx,
    }


def variable_projection_scan(
    nu_list: list[np.ndarray],
    r_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    *,
    t_range: tuple[float, float] = T_SCAN_RANGE_SI,
    t_step: float = T_SCAN_STEP,
    p: int = BASELINE_POLY_DEG,
    q: int = ENVELOPE_POLY_DEG,
    nu_ref: float | None = None,
    shared: bool = True,
) -> dict:
    """主干反演：基线-干涉分解 + 一维相位频率扫描（formulation (6.5)）。

    shared=True：两角共享 t（主判据，B/C/S 按角度独立、t 全局共享），J(t)=Σ_k J_k(t)。
    shared=False：每角独立 t，各自扫描（一致性检验/报告每角 t̂_k）。
    """
    if len({len(nu_list), len(r_list), len(theta_list), len(n_list), len(weights_list)}) != 1:
        raise ValueError("nu/r/theta/n/weights 列表长度不一致")
    if not nu_list:
        raise ValueError("至少需要一个角度")
    n_angles = len(nu_list)
    if nu_ref is None:
        all_nu = np.concatenate([np.asarray(nu, dtype=float) for nu in nu_list])
        nu0, half = _poly_scale_center(all_nu)
    else:
        nu0 = float(nu_ref)
        half = max(float(np.max(np.concatenate([np.asarray(nu, dtype=float) for nu in nu_list])) - nu0), 1e-12)

    results: list[dict] = []
    for k in range(n_angles):
        results.append(
            _scan_angle(
                nu_list[k], r_list[k], n_list[k], theta_list[k], weights_list[k],
                t_range, t_step, p, q, nu0, half,
            )
        )

    if not shared:
        return {
            "mode": "independent",
            "shared": False,
            "angle_scan": results,
            "t_hat_per_angle": [r["t_refined"] for r in results],
            "t_refined_per_angle": [r["t_refined"] for r in results],
            "J_min_per_angle": [float(r["j_vals"][r["idx_min"]]) for r in results],
            "nu_ref": nu0,
            "half_width": half,
            "p": p,
            "q": q,
        }

    ref = results[0]
    t_grid = ref["t_grid"]
    j_shared = np.zeros(t_grid.size, dtype=float)
    for r in results:
        j_shared += r["j_vals"]

    out = {
        "mode": "shared",
        "shared": True,
        "nu_ref": nu0,
        "half_width": half,
        "p": p,
        "q": q,
        "t_grid": t_grid,
        "J_shared": j_shared,
        "angle_scan": results,
        "n_angles": n_angles,
        "J_min_per_angle": [float(r["j_vals"][r["idx_min"]]) for r in results],
    }
    idx = int(np.argmin(j_shared))
    out["t_hat"] = float(t_grid[idx])
    out["J_min_shared"] = float(j_shared[idx])
    t_refined = out["t_hat"]
    if 0 < idx < t_grid.size - 1:
        _, b, _ = t_grid[idx - 1], t_grid[idx], t_grid[idx + 1]
        ja, jb, jc = j_shared[idx - 1], j_shared[idx], j_shared[idx + 1]
        denom = ja - 2.0 * jb + jc
        if abs(denom) > 1e-15:
            t_refined = float(b + 0.5 * (ja - jc) / denom * t_step)
    out["t_hat_refined"] = t_refined
    angle_fits: list[dict] = []
    for k in range(n_angles):
        phi = vp_design_matrix(nu_list[k], n_list[k], theta_list[k], t_refined, p, q, nu0, half)
        fit = vp_linear_ls(phi, r_list[k], weights_list[k])
        beta = fit["beta"]
        b_cols = p + 1
        c_cols = q + 1
        c_beta = beta[b_cols : b_cols + c_cols]
        s_beta = beta[b_cols + c_cols : b_cols + 2 * c_cols]
        nu_ref_pt = np.asarray([AMP_REF_NU_CM1], dtype=float)
        c_poly = np.polynomial.chebyshev.chebvander((nu_ref_pt - nu0) / half, q)
        s_poly = np.polynomial.chebyshev.chebvander((nu_ref_pt - nu0) / half, q)
        c_val = float((c_poly @ c_beta)[0])
        s_val = float((s_poly @ s_beta)[0])
        amplitude = float(np.hypot(c_val, s_val))
        angle_fits.append({"theta_deg": theta_list[k], "beta": beta, "amplitude": amplitude, "rss": fit["rss"]})
    out["angle_fits"] = angle_fits
    out["amplitude_ref_um"] = AMP_REF_NU_CM1
    return out


def profile_ci_from_Jcurve(
    t_grid: np.ndarray,
    j_vals: np.ndarray,
    t_hat: float,
    *,
    n_tot: int,
    n_params: int,
    chi2: float = 3.841,
) -> dict | None:
    """轮廓似然 95% CI（formulation §7.5：由 J(t) 在 t̂ 附近抛物近似/夹逼区间）。

    区间边界 t 满足 J(t) - J(t̂) = chi2_{0.95,1}·sigma²，sigma² = J(t̂)/(n_tot - n_params)。
    """
    j = np.asarray(j_vals, dtype=float)
    t = np.asarray(t_grid, dtype=float)
    idx = int(np.argmin(j))
    j_min = float(j[idx])
    df = n_tot - n_params
    if df <= 0:
        return None
    sigma2 = j_min / df
    threshold = float(chi2) * sigma2
    t_low = None
    t_high = None
    for i in range(idx, 0, -1):
        if j[i] >= j_min + threshold:
            t0, t1 = t[i], t[i + 1]
            j0, j1 = j[i], j[i + 1]
            if j1 != j0:
                frac = (threshold - (j0 - j_min)) / (j1 - j0)
                t_low = float(t0 + frac * (t1 - t0))
            else:
                t_low = float(t1)
            break
    for i in range(idx, len(j) - 1):
        if j[i] >= j_min + threshold:
            t0, t1 = t[i - 1], t[i]
            j0, j1 = j[i - 1], j[i]
            if j1 != j0:
                frac = (threshold - (j0 - j_min)) / (j1 - j0)
                t_high = float(t0 + frac * (t1 - t0))
            else:
                t_high = float(t0)
            break
    if t_low is None or t_high is None:
        return None
    halfwidth = 0.5 * (t_high - t_low)
    return {
        "t_low": t_low,
        "t_high": t_high,
        "halfwidth_um": halfwidth,
        "halfwidth_percent": halfwidth / t_hat * 100.0 if t_hat > 0 else float("inf"),
        "sigma2": sigma2,
        "n_tot": int(n_tot),
        "n_params": int(n_params),
        "chi2": chi2,
    }


def two_angle_ftest_vp(shared_scan: dict, indep_scan: dict, *, n_tot: int, alpha: float = 0.05) -> dict:
    """两角一致性嵌套 F 检验（formulation §7.2，对相位-频率拟合）。

    M_shared：两角共享 t（SS_shared = J_min_shared）；M_indep：两角独立 t（SS_indep = Σ J_min_k）。
    df1 = 2-1 = 1；df2 = n_tot - n_params_indep。
    """
    from scipy.stats import f as f_dist

    ss_shared = float(shared_scan["J_min_shared"])
    ss_indep = float(sum(shared_scan["J_min_per_angle"]))
    df1 = 2 - 1
    p = int(shared_scan["p"])
    q = int(shared_scan["q"])
    n_angles = int(shared_scan.get("n_angles", 2))
    coef_per_angle = (p + 1) + 2 * (q + 1)
    n_params_indep = n_angles * coef_per_angle + n_angles
    df2 = int(n_tot - n_params_indep)
    if df2 <= 0 or ss_indep <= 0:
        f_stat = float("inf")
        p_value = 0.0
        f_crit = float("inf")
    else:
        f_stat = ((ss_shared - ss_indep) / df1) / (ss_indep / df2)
        p_value = float(1.0 - f_dist.cdf(f_stat, df1, df2))
        f_crit = float(f_dist.ppf(1.0 - alpha, df1, df2))
    accepted = bool(f_stat <= f_crit)
    t1, t2 = indep_scan["t_hat_per_angle"]
    tbar = 0.5 * (t1 + t2)
    eps12 = abs(t1 - t2) / tbar * 100.0 if tbar > 0 else float("inf")
    return {
        "status": "PASS" if accepted else "FAIL",
        "F_stat": f_stat,
        "F_critical": f_crit,
        "p_value": p_value,
        "alpha": alpha,
        "df1": df1,
        "df2": df2,
        "accept_shared_t": accepted,
        "ss_shared": ss_shared,
        "ss_indep": ss_indep,
        "t_theta10_um": t1,
        "t_theta15_um": t2,
        "t_mean_um": tbar,
        "eps12_percent": eps12,
    }


def multibeam_improvement(
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    t_um: float,
    n_nu: np.ndarray,
    n_sub: float,
    theta_deg: float,
) -> dict:
    """多光束判定主判据：Airy 模型相对两光束模型的全谱残差改善率 η_mb（formulation §7.2/§7.1）。

    η_mb = (SSE_2b - SSE_Airy)/SSE_2b × 100%（两光束为 basline，Airy 为多光束模型，二者均用
    物理正模型 Fresnel DC 基线）。η_mb ≤ τ_mb（默认 10%）则两光束适用；否则需 Airy 修正（§7.4）。
    """
    r_2b = np.asarray(forward_reflectance(nu_cm1, t_um, n_nu, n_sub, theta_deg), dtype=float)
    r_airy = np.asarray(airy_reflectance(nu_cm1, t_um, n_nu, n_sub, theta_deg), dtype=float)
    sse_2b = float(np.sum((r_obs - r_2b) ** 2))
    sse_airy = float(np.sum((r_obs - r_airy) ** 2))
    rmse_2b = float(np.sqrt(np.mean((r_obs - r_2b) ** 2)))
    rmse_airy = float(np.sqrt(np.mean((r_obs - r_airy) ** 2)))
    eta = (sse_2b - sse_airy) / sse_2b * 100.0 if sse_2b > 0 else 0.0
    return {
        "sse_two_beam": sse_2b,
        "sse_airy": sse_airy,
        "rmse_two_beam": rmse_2b,
        "rmse_airy": rmse_airy,
        "improvement_percent": float(eta),
        "needs_multibeam_correction": bool(eta > TAU_MB_PERCENT),
        "threshold_percent": TAU_MB_PERCENT,
    }


# ---------------------------------------------------------------------------
# 接口探针（秒级）
# ---------------------------------------------------------------------------
def _near(a: float, b: float, tol: float = 1e-3) -> bool:
    return abs(float(a) - float(b)) / max(abs(float(b)), 1e-12) < tol


def airy_two_beam_limit_gap(n_sub: float, theta_deg: float, n_epi: float, t_um: float, nu_array: np.ndarray) -> float:
    """Airy 模型与两光束模型的反射率 RMS 差 |ΔR|（§13.2：验证多光束相对两光束可忽略）。

    返回 RMS|R_Airy - R_2b|（无量纲反射率）。Rbar 越小该差值越小（O(Rbar²)）。
    """
    r_2b = np.asarray(forward_reflectance(nu_array, t_um, n_epi, n_sub, theta_deg), dtype=float)
    r_airy = np.asarray(airy_reflectance(nu_array, t_um, n_epi, n_sub, theta_deg), dtype=float)
    return float(np.sqrt(np.mean((r_2b - r_airy) ** 2)))


def run_probes() -> dict[str, bool]:
    """接口探针：核验 formulation_v002 的数值例与代码机械（秒级小计算，不运行完整数据集）。

    覆盖：硅 Sellmeier、SiC Sellmeier、Airy↔两光束极限、极值位置不变性（L17）、
    必要条件 N1-N4（含 R2：finesse=π√R̄/(1−R̄) 修正值）、变量投影往返（shared/indep）、
    基线阶数稳健、n_sub 幅值弱辨识、轮廓似然 CI、两角嵌套 F 检验、多光束改善率（η_mb）量级。
    """
    checks: dict[str, bool] = {}

    # 1. 硅 Sellmeier：n(5um)≈3.4221、n(3000 cm^-1=3.333um)≈3.4293、n(2.5um)≈3.4394（formulation §5.1/§13.2）
    n5 = float(np.asarray(sellmeier_si(5.0), dtype=float))
    checks["si_sellmeier_n5um"] = _near(n5, 3.4221)
    n_l3 = float(np.asarray(sellmeier_si(3.3333), dtype=float))
    checks["si_sellmeier_n3p333"] = _near(n_l3, 3.4293, 2e-3)
    n_l25 = float(np.asarray(sellmeier_si(2.5), dtype=float))
    checks["si_sellmeier_n2p5um"] = _near(n_l25, 3.4394, 2e-3)

    # 2. SiC Sellmeier：n(5um)≈2.4954（prob02 核验值，供 SiC §7.3 对照）
    n_sic5 = float(np.asarray(sellmeier_n4hsi(5.0), dtype=float))
    checks["sic_sellmeier_n5um"] = _near(n_sic5, 2.4954)

    # 3. 硅色散模型类型：N-SE / N-SE-delta / N-const
    nu_hi = np.array([4000.0, 3000.0, 2500.0])
    n_hi = np.asarray(dispersion_epi_si(nu_hi, model="N-SE"), dtype=float)
    checks["si_dispersion_nse"] = bool(
        np.allclose(n_hi, np.asarray(sellmeier_si(1e4 / nu_hi), dtype=float), rtol=1e-9, atol=1e-12)
    )
    n_delta = np.asarray(dispersion_epi_si(nu_hi, model="N-SE-delta", c_disp=1.005), dtype=float)
    checks["si_dispersion_nse_delta_scale"] = bool(np.allclose(n_delta, n_hi * 1.005, atol=1e-12))
    n_const = np.asarray(dispersion_epi_si(nu_hi, model="N-const"), dtype=float)
    checks["si_dispersion_nconst_constant"] = bool(np.allclose(n_const, n_const[0], atol=1e-12))

    # 4. Airy↔两光束极限：Rbar 小 → |ΔR|（RMS）随 Rbar² 减小（§13.2 量化多光束可忽略）。
    #    n_sub 越接近 n_epi（Δn 小 → R12 小 → Rbar 小）则 Airy 与两光束差越小。
    nu_airy = np.linspace(2000.0, 4000.0, 200)
    n_epi_a = float(np.mean(np.asarray(dispersion_epi_si(nu_airy, model="N-SE"), dtype=float)))
    gap_low = airy_two_beam_limit_gap(3.6, 10.0, n_epi_a, 6.9, nu_airy)  # Δn 小（R12 小）
    gap_high = airy_two_beam_limit_gap(3.05, 10.0, n_epi_a, 6.9, nu_airy)  # Δn 大（R12 大）
    checks["airy_two_beam_limit_small"] = bool(gap_low < 3e-3)
    checks["airy_two_beam_limit_smaller_than_large"] = bool(gap_low <= gap_high)

    # 5. 极值位置不变性（L17 独立验证，§3.5）：无吸收时 dR_Airy/dδ=0 当且仅当 sinδ=0 → δ=mπ
    #    验证 Airy 反射率在 δ=mπ 处取极值（dR/dδ≈0），且与 R01·R12 无关。
    delta_grid = np.linspace(0.0, 4.0 * np.pi, 4001)
    r01a, r12a = 0.30, 0.002  # 硅带内典型值
    r01b, r12b = 0.301, 0.001  # 另一组（Rbar 不同）
    # 由 Airy (2.6)：R = (A+B cosδ)/(C+B cosδ)，A=R01+R12, B=2sqrt(R01 R12), C=1+R01 R12
    def airy_curve(r01, r12, d):
        a = r01 + r12
        b = 2.0 * np.sqrt(r01 * r12)
        c = 1.0 + r01 * r12
        return (a + b * np.cos(d)) / (c + b * np.cos(d))

    r_a = airy_curve(r01a, r12a, delta_grid)
    r_b = airy_curve(r01b, r12b, delta_grid)
    # 极值位置：δ=mπ（等间距 π）。一阶离散差分符号变化所在的 δ 应落在 mπ 附近。
    # 检查每个 m*pi 网格点处是否为局部极值（用局部 3 点差分判符号变化）。
    def extremum_at(d):  # d 为标量，检查是否局部极值
        i = int(np.argmin(np.abs(delta_grid - d)))
        if i <= 0 or i >= delta_grid.size - 1:
            return False
        return (r_a[i] - r_a[i - 1]) * (r_a[i + 1] - r_a[i]) <= 0

    ok_extremum = all(extremum_at(m * np.pi) for m in range(1, 4))
    checks["airy_extremum_at_m_pi"] = bool(ok_extremum)

    # 6. 必要条件 N1-N4 数值（硅带内，n=3.43，t≈6.9，幅值弱辨识 R12 取范围）
    rp = interface_reflectivity_product(3.4293, 3.05, 10.0)
    checks["r01_si_approx_0p30"] = _near(rp["R01"], 0.301, 5e-2)
    r12_from_amp = r12_from_amplitude(0.014, rp["R01"])  # q=0 常数包络 A≈0.014
    rbar_low = float(np.sqrt(rp["R01"] * r12_from_amp)) if r12_from_amp else None
    checks["rbar_si_le_theta_mb"] = bool(rbar_low is not None and rbar_low <= THETA_MB)
    # R2（formulation_v002）：finesse 须为 π√R̄/(1−R̄)。Rbar≈0.0101 → ≈0.319（v001 bug 给出 0.032）。
    f_correct = float(np.pi * np.sqrt(rp["Rbar"]) / (1.0 - rp["Rbar"]))
    checks["r2_finesse_formula_correct"] = bool(_near(rp["finesse"], f_correct, 1e-6))
    # 幅度弱辨识 Rbar≈0.0101 对应的 finesse 应≈0.319，而非 v001 bug 的 0.032。
    f_bar = float(np.pi * np.sqrt(rbar_low) / (1.0 - rbar_low)) if rbar_low is not None else None
    checks["r2_finesse_magnitude_0p319"] = bool(f_bar is not None and _near(f_bar, 0.319, 5e-2))
    nc = necessary_conditions(3.4293, 3.05, 10.0, 6.9, amplitude=0.014, nu_cm1=3000.0)
    checks["n1_criterion_met"] = bool(nc["N1"]["criterion_met"])
    checks["n2_coherence_criterion_met"] = bool(nc["N2"]["criterion_met"])
    checks["n3_parallelism_criterion_met"] = bool(nc["N3"]["criterion_met"])
    checks["n4_absorption_criterion_met"] = bool(nc["N4"]["criterion_met"])
    checks["nc_all_conditions_met"] = bool(nc["all_conditions_met"])

    # 7. 变量投影往返（硅合成谱，双角，shared/indep；§6 主方法）
    band_nu = np.linspace(2000.0, 4000.0, 400)
    band_n = np.asarray(dispersion_epi_si(band_nu, model="N-SE"), dtype=float)
    t_true = 6.9
    n_sub_true = 3.05
    p, q = 3, 1
    rng = np.random.default_rng(7)

    def synth_band(theta):
        base = np.asarray(forward_reflectance(band_nu, t_true, band_n, n_sub_true, theta), dtype=float)
        trend = 0.006 + 0.0008 * (band_nu - 2000.0) / 2000.0
        return base + trend + rng.normal(0.0, 1e-4, band_nu.shape)

    r_a = synth_band(10.0)
    r_b = synth_band(15.0)
    w_ones = np.ones(band_nu.shape)
    scan_shared = variable_projection_scan(
        [band_nu, band_nu], [r_a, r_b], [10.0, 15.0], [band_n, band_n],
        [w_ones, w_ones], t_range=(2.0, 12.0), t_step=0.05, p=p, q=q, shared=True,
    )
    checks["vp_roundtrip_shared_t"] = bool(abs(scan_shared["t_hat_refined"] - t_true) / t_true < 1e-2)
    scan_indep = variable_projection_scan(
        [band_nu, band_nu], [r_a, r_b], [10.0, 15.0], [band_n, band_n],
        [w_ones, w_ones], t_range=(2.0, 12.0), t_step=0.05, p=p, q=q, shared=False,
    )
    checks["vp_roundtrip_indep_t"] = bool(
        all(abs(v - t_true) / t_true < 1e-2 for v in scan_indep["t_hat_per_angle"])
    )

    # 8. 基线阶数稳健（p=1..6）
    t_p_vals = []
    for pp in (1, 3, 6):
        sc = variable_projection_scan(
            [band_nu], [r_a], [10.0], [band_n], [w_ones],
            t_range=(2.0, 12.0), t_step=0.05, p=pp, q=q, shared=True,
        )
        t_p_vals.append(sc["t_hat_refined"])
    checks["vp_baseline_degree_stable"] = bool((max(t_p_vals) - min(t_p_vals)) / t_true < 5e-2)

    # 9. n_sub 幅度弱辨识（由幅值 A=sqrt(C²+S²) 反演，弱对比度）
    amp0 = scan_shared["angle_fits"][0]["amplitude"]
    n_c = float(np.interp(3000.0, band_nu, band_n))
    nsub_est = nsub_from_amplitude(amp0, n_c, 10.0)
    checks["nsub_from_amplitude_finite"] = bool(nsub_est["n_sub"] is None or np.isfinite(nsub_est["n_sub"]))

    # 10. 轮廓似然 95% CI（§7.5）
    n_tot_probe = int(2 * r_a.size)
    coef_probe = (p + 1) + 2 * (q + 1)
    ci_probe = profile_ci_from_Jcurve(
        scan_shared["t_grid"], scan_shared["J_shared"], scan_shared["t_hat_refined"],
        n_tot=n_tot_probe, n_params=2 * coef_probe + 1,
    )
    checks["vp_profile_ci_positive"] = bool(ci_probe is not None and ci_probe["halfwidth_um"] > 0.0)

    # 11. 两角一致性嵌套 F 检验（§7.2）：合成数据共享 t → 接受共享 t
    ftest_probe = two_angle_ftest_vp(scan_shared, scan_indep, n_tot=n_tot_probe, alpha=0.05)
    checks["vp_ftest_accept_shared"] = bool(ftest_probe["accept_shared_t"])

    # 12. 多光束改善率 η_mb 量级（§7.2）：两光束适用（η_mb ≪ τ_mb=10%）
    mb = multibeam_improvement(band_nu, r_a, scan_shared["t_hat_refined"], band_n, n_sub_true, 10.0)
    checks["mb_improvement_small"] = bool(mb["improvement_percent"] < TAU_MB_PERCENT)

    # 13. SiC 重新判定（§7.3）：Rbar_SiC = sqrt(R01 R12) 对照值 ≤ θ_mb
    rbar_sic = float(np.sqrt(SIC_R01_REF * SIC_R12_REF))
    checks["sic_rbar_le_theta_mb"] = bool(rbar_sic <= THETA_MB)

    return checks


if __name__ == "__main__":  # pragma: no cover - 仅用于手动/探针入口
    results = run_probes()
    for name, passed in results.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    raise SystemExit(0 if all(results.values()) else 1)
