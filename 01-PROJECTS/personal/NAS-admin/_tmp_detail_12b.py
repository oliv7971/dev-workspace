"""Zoome sur les anomalies dans 00-DONNEES-BRUTES-CANAL (ex-12-BARRAGE RENAISON)."""
import sqlite3, datetime
from collections import defaultdict

conn = sqlite3.connect(r'inventaires/inventaire_09-BARRAGES RENAISON.db')
c = conn.cursor()
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\12-BARRAGE RENAISON\renaison_canal_evacuateur'

# 1) 10-TRUVIEW : dates et structure — d'où viennent les fichiers 2012 ?
pfx = BASE + r'\10-TRUVIEW' + '\\'
c.execute('SELECT path, filename, size, extension, modified_time FROM files WHERE path LIKE ? ORDER BY modified_time',
          (pfx + '%',))
rows = c.fetchall()
print(f'=== 10-TRUVIEW : {len(rows)} fichiers ===')
# Regrouper par sous-dossier et plage de dates
subs = defaultdict(lambda: [0, 0, None, None])
for p, fn, sz, ext, mt in rows:
    rel = p[len(pfx):]
    k = rel.split('\\')[0]
    subs[k][0] += 1; subs[k][1] += (sz or 0)
    if mt:
        if subs[k][2] is None or mt < subs[k][2]: subs[k][2] = mt
        if subs[k][3] is None or mt > subs[k][3]: subs[k][3] = mt

for k, (n, s, tmin, tmax) in sorted(subs.items(), key=lambda x: -x[1][1])[:20]:
    dmin = datetime.datetime.fromtimestamp(tmin).strftime('%Y-%m-%d') if tmin else '?'
    dmax = datetime.datetime.fromtimestamp(tmax).strftime('%Y-%m-%d') if tmax else '?'
    print(f'  {k:55s}  {n:4d} f  {s/1e6:7.1f} Mo  {dmin} → {dmax}')

# Quelques noms de fichiers anciens (2012)
print('\n  Fichiers les plus anciens :')
c.execute('SELECT filename, size, modified_time, path FROM files WHERE path LIKE ? ORDER BY modified_time LIMIT 10',
          (pfx + '%',))
for fn, sz, mt, p in c.fetchall():
    d = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d') if mt else '?'
    # chemin relatif court
    rel = p[len(pfx):]
    print(f'  {d}  {rel[:80]}')

print()

# 2) Fichiers "bassinCentral" éparpillés DANS renaison_canal_evacuateur
print('=== Fichiers bassinCentral dans renaison_canal_evacuateur ===')
c.execute('SELECT path, filename, size, modified_time FROM files WHERE path LIKE ? AND filename LIKE ?',
          (BASE + r'\%', '%bassinCentral%'))
for p, fn, sz, mt in c.fetchall():
    d = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d') if mt else '?'
    rel = p[len(BASE)+1:]
    print(f'  {d}  {rel[:90]}')

print()

# 3) Comparer "02-SCANS" vs "scan" : sont-ils distincts ou redondants ?
print('=== Comparaison 02-SCANS vs scan ===')
for d in ['02-SCANS', 'scan']:
    pfxd = BASE + '\\' + d + '\\'
    c.execute('SELECT filename, size, modified_time FROM files WHERE path LIKE ? ORDER BY size DESC LIMIT 8',
              (pfxd + '%',))
    rows_d = c.fetchall()
    print(f'  {d} (top 8 par taille) :')
    for fn, sz, mt in rows_d:
        dt = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d') if mt else '?'
        print(f'    {fn:50s}  {(sz or 0)/1e6:8.1f} Mo  {dt}')
    print()

conn.close()
