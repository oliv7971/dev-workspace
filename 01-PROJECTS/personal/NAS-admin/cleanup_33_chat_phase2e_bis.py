"""
Phase 2e-bis — Supprimer la poupée russe 270616_CHAT/270616_CHAT/
C'est une copie exacte du parent (3614/3615 fichiers identiques, 
le seul unique est un Thumbs.db).

Gain: ~30.6 Go

Dry-run par défaut, --apply pour exécuter.
"""
import os
import sys
import shutil

APPLY = '--apply' in sys.argv
TARGET = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT\TMS\270616_CHAT\270616_CHAT'

report = []
report.append("=" * 70)
report.append("PHASE 2e-bis — Suppression poupée russe 270616_CHAT/270616_CHAT/")
report.append(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
report.append("=" * 70)

if not os.path.exists(TARGET):
    report.append("[SKIP] Le dossier n'existe pas")
else:
    count = sum(len(files) for _, _, files in os.walk(TARGET))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(TARGET) for f in files)
    report.append(f"\n[DELETE] 270616_CHAT/270616_CHAT/")
    report.append(f"  {count} fichiers, {size/1073741824:.1f} Go")
    report.append(f"  99% identique au parent, seul unique = Thumbs.db")
    
    if APPLY:
        try:
            shutil.rmtree(TARGET)
            report.append(f"  ✓ Supprimé")
        except Exception as e:
            report.append(f"  ✗ Erreur: {e}")
    else:
        report.append(f"  (dry-run)")

report.append(f"\n{'=' * 70}")
output = '\n'.join(report)
print(output)

log = f"reports/cleanup_33_chat_phase2e_bis_{'log' if APPLY else 'dryrun'}.txt"
os.makedirs('reports', exist_ok=True)
with open(log, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"Rapport: {log}")
