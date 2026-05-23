"""
Compresse les fichiers .PTS (exports Sintegra) avec 7-Zip compression maximale.
Crée une archive par dossier contenant des .PTS, puis supprime les originaux.

Usage:
    python compress_pts_7z.py           # dry-run, affiche ce qui serait fait
    python compress_pts_7z.py --execute # compression réelle + suppression originaux
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from collections import defaultdict

# Chemin NAS
BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"

# DB SQLite (contient déjà tous les chemins, évite le MAX_PATH Windows de 260 chars)
DB_PATH = "./reports/inventory_chambon37.db"

# 7-Zip — chemins classiques Windows
SEVENZIP_PATHS = [
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
]

EXECUTE = "--execute" in sys.argv


def find_7zip():
    for p in SEVENZIP_PATHS:
        if os.path.isfile(p):
            return p
    # Essai via PATH
    try:
        result = subprocess.run(["7z", "--version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            return "7z"
    except Exception:
        pass
    return None


def find_pts_by_folder():
    """
    Trouve tous les .PTS via la DB SQLite (évite le MAX_PATH Windows = 260 chars).
    Les chemins profonds comme CHAMBON final 7mai15\80-export scans... dépassent la limite.
    """
    folders = defaultdict(list)

    if not os.path.exists(DB_PATH):
        print(f"ERREUR : DB introuvable : {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT path FROM files WHERE UPPER(filename) LIKE '%.PTS'"
    )
    rows = cur.fetchall()
    conn.close()

    print(f"  DB : {len(rows)} entrées .PTS trouvées")

    for (full_path,) in rows:
        # Vérifier que le fichier existe vraiment (la DB peut être antérieure à des suppressions)
        if os.path.exists(full_path):
            folder = os.path.dirname(full_path)
            folders[folder].append(full_path)
        else:
            print(f"  SKIP (disparu) : {os.path.basename(full_path)}")

    return folders


def format_size(size_bytes):
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.1f} Go"
    elif size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} Mo"
    return f"{size_bytes / 1024:.1f} Ko"


def main():
    sevenzip = find_7zip()
    if sevenzip is None:
        print("ERREUR : 7-Zip introuvable.")
        print("Installez 7-Zip depuis https://www.7-zip.org/ puis relancez.")
        sys.exit(1)
    print(f"7-Zip trouvé : {sevenzip}")

    print(f"\nRecherche des fichiers .PTS dans :\n  {BASE}\n")
    folders = find_pts_by_folder()

    if not folders:
        print("Aucun fichier .PTS trouvé.")
        return

    total_files = sum(len(v) for v in folders.values())
    total_size = sum(
        os.path.getsize(f)
        for files in folders.values()
        for f in files
    )

    print(f"Trouvé : {total_files} fichiers .PTS dans {len(folders)} dossier(s)")
    print(f"Taille totale : {format_size(total_size)}\n")

    if not EXECUTE:
        print("=== DRY-RUN — aucune modification ===\n")

    errors = []

    for folder, pts_files in sorted(folders.items()):
        folder_size = sum(os.path.getsize(f) for f in pts_files)
        rel = os.path.relpath(folder, BASE)
        archive_name = "scans_PTS_sintegra.7z"
        archive_path = os.path.join(folder, archive_name)

        print(f"Dossier : {rel}")
        print(f"  {len(pts_files)} fichiers  |  {format_size(folder_size)}")
        print(f"  Archive  : {archive_name}")

        if not EXECUTE:
            for f in sorted(pts_files):
                print(f"    {format_size(os.path.getsize(f))}  {os.path.basename(f)}")
            print()
            continue

        # Vérifier que l'archive n'existe pas déjà
        if os.path.exists(archive_path):
            print(f"  SKIP : {archive_name} existe déjà dans ce dossier.")
            print()
            continue

        # Construction de la commande 7z
        # -mx=9 : compression maximale
        # -mmt=on : multi-thread
        # On passe les fichiers via un fichier liste (@listfile) pour éviter MAX_PATH
        list_file = archive_path + ".filelist.txt"
        try:
            with open(list_file, "w", encoding="utf-8") as lf:
                for f in sorted(pts_files):
                    lf.write(f + "\n")
            cmd = [sevenzip, "a", "-mx=9", "-mmt=on", archive_path, f"@{list_file}"]
        except Exception as e:
            print(f"  ERREUR création liste : {e}")
            errors.append(folder)
            print()
            continue

        print(f"  Compression en cours... (peut prendre plusieurs minutes)")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
            if result.returncode != 0:
                print(f"  ERREUR 7z (code {result.returncode}) :")
                print(result.stderr[-500:] if result.stderr else "(pas de stderr)")
                errors.append(folder)
                print()
                continue
        except subprocess.TimeoutExpired:
            print("  ERREUR : timeout dépassé (2h)")
            errors.append(folder)
            print()
            continue
        except Exception as e:
            print(f"  ERREUR : {e}")
            errors.append(folder)
            print()
            continue
        finally:
            # Nettoyage du fichier liste
            if os.path.exists(list_file):
                os.remove(list_file)

        # Vérifier que l'archive a bien été créée et n'est pas vide
        if not os.path.exists(archive_path) or os.path.getsize(archive_path) < 1024:
            print("  ERREUR : archive créée mais vide ou manquante, originaux conservés.")
            errors.append(folder)
            print()
            continue

        archive_size = os.path.getsize(archive_path)
        ratio = (1 - archive_size / folder_size) * 100 if folder_size > 0 else 0
        print(f"  Archive créée : {format_size(archive_size)}  (gain : {ratio:.1f}%)")

        # Suppression des originaux
        deleted = 0
        for f in pts_files:
            try:
                os.remove(f)
                deleted += 1
            except Exception as e:
                print(f"  WARN : impossible de supprimer {os.path.basename(f)} : {e}")

        print(f"  Originaux supprimés : {deleted}/{len(pts_files)}")
        print()

    print("=" * 60)
    if not EXECUTE:
        print(f"DRY-RUN terminé. Relancez avec --execute pour compresser.")
    elif errors:
        print(f"Terminé avec {len(errors)} erreur(s) dans :")
        for e in errors:
            print(f"  {os.path.relpath(e, BASE)}")
    else:
        print("Compression terminée avec succès.")


if __name__ == "__main__":
    main()
