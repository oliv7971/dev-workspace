"""
Vérifie que les fichiers dans _olds, 99-cle intenso et cle 181209
sont présents ailleurs dans 38-TUNNEL DE SIAIX.

L'index de référence exclut ces dossiers eux-mêmes pour éviter
la circularité (un fichier ne peut être son propre doublon).
"""
import sqlite3
from collections import defaultdict

DB_PATH = "./reports/inventory_siaix38.db"
ROOT    = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\38-TUNNEL DE SIAIX\\"

# Dossiers à vérifier (relatifs à ROOT)
SUSPECTS = [
    "_olds",
    "99-cle intenso",
    "cle 181209",
]

def format_size(n):
    if n is None: n = 0
    if n >= 1_073_741_824: return f"{n/1_073_741_824:.2f} Go"
    if n >= 1_048_576:     return f"{n/1_048_576:.1f} Mo"
    return f"{n/1024:.1f} Ko"


conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()
cur.execute("SELECT filename, size, path FROM files")
all_rows = cur.fetchall()
conn.close()

print(f"DB chargée : {len(all_rows):,} fichiers\n")

# Préfixes à exclure de l'index de référence
suspect_prefixes = tuple(ROOT + s for s in SUSPECTS)

# Index de référence = tout SAUF les dossiers suspects
ref_index = defaultdict(list)
for fname, size, path in all_rows:
    if not path.startswith(suspect_prefixes):
        ref_index[(fname, size)].append(path)

print(f"Index de référence (hors suspects) : {len(ref_index):,} clés (nom+taille)\n")

# Pour chaque dossier suspect, analyser
for suspect in SUSPECTS:
    prefix = ROOT + suspect
    files = [(fname, size, path) for fname, size, path in all_rows
             if path.startswith(prefix)]

    if not files:
        print(f"\n{'='*72}")
        print(f"DOSSIER : {suspect}")
        print("  (vide ou non trouvé dans la DB)")
        continue

    total_size  = sum(s or 0 for _, s, _ in files)
    match       = [(fn, sz, p) for fn, sz, p in files if (fn, sz) in ref_index]
    no_match    = [(fn, sz, p) for fn, sz, p in files if (fn, sz) not in ref_index]
    match_size  = sum(sz or 0 for _, sz, _ in match)
    unique_size = sum(sz or 0 for _, sz, _ in no_match)

    print(f"\n{'='*72}")
    print(f"DOSSIER : {suspect}")
    print(f"  Total       : {len(files):>6} fichiers  {format_size(total_size)}")
    print(f"  Présents ailleurs (doublons) : {len(match):>6}  {format_size(match_size)}")
    print(f"  Uniques (à conserver)        : {len(no_match):>6}  {format_size(unique_size)}")

    if no_match:
        print(f"\n  FICHIERS UNIQUES (non trouvés ailleurs) — top 30 :")
        for fname, sz, path in sorted(no_match, key=lambda x: -(x[1] or 0))[:30]:
            rel = path[len(ROOT):]
            print(f"    {format_size(sz):>10}  {rel}")
    else:
        print(f"\n  ✅ Tous les fichiers sont présents ailleurs — dossier SUPPRIMABLE")

    # Quelques exemples de doublons
    if match:
        print(f"\n  Exemples de doublons (10 plus lourds) :")
        for fname, sz, path in sorted(match, key=lambda x: -(x[1] or 0))[:10]:
            rel = path[len(ROOT):]
            others = [p[len(ROOT):] for p in ref_index[(fname, sz)][:2]]
            print(f"    {format_size(sz):>10}  {rel}")
            for o in others:
                print(f"               -> {o}")

print(f"\n{'='*72}")
print("RÉCAPITULATIF")
print(f"{'='*72}")
for suspect in SUSPECTS:
    prefix = ROOT + suspect
    files  = [(fn, sz, p) for fn, sz, p in all_rows if p.startswith(prefix)]
    if not files: continue
    total  = sum(sz or 0 for _, sz, _ in files)
    match  = sum(1 for fn, sz, _ in files if (fn, sz) in ref_index)
    msize  = sum(sz or 0 for fn, sz, _ in files if (fn, sz) in ref_index)
    print(f"  {suspect:<35} {len(files):>6} fich. {format_size(total):>10}  →  doublons: {match} ({format_size(msize)})")
