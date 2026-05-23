import sqlite3
from collections import defaultdict

conn = sqlite3.connect(r'inventaires/inventaire_09-BARRAGES RENAISON.db')
c = conn.cursor()
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON'

# 12-BARRAGE RENAISON / renaison_canal_evacuateur
pfx = BASE + r'\12-BARRAGE RENAISON\renaison_canal_evacuateur' + '\\'
c.execute('SELECT path, size, modified_time FROM files WHERE path LIKE ?', (pfx + '%',))
rows = c.fetchall()
subs = defaultdict(lambda: [0, 0, None])
for p, sz, mt in rows:
    rel = p[len(pfx):]
    seg = rel.split('\\')[0]
    subs[seg][0] += 1
    subs[seg][1] += (sz or 0)
    if mt and (subs[seg][2] is None or mt > subs[seg][2]):
        subs[seg][2] = mt

print('=== 12-BARRAGE RENAISON / renaison_canal_evacuateur ===')
for k, (n, s, mt) in sorted(subs.items(), key=lambda x: -x[1][1]):
    print(f'  {k:55s} {n:4d} f  {s/1e6:8.1f} Mo  {mt or ""}')

print()

# SCANS / exports
pfx2 = BASE + r'\SCANS\exports' + '\\'
c.execute('SELECT filename, size, modified_time FROM files WHERE path LIKE ?', (pfx2 + '%',))
print('=== SCANS / exports ===')
for fn, sz, mt in c.fetchall():
    print(f'  {fn:55s} {(sz or 0)/1e9:6.1f} Go  {mt}')

print()

# SCANS / donnees
pfx3 = BASE + r'\SCANS\donnees' + '\\'
c.execute('SELECT filename, size, modified_time FROM files WHERE path LIKE ?', (pfx3 + '%',))
print('=== SCANS / donnees ===')
for fn, sz, mt in c.fetchall():
    print(f'  {fn:55s} {(sz or 0)/1e9:6.1f} Go  {mt}')

print()

# RENAISON 2014 / RENAISON-SCAN / exports : quelques noms de fichiers
pfx4 = BASE + r'\RENAISON 2014\RENAISON-SCAN\exports' + '\\'
c.execute('SELECT filename, size, modified_time FROM files WHERE path LIKE ? ORDER BY size DESC LIMIT 15', (pfx4 + '%',))
print('=== RENAISON 2014 / RENAISON-SCAN / exports (top 15 par taille) ===')
for fn, sz, mt in c.fetchall():
    print(f'  {fn:55s} {(sz or 0)/1e9:6.1f} Go  {mt}')

conn.close()
