"""
Nettoyage de 33-GGC-DONNEES :
- Suppression des doublons (garder le chemin le plus court / hors "a classer")
- Suppression des fichiers système Mac (.Spotlight-V100, .Trashes)
- Suppression des .cyberducksegment (uploads incomplets Cyberduck)
- Suppression des .bak (backups AutoCAD)
- Suppression des Thumbs.db

Usage:
  python cleanup_ggc_donnees.py            # Dry-run
  python cleanup_ggc_donnees.py --execute  # Exécution réelle
"""
import os
import sys
import sqlite3

DB = "./reports/inventory_ggc_donnees.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\33-GGC-DONNEES"

DRY_RUN = "--execute" not in sys.argv

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

conn = sqlite3.connect(DB)
cur = conn.cursor()

# ═══════════════════════════════════════════════════════════════
# PARTIE 1 : DOUBLONS
# ═══════════════════════════════════════════════════════════════
print("=" * 70)
print("PARTIE 1 : SUPPRESSION DES DOUBLONS")
print("=" * 70)

# Get duplicate groups
cur.execute("""SELECT hash_md5, size, file_count FROM duplicate_groups ORDER BY wasted_space DESC""")
groups = cur.fetchall()

dup_delete = []
dup_keep = []

for hash_md5, size, file_count in groups:
    cur.execute("SELECT path FROM files WHERE hash_md5 = ? AND size = ?", (hash_md5, size))
    paths = [r[0] for r in cur.fetchall()]
    if len(paths) < 2:
        continue
    
    # Priority: keep files NOT in "--- a classer ---", NOT in .Spotlight/.Trashes
    def score(p):
        s = 0
        if '--- a classer ---' in p: s += 100
        if '.Spotlight-V100' in p: s += 200
        if '.Trashes' in p: s += 200
        if '.fseventsd' in p: s += 200
        s += len(p)  # shorter path = original
        return s
    
    paths.sort(key=score)
    dup_keep.append(paths[0])
    dup_delete.extend(paths[1:])

total_dup_size = 0
for p in dup_delete:
    cur.execute("SELECT size FROM files WHERE path = ?", (p,))
    row = cur.fetchone()
    if row:
        total_dup_size += row[0]

print(f"  Doublons à supprimer : {len(dup_delete)} fichiers, {format_size(total_dup_size)}")
print(f"  Fichiers conservés   : {len(dup_keep)}")

# ═══════════════════════════════════════════════════════════════
# PARTIE 2 : FICHIERS MAC (.Spotlight-V100, .Trashes)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 2 : FICHIERS SYSTÈME MAC")
print("=" * 70)

cur.execute("""SELECT path, size FROM files 
    WHERE path LIKE '%.Spotlight-V100%' 
    OR path LIKE '%.Trashes%' 
    OR path LIKE '%.fseventsd%' 
    OR filename = '.DS_Store'
    OR path LIKE '%.TemporaryItems%'""")
mac_files = cur.fetchall()
# Exclude those already in dup_delete
mac_paths = [r[0] for r in mac_files if r[0] not in set(dup_delete)]
mac_size = sum(r[1] for r in mac_files if r[0] not in set(dup_delete))
print(f"  Fichiers Mac : {len(mac_paths)} fichiers, {format_size(mac_size)}")

# ═══════════════════════════════════════════════════════════════
# PARTIE 3 : .cyberducksegment
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 3 : UPLOADS INCOMPLETS CYBERDUCK")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE extension = '.cyberducksegment'")
cyber_files = cur.fetchall()
cyber_paths = [r[0] for r in cyber_files]
cyber_size = sum(r[1] for r in cyber_files)
print(f"  .cyberducksegment : {len(cyber_paths)} fichiers, {format_size(cyber_size)}")

# Also get the parent .cyberducksegment folder to clean up
# The files are in folders like X.imp.cyberducksegment/
cyber_folders = set()
for p in cyber_paths:
    parts = p.split("\\")
    for i, part in enumerate(parts):
        if '.cyberducksegment' in part:
            cyber_folders.add("\\".join(parts[:i+1]))
            break

