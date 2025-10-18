#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMC_evolutions.py — v0.7 (convergences + déplacements)

Cette version réintègre la lecture **ultra‑linéaire** des *déplacements* dans le
script global, tout en conservant les convergences existantes.

Principes clés côté déplacements :
- Parcours **colonne par colonne** (ordre Excel garanti : B → dernière utile)
- Aucune réorganisation/tri a posteriori ; on **append** directement dans l'ordre lu
- Etiquettes : ligne 9 sinon ligne 8, sinon "COL_<Lettre>"
- Zone utile bornée par min( bord droit fusion couvrant A5 ; dernier header non vide ligne 9 )
  avec fallback via "Point bas droit" en ligne 8 si A5 non présent
- Colonnes ajoutées au CSV pour audit et ordre : `col_index`, `col_letter`

Pour limiter les régressions, un drapeau permet d'activer/désactiver
l'extraction *Convergences* par la voie "chemin court" (header=8) :
  CONVERGENCES_ENABLED = False  # ← mettre True quand vous voulez les reprendre
"""
from __future__ import annotations

import argparse
import sys
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

CONVERGENCES_ENABLED = True  # sécurité : éviter les régressions pendant qu'on fiabilise les déplacements

CONV_POSITIONS = ["BG", "HG", "HD", "BD", "LH", "LB"]
DATE_CANDIDATE_PATTERNS = [
    r"^\s*date\s*$",
    r"^\s*(date\s*/\s*jour)\s*$",
    r"^\s*(date\s*et\s*heure|datetime|horodat.*)\s*$",
    r"^\s*jour\s*$",
]
EU_MINUS = "−"  # signe moins unicode

# ------------------------------------------------------------------
# Utilitaires généraux
# ------------------------------------------------------------------

def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def is_smc_file(path: Path) -> bool:
    return path.suffix.lower() in {".xlsx", ".xlsm"} and ("smc" in path.name.lower())


def _norm(txt: str) -> str:
    if not isinstance(txt, str):
        return ""
    t = unicodedata.normalize("NFD", txt.upper())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")


def month_bounds(month_str: str) -> Tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.to_datetime(month_str + "-01", format="%Y-%m-%d")
    end = start + pd.offsets.MonthEnd(0)
    return start, end


def to_numeric_eu(series: pd.Series) -> pd.Series:
    s = series.astype(str)
    s = s.str.replace("mm", "", case=False, regex=False)
    s = s.str.replace(" ", "")
    s = s.str.replace("\u00A0", "")  # nbsp
    s = s.str.replace(EU_MINUS, "-")
    s = s.str.replace(",", ".")
    return pd.to_numeric(s, errors="coerce")


def to_float(val) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = (str(val)
         .replace("mm", "")
         .replace("\u00A0", "")
         .replace(" ", "")
         .replace("\u2212", "-")
         .replace(",", "."))
    try:
        return float(s)
    except Exception:
        return None


def find_date_column(df: pd.DataFrame) -> Optional[str]:
    # 1) dtype datetime
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            return c
    # 2) pattern de nom
    for c in df.columns:
        cn = str(c).strip().lower()
        for pat in DATE_CANDIDATE_PATTERNS:
            if re.match(pat, cn, flags=re.IGNORECASE):
                return c
    # 3) heuristique parseable
    for c in df.columns:
        try:
            parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
        except Exception:
            continue
        if parsed.notna().mean() >= 0.5:
            return c
    return None


def coerce_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=True)

# ------------------------------------------------------------------
# Déplacements — lecture ULTRA-LINÉAIRE (ordre Excel)
# ------------------------------------------------------------------

def _last_col_strict(ws) -> Optional[int]:
    """Dernière colonne utile = min(A5_merge_right, dernier header non vide ligne 9),
    fallback via "Point bas droit" en ligne 8 si A5 manquant."""
    last_col_A5 = None
    for rng in ws.merged_cells.ranges:
        if rng.min_row <= 5 <= rng.max_row and rng.min_col <= 1 <= rng.max_col:
            last_col_A5 = rng.max_col
            break
    last_col_hdr = None
    for c in range(ws.max_column, 1, -1):
        v = ws.cell(row=9, column=c).value
        if v not in (None, ""):
            last_col_hdr = c
            break
    if last_col_A5 is None:
        for cell in ws[8]:
            txt = _norm(cell.value) if cell.value else ""
            if "POINT BAS DROIT" in txt:
                mrg = None
                for r in ws.merged_cells.ranges:
                    if r.min_row <= 8 <= r.max_row and r.min_col <= cell.column <= r.max_col:
                        mrg = r
                        break
                last_col_A5 = (mrg.max_col if mrg else cell.column)
                break
    cands = [c for c in (last_col_A5, last_col_hdr) if c]
    return min(cands) if cands else None


def read_sheet_deplacements_linear(xl_path: Path, sheet_name: str, month_str: str) -> Tuple[List[Dict], List[Dict]]:
    """Lit l’onglet Déplacements colonne par colonne (ordre Excel garanti)."""
    start, end = month_bounds(month_str)

    wb = load_workbook(xl_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        return [], []
    ws = wb[sheet_name]

    last_col = _last_col_strict(ws)
    if not last_col or last_col < 2:
        return [], []

    rows_disp: List[Dict] = []
    month_dates: set = set()

    for col_idx in range(2, last_col + 1):  # B → dernière
        h9 = ws.cell(row=9, column=col_idx).value
        h8 = ws.cell(row=8, column=col_idx).value
        header = ("" if h9 is None else str(h9).strip()) or ("" if h8 is None else str(h8).strip()) or f"COL_{get_column_letter(col_idx)}"
        # vraie colonne Date → sauter si c'est B et intitulée Date
        if _norm(header) == "DATE" and col_idx == 2:
            continue

        pairs = []  # (date, valeur) dans l'ordre des lignes
        for r in range(10, ws.max_row + 1):
            raw_date = ws.cell(row=r, column=2).value  # B = Date
            if raw_date in (None, ""):
                continue
            try:
                d = pd.to_datetime(raw_date, errors="raise", dayfirst=True)
            except Exception:
                continue
            v = to_float(ws.cell(row=r, column=col_idx).value)
            if v is not None:
                pairs.append((d, v))

        s = pd.Series({d: v for d, v in pairs}).sort_index()
        if s.empty:
            periodic = None
            cumulative = None
            outside = None
        else:
            cumulative = float(s.iloc[-1])
            s_before = s[s.index < start]
            v_before = float(s_before.iloc[-1]) if not s_before.empty else None
            s_in = s[(s.index >= start) & (s.index <= end)]
            v_in = float(s_in.iloc[-1]) if not s_in.empty else None
            periodic = None if (v_before is None or v_in is None) else (v_in - v_before)
            last_date_any = s.index.max()
            outside = not (start <= last_date_any <= end)
            month_dates |= set(s_in.index.to_pydatetime())

        rows_disp.append({
            "source_file": str(xl_path),
            "sheet": sheet_name,
            "month": month_str,
            "measure_label": header,
            "col_index": col_idx,
            "col_letter": get_column_letter(col_idx),
            "periodic_mm": periodic,
            "cumulative_mm": cumulative,
            "cumulative_outside_month": outside,
        })

    rows_dates: List[Dict] = []
    if month_dates:
        rows_dates.append({
            "source_file": str(xl_path),
            "sheet": sheet_name,
            "month": month_str,
            "dates": ";".join(sorted({d.strftime("%Y-%m-%d") for d in month_dates})),
        })

    return rows_dates, rows_disp

# ------------------------------------------------------------------
# Convergences (inchangé)
# ------------------------------------------------------------------

def read_convergences_block(xl_path: Path, sheet_name: str) -> Optional[pd.DataFrame]:
    raw = pd.read_excel(xl_path, sheet_name=sheet_name, header=None, engine="openpyxl")
    if raw.empty:
        return None
    marker_rx = re.compile(r"convergences?\s*-\s*en\s*mm", re.IGNORECASE)
    header_row = None
    for r in range(min(60, len(raw))):
        for c in range(min(20, raw.shape[1])):
            val = raw.iat[r, c]
            if isinstance(val, str) and marker_rx.search(val.strip()):
                header_row = r + 1
                break
        if header_row is not None:
            break
    if header_row is None:
        return None

    df = pd.read_excel(xl_path, sheet_name=sheet_name, header=header_row, engine="openpyxl")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join([str(x) for x in tup if pd.notna(x)]).strip() for tup in df.columns]
    df.columns = [str(c).strip().upper() for c in df.columns]

    wanted = ["BG", "HG", "HD", "BD", "LH", "LB", "IG", "ID", "LI"]
    keep = [c for c in df.columns if c in wanted]

    date_series = None
    if raw.shape[1] >= 2:
        candidate = df.iloc[:, 0] if df.columns[0] not in keep else None
        if candidate is None and df.shape[1] >= 2:
            candidate = df.iloc[:, 1]
        if candidate is not None:
            parsed = pd.to_datetime(candidate, errors="coerce", dayfirst=True)
            if parsed.notna().mean() > 0.5:
                date_series = parsed
    if date_series is None:
        best_c = None
        best_ratio = 0
        for c in df.columns:
            try:
                parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
                ratio = parsed.notna().mean()
                if ratio > best_ratio:
                    best_ratio, best_c = ratio, c
                    date_series = parsed
            except Exception:
                pass
    if date_series is None:
        return None

    out = pd.DataFrame(index=date_series)
    for c in keep:
        out[c] = to_numeric_eu(df[c])
    out = out.loc[date_series.notna()].sort_index()
    out.index.name = "DATE"
    return out


def compute_convergences_from_fixed_header(xl_path: Path, sheet_name: str, month_str: str):
    start, end = month_bounds(month_str)
    df = pd.read_excel(xl_path, sheet_name=sheet_name, header=8, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    if "Date" not in df.columns:
        return [], []
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df = df[df["Date"].notna()].sort_values("Date").set_index("Date")

    positions = ["BG", "HG", "HD", "BD", "LH", "LB", "IG", "ID", "LI"]
    dates_in_month = df.loc[(df.index >= start) & (df.index <= end)].index
    rows_dates = [{
        "source_file": str(xl_path),
        "sheet": sheet_name,
        "month": month_str,
        "dates": ";".join(d.strftime("%Y-%m-%d") for d in dates_in_month),
    }]

    def to_num(s):
        s = (s.astype(str).str.replace("mm", "", case=False)
             .str.replace("\u00A0", "").str.replace(" ", "")
             .str.replace("\u2212", "-").str.replace(",", "."))
        return pd.to_numeric(s, errors="coerce")

    rows_conv = []
    for pos in positions:
        if pos not in df.columns:
            rows_conv.append({
                "source_file": str(xl_path), "sheet": sheet_name, "month": month_str,
                "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                "cumulative_outside_month": None,
            })
            continue
        s = to_num(df[pos]).dropna()
        if s.empty:
            rows_conv.append({
                "source_file": str(xl_path), "sheet": sheet_name, "month": month_str,
                "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                "cumulative_outside_month": None,
            })
            continue
        cumu = float(s.iloc[-1])
        s_before = s[s.index < start]
        s_in = s[(s.index >= start) & (s.index <= end)]
        v_before = float(s_before.iloc[-1]) if not s_before.empty else None
        v_in = float(s_in.iloc[-1]) if not s_in.empty else None
        periodic = None if (v_before is None or v_in is None) else (v_in - v_before)
        last_date_any = s.index.max()
        outside = not (start <= last_date_any <= end)
        rows_conv.append({
            "source_file": str(xl_path), "sheet": sheet_name, "month": month_str,
            "metric": pos, "periodic_mm": periodic, "cumulative_mm": cumu,
            "cumulative_outside_month": outside,
        })

    return rows_dates, rows_conv

# ------------------------------------------------------------------
# Fallback générique (gardé pour convergences uniquement)
# ------------------------------------------------------------------

def load_sheet_with_flexible_header(xl_path: Path, sheet_name: str) -> Optional[pd.DataFrame]:
    for header_row in range(0, 12):
        try:
            df = pd.read_excel(xl_path, sheet_name=sheet_name, header=header_row, engine="openpyxl")
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join([str(x) for x in tup if str(x) != "nan"]).strip() for x in df.columns]
            df = df.dropna(how="all")
            if df.shape[1] == 0:
                continue
            return df
        except Exception:
            continue
    return None


def compute_metrics_for_sheet(
    df: pd.DataFrame,
    file_path: Path,
    sheet_name: str,
    month_str: str,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Fallback : on ne calcule PLUS les déplacements ici (évite les doublons).
    On garde uniquement les convergences si le bloc explicite n'a pas été trouvé.
    """
    start, end = month_bounds(month_str)
    rows_dates: List[Dict] = []
    rows_conv: List[Dict] = []
    rows_disp: List[Dict] = []

    conv_block = read_convergences_block(file_path, sheet_name)
    if conv_block is not None and not conv_block.empty:
        dates_in_month = conv_block.loc[(conv_block.index >= start) & (conv_block.index <= end)].index
        rows_dates.append({
            "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
            "dates": ";".join(d.strftime("%Y-%m-%d") for d in dates_in_month),
        })
        for pos in ["BG", "HG", "HD", "BD", "LH", "LB"]:
            if pos not in conv_block.columns:
                rows_conv.append({
                    "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
                    "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                    "cumulative_outside_month": None,
                })
                continue
            s = conv_block[pos].dropna()
            if s.empty:
                rows_conv.append({
                    "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
                    "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                    "cumulative_outside_month": None,
                })
                continue
            v_any = float(s.iloc[-1])
            s_before = s[s.index < start]
            v_before = float(s_before.iloc[-1]) if not s_before.empty else None
            s_in = s[(s.index >= start) & (s.index <= end)]
            v_in = float(s_in.iloc[-1]) if not s_in.empty else None
            periodic = None if (v_before is None or v_in is None) else (v_in - v_before)
            last_date_any = s.index.max()
            cumulative_outside = not (start <= last_date_any <= end)
            rows_conv.append({
                "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
                "metric": pos, "periodic_mm": periodic, "cumulative_mm": v_any,
                "cumulative_outside_month": cumulative_outside,
            })
        return rows_dates, rows_conv, rows_disp

    # Fallback convergences générique
    date_col = find_date_column(df)
    if not date_col:
        return rows_dates, rows_conv, rows_disp
    df = df.copy()
    df[date_col] = coerce_datetime(df[date_col])
    df = df[df[date_col].notna()].sort_values(date_col)
    if df.empty:
        return rows_dates, rows_conv, rows_disp
    df = df.set_index(date_col)

    dates_in_month = df.loc[(df.index >= start) & (df.index <= end)].index
    rows_dates.append({
        "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
        "dates": ";".join(d.strftime("%Y-%m-%d") for d in dates_in_month),
    })

    for pos in ["BG", "HG", "HD", "BD", "LH", "LB"]:
        if pos not in df.columns:
            rows_conv.append({
                "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
                "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                "cumulative_outside_month": None,
            })
            continue
        s = to_numeric_eu(df[pos])
        if s.dropna().empty:
            rows_conv.append({
                "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
                "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                "cumulative_outside_month": None,
            })
            continue
        v_before = float(s[s.index < start].dropna().iloc[-1]) if not s[s.index < start].dropna().empty else None
        v_in = float(s[(s.index >= start) & (s.index <= end)].dropna().iloc[-1]) if not s[(s.index >= start) & (s.index <= end)].dropna().empty else None
        v_any = float(s.dropna().iloc[-1]) if not s.dropna().empty else None
        periodic = None if (v_before is None or v_in is None) else (v_in - v_before)
        last_date_any = s.dropna().index.max() if s.dropna().size else None
        cumulative_outside = ((last_date_any is not None) and not (start <= last_date_any <= end))
        rows_conv.append({
            "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
            "metric": pos, "periodic_mm": periodic, "cumulative_mm": v_any,
            "cumulative_outside_month": cumulative_outside,
        })

    return rows_dates, rows_conv, rows_disp

