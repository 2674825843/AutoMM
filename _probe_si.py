import numpy as np, pandas as pd
from pathlib import Path
d = Path(r"E:\项目\AutoMM\data\2025_cumcm_B")
def load(name):
    df = pd.read_excel(d/name, header=0)
    nu = df.iloc[:,0].to_numpy(float); R = df.iloc[:,1].to_numpy(float)
    return nu, R
def sellmeier_si(lam):
    lam2=lam**2
    return np.sqrt(1+10.6684293*lam2/(lam2-0.301516485**2)+0.0030434748*lam2/(lam2-1.13475115**2)+1.54133408*lam2/(lam2-1104.0**2))
for name,theta in [("附件3.xlsx",10.0),("附件4.xlsx",15.0)]:
    nu,R = load(name)
    print(f"\n=== {name} theta={theta} ===  nu[{nu[0]:.2f},{nu[-1]:.2f}] n={len(nu)}  Rmax={R.max():.2f}")
    band = (nu>=2000)&(nu<=4000)
    nu_b = nu[band]; R_b = R[band]
    s = np.sign(np.diff(R_b))
    peaks = [i for i in range(1,len(R_b)-1) if R_b[i]>R_b[i-1] and R_b[i]>=R_b[i+1]]
    print(f" band n={len(nu_b)}  local maxima count={len(peaks)}")
    x = R_b - R_b.mean()
    N=len(x); F=np.abs(np.fft.rfft(x*np.hanning(N)))
    k=np.argmax(F[1:])+1
    dnu = nu_b[1]-nu_b[0]
    f_c = k/(N*dnu)
    delta_nu = 1/f_c
    n_ref = sellmeier_si(1e4/3000.0)
    ctp = np.sqrt(1-(np.sin(np.deg2rad(theta))/n_ref)**2)
    t = 1/(2e-4*n_ref*ctp*delta_nu)
    print(f" FFT dominant cycles in band ~ {k} ; f_c={f_c:.6f} /cm ; delta_nu={delta_nu:.2f} cm^-1 "
          f"-> t=1/(2e-4 n cosq' dnu) = {t:.4f} um  (n={n_ref:.4f}, cosq'={ctp:.4f})")
