# Module axe_routier.py — version modulaire et documentée

import pandas as pd
import numpy as np

def lire_options_excel(xls):
    try:
        df_options = xls.parse("options")
        options = dict(zip(df_options["nom_option"].str.lower(), df_options["valeur"]))
        return options
    except Exception:
        return {}

def generer_axe_plan_depuis_parametres(df_input):
    rows = []
    for _, row in df_input.iterrows():
        mode = row["mode"].strip().upper()
        PK = row["PK"]
        X1, Y1 = row["X"], row["Y"]
        if mode == "A":
            X2, Y2 = row["X2"], row["Y2"]
            dx, dy = X2 - X1, Y2 - Y1
            longueur = np.hypot(dx, dy)
            azimut_rad = np.arctan2(dx, dy)
            azimut_grad = (azimut_rad * 200 / np.pi) % 400
        elif mode == "B":
            azimut_grad = row["azimut_grad"] % 400
            longueur = row["longueur"]
            azimut_rad = azimut_grad * np.pi / 200
            X2 = X1 + longueur * np.sin(azimut_rad)
            Y2 = Y1 + longueur * np.cos(azimut_rad)
        else:
            continue
        rows.append({
            "PK": PK,
            "X": X1,
            "Y": Y1,
            "azimut_grad": round(azimut_grad, 4),
            "PK_end": PK + longueur,
            "type_segment": "DROITE",
            "rayon_m": None,
            "sens": None,
            "parametre_clothoide": None
        })
    return pd.DataFrame(rows)

def calcul_xy_droite(row, PK, deport):
    az_rad = np.radians(row["azimut_grad"] * 0.9)
    d = PK - row["PK"]
    X = row["X"] + d * np.sin(az_rad) - deport * np.cos(az_rad)
    Y = row["Y"] + d * np.cos(az_rad) + deport * np.sin(az_rad)
    return X, Y

def calcul_z_droite(row, PK):
    pente = row["pente_pct"] / 100.0
    Z = row["Z_start"] - (PK - row["PK_start"]) * pente
    return Z

def appliquer_deport_vertical(Z, pente_pct, deport_vertical, mode="verticale"):
    if mode == "verticale":
        return Z + deport_vertical
    elif mode == "perpendiculaire":
        pente = pente_pct / 100.0
        correction = deport_vertical * np.sqrt(1 + pente**2)
        return Z + correction * (-1 if pente >= 0 else 1)
    else:
        raise ValueError("Mode de déport vertical inconnu : verticale ou perpendiculaire")

def calculer_xyz_from_dataframes(df_plan, df_profil, PK, deport=0.0, deport_vertical=0.0, mode="verticale"):
    for _, row in df_plan.iterrows():
        if row["PK"] <= PK <= row["PK_end"]:
            X, Y = calcul_xy_droite(row, PK, deport)
            break
    else:
        return None, None, None

    for _, row in df_profil.iterrows():
        if row["PK_start"] <= PK <= row["PK_end"]:
            Z = calcul_z_droite(row, PK)
            Z = appliquer_deport_vertical(Z, row["pente_pct"], deport_vertical, mode)
            break
    else:
        Z = None

    return round(X, 3), round(Y, 3), round(Z, 3)

def projeter_sur_droite(X, Y, row):
    x0, y0 = row["X"], row["Y"]
    az_rad = np.radians(row["azimut_grad"] * 0.9)
    dx = X - x0
    dy = Y - y0
    d_proj = dx * np.sin(az_rad) + dy * np.cos(az_rad)
    pk_proj = row["PK"] + d_proj
    d_lat = -dx * np.cos(az_rad) + dy * np.sin(az_rad)
    deport = d_lat
    return (None, None), abs(deport), pk_proj, deport

def calcul_inverse_xyz_from_dataframes(df_plan, df_profil, X, Y, Z=None, mode="verticale"):
    meilleure_projection = None
    min_distance = float("inf")
    pk_proj = None
    deport = None

    for i, row in df_plan.iterrows():
        if pd.isna(row["PK_end"]):
            continue
        if row.get("type_segment", "DROITE") == "DROITE":
            _, distance, pk, dep = projeter_sur_droite(X, Y, row)
        else:
            continue
        if distance < min_distance:
            min_distance = distance
            meilleure_projection = row
            pk_proj = pk
            deport = dep

    if meilleure_projection is None:
        return None, None, None, None

    pente_pct = None
    Zaxe = None
    row_profil = None
    for _, row in df_profil.iterrows():
        if row["PK_start"] <= pk_proj <= row["PK_end"]:
            pente_pct = row["pente_pct"]
            Zaxe = calcul_z_droite(row, pk_proj)
            row_profil = row
            break

    if Z is not None and Zaxe is not None and mode == "perpendiculaire" and pente_pct is not None:
        d_plan = pk_proj - row_profil["PK_start"]
        delta_z = Z - Zaxe
        pk_curvi = row_profil["PK_start"] + np.hypot(d_plan, delta_z)
        Zaxe = calcul_z_droite(row_profil, pk_curvi)
        pk_proj = pk_curvi

    return round(pk_proj, 3), round(deport, 3), round(Zaxe, 3), Z
