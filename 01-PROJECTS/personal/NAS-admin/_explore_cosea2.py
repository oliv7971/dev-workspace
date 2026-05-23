import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_12-COSEA.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\12-COSEA'

conn = sqlite3.connect(DB)
c = conn.cursor()

# ── 1) Dossiers de 1er niveau ───────────────────────────────────────────
c.execute("SELECT path, size FROM files")
level1 = defaultdict(lambda: [0, 0])
for path, size in c.fetchall():
    rel = path.replace(BASE, '').lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine)'
    level1[top][0] += 1
    level1[top][1] += (size or 0)

print(f"{'Dossier 1er niveau':<50} {'Fichiers':>8} {'Go':>8}")
print('=' * 70)
for d in sorted(level1.keys()):
    cnt, sz = level1[d]
    print(f"  {d:<48} {cnt:>8} {sz/1024**3:>7.1f}")
print()

# ── 2) Gros dossiers de sauvegarde ─────────────────────────────────────
backup_kw = ['sauvegarde', 'sauv', 'backup', 'copie de', 'old', 'archive', 'save']
c.execute("SELECT DISTINCT path FROM files")
all_paths = set()
for (p,) in c.fetchall():
    rel = p.replace(BASE, '').lstrip('\\')
    parts = rel.split('\\')
    for i, part in enumerate(parts):
        if any(kw in part.lower() for kw in backup_kw):
            all_paths.add(BASE + '\\' + '\\'.join(parts[:i+1]))

# Regrouper et mesurer (ne garder que les racines — pas les sous-chemins d'autres)
roots = sorted(all_paths)
# Éliminer les sous-chemins
filtered = []
for p in roots:
    if not any(p.startswith(other + '\\') for other in roots if other != p):
        filtered.append(p)

print(f"{'Dossiers sauvegarde/copie (racines)':<80} {'Fich':>7} {'Go':>7}")
print('=' * 98)
total_bk_files = 0
total_bk_size = 0
for p in sorted(filtered):
    c.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?", (p + '%',))
    cnt, sz = c.fetchone()
    if cnt > 10:  # ignorer dossiers minuscules
        rel = p.replace(BASE + '\\', '')
        total_bk_files += cnt
        total_bk_size += sz
        print(f"  {rel:<78} {cnt:>7} {sz/1024**3:>6.1f}")

print(f"\n  TOTAL sauvegardes/copies (>10 fichiers) : {total_bk_files} fichiers, {total_bk_size/1024**3:.1f} Go")

# ── 3) Combien de hash MD5 disponibles ─────────────────────────────────
c.execute("SELECT COUNT(*) FROM files")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL AND hash_md5 != ''")
hashed = c.fetchone()[0]
print(f"\n  Hash MD5 : {hashed}/{total} ({100*hashed//total}%)")

conn.close()
