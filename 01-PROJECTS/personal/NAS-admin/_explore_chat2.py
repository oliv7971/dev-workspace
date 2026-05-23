"""Analyse des recouvrements entre dossiers de 1er niveau du tunnel du Chat."""
import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Construire un index : hash_md5 → set de dossiers L1 qui le contiennent
c.execute("SELECT path, hash_md5, size FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''")
hash_to_dirs = defaultdict(set)
hash_to_size = {}
dir_hashes = defaultdict(set)

for path, h, sz in c.fetchall():
    rel = path.replace(BASE, '').lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine)'
    hash_to_dirs[h].add(top)
    hash_to_size[h] = sz or 0
    dir_hashes[top].add(h)

# ── Matrice de recouvrement entre paires de dossiers ─────────────────────
dirs_list = sorted(dir_hashes.keys(), key=lambda d: -len(dir_hashes[d]))
# Ne garder que les dossiers avec >10 fichiers hashés
dirs_list = [d for d in dirs_list if len(dir_hashes[d]) > 10]

print(f"{'Dossier A':<40} {'Dossier B':<40} {'Communs':>8} {'Go com':>7} {'%A':>5} {'%B':>5}")
print('=' * 107)

pairs = []
for i, da in enumerate(dirs_list):
    for db in dirs_list[i+1:]:
        common = dir_hashes[da] & dir_hashes[db]
        if len(common) < 5:
            continue
        sz_common = sum(hash_to_size.get(h, 0) for h in common)
        pct_a = 100 * len(common) / len(dir_hashes[da])
        pct_b = 100 * len(common) / len(dir_hashes[db])
        pairs.append((da, db, len(common), sz_common, pct_a, pct_b))

# Trier par taille commune décroissante
pairs.sort(key=lambda x: -x[3])
for da, db, n, sz, pa, pb in pairs[:30]:
    print(f"  {da:<38} {db:<38} {n:>8} {sz/1024**3:>6.1f} {pa:>4.0f}% {pb:>4.0f}%")

# ── Focus : 03-tunnel chat vs TUNNEL DU CHAT - 2017 ─────────────────────
print("\n\n=== FOCUS : 03-tunnel chat vs TUNNEL DU CHAT - 2017 ===")
d1 = '03-tunnel chat'
d2 = 'TUNNEL DU CHAT - 2017'
h1 = dir_hashes.get(d1, set())
h2 = dir_hashes.get(d2, set())
common = h1 & h2
only1 = h1 - h2
only2 = h2 - h1
sz_com = sum(hash_to_size.get(h,0) for h in common)
sz_o1  = sum(hash_to_size.get(h,0) for h in only1)
sz_o2  = sum(hash_to_size.get(h,0) for h in only2)
print(f"  Communs : {len(common)} hashes, {sz_com/1024**3:.1f} Go")
print(f"  Uniques à {d1} : {len(only1)} hashes, {sz_o1/1024**3:.1f} Go")
print(f"  Uniques à {d2} : {len(only2)} hashes, {sz_o2/1024**3:.1f} Go")

# Quels types de fichiers sont uniques à chacun ?
for label, hset in [(f'Uniques {d1}', only1), (f'Uniques {d2}', only2)]:
    ext_cnt = defaultdict(lambda: [0, 0])
    for h in hset:
        c.execute("SELECT extension, size FROM files WHERE hash_md5 = ? LIMIT 1", (h,))
        row = c.fetchone()
        if row:
            ext_cnt[row[0] or '(sans)'][0] += 1
            ext_cnt[row[0] or '(sans)'][1] += (row[1] or 0)
    print(f"\n  {label} — par extension :")
    for ext in sorted(ext_cnt, key=lambda e: -ext_cnt[e][1])[:10]:
        cnt, sz = ext_cnt[ext]
        print(f"    {ext:<12} {cnt:>5} fich  {sz/1024**3:>6.2f} Go")

conn.close()
