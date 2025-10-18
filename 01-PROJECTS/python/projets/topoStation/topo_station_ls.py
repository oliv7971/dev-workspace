"""
topo_station_ls.py — Free-station least squares with per-type and per-ray weighting.

Usage (CLI):
    python topo_station_ls.py \
        --controls /path/controls.csv \
        --observations /path/observations.csv \
        --rays /path/rays.csv \
        --config /path/config.json \
        --out /path/output/results

See README_topo_station_ls.md for CSV schemas.
"""

import math
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from pathlib import Path

GON_TO_RAD = math.pi / 200.0
DEG_TO_RAD = math.pi / 180.0

@dataclass
class ControlPoint:
    pid: str
    X: float
    Y: float
    Z: float

@dataclass
class RayMeta:
    ray_id: str
    kappa: float = 1.0

@dataclass
class Observation:
    ray_id: str
    pid: str
    obs_type: str  # 'dir' | 'zen' | 'dist'
    value: float   # angle (gon/deg/rad) or distance (m)
    unit: str      # 'gon' | 'deg' | 'rad' | 'm'
    n_series: int = 1
    h_target: float = 0.0
    extras: Dict = field(default_factory=dict)

@dataclass
class Config:
    sigma_dir_mgon: float = 0.5
    sigma_zen_mgon: float = 1.0
    edm_a_mm: float = 1.5
    edm_b_ppm: float = 2.0
    h_instrument: float = 0.0
    estimate_mu: bool = False
    estimate_c: bool = False
    angles_unit: str = "gon"
    max_iter: int = 10
    tol: float = 1e-10

@dataclass
class LSResult:
    x_hat: np.ndarray
    cov_x: np.ndarray
    sigma0_hat: float
    param_names: List[str]
    residuals: np.ndarray
    norm_residuals: np.ndarray
    redundancies: np.ndarray
    Qvv_diag: np.ndarray
    A: np.ndarray
    P: np.ndarray
    l: np.ndarray
    f: np.ndarray

