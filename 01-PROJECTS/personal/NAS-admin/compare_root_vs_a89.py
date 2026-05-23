# Compare les dossiers homonymes a la racine de 39-A89 vs ceux dans A89\
# Pour chaque paire, liste les fichiers presents uniquement a la racine (potentiels uniques)
import os

ROOT39 = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\39-autoroute A89"
ROOT_A89 = os.path.join(ROOT39, "A89")

# Paires a comparer : (dossier racine, dossier dans A89\)
PAIRS = [
    ("A89-auscultations OCT 20201", "A89-auscultations OCT 20201"),
    ("A89-auscultations OCT 2022",  "A89-auscultations OCT 2022"),
    ("A89-D233",                    "A89-D233"),
]

def get_files(folder):
    result = {}
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, folder).replace("\\", "/").lower()
            try:
                result[rel] = os.path.getsize(full)
            except OSError:
                pass
    return result

for root_name, a89_name in PAIRS:
    path_root = os.path.join(ROOT39, root_name)
    path_a89  = os.path.join(ROOT_A89, a89_name)

    print(f"\n{'='*70}")
    print(f"RACINE : {root_name}")
    print(f"A89\\   : {a89_name}")

    if not os.path.isdir(path_root):
        print(f"  !! Dossier racine absent")
        continue
    if not os.path.isdir(path_a89):
        print(f"  !! Dossier A89\\ absent")
        continue

    files_root = get_files(path_root)
    files_a89  = get_files(path_a89)

    size_root = sum(files_root.values()) / 1024 / 1024
    size_a89  = sum(files_a89.values())  / 1024 / 1024
    print(f"  Racine : {len(files_root):>5} fichiers  {size_root:>8.1f} Mo")
    print(f"  A89\\   : {len(files_a89):>5} fichiers  {size_a89:>8.1f} Mo")

    # Fichiers uniquement dans la racine (pas dans A89\)
    only_root = {k: v for k, v in files_root.items() if k not in files_a89}
    # Fichiers dans les deux (doublons purs)
    both = {k for k in files_root if k in files_a89}

    print(f"\n  Doublons (meme chemin relatif) : {len(both)} fichiers")

    if only_root:
        total = sum(only_root.values()) / 1024 / 1024
        print(f"  Uniquement a la RACINE        : {len(only_root)} fichiers  {total:.1f} Mo")
        for k, v in sorted(only_root.items())[:15]:
            print(f"      {k[:80]}  ({v/1024:.1f} Ko)")
        if len(only_root) > 15:
            print(f"      ... et {len(only_root)-15} autres")
    else:
        print(f"  -> Tous les fichiers racine sont dans A89\\ => racine est un sous-ensemble")

print("\n\nDone.")
