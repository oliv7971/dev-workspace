"""
Déplace _olds, 99-cle intenso et cle 181209 dans _atrier
au sein de 38-TUNNEL DE SIAIX.

Usage :
  python move_siaix_atrier.py           → dry-run (aperçu)
  python move_siaix_atrier.py --execute → exécution réelle
"""
import sys
import os
import shutil

ROOT = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\38-TUNNEL DE SIAIX"
ATRIER = os.path.join(ROOT, "_atrier")

SOURCES = [
    "_olds",
    "99-cle intenso",
    "cle 181209",
]

dry_run = "--execute" not in sys.argv

if dry_run:
    print("=== DRY-RUN — aucune modification (ajouter --execute pour appliquer) ===\n")
else:
    print("=== EXÉCUTION ===\n")

for src_name in SOURCES:
    src = os.path.join(ROOT, src_name)
    dst = os.path.join(ATRIER, src_name)

    if not os.path.exists(src):
        print(f"  [ABSENT]  {src_name}")
        continue

    print(f"  {'[MOVE]' if not dry_run else '[DRY]'}  {src_name}  →  _atrier\\{src_name}")

    if not dry_run:
        os.makedirs(ATRIER, exist_ok=True)
        shutil.move(src, dst)
        print(f"           OK")

if dry_run:
    print("\nRelancer avec --execute pour appliquer.")
else:
    print("\nTerminé.")
