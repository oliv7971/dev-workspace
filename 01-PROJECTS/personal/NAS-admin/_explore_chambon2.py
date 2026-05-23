"""Analyse approfondie de 37-TUNNEL GRAND CHAMBON.
- CHAMBON-161220 vs 02-PHASE 02
- Petits dossiers orphelins vs phases principales
- tms vs TMS CHAMBON
- Dossiers racine candidats a regrouper
"""
import sqlite3
import os
from collections import defaultdict

DB = r'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'
base_len = len(BASE) + 1

conn = sqlite3.connect(DB)
c = conn.cursor()

def get_folder_files(prefix):
    """Retourne {hash: [(relpath, filename, size)]} pour un dossier L1."""
    c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?",
              (BASE + '\\' + prefix + '%',))
    result = defaultdict(list)
    no_hash = []
    for p, fn, sz, h in c.fetchall():
        rel = p[base_len:]
        if h:
            result[h].append((rel, fn, sz))
        else:
            no_hash.append((rel, fn, sz))
    return result, no_hash

def inclusion_analysis(name_a, name_b):
    """Analyse l'inclusion de A dans B (par hash)."""
    files_a, nohash_a = get_folder_files(name_a)
    files_b, nohash_b = get_folder_files(name_b)
    
    total_a = sum(len(v) for v in files_a.values())
    hashes_a = set(files_a.keys())
    hashes_b = set(files_b.keys())
    common = hashes_a & hashes_b
    only_a = hashes_a - hashes_b
    
    common_files = sum(len(files_a[h]) for h in common)
    unique_files = sum(len(files_a[h]) for h in only_a)
    unique_size = sum(sz for h in only_a for _, _, sz in files_a[h])
    
    print(f"\n  {name_a} -> {name_b}:")
    print(f"    Total {name_a}: {total_a} fichiers hashes + {len(nohash_a)} sans hash")
    print(f"    Hashes en commun: {len(common)} ({common_files} fichiers)")
    print(f"    Hashes uniques a {name_a}: {len(only_a)} ({unique_files} fichiers, {unique_size/1048576:.1f} Mo)")
    
    if only_a:
        # Montrer les plus gros fichiers uniques
        unique_list = []
        for h in only_a:
            for rel, fn, sz in files_a[h]:
                unique_list.append((rel, fn, sz))
        unique_list.sort(key=lambda x: -x[2])
        print(f"    Top fichiers uniques:")
        for rel, fn, sz in unique_list[:15]:
            print(f"      {fn:50s} {sz/1048576:.1f} Mo  [{rel[:60]}]")
    
    # Fichiers sans hash - comparer par nom+taille
    if nohash_a:
        # Construire index nom+taille de B (avec hash et sans)
        b_ns = set()
        c.execute("SELECT filename, size FROM files WHERE path LIKE ?",
                  (BASE + '\\' + name_b + '%',))
        for fn, sz in c.fetchall():
            b_ns.add((fn, sz))
        
        nohash_found = sum(1 for _, fn, sz in nohash_a if (fn, sz) in b_ns)
        nohash_notfound = len(nohash_a) - nohash_found
        print(f"    Sans hash: {nohash_found}/{len(nohash_a)} trouves par nom+taille dans {name_b}")
        if nohash_notfound > 0:
            nohash_unique_sz = sum(sz for _, fn, sz in nohash_a if (fn, sz) not in b_ns)
            print(f"    Sans hash uniques: {nohash_notfound} fichiers, {nohash_unique_sz/1048576:.1f} Mo")
    
    pct = common_files * 100 // total_a if total_a else 0
    return pct, unique_files, unique_size, len(nohash_a)


# ============================================================
# 1. CHAMBON-161220 vs 02-PHASE 02
# ============================================================
print("=" * 100)
print("1. CHAMBON-161220 vs 02-PHASE 02 - Eiffage 2016")
print("=" * 100)
pct, uniq, uniq_sz, nh = inclusion_analysis('CHAMBON-161220', '02-PHASE 02 - Eiffage 2016')
print(f"\n  => Inclusion: {pct}%")

# Inverse aussi
pct2, uniq2, uniq_sz2, nh2 = inclusion_analysis('02-PHASE 02 - Eiffage 2016', 'CHAMBON-161220')

# ============================================================
# 2. tms vs TMS CHAMBON
# ============================================================
print(f"\n{'=' * 100}")
print("2. tms (55 Mo) vs TMS CHAMBON (3.47 Go)")
print("=" * 100)
inclusion_analysis('tms', 'TMS CHAMBON')
inclusion_analysis('tms', '02-PHASE 02 - Eiffage 2016')

