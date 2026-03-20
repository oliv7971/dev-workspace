#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMC_evolutions.py — v0.6

Objectif
--------
Extraire automatiquement les données SMC (prioritaires mais pas exclusives),
calculer l'évolution PÉRIODIQUE et la CUMULÉE, puis produire 3 CSV :
  1) dates_mesures.csv   — liste des dates dans le mois demandé
  2) convergences.csv    — BG, HG, HD, BD, LH, LB (si présents)
  3) deplacements.csv    — (DPM|DH|DZ) × positions, via regex/mapping

Tolérance / robustesse
----------------------
- Ignore les fichiers non-SMC sans planter.
- Tolère variations d'onglets et de noms de colonnes (regex souples).
- Si une colonne est absente ou aucune mesure dans le mois : champs vides.
- CSV en UTF-8 avec BOM pour ouverture directe dans Excel.

Usage (CLI)
-----------
python SMC_evolutions.py \
  --root "C:/mesures" \
  --month 2025-07 \
  --out "C:/sorties"  # dossier de sortie (créé si absent)

Notes
-----
- Convergences attendues: BG, HG, HD, BD, LH, LB (casse/espaces tolérés)
- Déplacements : colonnes de type (DPM|DH|DZ) + position
  Exemple : "DPM_BG", "DH-BD", "Dz lh", etc.
