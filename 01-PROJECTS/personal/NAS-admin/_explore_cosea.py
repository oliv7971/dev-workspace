import sqlite3, os
from collections import defaultdict

DB = r'inventaires/inventaire_12-COSEA.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\12-COSEA'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Structure de premier niveau
c.execute("SELECT path FROM files")
rows = c.fetchall()

# Extraire les dossiers de 1er et 2e niveau
level1 = defaultdict(lambda: {'count': 0, 'size': 0})
conn2 = sqlite3.connect(DB)
c2 = conn2.cursor()
c2.execute("SELECT path, size FROM files")
for path, size in c2.fetchall():
    # Extraire le dossier de 1er niveau
    rel = path.replace(BASE, '').lstrip('\\').lstrip('/')
    parts = rel.split('\\')
    if len(parts) >= 1:
        top = parts[0]
        level1[top]['count'] += 1
        level1[top]['size'] += (size or 0)

print(f"{'Dossier':<60} {'Fichiers':>8} {'Taille':>10}")
print('=' * 82)
total_files = 0
total_size = 0
for d in sorted(level1.keys()):
    info = level1[d]
    sz_go = info['size'] / 1024 / 1024 / 1024
    print(f"  {d:<58} {info['count']:>8} {sz_go:>9.1f} Go")
    total_files += info['count']
    total_size += info['size']

print('=' * 82)
print(f"  {'TOTAL':<58} {total_files:>8} {total_size/1024/1024/1024:>9.1f} Go")

conn2.close()

# Identifier les dossiers qui ressemblent à des sauvegardes
print("\n\n=== Dossiers potentiellement 'sauvegarde' ===")
c.execute("SELECT DISTINCT path FROM files")
all_paths = [r[0] for r in c.fetchall()]
backup_words = ['sauvegarde', 'sauv', 'backup', 'copie', 'old', 'archive']
backup_dirs = set()
for p in all_paths:
    rel = p.replace(BASE, '').lower()
    for w in backup_words:
        if w in rel:
            parts = p.replace(BASE, '').lstrip('\\').split('\\')
            for i, part in enumerate(parts):
                if w in part.lower():
                    bd = '\\'.join(parts[:i+1])
                    backup_dirs.add(bd)
                    break

for bd in sorted(backup_dirs):
    full = os.path.join(BASE, bd)
    c.execute("SELECT COUNT(*), SUM(size) FROM files WHERE path LIKE ?", (full + '%',))
    cnt, sz = c.fetchone()
    sz_mo = (sz or 0) / 1024 / 1024
    print(f"  {bd:<70} {cnt:>6} fich  {sz_mo:>8.0f} Mo")

conn.close()
