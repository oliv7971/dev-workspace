
import sys
import pandas as pd
from dataclasses import dataclass
from math import hypot, cos, sin, radians
from typing import Tuple

@dataclass
class AlignmentLine:
    X0: float
    Y0: float
    Z0: float
    ux: float
    uy: float
    p: float

    @staticmethod
    def from_two_points(P0: Tuple[float, float, float], P1: Tuple[float, float, float]) -> "AlignmentLine":
        X0, Y0, Z0 = P0
        X1, Y1, Z1 = P1
        dx, dy = X1 - X0, Y1 - Y0
        ds = hypot(dx, dy)
        if ds == 0:
            raise ValueError("Deux points confondus : axe illisible.")
        ux, uy = dx / ds, dy / ds
        p = (Z1 - Z0) / ds
        return AlignmentLine(X0, Y0, Z0, ux, uy, p)

    @staticmethod
    def from_point_azimuth_slope(P0: Tuple[float, float, float], az_deg: float, slope_p: float) -> "AlignmentLine":
        X0, Y0, Z0 = P0
        th = radians(az_deg)
        ux, uy = cos(th), sin(th)
        return AlignmentLine(X0, Y0, Z0, ux, uy, slope_p)

    def _n_left(self) -> Tuple[float, float]:
        return (-self.uy, self.ux)

    def axis_point(self, s: float) -> Tuple[float, float, float]:
        return (self.X0 + s * self.ux, self.Y0 + s * self.uy, self.Z0 + self.p * s)

    def forward(self, s: float, h: float = 0.0, v: float = 0.0):
        nx, ny = self._n_left()
        Xa, Ya, Za = self.axis_point(s)
        return (Xa + h * nx, Ya + h * ny, Za + v)

    def project_2d(self, X: float, Y: float, Z: float):
        dx, dy = X - self.X0, Y - self.Y0
        nx, ny = self._n_left()
        s2D = dx * self.ux + dy * self.uy
        h2D = dx * nx + dy * ny
        v2D = Z - (self.Z0 + self.p * s2D)
        return (s2D, h2D, v2D)

    def project_3d(self, X: float, Y: float, Z: float):
        dx, dy, dz = X - self.X0, Y - self.Y0, Z - self.Z0
        denom = 1.0 + self.p * self.p
        s3D = (dx * self.ux + dy * self.uy + dz * self.p) / denom
        Xa, Ya, Za = self.axis_point(s3D)
        nx, ny = self._n_left()
        h3D = (X - Xa) * nx + (Y - Ya) * ny
        v3D = Z - Za
        return (s3D, h3D, v3D)

def build_alignment(axe_df: pd.DataFrame) -> AlignmentLine:
    row = axe_df.loc[axe_df["use_this_row"]==1].iloc[0]
    mode = str(row["mode"]).strip().lower()
    if mode == "two_points":
        P0 = (float(row["X0"]), float(row["Y0"]), float(row["Z0"]))
        P1 = (float(row["X1"]), float(row["Y1"]), float(row["Z1"]))
        return AlignmentLine.from_two_points(P0, P1)
    elif mode == "azimuth":
        P0 = (float(row["X0"]), float(row["Y0"]), float(row["Z0"]))
        az = float(row["az_deg"])
        slope = float(row["slope_p"])
        return AlignmentLine.from_point_azimuth_slope(P0, az, slope)
    else:
        raise ValueError("Mode inconnu dans AXE.mode (attendu: 'two_points' ou 'azimuth').")

def main(xlsx_path: str):
    xls = pd.ExcelFile(xlsx_path)
    axe_df = pd.read_excel(xls, "AXE")
    A = build_alignment(axe_df)

    # Forward
    if "FORWARD_INPUT" in xls.sheet_names:
        fin = pd.read_excel(xls, "FORWARD_INPUT")
        fout = fin.copy()
        Xs, Ys, Zs = [], [], []
        for _, r in fin.iterrows():
            X, Y, Z = A.forward(float(r["s"]), float(r.get("h",0.0)), float(r.get("v",0.0)))
            Xs.append(X); Ys.append(Y); Zs.append(Z)
        fout["X"] = Xs; fout["Y"] = Ys; fout["Z"] = Zs
    else:
        fout = pd.DataFrame()

    # Project
    if "PROJECT_INPUT" in xls.sheet_names:
        pin = pd.read_excel(xls, "PROJECT_INPUT")
        p2d = pin.copy()
        p3d = pin.copy()
        s2, h2, v2 = [], [], []
        s3, h3, v3 = [], [], []
        for _, r in pin.iterrows():
            s2d, h2d, v2d = A.project_2d(float(r["X"]), float(r["Y"]), float(r["Z"]))
            s3d, h3d, v3d = A.project_3d(float(r["X"]), float(r["Y"]), float(r["Z"]))
            s2.append(s2d); h2.append(h2d); v2.append(v2d)
            s3.append(s3d); h3.append(h3d); v3.append(v3d)
        p2d["s2D"] = s2; p2d["h2D"] = h2; p2d["v2D"] = v2
        p3d["s3D"] = s3; p3d["h3D"] = h3; p3d["v3D"] = v3
    else:
        p2d = pd.DataFrame(); p3d = pd.DataFrame()

    # Write outputs
    with pd.ExcelWriter(xlsx_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        axe_df.to_excel(writer, sheet_name="AXE", index=False)
        if not fout.empty:
            fout.to_excel(writer, sheet_name="FORWARD_OUTPUT", index=False)
        if not p2d.empty:
            p2d.to_excel(writer, sheet_name="PROJECT_OUTPUT_2D", index=False)
        if not p3d.empty:
            p3d.to_excel(writer, sheet_name="PROJECT_OUTPUT_3D", index=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_alignment_excel.py <chemin_du_classeur.xlsx>")
    else:
        main(sys.argv[1])
