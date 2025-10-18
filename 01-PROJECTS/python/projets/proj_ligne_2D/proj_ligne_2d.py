# -*- coding: utf-8 -*-
"""
Projection 2D (plan XY) sur une ligne DEBUT/FIN.
Calcule :
- PM (2D) : distance à plat le long de la ligne jusqu'au pied perpendiculaire 2D,
            avec décalage PM0_OFFSET appliqué (PM = s [+ clamp] + PM0_OFFSET)
- H       : déport horizontal (signé) dans le plan XY
- V       : écart vertical GLOBAL (Z_M - Z_ligne à l'abscisse t), pas perpendiculaire

Entrée (feuille principale) : POINT | X | Y | Z  (alias tolérés)
Option (feuille 'LIGNE')   : NOM | X | Y | Z  (lignes 'DEBUT' et 'FIN')
Sortie : POINT | X | Y | Z | PM | H | V
"""

import math
from pathlib import Path
import pandas as pd
import unicodedata

# -----------------------
# Paramètres utilisateur
# -----------------------
INPUT_XLSX  = r"points_2d.xlsx"
OUTPUT_XLSX = r"points_2d_resultats.xlsx"

CLAMP_PM_TO_SEGMENT = False   # True => bride PM à [0, L2D] ; False => droite infinie
PM0_OFFSET          = 0.0     # décalage d'abscisse (chaîne de départ)

LINE_SHEET_NAME = "LIGNE"
LINE_DEBUT_KEY  = "DEBUT"
LINE_FIN_KEY    = "FIN"

EPS = 1e-12

# -----------------------
# Aliases entêtes
# -----------------------
def _norm_key(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s)).encode("ascii","ignore").decode("ascii")
    return t.strip().lower().replace(" ","").replace("_","")

ALIASES = {
    "POINT": ["point","pt","nom","name","id","nomdupoint","pointname"],
    "X":     ["x","est","e","xgeo","coordonneex"],
    "Y":     ["y","nord","n","ygeo","coordonneey"],
    "Z":     ["z","alt","h","zgeo","altitude","altimetrie"],
}

def map_columns(df):
    keys = {_norm_key(c): c for c in df.columns}
    mapping, missing = {}, []
    for target, alts in ALIASES.items():
        found = None
        for a in alts:
            if a in keys:
                found = keys[a]; break
        if found is None:
            missing.append(target)
        else:
            mapping[target] = found
    if missing:
        raise ValueError("Colonnes manquantes: " + ", ".join(missing) +
                         f" | Entêtes trouvées: {list(df.columns)}")
    return mapping

# -----------------------
# Outils géométriques
# -----------------------
def norm2(vx, vy): return math.hypot(vx, vy)

def read_line_from_excel(xlsx_path):
    try:
        df_line = pd.read_excel(xlsx_path, sheet_name=LINE_SHEET_NAME)
    except Exception:
        return None
    need = {"NOM","X","Y","Z"}
    if not need.issubset({c.strip().upper() for c in df_line.columns}):
        return None
    df = df_line.copy()
    df.columns = [c.strip().upper() for c in df.columns]

    def get_row(name):
        sub = df[df["NOM"].astype(str).str.upper().str.strip() == name]
        if sub.empty: return None
        r = sub.iloc[0]
        return float(r["X"]), float(r["Y"]), float(r["Z"])
    P0 = get_row(LINE_DEBUT_KEY)
    P1 = get_row(LINE_FIN_KEY)
    if P0 is None or P1 is None: return None
    return P0, P1

# -----------------------
# Main
# -----------------------
def main():
    xlsx_in = Path(INPUT_XLSX)
    if not xlsx_in.exists():
        raise FileNotFoundError(f"Fichier introuvable: {xlsx_in}")

    # Ligne
    line = read_line_from_excel(xlsx_in)
    if line is not None:
        (X0,Y0,Z0), (X1,Y1,Z1) = line
    else:
        raise ValueError("Définis la feuille 'LIGNE' avec DEBUT/FIN (X,Y,Z) pour la version 2D.")

    # Direction 2D u = (ux,uy), normale 2D n = (-uy, ux)
    dx, dy = (X1-X0), (Y1-Y0)
    L2D = norm2(dx, dy)
    if L2D < EPS:
        raise ValueError("Ligne 2D de longueur nulle (mêmes XY pour DEBUT et FIN).")
    ux, uy = dx/L2D, dy/L2D
    nx, ny = -uy, ux

    dZ = Z1 - Z0

    # Données
    df = pd.read_excel(xlsx_in)
    cols = map_columns(df)
    df_out = df.rename(columns={
        cols["POINT"]:"POINT", cols["X"]:"X", cols["Y"]:"Y", cols["Z"]:"Z"
    }).copy()

    PM_list, H_list, V_list = [], [], []

    for _, row in df_out.iterrows():
        try:
            X, Y, Z = float(row["X"]), float(row["Y"]), float(row["Z"])
        except Exception:
            PM_list.append(None); H_list.append(None); V_list.append(None); continue

        ax, ay = X - X0, Y - Y0
        s = ax*ux + ay*uy  # abscisse 2D le long de la droite (non décalée)

        s_used = max(0.0, min(s, L2D)) if CLAMP_PM_TO_SEGMENT else s

        # pied 2D
        Fx, Fy = X0 + s_used*ux, Y0 + s_used*uy
        # déport horizontal signé en 2D
        H = (X - Fx)*nx + (Y - Fy)*ny
        # vertical global: Z - Z_ligne(t) avec t = s_used/L2D
        t = s_used / L2D
        Z_line = Z0 + t*dZ
        V = Z - Z_line

        PM_val = s_used + PM0_OFFSET
        PM_list.append(PM_val)
        H_list.append(H)
        V_list.append(V)

    df_out["PM"] = PM_list
    df_out["H"]  = H_list
    df_out["V"]  = V_list

    desired = ["POINT","X","Y","Z","PM","H","V"]
    df_out = df_out[[c for c in desired if c in df_out.columns] +
                    [c for c in df_out.columns if c not in desired]]

    df_out.to_excel(OUTPUT_XLSX, index=False)
    print(f"OK. Résultats écrits dans: {OUTPUT_XLSX}")

if __name__ == "__main__":
    main()
