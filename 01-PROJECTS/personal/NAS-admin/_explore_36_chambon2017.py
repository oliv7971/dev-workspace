"""Compare CHAMBON 2017 (dans 36) avec Phase 03."""
import os, sqlite3
from collections import defaultdict

DB = 'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Fichiers de 36/CHAMBON 2017 dans la DB
cur.execute("SELECT path, size, hash_md5, filename FROM files WHERE path LIKE '%36-TUNNEL GRAND CHAMBON%CHAMBON 2017%'")
chambon2017 = cur.fetchall()
print(f'36/.../CHAMBON 2017: {len(chambon2017)} fichiers')

# Fichiers de 03-PHASE 03
cur.execute("SELECT path, size, hash_md5, filename FROM files WHERE path LIKE '%03-PHASE 03%'")
phase03 = cur.fetchall()
print(f'03-PHASE 03: {len(phase03)} fichiers')

# Index phase03 par hash
ph3_hash = {}
ph3_name_size = defaultdict(list)
for p, sz, h, fn in phase03:
    if h:
        ph3_hash[h] = p
    ph3_name_size[(fn.lower(), sz)].append(p)

# Comparer
found_h = 0
found_ns = 0
unique = []
found_size = 0
unique_size = 0
for p, sz, h, fn in chambon2017:
    rel = p.split('CHAMBON 2017\\', 1)[-1] if 'CHAMBON 2017\\' in p else p
    if h and h in ph3_hash:
        found_h += 1
        found_size += sz
    elif (fn.lower(), sz) in ph3_name_size:
        found_ns += 1
        found_size += sz
    else:
        unique.append((rel, sz))
        unique_size += sz

total = len(chambon2017)
print(f'\n--- CHAMBON 2017 vs Phase 03 ---')
print(f'Doublons hash:       {found_h:>5} ({found_h*100/max(total,1):.0f}%)')
print(f'Doublons nom+size:   {found_ns:>5} ({found_ns*100/max(total,1):.0f}%)')
print(f'Uniques:             {len(unique):>5} ({len(unique)*100/max(total,1):.0f}%)  {unique_size/1048576:.1f} Mo')
print(f'Taille doublons:     {found_size/1048576:.1f} Mo')

if unique:
    print(f'\n--- Uniques (top 30) ---')
    unique.sort(key=lambda x: -x[1])
    for rel, sz in unique[:30]:
        if sz > 1048576: s = f'{sz/1048576:.0f} Mo'
        elif sz > 1024: s = f'{sz/1024:.0f} Ko'
        else: s = f'{sz} o'
        print(f'  {s:>8}  {rel}')
    if len(unique) > 30:
        print(f'  ... et {len(unique)-30} autres')

    # Grouper par sous-dossier
    print(f'\n--- Uniques par sous-dossier ---')
    by_dir = defaultdict(lambda: [0, 0])
    for rel, sz in unique:
        parts = rel.split(os.sep)
        top = parts[0] if len(parts) > 1 else '(racine)'
        by_dir[top][0] += 1
        by_dir[top][1] += sz
    for d, (cnt, s) in sorted(by_dir.items(), key=lambda x: -x[1][1]):
        if s > 1048576: ss = f'{s/1048576:.0f} Mo'
        else: ss = f'{s/1024:.0f} Ko'
        print(f'  {d:50s} {cnt:>5} fich  {ss:>8}')

# Lister L1 de Phase 03
print(f'\n--- Contenu de 03-PHASE 03 (L1 live) ---')
base_ph3 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON\03-PHASE 03 - interchantier 2017'
if os.path.exists(base_ph3):
    for name in sorted(os.listdir(base_ph3)):
        pp = os.path.join(base_ph3, name)
        if os.path.isdir(pp):
            try:
                count = sum(len(files) for _, _, files in os.walk(pp))
                size = sum(os.path.getsize(os.path.join(d,f)) for d,_,files in os.walk(pp) for f in files)
                if size > 1048576: s = f'{size/1048576:.0f} Mo'
                else: s = f'{size/1024:.0f} Ko'
                print(f'  {name:55s} {count:>5} fich  {s:>8}')
            except Exception as e:
                print(f'  {name:55s} ERREUR: {e}')
        else:
            print(f'  [F] {name}')
else:
    print('  Dossier introuvable!')

# Aussi: le reste de 36 (hors CHAMBON 2017) - combien de doublons vs tout 37?
print(f'\n--- Reste de 36 (hors CHAMBON 2017) ---')
cur.execute("SELECT path, size, hash_md5, filename FROM files WHERE path LIKE '%36-TUNNEL GRAND CHAMBON%' AND path NOT LIKE '%CHAMBON 2017%'")
reste_36 = cur.fetchall()
print(f'Fichiers: {len(reste_36)}')

# Index de tout 37 hors 36
cur.execute("SELECT hash_md5 FROM files WHERE path NOT LIKE '%36-TUNNEL GRAND CHAMBON%' AND hash_md5 IS NOT NULL")
all_hashes_37 = set(row[0] for row in cur.fetchall())

r_dup = 0
r_uniq = 0
r_dup_sz = 0
r_uniq_sz = 0
r_unique_list = []
for p, sz, h, fn in reste_36:
    if h and h in all_hashes_37:
        r_dup += 1
        r_dup_sz += sz
    else:
        r_uniq += 1
        r_uniq_sz += sz
        rel = p.split('36-TUNNEL GRAND CHAMBON\\', 1)[-1] if '36-TUNNEL GRAND CHAMBON\\' in p else p
        r_unique_list.append((rel, sz))

rt = len(reste_36)
print(f'Doublons: {r_dup} ({r_dup*100/max(rt,1):.0f}%)  {r_dup_sz/1048576:.1f} Mo')
print(f'Uniques:  {r_uniq} ({r_uniq*100/max(rt,1):.0f}%)  {r_uniq_sz/1048576:.1f} Mo')
if r_unique_list:
    r_unique_list.sort(key=lambda x: -x[1])
    print('Top uniques:')
    for rel, sz in r_unique_list[:15]:
        if sz > 1024: s = f'{sz/1024:.0f} Ko'
        else: s = f'{sz} o'
        print(f'  {s:>8}  {rel}')

conn.close()
