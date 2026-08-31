"""prob02 实测反射率谱厚度反演模型（formulation_v003 / assumption_v001）。

实现 `formulations/formulation_v003/formulation.md` 的公式（v002 修订版）。本版主方法由
「全谱幅值 NLS」改为「基线-干涉分解 + 一维相位频率扫描（variable projection）」：

- (2.1)  Snell 折射角：sin(theta') = sin(theta)/n（n_air = 1）
- (2.2)  光程差 Delta = 2 t sqrt(n^2 - sin^2(theta))；相位差 delta = 4pi*1e-4*n*t*nu*cos(theta')
- (2.3)-(2.4) 两光束反射率正模型 R(nu;t,n(nu),theta,n_sub)，s/p 平均
- (3.1)-(3.2) 反演谱段截断 nu_inv=[2000,4000]（Sellmeier 已知区，B6）；权重 w^inv（Reststrahlen w=0、
               异常点 w=w_anom、nu<2000 w=0 截断）
- (4.1)  4H-SiC Sellmeier（nu>=nu_c / lam<=5um，L09）——主反演带内唯一模型 N-SE
- (4.2)  N-SE-delta：Sellmeier×c_disp（带内色散灵敏）；N-const：常数 n 基线（B10 对照）；
         lambda>5um（nu<2000）n_ref 锚点插值仅作背景/Δt_inv_band 全谱诊断，不进入主反演
- (5.1)-(5.7) **主反演＝基线-干涉分解 + 一维相位频率扫描（variable projection）**：R=B(ν)+C(ν)cosδ+S(ν)sinδ，
         B/C/S 用中心化正交化多项式基（v003）；对固定 t 线性 LS，对 t 一维扫描取全局最小；t 与 n_sub 解耦
- (5.8)-(5.9) t=1/(2×1e-4·Δg)（相位频率/周期→厚度）
- (6.1)-(6.3) 极值间距、色散相位法、厚度周期歧义（M2/M3 初值/交叉验证）
- §6.4  物理正模型 NLS（含基线 + Fresnel 幅度）局部交叉校验（M1-P1/P2），起点 t̂
- (7.1)  两角一致性嵌套 F 检验（对相位-频率拟合的 M_shared 共享 t vs M_indep 每角独立 t）
- (7.2)-(7.3) 色散敏感性（带内 N-SE/N-SE-δ）+ 谱段截断影响 Δt_inv_band；n_sub 幅值弱辨识/解耦诊断
- (7.4)-(7.6) 噪声 95% CI（轮廓似然，由 J(t) 曲线）、异常点影响、多光束诊断

单位约定（与 parameters.yaml / formula_validation.md 一致）：
t [um]、nu [cm^-1]、lambda [um]=1e4/nu、theta [deg]（三角内转 rad）、delta [rad]、delta_nu [cm^-1]。

本模块为可复用/无副作用核心；`compute.py` 为 CLI，`probe.py` 为秒级接口探针。
实现阶段只做静态检查与小型探针，不运行完整数据集（由 supervised worker 在 computation 阶段执行）。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# ---- 物理常量与谱段边界（parameters.yaml 登记值，权威来源） ----
N_AIR: float = 1.0  # A9/B5：空气折射率
SELLMEIER_BOUNDARY_UM: float = 5.0  # B6/L09：Sellmeier 适用上界（波长）
VC_CM1: float = 2000.0  # B6：色散分界波数（lambda_c = 5 um，即 Sellmeier 有效下界 nu_c）
NU_RANGE_CM1: tuple[float, float] = (400.0, 4000.0)  # 题面谱段
RESTSTRAHLEN_EXCLUDE_CM1: tuple[float, float] = (700.0, 1000.0)  # B3：近 Reststrahlen 区（模型不适用）
INV_BAND_CM1: tuple[float, float] = (2000.0, 4000.0)  # 主反演谱段 nu_inv（Sellmeier 已知区，B6/v002 修订）
RELIABLE_BAND_CM1: tuple[float, float] = INV_BAND_CM1  # 兼容别名：方法 A/相位法/周期初值也在该带内
LOW_BAND_CM1: tuple[float, float] = (400.0, 700.0)  # 低频谱段（Fischer/SiC 远红外，B6）
ANOMALY_UPPER_PCT: float = 100.0  # B2：反射率 >100% 判定为异常点
ANOMALY_LOWER_PCT: float = 0.0  # B2：下界（物理下限，防御性标记）
N_SUB_INIT: float = 2.55  # B7/v002：n_sub 联合反演初值（实测带内强偏好 n_sub≈2.58）
N_SUB_BOUNDS: tuple[float, float] = (2.4, 4.0)  # B7/v002：n_sub 边界（重掺 SiC 衬底折射率合理区间）
DELTA_C_DISP: float = 0.005  # v002 §4.2/§7.2：Sellmeier 系数可复现性扰动半宽（0.5%）

# ---- v003 基线-干涉分解 + 一维相位频率扫描（variable projection）登记参数 ----
BASELINE_POLY_DEG: int = 3  # B(ν) 基线多项式阶数 p（formulation §5.5：默认 3，计算前固定）
ENVELOPE_POLY_DEG: int = 1  # C(ν)/S(ν) 包络多项式阶数 q（formulation §5.5：默认 1，计算前固定）
T_SCAN_RANGE: tuple[float, float] = (3.0, 20.0)  # 主反演一维扫描区间 [t_lo,t_hi]（§6.2/parameters.yaml）
T_SCAN_STEP: float = 0.01  # 扫描步长（≤0.01µm，全局极小捕获与唯一性分辨率，parameters.yaml t_scan_step）
N_SUB_AMP_INIT: float = 2.58  # n_sub 幅度弱辨识初值（formulation §5.1 由幅值 A≈0.0040 反演；B7/L26）
AMP_REF_NU_CM1: float = 3000.0  # 取干涉幅值 A=√(C²+S²) 的代表波数（带内中心，L09 Sellmeier 已知区）

# 色散锚点文件（n_ref(lam)）：Sellmeier<=5um + Fischer>=17um；5-17um 缺口为文档化临时插值。
_DEFAULT_ANCHOR = Path(__file__).resolve().parent / "data" / "n_ref_anchor.csv"


# ---------------------------------------------------------------------------
# 色散模型（B6）
# ---------------------------------------------------------------------------
def sellmeier_n4hsi(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """4H-SiC Sellmeier 折射率 n(lambda)（formulation.md (4.1)，L09）。

    n^2 = 6.79485 + 0.15558/(lambda^2 - 0.03535) - 0.02296*lambda^2，lambda 单位 um。
    仅适用于 lambda <= SELLMEIER_BOUNDARY_UM；超界由 dispersion_epi 负责切换到 n_ref。
    """
    lam2 = np.asarray(lambda_um, dtype=float) ** 2
    return np.sqrt(6.79485 + 0.15558 / (lam2 - 0.03535) - 0.02296 * lam2)


def fischer_n4hsi(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """Fischer et al. 2017，4H-SiC n(o) 远红外（refractiveindex.info，系数 [6.055, 2.669, 167.8]）。

    n^2 = 6.055 + 2.669*lambda^2/(lambda^2 - 167.8)，lambda 单位 um，适用于 17-150 um。
    极点在 lambda^2=167.8（约 12.95 um，即 Reststrahlen 横向声子共振），故仅 lambda>=17 um 有效。
    """
    lam2 = np.asarray(lambda_um, dtype=float) ** 2
    return np.sqrt(6.055 + 2.669 * lam2 / (lam2 - 167.8))


def load_n_ref_anchor(path: Path | str | None = None) -> tuple[np.ndarray, np.ndarray]:
    """载入 n_ref 锚点表（lambda_um, n_ref）。

    数据来源登记：
      - lambda<=5um：n = Sellmeier（L09 / Wang et al. 2013 4H-SiC，n(e) 0.405-2.33um、n(o) 到 5um）
      - lambda>=17um：n = Fischer et al. 2017 4H-SiC n(o)（17-150um，refractiveindex.info 系数 [6.055,2.669,167.8]）
      - 5-17um：文献/数据缺口（B6 待 L26 全文取数），模型在 5um 与 17um 锚点间做单调插值（临时代理）。
    返回按波长升序的 (lambda_um, n_ref)。
    """
    path = Path(path) if path else Path(_DEFAULT_ANCHOR)
    if not path.exists():
        raise FileNotFoundError(f"找不到 n_ref 锚点文件：{path}")
    arr = np.loadtxt(path, delimiter=",", comments="#", usecols=(0, 1))
    lam = arr[:, 0].astype(float)
    n = arr[:, 1].astype(float)
    order = np.argsort(lam)
    return lam[order], n[order]


def interpolate_n_ref(
    lambda_um: np.ndarray,
    anchor_path: Path | str | None = None,
) -> np.ndarray:
    """n_ref(lambda) 在锚点间做单调（PCHIP）插值（formulation (4.2) 的 n_ref(nu)）。

    PCHIP 保证单调性与无过冲，避免线性折角；对超出锚点范围的 lambda 做边界常值（不外推）。
    """
    from scipy.interpolate import PchipInterpolator

    lam_anchor, n_anchor = load_n_ref_anchor(anchor_path)
    values = np.asarray(lambda_um, dtype=float)
    interp = PchipInterpolator(lam_anchor, n_anchor, extrapolate=False)
    result = np.full(values.shape, np.nan, dtype=float)
    inside = (values >= lam_anchor[0]) & (values <= lam_anchor[-1])
    result[inside] = interp(values[inside])
    result[values < lam_anchor[0]] = float(n_anchor[0])
    result[values > lam_anchor[-1]] = float(n_anchor[-1])
    return result


def dispersion_epi(
    nu_cm1: np.ndarray | float,
    *,
    model: str = "N-SE",
    c_disp: float = 1.0,
    anchor_path: Path | str | None = None,
) -> np.ndarray | float:
    """外延层色散折射率 n(nu)（formulation_v002 (4.1)-(4.2)，B6）。

    模型：
      - N-SE（主）：nu>=nu_c 用 Sellmeier（L09）；nu<nu_c 用 n_ref(lam) 插值（L26 初值，仅作背景/
        Δt_inv_band 全谱诊断）。主反演只查询 nu_inv=[2000,4000]，该带内退化为纯 Sellmeier。
      - N-SE-delta：N-SE 全谱乘以 c_disp（用于带内色散灵敏度，§7.2；c_disp=1±delta_c_disp）。
      - N-const（基线）：常数 n=Sellmeier(5um)（prob01 方法 A 近似，B10 对照，不列入 Δt_disp 候选集）。
    nu 与 lambda 换算：lambda[um]=1e4/nu。c_disp=1 时为 N-SE（主）。
    """
    if model not in {"N-SE", "N-SE-delta", "N-const"}:
        raise ValueError(f"未知色散模型：{model!r}")
    nu_arr = np.atleast_1d(np.asarray(nu_cm1, dtype=float))
    scalar = np.ndim(nu_cm1) == 0
    lam = nu_to_lambda(nu_arr)

    if model == "N-const":
        n_vc = float(np.asarray(sellmeier_n4hsi(SELLMEIER_BOUNDARY_UM), dtype=float))
        result = np.full(nu_arr.shape, n_vc, dtype=float)
    else:
        result = np.empty_like(nu_arr)
        sell_region = nu_arr >= VC_CM1
        if np.any(sell_region):
            result[sell_region] = np.asarray(sellmeier_n4hsi(lam[sell_region]), dtype=float)
        ref_region = ~sell_region
        if np.any(ref_region):
            result[ref_region] = np.asarray(interpolate_n_ref(lam[ref_region], anchor_path), dtype=float)
        if model == "N-SE-delta":
            result = result * c_disp

    return float(result[0]) if scalar else result


def nu_to_lambda(nu_cm1: np.ndarray | float) -> np.ndarray | float:
    """波长换算：lambda[um] = 1e4 / nu[cm^-1]。"""
    return 1e4 / np.asarray(nu_cm1, dtype=float)


def lambda_to_nu(lambda_um: np.ndarray | float) -> np.ndarray | float:
    """波数换算：nu[cm^-1] = 1e4 / lambda[um]。"""
    return 1e4 / np.asarray(lambda_um, dtype=float)


# ---------------------------------------------------------------------------
# 几何 / 相位（B5，继承 prob01）
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
# Fresnel 正模型（B4，继承 prob01）
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
    """两光束反射率正模型 R(nu;t,n(nu),theta,n_sub)（formulation.md (2.3)/(2.4)）。

    n 为标量或与 nu 同形数组；R1、R2、theta'、delta 逐点由 n(nu) 计算。
    Returns 无量纲 0-1 强度反射率。pol 为 's'/'p'/'avg'。
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


