"""Analyse rapide de 36-TUNNEL GRAND CHAMBON dans 37, en utilisant l'inventaire DB."""
import os
import sqlite3
import hashlib
from collections import defaultdict

DB_PATH = 'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'
PATH36 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON\36-TUNNEL GRAND CHAMBON'

# 1) Verifier existence
if not os.path.exists(PATH36):
    print('36-TUNNEL GRAND CHAMBON n\'existe PAS dans 37')
    exit()

# 2) Lister L1 de 36
print('=' * 80)
print('CONTENU de 37/.../36-TUNNEL GRAND CHAMBON')
print('=' * 80)
total_files_36 = 0
total_size_36 = 0
for name in sorted(os.listdir(PATH36)):
    p = os.path.join(PATH36, name)
    if os.path.isdir(p):
        try:
            count = sum(len(files) for _, _, files in os.walk(p))
            size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(p) for f in files)
            if size > 1073741824: sz = f'{size/1073741824:.2f} Go'
            elif size > 1048576: sz = f'{size/1048576:.0f} Mo'
            else: sz = f'{size/1024:.0f} Ko'
            print(f'  {name:60s} {count:>6} fich  {sz:>10}')
            total_files_36 += count
            total_size_36 += size
        except Exception as e:
            print(f'  {name:60s} ERREUR: {e}')
    else:
        try:
            sz = os.path.getsize(p)
            print(f'  [F] {name:57s} {sz:>10}')
            total_files_36 += 1
            total_size_36 += sz
        except:
            print(f'  [F] {name:57s} ERREUR')

print(f'\nTotal 36: {total_files_36} fichiers, {total_size_36/1073741824:.2f} Go')

# 3) Utiliser l'inventaire DB pour comparer
print()
print('=' * 80)
print('COMPARAISON avec inventaire DB')
print('=' * 80)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Recuperer les fichiers de 36 depuis la DB
cur.execute("SELECT path, size, hash_md5 FROM files WHERE path LIKE '%36-TUNNEL GRAND CHAMBON%'")
files_36_db = cur.fetchall()
print(f'Fichiers de 36 dans la DB: {len(files_36_db)}')

if not files_36_db:
    print('ATTENTION: 36 n\'est pas dans l\'inventaire DB!')
    print('On va scanner le dossier directement...')
    conn.close()
    
    # Scanner 36 et comparer par nom+taille avec la DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Index de tous les fichiers hors-36 par (nom, taille) 
    cur.execute("SELECT path, size, hash_md5 FROM files WHERE path NOT LIKE '%36-TUNNEL GRAND CHAMBON%'")
    all_other = cur.fetchall()
    
    name_size_idx = defaultdict(list)
    hash_idx = defaultdict(list)
    for p, sz, h in all_other:
        fname = os.path.basename(p).lower()
        name_size_idx[(fname, sz)].append(p)
        if h:
            hash_idx[h].append(p)
    
    print(f'Index construit: {len(all_other)} fichiers dans le reste de 37')
    
    # Scanner 36 en live
    print('Scan live de 36...')
    found_ns = 0
    unique = []
    found_size = 0
    unique_size = 0
    
    for dirpath, dirs, files in os.walk(PATH36):
        for f in files:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, PATH36)
            try:
                size = os.path.getsize(full)
            except:
                unique.append((rel, 0))
                continue
            
            fname = f.lower()
            if (fname, size) in name_size_idx:
                found_ns += 1
                found_size += size
            else:
                unique.append((rel, size))
                unique_size += size
    
    total = found_ns + len(unique)
    print(f'\n--- RESULTATS (par nom+taille) ---')
    print(f'Total fichiers scannes: {total}')
    print(f'Doublons (nom+taille):  {found_ns:>6}  ({found_ns*100/max(total,1):.1f}%)  {found_size/1048576:.0f} Mo')
    print(f'Uniques:                {len(unique):>6}  ({len(unique)*100/max(total,1):.1f}%)  {unique_size/1048576:.0f} Mo')
    
    if unique:
        print(f'\n--- Fichiers uniques (top 30 par taille) ---')
        unique.sort(key=lambda x: -x[1])
        for rel, size in unique[:30]:
            if size > 1048576: szs = f'{size/1048576:.0f} Mo'
            elif size > 1024: szs = f'{size/1024:.0f} Ko'
            else: szs = f'{size} o'
            print(f'  {szs:>8}  {rel}')
        if len(unique) > 30:
            print(f'  ... et {len(unique) - 30} autres')
        
        # Par sous-dossier
        print(f'\n--- Uniques par sous-dossier L1 ---')
        by_dir = defaultdict(lambda: [0, 0])
        for rel, size in unique:
            parts = rel.split(os.sep)
            top = parts[0] if len(parts) > 1 else '(racine)'
            by_dir[top][0] += 1
            by_dir[top][1] += size
        for d, (cnt, sz) in sorted(by_dir.items(), key=lambda x: -x[1][1]):
            if sz > 1048576: szs = f'{sz/1048576:.0f} Mo'
            else: szs = f'{sz/1024:.0f} Ko'
            print(f'  {d:55s} {cnt:>5} fich  {szs:>8}')
    
    conn.close()
    exit()

# Si 36 est dans la DB, comparer par hash
hashes_36 = set()
sizes_36 = {}
for path, size, h in files_36_db:
    if h:
        hashes_36.add(h)
    sizes_36[path] = (size, h)

# Recuperer les fichiers du reste de 37 qui ont les memes hashes
if hashes_36:
    placeholders = ','.join(['?'] * len(hashes_36))
    cur.execute(f"""
        SELECT hash_md5, COUNT(*) as cnt 
        FROM files 
        WHERE hash_md5 IN ({placeholders}) 
        AND path NOT LIKE '%36-TUNNEL GRAND CHAMBON%'
        GROUP BY hash_md5
    """, list(hashes_36))
    found_hashes = {row[0]: row[1] for row in cur.fetchall()}
else:
    found_hashes = {}

# Stats
found_by_hash = 0
unique_files = []
found_size = 0
unique_size = 0

for path, size, h in files_36_db:
    if h and h in found_hashes:
        found_by_hash += 1
        found_size += size
    else:
        rel = path.split('36-TUNNEL GRAND CHAMBON' + os.sep, 1)[-1] if '36-TUNNEL GRAND CHAMBON' in path else path
        unique_files.append((rel, size))
        unique_size += size

print(f'\n--- RESULTATS ---')
print(f'Total fichiers:          {len(files_36_db)}')
print(f'Doublons par hash:       {found_by_hash:>6}  ({found_by_hash*100/max(len(files_36_db),1):.1f}%)  {found_size/1048576:.0f} Mo')
print(f'Uniques (ou sans hash):  {len(unique_files):>6}  ({len(unique_files)*100/max(len(files_36_db),1):.1f}%)  {unique_size/1048576:.0f} Mo')

if unique_files:
    print(f'\n--- Fichiers uniques (top 30) ---')
    unique_files.sort(key=lambda x: -x[1])
    for rel, size in unique_files[:30]:
        if size > 1048576: szs = f'{size/1048576:.0f} Mo'
        elif size > 1024: szs = f'{size/1024:.0f} Ko'
        else: szs = f'{size} o'
        print(f'  {szs:>8}  {rel}')

conn.close()
