# concat_pm_csv.py
# Concatène des CSV "AnalysisData_PM_*.csv" en ajoutant le PM du nom de fichier
# Dépendances : pandas  (pip install pandas)

import re
from pathlib import Path
import pandas as pd

# ========= PARAMÈTRES À ADAPTER ======================================
INPUT_DIR = Path("./in")                  # Dossier source contenant les CSV
GLOB_PATTERN = "AnalysisData_PM_*.csv"    # Motif des fichiers
OUTPUT_PATH = Path("./out/concat_analysisdata.csv")  # Fichier de sortie
OUTPUT_SEP = ","                          # Séparateur de sortie ("," ou "\t")
# =====================================================================

PM_REGEXES = [
    # ex: AnalysisData_PM_242.250m.csv  → 242.250
    re.compile(r"PM[_\s-]?(\d+(?:[.,]\d+)?)m", re.IGNORECASE),
    # ex: PM242.250.csv
    re.compile(r"PM[_\s-]?(\d+(?:[.,]\d+)?)", re.IGNORECASE),
]

def parse_pm_from_name(name: str):
    """Retourne le PM (float) extrait du nom de fichier, sinon None."""
    for rx in PM_REGEXES:
        m = rx.search(name)
        if m:
            pm = m.group(1).replace(",", ".")
            try:
                return float(pm)
            except ValueError:
                pass
    return None

def read_csv_flexible(path: Path) -> pd.DataFrame:
    """Lit un CSV avec détection d'encodage et du séparateur."""
    encodings = ["utf-8-sig", "cp1252", "latin1", "utf-8"]
    last_err = None
    for enc in encodings:
        try:
            # sep=None + engine="python" → sniff automatique (tab, ;, ,)
            df = pd.read_csv(path, sep=None, engine="python", encoding=enc)
            return df
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Échec lecture {path.name}: {last_err}")

def main():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob(GLOB_PATTERN))
    if not files:
        print(f"Aucun fichier trouvé dans {INPUT_DIR} avec {GLOB_PATTERN}")
        return

    frames = []
    for f in files:
        try:
            df = read_csv_flexible(f)

            # Ajout PM/nom de fichier
            pm = parse_pm_from_name(f.name)
            df.insert(0, "PM_fichier", pm)  # 1re colonne = PM (float ou NaN)
            df.insert(1, "source_fichier", f.name)  # 2e colonne = nom du fichier

            frames.append(df)
        except Exception as e:
            print(f"[WARN] {f.name}: {e}")

    if not frames:
        print("Aucune donnée exploitable.")
        return

    out_df = pd.concat(frames, ignore_index=True)

    # Export
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig", sep=OUTPUT_SEP)
    print(f"[OK] Concaténation : {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
