"""
Analyse le contenu de _a_classer dans 37-TUNNEL GRAND CHAMBON.
Compare nom+taille avec le reste du dossier (via DB SQLite).
"""
import sqlite3
import os
from collections import defaultdict

DB_PATH = "./reports/inventory_chambon37.db"
BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"
A_CLASSER = os.path.join(BASE, "_a_classer")


def format_size(n):
    if n >= 1_073_741_824:
        return f"{n / 1_073_741_824:.2f} Go"
    elif n >= 1_048_576:
        return f"{n / 1_048_576:.1f} Mo"
    return f"{n / 1024:.1f} Ko"


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── Contenu de _a_classer ────────────────────────────────────────────────────
cur.execute("""
    SELECT filename, size, path, extension
    FROM files
    WHERE path LIKE '%\\_a_classer%' ESCAPE '\\'
    ORDER BY size DESC
""")
ac_rows = cur.fetchall()

print(f"=== Contenu _a_classer ===")
print(f"Fichiers : {len(ac_rows)}")
total_ac = sum(r[1] for r in ac_rows)
print(f"Taille   : {format_size(total_ac)}\n")

# Arborescence 2 niveaux
from collections import Counter
sub_dirs = Counter()
for fname, size, path, ext in ac_rows:
    rel = os.path.relpath(path, A_CLASSER)
    parts = rel.split(os.sep)
    sub_dirs[parts[0] if len(parts) > 1 else "(racine)"] += 1

print("Sous-dossiers :")
for d, n in sorted(sub_dirs.items()):
    print(f"  {d:<60} {n} fichiers")

# Extensions
print("\nExtensions :")
ext_cnt = Counter()
ext_size = defaultdict(int)
for fname, size, path, ext in ac_rows:
    e = (ext or "").lower()
    ext_cnt[e] += 1
    ext_size[e] += size
for e, n in ext_cnt.most_common(15):
    print(f"  {e or '(sans)':<15} {n:>5} fichiers  {format_size(ext_size[e]):>10}")

# ── Comparaison nom+taille avec le reste ────────────────────────────────────
print(f"\n=== Comparaison avec le reste du NAS (nom+taille) ===")

# Index des fichiers HORS _a_classer
cur.execute("""
    SELECT filename, size
    FROM files
    WHERE path NOT LIKE '%\\_a_classer%' ESCAPE '\\'
""")
rest = defaultdict(set)
for fname, size in cur.fetchall():
    rest[fname].add(size)

match = 0
no_match = 0
match_list = []
no_match_list = []

for fname, size, path, ext in ac_rows:
    if fname in rest and size in rest[fname]:
        match += 1
        match_list.append((fname, size, path))
    else:
        no_match += 1
        no_match_list.append((fname, size, path))

total_match_size = sum(r[1] for r in match_list)
total_nomatch_size = sum(r[1] for r in no_match_list)

print(f"\nDéjà présents ailleurs (nom+taille)  : {match:>4} fichiers  {format_size(total_match_size):>10}")
print(f"Uniques dans _a_classer              : {no_match:>4} fichiers  {format_size(total_nomatch_size):>10}")

if no_match_list:
    print(f"\nFichiers UNIQUES dans _a_classer (non trouvés ailleurs) :")
    for fname, size, path in sorted(no_match_list, key=lambda x: -x[1])[:40]:
        rel = os.path.relpath(path, A_CLASSER)
        print(f"  {format_size(size):>10}  {rel}")
    if len(no_match_list) > 40:
        print(f"  ... et {len(no_match_list)-40} autres")

conn.close()
