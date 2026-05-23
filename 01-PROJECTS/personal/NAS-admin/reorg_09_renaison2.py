"""
Réorganisation de 09-BARRAGES RENAISON — phase 2 :
  Rangement des gros dossiers ambigus après la phase 1.

Contexte :
  Le projet a consisté en :
    - 2012-2014 : scans Geode du barrage (corps barrage + galerie + pendule)
    - 2015      : levé du canal évacuateur de crues + bassin central aval
    - 2021-2022 : re-exports finaux pour études aménagement centrale électrique

  "12-BARRAGE RENAISON" (mal nommé) contient en réalité les données brutes
  Cyclone du canal évacuateur (mission 2015) et doit aller dans RENAISON 2015/.

  "SCANS" contient des exports finaux datés juil.2021 pour études centrale élec.

Opérations :
  A) 12-BARRAGE RENAISON   → RENAISON 2015/00-DONNEES-BRUTES-CANAL
  B) SCANS                 → RENAISON 2022/EXPORTS-CENTRALE-ELEC

Usage :
    python reorg_09_renaison2.py           → dry-run
    python reorg_09_renaison2.py --apply   → exécution réelle
"""
import sys, os, shutil

DRY_RUN = '--apply' not in sys.argv
BASE    = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON'
LOG     = os.path.abspath('reports/reorg_09_renaison2_log.txt')

OPERATIONS = [
    {
        'src_rel': '12-BARRAGE RENAISON',
        'dst_rel': r'RENAISON 2015\00-DONNEES-BRUTES-CANAL',
        'raison':  (
            'Contient les données brutes Cyclone du canal évacuateur (mission 2015) :\n'
            '    - renaison_canal_evacuateur/ : fichiers .LPR / .PJD / .CFG + 02-SCANS (25.9 Go)\n'
            '    - renaison-canal-partie1-seule / partie2-seule\n'
            '    Dates fichiers : juin-août 2015.'
        ),
    },
    {
        'src_rel': 'SCANS',
        'dst_rel': r'RENAISON 2022\EXPORTS-CENTRALE-ELEC',
        'raison':  (
            'Contient des exports finaux datés juil.2021 :\n'
            '    - mesh_barage_cyclone.dxf (19.6 Go), galerie.ptx (6.7 Go)\n'
            '    - maillage_barrage.dxf (5.3 Go), barrage_complet.pts (4.8 Go)\n'
            '    - RENAISON.imp (1.3 Go)\n'
            '    Ces exports ont été générés pour les études d\'aménagement centrale électrique.'
        ),
    },
]


# ── Utilitaires ──────────────────────────────────────────────────────────────

def log(msg=''):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def human_size(path):
    """Taille totale d'un dossier ou fichier (approximative via os.walk)."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for fn in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                pass
    return total


# ── Log header ───────────────────────────────────────────────────────────────

open(LOG, 'w', encoding='utf-8').close()
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Réorganisation 09-BARRAGES RENAISON — phase 2")
log('=' * 72)
log(f"  Base : {BASE}")
log()

moved = skipped = errors = 0

for op in OPERATIONS:
    src = os.path.join(BASE, op['src_rel'])
    dst = os.path.join(BASE, op['dst_rel'])

    log(f"  {'[DRY] ' if DRY_RUN else ''}MOVE  {op['src_rel']}")
    log(f"        → {op['dst_rel']}")
    log(f"  Raison : {op['raison']}")

    if not os.path.exists(src):
        log(f"  !! SKIP — source introuvable : {src}")
        skipped += 1
        log()
        continue

    if os.path.exists(dst):
        log(f"  !! SKIP — destination existe déjà : {dst}")
        log(f"     Vérifier manuellement avant fusion.")
        skipped += 1
        log()
        continue

    if DRY_RUN:
        # Estimer la taille (peut prendre du temps sur réseau — juste indicatif)
        log(f"  [DRY] Déplacement simulé — taille non calculée en dry-run pour les gros dossiers")
    else:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            log(f"  OK")
            moved += 1
        except Exception as e:
            log(f"  !! ERREUR : {e}")
            errors += 1
    log()

log('=' * 72)
log("RÉSUMÉ")
log('=' * 72)
log(f"  Déplacements {'simulés' if DRY_RUN else 'effectués'} : {moved}")
log(f"  Ignorés       : {skipped}")
log(f"  Erreurs       : {errors}")
if DRY_RUN:
    log()
    log("  → relancer avec --apply pour exécuter")
log()
log("  _a_classer (4.7 Go) reste à traiter manuellement.")
