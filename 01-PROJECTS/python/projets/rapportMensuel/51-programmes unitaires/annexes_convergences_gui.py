#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script autonome (sans ligne de commande)
---------------------------------------
- Ouvre un sélecteur de fichier pour choisir `convergences_YYYY-MM.csv`
- Génère un fichier XLSX avec un onglet "Annexe"
- Mise en forme demandée :
    NOM DU FICHIER
    (ligne vide)
    CONVERGENCES PERIODIQUES
    [BG IG HG HD ID BD LH LI LB]
    [valeurs périodiques]
    (ligne vide)
    CONVERGENCES CUMULEE
    [BG IG HG HD ID BD LH LI LB]
    [valeurs cumulées]
    (2 lignes vides)
    → passe au fichier suivant
- Sauvegarde par défaut : <dossier_du_CSV>\_recaps\annexe_convergences.xlsx

Usage :
- Double-cliquez le fichier (si l'association .py est configurée) ou
- Clic droit → Ouvrir avec → Python
"""
from __future__ import annotations

import os
from pathlib import Path
import pandas as pd
from tkinter import Tk, filedialog, messagebox
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

POSITIONS = ["BG", "IG", "HG", "HD", "ID", "BD", "LH", "LI", "LB"]

# --- Helpers Excel ---

def _last_notna(series: pd.Series):
    s = series.dropna()
    return None if s.empty else s.iloc[-1]

def _pick_values_for_file(df_file: pd.DataFrame):
    periodic_vals, cumulative_vals = [], []
    for pos in POSITIONS:
        sub = df_file[df_file["metric"].astype(str).str.upper().str.strip() == pos]
        if sub.empty:
            periodic_vals.append("")
            cumulative_vals.append("")
            continue
        per = _last_notna(sub["periodic_mm"])  # NaN → vide
        cum = _last_notna(sub["cumulative_mm"])  # NaN → vide
        periodic_vals.append("" if pd.isna(per) else float(per))
        cumulative_vals.append("" if pd.isna(cum) else float(cum))
    return periodic_vals, cumulative_vals

def _autosize(ws) -> None:
    for col_idx in range(1, ws.max_column + 1):
        letter = get_column_letter(col_idx)
        max_len = 0
        for cell in ws[letter]:
            txt = "" if cell.value is None else str(cell.value)
            if len(txt) > max_len:
                max_len = len(txt)
        ws.column_dimensions[letter].width = min(max_len + 2, 40)


def _write_block(ws, filename: str, periodic: list, cumulative: list, start_row: int) -> int:
    bold = Font(bold=True)
    big  = Font(bold=True, size=12)
    title= Font(bold=True, size=14)
    center = Alignment(horizontal="center")
    r = start_row

    # Nom du fichier
    cell = ws.cell(row=r, column=1, value=filename)
    cell.font = title
    r += 2

    # CONVERGENCES PERIODIQUES
    ws.cell(row=r, column=1, value="CONVERGENCES PERIODIQUES").font = big
    r += 1
    # entêtes
    for j, h in enumerate(POSITIONS, start=1):
        c = ws.cell(row=r, column=j, value=h)
        c.font = bold
        c.alignment = center
    # valeurs périodiques
    for j, v in enumerate(periodic, start=1):
        c = ws.cell(row=r + 1, column=j, value=v)
        if isinstance(v, (int, float)):
            c.number_format = "0.00"
        c.alignment = center
    r += 3

    # CONVERGENCES CUMULEE
    ws.cell(row=r, column=1, value="CONVERGENCES CUMULEE").font = big
    r += 1
    for j, h in enumerate(POSITIONS, start=1):
        c = ws.cell(row=r, column=j, value=h)
        c.font = bold
        c.alignment = center
    for j, v in enumerate(cumulative, start=1):
        c = ws.cell(row=r + 1, column=j, value=v)
        if isinstance(v, (int, float)):
            c.number_format = "0.00"
        c.alignment = center
    r += 3
    return r

# --- Coeur ---

def build_annexe_from_csv(conv_csv: Path, out_xlsx: Path) -> Path:
    df = pd.read_csv(conv_csv, encoding="utf-8-sig")
    needed = {"source_file", "metric", "periodic_mm", "cumulative_mm"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {conv_csv}: {sorted(missing)}")

    wb = Workbook()
    ws = wb.active
    ws.title = "Annexe"

    row = 1
    # grouper par fichier (toutes feuilles confondues)
    for src, grp in df.groupby("source_file", sort=False):
        filename = os.path.basename(src)
        periodic_vals, cumulative_vals = _pick_values_for_file(grp)
        row = _write_block(ws, filename, periodic_vals, cumulative_vals, row)

    _autosize(ws)
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    return out_xlsx

# --- UI minimale ---

def main():
    root = Tk()
    root.withdraw()  # pas de fenêtre principale

    messagebox.showinfo("Annexe convergences", "Choisissez le fichier convergences_YYYY-MM.csv")
    path = filedialog.askopenfilename(
        title="Choisir convergences_YYYY-MM.csv",
        filetypes=[("CSV", "*.csv")]
    )
    if not path:
        return

    conv_csv = Path(path)
    out_xlsx = conv_csv.parent / "_recaps" / "annexe_convergences.xlsx"

    try:
        result = build_annexe_from_csv(conv_csv, out_xlsx)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de créer l'annexe:\n{e}")
        return

    messagebox.showinfo("OK", f"Annexe créée :\n{result}")
    try:
        os.startfile(str(result))  # ouvrir le fichier sous Windows
    except Exception:
        pass

if __name__ == "__main__":
    main()