def two_beam_envelope(
    n: float,
    n_sub: float,
    theta_deg: float,
    n_air: float = N_AIR,
    pol: str = "avg",
) -> tuple[float, float]:
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


# ---------------------------------------------------------------------------
# 厚度反演（B8-B10）
# ---------------------------------------------------------------------------
def thickness_from_delta_nu(delta_nu_cm1: float, n: float, theta_deg: float, n_air: float = N_AIR) -> float:
    if delta_nu_cm1 <= 0.0:
        raise ValueError(f"Delta_nu 必须为正，得到 {delta_nu_cm1}")
    return 1e4 / (2.0 * n * cos_theta_prime(theta_deg, n, n_air) * delta_nu_cm1)


def thickness_from_phase_gap(g_m_plus_2: float, g_m: float) -> float:
    gap = g_m_plus_2 - g_m
    if gap <= 0.0:
        raise ValueError(f"同型相邻极值的 g 间隔必须为正，得到 {gap:.6e}")
    return 1e4 / (2.0 * gap)


def find_extrema(
    nu_cm1: np.ndarray,
    values: np.ndarray,
    kind: str = "both",
    prominence: float = 0.0,
) -> dict[str, np.ndarray]:
    """定位干涉极值（formulation.md (3.7)）。kind = 'max'/'min'/'both'。

    prominence 传给 scipy.signal.find_peaks，抑制噪声伪峰（B8：定位精度受噪声影响）。
    """
    from scipy.signal import find_peaks

    nu_arr = np.asarray(nu_cm1, dtype=float)
    val_arr = np.asarray(values, dtype=float)
    if nu_arr.shape != val_arr.shape or nu_arr.size < 3:
        raise ValueError("极值定位需要等长的 nu/values 数组且至少 3 个点")
    maxima, _ = find_peaks(val_arr, prominence=prominence)
    minima, _ = find_peaks(-val_arr, prominence=prominence)
    if kind == "max":
        return {"max": maxima, "min": np.array([], dtype=int)}
    if kind == "min":
        return {"min": minima, "max": np.array([], dtype=int)}
    return {"max": maxima, "min": minima}


