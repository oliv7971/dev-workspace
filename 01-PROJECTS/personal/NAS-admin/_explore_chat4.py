"""Analyse des dossiers restants après phase 1 et leurs recouvrements."""
import sqlite3, os
from collections import defaultdict

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'

# Dossiers supprimés en phase 1
DELETED = {
    'TUNNEL DU CHAT - 2017',
    'rep pytha scooter ordi chat',
    '10-Tunnel du Chat',
    '01-donnees avant projet 2017- PAUL & LUDO & TMS',
    '21-travaux-bureau-proj',
    '70-sauvegardes cartes TPS1200',
    'Migration TMS Amberg chat',
    'LUDO',
}

conn = sqlite3.connect(DB)
c = conn.cursor()

# Filtrer les fichiers des dossiers encore existants
c.execute("SELECT path, hash_md5, size, filename, modified_time FROM files")
dir_hashes = defaultdict(set)
dir_files = defaultdict(list)
hash_size = {}

for path, h, sz, fn, mt in c.fetchall():
    rel = path.replace(BASE, '').lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine)'
    if top in DELETED:
        continue
    if h:
        dir_hashes[top].add(h)
        hash_size[h] = sz or 0
    dir_files[top].append((fn, sz, h, mt, rel))

# Stats restantes
print(f"{'Dossier restant':<55} {'Fich':>7} {'Hash':>7} {'Go':>7}")
print('=' * 80)
for d in sorted(dir_files.keys(), key=lambda x: -sum(s or 0 for _,s,_,_,_ in dir_files[x])):
    n = len(dir_files[d])
    nh = len(dir_hashes[d])
    sz = sum(s or 0 for _,s,_,_,_ in dir_files[d])
    print(f"  {d:<53} {n:>7} {nh:>7} {sz/1024**3:>6.1f}")

# Recouvrements
dirs_list = [d for d in sorted(dir_hashes.keys()) if len(dir_hashes[d]) > 5]
print(f"\n{'Dossier A':<35} {'Dossier B':<35} {'Com':>5} {'Go':>6} {'%A':>5} {'%B':>5}")
print('=' * 95)

pairs = []
for i, da in enumerate(dirs_list):
    for db in dirs_list[i+1:]:
        common = dir_hashes[da] & dir_hashes[db]
        if len(common) < 3:
            continue
        sz_common = sum(hash_size.get(h, 0) for h in common)
        pct_a = 100 * len(common) / len(dir_hashes[da])
        pct_b = 100 * len(common) / len(dir_hashes[db])
        pairs.append((da, db, len(common), sz_common, pct_a, pct_b))

pairs.sort(key=lambda x: -x[3])
for da, db, n, sz, pa, pb in pairs[:25]:
    print(f"  {da:<33} {db:<33} {n:>5} {sz/1024**3:>5.1f} {pa:>4.0f}% {pb:>4.0f}%")

# Structure de 2e niveau des dossiers intéressants
print("\n\n=== Structure 2e niveau des dossiers restants (hors TMS) ===")
for d in sorted(dir_files.keys()):
    if d == 'TMS':
        continue
    sz_total = sum(s or 0 for _,s,_,_,_ in dir_files[d])
    if sz_total < 1_000_000:  # skip < 1 Mo
        continue
    print(f"\n  {d}/ ({len(dir_files[d])} fich, {sz_total/1024**3:.2f} Go)")
    # Sous-dossiers
    subs = defaultdict(lambda: [0, 0])
    for fn, sz, h, mt, rel in dir_files[d]:
        parts = rel.split('\\')
        if len(parts) >= 2:
            sub = parts[1]
        else:
            sub = '(racine)'
        subs[sub][0] += 1
        subs[sub][1] += (sz or 0)
    for sub in sorted(subs.keys(), key=lambda s: -subs[s][1]):
        cnt, sz = subs[sub]
        if cnt > 2 or sz > 100_000:
            print(f"    {sub:<50} {cnt:>5} fich  {sz/1024**3:>6.2f} Go")

conn.close()
