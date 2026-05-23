"""
Compare les fichiers de _a_classer (scan filesystem réel)
contre toute la DB SQLite (tous les dossiers de 37-TUNNEL GRAND CHAMBON).
"""
import os
import sqlite3
from collections import defaultdict

DB_PATH = "./reports/inventory_chambon37.db"
BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"
A_CLASSER = os.path.join(BASE, "_a_classer")


def format_size(n):
    if n >= 1_073_741_824:
        return f"{n/1_073_741_824:.2f} Go"
    elif n >= 1_048_576:
        return f"{n/1_048_576:.1f} Mo"
    return f"{n/1024:.1f} Ko"


# ── Index DB : (filename, size) → liste de chemins ──────────────────────────
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT filename, size, path FROM files")
db_index = defaultdict(list)
for fname, size, path in cur.fetchall():
    db_index[(fname, size)].append(path)
conn.close()
print(f"DB chargée : {len(db_index)} entrées (nom+taille uniques)\n")

# ── Scan filesystem de _a_classer ────────────────────────────────────────────
ac_files = []
for root, dirs, files in os.walk(A_CLASSER):
    for f in files:
        fp = os.path.join(root, f)
        try:
            size = os.path.getsize(fp)
            ac_files.append((f, size, fp))
        except OSError:
            pass

print(f"_a_classer (filesystem) : {len(ac_files)} fichiers  |  {format_size(sum(s for _,s,_ in ac_files))}\n")

# ── Comparaison ──────────────────────────────────────────────────────────────
match = []
no_match = []

for fname, size, fpath in ac_files:
    key = (fname, size)
    if key in db_index:
        match.append((fname, size, fpath, db_index[key]))
    else:
        no_match.append((fname, size, fpath))

print(f"{'='*70}")
print(f"Deja presents ailleurs (nom+taille) : {len(match):>4}  |  {format_size(sum(s for _,s,_,__ in match))}")
print(f"Uniques dans _a_classer             : {len(no_match):>4}  |  {format_size(sum(s for _,s,_ in no_match))}")
print(f"{'='*70}\n")

if no_match:
    print("FICHIERS UNIQUES (non trouves ailleurs dans le NAS) :")
    for fname, size, fpath in sorted(no_match, key=lambda x: -x[1]):
        rel = os.path.relpath(fpath, A_CLASSER)
        print(f"  {format_size(size):>10}  {rel}")

print()
print("FICHIERS DEJA PRESENTS AILLEURS (echantillon - 20 premiers) :")
for fname, size, fpath, others in sorted(match, key=lambda x: -x[1])[:20]:
    rel = os.path.relpath(fpath, A_CLASSER)
    other_rels = [os.path.relpath(p, BASE) for p in others[:2]]
    print(f"  {format_size(size):>10}  {rel}")
    for r in other_rels:
        print(f"             -> {r}")
