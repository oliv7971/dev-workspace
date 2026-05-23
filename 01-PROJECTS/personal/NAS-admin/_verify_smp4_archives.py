"""Vérification des archives de 34-controle voussoirs SMP4.
Liste le contenu des archives (7z l) et compare avec l'inventaire existant."""
import subprocess
import sqlite3
import os
import re
from collections import defaultdict

DB = r'inventaires/inventaire_34-controle voussoirs SMP4.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4'
SEVENZ = r'C:\Program Files\7-Zip\7z.exe'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Charger l'inventaire complet (hors archives elles-mêmes)
print("Chargement de l'inventaire...")
c.execute("""SELECT path, filename, size, hash_md5 FROM files 
WHERE extension NOT IN ('.7z', '.zip', '.rar', '.gz')""")
all_files = c.fetchall()

# Index par filename+size et par hash
idx_ns = defaultdict(list)
idx_hash = {}
for p, fn, sz, h in all_files:
    idx_ns[(fn, sz)].append(p)
    if h:
        idx_hash[h] = p

print(f"  {len(all_files)} fichiers non-archivés dans l'inventaire")
print(f"  {len(idx_hash)} hashes uniques")

# Lister les archives à vérifier
archives = []

# Archives dans ZIP/
zip_dir = os.path.join(BASE, 'USINE-VOUSSOIRS-SMLP', 'ZIP')
c.execute("""SELECT path || filename as full, filename, size FROM files 
WHERE path LIKE ? AND extension IN ('.7z', '.zip', '.rar')
ORDER BY size DESC""", (BASE + '\\USINE-VOUSSOIRS-SMLP\\ZIP\\%',))
for full, fn, sz in c.fetchall():
    archives.append((os.path.join(zip_dir, fn), fn, sz))

# 11-SMP4.zip
c.execute("SELECT path, filename, size FROM files WHERE filename = '11-SMP4.zip'")
for p, fn, sz in c.fetchall():
    archives.append((os.path.join(p, fn) if not p.endswith(fn) else p, fn, sz))

print(f"\n{len(archives)} archives à vérifier")

def list_archive(archive_path):
    """Liste le contenu d'une archive avec 7z l. Retourne [(name, size), ...]"""
    try:
        result = subprocess.run(
            [SEVENZ, 'l', '-slt', archive_path],
            capture_output=True, text=True, timeout=300, encoding='utf-8', errors='replace'
        )
        if result.returncode != 0:
            return None, result.stderr[:200]
        
        entries = []
        current_name = None
        current_size = None
        current_is_dir = False
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('Path = '):
                if current_name and not current_is_dir:
                    entries.append((current_name, current_size))
                current_name = line[7:]
                current_size = 0
                current_is_dir = False
            elif line.startswith('Size = '):
                try:
                    current_size = int(line[7:])
                except:
                    current_size = 0
            elif line.startswith('Folder = +') or line.startswith('Folder = 1'):
                current_is_dir = True
        
        # Dernier entry
        if current_name and not current_is_dir:
            entries.append((current_name, current_size))
        
        # Skip first entry (archive itself)
        if entries and entries[0][0] == os.path.basename(archive_path):
            entries = entries[1:]
            
        return entries, None
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    except Exception as e:
        return None, str(e)

def check_coverage(entries):
    """Compare les fichiers d'une archive avec l'inventaire."""
    found = 0
    not_found = []
    found_sz = 0
    not_found_sz = 0
    
    for name, size in entries:
        # Extraire le nom de fichier
        fn = os.path.basename(name)
        if not fn:
            continue
        
        # Chercher par nom+taille
        if (fn, size) in idx_ns:
            found += 1
            found_sz += size
        else:
            not_found.append((name, size))
            not_found_sz += size
    
    return found, not_found, found_sz, not_found_sz

# Traiter chaque archive
print("\n" + "=" * 120)
print("VERIFICATION DES ARCHIVES")
print("=" * 120)

total_archives_sz = 0
all_not_found = []

