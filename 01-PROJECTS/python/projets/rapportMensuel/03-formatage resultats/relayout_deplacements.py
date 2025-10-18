#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relayout des déplacements (depuis "Annexe Deplacements")
-------------------------------------------------------
- Ouvre un sélecteur de fichier pour choisir `annexe_deplacements.xlsx`.
- Lit l'onglet "Annexe Deplacements" (tolérance casse/espaces).
- Recompose un onglet `presentation` avec :
    * titre = nom du fichier (lignes où la 1ʳᵉ cellule se termine par .xlsx/.xlsm)
    * sections "DEPLACEMENTS PERIODIQUES" puis "DEPLACEMENTS CUMULES"
    * regroupement par **triplets** (DPM, DH, DZ) **dans l'ordre** où ils apparaissent
    * affichage par **paires de points côte à côte** (3 colonnes + 1 vide),
      et **centrage** si un point reste seul (colonnes 3..5)
- Mise en forme :
    * Titres (nom de fichier + libellés de section) : alignement **gauche**, **vertical centré**, **pas de renvoi** de ligne, **fond jaune**.
    * Tableaux (entêtes + valeurs) : **wrap text** activé, centré H/V, police **Lucida Sans 9** (entêtes en gras),
      nombre au format **1 décimale**, **bordures fines**.
    * Hauteur des lignes : **25** pour entêtes/titres, **20** pour les lignes de **valeurs**.
    * Largeur des colonnes : **12** pour toutes les colonnes utilisées.
- Sauvegarde dans un **nouveau fichier** `*_relayout.xlsx` (l'original n'est pas modifié).

Usage : double‑cliquer le fichier, ou `python relayout_deplacements.py`.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox

from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# ---------------------- Mise en forme ----------------------
# Polices
TITLE_FONT       = Font(bold=True, size=14)
SECTION_FONT     = Font(bold=True, size=12)
TABLE_HDR_FONT   = Font(name="Lucida Sans", size=8.5, bold=True)
TABLE_VAL_FONT   = Font(name="Lucida Sans", size=8.5, bold=False)

# Alignements
TITLE_ALIGN      = Alignment(horizontal="left",  vertical="center", wrap_text=False)
SECTION_ALIGN    = Alignment(horizontal="left",  vertical="center", wrap_text=False)
TABLE_ALIGN      = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Bordures & remplissage
THIN             = Side(style="thin")
BOX              = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TITLE_FILL       = PatternFill(fill_type="solid", start_color="FFFF00", end_color="FFFF00")  # jaune

# Dimensions
ROW_H_TITLE      = 22
ROW_H_SECTION    = 22
ROW_H_VALUES     = 16
COL_WIDTH        = 11

# ---------------------- Helpers ----------------------------

def _is_filename(s: str) -> bool:
    s = s.strip().lower()
    return s.endswith((".xlsx", ".xlsm"))


def _find_source_sheet_name(wb) -> str:
    # Cherche "Annexe Deplacements" avec tolérance casse/espaces
    for n in wb.sheetnames:
        if n.strip().lower() == "annexe deplacements":
            return n
    # fallback : première feuille
    return wb.sheetnames[0]


def _read_block_headers_values(ws, title_row: int) -> Tuple[List[str], List[float]]:
    """Lit headers (ligne +1) et valeurs (ligne +2) jusqu'à la première cellule vide."""
    hdr_row = title_row + 1
    val_row = title_row + 2
    headers: List[str] = []
    values: List[float] = []
    col = 1
    while True:
        hv = ws.cell(row=hdr_row, column=col).value
        if hv is None:
            break
        headers.append(str(hv).strip())
        values.append(ws.cell(row=val_row, column=col).value)
        col += 1
    return headers, values


def _split_points_by_triplets(headers: List[str], values: List[float]):
    """Découpe en points (triplets DPM/DH/DZ) **sans interprétation**,
    strictement dans l'ordre d'apparition.
    Retourne une liste de paires (labels3, vals3).
    """
    points = []
    i = 0
    while i < len(headers):
        labels3 = headers[i:i+3]
        vals3   = values[i:i+3]
        if len(labels3) < 3:
            break
        points.append((labels3, vals3))
        i += 3
    return points