class FreeStationLS:
    def __init__(self,
                 controls: Dict[str, ControlPoint],
                 observations: List[Observation],
                 rays: Dict[str, RayMeta],
                 cfg: Config):
        self.controls = controls
        self.obs = observations
        self.rays = rays
        self.cfg = cfg

        self.param_names = ["X0", "Y0", "Z0", "omega"]
        if cfg.estimate_mu:
            self.param_names.append("mu")
        if cfg.estimate_c:
            self.param_names.append("c")

        self.x0 = self._initial_guess()

    def _angle_to_rad(self, val: float, unit: str) -> float:
        if unit == "rad":
            return val
        if unit == "gon":
            return val * GON_TO_RAD
        if unit == "deg":
            return val * DEG_TO_RAD
        if self.cfg.angles_unit == "gon":
            return val * GON_TO_RAD
        elif self.cfg.angles_unit == "deg":
            return val * DEG_TO_RAD
        else:
            return val

    def _dir_sigma_rad(self) -> float:
        return (self.cfg.sigma_dir_mgon * 1e-3) * GON_TO_RAD

    def _zen_sigma_rad(self) -> float:
        return (self.cfg.sigma_zen_mgon * 1e-3) * GON_TO_RAD

    def _initial_guess(self) -> np.ndarray:
        if not self.obs:
            raise ValueError("No observations provided")
        xs, ys, zs, n = 0.0, 0.0, 0.0, 0
        for o in self.obs:
            cp = self.controls.get(o.pid)
            if cp:
                xs += cp.X; ys += cp.Y; zs += cp.Z; n += 1
        if n == 0:
            raise ValueError("No valid control points referenced in observations")
        X0 = xs / n
        Y0 = ys / n
        Z0 = zs / n - (self.cfg.h_instrument if self.cfg.h_instrument else 0.0)
        omega = 0.0
        x = [X0, Y0, Z0, omega]
        if self.cfg.estimate_mu:
            x.append(0.0)
        if self.cfg.estimate_c:
            x.append(0.0)
        return np.array(x, dtype=float)

    def _build_system(self, x: np.ndarray):
        X0, Y0, Z0, omega = x[0], x[1], x[2], x[3]
        mu = x[4] if self.cfg.estimate_mu else 0.0
        c  = x[5] if (self.cfg.estimate_mu and self.cfg.estimate_c) else (x[4] if self.cfg.estimate_c else 0.0)

        m = len(self.obs)
        npar = len(self.param_names)

        A = np.zeros((m, npar), dtype=float)
        l = np.zeros(m, dtype=float)
        f = np.zeros(m, dtype=float)
        P_diag = np.zeros(m, dtype=float)

        hI = self.cfg.h_instrument

        sig_dir = self._dir_sigma_rad()
        sig_zen = self._zen_sigma_rad()

        labels = []

        for k, o in enumerate(self.obs):
            cp = self.controls[o.pid]
            Xt, Yt, Zt = cp.X, cp.Y, cp.Z + o.h_target
            dX = Xt - X0
            dY = Yt - Y0
            dZ = (Zt) - (Z0 + hI)

            H = math.hypot(dX, dY)
            rho = math.sqrt(dX*dX + dY*dY + dZ*dZ)

            alpha = math.atan2(dX, dY)
            z_theo = math.acos(max(-1.0, min(1.0, dZ / rho)))

            ray_kappa = self.rays.get(o.ray_id, RayMeta(o.ray_id, 1.0)).kappa
            nk = max(1, int(o.n_series))

            if o.obs_type == "dir":
                D_obs = self._angle_to_rad(o.value, o.unit)
                l[k] = D_obs
                f[k] = alpha + omega
                denom = (dX*dX + dY*dY)
                d_alpha_dX0 =  dY / denom
                d_alpha_dY0 = -dX / denom
                A[k, 0] = -d_alpha_dX0
                A[k, 1] = -d_alpha_dY0
                A[k, 2] = 0.0
                A[k, 3] = -1.0
                var = (sig_dir**2) / nk
                P_diag[k] = 1.0 / (ray_kappa * var)
                labels.append(f"DIR ray={o.ray_id}->{o.pid}")

            elif o.obs_type == "zen":
                Z_obs = self._angle_to_rad(o.value, o.unit)
                l[k] = Z_obs
                f[k] = z_theo
                eps = 1e-12
                H_safe = max(H, eps)
                ratio = dZ / H_safe
                denomE = 1.0 + ratio*ratio
                dH_dX0 = -dX / H_safe
                dH_dY0 = -dY / H_safe
                dE_dX0 = (-(dZ * dH_dX0) / (H_safe*H_safe)) / denomE
                dE_dY0 = (-(dZ * dH_dY0) / (H_safe*H_safe)) / denomE
                dE_dZ0 = (-1.0 / H_safe) / denomE
                A[k, 0] = +dE_dX0
                A[k, 1] = +dE_dY0
                A[k, 2] = +dE_dZ0
                A[k, 3] = 0.0
                var = (sig_zen**2) / nk
                P_diag[k] = 1.0 / (ray_kappa * var)
                labels.append(f"ZEN ray={o.ray_id}->{o.pid}")

            elif o.obs_type == "dist":
                rho_obs = o.value
                l[k] = rho_obs
                f[k] = (1.0 + mu) * rho + (c if self.cfg.estimate_c else 0.0)

                if self.cfg.estimate_mu and self.cfg.estimate_c:
                    col_mu = 4; col_c = 5
                elif self.cfg.estimate_mu and not self.cfg.estimate_c:
                    col_mu = 4; col_c = None
                elif (not self.cfg.estimate_mu) and self.cfg.estimate_c:
                    col_mu = None; col_c = 4
                else:
                    col_mu = None; col_c = None

                A[k, 0] = -(1.0 + mu) * (dX / rho)
                A[k, 1] = -(1.0 + mu) * (dY / rho)
                A[k, 2] = -(1.0 + mu) * (dZ / rho)
                A[k, 3] = 0.0
                if col_mu is not None:
                    A[k, col_mu] = -rho
                if col_c is not None:
                    A[k, col_c]  = -1.0

                a = self.cfg.edm_a_mm * 1e-3
                b = self.cfg.edm_b_ppm * 1e-6
                var = (a*a + (b * rho_obs)**2) / nk
                P_diag[k] = 1.0 / (ray_kappa * var)
                labels.append(f"DIST ray={o.ray_id}->{o.pid}")

            else:
                raise ValueError(f"Unknown observation type: {o.obs_type}")

        P = np.diag(P_diag)
        w = l - f
        return A, w, P, labels, l, f

    def solve(self) -> "LSResult":
        x = self.x0.copy()
        for _ in range(self.cfg.max_iter):
            A, w, P, labels, l, f = self._build_system(x)
            N = A.T @ P @ A
            u = A.T @ P @ w
            try:
                dx = np.linalg.solve(N, u)
            except np.linalg.LinAlgError:
                dx = np.linalg.lstsq(N, u, rcond=None)[0]
            x += dx
            if np.linalg.norm(dx) < self.cfg.tol:
                break

        A, w, P, labels, l, f = self._build_system(x)
        v = l - f - A @ (x - self.x0)
        dof = len(l) - len(self.param_names)
        sigma0_hat = math.sqrt(float(v.T @ P @ v) / max(1, dof))

        N = A.T @ P @ A
        try:
            Qxx = np.linalg.inv(N)
        except np.linalg.LinAlgError:
            Qxx = np.linalg.pinv(N)
        cov_x = sigma0_hat**2 * Qxx

        H = A @ Qxx @ A.T @ P
        I = np.eye(H.shape[0])
        Qvv = I - H
        qvv_diag = np.clip(np.diag(Qvv), 1e-12, None)
        norm_res = v / (sigma0_hat * np.sqrt(qvv_diag))
        redundancies = np.diag(H)

        return LSResult(
            x_hat=x, cov_x=cov_x, sigma0_hat=sigma0_hat,
            param_names=self.param_names, residuals=v, norm_residuals=norm_res,
            redundancies=redundancies, Qvv_diag=qvv_diag, A=A, P=P, l=l, f=f
        )

