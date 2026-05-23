"""
Réorganisation de 05-CROIX ROUSSE selon la structure standard :
  00-ADMIN/     → documents administratifs
  01-DONNEES/   → données terrain
  02-TRAVAIL/   → fichiers de travail
  03-LIVRAISON/ → livrables finaux
  04-ARCHIVES/  → anciennes versions

Usage:
  python reorg_05_croix_rousse.py           (dry-run)
  python reorg_05_croix_rousse.py --apply   (exécution réelle)
"""
import sys, os, shutil

DRY_RUN = '--apply' not in sys.argv
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\05-CROIX ROUSSE'
LOG  = os.path.abspath('reports/reorg_05_croix_rousse_log.txt')

MAPPING = {
    # 00-ADMIN
    'DIVERS':                                '00-ADMIN',
    'Croix rousse coordonnees_refs_171012.txt': '00-ADMIN',

    # 01-DONNEES
    'TUNNEL_CROIX_ROUSSE_SCAN2012':          '01-DONNEES',
    'donnees_pvdz':                          '01-DONNEES',

    # 02-TRAVAIL
    'ACTIVITES':                             '02-TRAVAIL',
    'CYCLONE-croixrousse':                   '02-TRAVAIL',
    'croix_rousse':                          '02-TRAVAIL',

    # 03-LIVRAISON
    'LIVRAISONS':                            '03-LIVRAISON',
    'PROFILS':                               '03-LIVRAISON',

    # 04-ARCHIVES
    'archives':                              '04-ARCHIVES',
    'calculs_beton':                         '04-ARCHIVES',
}

def log(msg):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def move(src, dst_dir):
    dst = os.path.join(BASE, dst_dir, os.path.basename(src))
    log(f"  {'[DRY]' if DRY_RUN else 'MOVE'} {os.path.basename(src)}")
    log(f"       {src}")
    log(f"    -> {dst}")
    if not DRY_RUN:
        os.makedirs(os.path.join(BASE, dst_dir), exist_ok=True)
        shutil.move(src, dst)

open(LOG, 'w').close()
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Réorganisation 05-CROIX ROUSSE")
log("="*80)

for d in ['00-ADMIN', '01-DONNEES', '02-TRAVAIL', '03-LIVRAISON', '04-ARCHIVES']:
    dst = os.path.join(BASE, d)
    if not DRY_RUN:
        os.makedirs(dst, exist_ok=True)
    else:
        log(f"  [DRY] Créer dossier : {dst}")

log("")
moved = skipped = 0

for nom, destination in MAPPING.items():
    src = os.path.join(BASE, nom)
    if os.path.exists(src):
        move(src, destination)
        moved += 1
    else:
        log(f"  SKIP (introuvable) : {nom}")
        skipped += 1

log("")
log(f"  Déplacements {'simulés' if DRY_RUN else 'effectués'} : {moved}")
log(f"  Introuvables (skip) : {skipped}")
if DRY_RUN:
    log("\n[DRY-RUN] Relancez avec --apply pour exécuter.")
