import sqlite3
from collections import defaultdict

c = sqlite3.connect('reports/inventory_chambon37.db')
ROOT = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON' + '\\'

def hs(n):
    if not n: n = 0
    for u in ['o', 'Ko', 'Mo', 'Go']:
        if n < 1024: return f'{n:.1f} {u}'
        n /= 1024
    return f'{n:.1f} Go'

print('=== CHEMINS EXACTS .PTS et .ZFS (triés par taille) ===')
rows = c.execute(
    "SELECT path, size FROM files WHERE extension IN ('.pts','.zfs','.PTS','.ZFS') ORDER BY size DESC"
).fetchall()

for path, sz in rows:
    rel = path[len(ROOT):]
    print(f'  {hs(sz):>9}  {rel}')

print(f'\nTotal : {len(rows)} fichiers')
c.close()
