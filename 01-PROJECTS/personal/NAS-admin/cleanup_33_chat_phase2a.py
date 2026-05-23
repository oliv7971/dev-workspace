"""
Phase 2a — Suppression des dossiers 100% inclus dans d'autres.
5 dossiers confirmés comme totalement redondants.

Dry-run par défaut, exécuter avec --apply pour supprimer réellement.
"""
import os
import sys
import shutil

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'
APPLY = '--apply' in sys.argv

# Dossiers à supprimer : (dossier, fichiers, inclus_dans)
TO_DELETE = [
    ('Etude BG',       10, '99-olivier'),
    ('PAUL',           16, 'TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('Pour Eiffage',   17, '20150904-CHAT'),
    ('03-POLYGONALE',   4, 'TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('voute parapluie', 8, '20150904-CHAT'),
]

report = []
report.append("=" * 70)
report.append("PHASE 2a — Suppression des dossiers 100% inclus")
report.append(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
report.append("=" * 70)

total_deleted = 0
for folder, expected_files, parent in TO_DELETE:
    path = os.path.join(BASE, folder)
    if not os.path.exists(path):
        report.append(f"\n[SKIP] {folder} — n'existe plus (déjà supprimé en P1?)")
        continue
    
    # Compter les fichiers réels
    count = sum(len(files) for _, _, files in os.walk(path))
    
    report.append(f"\n[DELETE] {folder}")
    report.append(f"  → {count} fichiers, 100% contenus dans {parent}")
    
    if APPLY:
        try:
            shutil.rmtree(path)
            report.append(f"  ✓ Supprimé")
            total_deleted += 1
        except Exception as e:
            report.append(f"  ✗ Erreur: {e}")
    else:
        report.append(f"  (dry-run)")
        total_deleted += 1

report.append(f"\n{'=' * 70}")
report.append(f"Bilan: {total_deleted} dossiers {'supprimés' if APPLY else 'à supprimer'}")
report.append(f"{'=' * 70}")

output = '\n'.join(report)
print(output)

log_name = 'reports/cleanup_33_chat_phase2a_log.txt' if APPLY else 'reports/cleanup_33_chat_phase2a_dryrun.txt'
os.makedirs('reports', exist_ok=True)
with open(log_name, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"\nRapport: {log_name}")
