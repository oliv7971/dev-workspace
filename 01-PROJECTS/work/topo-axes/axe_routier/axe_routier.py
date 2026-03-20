# Module axe_routier.py

import pandas as pd
import numpy as np

def lire_axe_plan_csv(chemin_fichier):
    df = pd.read_csv(chemin_fichier, sep=";", encoding="utf-8")
    df["PK_end"] = df["PK"].shift(-1)
    df.iloc[-1, df.columns.get_loc("PK_end")] = df["PK"].iloc[-1] + 10
    return df

def lire_profil_long_csv(chemin_fichier):
    df = pd.read_csv(chemin_fichier, sep=";", encoding="utf-8")
    df["PK_end"] = df["PK_start"].shift(-1)
    df.iloc[-1, df.columns.get_loc("PK_end")] = df["PK_start"].iloc[-1] + 10
    return df

def calculer_xyz_from_dataframes(df_plan, df_profil, PK, deport=0.0):
    for _, row in df_plan.iterrows():
        if row["PK"] <= PK <= row["PK_end"]:
            d = PK - row["PK"]
            az_rad = np.radians(row["azimut_deg"])
            X = row["X"] + d * np.sin(az_rad)
            Y = row["Y"] + d * np.cos(az_rad)
            X -= deport * np.cos(az_rad)
            Y += deport * np.sin(az_rad)
            break
    else:
        return None

    for _, row in df_profil.iterrows():
        if row["PK_start"] <= PK <= row["PK_end"]:
            pente = row["pente_pct"] / 100.0
            Z = row["Z_start"] - (PK - row["PK_start"]) * pente
            break
    else:
        Z = None

    return round(X, 3), round(Y, 3), round(Z, 3)

def calcul_inverse_xyz_from_dataframes(df_plan, df_profil, X, Y, Z=None):
    """
    Trouve le PK et le déport latéral correspondant à un point (X, Y), en se basant sur df_plan.
    Puis calcule l'altitude théorique Z selon df_profil (si demandé).
    """

    meilleure_projection = None
    min_distance = float("inf")
    pk_proj = None
    deport = None

    for i, row in df_plan.iterrows():
        if pd.isna(row["PK_end"]):
            continue

        x0, y0 = row["X"], row["Y"]
        az_rad = np.radians(row["azimut_deg"])
        L = (row["PK_end"] - row["PK"])
        x1 = x0 + L * np.sin(az_rad)
        y1 = y0 + L * np.cos(az_rad)

        # Vecteurs
        vx, vy = x1 - x0, y1 - y0
        wx, wy = X - x0, Y - y0
        L2 = vx**2 + vy**2

        if L2 == 0:
            continue

        # Projection scalaire
        t = (wx * vx + wy * vy) / L2
        t_clamped = max(0, min(1, t))
        x_proj = x0 + t_clamped * vx
        y_proj = y0 + t_clamped * vy

        distance = np.hypot(X - x_proj, Y - y_proj)

        if distance < min_distance:
            min_distance = distance
            meilleure_projection = row
            pk_proj = row["PK"] + t_clamped * L
            # Déport : distance latérale avec signe
            angle = np.arctan2(Y - y_proj, X - x_proj) - az_rad
            deport = distance * np.sign(np.sin(angle))

    if meilleure_projection is None:
        return None, None, None, None

    # Interpolation Z
    Z_theorique = None
    for _, row in df_profil.iterrows():
        if row["PK_start"] <= pk_proj <= row["PK_end"]:
            pente = row["pente_pct"] / 100.0
            Z_theorique = row["Z_start"] - (pk_proj - row["PK_start"]) * pente
            break

    return round(pk_proj, 3), round(deport, 3), round(Z_theorique, 3), Z