for archive_path, archive_name, archive_sz in archives:
    total_archives_sz += archive_sz
    sz_go = archive_sz / 1073741824
    
    # Construire le chemin NAS correct
    if '_a_classer' in archive_name:
        full_path = os.path.join(BASE, '_a_classer', archive_name)
    else:
        full_path = os.path.join(BASE, 'USINE-VOUSSOIRS-SMLP', 'ZIP', archive_name)
    
    # Essayer le chemin direct d'abord
    if not os.path.exists(full_path):
        full_path = archive_path
    
    print(f"\n{'-' * 120}")
    print(f"[ARCHIVE] {archive_name} ({sz_go:.2f} Go)")
    
    if not os.path.exists(full_path):
        print(f"  /!\\ FICHIER INTROUVABLE: {full_path}")
        continue
    
    entries, err = list_archive(full_path)
    
    if err:
        print(f"  /!\\ ERREUR: {err}")
        continue
    
    total_uncompressed = sum(s for _, s in entries)
    print(f"  Contenu: {len(entries)} fichiers, {total_uncompressed/1073741824:.2f} Go décompressé")
    print(f"  Ratio compression: {archive_sz/total_uncompressed:.1%}" if total_uncompressed > 0 else "")
    
    found, not_found, found_sz, not_found_sz = check_coverage(entries)
    total = len(entries)
    pct = found * 100 // total if total else 0
    
    if total == 0:
        print(f"  /!\\ Archive vide")
        continue
    
    print(f"  Couverture: {found}/{total} ({pct}%) fichiers trouvés dans l'inventaire")
    print(f"    Trouvés: {found_sz/1073741824:.2f} Go | Manquants: {not_found_sz/1073741824:.2f} Go")
    
    if pct == 100:
        print(f"  [OK] 100% couvert -- archive supprimable")
    elif pct >= 95:
        print(f"  [OK] ~{pct}% couvert")
        # Afficher les manquants
        print(f"  Fichiers manquants ({len(not_found)}):")
        for name, size in sorted(not_found, key=lambda x: -x[1])[:20]:
            print(f"    {name} ({size:,} bytes)")
        if len(not_found) > 20:
            print(f"    ... et {len(not_found)-20} autres")
    elif pct >= 80:
        print(f"  [WARN] {pct}% couvert -- {len(not_found)} fichiers manquants")
        for name, size in sorted(not_found, key=lambda x: -x[1])[:10]:
            print(f"    {name} ({size:,} bytes)")
        if len(not_found) > 10:
            print(f"    ... et {len(not_found)-10} autres")
    else:
        print(f"  [NOK] Seulement {pct}% couvert -- {len(not_found)} fichiers absents de l'inventaire!")
        # Analyse des extensions manquantes
        ext_stats = defaultdict(lambda: [0, 0])
        for name, size in not_found:
            ext = os.path.splitext(name)[1].lower() or '(no ext)'
            ext_stats[ext][0] += 1
            ext_stats[ext][1] += size
        print(f"  Extensions manquantes:")
        for ext, (cnt, sz) in sorted(ext_stats.items(), key=lambda x: -x[1][1])[:10]:
            print(f"    {ext:<15} {cnt:>6} fich  {sz/1048576:.1f} Mo")
    
    all_not_found.extend([(archive_name, n, s) for n, s in not_found])

# Résumé
print(f"\n{'=' * 120}")
print("RESUME")
print("=" * 120)
print(f"Archives verifiees: {len(archives)}")
print(f"Taille totale archives: {total_archives_sz/1073741824:.1f} Go")
print(f"Fichiers non couverts au total: {len(all_not_found)}")
if all_not_found:
    not_found_total_sz = sum(s for _, _, s in all_not_found)
    print(f"Taille non couverte: {not_found_total_sz/1073741824:.2f} Go")
    
    # Grouper par archive
    by_archive = defaultdict(list)
    for an, n, s in all_not_found:
        by_archive[an].append((n, s))
    print(f"\nPar archive:")
    for an in by_archive:
        items = by_archive[an]
        print(f"  {an}: {len(items)} fichiers manquants ({sum(s for _,s in items)/1048576:.1f} Mo)")

conn.close()
