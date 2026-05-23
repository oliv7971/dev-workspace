import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Base commune
c.execute("SELECT MIN(path) FROM files")
sample = c.fetchone()[0]
# Reconstruct base
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'

# Stats globales
c.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files")
total, total_sz = c.fetchone()
c.execute("SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''")
hashed = c.fetchone()[0]
print(f"Total : {total} fichiers, {total_sz/1024**3:.1f} Go")
print(f"Hash MD5 : {hashed}/{total} ({100*hashed//max(total,1)}%)")

# ── 1) Dossiers 1er niveau ──────────────────────────────────────────────
c.execute("SELECT path, size FROM files")
level1 = defaultdict(lambda: [0, 0])
for path, size in c.fetchall():
    rel = path.replace(BASE, '').lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine)'
    level1[top][0] += 1
    level1[top][1] += (size or 0)

print(f"\n{'Dossier 1er niveau':<65} {'Fich':>7} {'Go':>7}")
print('=' * 83)
for d in sorted(level1.keys(), key=lambda x: -level1[x][1]):
    cnt, sz = level1[d]
    print(f"  {d:<63} {cnt:>7} {sz/1024**3:>6.1f}")

# ── 2) Extensions dominantes ────────────────────────────────────────────
c.execute("""
    SELECT LOWER(extension), COUNT(*), COALESCE(SUM(size),0)
    FROM files GROUP BY LOWER(extension)
    ORDER BY SUM(size) DESC LIMIT 15
""")
print(f"\n{'Extension':<15} {'Fich':>8} {'Go':>8}")
print('-' * 35)
for ext, cnt, sz in c.fetchall():
    print(f"  {ext or '(sans)':<13} {cnt:>8} {sz/1024**3:>7.2f}")

# ── 3) Doublons par hash MD5 ────────────────────────────────────────────
c.execute("""
    SELECT hash_md5, COUNT(*) as cnt
    FROM files
    WHERE hash_md5 IS NOT NULL AND hash_md5 != ''
    GROUP BY hash_md5
    HAVING COUNT(*) > 1
""")
dupes = c.fetchall()
# Pour chaque hash dupliqué, calculer la taille récupérable
total_dupe_files = 0
total_dupe_size = 0
for h, cnt in dupes:
    c.execute("SELECT size FROM files WHERE hash_md5 = ? LIMIT 1", (h,))
    sz = c.fetchone()[0] or 0
    total_dupe_files += (cnt - 1)
    total_dupe_size += sz * (cnt - 1)

print(f"\n=== Doublons MD5 (fichiers identiques) ===")
print(f"  {len(dupes)} hashes dupliqués")
print(f"  {total_dupe_files} fichiers en surplus")
print(f"  {total_dupe_size/1024**3:.1f} Go récupérables")

# ── 4) Fichiers même nom mais hash différent ────────────────────────────
c.execute("""
    SELECT filename, COUNT(DISTINCT hash_md5) as n_versions, COUNT(*) as n_copies
    FROM files
    WHERE hash_md5 IS NOT NULL AND hash_md5 != ''
    GROUP BY filename
    HAVING COUNT(DISTINCT hash_md5) > 1
    ORDER BY COUNT(*) DESC
""")
same_name_diff = c.fetchall()
print(f"\n=== Fichiers même nom, contenu DIFFÉRENT ===")
print(f"  {len(same_name_diff)} noms de fichiers avec plusieurs versions")
# Top 20
print(f"\n  {'Fichier':<50} {'Versions':>9} {'Copies':>7}")
print('  ' + '-' * 70)
for fn, nv, nc in same_name_diff[:30]:
    print(f"  {fn:<50} {nv:>9} {nc:>7}")

# ── 5) Doublons par nom+taille (pour fichiers sans hash) ────────────────
c.execute("""
    SELECT filename, size, COUNT(*) as cnt
    FROM files
    WHERE (hash_md5 IS NULL OR hash_md5 = '')
    GROUP BY filename, size
    HAVING COUNT(*) > 1
    ORDER BY size * COUNT(*) DESC
    LIMIT 20
""")
no_hash_dupes = c.fetchall()
if no_hash_dupes:
    print(f"\n=== Doublons probables SANS hash (même nom + taille) ===")
    for fn, sz, cnt in no_hash_dupes:
        print(f"  {fn:<50} {sz//1024:>8} Ko × {cnt}")

conn.close()