# ============================================================
# 3. Petits dossiers orphelins vs phases principales
# ============================================================
print(f"\n{'=' * 100}")
print("3. PETITS DOSSIERS ORPHELINS")
print("=" * 100)

orphans = [
    'avant nov 2016', '97-divers', '70-implantation eclairage',
    '03-PHASE 03 - interchantier 2017', 'chambon 15&18 avril 2016',
    '10-recollement externes', 'nov2016', '81-bp', '96-heures',
    '100-presse', '_divers', 'TUNNEL DE CHAMBON', 'profils tunnel existant',
    'carte TC 20160418', 'chambon', 'IMAGES CHAMBON', '20160415',
    '98-sauvegardes', '03-CONVERGENCES', '200-reprise DOE tete amont',
    '80-divers', '36-TUNNEL GRAND CHAMBON', '06-LIVRAISON AUSCULTATION'
]

# Pour chaque orphelin, compter les fichiers et verifier l'overlap avec toutes les phases
phases = ['01-PHASE 01 - GGC2015', '02-PHASE 02 - Eiffage 2016', 
          '04-PHASE04-Eiffage 2017', '05-PHASE05-AUSCULTATIONS']

# Build hash index for all phases
phase_hashes = {}
for phase in phases:
    files_p, _ = get_folder_files(phase)
    phase_hashes[phase] = set(files_p.keys())

all_phase_hashes = set()
for h_set in phase_hashes.values():
    all_phase_hashes |= h_set

print(f"\n{'Dossier':<40} {'Fich':>6} {'Taille':>10} {'% dans phases':>15} {'Uniques':>10}")
print("-" * 90)

for orphan in sorted(orphans):
    c.execute("SELECT COUNT(*), SUM(size) FROM files WHERE path LIKE ?",
              (BASE + '\\' + orphan + '%',))
    cnt, sz = c.fetchone()
    if not cnt:
        continue
    
    files_o, nohash_o = get_folder_files(orphan)
    total_hashed = sum(len(v) for v in files_o.values())
    
    if total_hashed > 0:
        in_phases = sum(len(files_o[h]) for h in files_o if h in all_phase_hashes)
        pct = in_phases * 100 // total_hashed
        unique = total_hashed - in_phases
    else:
        pct = 0
        unique = cnt
    
    sz_str = f"{sz/1073741824:.2f} Go" if sz > 1073741824 else f"{sz/1048576:.0f} Mo"
    print(f"  {orphan:<38} {cnt:>6} {sz_str:>10} {pct:>13}% {unique:>10}")

# ============================================================
# 4. 36-TUNNEL GRAND CHAMBON (doublon de nom?)
# ============================================================
print(f"\n{'=' * 100}")
print("4. 36-TUNNEL GRAND CHAMBON (sous-dossier homonyme)")
print("=" * 100)
c.execute("SELECT path, filename, size FROM files WHERE path LIKE ? ORDER BY size DESC",
          (BASE + '\\36-TUNNEL GRAND CHAMBON%',))
rows = c.fetchall()
print(f"  {len(rows)} fichiers")
# L2 structure
l2 = defaultdict(lambda: [0,0])
for p, fn, sz in rows:
    rel = p[base_len:]
    if rel.endswith(fn):
        rel = rel[:-len(fn)].rstrip('\\')
    parts = rel.split('\\')
    if len(parts) >= 2:
        l2[parts[1]][0] += 1
        l2[parts[1]][1] += sz
for name, (cnt, sz) in sorted(l2.items(), key=lambda x: -x[1][1]):
    print(f"    {name:50s} {cnt:>5} fich  {sz/1048576:.1f} Mo")

# ============================================================
# 5. Fichiers racine
# ============================================================
print(f"\n{'=' * 100}")
print("5. FICHIERS A LA RACINE")
print("=" * 100)
c.execute("""SELECT filename, size, hash_md5 FROM files 
WHERE path LIKE ? AND path NOT LIKE ?""",
          (BASE + '\\%', BASE + '\\%\\%'))
# Hmm, les fichiers racine dans l'inventaire ont path = BASE + '\' + filename
# Essayons autrement
c.execute("SELECT path, filename, size FROM files")
root_files = []
for p, fn, sz in c.fetchall():
    rel = p[base_len:] if len(p) > base_len else ''
    if rel.endswith(fn):
        rel = rel[:-len(fn)].rstrip('\\')
    if not rel:
        root_files.append((fn, sz))

print(f"  {len(root_files)} fichiers racine, {sum(s for _,s in root_files)/1048576:.1f} Mo")
for fn, sz in sorted(root_files, key=lambda x: -x[1]):
    print(f"    {fn:60s} {sz/1048576:.1f} Mo")

conn.close()
