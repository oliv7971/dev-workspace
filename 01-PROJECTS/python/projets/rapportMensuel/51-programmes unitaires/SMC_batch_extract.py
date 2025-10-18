# smc_batch_extract.py
# -*- coding: utf-8 -*-
"""
Extraction SMC tout-en-un :
- Scan récursif d'un dossier racine
- Filtre par mois (AAAA-MM) sur la date de modification de fichier (optionnel)
- Lecture tolérante des onglets Convergences / Déplacements
- Calcul des valeurs périodiques (dernière du mois - précédente) et cumulées (dernière du mois - première du fichier)
- Exporte 3 CSV : dates, convergences, déplacements

Dépendances : pandas, openpyxl
pip install pandas openpyxl
"""

from __future__ import annotations
import argparse, os, sys, re, json, datetime as dt
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd

# ---------------- Windows long paths (si besoin) ----------------
def win_longpath(p: Path) -> str:
    s = str(p)
    if os.name == "nt":
        s = s.replace("/", "\\")
        if not s.startswith("\\\\?\\"):
            s = "\\\\?\\" + s
    return s

# ---------------- utilitaires date/mois ----------------
def parse_year_month(s: Optional[str]) -> Optional[Tuple[int,int]]:
    if not s:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})", s.strip())
    if not m:
        raise ValueError("Format mois attendu : AAAA-MM")
    y, mm = int(m.group(1)), int(m.group(2))
    if not (1 <= mm <= 12):
        raise ValueError("Mois invalide")
    return y, mm

def in_target_month(d: dt.date, ym: Optional[Tuple[int,int]]) -> bool:
    if ym is None:
        return True
    y, m = ym
    return (d.year == y and d.month == m)

def month_bounds(y: int, m: int) -> Tuple[dt.datetime, dt.datetime]:
    start = dt.datetime(y, m, 1)
    if m == 12:
        end = dt.datetime(y+1, 1, 1) - dt.timedelta(seconds=1)
    else:
        end = dt.datetime(y, m+1, 1) - dt.timedelta(seconds=1)
    return start, end

# ---------------- détection d’onglets ----------------
SHEET_CANDS_CONV = [
    r"^convergences?$", r"^convergence$", r"^smc.*conv", r"^conv.*",
    r".*convergen.*",
]
SHEET_CANDS_DEPL = [
    r"^deplacements?$", r"^déplacements?$", r"^depl.*", r".*deplac.*"
]

def match_any(name: str, patterns: List[str]) -> bool:
    n = name.strip().lower()
    for p in patterns:
        if re.match(p, n, re.IGNORECASE):
            return True
    return False

# ---------------- colonnes attendues ----------------
# Convergences : cordes 3D (selon tes docs)
CONV_KEYS = ["BG","HG","HD","BD","LH","LB"]  # parfois certaines manquent, on prend ce qui existe

# Déplacements : groupes (DPM, DH, DZ) x cibles (bas/inter/haut/voute/centre) x (gauche/droit)
# On va tolérer pas mal de variantes, et mapper vers des alias canonique :
# Exemple d’en-têtes possibles -> canonique
DEPL_ALIAS = {
    # Bas gauche
    r"^dpm.*bas.*gauche$": "DPM_BG", r"^dh.*bas.*gauche$": "DH_BG", r"^dz.*bas.*gauche$": "DZ_BG",
    # Haut gauche
    r"^dpm.*haut.*gauche$": "DPM_HG", r"^dh.*haut.*gauche$": "DH_HG", r"^dz.*haut.*gauche$": "DZ_HG",
    # Centre haut
    r"^dpm.*centre.*haut$": "DPM_CH", r"^dh.*centre.*haut$": "DH_CH", r"^dz.*centre.*haut$": "DZ_CH",
    # Haut droit
    r"^dpm.*haut.*droit$": "DPM_HD", r"^dh.*haut.*droit$": "DH_HD", r"^dz.*haut.*droit$": "DZ_HD",
    # Bas droit
    r"^dpm.*bas.*droit$": "DPM_BD", r"^dh.*bas.*droit$": "DH_BD", r"^dz.*bas.*droit$": "DZ_BD",
    # Inter gauche/droit
    r"^dpm.*inter.*gauche$": "DPM_IG", r"^dh.*inter.*gauche$": "DH_IG", r"^dz.*inter.*gauche$": "DZ_IG",
    r"^dpm.*inter.*droit$": "DPM_ID", r"^dh.*inter.*droit$": "DH_ID", r"^dz.*inter.*droit$": "DZ_ID",
    # Voûte gauche/droite (quand présentes)
    r"^dpm.*voute.*gauche$": "DPM_VG", r"^dh.*voute.*gauche$": "DH_VG", r"^dz.*voute.*gauche$": "DZ_VG",
    r"^dpm.*voute.*droit$": "DPM_VD", r"^dh.*voute.*droit$": "DH_VD", r"^dz.*voute.*droit$": "DZ_VD",
}

