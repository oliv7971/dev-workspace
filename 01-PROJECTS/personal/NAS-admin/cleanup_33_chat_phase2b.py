"""
Phase 2b — Regrouper les petits dossiers orphelins dans _a_trier.
Aussi absorber les dossiers dont le contenu appartient clairement
à un dossier thématique existant.

Dry-run par défaut, --apply pour exécuter.
"""
import os
import sys
import shutil

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'
APPLY = '--apply' in sys.argv

# Gros dossiers thématiques à conserver tels quels
KEEP = {
    'TMS', '03-tunnel chat', '20150904-CHAT', 'tunnel-chat',
    'TUNNEL DU CHAT - 2017 - 19mai2017', '99-olivier',
    '2017', '02-ACTIVITES TOPO',
}

# Petits dossiers à déplacer dans _a_trier
ORPHANS = [
    'TMS Office',           # 105 fich, 205 Mo — config TMS, lié à TMS mais pas inclus
    'CHAT',                 # 3 fich, 92 Mo — .imp Amberg
    'documents-tunnel-du-chat',  # 43 fich, 51 Mo
    'TUNNEL CHAT',          # 49 fich, 20 Mo
    'xxxxxxxx a classer xxxxxxxx',  # 65 fich, 20 Mo
    '14 tunnel chat',       # 34 fich, 10 Mo
    '01-reperage 23nov2014',  # 20 fich, 10 Mo
    'Plans EIFFAGE',        # 5 fich, 10 Mo
    'carte tps 170615',     # 283 fich — sauvegarde cartes TPS
    '89-PLANS EXE',         # 39 fich
    'leve-tetes-dec2014',   # 32 fich
    'scan chat rescindement',  # 15 fich
    'TUNNEL DU CHAT',       # 35 fich
    'Polygo chat lucas',    # 2 fich
    '71-envoi FC scans mai2017',  # 4 fich
    '99-LREF carneaux',     # 3 fich
    '11-TUNNEL DU CHAT',    # 3 fich — config Amberg
    'polygo 20150926',      # 1 fich
    'temp',                 # 1 fich
    '98-LREF rameaux',      # 1 fich
]

a_trier = os.path.join(BASE, '_a_trier')
report = []
report.append("=" * 70)
report.append("PHASE 2b — Regroupement des petits dossiers orphelins")
report.append(f"Destination: _a_trier/")
report.append(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}")
report.append("=" * 70)

moved = 0
for folder in ORPHANS:
    src = os.path.join(BASE, folder)
    dst = os.path.join(a_trier, folder)
    
    if not os.path.exists(src):
        report.append(f"  [SKIP] {folder} — n'existe plus")
        continue
    
    count = sum(len(files) for _, _, files in os.walk(src))
    report.append(f"  [MOVE] {folder} ({count} fich) → _a_trier/{folder}")
    
    if APPLY:
        os.makedirs(a_trier, exist_ok=True)
        try:
            shutil.move(src, dst)
            report.append(f"         ✓ Déplacé")
            moved += 1
        except Exception as e:
            report.append(f"         ✗ Erreur: {e}")
    else:
        moved += 1

# Fichier orphelin en racine
root_file = os.path.join(BASE, 'TUNNEL CHAT - nouveau PL - TMS - 20150807 .txt')
if os.path.exists(root_file):
    report.append(f"  [MOVE] TUNNEL CHAT - nouveau PL - TMS - 20150807 .txt → _a_trier/")
    if APPLY:
        os.makedirs(a_trier, exist_ok=True)
        try:
            shutil.move(root_file, os.path.join(a_trier, os.path.basename(root_file)))
            report.append(f"         ✓ Déplacé")
        except Exception as e:
            report.append(f"         ✗ Erreur: {e}")

report.append(f"\n{'=' * 70}")
report.append(f"Bilan: {moved} dossiers {'déplacés' if APPLY else 'à déplacer'} dans _a_trier/")
report.append(f"{'=' * 70}")

output = '\n'.join(report)
print(output)

log = f"reports/cleanup_33_chat_phase2b_{'log' if APPLY else 'dryrun'}.txt"
os.makedirs('reports', exist_ok=True)
with open(log, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"\nRapport: {log}")

# Afficher ce qui restera en racine
print("\nDossiers restants en racine après phase 2b:")
for k in sorted(KEEP):
    if os.path.exists(os.path.join(BASE, k)):
        print(f"  📁 {k}")
if moved > 0:
    print(f"  📁 _a_trier  ({moved} sous-dossiers)")
