# -*- coding: utf-8 -*-
"""
Reconstruire les coordonnées (X,Y,Z) à partir de:
- PM : abscisse curviligne 3D le long de la ligne (depuis DEBUT)
- H  : écart horizontal perpendiculaire à la ligne
- V  : écart vertical   perpendiculaire à la ligne

Entrée (feuille principale):
    POINT | PM | H | V

Optionnel (feuille 'LIGNE'):
    NOM   | X | Y | Z
    DEBUT | ...
    FIN   | ...

Sortie:
    POINT | PM | H | V | X | Y | Z
"""

import math
from pathlib import Path
import pandas as pd
import unicodedata

# =========================
# PARAMÈTRES UTILISATEUR
# =========================
INPUT_XLSX  = r"points_inverse_HA211.xlsx"
OUTPUT_XLSX = r"points_inverse_resultats_HA211.xlsx"

LINE_START = (823148.77859181060921400785, 1091707.64696751441806554794, -123.75799999999999556621)   # X, Y, Z du DEBUT
LINE_END   = (823127.60033771605230867863, 1091752.94025127147324383259, -122.75799999999999556621)   # X, Y, Z de la FIN

LINE_SHEET_NAME = "LIGNE"
LINE_DEBUT_KEY  = "DEBUT"
LINE_FIN_KEY    = "FIN"

COL_POINT = "POINT"
COL_PM, COL_H, COL_V = "PM", "H", "V"
COL_X, COL_Y, COL_Z = "X", "Y", "Z"

# Tolérance num.
EPS = 1e-12

# =========================
# OUTILS GÉOMÉTRIQUES
# =========================
def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def mul_scalar(a, s):
    return (a[0]*s, a[1]*s, a[2]*s)

def sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def safe_unit(v, eps=EPS):
    n = norm(v)
    if n < eps:
        return (0.0, 0.0, 0.0), 0.0
    return (v[0]/n, v[1]/n, v[2]/n), n

# Base locale liée à la ligne (même logique que le script direct):
#  u = direction unité (P0->P1)
#  v_perp = composante de la verticale globale (0,0,1) orthogonale à u (si possible)
#  h_perp = u x v_perp
#  Si ligne ~ verticale: v_perp=(0,0,0) et on définit h_perp stablement.
def line_local_basis(P0, P1, eps=EPS):
    u_raw = sub(P1, P0)
    u, L = safe_unit(u_raw, eps)
    if L < eps:
        raise ValueError("DEBUT et FIN confondus: longueur de ligne nulle.")
    k = (0.0, 0.0, 1.0)

    k_par = mul_scalar(u, dot(k, u))
    v_temp = sub(k, k_par)
    v_perp, nv = safe_unit(v_temp, eps)

    if nv < eps:
        # ligne quasi verticale
        # construire un h_perp quelconque dans le plan normal
        ref = (1.0, 0.0, 0.0)
        if norm(cross(u, ref)) < eps:
            ref = (0.0, 1.0, 0.0)
        ref_perp = sub(ref, mul_scalar(u, dot(ref, u)))
        h_perp, _ = safe_unit(ref_perp, eps)
        return u, (0.0,0.0,0.0), h_perp, L
    else:
        h_perp = cross(u, v_perp)
        h_perp, _ = safe_unit(h_perp, eps)
        return u, v_perp, h_perp, L

# =========================
# MAPPINGS D'ENTÊTES (tolérance)
# =========================
def _norm_key(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode("ascii")
    return t.strip().lower().replace(" ", "").replace("_", "")

ALIASES = {
    "POINT": ["point", "pt", "nom", "name", "id"],
    "PM":    ["pm", "chaine", "abscisse", "abscisse3d", "distance3d"],
    "H":     ["h", "deporth", "dh", "horiz", "horizontal"],
    "V":     ["v", "deportv", "dv", "vert", "vertical"],
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

# =========================
# LECTURE LIGNE
# =========================
def read_line_from_excel(xlsx_path):
    try:
        df_line = pd.read_excel(xlsx_path, sheet_name=LINE_SHEET_NAME)
    except Exception:
        return None
    need = {"NOM", "X", "Y", "Z"}
    if not need.issubset({c.strip().upper() for c in df_line.columns}):
        return None
    df = df_line.copy()
    df.columns = [c.strip().upper() for c in df.columns]

    def get_row(name):
        subdf = df[df["NOM"].astype(str).str.upper().str.strip() == name]
        if subdf.empty:
            return None
        r = subdf.iloc[0]
        return (float(r["X"]), float(r["Y"]), float(r["Z"]))

    P0 = get_row(LINE_DEBUT_KEY)
    P1 = get_row(LINE_FIN_KEY)
    if P0 is None or P1 is None:
        return None
    return P0, P1

# =========================
# CALCUL INVERSE
# =========================
def reconstruct_point(P0, u, v_perp, h_perp, PM, H, V):
    # M = P0 + PM*u + H*h_perp + V*v_perp
    M = add(P0, add(mul_scalar(u, PM), add(mul_scalar(h_perp, H), mul_scalar(v_perp, V))))
    return M

# =========================
# MAIN
# =========================
def main():
    xlsx_in = Path(INPUT_XLSX)
    if not xlsx_in.exists():
        raise FileNotFoundError(f"Fichier introuvable: {xlsx_in}")

    # Ligne : feuille LIGNE prioritaire, sinon valeurs en dur
    line = read_line_from_excel(xlsx_in)
    if line is not None:
        P0, P1 = line
    else:
        P0, P1 = LINE_START, LINE_END

    u, v_perp, h_perp, L = line_local_basis(P0, P1)

    df = pd.read_excel(xlsx_in)
    cols = map_columns(df)

    # Renommer pour travailler avec des noms stables
    df_in = df.rename(columns={
        cols["POINT"]: "POINT",
        cols["PM"]: "PM",
        cols["H"]: "H",
        cols["V"]: "V",
    }).copy()

    X_list, Y_list, Z_list = [], [], []
    warnings = []

    for i, row in df_in.iterrows():
        try:
            PM = float(row["PM"])
            H  = float(row["H"])
            V  = float(row["V"])
        except Exception:
            X_list.append(None); Y_list.append(None); Z_list.append(None)
            continue

        # Cas ligne quasi verticale: v_perp=(0,0,0) => V ignoré (doit être ~0)
        if v_perp == (0.0, 0.0, 0.0) and abs(V) > 1e-9:
            warnings.append(f"Row {i}: ligne verticale -> V ≈ 0 attendu; V={V} utilisé comme 0.")
            V = 0.0

        M = reconstruct_point(P0, u, v_perp, h_perp, PM, H, V)
        X_list.append(M[0]); Y_list.append(M[1]); Z_list.append(M[2])

    df_out = df_in.copy()
    df_out["X"] = X_list
    df_out["Y"] = Y_list
    df_out["Z"] = Z_list

    # Ordre colonnes
    desired = ["POINT", "PM", "H", "V", "X", "Y", "Z"]
    cols_final = [c for c in desired if c in df_out.columns] + [c for c in df_out.columns if c not in desired]
    df_out = df_out[cols_final]

    df_out.to_excel(OUTPUT_XLSX, index=False)

    print(f"OK. Résultats écrits dans: {OUTPUT_XLSX}")
    if warnings:
        print("Avertissements:")
        for w in warnings:
            print(" -", w)

if __name__ == "__main__":
    main()