DATE_COL_CANDS = [
    r"^date", r"^jour", r"^mesure", r"^mesures", r"^timestamp", r"^time"
]

def find_date_column(cols: List[str]) -> Optional[str]:
    lc = [c.strip().lower() for c in cols]
    for i, c in enumerate(lc):
        for p in DATE_COL_CANDS:
            if re.match(p, c):
                return cols[i]
    # fallback : 1ʳᵉ colonne si convertible en dates
    return cols[0] if cols else None

def normalize_depl_columns(cols: List[str]) -> Dict[str, str]:
    """
    Retourne un mapping {col_source: alias_canonique} pour les colonnes déplacements reconnues.
    """
    mapping = {}
    for c in cols:
        key = c.strip().lower()
        key = key.replace("é","e").replace("è","e").replace("ô","o").replace("à","a").replace("ù","u")
        key = re.sub(r"\s+", " ", key)
        for rx, alias in DEPL_ALIAS.items():
            if re.match(rx, key):
                mapping[c] = alias
                break
    return mapping

# ---------------- chargement d’un onglet en DataFrame propre ----------------
def read_sheet(path: Path, sheet_name: str) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_excel(win_longpath(path), sheet_name=sheet_name, engine="openpyxl")
    except Exception:
        return None
    # Nettoyage simple : drop colonnes vides doubles, trim headers
    df.columns = [str(c).strip() for c in df.columns]
    # Supprimer les lignes totalement vides
    if not df.empty:
        df = df.dropna(how="all")
    return df if df is not None and not df.empty else None

def find_candidate_sheet_name(xl: pd.ExcelFile, patterns: List[str]) -> Optional[str]:
    for s in xl.sheet_names:
        if match_any(s, patterns):
            return s
    return None

# ---------------- extraction des dates + indices ----------------
def extract_date_series(df: pd.DataFrame) -> Tuple[Optional[str], pd.Series]:
    if df is None or df.empty:
        return None, pd.Series(dtype="datetime64[ns]")
    date_col = find_date_column(list(df.columns))
    if not date_col or date_col not in df.columns:
        # essaie de convertir 1ʳᵉ colonne
        date_col = df.columns[0]
    series = pd.to_datetime(df[date_col], errors="coerce")
    return date_col, series

def pick_prev_and_last_idx(dates: pd.Series, ym: Tuple[int,int]) -> Tuple[Optional[int], Optional[int], List[dt.date]]:
    """
    Renvoie (idx_prev, idx_last, dates_du_mois)
    - idx_last : index de la dernière mesure dans le mois cible
    - idx_prev : index de la mesure précédente (tous mois confondus)
    """
    if dates is None or dates.empty:
        return None, None, []
    y, m = ym
    # indices valides (datés)
    ok = dates.dropna()
    if ok.empty:
        return None, None, []
    # lignes dans le mois
    inmo = ok[(ok.dt.year == y) & (ok.dt.month == m)]
    if inmo.empty:
        return None, None, []
    idx_last = inmo.index.max()
    # précédente = plus grand index < idx_last avec date non nulle
    prev = ok[ok.index < idx_last]
    idx_prev = prev.index.max() if not prev.empty else None
    # toutes les dates dans le mois (pour ta phrase)
    list_inmo = [d.date() for d in inmo.sort_index().tolist()]
    return idx_prev, idx_last, list_inmo