def same_type_spacings(extrema_nu: np.ndarray) -> np.ndarray:
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
    prominence: float = 0.0,
) -> dict[str, float]:
    """方法 A（极值间隔法，(3.9)/(3.10) 常数 n 基线）。

    仅在忽略色散时适用；2000-4000 cm^-1 带色散效应引入约 4% 系统偏差（B10），故作基线/初值。
    """
    extrema = find_extrema(nu_cm1, reflectance, kind=kind, prominence=prominence)
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
    prominence: float = 0.0,
) -> dict[str, float]:
    """色散化相位法（formulation.md (6.1)/(3.13)，M2）。

    同型相邻极值 g 函数间隔 delta_g = 1/(2*1e-4*t)，t = 1e4/(2*delta_g)。解析、快速，作初值+交叉验证。
    """
    extrema = find_extrema(nu_cm1, reflectance, kind=kind, prominence=prominence)
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


def phase_period_estimate(nu_cm1: np.ndarray, n_nu: np.ndarray, theta_deg: float, n_air: float = N_AIR) -> float:
    """厚度周期歧义周期（formulation.md (6.3)）。谱段中心处估计。"""
    nu_c = float(np.mean(np.asarray(nu_cm1, dtype=float)))
    n_c = float(np.mean(np.asarray(n_nu, dtype=float)))
    return 1.0 / (2.0 * 1e-4 * n_c * nu_c * cos_theta_prime(theta_deg, n_c, n_air))


# ---------------------------------------------------------------------------
# 加权全谱 NLS（B9）
# ---------------------------------------------------------------------------
def weighted_residual(
    p: np.ndarray,
    nu_list: list[np.ndarray],
    r_obs_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    *,
    fit_nsub: bool,
    n_sub_init: float = N_SUB_INIT,
    pol: str = "avg",
) -> np.ndarray:
    """加权全谱残差向量（formulation_v002 (5.1)）。

    p：P1=[t]；P2=[t, n_sub]。对每个角度 r = sqrt(w) * (R_obs - R_model)。
    权重 w 为 0（Reststrahlen 剔除）或小量（异常点降权）时该项几乎/完全被忽略。
    """
    t_um = float(p[0])
    n_sub = float(p[1]) if fit_nsub else float(n_sub_init)
    residuals: list[np.ndarray] = []
    for nu, r_obs, theta, n_nu, w in zip(nu_list, r_obs_list, theta_list, n_list, weights_list):
        model = np.asarray(forward_reflectance(nu, t_um, n_nu, n_sub, theta, pol=pol), dtype=float)
        sq_w = np.sqrt(np.clip(w, 0.0, None))
        residuals.append(sq_w * (np.asarray(r_obs, dtype=float) - model))
    return np.concatenate(residuals) if residuals else np.array([], dtype=float)


def invert_nls(
    nu_list: list[np.ndarray],
    r_obs_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    t0_um: float,
    *,
    fit_nsub: bool = False,
    n_sub_init: float = N_SUB_INIT,
    bounds: tuple[float, float] = (0.1, 100.0),
    n_sub_bounds: tuple[float, float] = N_SUB_BOUNDS,
    ftol: float = 1e-10,
    xtol: float = 1e-10,
    gtol: float = 1e-10,
    max_nfev: int = 400,
    pol: str = "avg",
) -> dict:
    """精确非线性最小二乘（scipy.optimize.least_squares，LM/信赖域）。

    P1：仅 t；P2：联合 (t, n_sub)。返回求解器状态、t_um、（可选 n_sub）、残差诊断与雅可比。
    n_sub 边界 v002 用 N_SUB_BOUNDS（重掺 SiC 衬底折射率合理区间），不再用 v001 的宽松 [1+ε,10]。
    """
    from scipy.optimize import least_squares

    x0 = np.array([float(t0_um)] + ([float(n_sub_init)] if fit_nsub else []))
    lo = bounds[0]
    hi = bounds[1]
    lb = np.array([lo] + ([n_sub_bounds[0]] if fit_nsub else []))
    ub = np.array([hi] + ([n_sub_bounds[1]] if fit_nsub else []))
    result = least_squares(
        lambda p: weighted_residual(
            p, nu_list, r_obs_list, theta_list, n_list, weights_list, fit_nsub=fit_nsub, n_sub_init=n_sub_init, pol=pol
        ),
        x0=x0,
        bounds=(lb, ub),
        ftol=ftol,
        xtol=xtol,
        gtol=gtol,
        max_nfev=max_nfev,
    )
    out = {
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
        "jac": result.jac,
        "n_obs": int(result.fun.size),
        "n_params": int(1 + (1 if fit_nsub else 0)),
    }
    if fit_nsub:
        out["n_sub"] = float(result.x[1])
    return out


def residual_indep(
    p: np.ndarray,
    nu_list: list[np.ndarray],
    r_obs_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    *,
    fit_nsub: bool = False,
    n_sub_init: float = N_SUB_INIT,
    pol: str = "avg",
) -> np.ndarray:
    """两角度独立 t 的加权残差向量（formulation_v002 §7.1 M_indep）。

    p：[t1, t2]（fit_nsub=False）或 [t1, t2, n_sub]（fit_nsub=True）。
    用于两角一致性嵌套 F 检验的"允许独立 t₁,t₂（共享 n_sub）"模型。
    """
    n_angles = len(nu_list)
    if len(p) < n_angles:
        raise ValueError(f"独立 t 需要至少 {n_angles} 个 t 分量，得到 {len(p)}")
    t_vals = [float(p[k]) for k in range(n_angles)]
    n_sub = float(p[n_angles]) if fit_nsub else float(n_sub_init)
    residuals: list[np.ndarray] = []
    for k in range(n_angles):
        model = np.asarray(
            forward_reflectance(nu_list[k], t_vals[k], n_list[k], n_sub, theta_list[k], pol=pol), dtype=float
        )
        sq_w = np.sqrt(np.clip(weights_list[k], 0.0, None))
        residuals.append(sq_w * (np.asarray(r_obs_list[k], dtype=float) - model))
    return np.concatenate(residuals) if residuals else np.array([], dtype=float)


