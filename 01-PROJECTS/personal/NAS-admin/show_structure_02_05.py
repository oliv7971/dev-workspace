import sqlite3, os
from collections import defaultdict

DOSSIERS = [
    ("02-STRASBOURG ETOILE", r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\02-STRASBOURG ETOILE' + '\\'),
    ("03-BALESMES",          r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\03-BALESMES' + '\\'),
    ("04-TUNNEL MONTETS",    r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\04-TUNNEL MONTETS' + '\\'),
    ("05-CROIX ROUSSE",      r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\05-CROIX ROUSSE' + '\\'),
]

DB_DIR = os.path.abspath('inventaires')

for nom, base in DOSSIERS:
    db_path = os.path.join(DB_DIR, f'inventaire_{nom}.db')
    conn = sqlite3.connect(db_path)
    rows = conn.execute('SELECT path, size FROM files').fetchall()
    dossiers = defaultdict(lambda: [0, 0])
    for path, size in rows:
        rel = path[len(base):]
        top = rel.split('\\')[0]
        dossiers[top][0] += 1
        dossiers[top][1] += size
    print(f"\n{'='*60}")
    print(f"  {nom}")
    print(f"{'='*60}")
    for d, (nb, sz) in sorted(dossiers.items(), key=lambda x: -x[1][1]):
        print(f"  {sz/1024**3:7.2f} Go  {nb:6} fichiers  {d}")
    conn.close()
