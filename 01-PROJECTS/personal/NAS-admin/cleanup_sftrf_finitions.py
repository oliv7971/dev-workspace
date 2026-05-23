"""
Nettoyage finitions 01-SFTRF :
1. DLL parasites dans 16-RAMEAUX ET BP (résidus d'installation Cyclone copiés avec les scans)
2. Photos orphelines à la racine de 40-Photos
3. Autres fichiers parasites (.exe, .ocx, .manifest dans les dossiers scan)
"""
import os
import sys
from pathlib import Path
from collections import defaultdict

BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\01-SFTRF"
DRY_RUN = "--execute" not in sys.argv

def format_size(size):
    for unit in ['octets', 'Ko', 'Mo', 'Go', 'To']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} Po"

def scan_parasites(base_path):
    """Trouve les fichiers parasites (DLL, EXE, etc.) dans les dossiers de scan."""
    # Extensions parasites = résidus d'installation logicielle copiés par erreur
    parasite_exts = {'.dll', '.exe', '.ocx', '.manifest', '.config', '.pdb'}
    # Exclure les .exe qui pourraient être des outils légitimes
    legit_names = set()  # à remplir si on trouve des faux positifs
    
    parasites = []
    by_folder = defaultdict(lambda: {"count": 0, "size": 0, "files": []})
    
    for root, dirs, files in os.walk(base_path):
        # Exclure les dossiers Synology
        dirs[:] = [d for d in dirs if d not in ('@eaDir', '#recycle', '@tmp')]
        
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in parasite_exts and f.lower() not in legit_names:
                full = os.path.join(root, f)
                try:
                    size = os.path.getsize(full)
                    rel = os.path.relpath(full, base_path)
                    # Dossier parent de premier niveau
                    top_folder = rel.split(os.sep)[0] if os.sep in rel else "(racine)"
                    parasites.append((full, rel, size, ext))
                    by_folder[top_folder]["count"] += 1
                    by_folder[top_folder]["size"] += size
                except OSError:
                    pass
    
    return parasites, by_folder

def scan_photos_orphelines():
    """Trouve les fichiers à la racine de 40-Photos (pas dans un sous-dossier)."""
    photos_dir = os.path.join(BASE, "40-Photos")
    if not os.path.exists(photos_dir):
        return []
    
    orphelins = []
    for item in os.listdir(photos_dir):
        full = os.path.join(photos_dir, item)
        if os.path.isfile(full):
            try:
                size = os.path.getsize(full)
                orphelins.append((full, item, size))
            except OSError:
                pass
    return orphelins

def scan_junk_files():
    """Trouve Thumbs.db, .DS_Store, fichiers Mac (._*) dans tout 01-SFTRF."""
    junk_names = {'Thumbs.db', '.DS_Store', 'desktop.ini', '._.DS_Store'}
    junk = []
    
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ('@eaDir', '#recycle', '@tmp')]
        for f in files:
            is_junk = f in junk_names or (f.startswith('._') and not f.startswith('._@'))
            if is_junk:
                full = os.path.join(root, f)
                try:
                    size = os.path.getsize(full)
                    junk.append((full, os.path.relpath(full, BASE), size))
                except OSError:
                    pass
    return junk


print("=" * 80)
print("NETTOYAGE FINITIONS 01-SFTRF")
print("=" * 80)

# 1. DLL et fichiers parasites
print("\n--- 1. FICHIERS PARASITES (DLL, EXE, etc.) ---")
print("Scan en cours...")
parasites, by_folder = scan_parasites(BASE)