def invert_nls_indep(
    nu_list: list[np.ndarray],
    r_obs_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    t0_list: list[float],
    *,
    fit_nsub: bool = False,
    n_sub_init: float = N_SUB_INIT,
    t_bounds: tuple[float, float] = (0.1, 100.0),
    n_sub_bounds: tuple[float, float] = N_SUB_BOUNDS,
    ftol: float = 1e-10,
    xtol: float = 1e-10,
    gtol: float = 1e-10,
    max_nfev: int = 400,
    pol: str = "avg",
) -> dict:
    """两角度独立 t 的非线性最小二乘（formulation_v002 §7.1 M_indep，(t1,t2[,n_sub])）。"""
    from scipy.optimize import least_squares

    if len(t0_list) != len(nu_list):
        raise ValueError("t0_list 长度须等于角度数")
    x0 = np.array([float(v) for v in t0_list] + ([float(n_sub_init)] if fit_nsub else []))
    lo = t_bounds[0]
    hi = t_bounds[1]
    lb = np.array([lo] * len(t0_list) + ([n_sub_bounds[0]] if fit_nsub else []))
    ub = np.array([hi] * len(t0_list) + ([n_sub_bounds[1]] if fit_nsub else []))
    result = least_squares(
        lambda p: residual_indep(
            p, nu_list, r_obs_list, theta_list, n_list, weights_list, fit_nsub=fit_nsub, n_sub_init=n_sub_init, pol=pol
        ),
        x0=x0,
        bounds=(lb, ub),
        ftol=ftol,
        xtol=xtol,
        gtol=gtol,
        max_nfev=max_nfev,
    )
    out = {
        "t_um_list": [float(v) for v in result.x[: len(t0_list)]],
        "success": bool(result.success),
        "status": int(result.status),
        "cost": float(result.cost),
        "nfev": int(result.nfev),
        "message": str(result.message),
        "rmse": float(np.sqrt(np.mean(result.fun**2))) if result.fun.size else None,
        "n_obs": int(result.fun.size),
        "n_params": int(len(t0_list) + (1 if fit_nsub else 0)),
    }
    if fit_nsub:
        out["n_sub"] = float(result.x[len(t0_list)])
    return out


def analytic_ci_from_jac(jac: np.ndarray, rss: float, n_obs: int, n_params: int, *, z: float = 1.96) -> dict | None:
    """解析协方差置信区间（formulation_v002 §7.4：LM 雅可比→参数协方差→投影到 t）。

    cov = sigma^2 * inv(J^T J)，sigma^2 = rss/(n_obs - n_params)；σ_t = sqrt(cov[0,0])。
    95% CI 半宽 = z*σ_t。若 (J^T J) 奇异（弱可辨识，如 n_sub 对比度过弱）返回 None。
    """
    if jac is None or n_obs <= n_params:
        return None
    try:
        J = np.asarray(jac, dtype=float)
        h = J.T @ J
        if np.any(~np.isfinite(h)):
            return None
        cov = np.linalg.inv(h) * (float(rss) / (n_obs - n_params))
        sigma_t = float(np.sqrt(max(cov[0, 0], 0.0)))
    except np.linalg.LinAlgError:
        return None
    return {"sigma_t": sigma_t, "ci_halfwidth": z * sigma_t, "cov": cov}


def grid_scan_t0(
    nu_list: list[np.ndarray],
    r_obs_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    *,
    t_range: tuple[float, float] = (1.0, 30.0),
    n_points: int = 200,
    fit_nsub: bool = False,
    n_sub_init: float = N_SUB_INIT,
    pol: str = "avg",
) -> dict:
    """网格扫描初值：在 t_range 上粗扫 RMS 最小的 t0（prob01 robustness E4 升级策略）。

    噪声下解析初值（方法 A/相位法）会严重失真（prob01 robustness 实测），改为网格扫描 + 局部精化。
    """
    best_t0: float | None = None
    best_rmse = float("inf")
    for t_cand in np.linspace(t_range[0], t_range[1], n_points):
        res = weighted_residual(
            np.array([t_cand] + ([n_sub_init] if fit_nsub else [])),
            nu_list,
            r_obs_list,
            theta_list,
            n_list,
            weights_list,
            fit_nsub=fit_nsub,
            n_sub_init=n_sub_init,
            pol=pol,
        )
        rmse = float(np.sqrt(np.mean(res**2))) if res.size else float("inf")
        if rmse < best_rmse:
            best_rmse = rmse
            best_t0 = float(t_cand)
    return {"t0_best": best_t0, "rmse_best": best_rmse}


def invert_nls_multistart(
    nu_list: list[np.ndarray],
    r_obs_list: list[np.ndarray],
    theta_list: list[float],
    n_list: list[np.ndarray],
    weights_list: list[np.ndarray],
    *,
    t0_um: float | None = None,
    alt_t0_um: float | None = None,
    fit_nsub: bool = False,
    n_sub_init: float = N_SUB_INIT,
    t_range: tuple[float, float] = (1.0, 30.0),
    grid_points: int = 200,
    period: float | None = None,
    pol: str = "avg",
) -> dict:
    """多初值全谱 NLS：网格扫描 + 相位法 + ±周期布点，取最小 RMSE（formulation_v002 (6.2)，B9）。

    消除 cos(delta) 厚度周期歧义（约 0.96 um，formula_validation §6）与噪声下解析初值失真。
    """
    # 主起点以网格扫描为准（鲁棒）
    scan = grid_scan_t0(
        nu_list,
        r_obs_list,
        theta_list,
        n_list,
        weights_list,
        t_range=t_range,
        n_points=grid_points,
        fit_nsub=fit_nsub,
        n_sub_init=n_sub_init,
        pol=pol,
    )
    starts: list[float] = []
    if scan["t0_best"] is not None:
        starts.append(scan["t0_best"])
    if t0_um is not None:
        starts.append(float(t0_um))
    if alt_t0_um is not None:
        starts.append(float(alt_t0_um))
    if period is None:
        # 用第一个角度的全谱估计一个代表性周期
        ref_nu = nu_list[0]
        ref_n = n_list[0]
        period = phase_period_estimate(ref_nu, ref_n, theta_list[0])
    if period:
        for s in list(starts):
            starts.append(s - period)
            starts.append(s + period)
    # 去重
    unique: list[float] = []
    for s in starts:
        if s > 0.0 and all(abs(s - u) > 1e-6 for u in unique):
            unique.append(s)
    fits = [
        invert_nls(
            nu_list,
            r_obs_list,
            theta_list,
            n_list,
            weights_list,
            float(s),
            fit_nsub=fit_nsub,
            n_sub_init=n_sub_init,
            pol=pol,
        )
        for s in unique
    ]
    best = min(fits, key=lambda item: item["rmse"] if item["rmse"] is not None else float("inf"))
    return {"best": best, "starts": fits, "period_um_estimate": float(period), "scan": scan, "n_starts": len(unique)}


