"""
Réorganisation de 02-STRASBOURG ETOILE selon la structure standard :
  00-ADMIN/     → documents administratifs
  01-DONNEES/   → données terrain
  02-TRAVAIL/   → fichiers de travail
  03-LIVRAISON/ → livrables finaux
  04-ARCHIVES/  → anciennes versions

Usage:
  python reorg_02_strasbourg.py           (dry-run)
  python reorg_02_strasbourg.py --apply   (exécution réelle)
"""
import sys, os, shutil

DRY_RUN = '--apply' not in sys.argv
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\02-STRASBOURG ETOILE'
LOG  = os.path.abspath('reports/reorg_02_strasbourg_log.txt')

# Mapping : nom_actuel -> destination (chemin relatif dans BASE)
MAPPING = {
    # 00-ADMIN
    'DPE1033C_00_AE.DOC':                   '00-ADMIN',
    '02B DPE1033C_PROGRAMME.pdf':            '00-ADMIN',
    'DPE1033C_CCTP.pdf':                     '00-ADMIN',
    'engagement_sous-traitance-exemple_vide.doc': '00-ADMIN',
    '02A planning ggc_AOUT2012.pdf':         '00-ADMIN',
    '01 mail envoyé par Egis pour def mission.docx': '00-ADMIN',

    # 01-DONNEES
    'fichiers bruts':                        '01-DONNEES',
    'STRASBOURG scan 6a9aout12.rar':         '01-DONNEES',
    'donnees_entrées3Dphotos_EGIS':          '01-DONNEES',

    # 02-TRAVAIL
    'tunnel-etoile-strasbourg':              '02-TRAVAIL',
    'fichiers_travail':                      '02-TRAVAIL',
    'calculs scan':                          '02-TRAVAIL',
    'polygo_xls':                            '02-TRAVAIL',
    'STRASBOURG polygo&calage scan 6a9aout12': '02-TRAVAIL',
    'gabarit_provisoire':                    '02-TRAVAIL',

    # 03-LIVRAISON
    'LIVRABLES':                             '03-LIVRAISON',
    'livraison_complements':                 '03-LIVRAISON',
    'strasbourg VUE-EN-PLAN-TUN-ETOILE-V02 - Standard': '03-LIVRAISON',

    # 04-ARCHIVES
    'livraison-3aout2012':                   '04-ARCHIVES',
    'doc de aout12':                         '04-ARCHIVES',
    'levé _xls_gsi_dxf':                    '04-ARCHIVES',
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
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Réorganisation 02-STRASBOURG ETOILE")
log("="*80)

# Créer les dossiers cibles (en dry-run, juste afficher)
for d in ['00-ADMIN', '01-DONNEES', '02-TRAVAIL', '03-LIVRAISON', '04-ARCHIVES']:
    dst = os.path.join(BASE, d)
    if not DRY_RUN:
        os.makedirs(dst, exist_ok=True)
    else:
        log(f"  [DRY] Créer dossier : {dst}")

log("")
moved = 0
skipped = 0

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
