"""
Phase 2d — Fusionner 99-olivier L1 dans 20150904-CHAT/99-olivier
puis supprimer 99-olivier L1.

Les 2 versions se chevauchent partiellement:
- L1 a 3975 fich, dont ~1314 uniques
- 20150904-CHAT/99-olivier a 5171 fich, dont ~2523 uniques
On fusionne L1 → 20150904-CHAT/99-olivier, puis on supprime L1.

Dry-run par défaut, --apply pour exécuter.
"""
import os
import sys
import shutil
import sqlite3

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'
APPLY = '--apply' in sys.argv
DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE_DB = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'

SRC = os.path.join(BASE, '99-olivier')
DST = os.path.join(BASE, '20150904-CHAT', '99-olivier')

conn = sqlite3.connect(DB)
c = conn.cursor()

# Fichiers dans DST (destination)
dst_prefix = BASE_DB + '20150904-CHAT\\99-olivier\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (dst_prefix + '%',))
dst_hashes = set()
dst_ns = set()
for fn, sz, h in c.fetchall():
    if h: dst_hashes.add(h)
    dst_ns.add((fn, sz))

# Fichiers dans SRC
src_prefix = BASE_DB + '99-olivier\\'
c.execute("SELECT path, filename, size, hash_md5 FROM files WHERE path LIKE ?", (src_prefix + '%',))

report = []
report.append("=" * 70)
report.append("PHASE 2d — Fusion 99-olivier L1 → 20150904-CHAT/99-olivier")
report.append(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
report.append("=" * 70)

unique_files = []
duplicates = 0
for path, fn, sz, h in c.fetchall():
    if (h and h in dst_hashes) or (fn, sz) in dst_ns:
        duplicates += 1
    else:
        unique_files.append((path, fn, sz))

report.append(f"\n99-olivier L1: {duplicates + len(unique_files)} fichiers")
report.append(f"  • {duplicates} doublons (déjà dans 20150904-CHAT/99-olivier)")
report.append(f"  • {len(unique_files)} fichiers uniques à fusionner")

# Fusionner les uniques. On met dans un sous-dossier _from_L1 pour éviter les conflits d'arbo
# car la structure de L1 peut différer de celle de 20150904-CHAT/99-olivier
moved = 0
errors = 0
for path, fn, sz in unique_files:
    rel = path[len(src_prefix):]
    src_file = os.path.join(SRC, rel)
    dst_file = os.path.join(DST, '_merged_from_L1', rel)
    
    if moved < 30 or moved == len(unique_files) - 1:
        report.append(f"  [FUSE] {rel}")
    elif moved == 30:
        report.append(f"  ... ({len(unique_files) - 30} fichiers de plus) ...")
    
    if APPLY:
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        try:
            shutil.copy2(src_file, dst_file)
            moved += 1
        except Exception as e:
            report.append(f"         ✗ Erreur: {e}")
            errors += 1
    else:
        moved += 1

report.append(f"\n--- Fusion: {moved} fichiers {'copiés' if APPLY else 'à copier'} dans _merged_from_L1/")
if errors:
    report.append(f"    {errors} erreurs")

if APPLY and errors == 0:
    try:
        shutil.rmtree(SRC)
        report.append(f"[DELETE] 99-olivier L1 supprimé ✓")
    except Exception as e:
        report.append(f"[DELETE] 99-olivier L1 erreur: {e}")
elif not APPLY:
    report.append(f"[DELETE] 99-olivier L1 sera supprimé après fusion")

report.append(f"\n{'=' * 70}")
output = '\n'.join(report)
print(output)

log = f"reports/cleanup_33_chat_phase2d_{'log' if APPLY else 'dryrun'}.txt"
os.makedirs('reports', exist_ok=True)
with open(log, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"Rapport: {log}")

conn.close()
