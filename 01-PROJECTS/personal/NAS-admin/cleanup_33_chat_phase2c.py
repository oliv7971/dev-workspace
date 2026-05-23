"""
Phase 2c — Fusionner 2017/ dans TUNNEL DU CHAT - 2017 - 19mai2017
puis supprimer 2017/.

2017/ est un snapshot partiel antérieur au 19 mai (dates 72-98% overlap).
On fusionne les fichiers uniques restants.

Dry-run par défaut, --apply pour exécuter.
"""
import os
import sys
import shutil
import sqlite3

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'
APPLY = '--apply' in sys.argv

SRC = os.path.join(BASE, '2017')
DST = os.path.join(BASE, 'TUNNEL DU CHAT - 2017 - 19mai2017')
DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE_DB = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Récupérer les hashes et (nom, taille) des fichiers dans DST
dst_prefix = BASE_DB + 'TUNNEL DU CHAT - 2017 - 19mai2017\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (dst_prefix + '%',))
dst_files = c.fetchall()
dst_hashes = {h for _, _, h in dst_files if h}
dst_ns = {(fn, sz) for fn, sz, _ in dst_files}

# Récupérer les fichiers de SRC
src_prefix = BASE_DB + '2017\\'
c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?", (src_prefix + '%',))
src_files = c.fetchall()

report = []
report.append("=" * 70)
report.append("PHASE 2c — Fusion de 2017/ dans TUNNEL DU CHAT - 2017 - 19mai2017")
report.append(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
report.append("=" * 70)

# Identifier les fichiers uniques dans SRC
unique_files = []
duplicate_files = []
for path, fn, sz, h in src_files:
    if (h and h in dst_hashes) or (fn, sz) in dst_ns:
        duplicate_files.append((path, fn, sz))
    else:
        unique_files.append((path, fn, sz))

report.append(f"\n2017/: {len(src_files)} fichiers total")
report.append(f"  • {len(duplicate_files)} doublons (déjà dans le snapshot 19mai)")
report.append(f"  • {len(unique_files)} fichiers uniques à fusionner")

# Fusionner les fichiers uniques : conserver la structure relative
moved = 0
errors = 0
for path, fn, sz in unique_files:
    # Chemin relatif dans 2017/
    rel = path[len(src_prefix):]  # ex: "02-ACTIVITES TOPO\fichier.xlsx"
    src_file = os.path.join(SRC, rel)
    dst_file = os.path.join(DST, rel)
    
    report.append(f"  [FUSE] {rel}")
    
    if APPLY:
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        if os.path.exists(dst_file):
            # Conflit de nom — renommer avec suffixe
            base, ext = os.path.splitext(dst_file)
            dst_file = f"{base}_from2017{ext}"
            report.append(f"         → rename: {os.path.basename(dst_file)}")
        try:
            shutil.copy2(src_file, dst_file)
            moved += 1
        except Exception as e:
            report.append(f"         ✗ Erreur: {e}")
            errors += 1
    else:
        moved += 1

report.append(f"\n--- Fusion: {moved} fichiers {'copiés' if APPLY else 'à copier'}")
if errors:
    report.append(f"    {errors} erreurs")

# Suppression de 2017/ après fusion
if APPLY and errors == 0:
    try:
        shutil.rmtree(SRC)
        report.append(f"[DELETE] 2017/ supprimé ✓")
    except Exception as e:
        report.append(f"[DELETE] 2017/ erreur: {e}")
elif not APPLY:
    report.append(f"[DELETE] 2017/ sera supprimé après fusion")

report.append(f"\n{'=' * 70}")
output = '\n'.join(report)
print(output)

log = f"reports/cleanup_33_chat_phase2c_{'log' if APPLY else 'dryrun'}.txt"
os.makedirs('reports', exist_ok=True)
with open(log, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"Rapport: {log}")

conn.close()
