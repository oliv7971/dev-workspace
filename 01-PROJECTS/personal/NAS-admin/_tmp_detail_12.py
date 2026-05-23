"""Explore en détail le contenu de RENAISON 2015/00-DONNEES-BRUTES-CANAL
(anciennement 12-BARRAGE RENAISON)."""
import sqlite3, datetime
from collections import defaultdict

conn = sqlite3.connect(r'inventaires/inventaire_09-BARRAGES RENAISON.db')
c = conn.cursor()

# Le dossier s'appelait encore 12-BARRAGE RENAISON au moment du scan
BASE_OLD = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\12-BARRAGE RENAISON'

c.execute('SELECT path, filename, size, extension, modified_time FROM files WHERE path LIKE ?',
          (BASE_OLD + r'\%',))
rows = c.fetchall()

print(f'Total : {len(rows)} fichiers dans 12-BARRAGE RENAISON')
print()

# Niveau 2 avec dates min/max
pfx = BASE_OLD + '\\'
subs = defaultdict(lambda: [0, 0, None, None])
for p, fn, sz, ext, mt in rows:
    rel = p[len(pfx):]
    parts = rel.split('\\')
    k = parts[0] if parts else '(racine)'
    subs[k][0] += 1
    subs[k][1] += (sz or 0)
    if mt:
        if subs[k][2] is None or mt < subs[k][2]: subs[k][2] = mt
        if subs[k][3] is None or mt > subs[k][3]: subs[k][3] = mt

print(f'{"Dossier":50s}  {"Nb":>5}  {"Taille":>10}  {"Date min":>12}  {"Date max":>12}')
print('-' * 100)
for k, (n, s, tmin, tmax) in sorted(subs.items(), key=lambda x: -x[1][1]):
    dmin = datetime.datetime.fromtimestamp(tmin).strftime('%Y-%m-%d') if tmin else '?'
    dmax = datetime.datetime.fromtimestamp(tmax).strftime('%Y-%m-%d') if tmax else '?'
    print(f'{k:50s}  {n:5d}  {s/1e6:9.1f} Mo  {dmin:>12}  {dmax:>12}')

print()

# Zoom sur renaison_canal_evacuateur niveau 3
pfx2 = BASE_OLD + r'\renaison_canal_evacuateur' + '\\'
c.execute('SELECT path, filename, size, extension, modified_time FROM files WHERE path LIKE ?',
          (pfx2 + '%',))
rows2 = c.fetchall()
subs2 = defaultdict(lambda: [0, 0, None, None])
for p, fn, sz, ext, mt in rows2:
    rel = p[len(pfx2):]
    k = rel.split('\\')[0]
    subs2[k][0] += 1
    subs2[k][1] += (sz or 0)
    if mt:
        if subs2[k][2] is None or mt < subs2[k][2]: subs2[k][2] = mt
        if subs2[k][3] is None or mt > subs2[k][3]: subs2[k][3] = mt

print(f'  renaison_canal_evacuateur — détail niveau 3 :')
print(f'  {"Sous-dossier":50s}  {"Nb":>5}  {"Taille":>10}  {"Date min":>12}  {"Date max":>12}')
print('  ' + '-' * 96)
for k, (n, s, tmin, tmax) in sorted(subs2.items(), key=lambda x: -x[1][1]):
    dmin = datetime.datetime.fromtimestamp(tmin).strftime('%Y-%m-%d') if tmin else '?'
    dmax = datetime.datetime.fromtimestamp(tmax).strftime('%Y-%m-%d') if tmax else '?'
    print(f'  {k:50s}  {n:5d}  {s/1e6:9.1f} Mo  {dmin:>12}  {dmax:>12}')

print()

# Extensions dominantes dans 02-SCANS et scan
for sous in ['02-SCANS', 'scan']:
    pfx3 = pfx2 + sous + '\\'
    c.execute('SELECT extension, COUNT(*), SUM(size) FROM files WHERE path LIKE ? GROUP BY extension ORDER BY SUM(size) DESC LIMIT 10',
              (pfx3 + '%',))
    print(f'  Extensions dans renaison_canal_evacuateur/{sous} :')
    for ext, n, s in c.fetchall():
        print(f'    {ext or "(sans)":15s}  {n:4d} f  {(s or 0)/1e6:8.1f} Mo')
    print()

# Les 2 petits dossiers "parties"
for d in ['renaison-canal-partie1-seule', 'renaison-canal-partie2-seule']:
    pfx4 = BASE_OLD + '\\' + d + '\\'
    c.execute('SELECT filename, size, extension, modified_time FROM files WHERE path LIKE ?', (pfx4 + '%',))
    rows4 = c.fetchall()
    print(f'  {d} ({len(rows4)} fichiers) :')
    for fn, sz, ext, mt in rows4[:10]:
        dmt = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d') if mt else '?'
        print(f'    {fn:50s}  {(sz or 0)/1e6:6.2f} Mo  {ext:8s}  {dmt}')
    print()

conn.close()
