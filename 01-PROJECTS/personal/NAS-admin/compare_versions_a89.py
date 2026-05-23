# Compare les dates de modification pour les fichiers en doublon (racine vs A89\)
# Signale les fichiers ou la version RACINE est plus recente que A89\ -> a ne pas supprimer
import os

ROOT39  = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\39-autoroute A89"
ROOT_A89 = os.path.join(ROOT39, "A89")

PAIRS = [
    ("A89-auscultations OCT 20201", "A89-auscultations OCT 20201"),
    ("A89-auscultations OCT 2022",  "A89-auscultations OCT 2022"),
    ("A89-D233",                    "A89-D233"),
]

def get_files_with_mtime(folder):
    result = {}
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, folder).replace("\\", "/").lower()
            try:
                st = os.stat(full)
                result[rel] = (st.st_size, st.st_mtime, full)
            except OSError:
                pass
    return result

from datetime import datetime

for root_name, a89_name in PAIRS:
    path_root = os.path.join(ROOT39, root_name)
    path_a89  = os.path.join(ROOT_A89, a89_name)

    print(f"\n{'='*70}")
    print(f"RACINE : {root_name}")

    if not os.path.isdir(path_root) or not os.path.isdir(path_a89):
        print("  !! Dossier manquant")
        continue

    files_root = get_files_with_mtime(path_root)
    files_a89  = get_files_with_mtime(path_a89)

    # Fichiers communs : comparer les dates
    newer_in_root   = []  # racine plus recente
    older_in_root   = []  # A89\ plus recente ou egale
    same_in_root    = 0

    for rel, (size_r, mtime_r, path_r) in files_root.items():
        if rel in files_a89:
            size_a, mtime_a, path_a = files_a89[rel]
            diff = mtime_r - mtime_a  # secondes
            if diff > 2:   # racine plus recente de plus de 2s
                newer_in_root.append((rel, size_r, mtime_r, mtime_a, diff))
            else:
                same_in_root += 1

    # Fichiers uniques en racine (hors ~$ temporaires Office)
    only_root = {k: v for k, v in files_root.items()
                 if k not in files_a89 and not os.path.basename(k).startswith("~$")}

    print(f"  Fichiers communs dont racine PLUS RECENTE : {len(newer_in_root)}")
    print(f"  Fichiers communs ok (A89\\ >= racine)       : {same_in_root}")
    print(f"  Fichiers uniques en racine (hors ~$)        : {len(only_root)}")

    if newer_in_root:
        print(f"\n  !! FICHIERS RACINE PLUS RECENTS (a conserver) :")
        for rel, size_r, mtime_r, mtime_a, diff in sorted(newer_in_root, key=lambda x: -x[4]):
            dr = datetime.fromtimestamp(mtime_r).strftime("%Y-%m-%d %H:%M")
            da = datetime.fromtimestamp(mtime_a).strftime("%Y-%m-%d %H:%M")
            print(f"      {rel[:70]}")
            print(f"           racine={dr}  A89\\={da}  (+{diff/3600:.1f}h)")
    else:
        print(f"\n  -> Aucun fichier racine plus recent : suppression racine OK")

    if only_root:
        total = sum(v[0] for v in only_root.values()) / 1024 / 1024
        print(f"\n  Fichiers UNIQUES a la racine ({len(only_root)}, {total:.1f} Mo) :")
        for rel, (size, mtime, _) in sorted(only_root.items())[:10]:
            d = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            print(f"      {rel[:70]}  {size/1024:.0f} Ko  {d}")
        if len(only_root) > 10:
            print(f"      ... et {len(only_root)-10} autres")

print("\n\nDone.")
