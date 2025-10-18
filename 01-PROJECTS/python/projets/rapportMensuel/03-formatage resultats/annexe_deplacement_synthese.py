#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script autonome (sans ligne de commande) — SYNTHÈSE DÉPLACEMENTS
----------------------------------------------------------------
- Ouvre un sélecteur de fichier pour choisir `deplacements_YYYY-MM.csv`
- Génère un fichier XLSX avec un onglet "Annexe Deplacements"
- Mise en forme par FICHIER (toutes feuilles confondues) :

    NOM DU FICHIER
    (ligne vide)
    DEPLACEMENTS PERIODIQUES
    [<mesure1> <mesure2> ...]  ← entêtes = intitulés EXACTS du CSV (measure_label)
    [valeurs périodiques]
    (ligne vide)
    DEPLACEMENTS CUMULES
    [<mesure1> <mesure2> ...]
    [valeurs cumulées]
    (2 lignes vides)
    → passe au fichier suivant

- Sauvegarde par défaut : <dossier_du_CSV>\_recaps\annexe_deplacements.xlsx

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

# --- Helpers ---

def _last_notna(series: pd.Series):
    s = series.dropna()
    return None if s.empty else s.iloc[-1]

def _ensure_measure_label(df: pd.DataFrame) -> pd.Series:
    """Retourne une série 'measure_label'. Si absente, la construit à partir de kind/position."""
    if "measure_label" in df.columns:
        return df["measure_label"].astype(str)
    # fallback : concat kind + position si dispo
    kind = df.get("kind", pd.Series([None]*len(df)))
    pos  = df.get("position", pd.Series([None]*len(df)))
    lab = kind.fillna("").astype(str).str.strip() + " " + pos.fillna("").astype(str).str.strip()
    lab = lab.str.strip()
    lab = lab.replace({"": None})
    return lab

def _collect_measures_in_order(df_file: pd.DataFrame) -> list[str]:
    labels = _ensure_measure_label(df_file)
    # S’il y a col_index → on ordonne d’abord par col_index, sinon on garde l’ordre d’apparition
    if "col_index" in df_file.columns:
        tmp = df_file[[labels.name, "col_index"]].copy()
        tmp.columns = ["measure_label", "col_index"]
        tmp = tmp.dropna(subset=["measure_label"]).sort_values("col_index", kind="stable")
        order = []
        seen = set()
        for _, row in tmp.iterrows():
            lab = str(row["measure_label"]).strip()
            if lab and lab not in seen:
                seen.add(lab)
                order.append(lab)
        return order
    # fallback : ordre d’apparition
    order, seen = [], set()
    for x in labels:
        if pd.isna(x): continue
        s = str(x).strip()
        if s and s not in seen:
            seen.add(s); order.append(s)
    return order


def _values_for_labels(df_file: pd.DataFrame, labels: list[str], value_col: str) -> list:
    vals = []
    labels_series = _ensure_measure_label(df_file)
    for lab in labels:
        sub = df_file[labels_series == lab]
        if sub.empty:
            vals.append("")
            continue
        v = _last_notna(sub[value_col]) if value_col in sub.columns else None
        if pd.isna(v) or v is None:
            vals.append("")
        else:
            try:
                vals.append(float(v))
            except Exception:
                vals.append(v)
    return vals

# --- Mise en forme Excel ---

def _autosize(ws) -> None:
    for col_idx in range(1, ws.max_column + 1):
        letter = get_column_letter(col_idx)
        max_len = 0
        for cell in ws[letter]:
            txt = "" if cell.value is None else str(cell.value)
            if len(txt) > max_len:
                max_len = len(txt)
        ws.column_dimensions[letter].width = min(max_len + 2, 50)


def _write_table(ws, start_row: int, title: str, headers: list[str], values: list):
    bold = Font(bold=True)
    big  = Font(bold=True, size=12)
    center = Alignment(horizontal="center")
    r = start_row

    # Titre
    c = ws.cell(row=r, column=1, value=title); c.font = big
    r += 1

    # En-têtes
    for j, h in enumerate(headers, start=1):
        cc = ws.cell(row=r, column=j, value=h)
        cc.font = bold
        cc.alignment = center

    # Valeurs
    for j, v in enumerate(values, start=1):
        cc = ws.cell(row=r + 1, column=j, value=v)
        if isinstance(v, (int, float)):
            cc.number_format = "0.00"
        cc.alignment = center

    return r + 3  # saute une ligne après le tableau

# --- Cœur ---

def build_annexe_from_csv(disp_csv: Path, out_xlsx: Path) -> Path:
    df = pd.read_csv(disp_csv, encoding="utf-8-sig")
    needed_any = {"source_file", "periodic_mm", "cumulative_mm"}
    if not needed_any.issubset(df.columns):
        raise ValueError(f"Colonnes manquantes dans {disp_csv}: il faut au minimum {sorted(needed_any)}")

    wb = Workbook()
    ws = wb.active
    ws.title = "Annexe Deplacements"

    row = 1
    # Grouper par fichier (toutes feuilles confondues)
    for src, grp in df.groupby("source_file", sort=False):
        filename = os.path.basename(src)

        # Collecter l'ordre des mesures (entêtes = libellés exacts du CSV)
        labels = _collect_measures_in_order(grp)
        if not labels:
            # rien à afficher pour ce fichier
            continue

        # Préparer les lignes périodique & cumulée
        periodic_vals  = _values_for_labels(grp, labels, "periodic_mm")
        cumulative_vals= _values_for_labels(grp, labels, "cumulative_mm")

        # Titre (nom de fichier)
        title_cell = ws.cell(row=row, column=1, value=filename)
        title_cell.font = Font(bold=True, size=14)
        row += 2

        # Tables
        row = _write_table(ws, row, "DEPLACEMENTS PERIODIQUES", labels, periodic_vals)
        row = _write_table(ws, row, "DEPLACEMENTS CUMULES",   labels, cumulative_vals)
        row += 2

    _autosize(ws)
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    return out_xlsx

# --- UI minimale ---

def main():
    root = Tk(); root.withdraw()
    messagebox.showinfo("Annexe déplacements (synthèse)", "Choisissez le fichier deplacements_YYYY-MM.csv")
    path = filedialog.askopenfilename(
        title="Choisir deplacements_YYYY-MM.csv",
        filetypes=[("CSV", "*.csv")]
    )
    if not path:
        return

    disp_csv = Path(path)
    out_xlsx = disp_csv.parent / "_recaps" / "annexe_deplacements.xlsx"

    try:
        result = build_annexe_from_csv(disp_csv, out_xlsx)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de créer l'annexe:\n{e}")
        return

    messagebox.showinfo("OK", f"Annexe créée :\n{result}")
    try:
        os.startfile(str(result))
    except Exception:
        pass

if __name__ == "__main__":
    main()
