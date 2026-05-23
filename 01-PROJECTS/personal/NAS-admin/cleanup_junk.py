"""
Nettoyage des fichiers temporaires et backups inutiles dans 21-CERENE.
Niveau 1 : suppressions sans risque (tmp, .bak, Backup redondants).

Usage:
    python cleanup_junk.py            # dry-run
    python cleanup_junk.py --execute  # suppression réelle
"""
import os
import sys
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_cerene.db"
NAS_BASE = "\\\\Nas_travail\\01-ds414-data\\21-CERENE\\"
EXECUTE = "--execute" in sys.argv

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    if size >= 1e3: return f"{size/1e3:.1f} Ko"
    return f"{size} o"

def rel(path):
    return path[len(NAS_BASE):] if path.startswith(NAS_BASE) else path

# ============================================================
# RÈGLES DE NETTOYAGE
# ============================================================

def is_deletable(path, filename, ext, size):
    """Retourne (True, raison) si le fichier peut être supprimé."""
    r = rel(path).lower()
    segs = rel(path).split("\\")
    
    # --- RÈGLE 1 : Dossiers tmp/temp dans 10-SERVEURS ---
    if r.startswith("10-serveurs"):
        for seg in segs:
            if seg.lower() in ("tmp", "temp"):
                return True, "tmp dans SERVEURS"
    
    # --- RÈGLE 2 : Fichiers .bak dans 02-AFFAIRES ---
    # Ce sont des backups automatiques AutoCAD (.dwg → .bak)
    if r.startswith("02-affaires") and ext and ext.lower() == ".bak":
        return True, ".bak AutoCAD"
    
    # --- RÈGLE 3 : Fichiers .bak dans 10-SERVEURS ---
    if r.startswith("10-serveurs") and ext and ext.lower() == ".bak":
        return True, ".bak dans SERVEURS"
    
    # --- RÈGLE 4 : Backup DWG dans 02-AFFAIRES ---
    # Dossiers Backup/BAK contenant des vieilles versions
    if r.startswith("02-affaires"):
        for i, seg in enumerate(segs):
            if seg.lower() in ("backup", "bak") and i > 0:
                parent_type = segs[0]
                return True, f"Dossier Backup dans {parent_type}"
    
    # --- RÈGLE 5 : Nouveau dossier quasi-vide ---
    # Seulement les petits (< 1 Mo et ≤ 5 fichiers) - on renomme les gros à part
    # Ces cas sont gérés dans le renommage, pas ici
    
    # --- RÈGLE 6 : Dossiers tmp/temp dans 02-AFFAIRES ---
    if r.startswith("02-affaires"):
        for seg in segs:
            if seg.lower() in ("tmp", "temp"):
                return True, "tmp dans AFFAIRES"
    
    # --- RÈGLE 7 : Fichiers Thumbs.db partout ---
    if filename.lower() == "thumbs.db":
        return True, "Thumbs.db"
    
    # --- RÈGLE 8 : Fichiers .bak dans 03-PROJETS ---
    if r.startswith("03-projets") and ext and ext.lower() == ".bak":
        return True, ".bak dans PROJETS"
    
    # --- RÈGLE 9 : Installeurs/ISO dans 10-SERVEURS (logiciels obsolètes) ---
    if r.startswith("10-serveurs") and ext and ext.lower() in (".iso", ".msi"):
        if size > 50_000_000:  # > 50 Mo
            return True, "ISO/MSI dans SERVEURS"
    
    return False, ""


def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute("SELECT path, filename, extension, size FROM files")
    all_files = cur.fetchall()
    db.close()
    
    # Classifier
    to_delete = []
    stats_by_reason = defaultdict(lambda: [0, 0])
    
    for path, fn, ext, size in all_files:
        delete, reason = is_deletable(path, fn, ext, size)
        if delete:
            to_delete.append((path, fn, size, reason))
            stats_by_reason[reason][0] += 1
            stats_by_reason[reason][1] += size
    
    # Affichage
    mode = "🗑️  SUPPRESSION" if EXECUTE else "🔍 DRY-RUN (simulation)"
    print(mode)
    print("=" * 70)
    
    print("\nRègles appliquées :")
    for reason in sorted(stats_by_reason, key=lambda x: stats_by_reason[x][1], reverse=True):
        nb, sz = stats_by_reason[reason]
        print(f"  {reason:30s}  {nb:>8,} fichiers  {fmt(sz):>10s}")
    
    total_files = sum(n for n, _ in stats_by_reason.values())
    total_size = sum(s for _, s in stats_by_reason.values())
    print(f"\n  {'─' * 55}")
    print(f"  {'TOTAL':30s}  {total_files:>8,} fichiers  {fmt(total_size):>10s}")
    
    # Top 20 plus gros fichiers à supprimer
    print(f"\nTop 20 plus gros fichiers à supprimer :")
    top = sorted(to_delete, key=lambda x: x[2], reverse=True)[:20]
    for path, fn, size, reason in top:
        l1 = rel(path).split("\\")[0]
        print(f"  [{l1:15s}] {fn:50s}  {fmt(size):>10s}  ({reason})")
    
    # Par dossier niveau 1
    print(f"\nPar dossier :")
    by_folder = defaultdict(lambda: [0, 0])
    for path, fn, size, reason in to_delete:
        l1 = rel(path).split("\\")[0]
        by_folder[l1][0] += 1
        by_folder[l1][1] += size
    
    for folder in sorted(by_folder, key=lambda x: by_folder[x][1], reverse=True):
        nb, sz = by_folder[folder]
        print(f"  {folder:30s}  {nb:>8,} fichiers  {fmt(sz):>10s}")
    
    if EXECUTE:
        print(f"\n⚡ Suppression en cours...")
        deleted = 0
        failed = 0
        freed = 0
        
        for path, fn, size, reason in to_delete:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    deleted += 1
                    freed += size
                else:
                    # Déjà supprimé (doublon précédent)
                    deleted += 1
                    freed += size
            except Exception as e:
                failed += 1
                if failed <= 10:
                    print(f"  ❌ {fn}: {e}")
        
        print(f"\n  ✅ Supprimés : {deleted:,} fichiers ({fmt(freed)})")
        if failed:
            print(f"  ❌ Échecs   : {failed:,}")
    else:
        print(f"\n→ Pour exécuter : python cleanup_junk.py --execute")


if __name__ == "__main__":
    main()
