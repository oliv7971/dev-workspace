# -*- coding: utf-8 -*-
"""
Reconstruction 2D (plan XY) depuis PM,H,V (définis en 2D):
- XY : P0 + s*u + H*n  avec s = PM - PM0_OFFSET
- Z  : Z0 + (s/L2D)*(Z1-Z0) + V  (V vertical global)
Entrée : POINT | PM | H | V
Option (feuille 'LIGNE') : NOM | X | Y | Z  (DEBUT/FIN)
Sortie : POINT | PM | H | V | X | Y | Z
"""

import math
from pathlib import Path
import pandas as pd
import unicodedata

# -----------------------
# Paramètres utilisateur
# -----------------------
INPUT_XLSX  = r"points_2d_inverse.xlsx"
OUTPUT_XLSX = r"points_2d_inverse_resultats.xlsx"

PM0_OFFSET = 0.0               # même décalage que côté projection

LINE_SHEET_NAME = "LIGNE"
LINE_DEBUT_KEY  = "DEBUT"
LINE_FIN_KEY    = "FIN"

EPS = 1e-12

def _norm_key(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s)).encode("ascii","ignore").decode("ascii")
    return t.strip().lower().replace(" ","").replace("_","")

ALIASES = {
    "POINT": ["point","pt","nom","name","id"],
    "PM":    ["pm","chaine","abscisse","abscisse2d","distance2d"],
    "H":     ["h","deporth","dh","horiz","horizontal"],
    "V":     ["v","deportv","dv","vert","vertical"],
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

def main():
    xlsx_in = Path(INPUT_XLSX)
    if not xlsx_in.exists():
        raise FileNotFoundError(f"Fichier introuvable: {xlsx_in}")

    line = read_line_from_excel(xlsx_in)
    if line is None:
        raise ValueError("Définis la feuille 'LIGNE' avec DEBUT/FIN (X,Y,Z).")
    (X0,Y0,Z0), (X1,Y1,Z1) = line

    dx, dy = (X1-X0), (Y1-Y0)
    L2D = norm2(dx, dy)
    if L2D < EPS:
        raise ValueError("Ligne 2D de longueur nulle (mêmes XY pour DEBUT et FIN).")
    ux, uy = dx/L2D, dy/L2D
    nx, ny = -uy, ux
    dZ = Z1 - Z0

    df = pd.read_excel(xlsx_in)
    cols = map_columns(df)
    df_in = df.rename(columns={
        cols["POINT"]:"POINT", cols["PM"]:"PM", cols["H"]:"H", cols["V"]:"V"
    }).copy()

    Xs, Ys, Zs = [], [], []
    for _, row in df_in.iterrows():
        try:
            PM, H, V = float(row["PM"]), float(row["H"]), float(row["V"])
        except Exception:
            Xs.append(None); Ys.append(None); Zs.append(None); continue

        # ramener PM dans le repère de la ligne
        s = PM - PM0_OFFSET

        # XY
        X = X0 + s*ux + H*nx
        Y = Y0 + s*uy + H*ny
        # Z (vertical global)
        t = s / L2D
        Z_line = Z0 + t*dZ
        Z = Z_line + V

        Xs.append(X); Ys.append(Y); Zs.append(Z)

    df_out = df_in.copy()
    df_out["X"] = Xs
    df_out["Y"] = Ys
    df_out["Z"] = Zs

    desired = ["POINT","PM","H","V","X","Y","Z"]
    df_out = df_out[[c for c in desired if c in df_out.columns] +
                    [c for c in df_out.columns if c not in desired]]

    df_out.to_excel(OUTPUT_XLSX, index=False)
    print(f"OK. Résultats écrits dans: {OUTPUT_XLSX}")

if __name__ == "__main__":
    main()
