"""
Phase 2e — Nettoyage de TMS (106 Go)
1. Fusionner le 1 fichier unique de 270616_CHAT2 dans 270616_CHAT
2. Supprimer 270616_CHAT2 (25.4 Go)
3. Supprimer les 3 fichiers .zip (19.4 Go)

Gain estimé: ~44 Go

Dry-run par défaut, --apply pour exécuter.
"""
import os
import sys
import shutil

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT\TMS'
APPLY = '--apply' in sys.argv

report = []
report.append("=" * 70)
report.append("PHASE 2e — Nettoyage de TMS")
report.append(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
report.append("=" * 70)

# 1. Fusionner le fichier unique de CHAT2
unique_file = r'270616_CHAT2\270616_CHAT\s01-scans 280616\AMTP5003_20160629012022_59_0.zfs.PTS'
src = os.path.join(BASE, unique_file)
dst = os.path.join(BASE, '270616_CHAT', 's01-scans 280616', 'AMTP5003_20160629012022_59_0.zfs.PTS')

if os.path.exists(src):
    sz_mb = os.path.getsize(src) / 1048576
    report.append(f"\n[FUSE] {os.path.basename(src)} ({sz_mb:.0f} Mo)")
    report.append(f"  de: 270616_CHAT2/.../s01-scans 280616/")
    report.append(f"  vers: 270616_CHAT/s01-scans 280616/")
    
    if APPLY:
        if os.path.exists(dst):
            report.append(f"  ⚠ Destination existe déjà — renommage")
            base, ext = os.path.splitext(dst)
            dst = base + '_from_CHAT2' + ext
        try:
            shutil.copy2(src, dst)
            report.append(f"  ✓ Copié")
        except Exception as e:
            report.append(f"  ✗ Erreur: {e}")
else:
    report.append(f"\n[SKIP] Fichier unique de CHAT2 non trouvé")

# 2. Supprimer 270616_CHAT2
chat2_path = os.path.join(BASE, '270616_CHAT2')
if os.path.exists(chat2_path):
    # Compter fichiers et taille
    count = sum(len(files) for _, _, files in os.walk(chat2_path))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(chat2_path) for f in files)
    report.append(f"\n[DELETE] 270616_CHAT2 ({count} fich, {size/1073741824:.1f} Go)")
    
    if APPLY:
        try:
            shutil.rmtree(chat2_path)
            report.append(f"  ✓ Supprimé")
        except Exception as e:
            report.append(f"  ✗ Erreur: {e}")
    else:
        report.append(f"  (dry-run)")

# 3. Supprimer les .zip
zips = ['270616_CHAT.zip', '270616_CHAT2.zip', '270616_CHAT-1.zip']
for zf in zips:
    zpath = os.path.join(BASE, zf)
    if os.path.exists(zpath):
        sz_go = os.path.getsize(zpath) / 1073741824
        report.append(f"\n[DELETE] {zf} ({sz_go:.1f} Go)")
        
        if APPLY:
            try:
                os.remove(zpath)
                report.append(f"  ✓ Supprimé")
            except Exception as e:
                report.append(f"  ✗ Erreur: {e}")
        else:
            report.append(f"  (dry-run)")

report.append(f"\n{'=' * 70}")
report.append(f"Gain estimé: ~44 Go")
report.append(f"{'=' * 70}")

output = '\n'.join(report)
print(output)

log = f"reports/cleanup_33_chat_phase2e_{'log' if APPLY else 'dryrun'}.txt"
os.makedirs('reports', exist_ok=True)
with open(log, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"\nRapport: {log}")
