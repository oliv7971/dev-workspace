"""
Fusionne plusieurs groupes de dossiers dans 38-TUNNEL DE SIAIX.
Chaque groupe est déplacé dans un dossier cible neutre (_NOM_MERGE_).

Stratégie : déplace chaque dossier source entier dans le dossier cible.
Aucune suppression automatique — à faire manuellement après vérification.

Usage :
  python merge_siaix_groupes.py           → dry-run
  python merge_siaix_groupes.py --execute → exécution réelle
"""
import os
import sys
import shutil

ROOT = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\38-TUNNEL DE SIAIX"
DRY  = "--execute" not in sys.argv

# Groupes à fusionner : (nom_cible_neutre, [dossiers_sources])
# Le nom cible est volontairement différent de TOUS les noms sources
# pour éviter la collision case-insensitive sur NAS Synology.
GROUPES = [
    (
        "_02-AUSCULTATIONS_CONV_",
        [
            "02-AUSCULTATIONS & CONVERGENCES",
            "02-Auscultation et convergences",
            "203-CONVERGENCES 171009",
        ]
    ),
    (
        "_30-METRES_",
        [
            "30-metres",
            "SIAIX-metres",
            "SIAIX-metres2",
            "001-calculs metres siaix 20180604",
        ]
    ),
    (
        "_SCANS_",
        [
            "scans siaix",
            "cubes scan siaix",
            "70-scan 171103",
        ]
    ),
]

print(f"{'=== DRY-RUN ===' if DRY else '=== EXÉCUTION ==='}\n")

for target_name, sources in GROUPES:
    target = os.path.join(ROOT, target_name)
    print(f"{'='*70}")
    print(f"GROUPE → {target_name}")
    print(f"{'='*70}")

    for src_name in sources:
        src = os.path.join(ROOT, src_name)
        dst = os.path.join(target, src_name)

        if not os.path.exists(src):
            print(f"  [ABSENT]  {src_name}")
            continue

        if os.path.exists(dst):
            print(f"  [DÉJÀ LÀ] {src_name}  →  {target_name}\\{src_name}")
            continue

        print(f"  {'[MOVE]' if not DRY else '[DRY] '} {src_name}  →  {target_name}\\{src_name}")

        if not DRY:
            os.makedirs(target, exist_ok=True)
            shutil.move(src, dst)
            print(f"          OK")

    print()

if DRY:
    print("Relancer avec --execute pour appliquer.")
else:
    print("Terminé. Vérifiez le contenu des dossiers _*_MERGE_* puis supprimez les sources à la main.")