def _write_pair_row(ws_out, start_row: int, left_triplet, right_triplet=None) -> int:
    """Écrit une rangée :
       - deux blocs côte à côte (3 colonnes chacun, 1 colonne vide entre)
       - ou un bloc **centré** si `right_triplet` est None (colonnes 3..5)
    Retourne la prochaine ligne d'écriture.
    """
    r = start_row
    left_c   = 1
    right_c  = 5   # 1..3 + 1 vide => 5..7
    center_c = 3   # colonnes 3..5

    def write_block(c0, labels3, vals3):
        # en‑têtes
        for j, lbl in enumerate(labels3):
            cell = ws_out.cell(row=r, column=c0 + j, value=lbl)
            cell.font = TABLE_HDR_FONT
            cell.alignment = TABLE_ALIGN
            cell.border = BOX
        # valeurs
        for j, v in enumerate(vals3):
            cell = ws_out.cell(row=r+1, column=c0 + j, value=v)
            cell.font = TABLE_VAL_FONT
            cell.alignment = TABLE_ALIGN
            cell.border = BOX
            if isinstance(v, (int, float)):
                cell.number_format = "0.0"

        # Hauteurs de lignes : en‑têtes 25, valeurs 20
        ws_out.row_dimensions[r].height = ROW_H_SECTION  # 25 pour ligne d'entêtes de bloc
        ws_out.row_dimensions[r+1].height = ROW_H_VALUES # 20 pour ligne de valeurs

    if right_triplet is None:
        write_block(center_c, *left_triplet)
    else:
        write_block(left_c,  *left_triplet)
        write_block(right_c, *right_triplet)

    return r + 3  # laisse une ligne vide après

# ---------------------- Cœur -------------------------------

def relayout_file(xlsx_path: Path) -> Path:
    wb = load_workbook(xlsx_path, data_only=True)
    src_name = _find_source_sheet_name(wb)
    ws = wb[src_name]

    # (Re)créer la feuille de sortie
    if "presentation" in wb.sheetnames:
        del wb["presentation"]
    ws_out = wb.create_sheet("presentation")

    row_out = 1
    r = 1
    max_used_col = 0
    while r <= ws.max_row:
        v = ws.cell(row=r, column=1).value
        if isinstance(v, str) and v.strip():
            txt = v.strip()
            up  = txt.upper()

            # Nom de fichier (titre)
            if _is_filename(txt):
                tcell = ws_out.cell(row=row_out, column=1, value=txt)
                tcell.font = TITLE_FONT
                tcell.alignment = TITLE_ALIGN
                tcell.border = BOX
                tcell.fill = TITLE_FILL
                ws_out.row_dimensions[row_out].height = ROW_H_TITLE
                max_used_col = max(max_used_col, 1)
                row_out += 2

            # Début de section (périodiques / cumulées)
            elif ("DEPLACEMENTS" in up) and ("PERIOD" in up or "CUMUL" in up):
                headers, values = _read_block_headers_values(ws, r)
                points = _split_points_by_triplets(headers, values)

                label = "DEPLACEMENTS PERIODIQUES" if "PERIOD" in up else "DEPLACEMENTS CUMULES"
                sec = ws_out.cell(row=row_out, column=1, value=label)
                sec.font = SECTION_FONT
                sec.alignment = SECTION_ALIGN
                sec.border = BOX
                sec.fill = TITLE_FILL
                ws_out.row_dimensions[row_out].height = ROW_H_SECTION
                max_used_col = max(max_used_col, 1)
                row_out += 1

                i = 0
                while i < len(points):
                    left  = points[i]
                    right = points[i+1] if i+1 < len(points) else None
                    row_out = _write_pair_row(ws_out, row_out, left, right)
                    max_used_col = max(max_used_col, 7)  # jusqu'à la colonne 7 lorsque 2 blocs
                    i += 2

                row_out += 1  # espace après section
                r += 2        # sauter headers + valeurs
        r += 1

    # Largeur de colonnes fixe = 12, et wrap/centrage déjà géré au moment de l'écriture
    if max_used_col == 0:
        max_used_col = ws_out.max_column
    for cc in range(1, max_used_col + 1):
        ws_out.column_dimensions[get_column_letter(cc)].width = COL_WIDTH

    out_path = xlsx_path.with_name(xlsx_path.stem + "_relayout.xlsx")
    wb.save(out_path)
    return out_path

# ---------------------- UI --------------------------------

def main():
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo("Relayout déplacements", "Choisissez le fichier annexe_deplacements.xlsx")
    path = filedialog.askopenfilename(title="Choisir annexe_deplacements.xlsx", filetypes=[["Excel","*.xlsx"]])
    if not path:
        return

    src = Path(path)
    try:
        result = relayout_file(src)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de créer la présentation :{e}")
        return

    messagebox.showinfo("OK", f"Fichier créé :{result}")

if __name__ == "__main__":
    main()
