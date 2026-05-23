import sqlite3, os

DB   = r'inventaires/inventaire_09-BARRAGES RENAISON.db'
OLD  = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\12-BARRAGE RENAISON\renaison_canal_evacuateur'
conn = sqlite3.connect(DB)
c    = conn.cursor()

# Tous les fichiers sous scan\renaison 20150401 et 02-SCANS\ avec leur hash
c.execute("""
SELECT path, filename, size, hash_md5
FROM files
WHERE (path LIKE ? OR path LIKE ?)
AND filename LIKE '%.PTS'
ORDER BY filename
""", (OLD + r'\scan\%', OLD + r'\02-SCANS\%'))

rows = c.fetchall()
conn.close()

# Indexer par filename
from collections import defaultdict
by_name = defaultdict(list)
for p, fn, sz, h in rows:
    loc = 'scan' if r'\scan\\' in p.lower() or r'\scan/' in p or '\\scan\\' in p or '/scan/' in p else '02-SCANS'
    # Detect which folder
    if '\\scan\\' in p or '/scan/' in p:
        loc = 'scan'
    elif '02-SCANS' in p or '02-scans' in p.lower():
        loc = '02-SCANS'
    by_name[fn].append((loc, sz, h, p))

print(f"{'Fichier':<55} {'scan hash':<10} {'02-SCANS hash':<10} {'Dupl?'}")
print('-'*90)
match = 0
diff  = 0
only_scan = 0
only_02 = 0
for fn in sorted(by_name):
    entries = by_name[fn]
    s_hash  = next((h for loc,sz,h,p in entries if loc=='scan'),    None)
    o_hash  = next((h for loc,sz,h,p in entries if loc=='02-SCANS'), None)
    if s_hash and o_hash:
        dupl = 'OUI' if s_hash == o_hash else 'NON (diff)'
        if s_hash == o_hash:
            match += 1
        else:
            diff += 1
    elif s_hash:
        dupl = 'scan seul'
        only_scan += 1
    else:
        dupl = '02-SCANS seul'
        only_02 += 1
    print(f"{fn:<55} {(s_hash or 'N/A')[:8]:<10} {(o_hash or 'N/A')[:8]:<10} {dupl}")

print()
print(f"RÉSUMÉ: {match} doublons exacts, {diff} différents, {only_scan} scan-seul, {only_02} 02-SCANS-seul")
