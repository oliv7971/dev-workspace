
import pandas as pd
import numpy as np
import re
from pathlib import Path

# Charger les fichiers
lines_file = Path("I_GET2_pentesRBT.txt")
points_file = Path("20250730_GET.xyz")

# Charger les lignes théoriques
df_lines_raw = pd.read_csv(lines_file, sep=";", header=None, names=["code", "X", "Y", "Z"])
df_lines_raw["line_id"] = df_lines_raw["code"].astype(str).str[:-1]
df_lines_raw["pt_type"] = df_lines_raw["code"].astype(str).str[-1]

# Séparer points début/fin
start_pts = df_lines_raw[df_lines_raw["pt_type"] == "0"].set_index("line_id")
end_pts = df_lines_raw[df_lines_raw["pt_type"] == "1"].set_index("line_id")

# Créer les segments
lines = pd.merge(
    start_pts[["X", "Y", "Z"]], end_pts[["X", "Y", "Z"]],
    left_index=True, right_index=True,
    suffixes=("_start", "_end")
).reset_index()

# Charger les points levés
with open(points_file, "r") as f:
    raw_points = [line.strip() for line in f if line.strip()]

points_data = []
for line in raw_points:
    parts = re.split(r"\s+", line)
    if len(parts) == 4:
        name, x, y, z = parts
        points_data.append((name, float(x), float(y), float(z)))

df_pts = pd.DataFrame(points_data, columns=["name", "X", "Y", "Z"])

# Projection avec prolongement configurable
prolongement_max = 1.0  # en mètres
prolonged_results_signed = []

for _, pt in df_pts.iterrows():
    P = np.array([pt["X"], pt["Y"], pt["Z"]])
    best_match = None
    best_delta_z = float('inf')

    for _, line in lines.iterrows():
        A = np.array([line["X_start"], line["Y_start"], line["Z_start"]])
        B = np.array([line["X_end"], line["Y_end"], line["Z_end"]])
        AB = B - A
        AP = P - A
        AB_len = np.linalg.norm(AB)

        t = np.dot(AP, AB) / np.dot(AB, AB)
        proj = A + t * AB
        delta_z = abs(P[2] - proj[2])
        delta_xy = np.linalg.norm(P[:2] - proj[:2])
        abscisse_proj = t * AB_len  # signé

        if (-prolongement_max <= abscisse_proj <= AB_len + prolongement_max):
            if delta_z < best_delta_z:
                best_match = {
                    "point": pt["name"],
                    "X": pt["X"],
                    "Y": pt["Y"],
                    "Z_mesuré": pt["Z"],
                    "ligne": line["line_id"],
                    "abscisse_proj": abscisse_proj,
                    "déport_horizontal": delta_xy,
                    "Z_proj": proj[2],
                    "déport_altimétrique": pt["Z"] - proj[2],
                }
                best_delta_z = delta_z

    if best_match:
        prolonged_results_signed.append(best_match)

df_signed = pd.DataFrame(prolonged_results_signed)
df_signed["hors_tolerance"] = df_signed["déport_altimétrique"].abs() > 0.01

# Export Excel
df_signed.to_excel("resultat_projection_points_lignes_corrige.xlsx", index=False)
