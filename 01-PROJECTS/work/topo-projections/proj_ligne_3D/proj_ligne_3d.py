# -*- coding: utf-8 -*-
"""
Projeter des points sur une ligne 3D et calculer:
- PM : abscisse curviligne 3D depuis le début jusqu'au pied perpendiculaire
- H  : écart horizontal perpendiculaire à la ligne
- V  : écart vertical   perpendiculaire à la ligne (perpendiculaire à la ligne, pas à la verticale globale)

Entrée Excel (feuille par défaut = première feuille de données):
    POINT | X | Y | Z

Optionnel: feuille 'LIGNE' avec:
    NOM   | X | Y | Z
    DEBUT | ...
    FIN   | ...

Sortie: mêmes colonnes + PM, H, V (UTF-8, .xlsx)
"""

import math
import sys
from pathlib import Path
import pandas as pd

# =========================
# PARAMÈTRES UTILISATEUR
# =========================
INPUT_XLSX  = r"points_HA211.xlsx"        # Fichier d'entrée
OUTPUT_XLSX = r"points_resultats_HA211.xlsx"  # Fichier de sortie

# (Option 1) Définir la ligne en dur ici (sera ignoré si la feuille 'LIGNE' existe et est valide) :
LINE_START = (823148.77859181060921400785, 1091707.64696751441806554794, -123.75799999999999556621)   # X, Y, Z du DEBUT
LINE_END   = (823127.60033771605230867863, 1091752.94025127147324383259, -122.75799999999999556621)   # X, Y, Z de la FIN

# Si True, on serre PM à [0, L] (projection sur le SEGMENT). Si False, PM peut sortir de [0, L] (projection sur la DROITE).
CLAMP_PM_TO_SEGMENT = False

# Nom de la feuille qui décrit la ligne (option 2) :
LINE_SHEET_NAME = "LIGNE"
LINE_DEBUT_KEY = "DEBUT"
LINE_FIN_KEY   = "FIN"

# Colonnes attendues
COL_POINT = "POINT"
COL_X, COL_Y, COL_Z = "X", "Y", "Z"
COL_PM, COL_H, COL_V = "PM", "H", "V"

# =========================
# OUTILS GÉOMÉTRIQUES
# =========================
def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def mul_scalar(a, s):
    return (a[0]*s, a[1]*s, a[2]*s)

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def safe_unit(v, eps=1e-12):
    n = norm(v)
    if n < eps:
        return (0.0, 0.0, 0.0), 0.0
    return (v[0]/n, v[1]/n, v[2]/n), n

# Base orthonormée liée à la ligne:
#   u = direction unité de la ligne (DEBUT->FIN)
#   v_perp = composante de la verticale globale (0,0,1) orthogonale à u (si possible)
#   h_perp = u x v_perp (complète la base à droite)
# Si la ligne est verticale (u // (0,0,1)), alors v_perp = (0,0,0) et toute perpendiculaire est horizontale.
def line_local_basis(P0, P1, eps=1e-12):
    u_raw = sub(P1, P0)
    u, L = safe_unit(u_raw, eps)
    if L < eps:
        raise ValueError("Les points DEBUT et FIN de la ligne sont confondus.")
    k = (0.0, 0.0, 1.0)

    # composante verticale orthogonale à u
    k_proj_on_u = mul_scalar(u, dot(k, u))
    v_temp = sub(k, k_proj_on_u)
    v_perp, nv = safe_unit(v_temp, eps)

    if nv < eps:
        # Ligne quasi verticale: pas de composante 'verticale' perpendiculaire utile -> V=0, tout l'écart perpendiculaire est horizontal.
        # On construit malgré tout un h_perp stable:
        #   prendre un vecteur de référence non colinéaire à u, le projeter dans le plan normal à u, le normaliser.
        ref = (1.0, 0.0, 0.0)
        if norm(cross(u, ref)) < eps:
            ref = (0.0, 1.0, 0.0)
        ref_perp = sub(ref, mul_scalar(u, dot(ref, u)))  # projection de ref dans le plan normal
        h_perp, _ = safe_unit(ref_perp, eps)
        return u, (0.0, 0.0, 0.0), h_perp, L
    else:
        h_perp = cross(u, v_perp)
        h_perp, _ = safe_unit(h_perp, eps)
        return u, v_perp, h_perp, L