# ---------------- extraction Convergences ----------------
def extract_convergences(df: pd.DataFrame, ym: Tuple[int,int]) -> Tuple[Optional[Dict], Optional[Dict], List[dt.date]]:
    """
    Retourne (periodique, cumulee, dates_du_mois) sous forme de dict {clé: valeur}
    Clés possibles : BG, HG, HD, BD, LH, LB (on prend celles présentes).
    """
    if df is None or df.empty:
        return None, None, []
    date_col, dates = extract_date_series(df)
    if dates is None or dates.empty:
        return None, None, []

    idx_prev, idx_last, dates_in_month = pick_prev_and_last_idx(dates, ym)
    if idx_last is None:
        return None, None, []

    # colonnes utilisables = intersection CONV_KEYS et colonnes du DF
    avail = [k for k in CONV_KEYS if k in df.columns]
    if not avail:
        # parfois en majuscules/minuscules
        # tente un mapping tolerant (ex: 'Lb ' -> 'LB')
        canon = {}
        for c in df.columns:
            uc = str(c).strip().upper()
            if uc in CONV_KEYS:
                canon[c] = uc
        if not canon:
            return None, None, dates_in_month
        # renomme localement
        df = df.rename(columns=canon)
        avail = [k for k in CONV_KEYS if k in df.columns]

    # valeurs au dernier index
    last_vals = df.loc[idx_last, avail]
    # cumulée = last - first non nulle
    first_idx = dates.dropna().index.min()
    first_vals = df.loc[first_idx, avail]
    cum = {}
    for k in avail:
        try:
            cum[k] = float(last_vals[k]) - float(first_vals[k])
        except Exception:
            cum[k] = None

    # périodique = last - prev (s’il existe)
    per = {}
    if idx_prev is not None:
        prev_vals = df.loc[idx_prev, avail]
        for k in avail:
            try:
                per[k] = float(last_vals[k]) - float(prev_vals[k])
            except Exception:
                per[k] = None
    else:
        for k in avail:
            per[k] = None

    return per, cum, dates_in_month

# ---------------- extraction Déplacements ----------------
def extract_deplacements(df: pd.DataFrame, ym: Tuple[int,int]) -> Tuple[Optional[Dict], Optional[Dict], List[dt.date]]:
    """
    Retourne (periodique, cumulee, dates_du_mois) sous forme dict {alias: valeur}
      alias ∈ DEPL_ALIAS (ex: DPM_BG, DH_BG, DZ_BG, …)
    """
    if df is None or df.empty:
        return None, None, []
    date_col, dates = extract_date_series(df)
    if dates is None or dates.empty:
        return None, None, []

    idx_prev, idx_last, dates_in_month = pick_prev_and_last_idx(dates, ym)
    if idx_last is None:
        return None, None, []

    mapping = normalize_depl_columns(list(df.columns))
    if not mapping:
        return None, None, dates_in_month

    # on garde seulement les colonnes déplacements reconnues
    keep_cols = list(mapping.keys())
    sub = df[keep_cols].copy()

    # cumulée : last - first
    first_idx = dates.dropna().index.min()
    per, cum = {}, {}

    for src_col, alias in mapping.items():
        try:
            last_val = float(sub.loc[idx_last, src_col])
        except Exception:
            last_val = None
        try:
            first_val = float(sub.loc[first_idx, src_col])
        except Exception:
            first_val = None
        cum[alias] = (last_val - first_val) if (last_val is not None and first_val is not None) else None

        if idx_prev is not None:
            try:
                prev_val = float(sub.loc[idx_prev, src_col])
            except Exception:
                prev_val = None
            per[alias] = (last_val - prev_val) if (last_val is not None and prev_val is not None) else None
        else:
            per[alias] = None

    return per, cum, dates_in_month

# ---------------- pipeline fichier ----------------
def process_file(path: Path, ym: Optional[Tuple[int,int]]) -> Dict:
    out = {
        "file": str(path),
        "dates_in_month": [],
        "conv_periodique": None,
        "conv_cumulee": None,
        "depl_periodique": None,
        "depl_cumulee": None,
    }
    try:
        xl = pd.ExcelFile(win_longpath(path), engine="openpyxl")
    except Exception:
        return out

    # on fixe un mois par défaut : si pas filtrage demandé, on prend le mois du dernier enregistrement
    target_ym = ym

    # ----- Convergences -----
    s_conv = find_candidate_sheet_name(xl, SHEET_CANDS_CONV)
    if s_conv:
        df = read_sheet(path, s_conv)
        if df is not None and not df.empty:
            # si pas de mois passé, derive du dernier enregistrement
            if target_ym is None:
                _, dates = extract_date_series(df)
                if dates is not None and not dates.dropna().empty:
                    last = pd.to_datetime(dates.dropna().iloc[-1]).date()
                    target_ym = (last.year, last.month)
            if target_ym:
                per, cum, dates_inmo = extract_convergences(df, target_ym)
                if dates_inmo:
                    out["dates_in_month"] = sorted(set(out["dates_in_month"] + dates_inmo))
                if per:
                    out["conv_periodique"] = per
                if cum:
                    out["conv_cumulee"] = cum

    # ----- Déplacements -----
    s_depl = find_candidate_sheet_name(xl, SHEET_CANDS_DEPL)
    if s_depl:
        df = read_sheet(path, s_depl)
        if df is not None and not df.empty:
            # si pas de mois passé, derive du dernier enregistrement
            if target_ym is None:
                _, dates = extract_date_series(df)
                if dates is not None and not dates.dropna().empty:
                    last = pd.to_datetime(dates.dropna().iloc[-1]).date()
                    target_ym = (last.year, last.month)
            if target_ym:
                per, cum, dates_inmo = extract_deplacements(df, target_ym)
                if dates_inmo:
                    out["dates_in_month"] = sorted(set(out["dates_in_month"] + dates_inmo))
                if per:
                    out["depl_periodique"] = per
                if cum:
                    out["depl_cumulee"] = cum

    return out

