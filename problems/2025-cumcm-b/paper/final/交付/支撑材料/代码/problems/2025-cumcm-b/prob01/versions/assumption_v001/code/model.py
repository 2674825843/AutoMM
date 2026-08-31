"""prob01 两光束干涉测厚模型（formulation_v001 / assumption_v001）。

实现 `formulations/formulation_v001/formulation.md` 的公式：

- (2.2)  Snell 折射角：sin(theta') = sin(theta) / n（n_air = 1）
- (2.6)  几何光程差：Delta = 2 t sqrt(n^2 - sin^2(theta))
- (2.8)  相位差：delta = 4 pi * 1e-4 * n * t[um] * nu[cm^-1] * cos(theta')
- (3.1)-(3.3) Fresnel s/p 界面强度反射率 R1、R2
- (3.5)/(3.6) 两光束反射率正模型 R(nu; t, n(nu), theta, n_sub)
- (3.8)  同型相邻极值波数间隔 Delta_nu = 1e4 / (2 n t cos(theta'))
- (3.10) 厚度反演 t[um] = 1e4 / (2 n cos(theta') Delta_nu[cm^-1])
- (3.11)-(3.13) 色散化相位函数 g(nu) 与厚度 t = 1e4 / (2 (g(nu_{m+2}) - g(nu_m)))
- (4.1)  4H-SiC Sellmeier 色散（lambda <= 5 um）

色散处理：n 允许是标量或与 nu 同形的数组；色散显著时 R1、R2、theta'、delta 逐点由
n(nu) 计算（formulation.md §3.2 一般形式），弱色散反演（方法 A）按 §3.4 取谱段均值 n_eff。

单位约定（与 parameters.yaml / formula_validation.md 一致）：
t [um]、nu [cm^-1]、lambda [um] = 1e4 / nu、theta [deg]（三角函数内部转 rad）、delta [rad]。
"""

from __future__ import annotations

import numpy as np

# ---- 物理常量与谱段边界（parameters.yaml 登记值） ----
N_AIR: float = 1.0  # A9：空气折射率
SELLMEIER_BOUNDARY_UM: float = 5.0  # A5/L09：Sellmeier 适用上界（波长）
NU_RANGE_CM1: tuple[float, float] = (400.0, 4000.0)  # 题面谱段
RESTSTRAHLEN_EXCLUDE_CM1: tuple[float, float] = (700.0, 1000.0)  # A7：近 Reststrahlen 区（模型不适用）
WEAK_DISPERSION_BAND_CM1: tuple[float, float] = (2000.0, 4000.0)  # 弱色散/Sellmeier 有效区（方法 A 谱段）


