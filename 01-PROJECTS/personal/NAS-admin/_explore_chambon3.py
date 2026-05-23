"""Analyse de 10-ACTIVITES TOPO dans 02-PHASE 02.
Objectif: comprendre le classement par date, identifier les dossiers en vrac
et les doublons entre dossiers mois et racine."""
import sqlite3
import os
from collections import defaultdict
import re

DB = r'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'
ACTIVITES = BASE + r'\02-PHASE 02 - Eiffage 2016\10-ACTIVITES TOPO'
act_len = len(ACTIVITES) + 1

conn = sqlite3.connect(DB)
c = conn.cursor()

# Tous les fichiers dans 10-ACTIVITES TOPO
c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?",
          (ACTIVITES + '%',))
all_files = c.fetchall()
print(f"Total fichiers dans 10-ACTIVITES TOPO: {len(all_files)}")
print(f"Taille totale: {sum(sz for _,_,sz,_ in all_files)/1048576:.0f} Mo")

# Structure L1 sous ACTIVITES TOPO
l1_stats = defaultdict(lambda: {'count': 0, 'size': 0, 'files': []})
root_files = []

for path, filename, size, h in all_files:
    rel = path[act_len:] if path.startswith(ACTIVITES + '\\') else path[act_len:]
    if rel.endswith(filename):
        rel = rel[:-len(filename)].rstrip('\\')
    
    if not rel:
        root_files.append((filename, size, h))
    else:
        l1 = rel.split('\\')[0]
        l1_stats[l1]['count'] += 1
        l1_stats[l1]['size'] += size
        l1_stats[l1]['files'].append((rel, filename, size, h))

# Categoriser les dossiers
date_pattern = re.compile(r'(\d{2})-.*(\d{4})|(\d{4})[-_](\d{2})|(\d{2})[-_].*\b(201[5-9])\b|(\d{2})-[A-Z]', re.IGNORECASE)
month_folders = []
other_folders = []

print(f"\n{'=' * 100}")
print("SOUS-DOSSIERS DE 10-ACTIVITES TOPO")
print(f"{'=' * 100}")
print(f"\n{'Dossier':<60} {'Fich':>6} {'Taille':>10}")
print("-" * 80)

for name in sorted(l1_stats.keys()):
    stats = l1_stats[name]
    sz = stats['size']
    sz_str = f"{sz/1048576:.1f} Mo" if sz > 1048576 else f"{sz/1024:.0f} Ko"
    
    # Detecter si c'est un dossier de type mois/date
    is_date = bool(re.match(r'^\d{2}[-_ ]', name))
    marker = "  [DATE]" if is_date else "  [AUTRE]"
    
    print(f"  {name:<58} {stats['count']:>6} {sz_str:>10}{marker}")
    
    if is_date:
        month_folders.append(name)
    else:
        other_folders.append(name)

print(f"\n  Fichiers a la racine: {len(root_files)}, {sum(s for _,s,_ in root_files)/1048576:.1f} Mo")

print(f"\nDossiers 'date': {len(month_folders)}")
print(f"Dossiers 'autre': {len(other_folders)}")

# Pour chaque dossier "autre", verifier le chevauchement avec les dossiers "date"
print(f"\n{'=' * 100}")
print("ANALYSE DES DOSSIERS NON-DATE vs DOSSIERS DATE")
print(f"{'=' * 100}")

# Construire l'index hash de tous les dossiers date
date_hashes = set()
date_hash_to_folder = defaultdict(set)
for name in month_folders:
    for rel, fn, sz, h in l1_stats[name]['files']:
        if h:
            date_hashes.add(h)
            date_hash_to_folder[h].add(name)

print(f"\nHashes uniques dans dossiers date: {len(date_hashes)}")