def read_controls_csv(path: Path) -> Dict[str, ControlPoint]:
    df = pd.read_csv(path)
    controls = {}
    for _, row in df.iterrows():
        controls[str(row["pid"])] = ControlPoint(
            pid=str(row["pid"]), X=float(row["X"]), Y=float(row["Y"]), Z=float(row["Z"])
        )
    return controls

def read_rays_csv(path: Optional[Path]) -> Dict[str, RayMeta]:
    rays = {}
    if path is None or not path.exists():
        return rays
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        rays[str(row["ray_id"])] = RayMeta(ray_id=str(row["ray_id"]), kappa=float(row["kappa"]))
    return rays

def read_observations_csv(path: Path, default_angles_unit="gon") -> List[Observation]:
    df = pd.read_csv(path)
    obs = []
    for _, row in df.iterrows():
        unit = row.get("unit", default_angles_unit)
        obs.append(Observation(
            ray_id=str(row["ray_id"]), pid=str(row["pid"]),
            obs_type=str(row["obs_type"]).strip().lower(),
            value=float(row["value"]), unit=str(unit),
            n_series=int(row.get("n_series", 1)),
            h_target=float(row.get("h_target", 0.0)),
        ))
    return obs

def run_cli(controls_csv: Path, observations_csv: Path, rays_csv: Optional[Path],
            config_json: Optional[Path], output_prefix: Path):
    controls = read_controls_csv(controls_csv)
    rays = read_rays_csv(rays_csv)
    obs = read_observations_csv(observations_csv)

    cfg = Config()
    if config_json and config_json.exists():
        with open(config_json, "r", encoding="utf-8") as f:
            d = json.load(f)
        for k, v in d.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)

    solver = FreeStationLS(controls, obs, rays, cfg)
    res = solver.solve()

    output_prefix = Path(output_prefix)

    params = []
    for i, name in enumerate(res.param_names):
        sd = math.sqrt(res.cov_x[i, i]) if res.cov_x.shape[0] > i else float("nan")
        params.append({"param": name, "estimate": res.x_hat[i], "sd": sd})
    df_params = pd.DataFrame(params)
    df_params.to_csv(output_prefix.with_suffix(".params.csv"), index=False)

    df_res = pd.DataFrame({
        "obs_index": np.arange(len(res.residuals)),
        "residual": res.residuals,
        "norm_residual": res.norm_residuals,
        "redundancy": res.redundancies,
        "Qvv_diag": res.Qvv_diag,
    })
    df_res.to_csv(output_prefix.with_suffix(".residuals.csv"), index=False)

    meta = {
        "sigma0_hat": res.sigma0_hat,
        "dof": int(len(res.l) - len(res.param_names)),
        "param_names": res.param_names,
        "config_used": cfg.__dict__,
    }
    with open(output_prefix.with_suffix(".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Free-station LS adjustment with per-ray and per-type weighting.")
    ap.add_argument("--controls", required=True, help="CSV with columns: pid,X,Y,Z")
    ap.add_argument("--observations", required=True, help="CSV with columns: ray_id,pid,obs_type,value,unit,n_series,h_target")
    ap.add_argument("--rays", required=False, help="CSV with columns: ray_id,kappa (>=1)")
    ap.add_argument("--config", required=False, help="JSON with Config overrides")
    ap.add_argument("--out", required=True, help="Output prefix, e.g. /tmp/result")
    args = ap.parse_args()

    out = run_cli(Path(args.controls), Path(args.observations),
                  Path(args.rays) if args.rays else None,
                  Path(args.config) if args.config else None,
                  Path(args.out))
    print(json.dumps(out, indent=2))
