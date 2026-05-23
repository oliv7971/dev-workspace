import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_33-SMP4.db'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Trouver le chemin de base
c.execute("SELECT path FROM files LIMIT 1")
sample = c.fetchone()[0]
print(f"Exemple chemin : {sample}")

# Identifier la base
c.execute("SELECT MIN(path) FROM files")
base_raw = c.fetchone()[0]
# Trouver le préfixe commun
c.execute("SELECT DISTINCT path FROM files LIMIT 100")
paths100 = [r[0] for r in c.fetchall()]
import os
base = os.path.commonpath(paths100) if paths100 else ''
print(f"Base commune : {base}")

# Stats globales
c.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files")
total, total_sz = c.fetchone()
print(f"\nTotal : {total} fichiers, {total_sz/1024**3:.1f} Go")

c.execute("SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''")
hashed = c.fetchone()[0]
print(f"Hash MD5 : {hashed}/{total} ({100*hashed//max(total,1)}%)")

# Extensions
c.execute("""
    SELECT LOWER(extension), COUNT(*), COALESCE(SUM(size),0) 
    FROM files GROUP BY LOWER(extension) 
    ORDER BY SUM(size) DESC LIMIT 20
""")
print(f"\n{'Extension':<15} {'Fichiers':>8} {'Go':>8}")
print('-' * 35)
for ext, cnt, sz in c.fetchall():
    print(f"  {ext or '(sans)':<13} {cnt:>8} {sz/1024**3:>7.2f}")

# Structure 1er et 2e niveau
c.execute("SELECT path, size FROM files")
level1 = defaultdict(lambda: [0, 0])
level2 = defaultdict(lambda: [0, 0])
for path, size in c.fetchall():
    rel = path.replace(base, '').lstrip('\\')
    parts = rel.split('\\')
    if len(parts) >= 1:
        level1[parts[0]][0] += 1
        level1[parts[0]][1] += (size or 0)
    if len(parts) >= 2:
        key = parts[0] + '\\' + parts[1]
        level2[key][0] += 1
        level2[key][1] += (size or 0)

print(f"\n{'Dossier 1er niveau':<55} {'Fich':>7} {'Go':>7}")
print('=' * 73)
for d in sorted(level1.keys()):
    cnt, sz = level1[d]
    print(f"  {d:<53} {cnt:>7} {sz/1024**3:>6.1f}")

print(f"\n{'Dossier 2e niveau':<65} {'Fich':>7} {'Go':>7}")
print('=' * 83)
for d in sorted(level2.keys()):
    cnt, sz = level2[d]
    if cnt > 50 or sz > 100*1024*1024:
        print(f"  {d:<63} {cnt:>7} {sz/1024**3:>6.1f}")

# Doublons internes (hash identiques)
c.execute("""
    SELECT hash_md5, COUNT(*) as cnt, SUM(size) as sz
    FROM files
    WHERE hash_md5 IS NOT NULL AND hash_md5 != ''
    GROUP BY hash_md5
    HAVING COUNT(*) > 1
""")
dupes = c.fetchall()
n_dupe_files = sum(cnt - 1 for _, cnt, _ in dupes)
n_dupe_size = sum((cnt - 1) * (sz // cnt) for _, cnt, sz in dupes)
print(f"\n=== Doublons internes ===")
print(f"  {len(dupes)} hashes dupliqués")
print(f"  {n_dupe_files} fichiers en surplus (copies supplémentaires)")
print(f"  {n_dupe_size/1024**3:.1f} Go récupérables")

# Mots-clés sauvegarde/backup
print(f"\n=== Dossiers sauvegarde/backup ===")
backup_kw = ['sauvegarde', 'backup', 'save', 'copie', 'old', 'archive']
c.execute("SELECT DISTINCT path FROM files")
found = set()
for (p,) in c.fetchall():
    rel = p.replace(base, '').lstrip('\\').lower()
    parts = rel.split('\\')
    for i, part in enumerate(parts):
        if any(kw in part for kw in backup_kw):
            orig = p.replace(base, '').lstrip('\\').split('\\')
            found.add(base + '\\' + '\\'.join(orig[:i+1]))
            break

roots = sorted(found)
filtered = [p for p in roots if not any(p.startswith(o + '\\') for o in roots if o != p)]
for p in sorted(filtered):
    c.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?", (p + '%',))
    cnt, sz = c.fetchone()
    if cnt > 10:
        rel = p.replace(base + '\\', '')
        print(f"  {rel:<65} {cnt:>7} fich  {sz/1024**3:.1f} Go")

conn.close()