# ---------------- parcours répertoires ----------------
DEF_EXTS = {".xlsx", ".xlsm"}

def iter_files(roots: List[Path], ym: Optional[Tuple[int,int]]) -> List[Path]:
    files = []
    for r in roots:
        if not r.exists():
            continue
        for p in r.rglob("*"):
            if p.suffix.lower() in DEF_EXTS and p.is_file():
                if ym:
                    # filtre par mois de modification du fichier
                    y, m = ym
                    mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
                    if mtime.year == y and mtime.month == m:
                        files.append(p)
                else:
                    files.append(p)
    return files

# ---------------- export CSV ----------------
def write_csv_dates(rows: List[Dict], out_dir: Path, y_m: Optional[str]):
    tag = (y_m or "ALL").replace("-", "")
    out = out_dir / f"export_dates_{tag}.csv"
    data = []
    for r in rows:
        data.append({
            "file": r["file"],
            "dates_in_month": ", ".join(sorted({d.strftime("%Y-%m-%d") for d in r.get("dates_in_month", [])}))
        })
    pd.DataFrame(data).to_csv(out, index=False, encoding="utf-8-sig")
    return out

def flat_dict(prefix: str, d: Optional[Dict]) -> Dict:
    if not d:
        return {}
    return {f"{prefix}{k}": v for k, v in d.items()}

def write_csv_convergences(rows: List[Dict], out_dir: Path, y_m: Optional[str]):
    tag = (y_m or "ALL").replace("-", "")
    out = out_dir / f"export_convergences_{tag}.csv"
    data = []
    for r in rows:
        row = {"file": r["file"]}
        row.update(flat_dict("per_", r.get("conv_periodique")))
        row.update(flat_dict("cum_", r.get("conv_cumulee")))
        data.append(row)
    pd.DataFrame(data).to_csv(out, index=False, encoding="utf-8-sig")
    return out

def write_csv_deplacements(rows: List[Dict], out_dir: Path, y_m: Optional[str]):
    tag = (y_m or "ALL").replace("-", "")
    out = out_dir / f"export_deplacements_{tag}.csv"
    data = []
    for r in rows:
        row = {"file": r["file"]}
        row.update(flat_dict("per_", r.get("depl_periodique")))
        row.update(flat_dict("cum_", r.get("depl_cumulee")))
        data.append(row)
    pd.DataFrame(data).to_csv(out, index=False, encoding="utf-8-sig")
    return out

# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser(description="Extraction SMC tout-en-un")
    ap.add_argument("--roots", nargs="+", required=True, help="Dossier(s) racine à scanner")
    ap.add_argument("--modified-month", default=None, help="Filtre AAAA-MM sur la date de modification des fichiers")
    ap.add_argument("--out", default=None, help="Dossier de sortie (par défaut = 1er root)")
    args = ap.parse_args()

    roots = [Path(r) for r in args.roots]
    ym = parse_year_month(args.modified_month) if args.modified_month else None
    out_dir = Path(args.out) if args.out else roots[0]
    out_dir.mkdir(parents=True, exist_ok=True)

    files = iter_files(roots, ym)
    print(f"Fichiers détectés : {len(files)}")

    rows: List[Dict] = []
    for i, f in enumerate(files, 1):
        try:
            res = process_file(f, ym)
            rows.append(res)
        except Exception as e:
            print(f"[WARN] {f}: {e}", file=sys.stderr)

    p_dates = write_csv_dates(rows, out_dir, args.modified_month)
    p_conv  = write_csv_convergences(rows, out_dir, args.modified_month)
    p_depl  = write_csv_deplacements(rows, out_dir, args.modified_month)

    print("OK")
    print(f"Dates       → {p_dates}")
    print(f"Convergences→ {p_conv}")
    print(f"Déplacements→ {p_depl}")

if __name__ == "__main__":
    main()