# ---------------------------------------------------------------------------
# 数据加载与预处理（B1-B3）
# ---------------------------------------------------------------------------
def load_attachment(path: Path | str) -> dict:
    """读取附件 xlsx：列『波数 (cm-1)』『反射率 (%)』。

    返回 {nu: 升序 ndarray, r_obs: 0-1 归一 ndarray}。
    附件 2 波数列为降序，读入后重排为升序（B1）。反射率 %->0-1 归一（R_model = R%/100）。
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
    reststrahlen: tuple[float, float] = RESTSTRAHLEN_EXCLUDE_CM1,
    anomaly_upper_pct: float = ANOMALY_UPPER_PCT,
    weight_anomaly: float = 0.05,
    anomaly_band: tuple[float, float] | None = None,
) -> dict:
    """预处理：归一化、Reststrahlen 剔除/降权、异常点标记/降权（B1-B3）。

    返回 {nu, r_obs, weights, mask_valid, anomaly_idx, reststrahlen_idx, log}。
    权重 (5.2)：Reststrahlen 区 w=0；异常点 w=weight_anomaly；其余 w=1。
    不改原始数据；全部处理写入 log（含计数与阈值）。
    """
    nu_arr = np.asarray(nu, dtype=float)
    r_obs_arr = np.asarray(r_obs, dtype=float)
    if nu_arr.shape != r_obs_arr.shape:
        raise ValueError("nu 与 r_obs 形状不一致")

    rest_mask = (nu_arr >= reststrahlen[0]) & (nu_arr <= reststrahlen[1])
    # 异常点判定：反射率 >100%（附件2 超界）或物理下限 <0
    r_pct = r_obs_arr * 100.0
    anomaly_upper = r_pct > anomaly_upper_pct
    anomaly_lower = r_pct < ANOMALY_LOWER_PCT
    anomaly_base = anomaly_upper | anomaly_lower
    # 可选异常点谱段区间并集（稳健阈值之外的补充标记）
    if anomaly_band is not None:
        anomaly_base = anomaly_base | ((nu_arr >= anomaly_band[0]) & (nu_arr <= anomaly_band[1]))

    weights = np.ones(nu_arr.shape, dtype=float)
    weights[rest_mask] = 0.0
    weights[anomaly_base] = weight_anomaly

    log = {
        "n_points": int(nu_arr.size),
        "reststrahlen_range": list(reststrahlen),
        "n_reststrahlen_excluded": int(np.count_nonzero(rest_mask)),
        "anomaly_rule": f"R% > {anomaly_upper_pct} 或 R% < {ANOMALY_LOWER_PCT}（超界）",
        "n_anomaly": int(np.count_nonzero(anomaly_base)),
        "n_anomaly_upper": int(np.count_nonzero(anomaly_upper)),
        "n_anomaly_lower": int(np.count_nonzero(anomaly_lower)),
        "weight_anomaly": weight_anomaly,
        "n_valid_points": int(np.count_nonzero(weights > 0.0)),
        "note": "原始数据只读；反射率 %->0-1 归一；Reststrahlen 区 w=0；异常点降权 w=weight_anomaly",
    }
    return {
        "nu": nu_arr,
        "r_obs": r_obs_arr,
        "weights": weights,
        "mask_valid": weights > 0.0,
        "anomaly_idx": np.flatnonzero(anomaly_base),
        "reststrahlen_idx": np.flatnonzero(rest_mask),
        "log": log,
    }


def restrict_band(nu_cm1: np.ndarray, lo: float, hi: float) -> tuple[np.ndarray, np.ndarray]:
    nu_arr = np.asarray(nu_cm1, dtype=float)
    mask = (nu_arr >= lo) & (nu_arr <= hi)
    return nu_arr[mask], mask

# ---------------------------------------------------------------------------
# v003 主反演：基线-干涉分解 + 一维相位频率扫描（baseline-robust variable projection）
# ---------------------------------------------------------------------------
def vp_basis_deg() -> tuple[int, int]:
    """返回基线/包络多项式阶数 (p, q)（formulation_v003 §5.5；parameters.yaml 登记值，计算前固定）。"""
    return BASELINE_POLY_DEG, ENVELOPE_POLY_DEG


def _poly_scale_center(nu_cm1: np.ndarray, nu_ref: float | None = None) -> tuple[float, float]:
    """计算多项式基的归一化参考（中心化 + 缩放到 [-1,1]，formulation §5.5/§7：中心化/正交化 Vandomer）。

    默认以带中心 nu0 = (多角度平均带中值) 为参考。返回 (nu0, half)。
    """
    nu_arr = np.asarray(nu_cm1, dtype=float)
    if nu_ref is not None:
        nu0 = float(nu_ref)
    else:
        nu0 = float(np.mean(nu_arr))
    half = max(float(np.max(nu_arr) - nu0), float(nu0 - np.min(nu_arr)), 1e-12)
    return nu0, half


def poly_basis_cheb(nu_cm1: np.ndarray, deg: int, nu0: float, half: float) -> np.ndarray:
    """中心化/正交化的多项式基（Chebyshev Vandomer：把 ν 映射到 [-1,1] 后的 Chebyshev 多项式）。

    返回形状 (N, deg+1)，列为 T_0..T_deg（正交、良态），替代原始 ν^p 幂基（绝对值对基敏感，
    formulation §7/§13.1）。仅数值实现层面的归一化，不改变物理量纲。
    """
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
    """基线-干涉分解设计矩阵 Φ(t)（formulation_v003 (5.4)）。

    列 = [B 多项式(0..p),  C 多项式(0..q) * cos δ,  S 多项式(0..q) * sin δ]。
    δ(ν) = 4π×1e-4·t·g(ν)（(2.2)/(5.8)；φ 相位跃变吸收进 C/S 系数）。
    """
    g = np.asarray(phase_function(nu_cm1, n_nu, theta_deg), dtype=float)
    delta = 4.0 * np.pi * 1e-4 * float(t_um) * g
    b_poly = poly_basis_cheb(nu_cm1, p, nu0, half)
    c_poly = poly_basis_cheb(nu_cm1, q, nu0, half)
    s_poly = poly_basis_cheb(nu_cm1, q, nu0, half)
    cos_d = np.cos(delta)[:, None]
    sin_d = np.sin(delta)[:, None]
    return np.concatenate([b_poly, c_poly * cos_d, s_poly * sin_d], axis=1)


def vp_linear_ls(
    phi: np.ndarray,
    r_obs: np.ndarray,
    weights: np.ndarray,
) -> dict:
    """对固定 t 求解加权线性最小二乘 β（formulation_v003 (5.5)），返回 β、残差平方和、秩、条件数。

    A = sqrt(W)·Φ，b = sqrt(W)·R^obs；β = lstsq(A, b)。RSS = ||Aβ - b||²。
    """
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
    """单角度的 variable projection 残差平方和 J_k(t)（formulation (5.6) 的单项）。"""
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
    """单角度一维扫描 J_k(t)，返回 t 网格、J 值、全局最小位置与抛物线精化。"""
    t_lo, t_hi = float(t_range[0]), float(t_range[1])
    n_points = int(np.floor((t_hi - t_lo) / t_step)) + 1
    t_grid = t_lo + np.arange(n_points) * t_step
    j_vals = np.empty(n_points, dtype=float)
    for i, t in enumerate(t_grid):
        j_vals[i] = vp_angle_j(nu_cm1, r_obs, n_nu, theta_deg, weights, float(t), p, q, nu0, half)["rss"]
    idx = int(np.argmin(j_vals))
    t_hat = float(t_grid[idx])
    j_min = float(j_vals[idx])
    # 抛物线精化（局部二次拟合取极小）
    t_refined = t_hat
    if 0 < idx < n_points - 1:
        _, b, _ = t_grid[idx - 1], t_grid[idx], t_grid[idx + 1]
        ja, jb, jc = j_vals[idx - 1], j_vals[idx], j_vals[idx + 1]
        denom = (ja - 2.0 * jb + jc)
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
    t_range: tuple[float, float] = T_SCAN_RANGE,
    t_step: float = T_SCAN_STEP,
    p: int = BASELINE_POLY_DEG,
    q: int = ENVELOPE_POLY_DEG,
    nu_ref: float | None = None,
    shared: bool = True,
) -> dict:
    """主干反演：基线-干涉分解 + 一维相位频率扫描（formulation_v003 (5.6)/(5.7)）。

    shared=True：两角**共享 t**（主判据，B/C/S 按角度独立、t 全局共享），J(t)=Σ_k J_k(t)，
                 t̂=argmin；并返回每角在 t̂ 的拟合系数（供包络/幅值/n_sub 事后弱辨识）。
    shared=False：每角独立 t，各自扫描（一致性检验/报告每角 t̂_k）。
    多项式基为共享的归一化参考（nu0, half），保证两角同一坐标系。
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

    # 共享 t：J(t) = Σ_k J_k(t)。t 网格一致（shared t_range/t_step）。
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
        # 每角独立极小（同一扫描范围下的 J_k 最小值，供 F 检验/报告）
        "J_min_per_angle": [float(r["j_vals"][r["idx_min"]]) for r in results],
    }
    idx = int(np.argmin(j_shared))
    out["t_hat"] = float(t_grid[idx])
    out["J_min_shared"] = float(j_shared[idx])
    # 抛物线精化（共享 t）
    t_refined = out["t_hat"]
    if 0 < idx < t_grid.size - 1:
        _, b, _ = t_grid[idx - 1], t_grid[idx], t_grid[idx + 1]
        ja, jb, jc = j_shared[idx - 1], j_shared[idx], j_shared[idx + 1]
        denom = (ja - 2.0 * jb + jc)
        if abs(denom) > 1e-15:
            t_refined = float(b + 0.5 * (ja - jc) / denom * t_step)
    out["t_hat_refined"] = t_refined
    # 每角在共享 t̂ 处的拟合系数与包络
    angle_fits: list[dict] = []
    for k in range(n_angles):
        phi = vp_design_matrix(nu_list[k], n_list[k], theta_list[k], t_refined, p, q, nu0, half)
        fit = vp_linear_ls(phi, r_list[k], weights_list[k])
        beta = fit["beta"]
        b_cols = p + 1
        c_cols = q + 1
        c_beta = beta[b_cols : b_cols + c_cols]
        s_beta = beta[b_cols + c_cols : b_cols + 2 * c_cols]
        # 在参考波数处求 C/S → A
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


