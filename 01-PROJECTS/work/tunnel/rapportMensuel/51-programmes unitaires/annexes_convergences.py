#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
annexe_convergences.py — crée un XLSX d'annexe à partir de convergences_YYYY-MM.csv

Format demandé (pour chaque fichier, dans l'ordre découvert dans le CSV) :

NOM DU FICHIER

CONVERGENCES PERIODIQUES
[BG IG HG HD ID BD LH LI LB] (entêtes)
[valeurs périodiques dans cet ordre ; vide si manquant]

CONVERGENCES CUMULEE
[BG IG HG HD ID BD LH LI LB] (entêtes)
[valeurs cumulées dans cet ordre ; vide si manquant]

puis deux lignes vides et on passe au fichier suivant.

Par défaut, on agrège à l'échelle du fichier (toutes feuilles confondues) en
prenant la dernière valeur non nulle/non NaN par métrique.

Usage :
    python annexe_convergences.py \
        --csv "C:/temp/1-tableaux/convergences_2025-07.csv" \
        --out "C:/temp/1-tableaux/_recaps/annexe_convergences.xlsx"

Si --out est omis, le fichier sera écrit dans <dossier_csv>/_recaps/annexe_convergences.xlsx
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional, Iterable

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

POSITIONS = ["BG", "IG", "HG", "HD", "ID", "BD", "LH", "LI", "LB"]


def load_convergences(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    # Colonnes attendues : source_file, sheet, month, metric, periodic_mm, cumulative_mm, cumulative_outside_month
    needed = {"source_file", "metric", "periodic_mm", "cumulative_mm"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {csv_path}: {sorted(missing)}")
    df["metric"] = df["metric"].astype(str).str.strip().str.upper()
    return df


def last_notna(series: pd.Series):
    s = series.dropna()
    if s.empty:
        return None
    return s.iloc[-1]


def pick_values_for_file(df_file: pd.DataFrame) -> tuple[list, list]:
    """Retourne (periodic_list, cumulative_list) ordonnées selon POSITIONS.
    Agrégation sur toutes les feuilles : on prend la dernière valeur non-NaN pour chaque métrique.
    """
    periodic_vals = []
    cumulative_vals = []
    for pos in POSITIONS:
        sub = df_file[df_file["metric"] == pos]
        if sub.empty:
            periodic_vals.append("")
            cumulative_vals.append("")
            continue
        per = last_notna(sub["periodic_mm"])  # peut être NaN
        cum = last_notna(sub["cumulative_mm"])  # peut être NaN
        periodic_vals.append("" if pd.isna(per) else float(per))
        cumulative_vals.append("" if pd.isna(cum) else float(cum))
    return periodic_vals, cumulative_vals


def autosize(ws) -> None:
    for col_idx in range(1, ws.max_column + 1):
        letter = get_column_letter(col_idx)
        max_len = 0
        for cell in ws[letter]:
            val = "" if cell.value is None else str(cell.value)
            if len(val) > max_len:
                max_len = len(val)
        ws.column_dimensions[letter].width = min(max_len + 2, 40)


ess_bold = Font(bold=True)
head_bold = Font(bold=True, size=12)
file_bold = Font(bold=True, size=14)
center = Alignment(horizontal="center")


def write_block(ws, filename: str, periodic: list, cumulative: list, start_row: int) -> int:
    r = start_row
    # Nom de fichier
    ws.cell(row=r, column=1, value=filename).font = file_bold
    r += 2  # ligne vide

    # CONVERGENCES PERIODIQUES
    ws.cell(row=r, column=1, value="CONVERGENCES PERIODIQUES").font = head_bold
    r += 1
    # entêtes
    for j, h in enumerate(POSITIONS, start=1):
        c = ws.cell(row=r, column=j, value=h)
        c.font = ess_bold
        c.alignment = center
    # valeurs périodiques
    for j, v in enumerate(periodic, start=1):
        c = ws.cell(row=r + 1, column=j, value=v)
        if isinstance(v, (int, float)):
            c.number_format = "0.00"
        c.alignment = center
    r += 3  # saute une ligne après le tableau

    # CONVERGENCES CUMULEE
    ws.cell(row=r, column=1, value="CONVERGENCES CUMULEE").font = head_bold
    r += 1
    for j, h in enumerate(POSITIONS, start=1):
        c = ws.cell(row=r, column=j, value=h)
        c.font = ess_bold
        c.alignment = center
    for j, v in enumerate(cumulative, start=1):
        c = ws.cell(row=r + 1, column=j, value=v)
        if isinstance(v, (int, float)):
            c.number_format = "0.00"
        c.alignment = center
    r += 3
    return r


def build_annexe(conv_csv: Path, out_xlsx: Path) -> Path:
    df = load_convergences(conv_csv)
    # Regrouper par fichier uniquement (toutes feuilles confondues)
    groups = list(df.groupby("source_file", sort=False))

    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Annexe"

    row = 1
    for src, g in groups:
        filename = os.path.basename(src)
        periodic_vals, cumulative_vals = pick_values_for_file(g)
        row = write_block(ws, filename, periodic_vals, cumulative_vals, row)

    autosize(ws)
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_xlsx)
    return out_xlsx


def parse_args():
    ap = argparse.ArgumentParser(description="Annexe convergences → XLSX à partir du CSV")
    ap.add_argument("--csv", required=True, help="Chemin vers convergences_YYYY-MM.csv")
    ap.add_argument("--out", help="Chemin .xlsx de sortie (défaut: <dossier_csv>/_recaps/annexe_convergences.xlsx)")
    return ap.parse_args()


def main():
    args = parse_args()
    conv_csv = Path(args.csv)
    if not conv_csv.exists():
        raise FileNotFoundError(conv_csv)

    if args.out:
        out_xlsx = Path(args.out)
    else:
        out_xlsx = conv_csv.parent / "_recaps" / "annexe_convergences.xlsx"

    path = build_annexe(conv_csv, out_xlsx)
    print(f"[OK] Annexe écrite : {path}")


if __name__ == "__main__":
    main()
