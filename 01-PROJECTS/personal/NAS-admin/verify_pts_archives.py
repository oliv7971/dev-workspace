"""
Vérifie l'intégrité des archives scans_PTS_sintegra.7z créées par compress_pts_7z.py.
Utilise '7z t' (test) sur chaque archive.
Préfixe \\\\?\\ pour contourner la limite MAX_PATH de Windows.
"""

import os
import sys
import sqlite3
import subprocess
from collections import defaultdict

BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"
DB_PATH = "./reports/inventory_chambon37.db"
ARCHIVE_NAME = "scans_PTS_sintegra.7z"

SEVENZIP_PATHS = [
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
]


def find_7zip():
    for p in SEVENZIP_PATHS:
        if os.path.isfile(p):
            return p
    try:
        result = subprocess.run(["7z", "--version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            return "7z"
    except Exception:
        pass
    return None


def long_path(p):
    """Préfixe \\?\\ pour lever la limite MAX_PATH (260 chars) sur Windows."""
    if p.startswith("\\\\"):
        # UNC path → \\?\UNC\...
        return "\\\\?\\UNC\\" + p[2:]
    return "\\\\?\\" + p


def format_size(n):
    if n >= 1_073_741_824:
        return f"{n / 1_073_741_824:.2f} Go"
    elif n >= 1_048_576:
        return f"{n / 1_048_576:.1f} Mo"
    return f"{n / 1024:.1f} Ko"


def get_pts_folders():
    """Retrouve les dossiers qui contenaient des .PTS depuis la DB."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT path FROM files WHERE UPPER(filename) LIKE '%.PTS'")
    rows = cur.fetchall()
    conn.close()
    folders = set()
    for (path,) in rows:
        folders.add(os.path.dirname(path))
    return folders


def main():
    sevenzip = find_7zip()
    if sevenzip is None:
        print("ERREUR : 7-Zip introuvable.")
        sys.exit(1)
    print(f"7-Zip : {sevenzip}\n")

    folders = get_pts_folders()
    print(f"Dossiers à vérifier (depuis DB) : {len(folders)}\n")

    ok = 0
    fail = 0
    missing = 0

    for folder in sorted(folders):
        rel = os.path.relpath(folder, BASE)
        archive_path = os.path.join(folder, ARCHIVE_NAME)
        archive_long = long_path(archive_path)

        # Vérifier existence via préfixe long path
        exists = os.path.exists(archive_long)
        if not exists:
            print(f"MANQUANT : {rel}")
            print(f"  Chemin  : {archive_path}")
            missing += 1
            print()
            continue

        size = os.path.getsize(archive_long)
        print(f"Dossier : {rel}")
        print(f"  Archive : {ARCHIVE_NAME}  ({format_size(size)})")

        # Test 7z
        cmd = [sevenzip, "t", archive_long]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            if result.returncode == 0:
                print(f"  Intégrité : OK")
                ok += 1
            else:
                print(f"  Intégrité : ERREUR (code {result.returncode})")
                # Extraire la ligne d'erreur de la sortie 7z
                lines = (result.stdout + result.stderr).splitlines()
                for line in lines:
                    if "error" in line.lower() or "warning" in line.lower():
                        print(f"    {line.strip()}")
                fail += 1
        except subprocess.TimeoutExpired:
            print(f"  Intégrité : TIMEOUT")
            fail += 1
        except Exception as e:
            print(f"  Intégrité : ERREUR ({e})")
            fail += 1
        print()

    print("=" * 60)
    print(f"OK       : {ok}")
    print(f"Erreurs  : {fail}")
    print(f"Manquants: {missing}")
    if fail == 0 and missing == 0:
        print("\nToutes les archives sont valides.")
    else:
        print("\nATTENTION : des archives sont manquantes ou corrompues.")


if __name__ == "__main__":
    main()
