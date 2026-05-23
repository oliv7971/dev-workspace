import sqlite3, os
from collections import defaultdict

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\46-BPNL' + '\\'
DB = os.path.abspath('inventaires/inventaire_46-BPNL.db')
conn = sqlite3.connect(DB)

# Top 20 doublons
print("=== TOP 20 DOUBLONS ===")
doublons = conn.execute('''
    SELECT hash_md5, COUNT(*) as nb, size, GROUP_CONCAT(path, '|||') as chemins
    FROM files WHERE hash_md5 IS NOT NULL
    GROUP BY hash_md5 HAVING nb > 1
    ORDER BY (nb-1)*size DESC
    LIMIT 20
''').fetchall()
for h, nb, size, chemins in doublons:
    print(f'--- {nb} copies - {size/1024**2:.1f} Mo ---')
    for p in chemins.split('|||'):
        print(f'  {p}')
    print()

# Sous-dossiers racine
print("=== SOUS-DOSSIERS RACINE ===")
rows = conn.execute('SELECT path, size FROM files').fetchall()
dossiers = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(BASE):]
    top = rel.split('\\')[0]
    dossiers[top][0] += 1
    dossiers[top][1] += size
for d, (nb, sz) in sorted(dossiers.items(), key=lambda x: -x[1][1]):
    print(f'{sz/1024**3:7.2f} Go  {nb:6} fichiers  {d}')

conn.close()
