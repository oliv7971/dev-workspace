"""
Suppression des doublons dans 32-GGC-BUREAU.
Stratégie : garder le chemin le plus court (l'original), supprimer les copies.
Pour RIEGL : garder RIEGL\*.RiSCAN, supprimer RIEGL\RIEGL\*.
Pour vidéos AFTES : garder 02-COMMERCIAL (usage direct), supprimer copie dans FOURNISSEURS.

Usage:
    python cleanup_ggc_duplicates.py            # dry-run
    python cleanup_ggc_duplicates.py --execute  # suppression réelle
"""
import os
import sys
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_ggc.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\32-GGC-BUREAU\\"
EXECUTE = "--execute" in sys.argv

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    if size >= 1e3: return f"{size/1e3:.1f} Ko"
    return f"{size} o"

def rel(path):
    return path[len(BASE):] if path.startswith(BASE) else path

def pick_keeper(paths):
    """Choisir le fichier à garder parmi les doublons.
    Stratégie : chemin le plus court = l'original."""
    return min(paths, key=lambda p: len(p))

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    
    # Charger les groupes de doublons
    cur.execute("SELECT hash_md5, size, file_count FROM duplicate_groups ORDER BY size DESC")
    groups = cur.fetchall()
    
    to_delete = []
    to_keep = []
    
    for hash_md5, size, file_count in groups:
        cur2 = db.cursor()
        cur2.execute("SELECT path FROM files WHERE hash_md5 = ? AND size = ?", (hash_md5, size))
        paths = [r[0] for r in cur2.fetchall()]
        
        if len(paths) < 2:
            continue
        
        keeper = pick_keeper(paths)
        to_keep.append((keeper, size))
        
        for p in paths:
            if p != keeper:
                to_delete.append((p, size, rel(keeper)))
    
    # Affichage
    mode = "🗑️  SUPPRESSION" if EXECUTE else "🔍 DRY-RUN"
    print(mode)
    print("=" * 70)
    
    # Stats par dossier
    by_folder = defaultdict(lambda: [0, 0])
    for path, size, _ in to_delete:
        r = rel(path)
        l1 = r.split("\\")[0]
        by_folder[l1][0] += 1
        by_folder[l1][1] += size
    
    print("\nSuppressions par dossier :")
    for folder in sorted(by_folder, key=lambda x: by_folder[x][1], reverse=True):
        nb, sz = by_folder[folder]
        print(f"  {folder:40s}  {nb:>6,} fichiers  {fmt(sz):>10s}")
    
    total_files = len(to_delete)
    total_size = sum(s for _, s, _ in to_delete)
    print(f"\n  {'─' * 55}")
    print(f"  {'TOTAL':40s}  {total_files:>6,} fichiers  {fmt(total_size):>10s}")
    
    # Top 20 plus gros
    print(f"\nTop 20 fichiers supprimés :")
    top = sorted(to_delete, key=lambda x: x[1], reverse=True)[:20]
    for path, size, keeper in top:
        fn = path.split("\\")[-1]
        r = rel(path)
        # Tronquer
        if len(r) > 70:
            r = "..." + r[-67:]
        kr = rel(keeper)
        if len(kr) > 50:
            kr = "..." + kr[-47:]
        print(f"  {fmt(size):>10s}  SUPPR: {r}")
        print(f"             GARDÉ: {kr}")
    
    if EXECUTE:
        print(f"\n⚡ Suppression en cours...")
        deleted = 0
        failed = 0
        freed = 0
        
        for path, size, _ in to_delete:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    deleted += 1
                    freed += size
                else:
                    deleted += 1
                    freed += size
            except Exception as e:
                failed += 1
                if failed <= 10:
                    print(f"  ❌ {os.path.basename(path)}: {e}")
        
        print(f"\n  ✅ Supprimés : {deleted:,} fichiers ({fmt(freed)})")
        if failed:
            print(f"  ❌ Échecs   : {failed:,}")
    else:
        print(f"\n→ Pour exécuter : python cleanup_ggc_duplicates.py --execute")
    
    db.close()

if __name__ == "__main__":
    main()