- Date : détection heuristique (colonne datetime ou parsable)
"""

from __future__ import annotations

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from openpyxl import load_workbook
import unicodedata

import pandas as pd

# -------------------------------------------------------------
# Configuration / regex
# -------------------------------------------------------------

# Positions/abréviations de convergences (garder l'ordre stable)
CONV_POSITIONS = ["BG", "HG", "HD", "BD", "LH", "LB"]

# Regex souples pour repérer une colonne de date
DATE_CANDIDATE_PATTERNS = [
    r"^\s*date\s*$",
    r"^\s*(date\s*/\s*jour)\s*$",
    r"^\s*(date\s*et\s*heure|datetime|horodat.*)\s*$",
    r"^\s*jour\s*$",
]

# Regex pour extraire type de déplacement + position
# e.g. "DPM_BG", "DH-BD", "Dz lh", "dpm bg"
DISP_COL_REGEX = re.compile(
    r"\b(?P<kind>DPM|DH|DZ)\b[\s_\-]*\b(?P<pos>BG|HG|HD|BD|LH|LB)\b",
    re.IGNORECASE,
)

# Regex pour repérer convergences : BG, etc. (avec éventuels espaces)
CONV_COL_REGEXES: Dict[str, re.Pattern] = {
    pos: re.compile(rf"\b{pos}\b", re.IGNORECASE) for pos in CONV_POSITIONS
}

# Certains classeurs ont des lignes d'en-tête multiples : on essaie plusieurs lignes d'header
HEADER_ROW_CANDIDATES = list(range(0, 12))  # 0→4

# -------------------------------------------------------------
# Utilitaires
# -------------------------------------------------------------

def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def is_smc_file(path: Path) -> bool:
    """Retourne True si le nom de fichier contient 'SMC' (insensible à la casse)
    et que l'extension est .xlsx ou .xlsm.
    """
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        return False
    return "smc" in path.name.lower()


def find_date_column(df: pd.DataFrame) -> Optional[str]:
    """Heuristique pour détecter la colonne de date.
    1) colonnes de type datetime
    2) nom de colonne matchant les patterns
    3) première colonne parsable en dates avec >= 50% de valeurs parseables
    """
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
        series = df[c]
        try:
            parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)
        except Exception:
            continue
        ratio = parsed.notna().mean()
        if ratio >= 0.5:
            return c

    return None


def coerce_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def normalize_pos_token(token: str) -> Optional[str]:
    t = token.strip().upper()
    return t if t in CONV_POSITIONS else None

# --- NOUVEAU : conversion nombre FR → float ---
EU_MINUS = "−"  # signe moins unicode

def to_numeric_eu(series: pd.Series) -> pd.Series:
    """Convertit une série en float en tolérant les formats FR:
    - virgule décimale → point
    - espaces insécables / milliers → supprimés
    - unités (mm) supprimées
    - signe moins unicode normalisé
    """
    s = series.astype(str)
    s = s.str.replace("mm", "", case=False, regex=False)
    s = s.str.replace(" ", "")
    s = s.str.replace(" ", "")  # nbsp
    s = s.str.replace(EU_MINUS, "-")
    s = s.str.replace(",", ".")
    return pd.to_numeric(s, errors="coerce")


def month_bounds(month_str: str) -> Tuple[pd.Timestamp, pd.Timestamp]:
    # month_str = 'YYYY-MM'
    start = pd.to_datetime(month_str + "-01", format="%Y-%m-%d")
    end = (start + pd.offsets.MonthEnd(0))  # dernier jour du mois
    return start, end


def last_value_before(series: pd.Series, cutoff: pd.Timestamp) -> Optional[float]:
    # suppose un index datetime trié croissant
    s = series.dropna()
    s = s[s.index < cutoff]
    if s.empty:
        return None
    return float(s.iloc[-1])


def last_value_within(series: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> Optional[float]:
    s = series.dropna()
    s = s[(s.index >= start) & (s.index <= end)]
    if s.empty:
        return None
    return float(s.iloc[-1])


def last_value_any(series: pd.Series) -> Optional[float]:
    s = series.dropna()
    if s.empty:
        return None
    return float(s.iloc[-1])


# -------------------------------------------------------------
# Extraction par feuille
# -------------------------------------------------------------

def load_sheet_with_flexible_header(xl_path: Path, sheet_name: str) -> Optional[pd.DataFrame]:
    for header_row in HEADER_ROW_CANDIDATES:
        try:
            df = pd.read_excel(
                xl_path,
                sheet_name=sheet_name,
                header=header_row,
                engine="openpyxl",
            )
            # Drop colonnes totalement vides
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join([str(x) for x in tup if str(x) != "nan"]).strip() for tup in df.columns]
            df = df.dropna(how="all")
            if df.shape[1] == 0:
                continue
            return df
        except Exception:
            continue
    return None


def detect_metric_columns(df: pd.DataFrame) -> Tuple[Dict[str, str], Dict[Tuple[str, str], str]]:
    """Version adaptée :
    - Prend toutes les colonnes de convergences disponibles parmi BG, IG, HG, HD, ID, BD, LH, LI, LB.
    - Pour le CSV final, on filtrera si besoin, mais ici on garde tout ce qui existe pour ne rien perdre.
    - Cherche DH/DZ/DPM combiné avec toutes ces positions pour déplacements.
    """
    conv_cols: Dict[str, str] = {}
    disp_cols: Dict[Tuple[str, str], str] = {}

    all_positions = ["BG", "IG", "HG", "HD", "ID", "BD", "LH", "LI", "LB"]

    # Colonnes convergences
    for pos in all_positions:
        for col in df.columns:
            if str(col).strip().upper() == pos:
                conv_cols[pos] = col
                break

    # Déplacements : type + position dans le nom de colonne
    for col in df.columns:
        name_up = str(col).strip().upper()
        kind = None
        if "DPM" in name_up or " PM" in name_up:
            kind = "DPM"
        elif "DH" in name_up or "DX" in name_up or "HORIZ" in name_up:
            kind = "DH"
        elif "DZ" in name_up or "DV" in name_up or "VERT" in name_up:
            kind = "DZ"
        if kind:
            for pos in all_positions:
                if pos in name_up:
                    disp_cols[(kind, pos)] = col
                    break

    return conv_cols, disp_cols


def _norm(txt: str) -> str:
    if not isinstance(txt, str): return ""
    t = unicodedata.normalize("NFD", txt.upper())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")

def read_deplacements_block_strict(xl_path: Path, sheet_name: str, month_str: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Retourne (rows_dates, rows_disp) pour l'onglet Déplacements :
    - Dernière colonne = (1) bord droit de la fusion couvrant A5,
                         (2) sinon bord droit de la fusion en ligne 8 contenant 'POINT BAS DROIT',
                         (3) sinon dernière entête non vide ligne 9.
    - En-têtes = ligne 9 (conservés tels quels).
    - Date = colonne B ; données à partir de la ligne 10.
    """
    start, end = month_bounds(month_str)

    wb = load_workbook(xl_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        return [], []
    ws = wb[sheet_name]

    # 1) déterminer la dernière colonne utile
    last_col = None  # 1-based
    for rng in ws.merged_cells.ranges:
        if rng.min_row <= 5 <= rng.max_row and rng.min_col <= 1 <= rng.max_col:
            last_col = rng.max_col
            break
    if not last_col:
        for cell in ws[8]:
            val = _norm(cell.value) if cell.value is not None else ""
            if "POINT BAS DROIT" in val:
                merged_rng = None
                for rng in ws.merged_cells.ranges:
                    if rng.min_row <= 8 <= rng.max_row and rng.min_col <= cell.column <= rng.max_col:
                        merged_rng = rng
                        break
                last_col = (merged_rng.max_col if merged_rng else cell.column)
                break
    if not last_col:
        for c in range(ws.max_column, 1, -1):
            if ws.cell(row=9, column=c).value not in (None, ""):
                last_col = c
                break
    if not last_col or last_col < 2:
        return [], []

    # 2) entêtes ligne 9 (on garde tel quel)
    headers = [ws.cell(row=9, column=col).value for col in range(2, last_col + 1)]
    headers = [("" if h is None else str(h).strip()) for h in headers]

    # 3) balayer les données
    def to_float(v):
        if v is None: return None
        if isinstance(v, (int, float)): return float(v)
        s = str(v).replace("mm", "").replace("\u00A0", "").replace(" ", "").replace("\u2212", "-").replace(",", ".")
        try: return float(s)
        except Exception: return None

    series_map: Dict[str, List[Tuple[pd.Timestamp, Optional[float]]]] = {
        h: [] for h in headers if h and _norm(h) != "DATE"
    }

    for r in range(10, ws.max_row + 1):
        raw_date = ws.cell(row=r, column=2).value  # B = Date
        if raw_date in (None, ""):
            continue
        try:
            d = pd.to_datetime(raw_date, errors="raise", dayfirst=True)
        except Exception:
            continue
        for idx, h in enumerate(headers, start=2):
            if not h or _norm(h) == "DATE":
                continue
            v = to_float(ws.cell(row=r, column=idx).value)
            series_map[h].append((d, v))

    # 4) calculs + dates
    rows_disp: List[Dict] = []
    month_dates: set = set()

    for label, pairs in series_map.items():
        s = pd.Series({d: v for d, v in pairs if v is not None}).sort_index()
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
            "measure_label": label,  # libellé exact
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



def read_convergences_block(xl_path: Path, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    Ouvre la feuille brute (sans header), cherche la cellule contenant
    'Convergences - en mm' (casse/espaces tolérés), puis considère que
    la LIGNE SUIVANTE est la ligne d'entête: BG, IG, HG, HD, ID, BD, LH, LI, LB...
    On retourne un DataFrame avec un index DATETIME (colonne B) et les colonnes
    parmi {'BG','HG','HD','BD','LH','LB','IG','ID','LI'} si présentes.
    """
    # 1) lecture brute sans entête
    raw = pd.read_excel(xl_path, sheet_name=sheet_name, header=None, engine="openpyxl")
    if raw.empty:
        return None

    # 2) repérage de la cellule contenant 'Convergences - en mm'
    marker_rx = re.compile(r"convergences?\s*-\s*en\s*mm", re.IGNORECASE)
    header_row = None
    for r in range(min(60, len(raw))):  # on scanne les ~60 premières lignes
        for c in range(min(20, raw.shape[1])):  # et ~20 premières colonnes
            val = raw.iat[r, c]
            if isinstance(val, str) and marker_rx.search(val.strip()):
                header_row = r + 1  # ligne d'entête = ligne sous le titre
                break
        if header_row is not None:
            break
    if header_row is None:
        return None  # pas de bloc convergences dans cette feuille

    # 3) relire avec l'entête positionnée
    df = pd.read_excel(
        xl_path, sheet_name=sheet_name, header=header_row, engine="openpyxl"
    )

    # 4) normaliser les colonnes (supprimer MultiIndex, espaces, etc.)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            " ".join([str(x) for x in tup if pd.notna(x)]).strip() for tup in df.columns
        ]
    df.columns = [str(c).strip().upper() for c in df.columns]

    # 5) garder uniquement les colonnes utiles
    wanted = ["BG", "HG", "HD", "BD", "LH", "LB", "IG", "ID", "LI"]  # on tolère IG/ID/LI mais on ne les exportera pas
    keep = [c for c in df.columns if c in wanted]

    # 6) date = colonne B (index 1) dans ta maquette → on force une colonne DATETIME
    # Si la feuille a des colonnes en plus (A=vide, B=Date, etc.), on récupère la deuxième colonne non vide.
    # Fallback: heuristique "colonne la plus parseable"
    date_series = None
    # essaie la colonne d'index 1 si elle existe
    if raw.shape[1] >= 2:
        # la data commence 2 lignes sous le header (souvent une ligne vide juste après l'entête),
        # mais pd.read_excel(header=header_row) s’occupe déjà de l’offset → on prend telle quelle.
        candidate = df.iloc[:, 0] if df.columns[0] not in keep else None
        # si la 1ère colonne est déjà BG etc., la date est probablement la 2e colonne
        if candidate is None and df.shape[1] >= 2:
            candidate = df.iloc[:, 1]
        if candidate is not None:
            parsed = pd.to_datetime(candidate, errors="coerce", dayfirst=True)
            if parsed.notna().mean() > 0.5:
                date_series = parsed

    if date_series is None:
        # fallback: cherche la colonne la plus parsable
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

    # 7) construction DF final : index = date, colonnes utiles
    out = pd.DataFrame(index=date_series)
    for c in keep:
        out[c] = to_numeric_eu(df[c])  # conversion nombres FR → float
    out = out.loc[date_series.notna()].sort_index()
    out.index.name = "DATE"
    return out

def compute_convergences_from_fixed_header(xl_path: Path, sheet_name: str, month_str: str):
    """Lecture simple de la feuille Convergences: header à la ligne 9 (index 8)."""
    start, end = month_bounds(month_str)
    df = pd.read_excel(xl_path, sheet_name=sheet_name, header=8, engine="openpyxl")
    # normalisation
    df.columns = [str(c).strip() for c in df.columns]
    if "Date" not in df.columns:
        return [], []
    # index temps
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df = df[df["Date"].notna()].sort_values("Date").set_index("Date")

    # positions attendues
    positions = ["BG", "HG", "HD", "BD", "LH", "LB", "IG", "ID", "LI"]
    # dates du mois
    dates_in_month = df.loc[(df.index >= start) & (df.index <= end)].index
    rows_dates = [{
        "source_file": str(xl_path),
        "sheet": sheet_name,
        "month": month_str,
        "dates": ";".join(d.strftime("%Y-%m-%d") for d in dates_in_month),
    }]

    # conversions nombres (tolère virgules, 'mm', espaces)
    def to_num(s):
        s = s.astype(str).str.replace("mm","", case=False)\
                         .str.replace("\u00A0","").str.replace(" ","")\
                         .str.replace("\u2212","-").str.replace(",",".")
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

        # cumulée = dernière valeur dispo
        cumu = float(s.iloc[-1])
        # périodique = (dernier du mois) - (dernier avant le mois)
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

# -------------------------------------------------------------
# Calculs périodique / cumulée pour une feuille
# -------------------------------------------------------------

def compute_metrics_for_sheet(
    df: pd.DataFrame,
    file_path: Path,
    sheet_name: str,
    month_str: str,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    start, end = month_bounds(month_str)

    # Toujours initialiser les sorties
    rows_dates: List[Dict] = []
    rows_conv: List[Dict] = []
    rows_disp: List[Dict] = []

    # 1) Tentative: bloc explicite "Convergences - en mm"
    conv_block = read_convergences_block(file_path, sheet_name)
    if conv_block is not None and not conv_block.empty:
        # dates du mois
        dates_in_month = conv_block.loc[
            (conv_block.index >= start) & (conv_block.index <= end)
        ].index
        rows_dates.append({
            "source_file": str(file_path),
            "sheet": sheet_name,
            "month": month_str,
            "dates": ";".join(d.strftime("%Y-%m-%d") for d in dates_in_month),
        })
        # convergences pour BG/HG/HD/BD/LH/LB (IG/ID/LI ignorées)
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
        # on ne traite pas les déplacements ici → on renvoie déjà ce qu’on a
        return rows_dates, rows_conv, rows_disp

    # 2) Fallback générique (si pas de bloc convergences explicite)
    date_col = find_date_column(df)
    if not date_col:
        return rows_dates, rows_conv, rows_disp  # rien d’exploitable pour cette feuille

    df = df.copy()
    df[date_col] = coerce_datetime(df[date_col])
    df = df[df[date_col].notna()].sort_values(date_col)
    if df.empty:
        return rows_dates, rows_conv, rows_disp
    df = df.set_index(date_col)

    # dates dans le mois
    dates_in_month = df.loc[(df.index >= start) & (df.index <= end)].index
    rows_dates.append({
        "source_file": str(file_path),
        "sheet": sheet_name,
        "month": month_str,
        "dates": ";".join(d.strftime("%Y-%m-%d") for d in dates_in_month),
    })

    # colonnes dispo (convergences/déplacements) via detect_metric_columns
    conv_cols, disp_cols = detect_metric_columns(df)

    # convergences
    for pos in ["BG", "HG", "HD", "BD", "LH", "LB"]:
        col = conv_cols.get(pos)
        if not col:
            rows_conv.append({
                "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
                "metric": pos, "periodic_mm": None, "cumulative_mm": None,
                "cumulative_outside_month": None,
            })
            continue
        s = to_numeric_eu(df[col])
        v_before = last_value_before(s, start)
        v_in = last_value_within(s, start, end)
        v_any = last_value_any(s)
        periodic = None if (v_before is None or v_in is None) else (v_in - v_before)
        last_date_any = s.dropna().index.max() if s.dropna().size else None
        cumulative_outside = ((last_date_any is not None) and not (start <= last_date_any <= end))
        rows_conv.append({
            "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
            "metric": pos, "periodic_mm": periodic, "cumulative_mm": v_any,
            "cumulative_outside_month": cumulative_outside,
        })

    # déplacements (si détectés)
for (kind, pos), col in disp_cols.items():
    s = to_numeric_eu(df[col])
    v_before = last_value_before(s, start)
    v_in = last_value_within(s, start, end)
    v_any = last_value_any(s)
    periodic = None if (v_before is None or v_in is None) else (v_in - v_before)
    last_date_any = s.dropna().index.max() if s.dropna().size else None
    cumulative_outside = ((last_date_any is not None) and not (start <= last_date_any <= end))
    rows_disp.append({
        "source_file": str(file_path), "sheet": sheet_name, "month": month_str,
        "kind": kind, "position": pos,
        "measure_label": f"{kind} {pos}",   # 👈 ajouté
        "periodic_mm": periodic, "cumulative_mm": v_any,
        "cumulative_outside_month": cumulative_outside,
    })


    return rows_dates, rows_conv, rows_disp


# -------------------------------------------------------------
# Traitement d'un fichier Excel
# -------------------------------------------------------------

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

            # --- Convergences (chemin court fixe header=8) ---
            #if "CONVERG" in name_norm:
             #   r_dates, r_conv = compute_convergences_from_fixed_header(xl_path, sheet, month_str)
              #  rows_dates_all.extend(r_dates)
               # rows_conv_all.extend(r_conv)

            # --- Déplacements (lecture stricte avec A5 / 'Point bas droit') ---
            if "DEPLAC" in name_norm:
                r_dates, r_disp = read_deplacements_block_strict(xl_path, sheet, month_str)
                rows_dates_all.extend(r_dates)
                rows_disp_all.extend(r_disp)

            # (Option) Si tu veux garder un fallback générique pour autres feuilles, dé-commente :
            # else:
            #     df = load_sheet_with_flexible_header(xl_path, sheet)
            #     if df is None or df.empty:
            #         continue
            #     d, c, z = compute_metrics_for_sheet(df, xl_path, sheet, month_str)
            #     rows_dates_all.extend(d); rows_conv_all.extend(c); rows_disp_all.extend(z)

        except Exception:
            # Ne bloque pas tout le fichier si une feuille pose problème
            continue

    return rows_dates_all, rows_conv_all, rows_disp_all




# -------------------------------------------------------------
# Scan du dossier racine
# -------------------------------------------------------------

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
    #df_disp = pd.DataFrame(rows_disp, columns=[
    #    "source_file", "sheet", "month", "kind", "position",
    #    "periodic_mm", "cumulative_mm", "cumulative_outside_month",
    #])
    df_disp = pd.DataFrame(rows_disp)
    # Colonnes cibles dans l'ordre souhaité (prends ce qui existe)
    disp_cols_order = [
        "source_file", "sheet", "month",
        "measure_label",   # libellé exact si dispo
        "kind", "position",# optionnels ; présents si le fallback générique a été utilisé
        "periodic_mm", "cumulative_mm", "cumulative_outside_month",
    ]
    df_disp = df_disp[[c for c in disp_cols_order if c in df_disp.columns]]


    return df_dates, df_conv, df_disp


# -------------------------------------------------------------
# Sauvegarde CSV (UTF-8 SIG)
# -------------------------------------------------------------

def save_csvs(df_dates: pd.DataFrame, df_conv: pd.DataFrame, df_disp: pd.DataFrame, out_dir: Path, month_str: str) -> Tuple[Path, Path, Path]:
    safe_mkdir(out_dir)

    dates_path = out_dir / f"dates_mesures_{month_str}.csv"
    conv_path = out_dir / f"convergences_{month_str}.csv"
    disp_path = out_dir / f"deplacements_{month_str}.csv"

    df_dates.to_csv(dates_path, index=False, encoding="utf-8-sig")
    df_conv.to_csv(conv_path, index=False, encoding="utf-8-sig")
    df_disp.to_csv(disp_path, index=False, encoding="utf-8-sig")

    return dates_path, conv_path, disp_path


# -------------------------------------------------------------
# Main (CLI)
# -------------------------------------------------------------

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
    # Si lancé sans arguments (ex. depuis IDE), mode interactif
    if argv is None and len(sys.argv) == 1:
        root, month, out = prompt_interactive()
        if not validate_month(month):
            print("[ERREUR] --month doit être au format YYYY-MM (ex. 2025-07)", file=sys.stderr)
            return 2
        df_dates, df_conv, df_disp = scan_and_process(root, month)
        save_csvs(df_dates, df_conv, df_disp, out, month)
        print("Terminé (mode interactif).")
        return 0

    # Mode CLI
    args = parse_args(argv)

    # Aide si des arguments manquent
    if not (args.root and args.month and args.out):
        print("[ERREUR] Arguments requis manquants. Exemple d'usage:", file=sys.stderr)
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