# Projection d'un point Q sur la DROITE définie par P0 + s*u (u unitaire)
# Retourne s (abscisse curviligne le long de la ligne), le pied F, et le vecteur perpendiculaire d = Q - F
def project_point_on_line(P0, u, Q):
    a = sub(Q, P0)
    s = dot(a, u)               # PM non bridé (peut être <0 ou >L)
    F = add(P0, mul_scalar(u, s))
    d = sub(Q, F)               # vecteur perpendiculaire à la ligne
    return s, F, d

# Décomposition de d dans la base (v_perp, h_perp) du plan normal
def decompose_perp(d, v_perp, h_perp):
    if v_perp == (0.0, 0.0, 0.0):
        # Ligne verticale: tout dans H, V=0
        return dot(d, h_perp), 0.0
    H = dot(d, h_perp)
    V = dot(d, v_perp)
    return H, V

# =========================
# LECTURE DE LA LIGNE
# =========================
def read_line_from_excel(xlsx_path):
    try:
        df_line = pd.read_excel(xlsx_path, sheet_name=LINE_SHEET_NAME)
    except Exception:
        return None  # pas de feuille LIGNE -> on utilisera LINE_START/LINE_END

    needed = {"NOM", "X", "Y", "Z"}
    if not needed.issubset({c.strip().upper() for c in df_line.columns}):
        return None

    # normaliser les noms de colonnes
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
# TRAITEMENT PRINCIPAL
# =========================
def main():
    xlsx_in = Path(INPUT_XLSX)
    if not xlsx_in.exists():
        print(f"Fichier introuvable: {xlsx_in}")
        sys.exit(1)

    # Ligne depuis la feuille 'LIGNE' si disponible, sinon paramètres en dur
    line = read_line_from_excel(xlsx_in)
    if line is not None:
        P0, P1 = line
    else:
        P0, P1 = LINE_START, LINE_END

    u, v_perp, h_perp, L = line_local_basis(P0, P1)

    # Lire la première feuille de données
    df = pd.read_excel(xlsx_in)
    # Colonnes minimales
    for c in [COL_POINT, COL_X, COL_Y, COL_Z]:
        if c not in df.columns:
            raise ValueError(f"Colonne manquante: {c}")

    PM_list, H_list, V_list = [], [], []

    for _, row in df.iterrows():
        try:
            Q = (float(row[COL_X]), float(row[COL_Y]), float(row[COL_Z]))
        except Exception:
            PM_list.append(None); H_list.append(None); V_list.append(None)
            continue

        s, F, d = project_point_on_line(P0, u, Q)

        # PM = s si on considère la droite infinie; sinon, brider à [0, L] pour le segment
        if CLAMP_PM_TO_SEGMENT:
            s_clamped = max(0.0, min(s, L))
            # Si bridé, recalculer d avec le nouveau pied
            if abs(s_clamped - s) > 1e-12:
                F = add(P0, mul_scalar(u, s_clamped))
                d = sub(Q, F)
            PM_val = s_clamped
        else:
            PM_val = s

        H_val, V_val = decompose_perp(d, v_perp, h_perp)

        PM_list.append(PM_val)
        H_list.append(H_val)
        V_list.append(V_val)

    # Écrire les colonnes demandées dans l'ordre souhaité
    df_out = df.copy()
    df_out[COL_PM] = PM_list
    df_out[COL_H]  = H_list
    df_out[COL_V]  = V_list

    # Assurer l'ordre POINT|X|Y|Z|PM|H|V si possible
    desired = [COL_POINT, COL_X, COL_Y, COL_Z, COL_PM, COL_H, COL_V]
    cols = [c for c in desired if c in df_out.columns] + [c for c in df_out.columns if c not in desired]
    df_out = df_out[cols]

    # Sauvegarde
    df_out.to_excel(OUTPUT_XLSX, index=False)
    print(f"OK. Résultats écrits dans: {OUTPUT_XLSX}")

if __name__ == "__main__":
    main()