def nsub_from_amplitude(
    amplitude: float,
    n: float,
    theta_deg: float,
    *,
    n_air: float = N_AIR,
    n_sub_max: float = 4.0,
    pol: str = "avg",
) -> dict:
    """由干涉幅值 A 反演衬底折射率 n̂_sub（formulation_v003 §7.3 幅度弱辨识；B7/L26）。

    A = 2(1−R₁)√(R₁ R₂)（(2.3)，s/p 平均）→ √(R₁R₂) = A/(2(1−R₁)) → R₂ = (A/(2(1−R₁)))²/R₁；
    再由 Fresnel 界面反射率 R₂(n, n_sub, θ') 对 n_sub 做单调二分反演。
    返回 {n_sub, R1, R2, amplitude}；若 A 过小/不可逆，返回 n_sub=None（弱可辨识/回退文献）。
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

        # 先粗扫确定包围区间（R2 在 [n+eps, n_sub_max] 内可能非严格单调，取 R2 接近 target 的根）
        nvec = np.linspace(n + 1e-6, n_sub_max, 400)
        rvec = np.array([r2_of_nsub(v) for v in nvec])
        diff = rvec - r2_target
        # 找最近符号变化
        sign_changes = np.flatnonzero(diff[:-1] * diff[1:] <= 0)
        if sign_changes.size == 0:
            return {"n_sub": None, "R1": r1, "R2": r2_target, "amplitude": amplitude}
        idx0 = int(sign_changes[0])
        n_lo, n_hi = float(nvec[idx0]), float(nvec[idx0 + 1])
        n_sub_est = float(brentq(lambda v: r2_of_nsub(v) - r2_target, n_lo, n_hi, xtol=1e-9))
    except Exception:
        return {"n_sub": None, "R1": r1, "R2": r2_target, "amplitude": amplitude}
    return {"n_sub": n_sub_est, "R1": r1, "R2": r2_target, "amplitude": amplitude}


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


def profile_ci_from_Jcurve(
    t_grid: np.ndarray,
    j_vals: np.ndarray,
    t_hat: float,
    *,
    n_tot: int,
    n_params: int,
    chi2: float = 3.841,
) -> dict | None:
    """轮廓似然 95% CI（formulation_v003 §7.4：由 J(t) 在 t̂ 附近抛物近似/夹逼区间）。

    区间边界 t 满足 J(t) - J(t̂) = chi2_{0.95,1} * sigma²，sigma² = J(t̂)/(n_tot - n_params)
    （残差重采样 bootstrap 作为替代方案留 computation；本方法秒级、避免 bootstrap 超时）。
    返回 {t_low, t_high, halfwidth_um, halfwidth_percent, sigma2}；若无法确定两界返回 None。
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
    # 向左找 j>j_min+threshold 的边界
    for i in range(idx, 0, -1):
        if j[i] >= j_min + threshold:
            # 线性插值
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


def two_angle_ftest_vp(
    shared_scan: dict,
    indep_scan: dict,
    *,
    n_tot: int,
    alpha: float = 0.05,
) -> dict:
    """两角一致性嵌套 F 检验（formulation_v003 §7.1，对相位-频率拟合）。

    M_shared：两角共享 t（SS_shared = J_min_shared）；M_indep：两角独立 t（SS_indep = Σ J_min_k）。
    df1 = n_t_indep - n_t_shared = 2 - 1 = 1；df2 = n_tot - n_params_indep。
    F <= F_alpha(1, df2) → 接受共享 t（一致性 PASS）。
    """
    from scipy.stats import f as f_dist

    ss_shared = float(shared_scan["J_min_shared"])
    ss_indep = float(
        sum(shared_scan["J_min_per_angle"])
        if "J_min_per_angle" in shared_scan
        else sum(indep_scan["J_min_per_angle"])
    )
    df1 = 2 - 1
    # 每角基线/包络系数数 = (p+1) + 2(q+1)；独立 t 模型参数数 = n_angles*coef + n_angles
    p = int(shared_scan["p"])
    q = int(shared_scan["q"])
    n_angles = int(shared_scan["n_angles"]) if "n_angles" in shared_scan else 2
    coef_per_angle = (p + 1) + 2 * (q + 1)
    n_params_indep = n_angles * coef_per_angle + n_angles
    df2 = int(n_tot - n_params_indep)
    if df2 <= 0 or ss_indep <= 0:
        f_stat = float("inf")
        p_value = 0.0
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