def sellmeier_n4hsi(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """4H-SiC Sellmeier 折射率（formulation.md (4.1)，来源 L09）。

    n^2 = 6.79485 + 0.15558 / (lambda^2 - 0.03535) - 0.02296 * lambda^2，lambda 单位为 um。
    仅适用于 lambda <= 5 um（nu >= 2000 cm^-1）；超界调用由调用方负责（见 dispersion_epi）。
    """
    lam2 = np.asarray(lambda_um, dtype=float) ** 2
    return np.sqrt(6.79485 + 0.15558 / (lam2 - 0.03535) - 0.02296 * lam2)


def dispersion_epi(
    lambda_um: np.ndarray | float,
    *,
    extension: str = "constant",
    boundary_um: float = SELLMEIER_BOUNDARY_UM,
) -> np.ndarray | float:
    """外延层色散折射率 n(lambda)（A5）。

    - lambda <= boundary_um：4H-SiC Sellmeier（(4.1)，L09）；
    - lambda >  boundary_um：无现成体材料公式（workflow_state warning 已登记），按
      ``extension`` 策略延续。默认 ``constant``：取 n(boundary_um) 常数延续，并在调用方
      记录该谱段为 extrapolated（prob01 仅作合成验证；prob02 用数据反演/分谱段确定）。
    """
    values = np.asarray(lambda_um, dtype=float)
    scalar = values.ndim == 0
    arr = np.atleast_1d(values)
    result = np.empty_like(arr)
    in_range = arr <= boundary_um
    result[in_range] = np.asarray(sellmeier_n4hsi(arr[in_range]), dtype=float)
    boundary_n = float(np.asarray(sellmeier_n4hsi(boundary_um), dtype=float))
    if extension == "constant":
        result[~in_range] = boundary_n
    else:
        raise ValueError(f"未知色散延伸策略：{extension}")
    return float(result[0]) if scalar else result


def nu_to_lambda(nu_cm1: np.ndarray | float) -> np.ndarray | float:
    """波长换算：lambda[um] = 1e4 / nu[cm^-1]。"""
    return 1e4 / np.asarray(nu_cm1, dtype=float)


def theta_prime(theta_deg: float, n: float, n_air: float = N_AIR) -> float:
    """外延层内折射角 theta'（formulation.md (2.2)），返回度数。"""
    value = n_air * np.sin(np.deg2rad(theta_deg)) / n
    if value > 1.0:
        raise ValueError(f"全反射：sin(theta') = {value:.6f} > 1（n 过小或入射角过大）")
    return float(np.rad2deg(np.arcsin(value)))


def cos_theta_prime(theta_deg: float, n: float, n_air: float = N_AIR) -> float:
    """cos(theta') = sqrt(1 - (n_air sin(theta) / n)^2)（(2.2) 的余弦形式）。"""
    value = n_air * np.sin(np.deg2rad(theta_deg)) / n
    if value > 1.0:
        raise ValueError(f"全反射：sin(theta') = {value:.6f} > 1")
    return float(np.sqrt(1.0 - value * value))


def theta_double_prime(theta_prime_deg: float, n: float, n_sub: float) -> float:
    """衬底内折射角 theta''（formulation.md (2.3)），返回度数。"""
    value = n * np.sin(np.deg2rad(theta_prime_deg)) / n_sub
    if value > 1.0:
        raise ValueError(f"全反射：sin(theta'') = {value:.6f} > 1")
    return float(np.rad2deg(np.arcsin(value)))


def optical_path_difference(t_um: float, n: float, theta_deg: float, n_air: float = N_AIR) -> float:
    """几何光程差 Delta = 2 t sqrt(n^2 - n_air^2 sin^2(theta))（formulation.md (2.6)），单位 um。"""
    return 2.0 * t_um * np.sqrt(n * n - n_air * n_air * np.sin(np.deg2rad(theta_deg)) ** 2)


def phase_delta(
    nu_cm1: np.ndarray | float,
    t_um: float,
    n: np.ndarray | float,
    theta_deg: float,
    n_air: float = N_AIR,
) -> np.ndarray | float:
    """两光束相位差 delta = 4 pi * 1e-4 * n(nu) * t[um] * nu[cm^-1] * cos(theta'(nu))（(2.8)），单位 rad。

    n 可以是标量或与 nu 同形的数组（色散情形逐点计算 cos(theta')）。
    """
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
    """色散化相位函数 g(nu) = n(nu) * nu * cos(theta'(nu))（formulation.md (3.11)）。"""
    nu_arr = np.asarray(nu_cm1, dtype=float)
    n_arr = np.asarray(n_nu, dtype=float)
    cosv = np.sqrt(np.clip(1.0 - (n_air * np.sin(np.deg2rad(theta_deg)) / n_arr) ** 2, 0.0, 1.0))
    return nu_arr * n_arr * cosv


def forward_reflectance(
    nu_cm1: np.ndarray | float,
    t_um: float,
    n: np.ndarray | float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
    pol: str = "avg",
) -> np.ndarray | float:
    """两光束反射率正模型 R(nu; t, n(nu), theta, n_sub)（formulation.md (3.5)/(3.6)）。

    n 为标量或与 nu 同形的数组；R1、R2、theta'、delta 逐点由 n(nu) 计算。
    无吸收适用谱段内 R 应满足 0 <= R <= 1（能量守恒，见 formula_validation §4）。
    pol：'s' / 'p' / 'avg'（未指定偏振测量取 s/p 平均 (3.6)）。
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

    # 界面 1：空气 -> 外延层（(3.1)）
    r1s = (n_air * cos_theta - n_arr * cos_tp) / (n_air * cos_theta + n_arr * cos_tp)
    r1p = (n_arr * cos_theta - n_air * cos_tp) / (n_arr * cos_theta + n_air * cos_tp)
    # 界面 2：外延层 -> 衬底（(3.2)）
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


def fresnel_interface(
    n_incident: float,
    n_transmitted: float,
    theta_incident_deg: float,
    theta_transmitted_deg: float,
) -> tuple[float, float]:
    """单个界面的 s/p 振幅反射系数（formulation.md (3.1)-(3.2) 的通用形式）。

    返回 (r_s, r_p)；n_incident / n_transmitted 为入射/透射介质折射率，
    theta_incident_deg / theta_transmitted_deg 为入射角/透射角（度）。
    """
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
    """界面 1（空气/外延层）与界面 2（外延层/衬底）的 s/p 强度反射率（(3.1)-(3.3)）。

    返回 {"R1": (R1_s, R1_p), "R2": (R2_s, R2_p)}。
    """
    tp = theta_prime(theta_deg, n, n_air)
    tpp = theta_double_prime(tp, n, n_sub)
    r1s, r1p = fresnel_interface(n_air, n, theta_deg, tp)
    r2s, r2p = fresnel_interface(n, n_sub, tp, tpp)
    return {"R1": (r1s * r1s, r1p * r1p), "R2": (r2s * r2s, r2p * r2p)}


def two_beam_envelope(
    n: float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
    pol: str = "avg",
) -> tuple[float, float]:
    """两光束模型反射率理论包络 [R_min, R_max]（(3.5) 中 cos(delta)=±1 的极值）。

    与公式 (3.5) 精确一致：center = R1 + (1-R1)^2 R2，amp = 2(1-R1) sqrt(R1 R2)。
    用于核验模型反射率极值落在理论包络内（能量守恒，formula_validation §4）。
    """
    reflect = interface_reflectivities(n, n_sub, theta_deg, n_air)
    r1 = {"s": reflect["R1"][0], "p": reflect["R1"][1]}
    r2 = {"s": reflect["R2"][0], "p": reflect["R2"][1]}
    keys = ("s", "p") if pol == "avg" else (pol,)
    lows: list[float] = []
    highs: list[float] = []
    for key in keys:
        r1i, r2i = r1[key], r2[key]
        center = r1i + (1.0 - r1i) ** 2 * r2i
        amp = 2.0 * (1.0 - r1i) * np.sqrt(r1i * r2i)
        lows.append(center - amp)
        highs.append(center + amp)
    return float(np.mean(lows)), float(np.mean(highs))


def thickness_from_delta_nu(delta_nu_cm1: float, n: float, theta_deg: float, n_air: float = N_AIR) -> float:
    """厚度反演 t[um] = 1e4 / (2 n cos(theta') Delta_nu[cm^-1])（formulation.md (3.10)，A3）。"""
    if delta_nu_cm1 <= 0.0:
        raise ValueError(f"Delta_nu 必须为正，得到 {delta_nu_cm1}")
    return 1e4 / (2.0 * n * cos_theta_prime(theta_deg, n, n_air) * delta_nu_cm1)


def thickness_from_phase_gap(g_m_plus_2: float, g_m: float) -> float:
    """色散化厚度 t[um] = 1e4 / (2 (g(nu_{m+2}) - g(nu_m)))（formulation.md (3.13)）。

    g 由 phase_function 计算（单位 cm^-1）；同型相邻极值对应 g(nu_{m+2}) - g(nu_m) = 1/(2t[cm])。
    """
    gap = g_m_plus_2 - g_m
    if gap <= 0.0:
        raise ValueError(f"同型相邻极值的 g 间隔必须为正，得到 {gap:.6e}")
    return 1e4 / (2.0 * gap)


def find_extrema(nu_cm1: np.ndarray, values: np.ndarray, kind: str = "both") -> dict[str, np.ndarray]:
    """定位干涉极值（formulation.md (3.7)：极值条件 delta = m*pi）。

    使用 scipy.signal.find_peaks；kind 为 'max'/'min'/'both'。
    返回 {"max": array(索引), "min": array(索引)}。
    """
    from scipy.signal import find_peaks

    nu_arr = np.asarray(nu_cm1, dtype=float)
    val_arr = np.asarray(values, dtype=float)
    if nu_arr.shape != val_arr.shape or nu_arr.size < 3:
        raise ValueError("极值定位需要等长的 nu/values 数组且至少 3 个点")
    maxima, _ = find_peaks(val_arr)
    minima, _ = find_peaks(-val_arr)
    if kind == "max":
        return {"max": maxima, "min": np.array([], dtype=int)}
    if kind == "min":
        return {"min": minima, "max": np.array([], dtype=int)}
    return {"max": maxima, "min": minima}


def same_type_spacings(extrema_nu: np.ndarray) -> np.ndarray:
    """同型相邻极值（峰-峰或谷-谷）的波数间隔序列（formulation.md (3.8)）。"""
    extrema_nu = np.asarray(extrema_nu, dtype=float)
    if extrema_nu.size < 2:
        return np.array([], dtype=float)
    return np.diff(extrema_nu)


def invert_from_spacing(
    nu_cm1: np.ndarray,
    reflectance: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray | float,
    kind: str,
) -> dict[str, float]:
    """方法 A（极值间隔法，formulation.md §3.6）：由同型相邻极值间隔反演厚度。

    返回 {"delta_nu_median": ..., "t_spacing_um": ..., "n_eff": ..., "extrema_count": ...}；
    n_eff 取弱色散谱段内 n 的平均值；(3.9)/(3.10) 以常数 n 近似，色散修正见 invert_phase_method。
    """
    extrema = find_extrema(nu_cm1, reflectance, kind=kind)
    positions = extrema[kind]
    nu_ext = np.asarray(nu_cm1, dtype=float)[positions]
    spacings = same_type_spacings(nu_ext)
    if spacings.size < 1:
        raise ValueError(f"{kind} 同型极值少于 2 个，无法估计 Delta_nu")
    delta_nu = float(np.median(spacings))
    n_eff = float(np.mean(np.asarray(n_nu, dtype=float)))
    t_um = thickness_from_delta_nu(delta_nu, n_eff, theta_deg)
    return {"delta_nu_median": delta_nu, "t_spacing_um": t_um, "n_eff": n_eff, "extrema_count": int(positions.size)}


def invert_phase_method(
    nu_cm1: np.ndarray,
    reflectance: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray,
    kind: str,
) -> dict[str, float]:
    """色散化反演（formulation.md (3.13)）：由同型相邻极值处相位函数差直接求 t。

    (3.12) 中 m 为干涉级次，同型相邻极值（峰-峰或谷-谷）对应级次 m -> m+2，即
    同型极值列表中的相邻两项（delta 相差 2*pi）。对每个相邻同型极值对计算
    t_k = 1e4 / (2 (g(nu_{k+1}) - g(nu_k)))，取中位数；弱色散极限退化为 (3.8)/(3.9)
    （见 formula_validation §3）。返回 delta_g_median（cm^-1）与相位法厚度。
    """
    extrema = find_extrema(nu_cm1, reflectance, kind=kind)
    positions = extrema[kind]
    nu_ext = np.asarray(nu_cm1, dtype=float)[positions]
    n_ext = np.asarray(n_nu, dtype=float)[positions]
    g_ext = np.asarray(phase_function(nu_ext, n_ext, theta_deg), dtype=float)
    if g_ext.size < 2:
        raise ValueError(f"{kind} 同型极值少于 2 个，无法使用相位函数法")
    delta_g = np.diff(g_ext)
    t_k = np.asarray([thickness_from_phase_gap(g_ext[i + 1], g_ext[i]) for i in range(delta_g.size)], dtype=float)
    return {
        "t_phase_um": float(np.median(t_k)),
        "delta_g_median": float(np.median(delta_g)),
        "g_pairs": int(t_k.size),
        "g_monotonic": bool(np.all(delta_g > 0)),
    }


def residual_forward(
    t_um: float,
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    n_nu: np.ndarray,
    n_sub: float,
    theta_deg: float,
    pol: str = "avg",
) -> np.ndarray:
    """全谱 NLS 残差向量：r(t) = R_obs(nu) - R_model(nu; t, n(nu), theta, n_sub)（formulation.md §3.6 方法 B）。"""
    model = np.asarray(forward_reflectance(nu_cm1, t_um, n_nu, n_sub, theta_deg, pol=pol), dtype=float)
    return np.asarray(r_obs, dtype=float) - model


def invert_nls(
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray,
    n_sub: float,
    t0_um: float,
    pol: str = "avg",
    bounds: tuple[float, float] = (1e-4, 1e4),
    ftol: float = 1e-10,
    xtol: float = 1e-10,
    gtol: float = 1e-10,
    max_nfev: int = 200,
) -> dict:
    """方法 B（全谱非线性最小二乘，formulation.md §3.6）：单参数 t 最小二乘。

    使用 scipy.optimize.least_squares；t0 由方法 A 提供解析初值（避免局部极小，见
    formula_validation §6）。返回结果字段 + t_um。
    """
    from scipy.optimize import least_squares

    result = least_squares(
        lambda t: residual_forward(float(t), nu_cm1, r_obs, n_nu, n_sub, theta_deg, pol=pol),
        x0=float(t0_um),
        bounds=bounds,
        ftol=ftol,
        xtol=xtol,
        gtol=gtol,
        max_nfev=max_nfev,
    )
    return {
        "t_um": float(result.x[0]),
        "success": bool(result.success),
        "status": int(result.status),
        "cost": float(result.cost),
        "optimality": float(result.optimality),
        "nfev": int(result.nfev),
        "message": str(result.message),
        "t0_um": float(t0_um),
        "max_residual": float(np.max(np.abs(result.fun))) if result.fun.size else None,
        "rmse": float(np.sqrt(np.mean(result.fun**2))) if result.fun.size else None,
    }


def phase_period_estimate(nu_cm1: np.ndarray, n_nu: np.ndarray, theta_deg: float, n_air: float = N_AIR) -> float:
    """厚度周期歧义估计（um）：cos(delta) 对 t 的周期 = 1 / (2*1e-4*n_c*nu_c*cos(theta'))。

    谱段中心 (nu_c, n_c) 处估计；用于多初值 NLS 的候选初值布点（formula_validation §6 周期歧义）。
    """
    nu_c = float(np.mean(np.asarray(nu_cm1, dtype=float)))
    n_c = float(np.mean(np.asarray(n_nu, dtype=float)))
    return 1.0 / (2.0 * 1e-4 * n_c * nu_c * cos_theta_prime(theta_deg, n_c, n_air))


def invert_nls_multistart(
    nu_cm1: np.ndarray,
    r_obs: np.ndarray,
    theta_deg: float,
    n_nu: np.ndarray,
    n_sub: float,
    t0_um: float,
    *,
    alt_t0_um: float | None = None,
    pol: str = "avg",
    bounds: tuple[float, float] = (1e-4, 1e4),
    ftol: float = 1e-10,
    xtol: float = 1e-10,
    gtol: float = 1e-10,
    max_nfev: int = 200,
) -> dict:
    """方法 B 多初值全谱 NLS：规避 cos(delta) 周期歧义造成的局部极小（formula_validation §6）。

    从 t0、t0 ± period、以及可选 alt_t0（相位法初值）出发，取 rmse 最小者作为最优解；
    全部起步结果写入 starts 供 solver_status 审计。phase 法解析初值 + 多初值保证收敛到全局最小。
    """
    period = phase_period_estimate(nu_cm1, n_nu, theta_deg)
    starts = [t0_um, t0_um - period, t0_um + period]
    if alt_t0_um is not None:
        starts.append(alt_t0_um)
    fits: list[dict] = []
    for start in starts:
        fits.append(
            invert_nls(
                nu_cm1,
                r_obs,
                theta_deg,
                n_nu,
                n_sub,
                float(start),
                pol=pol,
                bounds=bounds,
                ftol=ftol,
                xtol=xtol,
                gtol=gtol,
                max_nfev=max_nfev,
            )
        )
    best = min(fits, key=lambda item: item["rmse"] if item["rmse"] is not None else float("inf"))
    return {"best": best, "starts": fits, "period_um_estimate": float(period)}


def dispersion_from_nu(nu_cm1: np.ndarray, extension: str = "constant") -> np.ndarray:
    """按波数网格计算外延层色散 n(nu)（nu -> lambda -> n，见 dispersion_epi）。"""
    lam = nu_to_lambda(nu_cm1)
    return np.asarray(dispersion_epi(lam, extension=extension), dtype=float)


def restrict_band(nu_cm1: np.ndarray, lo: float, hi: float) -> tuple[np.ndarray, np.ndarray]:
    """截取 [lo, hi] cm^-1 谱段，返回 (nu_masked, mask)。"""
    nu_arr = np.asarray(nu_cm1, dtype=float)
    mask = (nu_arr >= lo) & (nu_arr <= hi)
    return nu_arr[mask], mask


def gen_synthetic_spectrum(
    nu_cm1: np.ndarray,
    t_true_um: float,
    n_sub: float,
    theta_deg: float,
    *,
    n_air: float = N_AIR,
    pol: str = "avg",
    dispersion_extension: str = "constant",
) -> np.ndarray:
    """由正模型生成合成反射率谱 R_clean(nu)（prob01 无实测数据，用于数值验证公式与算法）。"""
    n_nu = dispersion_from_nu(nu_cm1, extension=dispersion_extension)
    return np.asarray(forward_reflectance(nu_cm1, t_true_um, n_nu, n_sub, theta_deg, n_air=n_air, pol=pol), dtype=float)


def add_gaussian_noise(r_clean: np.ndarray, sigma_percent: float, rng: np.random.Generator) -> np.ndarray:
    """以反射率百分比噪声添加高斯扰动（prob02 数据噪声鲁棒性预演；sigma_percent=0 时原样返回）。"""
    if sigma_percent <= 0.0:
        return np.asarray(r_clean, dtype=float)
    sigma = sigma_percent / 100.0
    return np.asarray(r_clean, dtype=float) + rng.normal(0.0, sigma, size=np.asarray(r_clean).shape)


def evaluate_spacing_theory(t_um: float, n_eff: float, theta_deg: float, n_air: float = N_AIR) -> float:
    """理论同型相邻极值间隔 Delta_nu = 1e4 / (2 n t cos(theta'))（(3.8)/(3.10)），单位 cm^-1。"""
    return 1e4 / (2.0 * n_eff * t_um * cos_theta_prime(theta_deg, n_eff, n_air))


def n_band_mean(nu_cm1: np.ndarray, extension: str = "constant") -> float:
    """谱段内色散折射率均值（方法 A 的 n_eff）。"""
    return float(np.mean(dispersion_from_nu(nu_cm1, extension=extension)))


def run_probes() -> dict[str, bool]:
    """接口探针：核验公式数值例（formula_validation.md 与 formulation 探针值）。

    供实现阶段静态检查与 compute.py --self-check 使用；全部为秒级小计算。
    """
    checks: dict[str, bool] = {}

    # 1. Sellmeier：n(5 um) ≈ 2.495（formula_validation 探针值）
    n5 = float(np.asarray(sellmeier_n4hsi(5.0), dtype=float))
    checks["sellmeier_n5um"] = abs(n5 - 2.495) / 2.495 < 1e-2

    # 2. 等价性 (2.5) = (2.6)：2 n t cos(theta') == 2 t sqrt(n^2 - sin^2(theta))
    eq_ok = True
    for n_val in (2.4, 2.6, 3.0):
        for theta in (0.0, 10.0, 15.0):
            lhs = 2.0 * n_val * cos_theta_prime(theta, n_val)
            rhs = 2.0 * np.sqrt(n_val * n_val - np.sin(np.deg2rad(theta)) ** 2)
            eq_ok = eq_ok and abs(lhs - rhs) < 1e-9 * max(1.0, abs(lhs))
    checks["path_equivalence_2_5_2_6"] = eq_ok

    # 3. 理论间隔：t=10 um、n=2.6、theta=10° -> Delta_nu ≈ 193 cm^-1（数量级核验）
    delta_nu_theory = evaluate_spacing_theory(10.0, 2.6, 10.0)
    checks["delta_nu_magnitude"] = abs(delta_nu_theory - 193.0) / 193.0 < 0.05

    # 4. 正模型物理边界：R in [0, 1]（formula_validation §4；n=2.6, n_sub=3.0, theta=10°）
    nu = np.linspace(400.0, 4000.0, 1801)
    n_nu = dispersion_from_nu(nu)
    r_clean = gen_synthetic_spectrum(nu, 10.0, 3.0, 10.0)
    # 常数 n=2.6 例：与 (3.5) 理论包络精确一致（formula_validation §4 文档值 [0.16, 0.24] 为近似例，
    # 精确 s/p 平均包络为 [0.1498, 0.2519]，见 implementation.md 说明）
    r_const = np.asarray(forward_reflectance(nu, 10.0, 2.6, 3.0, 10.0), dtype=float)
    env_low, env_high = two_beam_envelope(2.6, 3.0, 10.0)
    checks["forward_R_in_unit"] = bool(
        np.all(r_clean >= 0.0) and np.all(r_clean <= 1.0) and np.all(r_const >= 0.0) and np.all(r_const <= 1.0)
    )
    checks["forward_R_within_envelope"] = bool(
        np.min(r_const) >= env_low - 1e-9 and np.max(r_const) <= env_high + 1e-9
    )
    checks["forward_R_oscillates"] = bool(np.ptp(r_clean) > 0.01)

    # 5. 往返反演（小型端到端）：方法 A 基线、相位法、方法 B 恢复 t_true
    t_true = 10.0
    spacing_ok, phase_ok, nls_ok = True, True, True
    for theta in (10.0, 15.0):
        r = gen_synthetic_spectrum(nu, t_true, 3.0, theta)
        sub_nu, sub_mask = restrict_band(nu, *WEAK_DISPERSION_BAND_CM1)
        sub_r = r[sub_mask]
        sub_n = n_nu[sub_mask]
        spacing = invert_from_spacing(sub_nu, sub_r, theta, sub_n, kind="max")
        phase = invert_phase_method(sub_nu, sub_r, theta, sub_n, kind="max")
        nls = invert_nls_multistart(
            sub_nu, sub_r, theta, sub_n, 3.0, t0_um=spacing["t_spacing_um"], alt_t0_um=phase["t_phase_um"]
        )["best"]
        # 方法 A (3.9) 忽略色散引入系统偏差（A3 文档化，~4%），按基线容忍 5%
        spacing_ok = spacing_ok and abs(spacing["t_spacing_um"] - t_true) / t_true < 5e-2
        # 相位法 (3.13) 与 NLS 为色散修正主方法，严格 1%
        phase_ok = phase_ok and abs(phase["t_phase_um"] - t_true) / t_true < 1e-2
        nls_ok = nls_ok and abs(nls["t_um"] - t_true) / t_true < 1e-2
    checks["roundtrip_spacing_baseline"] = spacing_ok
    checks["roundtrip_phase_method"] = phase_ok
    checks["roundtrip_nls"] = nls_ok
    return checks


if __name__ == "__main__":  # pragma: no cover - 仅用于手动/探针入口
    results = run_probes()
    for name, passed in results.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    raise SystemExit(0 if all(results.values()) else 1)
