"""Analyse du dossier 34-controle voussoirs SMP4 (91798 fich, 69.62 Go)."""
import sqlite3
from datetime import datetime
from collections import defaultdict

DB = r'inventaires/inventaire_34-controle voussoirs SMP4.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Dossiers L1
print("=" * 100)
print("34-controle voussoirs SMP4 — Structure L1")
print("=" * 100)

def ts(t):
    try: return datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d')
    except: return '?'

c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as folder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY folder ORDER BY SUM(size) DESC""", (BASE, BASE, BASE, BASE, BASE))

print(f"  {'Dossier':<60} {'Fich':>6} {'Go':>8} {'De':>12} {'À':>12}")
print("  " + "-" * 100)
folders = []
for r in c.fetchall():
    folders.append((r[0], r[1], r[2]))
    print(f"  {r[0]:<60} {r[1]:>6} {r[2]:>8} {ts(r[3]):>12} {ts(r[4]):>12}")

# 2. Extensions globales
print(f"\n{'=' * 100}")
print("EXTENSIONS (top 20)")
print("=" * 100)
c.execute("""SELECT extension, COUNT(*), ROUND(SUM(size)/1073741824.0, 2)
FROM files GROUP BY extension ORDER BY SUM(size) DESC LIMIT 20""")
for ext, cnt, go in c.fetchall():
    print(f"  .{ext or '(sans)':<12} {cnt:>8} fich  {go:>8} Go")

# 3. Doublons globaux
print(f"\n{'=' * 100}")
print("DOUBLONS (par hash MD5)")
print("=" * 100)
c.execute("""SELECT hash_md5, COUNT(*) as cnt, SUM(size) as total_size
FROM files WHERE hash_md5 IS NOT NULL
GROUP BY hash_md5 HAVING cnt > 1
ORDER BY total_size DESC""")
dupes = c.fetchall()
total_dupe_files = sum(cnt - 1 for _, cnt, _ in dupes)
total_dupe_size = sum(sz * (cnt - 1) / cnt for _, cnt, sz in dupes)
total_dupe_groups = len(dupes)

print(f"  Groupes de doublons: {total_dupe_groups}")
print(f"  Fichiers en double: {total_dupe_files}")
print(f"  Espace récupérable: {total_dupe_size/1073741824:.1f} Go")

# Top 10 doublons par taille
print(f"\n  Top 10 doublons les plus lourds:")
c.execute("""SELECT hash_md5, COUNT(*) as cnt, SUM(size) as total_size, 
    MIN(filename) as example_name, MIN(size) as unit_size
FROM files WHERE hash_md5 IS NOT NULL
GROUP BY hash_md5 HAVING cnt > 1
ORDER BY total_size DESC LIMIT 10""")
for h, cnt, total, name, unit in c.fetchall():
    print(f"    {name:<50} x{cnt}  {unit/1048576:.1f} Mo chacun")

# 4. Doublons par dossier L1
print(f"\n{'=' * 100}")
print("DOUBLONS PAR DOSSIER L1 (fichiers dont le hash existe dans un autre dossier L1)")
print("=" * 100)

# Construire un index hash → dossiers L1
c.execute("SELECT path, hash_md5, size FROM files WHERE hash_md5 IS NOT NULL")
hash_to_folders = defaultdict(set)
hash_to_size = {}
for path, h, sz in c.fetchall():
    rel = path[len(BASE):]
    folder = rel.split('\\')[0]
    hash_to_folders[h].add(folder)
    hash_to_size[h] = sz

# Pour chaque dossier L1, compter combien de fichiers sont dupliqués dans un autre L1
folder_stats = defaultdict(lambda: {'total': 0, 'hashed': 0, 'duped_cross': 0, 'duped_size': 0})
c.execute("SELECT path, hash_md5, size FROM files")
for path, h, sz in c.fetchall():
    rel = path[len(BASE):]
    folder = rel.split('\\')[0]
    folder_stats[folder]['total'] += 1
    if h:
        folder_stats[folder]['hashed'] += 1
        if len(hash_to_folders.get(h, set())) > 1:
            folder_stats[folder]['duped_cross'] += 1
            folder_stats[folder]['duped_size'] += sz

print(f"  {'Dossier':<55} {'Total':>6} {'Dupes':>6} {'%':>5} {'Go dupes':>8}")
print("  " + "-" * 85)
for folder in sorted(folder_stats.keys(), key=lambda f: -folder_stats[f]['duped_size']):
    s = folder_stats[folder]
    pct = s['duped_cross'] * 100 // s['hashed'] if s['hashed'] else 0
    go = s['duped_size'] / 1073741824
    if s['duped_cross'] > 0:
        print(f"  {folder:<55} {s['total']:>6} {s['duped_cross']:>6} {pct:>4}% {go:>7.2f}")

# 5. Paires de dossiers L1 avec le plus d'overlap
print(f"\n{'=' * 100}")
print("OVERLAPS ENTRE DOSSIERS L1 (top 15 paires)")
print("=" * 100)

folder_hashes = defaultdict(set)
folder_ns = defaultdict(set)
folder_sizes = defaultdict(int)
c.execute("SELECT path, filename, size, hash_md5 FROM files")
for path, fn, sz, h in c.fetchall():
    rel = path[len(BASE):]
    folder = rel.split('\\')[0]
    if h:
        folder_hashes[folder].add(h)
    folder_ns[folder].add((fn, sz))
    folder_sizes[folder] += sz

all_folders = list(folder_hashes.keys())
overlaps = []
for i in range(len(all_folders)):
    for j in range(i+1, len(all_folders)):
        a, b = all_folders[i], all_folders[j]
        common = folder_hashes[a] & folder_hashes[b]
        if common:
            common_size = sum(hash_to_size.get(h, 0) for h in common)
            overlaps.append((a, b, len(common), common_size))

overlaps.sort(key=lambda x: -x[3])
for a, b, cnt, sz in overlaps[:15]:
    print(f"  {a:<35} ↔ {b:<35} {cnt:>5} fich  {sz/1073741824:.2f} Go")

conn.close()