if parasites:
    total_size = sum(p[2] for p in parasites)
    # Stats par extension
    by_ext = defaultdict(lambda: {"count": 0, "size": 0})
    for _, _, size, ext in parasites:
        by_ext[ext]["count"] += 1
        by_ext[ext]["size"] += size
    
    print(f"\n  Fichiers parasites trouvés: {len(parasites)} ({format_size(total_size)})")
    print(f"\n  Par extension:")
    for ext in sorted(by_ext, key=lambda e: by_ext[e]["size"], reverse=True):
        info = by_ext[ext]
        print(f"    {ext:15s} : {info['count']:6d} fichiers  ({format_size(info['size'])})")
    
    print(f"\n  Par dossier:")
    for folder in sorted(by_folder, key=lambda f: by_folder[f]["size"], reverse=True):
        info = by_folder[folder]
        print(f"    {folder:40s} : {info['count']:5d} fichiers  ({format_size(info['size'])})")
    
    # Exemples
    print(f"\n  Exemples de fichiers:")
    shown = set()
    for _, rel, size, ext in sorted(parasites, key=lambda p: p[2], reverse=True)[:15]:
        name = os.path.basename(rel)
        if name not in shown:
            print(f"    {name:40s} ({format_size(size)})")
            shown.add(name)
else:
    print("  Aucun fichier parasite trouvé.")

# 2. Photos orphelines
print("\n--- 2. PHOTOS ORPHELINES (racine de 40-Photos) ---")
orphelins = scan_photos_orphelines()
if orphelins:
    total_size = sum(o[2] for o in orphelins)
    print(f"  Fichiers à la racine de 40-Photos: {len(orphelins)} ({format_size(total_size)})")
    for _, name, size in sorted(orphelins, key=lambda o: o[1]):
        print(f"    {name:50s} ({format_size(size)})")
else:
    print("  Aucun fichier orphelin dans 40-Photos.")

# 3. Fichiers junk
print("\n--- 3. FICHIERS JUNK (Thumbs.db, .DS_Store, etc.) ---")
print("Scan en cours...")
junk = scan_junk_files()
if junk:
    total_size = sum(j[2] for j in junk)
    by_name = defaultdict(lambda: {"count": 0, "size": 0})
    for _, rel, size in junk:
        name = os.path.basename(rel)
        by_name[name]["count"] += 1
        by_name[name]["size"] += size
    
    print(f"  Fichiers junk trouvés: {len(junk)} ({format_size(total_size)})")
    for name in sorted(by_name, key=lambda n: by_name[n]["count"], reverse=True):
        info = by_name[name]
        print(f"    {name:30s} : {info['count']:5d} fichiers  ({format_size(info['size'])})")
else:
    print("  Aucun fichier junk trouvé.")

# Résumé et exécution
print("\n" + "=" * 80)
total_to_delete = len(parasites) + len(junk)
total_size_delete = sum(p[2] for p in parasites) + sum(j[2] for j in junk)
print(f"TOTAL À SUPPRIMER: {total_to_delete} fichiers ({format_size(total_size_delete)})")

if orphelins:
    print(f"PHOTOS ORPHELINES À RANGER: {len(orphelins)} fichiers")

if DRY_RUN:
    print("\n⚠️  Mode DRY-RUN. Relancer avec --execute pour supprimer.")
else:
    print("\n🚀 SUPPRESSION EN COURS...")
    
    deleted = 0
    errors = 0
    freed = 0
    
    # Supprimer parasites
    for full, rel, size, ext in parasites:
        try:
            os.remove(full)
            deleted += 1
            freed += size
        except OSError as e:
            print(f"  ❌ Erreur: {rel} - {e}")
            errors += 1
    
    # Supprimer junk
    for full, rel, size in junk:
        try:
            os.remove(full)
            deleted += 1
            freed += size
        except OSError as e:
            print(f"  ❌ Erreur: {rel} - {e}")
            errors += 1
    
    # Ranger photos orphelines dans un sous-dossier
    if orphelins:
        dest_dir = os.path.join(BASE, "40-Photos", "_fichiers-racine")
        os.makedirs(dest_dir, exist_ok=True)
        moved = 0
        for full, name, size in orphelins:
            try:
                dest = os.path.join(dest_dir, name)
                os.rename(full, dest)
                moved += 1
            except OSError as e:
                print(f"  ❌ Erreur déplacement: {name} - {e}")
        print(f"  📁 Photos déplacées vers _fichiers-racine: {moved}/{len(orphelins)}")
    
    print(f"\n✅ Terminé !")
    print(f"  Fichiers supprimés: {deleted}")
    print(f"  Espace libéré: {format_size(freed)}")
    if errors:
        print(f"  Erreurs: {errors}")
