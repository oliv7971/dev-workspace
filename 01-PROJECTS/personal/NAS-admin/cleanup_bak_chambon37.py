"""Supprime les fichiers .bak dans 37-TUNNEL GRAND CHAMBON.

Ces fichiers sont des sauvegardes automatiques (AutoCAD, Excel, etc.)
et ne présentent pas de valeur propre si le fichier source est conservé.

Usage :
  python cleanup_bak_chambon37.py           → dry-run (aucune suppression)
  python cleanup_bak_chambon37.py --execute → suppression réelle
"""
import os, sys, sqlite3

BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"
DB   = "reports/inventory_chambon37.db"
EXECUTE = "--execute" in sys.argv

def human_size(n):
    if not n: n = 0
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

c = sqlite3.connect(DB)
baks = c.execute(
    "SELECT path, size FROM files WHERE LOWER(extension) = '.bak' ORDER BY size DESC"
).fetchall()
c.close()

total_size = sum(s or 0 for _, s in baks)
print(f"\n{'='*72}")
print(f"NETTOYAGE .BAK — {'EXÉCUTION' if EXECUTE else 'DRY-RUN'}")
print(f"{'='*72}")
print(f"  Fichiers .bak trouvés : {len(baks):,}   Volume : {human_size(total_size)}\n")

ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\37-TUNNEL GRAND CHAMBON\\"

deleted = 0
errors  = 0
deleted_size = 0

for path, sz in baks:
    rel = path[len(ROOT):]
    if EXECUTE:
        try:
            os.remove(path)
            deleted += 1
            deleted_size += sz or 0
        except Exception as e:
            print(f"  ❌  {rel[:70]}  — {e}")
            errors += 1
    else:
        # dry-run : afficher les 20 plus gros
        pass

if not EXECUTE:
    print("  Top 20 fichiers :")
    for path, sz in baks[:20]:
        rel = path[len(ROOT):]
        print(f"  {human_size(sz):>9}  {rel[:70]}")
    if len(baks) > 20:
        print(f"  ... et {len(baks)-20} autres")
    print(f"\n⚠️  DRY-RUN — aucun fichier supprimé.")
    print(f"   Relancer avec : python cleanup_bak_chambon37.py --execute")
else:
    print(f"\n✅ Supprimés : {deleted:,} fichiers  ({human_size(deleted_size)})")
    if errors:
        print(f"❌ Erreurs   : {errors}")
