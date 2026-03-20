import argparse
import os
from pathlib import Path
import pandas as pd

DEFAULT_ROOT_DIR = r"C:\temp\1-tableaux"

def get_root_dir_from_args_or_default(arg_root: str | None) -> Path:
    if arg_root and os.path.isdir(arg_root):
        return Path(arg_root)
    if os.path.isdir(DEFAULT_ROOT_DIR):
        return Path(DEFAULT_ROOT_DIR)
    raise FileNotFoundError(f"Dossier racine introuvable : {arg_root or DEFAULT_ROOT_DIR}")

def main():
    ap = argparse.ArgumentParser(description="Assembler les CSV (smc_evolutions.py) en un récap")
    ap.add_argument("--root", help="Dossier contenant les CSV (dates_/convergences_/deplacements_)")
    ap.add_argument("--month", required=True, help="Mois au format YYYY-MM (ex : 2025-07)")
    args = ap.parse_args()

    root_dir = get_root_dir_from_args_or_default(args.root)
    ym = args.month

    dates_csv = root_dir / f"dates_mesures_{ym}.csv"
    conv_csv  = root_dir / f"convergences_{ym}.csv"
    disp_csv  = root_dir / f"deplacements_{ym}.csv"

    missing = [p for p in (dates_csv, conv_csv, disp_csv) if not p.exists()]
    if missing:
        print("[ERREUR] CSV manquants. Lance d’abord smc_evolutions.py pour", ym)
        for p in missing: print("  - manquant :", p)
        return 2

    # Lecture UTF-8 BOM
    dates = pd.read_csv(dates_csv, encoding="utf-8-sig")
    conv  = pd.read_csv(conv_csv,  encoding="utf-8-sig")
    disp  = pd.read_csv(disp_csv,  encoding="utf-8-sig")

    out_dir = root_dir / "_recaps"
    out_dir.mkdir(parents=True, exist_ok=True)
    master_xlsx = out_dir / f"_master_recap_{ym}.xlsx"

    with pd.ExcelWriter(master_xlsx, engine="openpyxl") as xw:
        dates.to_excel(xw, index=False, sheet_name="Dates")
        conv.to_excel(xw, index=False, sheet_name="Convergences")
        disp.to_excel(xw, index=False, sheet_name="Deplacements")

    print(f"[OK] Récap écrit : {master_xlsx}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