# ---------------------------------------------------------------------------
# 接口探针（秒级）
# ---------------------------------------------------------------------------
def run_probes(anchor_path: Path | str | None = None) -> dict[str, bool]:
    """接口探针：核验公式数值例与代码机械（formula_validation.md / formulation 探针值）。

    全部为秒级小计算，不运行完整数据集。供实现阶段静态检查与 compute.py --self-check 使用。
    """
    checks: dict[str, bool] = {}

    # 1. Sellmeier：n(5um) ≈ 2.4954（formula_validation 关键换算核验）
    n5 = float(np.asarray(sellmeier_n4hsi(5.0), dtype=float))
    checks["sellmeier_n5um"] = abs(n5 - 2.4954) / 2.4954 < 1e-3

    # 2. Fischer：n(25um) ≈ 3.115（Fischer 2017，远红外）且 n(17um)≈3.524（单调递减）
    n25 = float(np.asarray(fischer_n4hsi(25.0), dtype=float))
    n17 = float(np.asarray(fischer_n4hsi(17.0), dtype=float))
    checks["fischer_n25um"] = abs(n25 - 3.115) / 3.115 < 1e-2
    checks["fischer_mono_decrease"] = n25 < n17

    # 3. 色散分段（v002）：nu>=nu_c 用 Sellmeier；nu<nu_c 用 n_ref 插值（背景/Δt_inv_band 诊断）；
    #    N-const 基线为常数；N-SE-delta = N-SE × c_disp。
    nu_hi = np.array([4000.0, 3000.0, 2500.0])
    nu_lo = np.array([500.0, 450.0, 400.0])
    n_hi = np.asarray(dispersion_epi(nu_hi, model="N-SE", anchor_path=anchor_path), dtype=float)
    n_lo = np.asarray(dispersion_epi(nu_lo, model="N-SE", anchor_path=anchor_path), dtype=float)
    check_hi = all(
        abs(float(n_hi[i]) - float(np.asarray(sellmeier_n4hsi(1e4 / nu_hi[i]), dtype=float))) < 1e-9 for i in range(3)
    )
    checks["dispersion_split_high_sellmeier"] = check_hi
    checks["dispersion_ref_low_positive"] = bool(np.all(n_lo > 1.0))
    n_const = np.asarray(dispersion_epi(nu_lo, model="N-const"), dtype=float)
    checks["dispersion_nconst_baseline_constant"] = bool(np.allclose(n_const, n_const[0], atol=1e-12))
    checks["dispersion_nconst_equals_sellmeier_boundary"] = bool(
        abs(float(n_const[0]) - float(np.asarray(sellmeier_n4hsi(5.0), dtype=float))) < 1e-9
    )
    # N-SE-delta = N-SE × c_disp（带内色散灵敏度，§7.2）
    n_delta = np.asarray(dispersion_epi(nu_hi, model="N-SE-delta", c_disp=1.005, anchor_path=anchor_path), dtype=float)
    checks["dispersion_nse_delta_scale"] = bool(
        np.allclose(n_delta, n_hi * 1.005, atol=1e-12)
    )

    # 4. n_ref 锚点连续性：Sellmeier 在 5um 与 Fischer 在 17um 之间单调插值无 NaN
    lam_probe = np.array([6.0, 8.0, 10.0, 12.0])
    n_ref_probe = np.asarray(interpolate_n_ref(lam_probe, anchor_path), dtype=float)
    checks["n_ref_gap_no_nan"] = bool(np.all(np.isfinite(n_ref_probe)))

    # 5. 正模型物理边界：R in [0, 1]（formula_validation §4，n=2.6/n_sub=3.0/theta=10°）
    nu = np.linspace(400.0, 4000.0, 900)
    r_clean = np.asarray(forward_reflectance(nu, 10.0, 2.6, 3.0, 10.0), dtype=float)
    checks["forward_R_in_unit"] = bool(np.all(r_clean >= 0.0) and np.all(r_clean <= 1.0))
    checks["forward_R_oscillates"] = bool(np.ptp(r_clean) > 0.01)

    # 6. v002 P2 往返反演（带内 N-SE Sellmeier；P2 联合 (t,n_sub) 恢复；Band [2000,4000]）
    t_true = 2.25
    n_sub_true = 3.0
    band_nu = np.linspace(2000.0, 4000.0, 400)
    band_n = np.asarray(dispersion_epi(band_nu, model="N-SE", anchor_path=anchor_path), dtype=float)
    check_band_sellmeier = bool(np.allclose(band_n, sellmeier_n4hsi(1e4 / band_nu), rtol=1e-9, atol=1e-12))
    checks["nse_band_pure_sellmeier"] = check_band_sellmeier  # 主反演带内 N-SE 退化为纯 Sellmeier

    phase_ok, nls_ok = True, True
    for theta in (10.0, 15.0):
        r = np.asarray(forward_reflectance(band_nu, t_true, band_n, n_sub_true, theta), dtype=float)
        phase = invert_phase_method(band_nu, r, theta, band_n, kind="max", prominence=1e-4)
        w = np.ones(r.shape)
        nls = invert_nls_multistart(
            [band_nu],
            [r],
            [theta],
            [band_n],
            [w],
            t0_um=phase["t_phase_um"],
            alt_t0_um=None,
            fit_nsub=True,
            n_sub_init=2.55,
            t_range=(0.5, 20.0),
            grid_points=60,
        )["best"]
        phase_ok = phase_ok and abs(phase["t_phase_um"] - t_true) / t_true < 1e-2
        nls_ok = nls_ok and abs(nls["t_um"] - t_true) / t_true < 1e-2
    checks["roundtrip_phase_method"] = phase_ok
    checks["roundtrip_nls_p2"] = nls_ok

    # 7. t–n_sub 解耦（v002 §13.1：带内正确色散下 t 与 n_sub 近似解耦；P1 固定不同 n_sub 再反演 t）
    decouple_ok = True
    for theta in (10.0, 15.0):
        r = np.asarray(forward_reflectance(band_nu, t_true, band_n, n_sub_true, theta), dtype=float)
        t_ref = None
        for nsub_c in (2.5, 3.0, 3.5):
            fit = invert_nls([band_nu], [r], [theta], [band_n], [np.ones(r.shape)], t_true, n_sub_init=nsub_c)
            if t_ref is None:
                t_ref = fit["t_um"]
            decouple_ok = decouple_ok and abs(fit["t_um"] - t_true) / t_true < 1e-2
    checks["nsub_decouple_inband"] = decouple_ok

    # 8. 独立 t（F 检验 M_indep）+ 解析 CI 机械核验（formulation_v002 §7.1/§7.4）
    r1 = np.asarray(forward_reflectance(band_nu, t_true, band_n, n_sub_true, 10.0), dtype=float)
    r2 = np.asarray(forward_reflectance(band_nu, t_true, band_n, n_sub_true, 15.0), dtype=float)
    indep = invert_nls_indep(
        [band_nu, band_nu],
        [r1, r2],
        [10.0, 15.0],
        [band_n, band_n],
        [np.ones(r1.shape), np.ones(r2.shape)],
        [t_true, t_true],
        fit_nsub=True,
        n_sub_init=2.55,
    )
    ok_indep_t = bool(abs(indep["t_um_list"][0] - t_true) / t_true < 1e-2)
    ok_indep_t = ok_indep_t and bool(abs(indep["t_um_list"][1] - t_true) / t_true < 1e-2)
    checks["ftest_indep_fit"] = ok_indep_t
    # 共享 t P2（M_shared）
    shared = invert_nls(
        [band_nu, band_nu],
        [r1, r2],
        [10.0, 15.0],
        [band_n, band_n],
        [np.ones(r1.shape), np.ones(r2.shape)],
        t_true,
        fit_nsub=True,
        n_sub_init=2.55,
    )
    ci = analytic_ci_from_jac(shared["jac"], shared["cost"] * 2.0, shared["n_obs"], shared["n_params"])
    checks["analytic_ci_positive"] = bool(ci is not None and ci["sigma_t"] > 0.0 and ci["ci_halfwidth"] > 0.0)

    # 9. 数据契约与预处理（B1-B3）机械核验：异常点 >100% 标记与 Reststrahlen 剔除
    nu_small = np.linspace(399.0, 4000.0, 80)
    r_small = np.full(nu_small.shape, 30.0)
    in_rest = (nu_small >= 700.0) & (nu_small <= 1000.0)
    r_small[in_rest] = 40.0
    r_small[20] = 105.0  # 一个 >100% 异常点
    r_obs = r_small / 100.0
    pp = preprocess_spectrum(nu_small, r_obs)
    anomaly_count = int(np.count_nonzero(pp["anomaly_idx"]))
    rest_count = int(np.count_nonzero(pp["reststrahlen_idx"]))
    checks["preprocess_anomaly_flagged"] = anomaly_count >= 1
    checks["preprocess_reststrahlen_excluded"] = rest_count >= 1
    checks["preprocess_weights_zero_in_rest"] = bool(np.all(pp["weights"][in_rest] == 0.0))

    # ---- v003 主方法：基线-干涉分解 + 一维相位频率扫描（variable projection）数值核验 ----
    band_nu3 = np.linspace(2000.0, 4000.0, 400)
    band_n3 = np.asarray(dispersion_epi(band_nu3, model="N-SE", anchor_path=anchor_path), dtype=float)
    checks["vp_band_sellmeier"] = bool(np.allclose(band_n3, sellmeier_n4hsi(1e4 / band_nu3), rtol=1e-9, atol=1e-12))

    # 生成含慢变基线趋势 + 弱对比度干涉的合成谱（n_sub ≈ n），检验 vp 扫描能否按相位频率恢复 t_true。
    t_true3 = 7.4
    n_sub_true3 = 2.6
    p3, q3 = 3, 1
    noise_rng = np.random.default_rng(7)

    def synth_band(theta):
        base = np.asarray(forward_reflectance(band_nu3, t_true3, band_n3, n_sub_true3, theta), dtype=float)
        # 叠加一个线性慢变基线趋势（模拟未建模背景，formulation §0.1）与轻微噪声
        trend = 0.006 + 0.0008 * (band_nu3 - 2000.0) / 2000.0
        return base + trend + noise_rng.normal(0.0, 1e-4, band_nu3.shape)

    r3a = synth_band(10.0)
    r3b = synth_band(15.0)
    w_ones = np.ones(band_nu3.shape)
    scan_shared = variable_projection_scan(
        [band_nu3, band_nu3], [r3a, r3b], [10.0, 15.0], [band_n3, band_n3],
        [w_ones, w_ones], t_range=(3.0, 12.0), t_step=0.05, p=p3, q=q3, shared=True,
    )
    checks["vp_roundtrip_shared_t"] = bool(abs(scan_shared["t_hat_refined"] - t_true3) / t_true3 < 1e-2)
    # 独立扫描每角也恢复 t_true（两角一致）
    scan_indep = variable_projection_scan(
        [band_nu3, band_nu3], [r3a, r3b], [10.0, 15.0], [band_n3, band_n3],
        [w_ones, w_ones], t_range=(3.0, 12.0), t_step=0.05, p=p3, q=q3, shared=False,
    )
    ok_indep_vp = all(abs(v - t_true3) / t_true3 < 1e-2 for v in scan_indep["t_hat_per_angle"])
    checks["vp_roundtrip_indep_t"] = bool(ok_indep_vp)

    # 基线稳健性：p=1..6 下 t 保持稳定（formulation §13.2 t∈[7.38,7.40]），且与多项式基归一化无关
    t_p_vals = []
    for pp in (1, 3, 6):
        sc = variable_projection_scan(
            [band_nu3], [r3a], [10.0], [band_n3], [w_ones],
            t_range=(3.0, 12.0), t_step=0.05, p=pp, q=q3, shared=True,
        )
        t_p_vals.append(sc["t_hat_refined"])
    checks["vp_baseline_degree_stable"] = bool((max(t_p_vals) - min(t_p_vals)) / t_true3 < 5e-2)

    # n_sub 幅度弱辨识（B7）：由干涉幅值 A=√(C²+S²) 反演 R₂→n̂_sub（弱对比度）
    amp0 = scan_shared["angle_fits"][0]["amplitude"]
    n_c = float(np.interp(3000.0, band_nu3, band_n3))
    nsub_est = nsub_from_amplitude(amp0, n_c, 10.0)
    # 弱对比度下允许较大误差（仅验证机械上能返回有限 n_sub）
    checks["nsub_from_amplitude_finite"] = bool(nsub_est["n_sub"] is None or np.isfinite(nsub_est["n_sub"]))

    # 轮廓似然 95% CI（§7.4）：J(t) 曲线返回正 CI 半宽
    n_tot_probe = int(2 * r3a.size)
    coef_probe = (p3 + 1) + 2 * (q3 + 1)
    ci_probe = profile_ci_from_Jcurve(
        scan_shared["t_grid"], scan_shared["J_shared"], scan_shared["t_hat_refined"],
        n_tot=n_tot_probe, n_params=2 * coef_probe + 1,
    )
    checks["vp_profile_ci_positive"] = bool(ci_probe is not None and ci_probe["halfwidth_um"] > 0.0)

    # 两角一致性嵌套 F 检验（§7.1）：合成数据共享 t → 接受共享 t
    ftest_probe = two_angle_ftest_vp(scan_shared, scan_indep, n_tot=n_tot_probe, alpha=0.05)
    checks["vp_ftest_accept_shared"] = bool(ftest_probe["accept_shared_t"])

    return checks


if __name__ == "__main__":  # pragma: no cover - 仅用于手动/探针入口
    results = run_probes()
    for name, passed in results.items():
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    raise SystemExit(0 if all(results.values()) else 1)
