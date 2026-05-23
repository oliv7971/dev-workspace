"""
Supprime le dossier TMS CHAMBON\ (copie bit-à-bit confirmée des scans dans 02-PHASE 02).

Usage:
    python cleanup_tms_chambon.py           # dry-run
    python cleanup_tms_chambon.py --execute # suppression réelle
"""
import os
import sys
import shutil

BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"
TARGET = os.path.join(BASE, "TMS CHAMBON")

EXECUTE = "--execute" in sys.argv


def format_size(n):
    if n >= 1_073_741_824:
        return f"{n / 1_073_741_824:.2f} Go"
    elif n >= 1_048_576:
        return f"{n / 1_048_576:.1f} Mo"
    return f"{n / 1024:.1f} Ko"


def count_folder(path):
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
                total_files += 1
            except OSError:
                pass
    return total_files, total_size


def main():
    if not os.path.exists(TARGET):
        print(f"Dossier introuvable : {TARGET}")
        print("Peut-être déjà supprimé ?")
        sys.exit(0)

    print(f"Cible : {TARGET}\n")
    print("Comptage en cours...")
    n_files, total_size = count_folder(TARGET)
    print(f"  {n_files} fichiers  |  {format_size(total_size)}\n")

    if not EXECUTE:
        print("=== DRY-RUN — aucune modification ===")
        print(f"\nRelancez avec --execute pour supprimer le dossier.")
        return

    print("Suppression en cours...")
    try:
        shutil.rmtree(TARGET)
        print(f"Dossier supprimé : TMS CHAMBON\\")
        print(f"Libéré : {format_size(total_size)}  ({n_files} fichiers)")
    except Exception as e:
        print(f"ERREUR : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