# ------------------------------------------------------------------
# Traitement d'un fichier Excel (intègre déplacements linéaires)
# ------------------------------------------------------------------

def process_excel_file(xl_path: Path, month_str: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    rows_dates_all: List[Dict] = []
    rows_conv_all: List[Dict] = []
    rows_disp_all: List[Dict] = []

    try:
        xls = pd.ExcelFile(xl_path, engine="openpyxl")
    except Exception:
        return [], [], []

    for sheet in xls.sheet_names:
        try:
            name_norm = _norm(sheet)

            # --- Convergences (chemin court header=8) ---
            if CONVERGENCES_ENABLED and ("CONVERG" in name_norm):
                r_dates, r_conv = compute_convergences_from_fixed_header(xl_path, sheet, month_str)
                rows_dates_all.extend(r_dates)
                rows_conv_all.extend(r_conv)

            # --- Déplacements (lecture ultra-linéaire : ordre Excel) ---
            if "DEPLAC" in name_norm:
                r_dates, r_disp = read_sheet_deplacements_linear(xl_path, sheet, month_str)
                rows_dates_all.extend(r_dates)
                rows_disp_all.extend(r_disp)

            # (Option) autre contenu : fallback convergences uniquement
            # else:
            #     df = load_sheet_with_flexible_header(xl_path, sheet)
            #     if df is not None and not df.empty:
            #         d, c, _ = compute_metrics_for_sheet(df, xl_path, sheet, month_str)
            #         rows_dates_all.extend(d)
            #         rows_conv_all.extend(c)

        except Exception:
            continue

    return rows_dates_all, rows_conv_all, rows_disp_all

# ------------------------------------------------------------------
# Scan dossier et CSV
# ------------------------------------------------------------------

def scan_and_process(root: Path, month_str: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows_dates: List[Dict] = []
    rows_conv: List[Dict] = []
    rows_disp: List[Dict] = []

    for p in root.rglob("*"):
        if p.is_file() and is_smc_file(p):
            d, c, z = process_excel_file(p, month_str)
            rows_dates.extend(d)
            rows_conv.extend(c)
            rows_disp.extend(z)

    df_dates = pd.DataFrame(rows_dates, columns=["source_file", "sheet", "month", "dates"])
    df_conv = pd.DataFrame(rows_conv, columns=[
        "source_file", "sheet", "month", "metric",
        "periodic_mm", "cumulative_mm", "cumulative_outside_month",
    ])
    df_disp = pd.DataFrame(rows_disp)  # on conserve toutes les colonnes utiles (measure_label, col_index, ...)

    # Ordonner optionnellement les déplacements par (source_file, sheet, col_index) sans re-trier globalement
    if not df_disp.empty and {"source_file", "sheet", "col_index"}.issubset(df_disp.columns):
        df_disp = df_disp.sort_values(["source_file", "sheet", "col_index"], kind="stable")

    return df_dates, df_conv, df_disp


def save_csvs(df_dates: pd.DataFrame, df_conv: pd.DataFrame, df_disp: pd.DataFrame, out_dir: Path, month_str: str) -> Tuple[Path, Path, Path]:
    safe_mkdir(out_dir)
    dates_path = out_dir / f"dates_mesures_{month_str}.csv"
    conv_path = out_dir / f"convergences_{month_str}.csv"
    disp_path = out_dir / f"deplacements_{month_str}.csv"

    df_dates.to_csv(dates_path, index=False, encoding="utf-8-sig")
    df_conv.to_csv(conv_path, index=False, encoding="utf-8-sig")
    df_disp.to_csv(disp_path, index=False, encoding="utf-8-sig")

    return dates_path, conv_path, disp_path

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Extraction SMC → CSV (dates, convergences, déplacements)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("--root", type=Path, help="Dossier racine à balayer")
    ap.add_argument("--month", type=str, help="Mois au format YYYY-MM (ex. 2025-07)")
    ap.add_argument("--out", type=Path, help="Dossier de sortie des CSV")
    return ap.parse_args(argv)


def prompt_interactive() -> Tuple[Path, str, Path]:
    print("Aucun argument détecté — passage en mode interactif.")
    root = Path(input("Dossier racine (--root): ").strip().strip('"'))
    month = input("Mois YYYY-MM (--month): ").strip()
    out = Path(input("Dossier sortie (--out): ").strip().strip('"'))
    return root, month, out


def validate_month(m: str) -> bool:
    try:
        _ = pd.to_datetime(m + "-01", errors="raise")
        return True
    except Exception:
        return False


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None and len(sys.argv) == 1:
        root, month, out = prompt_interactive()
        if not validate_month(month):
            print("[ERREUR] --month doit être au format YYYY-MM (ex. 2025-07)", file=sys.stderr)
            return 2
        df_dates, df_conv, df_disp = scan_and_process(root, month)
        save_csvs(df_dates, df_conv, df_disp, out, month)
        print("Terminé (mode interactif).")
        return 0

    args = parse_args(argv)
    if not (args.root and args.month and args.out):
        print("[ERREUR] Arguments requis manquants.", file=sys.stderr)
        print("  python SMC_evolutions.py --root \"D:/Mesures\" --month 2025-07 --out \"D:/Sorties\"", file=sys.stderr)
        return 2
    if not validate_month(args.month):
        print("[ERREUR] --month doit être au format YYYY-MM (ex. 2025-07)", file=sys.stderr)
        return 2

    df_dates, df_conv, df_disp = scan_and_process(args.root, args.month)
    save_csvs(df_dates, df_conv, df_disp, args.out, args.month)

    print("CSV produits pour", args.month)
    print(" - dates_mesures_{}.csv".format(args.month))
    print(" - convergences_{}.csv".format(args.month))
    print(" - deplacements_{}.csv".format(args.month))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