# ═══════════════════════════════════════════════════════════════
# PARTIE 4 : .BAK FILES
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 4 : FICHIERS .BAK")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE extension = '.bak'")
bak_files = cur.fetchall()
bak_paths = [r[0] for r in bak_files]
bak_size = sum(r[1] for r in bak_files)
print(f"  .bak : {len(bak_paths)} fichiers, {format_size(bak_size)}")

# ═══════════════════════════════════════════════════════════════
# PARTIE 5 : THUMBS.DB
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PARTIE 5 : THUMBS.DB")
print("=" * 70)

cur.execute("SELECT path, size FROM files WHERE LOWER(filename) = 'thumbs.db'")
thumbs_files = cur.fetchall()
thumbs_paths = [r[0] for r in thumbs_files]
thumbs_size = sum(r[1] for r in thumbs_files)
print(f"  Thumbs.db : {len(thumbs_paths)} fichiers, {format_size(thumbs_size)}")

# ═══════════════════════════════════════════════════════════════
# RÉSUMÉ ET EXÉCUTION
# ═══════════════════════════════════════════════════════════════
all_delete = set(dup_delete) | set(mac_paths) | set(cyber_paths) | set(bak_paths) | set(thumbs_paths)
total_size = total_dup_size + mac_size + cyber_size + bak_size + thumbs_size

print("\n" + "=" * 70)
print("RÉSUMÉ TOTAL")
print("=" * 70)
print(f"  Doublons          : {len(dup_delete):5d} fichiers, {format_size(total_dup_size)}")
print(f"  Fichiers Mac      : {len(mac_paths):5d} fichiers, {format_size(mac_size)}")
print(f"  Cyberduck segments: {len(cyber_paths):5d} fichiers, {format_size(cyber_size)}")
print(f"  .bak              : {len(bak_paths):5d} fichiers, {format_size(bak_size)}")
print(f"  Thumbs.db         : {len(thumbs_paths):5d} fichiers, {format_size(thumbs_size)}")
print(f"  ─────────────────────────────────────────")
print(f"  TOTAL             : {len(all_delete):5d} fichiers, {format_size(total_size)}")

if DRY_RUN:
    print("\n🔍 DRY-RUN : aucun fichier supprimé.")
    print("   Relancez avec --execute pour supprimer.")
else:
    print(f"\n🗑️  SUPPRESSION EN COURS...")
    deleted = 0
    errors = 0
    freed = 0
    
    for path in sorted(all_delete):
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                os.remove(path)
                deleted += 1
                freed += size
                if deleted % 100 == 0:
                    print(f"  ... {deleted} fichiers supprimés ({format_size(freed)})")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ⚠️  Erreur: {e}")
    
    print(f"\n✅ Terminé !")
    print(f"  Fichiers supprimés : {deleted}")
    print(f"  Espace libéré      : {format_size(freed)}")
    if errors:
        print(f"  Erreurs            : {errors}")
    
    # Nettoyage des dossiers .cyberducksegment vides
    cleaned_dirs = 0
    for folder in sorted(cyber_folders, key=len, reverse=True):
        try:
            if os.path.isdir(folder) and not os.listdir(folder):
                os.rmdir(folder)
                cleaned_dirs += 1
        except:
            pass
    if cleaned_dirs:
        print(f"  Dossiers cyberducksegment supprimés : {cleaned_dirs}")
    
    # Nettoyage des dossiers Mac vides (.Spotlight-V100, .Trashes)
    mac_dirs = set()
    for p in mac_paths:
        parts = p.split("\\")
        for i, part in enumerate(parts):
            if part in ('.Spotlight-V100', '.Trashes', '.fseventsd', '.TemporaryItems'):
                mac_dirs.add("\\".join(parts[:i+1]))
                break
    
    cleaned_mac = 0
    for d in sorted(mac_dirs, key=len, reverse=True):
        try:
            # Remove recursively if empty or only empty subdirs
            for root, dirs, files in os.walk(d, topdown=False):
                if not files and not dirs:
                    os.rmdir(root)
            if os.path.isdir(d):
                os.rmdir(d)
            cleaned_mac += 1
        except:
            pass
    if cleaned_mac:
        print(f"  Dossiers Mac nettoyés : {cleaned_mac}")

conn.close()