for name in sorted(other_folders):
    stats = l1_stats[name]
    if stats['count'] == 0:
        continue
    
    hashed = [(rel, fn, sz, h) for rel, fn, sz, h in stats['files'] if h]
    in_dates = [(rel, fn, sz, h) for rel, fn, sz, h in hashed if h in date_hashes]
    unique = [(rel, fn, sz, h) for rel, fn, sz, h in hashed if h not in date_hashes]
    
    total = len(hashed)
    pct = len(in_dates) * 100 // total if total else 0
    unique_sz = sum(sz for _, _, sz, _ in unique)
    
    print(f"\n  {name} ({stats['count']} fich, {stats['size']/1048576:.1f} Mo)")
    print(f"    Hashes: {total}, dans dossiers date: {len(in_dates)} ({pct}%), uniques: {len(unique)} ({unique_sz/1048576:.1f} Mo)")
    
    if in_dates and len(in_dates) <= 10:
        for rel, fn, sz, h in in_dates:
            targets = date_hash_to_folder[h]
            print(f"      DUP: {fn} -> {', '.join(targets)}")
    
    if unique:
        for rel, fn, sz, h in sorted(unique, key=lambda x: -x[2])[:5]:
            print(f"      UNIQUE: {fn} ({sz/1048576:.1f} Mo)")

# Fichiers racine vs dossiers date
print(f"\n{'=' * 100}")
print("FICHIERS RACINE vs DOSSIERS DATE")
print(f"{'=' * 100}")

root_in_dates = [(fn, sz, h) for fn, sz, h in root_files if h and h in date_hashes]
root_unique = [(fn, sz, h) for fn, sz, h in root_files if h and h not in date_hashes]
root_nohash = [(fn, sz) for fn, sz, h in root_files if not h]

print(f"  Total racine: {len(root_files)}")
print(f"  Doublons des dossiers date: {len(root_in_dates)} ({sum(s for _,s,_ in root_in_dates)/1048576:.1f} Mo)")
print(f"  Uniques (hashes): {len(root_unique)} ({sum(s for _,s,_ in root_unique)/1048576:.1f} Mo)")
print(f"  Sans hash: {len(root_nohash)} ({sum(s for _,s in root_nohash)/1048576:.1f} Mo)")

if root_in_dates:
    print(f"\n  Doublons racine:")
    for fn, sz, h in sorted(root_in_dates, key=lambda x: -x[1])[:20]:
        targets = date_hash_to_folder[h]
        print(f"    {fn:50s} {sz/1048576:.1f} Mo -> {', '.join(sorted(targets))}")

if root_unique:
    print(f"\n  Fichiers uniques racine:")
    for fn, sz, h in sorted(root_unique, key=lambda x: -x[1])[:20]:
        print(f"    {fn:50s} {sz/1048576:.1f} Mo")

if root_nohash:
    print(f"\n  Fichiers sans hash (racine):")
    for fn, sz in sorted(root_nohash, key=lambda x: -x[1])[:20]:
        print(f"    {fn:50s} {sz/1048576:.1f} Mo")

# Doublons internes aux dossiers date
print(f"\n{'=' * 100}")
print("DOUBLONS ENTRE DOSSIERS DATE")
print(f"{'=' * 100}")

# Pour chaque hash, lister les dossiers date qui le contiennent
multi_date = {h: folders for h, folders in date_hash_to_folder.items() if len(folders) > 1}
print(f"  Hashes presents dans plusieurs dossiers date: {len(multi_date)}")

# Compter les fichiers concernes par paire
pair_count = defaultdict(int)
pair_size = defaultdict(int)
for h, folders in multi_date.items():
    # Trouver la taille
    for name in month_folders:
        for rel, fn, sz, fh in l1_stats[name]['files']:
            if fh == h:
                unit_sz = sz
                break
        else:
            continue
        break
    
    for a in sorted(folders):
        for b in sorted(folders):
            if a < b:
                pair_count[(a, b)] += 1
                pair_size[(a, b)] += unit_sz

if pair_count:
    print(f"\n  Paires avec chevauchement:")
    for (a, b), cnt in sorted(pair_count.items(), key=lambda x: -pair_size[x[0]]):
        if cnt >= 3:
            print(f"    {a} <-> {b}: {cnt} fichiers ({pair_size[(a,b)]/1048576:.1f} Mo)")

conn.close()
