"""Compare le contenu des dossiers _racine vs leurs homologues dans RENAISON 2022."""
import sqlite3, os
from collections import defaultdict

conn = sqlite3.connect(r'inventaires/inventaire_09-BARRAGES RENAISON.db')
c = conn.cursor()
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\RENAISON 2022'

# Paires à comparer
paires = [
    ('SESSION MAI 2022',   'SESSION MAI 2022_racine'),
    ('SESSION JUIN 2022',  'SESSION JUIN 2022_racine'),
    ('CCTP',               'CCTP_racine'),
    ('_recu de FAbrice',   '_recu de FAbrice_racine'),
]

for nom_orig, nom_racine in paires:
    for nom in (nom_orig, nom_racine):
        pfx = BASE + '\\' + nom + '\\'
        c.execute('SELECT filename, size, hash_md5, path FROM files WHERE path LIKE ?', (pfx + '%',))
        rows = c.fetchall()
        print(f'\n  === {nom} ({len(rows)} fichiers) ===')
        # Regrouper par sous-dossier
        subs = defaultdict(list)
        for fn, sz, h, p in rows:
            rel = p[len(pfx):]
            seg = rel.split('\\')[0] if '\\' in rel else '(racine)'
            subs[seg].append((fn, sz, h))
        for seg, files in sorted(subs.items()):
            total = sum(f[1] or 0 for f in files)
            print(f'    [{seg}]  {len(files)} f  {total/1e6:.1f} Mo')
            for fn, sz, h in files[:5]:
                print(f'      {fn:50s} {(sz or 0)/1e6:6.2f} Mo')
            if len(files) > 5:
                print(f'      ... +{len(files)-5} autres')
    print()

conn.close()
