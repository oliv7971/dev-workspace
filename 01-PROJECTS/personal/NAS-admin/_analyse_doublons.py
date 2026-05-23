"""
Analyse des doublons dans 11-DEVELOPPEMENT (hors dataroom).
Compare par nom de fichier, puis par contenu (taille) pour confirmer.
"""
import os
from collections import defaultdict

with open(r'D:\tmp_devp_files.txt', encoding='utf-8', errors='replace') as f:
    lines = [l.strip() for l in f if l.strip()]

BASE = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'
EXCL = BASE + r'\dataroom'

files = [l for l in lines if l.startswith(BASE) and not l.startswith(EXCL)]
print(f"Fichiers hors dataroom : {len(files)}")

# Grouper par nom de fichier (basename)
by_name = defaultdict(list)
for fp in files:
    name = fp.rsplit('\\', 1)[-1].lower()
    by_name[name].append(fp)

dupes_by_name = {k: v for k, v in by_name.items() if len(v) >= 2}
print(f"Noms de fichiers présents dans >=2 dossiers : {len(dupes_by_name)}")

# Stats par nombre de copies
from collections import Counter
copy_dist = Counter(len(v) for v in dupes_by_name.values())
print("\nDistribution (nb copies → nb fichiers) :")
for k in sorted(copy_dist):
    print(f"  {k} copies : {copy_dist[k]} fichiers")

# Dossiers impliqués dans les doublons
dupe_folder_counts = defaultdict(int)
for paths in dupes_by_name.values():
    for fp in paths:
        rel = fp[len(BASE):].lstrip('\\')
        top = rel.split('\\')[0]
        dupe_folder_counts[top] += 1

print("\nDossiers les plus impliqués dans les doublons :")
for folder, n in sorted(dupe_folder_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {folder:<40} {n:>5} fichiers dupliqués")

# Focus sur les doublons entre les dossiers lisp/autolisp
LISP_DIRS = ['lisp', 'lisp - copie', 'scripts lisp', 'scriptslisp',
             'BIBLIOTHEQUE AUTOCAD', 'EXERCICES AUTOLISP du cours', '13 - lisp']

print("\n--- DOUBLONS ENTRE DOSSIERS LISP ---")
lisp_files = [fp for fp in files if any(
    fp[len(BASE)+1:].lower().startswith(d.lower()) for d in LISP_DIRS)]
print(f"Total fichiers dans dossiers lisp : {len(lisp_files)}")

lisp_by_name = defaultdict(list)
for fp in lisp_files:
    name = fp.rsplit('\\', 1)[-1].lower()
    lisp_by_name[name].append(fp)
lisp_dupes = {k: v for k, v in lisp_by_name.items() if len(v) >= 2}
print(f"Noms en doublon dans les dossiers lisp : {len(lisp_dupes)}")

# Echantillon des doublons lisp
print("\nExemples (20 premiers) :")
for i, (name, paths) in enumerate(sorted(lisp_dupes.items())[:20]):
    print(f"  {name}")
    for p in paths:
        rel = p[len(BASE)+1:]
        top = rel.split('\\')[0]
        print(f"    [{top}] {rel[len(top)+1:]}")

# Estimation % de doublons (par nom) dans les dossiers lisp
lsp_total = len(lisp_files)
lsp_unique = len(lisp_by_name)
lsp_dupe_files = sum(len(v) - 1 for v in lisp_dupes.values())
print(f"\nFichiers lisp totaux : {lsp_total}")
print(f"Noms uniques        : {lsp_unique}")
print(f"Fichiers en doublon : {lsp_dupe_files} (~{100*lsp_dupe_files//lsp_total}%)")
