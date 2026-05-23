"""
Compare backup\18-A89 content vs existing auscultation folders.
Find files unique to backup (not yet in any destination).

backup\18-A89\
  01- auscultations juin 2018  ->  A89\01- auscultations juin 2018
  02-auscultation OCTOBRE 2018 ->  A89\02-auscultation OCTOBRE 2018  (vide)
                                   + racine\003-auscultations A89 (35 Mo)
  14-a89                       ->  racine\14-a89
  sauvegarde carte             ->  racine\sauvegarde carte
"""

import os
from pathlib import Path

ROOT_39 = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\39-autoroute A89"
BACKUP  = Path(ROOT_39) / "backup" / "18-A89"

# Paires (source_backup, destinations_a_comparer)
PAIRS = [
    (
        "01- auscultations juin 2018",
        [r"A89\01- auscultations juin 2018"]
    ),
    (
        "02-auscultation OCTOBRE 2018",
        [
            r"A89\02-auscultation OCTOBRE 2018",
            r"003-auscultations A89",
        ]
    ),
    (
        "14-a89",
        [r"14-a89", r"003-auscultations A89"]
    ),
    (
        "sauvegarde carte",
        [r"sauvegarde carte"]
    ),
]


def index_folder(folder: Path) -> dict[str, int]:
    """Returns {relative_path_lower: size} for all files."""
    index = {}
    if not folder.exists():
        return index
    for f in folder.rglob("*"):
        if f.is_file():
            rel = f.relative_to(folder)
            key = str(rel).lower().replace("\\", "/")
            index[key] = f.stat().st_size
    return index


def main():
    print(f"=== Compare backup\\18-A89 vs destinations ===\n")

    total_unique_files = 0
    total_unique_bytes = 0

    for src_name, dest_rel_list in PAIRS:
        src = BACKUP / src_name
        if not src.exists():
            print(f"[SKIP] backup\\{src_name} — dossier introuvable")
            continue

        # Build union of all destination files
        dest_union: dict[str, int] = {}
        for d in dest_rel_list:
            dest_path = Path(ROOT_39) / d
            dest_union.update(index_folder(dest_path))

        src_index = index_folder(src)

        # Files unique to backup (not in any destination)
        unique = []
        for key, size in src_index.items():
            if key not in dest_union:
                unique.append((key, size))

        unique_bytes = sum(s for _, s in unique)
        print(f"--- backup\\{src_name}")
        print(f"    Backup: {len(src_index)} fichiers")
        dest_labels = " + ".join(dest_rel_list)
        print(f"    Dest:   [{dest_labels}] → union {len(dest_union)} fichiers")
        print(f"    Uniques backup: {len(unique)} fichiers  ({unique_bytes/1024/1024:.1f} Mo)")

        if unique:
            # Show sample (first 20)
            print(f"    Exemples:")
            for key, size in sorted(unique)[:20]:
                print(f"      {size:>10,}  {key}")
            if len(unique) > 20:
                print(f"      ... et {len(unique)-20} autres")

        total_unique_files += len(unique)
        total_unique_bytes += unique_bytes
        print()

    print(f"=== TOTAL uniques dans backup : {total_unique_files} fichiers  ({total_unique_bytes/1024/1024:.1f} Mo) ===")


if __name__ == "__main__":
    main()
