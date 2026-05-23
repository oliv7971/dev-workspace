"""Compare CHAMBON-161220 vs 02-PHASE 02 - Eiffage 2016.

Phase 1 : correspondances nom+taille via SQLite (rapide).
Phase 2 : vérification MD5 sur un échantillon des candidats (lent).
"""
import sqlite3, os, hashlib, random

DB   = "reports/inventory_chambon37.db"
ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\37-TUNNEL GRAND CHAMBON\\"
DOSS_A = "CHAMBON-161220"   # dossier à tester
DOSS_B = "02-PHASE 02 - Eiffage 2016"   # référence

def human_size(n):
    if not n: n = 0
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

def md5(path, chunk=1<<20):
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for bloc in iter(lambda: f.read(chunk), b""):
                h.update(bloc)
        return h.hexdigest()
    except Exception as e:
        return None

c = sqlite3.connect(DB)

print(f"\n{'='*72}")
print(f"COMPARAISON  {DOSS_A}  vs  {DOSS_B}")
print(f"{'='*72}")

# --- Phase 1 : nom + taille ---
prefix_a = ROOT + DOSS_A + "\\"
prefix_b = ROOT + DOSS_B + "\\"

rows_a = c.execute(
    "SELECT path, filename, size FROM files WHERE path LIKE ?",
    (prefix_a + "%",)
).fetchall()
rows_b = c.execute(
    "SELECT path, filename, size FROM files WHERE path LIKE ?",
    (prefix_b + "%",)
).fetchall()

print(f"\n  {DOSS_A:30s} : {len(rows_a):>6} fichiers   {human_size(sum(r[2] or 0 for r in rows_a))}")
print(f"  {DOSS_B:30s} : {len(rows_b):>6} fichiers   {human_size(sum(r[2] or 0 for r in rows_b))}")

# Index B : (filename, size) → liste de paths
index_b = {}
for path, fname, sz in rows_b:
    key = (fname, sz)
    index_b.setdefault(key, []).append(path)

# Matchs dans A
matches = []   # (path_a, path_b)
no_match = []
for path_a, fname, sz in rows_a:
    key = (fname, sz)
    if key in index_b:
        matches.append((path_a, index_b[key][0]))
    else:
        no_match.append(path_a)

pct = len(matches) / len(rows_a) * 100 if rows_a else 0
print(f"\n  Correspondances nom+taille : {len(matches):,} / {len(rows_a):,}  ({pct:.1f}%)")
print(f"  Sans correspondance        : {len(no_match):,}")

# Volume des non-matchs
vol_no_match = sum(
    sz for _, fname, sz in rows_a
    if (fname, sz) not in index_b
)
print(f"  Volume sans correspondance : {human_size(vol_no_match)}")

# --- Phase 2 : vérification MD5 sur échantillon ---
SAMPLE = 40
print(f"\n{'='*72}")
print(f"VÉRIFICATION MD5 (échantillon {SAMPLE} fichiers parmi les candidats)")
print(f"{'='*72}")

sample = random.sample(matches, min(SAMPLE, len(matches)))
identiques = 0
differents  = 0
erreurs     = 0

for path_a, path_b in sample:
    h_a = md5(path_a)
    h_b = md5(path_b)
    if h_a is None or h_b is None:
        erreurs += 1
    elif h_a == h_b:
        identiques += 1
    else:
        differents += 1
        rel_a = path_a[len(ROOT):]
        print(f"  ❌ DIFF  {rel_a[:70]}")

print(f"\n  Sur {len(sample)} fichiers testés :")
print(f"    ✅ Identiques  : {identiques}")
print(f"    ❌ Différents  : {differents}")
print(f"    ⚠️  Erreurs     : {erreurs}")

# --- Résumé sous-dossiers de CHAMBON-161220 ---
print(f"\n{'='*72}")
print(f"RÉPARTITION des non-matchs par sous-dossier de {DOSS_A}")
print(f"{'='*72}")
from collections import defaultdict
subs = defaultdict(lambda: [0, 0])
for path, fname, sz in rows_a:
    rel = path[len(prefix_a):]
    sub = rel.split("\\")[0]
    key = (fname, sz)
    if key not in index_b:
        subs[sub][0] += 1
        subs[sub][1] += sz or 0

for sub, (n, s) in sorted(subs.items(), key=lambda x: -x[1][1]):
    print(f"  {sub:<50} {n:>5} fich.  {human_size(s):>10}")

print(f"\n{'='*72}")
if pct >= 90:
    print("CONCLUSION : CHAMBON-161220 est très probablement un doublon de 02-PHASE 02.")
    print("  → Peut être mis en _doublons après vérification MD5 complète.")
elif pct >= 60:
    print("CONCLUSION : Forte similarité. Vérifier les non-matchs avant de supprimer.")
else:
    print("CONCLUSION : Similarité partielle. Contenu original présent dans CHAMBON-161220.")

c.close()
