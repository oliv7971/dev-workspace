"""Exploration de 37-TUNNEL GRAND CHAMBON.
Structure, tailles, extensions, doublons."""
import sqlite3
import os
from collections import defaultdict

DB = r'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Stats generales
c.execute("SELECT COUNT(*), SUM(size), COUNT(DISTINCT hash_md5) FROM files")
total_files, total_size, unique_hashes = c.fetchone()
c.execute("SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''")
hashed = c.fetchone()[0]
print("=" * 100)
print("37-TUNNEL GRAND CHAMBON - Vue d'ensemble")
print("=" * 100)
print(f"Fichiers: {total_files:,}")
print(f"Taille totale: {total_size/1073741824:.2f} Go")
print(f"Hashes: {hashed:,} / {total_files:,} ({hashed*100//total_files}%)")
print(f"Hashes uniques: {unique_hashes:,}")

# Structure L1
print(f"\n{'=' * 100}")
print("STRUCTURE NIVEAU 1")
print("=" * 100)

# Extraire les sous-dossiers L1
base_len = len(BASE) + 1
c.execute("SELECT path, filename, size FROM files")
all_files = c.fetchall()

l1_stats = defaultdict(lambda: [0, 0])  # count, size
root_files = []

for path, filename, size in all_files:
    rel = path[base_len:] if path.startswith(BASE + '\\') else path[base_len:]
    # Enlever le filename de la fin du path si present
    if rel.endswith(filename):
        rel = rel[:-len(filename)].rstrip('\\')
    
    if not rel or rel == '':
        root_files.append((filename, size))
    else:
        l1 = rel.split('\\')[0]
        l1_stats[l1][0] += 1
        l1_stats[l1][1] += size

# Trier par taille
for name, (cnt, sz) in sorted(l1_stats.items(), key=lambda x: -x[1][1]):
    sz_str = f"{sz/1073741824:.2f} Go" if sz > 1073741824 else f"{sz/1048576:.0f} Mo"
    print(f"  {name:60s} {cnt:>6} fich  {sz_str:>10}")

if root_files:
    print(f"\n  Fichiers a la racine: {len(root_files)}")
    for fn, sz in sorted(root_files, key=lambda x: -x[1])[:10]:
        print(f"    {fn} ({sz:,} bytes)")

# Structure L2 pour les gros dossiers
print(f"\n{'=' * 100}")
print("STRUCTURE NIVEAU 2 (dossiers > 500 Mo)")
print("=" * 100)

big_l1 = [name for name, (cnt, sz) in l1_stats.items() if sz > 524288000]
for l1_name in sorted(big_l1, key=lambda x: -l1_stats[x][1]):
    print(f"\n  {l1_name}/ ({l1_stats[l1_name][1]/1073741824:.2f} Go, {l1_stats[l1_name][0]} fich)")
    
    l2_stats = defaultdict(lambda: [0, 0])
    l1_root = []
    
    for path, filename, size in all_files:
        rel = path[base_len:] if path.startswith(BASE + '\\') else path[base_len:]
        if rel.endswith(filename):
            rel = rel[:-len(filename)].rstrip('\\')
        
        parts = rel.split('\\') if rel else []
        if len(parts) >= 1 and parts[0] == l1_name:
            if len(parts) >= 2:
                l2_stats[parts[1]][0] += 1
                l2_stats[parts[1]][1] += size
            else:
                l1_root.append((filename, size))
    
    for name, (cnt, sz) in sorted(l2_stats.items(), key=lambda x: -x[1][1]):
        sz_str = f"{sz/1073741824:.2f} Go" if sz > 1073741824 else f"{sz/1048576:.0f} Mo"
        print(f"    {name:55s} {cnt:>6} fich  {sz_str:>10}")
    
    if l1_root:
        total_root_sz = sum(s for _, s in l1_root)
        print(f"    (fichiers racine: {len(l1_root)}, {total_root_sz/1048576:.0f} Mo)")

# Extensions
print(f"\n{'=' * 100}")
print("EXTENSIONS (par taille)")
print("=" * 100)
c.execute("""SELECT LOWER(extension) as ext, COUNT(*), SUM(size) 
FROM files GROUP BY ext ORDER BY SUM(size) DESC LIMIT 20""")
for ext, cnt, sz in c.fetchall():
    ext = ext if ext else '(no ext)'
    sz_str = f"{sz/1073741824:.2f} Go" if sz > 1073741824 else f"{sz/1048576:.0f} Mo"
    print(f"  {ext:<15} {cnt:>6} fich  {sz_str:>10}")

# Doublons par hash
print(f"\n{'=' * 100}")
print("DOUBLONS (par hash MD5)")
print("=" * 100)
c.execute("""SELECT hash_md5, COUNT(*) as cnt, SUM(size) as total_sz, 
MIN(size) as unit_sz, GROUP_CONCAT(filename, ' | ') 
FROM files 
WHERE hash_md5 IS NOT NULL AND hash_md5 != ''
GROUP BY hash_md5 HAVING cnt > 1 
ORDER BY total_sz DESC LIMIT 20""")
groups = c.fetchall()

c.execute("""SELECT COUNT(*), SUM(sz) FROM (
    SELECT hash_md5, (COUNT(*)-1) * MIN(size) as sz 
    FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''
    GROUP BY hash_md5 HAVING COUNT(*) > 1
)""")
dup_groups, dup_recoverable = c.fetchone()
print(f"Groupes de doublons: {dup_groups:,}")
print(f"Espace recuperable: {(dup_recoverable or 0)/1073741824:.2f} Go")

print(f"\nTop 20 groupes:")
for h, cnt, total_sz, unit_sz, names in groups:
    name_list = names[:80]
    print(f"  {cnt}x {unit_sz/1048576:.1f} Mo  {name_list}")

# Chevauchements entre L1
print(f"\n{'=' * 100}")
print("CHEVAUCHEMENTS ENTRE DOSSIERS L1 (par hash)")
print("=" * 100)

# Build hash -> L1 folders mapping
hash_to_l1 = defaultdict(set)
c.execute("SELECT path, hash_md5 FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''")
for path, h in c.fetchall():
    rel = path[base_len:] if path.startswith(BASE + '\\') else path[base_len:]
    parts = rel.split('\\')
    if parts:
        hash_to_l1[h].add(parts[0])

# Count overlaps between pairs
from itertools import combinations
pair_overlaps = defaultdict(int)
for h, folders in hash_to_l1.items():
    if len(folders) > 1:
        for a, b in combinations(sorted(folders), 2):
            pair_overlaps[(a, b)] += 1

if pair_overlaps:
    for (a, b), cnt in sorted(pair_overlaps.items(), key=lambda x: -x[1])[:15]:
        print(f"  {a} <-> {b}: {cnt} fichiers en commun")
else:
    print("  Aucun chevauchement detecte")

# Archives
print(f"\n{'=' * 100}")
print("ARCHIVES (.zip, .7z, .rar)")
print("=" * 100)
c.execute("""SELECT filename, size FROM files 
WHERE extension IN ('.7z', '.zip', '.rar') ORDER BY size DESC""")
archives = c.fetchall()
if archives:
    total_arch = sum(s for _, s in archives)
    print(f"{len(archives)} archives, {total_arch/1073741824:.2f} Go")
    for fn, sz in archives[:15]:
        sz_str = f"{sz/1073741824:.2f} Go" if sz > 1073741824 else f"{sz/1048576:.0f} Mo"
        print(f"  {fn:60s} {sz_str}")
else:
    print("  Aucune archive")

conn.close()
