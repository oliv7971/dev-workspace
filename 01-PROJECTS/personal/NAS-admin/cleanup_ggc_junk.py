"""
Nettoyage et corrections dans 32-GGC-BUREAU.
- Supprimer Thumbs.db, .bak, .temp suspects
- Renommer "founrisseurs" → fusionner dans 11-FOURNISSEURS
- Supprimer "gimp - copie.exe"

Usage:
    python cleanup_ggc_junk.py            # dry-run
    python cleanup_ggc_junk.py --execute  # exécution réelle
"""
import os
import sys
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_ggc.db"
NAS_BASE = "\\\\Nas_travail\\01-ds414-data\\32-GGC-BUREAU\\"
EXECUTE = "--execute" in sys.argv

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    if size >= 1e3: return f"{size/1e3:.1f} Ko"
    return f"{size} o"

def rel(path):
    return path[len(NAS_BASE):] if path.startswith(NAS_BASE) else path

def is_deletable(path, filename, ext, size):
    r = rel(path).lower()
    
    # Thumbs.db
    if filename.lower() == "thumbs.db":
        return True, "Thumbs.db"
    
    # .bak
    if ext and ext.lower() == ".bak":
        return True, ".bak"
    
    # gimp copie
    if "copie" in filename.lower() and ext and ext.lower() == ".exe":
        return True, "Installeur copie"
    
    return False, ""

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute("SELECT path, filename, extension, size FROM files")
    all_files = cur.fetchall()
    db.close()
    
    mode = "🗑️  SUPPRESSION" if EXECUTE else "🔍 DRY-RUN"
    print(f"{mode} — Nettoyage")
    print("=" * 70)
    
    # === PARTIE 1 : Suppressions ===
    to_delete = []
    stats = defaultdict(lambda: [0, 0])
    
    for path, fn, ext, size in all_files:
        delete, reason = is_deletable(path, fn, ext, size)
        if delete:
            to_delete.append((path, fn, size, reason))
            stats[reason][0] += 1
            stats[reason][1] += size
    
    print("\n1. SUPPRESSIONS")
    print("-" * 70)
    for reason in sorted(stats, key=lambda x: stats[x][1], reverse=True):
        nb, sz = stats[reason]
        print(f"  {reason:30s}  {nb:>6,} fichiers  {fmt(sz):>10s}")
    
    total_del = sum(s for _, _, s, _ in to_delete)
    print(f"  Total: {len(to_delete):,} fichiers, {fmt(total_del)}")
    
    # === PARTIE 2 : Renommage founrisseurs → fournisseurs ===
    print("\n2. RENOMMAGE")
    print("-" * 70)
    
    old_fourn = os.path.join(NAS_BASE[:-1], "11-FOURNISSEURS", "founrisseurs")
    new_fourn = os.path.join(NAS_BASE[:-1], "11-FOURNISSEURS", "fournisseurs-divers")
    
    fourn_exists = os.path.exists(old_fourn)
    fourn_conflict = os.path.exists(new_fourn)
    
    if fourn_exists and not fourn_conflict:
        print(f"  ✏️  11-FOURNISSEURS\\founrisseurs → 11-FOURNISSEURS\\fournisseurs-divers")
    elif not fourn_exists:
        print(f"  ⏭️  founrisseurs n'existe pas")
    else:
        print(f"  ⚠️  Conflit : fournisseurs-divers existe déjà")
    
    # === EXÉCUTION ===
    if EXECUTE:
        print("\n⚡ Exécution...")
        
        # Suppressions
        deleted = 0
        failed = 0
        for path, fn, size, reason in to_delete:
            try:
                if os.path.exists(path):
                    os.remove(path)
                deleted += 1
            except Exception as e:
                failed += 1
                if failed <= 5:
                    print(f"  ❌ {fn}: {e}")
        
        print(f"  ✅ Supprimés : {deleted:,} fichiers ({fmt(total_del)})")
        if failed:
            print(f"  ❌ Échecs : {failed}")
        
        # Renommage
        if fourn_exists and not fourn_conflict:
            try:
                os.rename(old_fourn, new_fourn)
                print(f"  ✅ founrisseurs renommé en fournisseurs-divers")
            except Exception as e:
                print(f"  ❌ Renommage échoué: {e}")
    else:
        print(f"\n→ Pour exécuter : python cleanup_ggc_junk.py --execute")

if __name__ == "__main__":
    main()
